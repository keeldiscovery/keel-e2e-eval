"""The stub issuer's identity registry -- a JSON file, three routes' worth of rules, and nothing
else (keel-cloud `canon/designs/e2e-matrix-design.md` §4.3).

**Why a registry at all.** On the local profiles the stub signs in as one of two identities named
in `stack/oidc.py`, and that is the whole of it. On the staging twin the matrix runs eighteen
cells a week and every cell wants *its own founder*, named for the cell and the day, so the
founder's morning is a picker that reads as the log they asked for:

    2026-09-11 . windows . copilot . py3.9   -- PASSED 5.0 (S-001)

So the two built-in identities gain a list beside them: written by `POST /identities` before a
cell signs in, patched by `PATCH /identities/<id>` when the cell has its verdict, read by
`GET /identities` and by the picker itself. It is a *list*, not a database: no schema migration,
no index, no query language, and it is thrown away by the monthly reset (§8).

**Three properties this file exists to hold.**

1. **Newest first.** The founder wants yesterday's cells at the top, and a registry that ordered
   by id would put `ubuntu-…` above `windows-…` forever.
2. **Atomic writes.** Eighteen cells register within a minute of each other and the file is read
   on every `/authorize`. A reader must never see half a write, so every write goes to a temp
   file in the same directory and is `os.replace`d into place -- one syscall, and the old bytes
   are the ones any reader in flight already has.
3. **Ownership is recorded, because the gate depends on it** (§4.2, invariant M6). Each entry
   remembers which gate user registered it, and that is what makes *"`harness` may only sign in
   as identities it registered"* a fact about data rather than a convention about behaviour.

**In memory by default.** `Registry()` with no path is a list that dies with the process, which
is exactly what the eval and playground profiles want: they pass no `--registry`, register
nothing, and their `/authorize` is byte-for-byte the page it was before this file existed.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from stack.stub_oidc.identity import Identity

#: What a cell's `sub` is derived from its id (§4.3). keel-cloud keys the account on the `sub`
#: alone (google-sign-in-design.md §3.4), so this prefix is the only thing that makes a cell's
#: founder a different person from every other cell's.
SUB_PREFIX = "cell-"

#: An id is a path segment and a `sub` suffix, so it is deliberately narrow: it appears in a URL
#: (`PATCH /identities/<id>`), in a hidden form field, and in keel-cloud's own account table.
ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")


class RegistryError(RuntimeError):
    """A registration the stub refuses. `status` is what the route answers with."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


@dataclass(frozen=True)
class Entry:
    """One registered identity, plus the two things the file knows that an `Identity` does not:
    who registered it, and when. `registered_at` is what "newest first" is ordered by -- the
    order entries were *written*, not the order their ids sort in."""

    identity: Identity
    registered_by: str
    registered_at: float

    def to_json(self) -> dict:
        return {
            "id": self.identity.id,
            "sub": self.identity.sub,
            "email": self.identity.email,
            "name": self.identity.name,
            "label": self.identity.label or "",
            "registered_by": self.registered_by,
            "registered_at": self.registered_at,
        }

    @classmethod
    def from_json(cls, raw: dict) -> "Entry":
        return cls(
            identity=Identity(
                id=str(raw["id"]),
                sub=str(raw.get("sub") or f"{SUB_PREFIX}{raw['id']}"),
                email=str(raw.get("email") or ""),
                name=str(raw.get("name") or raw["id"]),
                label=(raw.get("label") or None),
            ),
            registered_by=str(raw.get("registered_by") or ""),
            registered_at=float(raw.get("registered_at") or 0.0),
        )


class Registry:
    """The list. `path=None` keeps it in memory (the local profiles); a path makes it the JSON
    file on the staging box's own volume, re-read on every access so a registration made by one
    request is visible to the next one even if something outside this process wrote it."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else None
        self._lock = threading.Lock()
        self._entries: list[Entry] = []
        if self.path and self.path.exists():
            self._entries = self._read_file()

    # ---------------------------------------------------------------------------------- reads

    def _read_file(self) -> list[Entry]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            # A file that is not there yet, or that somebody truncated, reads as an empty
            # registry rather than as a dead issuer: the two built-in identities still sign in,
            # which is the difference between a degraded staging box and an unusable one.
            return []
        items = raw.get("identities", []) if isinstance(raw, dict) else raw
        entries = []
        for item in items:
            try:
                entries.append(Entry.from_json(item))
            except (KeyError, TypeError, ValueError):
                continue
        return entries

    def entries(self) -> list[Entry]:
        """Oldest first -- the order they were written, which is the order the file holds."""
        with self._lock:
            if self.path:
                self._entries = self._read_file()
            return list(self._entries)

    def newest_first(self) -> list[Entry]:
        """What `GET /identities` answers and what the picker renders (§4.3)."""
        return list(reversed(self.entries()))

    def identities(self) -> list[Identity]:
        return [entry.identity for entry in self.newest_first()]

    def find(self, hint: str) -> Entry | None:
        for entry in self.newest_first():
            if entry.identity.matches(hint):
                return entry
        return None

    # --------------------------------------------------------------------------------- writes

    def _write(self, entries: list[Entry]) -> None:
        self._entries = entries
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"identities": [e.to_json() for e in entries]}, indent=2) + "\n"
        # Temp file **in the same directory** (a rename across filesystems is not atomic), then
        # `os.replace`, which is atomic on POSIX and on Windows alike. A reader holding the old
        # inode reads the old file to its end; there is no moment at which the path names a
        # half-written document.
        temp = self.path.with_name(f".{self.path.name}.{os.getpid()}.{time.time_ns()}.tmp")
        try:
            temp.write_text(payload, encoding="utf-8")
            os.replace(temp, self.path)
        finally:
            temp.unlink(missing_ok=True)

    def register(self, *, id: str, name: str, email: str, label: str | None = None,
                 registered_by: str = "", reserved_ids: set[str] | None = None) -> Entry:
        """`POST /identities`. 409 on a duplicate id, 400 on anything malformed, and the `sub` is
        **derived, never supplied**: a caller that could choose its own `sub` could choose
        another cell's, and the `sub` is the whole of keel-cloud's identity (§3.4)."""
        id = (id or "").strip()
        if not ID_PATTERN.match(id):
            raise RegistryError(400, f"id {id!r} must match {ID_PATTERN.pattern}")
        name = (name or "").strip()
        email = (email or "").strip()
        if not name or not email:
            raise RegistryError(400, "name and email are both required")
        with self._lock:
            if self.path:
                self._entries = self._read_file()
            taken = {e.identity.id for e in self._entries} | (reserved_ids or set())
            if id in taken:
                raise RegistryError(409, f"identity {id!r} is already registered")
            entry = Entry(
                identity=Identity(id=id, sub=f"{SUB_PREFIX}{id}", email=email, name=name,
                                  label=(label or None)),
                registered_by=registered_by,
                registered_at=time.time(),
            )
            self._write(self._entries + [entry])
        return entry

    def relabel(self, id: str, label: str) -> Entry:
        """`PATCH /identities/<id>`. **Label only** -- a cell writes its verdict and nothing else,
        so a run can never rename, re-address or re-`sub` the founder it signed in as."""
        with self._lock:
            if self.path:
                self._entries = self._read_file()
            for index, entry in enumerate(self._entries):
                if entry.identity.id == id:
                    updated = Entry(
                        identity=Identity(
                            id=entry.identity.id, sub=entry.identity.sub,
                            email=entry.identity.email, name=entry.identity.name,
                            picture=entry.identity.picture, hd=entry.identity.hd,
                            label=(label or None)),
                        registered_by=entry.registered_by,
                        registered_at=entry.registered_at,
                    )
                    entries = list(self._entries)
                    entries[index] = updated
                    self._write(entries)
                    return updated
        raise RegistryError(404, f"no such identity {id!r}")
