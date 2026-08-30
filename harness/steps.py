"""The step() context manager: every step -- protocol call, browser action, assertion, or plain
note -- becomes one transcript.jsonl entry (data-model.md's transcript-entry shape). Screenshot
numbering lives here too, so harness/browser.py never has to track a counter of its own.
"""

from __future__ import annotations

import itertools
import json
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class StepRecord:
    seq: int
    ts: str
    kind: str  # protocol | browser | assert | note
    name: str
    party: str  # agent | founder | participant | stack
    ok: bool = True
    duration_s: float = 0.0
    error: str | None = None
    request: Any = None
    response: Any = None
    screenshots: list[str] = field(default_factory=list)


@dataclass
class StepHandle:
    """What `with recorder.step(...) as h:` hands the caller to enrich the record before it's
    written (finally, on the way out of the `with` block).
    """

    name: str
    party: str
    kind: str
    ok: bool = True
    error: str | None = None
    request: Any = None
    response: Any = None
    screenshots: list[str] = field(default_factory=list)

    def record_wire(self, request: Any, response: Any) -> None:
        """For a protocol step: the full request/response pair, JSON-serializable."""
        self.kind = "protocol"
        self.request = request
        self.response = response

    def record_assert(self, expected: Any, actual: Any) -> None:
        """For an assert step: what was expected vs. what was actually observed."""
        self.kind = "assert"
        self.request = expected
        self.response = actual

    def add_screenshot(self, filename: str) -> None:
        if self.kind == "note":
            self.kind = "browser"
        self.screenshots.append(filename)

    def fail(self, error: str) -> None:
        self.ok = False
        self.error = error


class Recorder:
    """One per run: owns transcript.jsonl and the screenshots/ numbering for a run bundle."""

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.screenshots_dir = run_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.transcript_path = run_dir / "transcript.jsonl"
        # Per-instance, not a module global: a second Recorder created elsewhere in the same
        # process (e.g. another test) must not perturb this one's numbering.
        self._seq = itertools.count(1)
        self._shot_seq = itertools.count(1)
        self.failed_step: str | None = None

    def next_screenshot_name(self, slug: str) -> str:
        n = next(self._shot_seq)
        safe = "".join(c if (c.isalnum() or c in "-_") else "-" for c in slug).strip("-")[:60] or "step"
        return f"{n:03d}-{safe}.png"

    def screenshot_path(self, filename: str) -> Path:
        return self.screenshots_dir / filename

    def _append(self, record: StepRecord) -> None:
        with self.transcript_path.open("a") as f:
            f.write(json.dumps(asdict(record), default=str) + "\n")
        if not record.ok and self.failed_step is None:
            self.failed_step = record.name

    @contextmanager
    def step(self, name: str, *, party: str = "stack", kind: str = "note") -> Iterator[StepHandle]:
        """Appends one transcript entry when the `with` block exits, pass or fail. An exception
        raised inside the block is recorded (ok=False, error=str(exc)) and then re-raised, so a
        crashed scenario still leaves a partial, honest transcript.
        """
        seq = next(self._seq)
        started = time.monotonic()
        handle = StepHandle(name=name, party=party, kind=kind)
        try:
            yield handle
        except Exception as exc:  # noqa: BLE001 - re-raised after recording
            handle.ok = False
            handle.error = handle.error or f"{type(exc).__name__}: {exc}"
            raise
        finally:
            duration = time.monotonic() - started
            self._append(StepRecord(
                seq=seq, ts=_now_iso(), kind=handle.kind, name=handle.name, party=handle.party,
                ok=handle.ok, duration_s=duration, error=handle.error,
                request=handle.request, response=handle.response, screenshots=handle.screenshots,
            ))

    def note(self, name: str, *, party: str = "stack", ok: bool = True, error: str | None = None) -> None:
        """A one-line record with no request/response/screenshot -- e.g. a scenario milestone."""
        with self.step(name, party=party, kind="note") as h:
            if not ok:
                h.fail(error or "unspecified failure")
