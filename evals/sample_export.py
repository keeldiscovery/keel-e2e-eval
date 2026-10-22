"""Spec 060: the sample project -- S-006's finished project exported as a snapshot for the landing page (keel-cloud
`canon/designs/landing-page-design.md` §18.8, §18.9 row 1, §18.11).

**Only when `KEEL_SAMPLE_EXPORT=<dir>` is set** (FR-1): `wanted()` is `None` otherwise and S-006 records no step of
it, so the eval cell is exactly what it was (FR-5). `make sample` sets it (FR-4).

What it does, in order:

1. `capture` -- every founder read FR-1 names, **as the founder session received them** (`Journey.get`, the founder's
   own browser context): `overview`, `plan`, `standings`, `roles`, `people`, `readings`, one `readings/<batchId>` for
   every batch `readings` lists, `invitations`, and one `invitations/<id>` for every row the register lists. The key is
   the path under `/v2/projects/{id}/` with the id removed (`FounderReadController`, `VectorsController`), so keel-web's
   sample route maps `/v2/projects/sample/<key>` -> `/sample/<key>.json` one to one.
2. `withhold` -- FR-2: every person's name is kept as the founder API served it (spec 061 FR-1: the entry's people are
   scripted and fictional), every `email` key goes and any address left in a text, the founder's own name and email go
   from every file, and invitation tokens and links read `withheld`.
3. `gate` -- FR-3: the finished project's decision label is `BUILD_BUT_CHANGE`, the three stages' verdicts are the
   entry's `expected.vector_verdicts`, every asked dimension carries its n (judgement call 1 in `tasks.md`: the
   entry's own n, since 05-paidly's commercial stage is eight decision-makers and no dimension of it can reach ten),
   and the pilot count and the price line the landing's card draws are there. Refused -> nothing is written.
4. `write` -- one JSON a read under `out_dir`, and `manifest.json` (FR-4): `{entry, corpus, exportedAt, cloud, files}`.
   Files a previous manifest listed are removed first, so a re-run never leaves a batch of the last run behind; the
   directory itself and anything the manifest did not list are left alone.

It lives in `evals/` and not in `harness/` because it refuses -- the gate is an assertion about the product's
answer, which `harness/` never makes.

Spec 060 FR-2's *Person 1* ... *Person n* aliasing: superseded by 061, 2026-10-22 (the founder's word: the sample keeps
its people's real-looking names; emails, the founder and tokens are still withheld).
"""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

#: The variable that turns the export on (FR-1), and nothing else does.
EXPORT_VAR = "KEEL_SAMPLE_EXPORT"

#: FR-1's reads, in the order they are taken and listed: the path under `/v2/projects/{id}/`.
TOP_READS = ("overview", "plan", "standings", "roles", "people", "readings", "invitations")

#: FR-2's word for a token or a link.
WITHHELD = "withheld"

#: FR-3 (the corpus's verdicts, read off the entry) and the card's three figures (§18.8).
DECISION_LABEL = "BUILD_BUT_CHANGE"
#: FR-3's n as the spec writes it. 05-paidly cannot meet it (commercial n 8, three problem / solution dimensions 9:
#: `expected.standings`), so the gate holds each asked dimension to the entry's own n instead and reports every
#: dimension under this one by name (judgement call 1) -- the founder's to overrule in one line.
SPEC_MIN_N = 10
#: The statuses a dimension carries no n under (`BriefFacts.decision` skips them too).
NOT_ASKED = ("LEFT_OUT", "NOT_ASKED_YET")

MANIFEST = "manifest.json"

#: A link a stranger opens (`/v2/i/<token>` on the wire, `/i/<token>` on keel-web).
_LINK = re.compile(r"(?:https?://[^\s\"']*)?/(?:v2/)?i/([A-Za-z0-9_\-]{8,})[^\s\"']*")
_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


class SampleRefused(AssertionError):
    """FR-3: the export refuses, its reasons named. Nothing was written."""

    def __init__(self, reasons: list[str]):
        self.reasons = list(reasons)
        super().__init__("the sample export refuses: " + "; ".join(self.reasons))


def wanted(env: dict | None = None) -> Path | None:
    """The export directory `KEEL_SAMPLE_EXPORT` names, or `None` when it is unset or empty (FR-1, FR-5)."""
    value = ((os.environ if env is None else env).get(EXPORT_VAR) or "").strip()
    return Path(value).expanduser() if value else None


# ------------------------------------------------------------------------------------------------ 1. capture

def capture(get: Callable[[str], Any], project_id: str) -> dict[str, Any]:
    """`{key: payload}` -- every read FR-1 names, through `get` (the founder session's `Journey.get`), keyed by the
    path under `/v2/projects/{id}/` with the id removed. Batches in the order `readings` lists them; invitations in
    the register's order (newest first, as served)."""
    base = f"/v2/projects/{project_id}"
    reads: dict[str, Any] = {}
    for name in TOP_READS:
        reads[name] = get(f"{base}/{name}")
    for batch_id in batch_ids(reads["readings"]):
        reads[f"readings/{batch_id}"] = get(f"{base}/readings/{batch_id}")
    for invitation_id in invitation_ids(reads["invitations"]):
        reads[f"invitations/{invitation_id}"] = get(f"{base}/invitations/{invitation_id}")
    return reads


def batch_ids(readings: Any) -> list[str]:
    """The batches `GET readings` lists (a bare array, newest first)."""
    rows = readings if isinstance(readings, list) else (readings or {}).get("batches") or []
    return [r["batchId"] for r in rows if isinstance(r, dict) and r.get("batchId")]


def invitation_ids(invitations: Any) -> list[str]:
    """The links `GET invitations` lists (`InvitationsResponse.invitations`)."""
    rows = (invitations or {}).get("invitations") or [] if isinstance(invitations, dict) else invitations or []
    return [r.get("invitationId") or r.get("id") for r in rows
            if isinstance(r, dict) and (r.get("invitationId") or r.get("id"))]


def expected_keys(reads: dict[str, Any]) -> list[str]:
    """Every key FR-1 owes for these reads: the seven, a batch each, an invitation each."""
    return ([*TOP_READS]
            + [f"readings/{b}" for b in batch_ids(reads.get("readings"))]
            + [f"invitations/{i}" for i in invitation_ids(reads.get("invitations"))])


# ----------------------------------------------------------------------------------------------- 2. withhold

@dataclass
class Withheld:
    """FR-2's result: the reads with emails, the founder and tokens gone (the people's names kept, spec 061 FR-1), and
    what was taken out (for the run bundle only; never written beside the snapshot)."""
    reads: dict[str, Any]
    emails: list[str] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)


def _walk_strings(value: Any) -> Iterable[tuple[str | None, str]]:
    """Every `(key, string)` in a JSON value, depth first, in document order."""
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, str):
                yield k, v
            else:
                yield from _walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            if isinstance(v, str):
                yield None, v
            else:
                yield from _walk_strings(v)


def _tokens_in(reads: dict[str, Any], known: Iterable[str]) -> list[str]:
    """The invitation tokens to withhold: those the journey made (`known`) and any a link on the wire carries."""
    found = [t for t in known if t]
    for value in reads.values():
        for k, v in _walk_strings(value):
            for m in _LINK.finditer(v):
                found.append(m.group(1))
            if k == "token" and v:
                found.append(v)
    return sorted(set(found), key=found.index)


def withhold(reads: dict[str, Any], *, founder_name: str = "", founder_email: str = "",
             tokens: Iterable[str] = ()) -> Withheld:
    """FR-2 over a deep copy of `reads`; `tokens` are the tokens the journey made. No person's name is touched
    (spec 061 FR-1)."""
    out = copy.deepcopy(reads)
    withheld_tokens = _tokens_in(out, tokens)
    token_res = [re.compile(re.escape(t)) for t in sorted(withheld_tokens, key=len, reverse=True)]
    founder_res = [re.compile(rf"(?<!\w){re.escape(s)}(?!\w)") for s in (founder_email, founder_name) if s]
    emails: list[str] = []

    def text(key: str | None, value: str) -> str | None:
        """The string as written, or `None` to drop the key it sits under."""
        if founder_name and value.strip() == founder_name or founder_email and value.strip() == founder_email:
            return None
        if key in ("url", "link", "href") and _LINK.search(value):
            return WITHHELD
        if key == "token":
            return WITHHELD
        for rx in founder_res:
            value = rx.sub("", value)
        value = _LINK.sub(WITHHELD, value)
        for rx in token_res:
            value = rx.sub(WITHHELD, value)
        for found in _EMAIL.findall(value):
            emails.append(found)
        value = _EMAIL.sub("", value)
        return value

    def walk(value: Any) -> Any:
        if isinstance(value, dict):
            kept = {}
            for k, v in value.items():
                if k == "email":
                    if isinstance(v, str) and v:
                        emails.append(v)
                    continue
                if isinstance(v, str):
                    new = text(k, v)
                    if new is None:
                        continue
                    kept[k] = new
                else:
                    kept[k] = walk(v)
            return kept
        if isinstance(value, list):
            items = []
            for v in value:
                if isinstance(v, str):
                    new = text(None, v)
                    if new is not None:
                        items.append(new)
                else:
                    items.append(walk(v))
            return items
        return value

    return Withheld(reads={k: walk(v) for k, v in out.items()}, emails=sorted(set(emails)), tokens=withheld_tokens)


def _hits(written: str, words: Iterable[str]) -> list[str]:
    """The words of `words` that `written` carries, whole words only."""
    return sorted({w for w in words if w and re.search(rf"(?<!\w){re.escape(w)}(?!\w)", written)})


def survivors(written: str, *, founder_name: str, founder_email: str,
              emails: Iterable[str] = (), tokens: Iterable[str] = ()) -> dict[str, list[str]]:
    """FR-2's grep: every email, founder word and token still in `written` (the whole output, read back). Empty is
    the pass. The people's names are not checked (spec 061 FR-2): they are kept."""
    return {k: v for k, v in {
        "emails": _hits(written, emails) + (["an address"] if _EMAIL.search(written) else []),
        "founder": _hits(written, [founder_name, founder_email]), "tokens": _hits(written, tokens),
    }.items() if v}


def names_kept(written: str, people: Iterable[str]) -> list[str]:
    """Spec 061 FR-2: the entry's people whose names `written` carries, in the entry's order. Measured and recorded,
    never gating (060 FR-3's gate is unchanged)."""
    found = set(_hits(written, people))
    return [p for p in people if p in found]


# --------------------------------------------------------------------------------------------------- 3. gate

def _standings(reads: dict[str, Any]) -> dict:
    return reads.get("standings") or {}


def card(reads: dict[str, Any]) -> dict:
    """The three figures the landing's card draws (§18.8), as the snapshot carries them: the decision label, the
    pilot count, the price line. They are on `standings` (`facts.decision`, `pilot`, `priceMedian`), which is what the
    report's Overview reads; `GET overview` carries none of them (judgement call 2)."""
    standings = _standings(reads)
    decision = (standings.get("facts") or {}).get("decision") or {}
    pilot = standings.get("pilot") or {}
    price = standings.get("priceMedian") or {}
    return {"decision": decision.get("label"), "howSure": decision.get("howSure"),
            "smallestN": decision.get("smallestN"),
            "pilot": ({k: pilot.get(k) for k in ("optedIn", "finished", "percent")} if pilot else None),
            "price": ({k: price.get(k) for k in ("edgeSaid", "chose", "n")} if price else None)}


def dimension_ns(reads: dict[str, Any]) -> dict[str, tuple[int | None, str | None]]:
    """`{dimension: (n, status)}` over every dimension the standings carry."""
    return {d.get("dimension"): (d.get("n"), d.get("status"))
            for v in _standings(reads).get("vectors") or [] for d in v.get("dimensions") or []}


def gate(reads: dict[str, Any], expected: dict) -> tuple[list[str], dict]:
    """FR-3: `(reasons, measured)` -- `reasons` empty is the pass. `expected` is the entry's `expected` block
    (`vector_verdicts`, `standings`)."""
    reasons: list[str] = []
    standings = _standings(reads)
    figures = card(reads)
    if figures["decision"] != DECISION_LABEL:
        reasons.append(f"the decision label is {figures['decision']!r}, not {DECISION_LABEL}")
    want_verdicts = {v: (w or {}).get("verdict") for v, w in (expected.get("vector_verdicts") or {}).items()}
    have_verdicts = {v.get("vector"): v.get("verdict") for v in standings.get("vectors") or []}
    if not want_verdicts:
        reasons.append("the entry records no expected.vector_verdicts to hold the stages to")
    for vector, want in want_verdicts.items():
        if have_verdicts.get(vector) != want:
            reasons.append(f"{vector} reads {have_verdicts.get(vector)!r}, the corpus expects {want}")
    ns = dimension_ns(reads)
    want_n = {k: (v or {}).get("n") for k, v in (expected.get("standings") or {}).items()}
    asked = {k: n for k, (n, status) in ns.items() if status not in NOT_ASKED}
    if not asked:
        reasons.append("no dimension was asked")
    for key, n in asked.items():
        floor = want_n.get(key)
        if floor is None:
            reasons.append(f"{key} is on the wire and not in the entry's expected.standings")
        elif not isinstance(n, int) or n < floor:
            reasons.append(f"{key} has n {n}, the corpus expects {floor}")
    for key in want_n:
        if key not in asked:
            reasons.append(f"{key} is in the entry's expected.standings and was not asked ({ns.get(key)})")
    pilot = figures["pilot"]
    if not pilot or not all(isinstance(pilot.get(k), int) for k in ("optedIn", "finished")) \
            or not pilot["finished"]:
        reasons.append(f"no pilot count on the standings ({standings.get('pilot')!r})")
    price = figures["price"]
    if not price or not (price.get("edgeSaid") or "").strip():
        reasons.append(f"no price line on the standings ({standings.get('priceMedian')!r})")
    measured = {"card": figures, "verdicts": have_verdicts,
                "n": {k: n for k, n in asked.items()},
                f"under {SPEC_MIN_N}": sorted(k for k, n in asked.items() if isinstance(n, int) and n < SPEC_MIN_N)}
    return reasons, measured


# -------------------------------------------------------------------------------------------------- 4. write

def _dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def cloud_sha(keel_cloud: Path | None) -> str | None:
    """keel-cloud's commit the stack ran (`git rev-parse HEAD` of the checkout `stack.toml` names), or `None`."""
    if keel_cloud is None or not Path(keel_cloud).is_dir():
        return None
    try:
        out = subprocess.run(["git", "-C", str(keel_cloud), "rev-parse", "HEAD"], capture_output=True,
                             encoding="utf-8", errors="replace", timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return out or None


def write(out_dir: Path, reads: dict[str, Any], *, entry_id: str, corpus_revision: int,
          cloud: str | None, exported_at: str | None = None) -> dict:
    """The snapshot under `out_dir` (one `<key>.json` a read) and its `manifest.json`; returns the manifest. Files a
    previous manifest in `out_dir` listed are removed first (never the directory, never a file it did not list)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    previous = out_dir / MANIFEST
    if previous.is_file():
        try:
            stale = json.loads(previous.read_text(encoding="utf-8")).get("files") or []
        except (OSError, ValueError):
            stale = []
        for rel in stale:
            path = (out_dir / rel).resolve()
            if out_dir.resolve() in path.parents and path.is_file():
                path.unlink()
    files = []
    for key, payload in reads.items():
        rel = f"{key}.json"
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_dumps(payload), encoding="utf-8")
        files.append(rel)
    manifest = {"entry": entry_id, "corpus": corpus_revision,
                "exportedAt": exported_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "cloud": cloud, "files": files}
    previous.write_text(_dumps(manifest), encoding="utf-8")
    return manifest


def size_of(out_dir: Path, manifest: dict) -> int:
    """The snapshot's bytes: every listed file and the manifest."""
    out_dir = Path(out_dir)
    return sum((out_dir / rel).stat().st_size for rel in [*manifest["files"], MANIFEST])


# ---------------------------------------------------------------------------------------------- the one step

def export_sample(j, out_dir: Path, *, run_dir: Path | None = None, gated: bool = True) -> dict:
    """FR-1 to FR-4 on a journey: capture the founder's reads, withhold, gate, write. Raises `SampleRefused` (nothing
    written) when the gate refuses or a name, email or token survives; returns `{manifest, size, card, ...}`. The
    reads as received go into the run bundle (`run_dir`, gitignored) and nowhere else.

    `gated=False` is spec 062's (the back-test: FR-3, *no verdict gate* -- 060 FR-3 is golden-only, and there the
    verdict is the finding): the gate's reading is recorded as a note, what a golden gate would have said beside it, and
    never refuses. The withholding and its grep are unchanged."""
    out_dir = Path(out_dir)
    founder = getattr(j, "founder_identity", None)
    founder_name = getattr(founder, "name", "") or ""
    founder_email = getattr(founder, "email", "") or ""
    people = [p.person for p in j.people]
    with j.recorder.step(f"sample (spec 060 FR-1): the founder's reads of the finished {j.entry.id} project, one a "
                         "path under /v2/projects/{id}/ -- overview, plan, standings, roles, people, readings and "
                         "every batch, invitations and every link", party="founder", kind="protocol") as h:
        reads = capture(j.get, j.project_id)
        missing = [k for k in expected_keys(reads) if k not in reads]
        h.record_wire({"project": j.project_id, "reads": list(TOP_READS)},
                      {"keys": list(reads), "batches": len(batch_ids(reads["readings"])),
                       "invitations": len(invitation_ids(reads["invitations"])), "missing": missing})
        assert not missing, missing
    if run_dir is not None:
        (Path(run_dir) / "sample-reads.json").write_text(_dumps(reads), encoding="utf-8")
    if not gated:
        with j.recorder.step("sample (spec 062 FR-3): no verdict gate on a back-test -- the card as the wire reads it, "
                             "recorded; the verdict is the finding", party="stack", kind="note") as h:
            reasons, measured = gate(reads, j.entry.expected)
            h.record_wire({"gated": False}, {**measured, "what a golden gate would have said": reasons})
        reasons = []
    else:
        with j.recorder.step("sample (FR-3): the verdict the corpus expects -- Build, but change it; PROBLEM and "
                             "SOLUTION holding up, COMMERCIAL not; every asked dimension at the entry's own n; the "
                             "pilot count and the price line the landing's card draws", party="stack",
                             kind="assert") as h:
            reasons, measured = gate(reads, j.entry.expected)
            h.record_assert({"decision": DECISION_LABEL,
                             "verdicts": {v: (w or {}).get("verdict")
                                          for v, w in (j.entry.expected.get("vector_verdicts") or {}).items()},
                             "pilot": "present", "price": "present", "reasons": []},
                            {**measured, "reasons": reasons})
    if reasons:
        raise SampleRefused(reasons)
    with j.recorder.step("sample (FR-2, spec 061): the people's names kept as served; emails, the founder's name and "
                         "email gone; tokens and links read withheld -- and none of those survives a grep of the "
                         "whole output", party="stack", kind="assert") as h:
        done = withhold(reads, founder_name=founder_name, founder_email=founder_email,
                        tokens=[*(getattr(j, "tokens", {}) or {}).values()])
        written = "".join(_dumps(v) for v in done.reads.values())
        left = survivors(written, founder_name=founder_name, founder_email=founder_email, emails=done.emails,
                         tokens=done.tokens)
        kept = names_kept(written, people)
        h.record_assert({"survivors": {}},
                        {"survivors": left, "names kept": f"{len(kept)} of {len(people)}",
                         "emails removed": len(done.emails), "tokens withheld": len(done.tokens)})
    if left:
        raise SampleRefused([f"FR-2: {k} survive the withholding: {v}" for k, v in left.items()])
    with j.recorder.step(f"sample (FR-4): the snapshot written under {out_dir} with manifest.json",
                         party="stack", kind="protocol") as h:
        cloud = cloud_sha(getattr(getattr(j, "stack", None), "keel_cloud", None))
        manifest = write(out_dir, done.reads, entry_id=j.entry.id, corpus_revision=j.entry.revision, cloud=cloud)
        size = size_of(out_dir, manifest)
        h.record_wire({"dir": str(out_dir)},
                      {"files": len(manifest["files"]), "bytes": size, "manifest": {
                          k: v for k, v in manifest.items() if k != "files"}, "card": measured["card"]})
    return {"manifest": manifest, "size": size, "card": measured["card"], "dir": str(out_dir),
            f"under {SPEC_MIN_N}": measured[f"under {SPEC_MIN_N}"], "people": len(kept)}


# ------------------------------------------------------------------------------------------ S-006's one seam

@dataclass
class Pending:
    """The export as S-006 carries it: `take` at the twenty answers (judgement call 3), `settle` after the journey's
    own marks are scored -- so a refusal is named with every S-006 mark already measured, and still fails the run
    (exit 1, FR-3)."""
    out_dir: Path
    run_dir: Path | None = None
    result: dict | None = None
    refused: SampleRefused | None = None

    def take(self, j) -> None:
        try:
            self.result = export_sample(j, self.out_dir, run_dir=self.run_dir)
        except SampleRefused as refusal:
            self.refused = refusal
        if self.run_dir is not None:
            record = self.result or {"refused": self.refused.reasons if self.refused else None}
            (Path(self.run_dir) / "sample.json").write_text(_dumps(record), encoding="utf-8")

    def settle(self) -> dict:
        import pytest                                       # noqa: PLC0415 -- the seam alone fails a test
        if self.refused is not None:
            pytest.fail(str(self.refused), pytrace=False)
        if self.result is None:
            pytest.fail("the sample export never ran: the journey ended before its twenty answers were read",
                        pytrace=False)
        r = self.result
        print(f"\nsample: {len(r['manifest']['files'])} files, {r['size']:,} bytes, under {r['dir']}"
              f"\nsample: decision {r['card']['decision']}, pilot {r['card']['pilot']}, price {r['card']['price']}")
        return r


def pending(run_dir: Path | None = None, env: dict | None = None) -> Pending | None:
    """S-006's export when `KEEL_SAMPLE_EXPORT` names a directory, else `None` (FR-1, FR-5)."""
    out_dir = wanted(env)
    return None if out_dir is None else Pending(out_dir=out_dir, run_dir=run_dir)
