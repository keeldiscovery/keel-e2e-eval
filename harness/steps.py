"""The step() context manager: every step -- protocol call, browser action, assertion, or plain
note -- becomes one transcript.jsonl entry (data-model.md's transcript-entry shape). Screenshot
numbering lives here too, so harness/browser.py never has to track a counter of its own.

002-eval-scoring adds interaction tagging (data-model.md's "Interaction tag (on StepRecord)"):
steps opened inside `Recorder.interaction(...)` carry an `{id, type}` tag that
harness/interactions.py later groups into scored interactions. Untagged steps (stack plumbing --
`load_skill`, `check_mcp_reachable`, the stack-lifecycle notes) belong to no interaction, and a
transcript with no tags at all (a pre-002 bundle) re-scores as "no interactions found" rather than
crashing (analysis finding A2; harness/rubric.py and harness/interactions.py both treat "no
interaction tags" as an empty-but-valid result).
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
    # data-model.md: "{id, type}", optional -- untagged steps (stack plumbing) belong to no
    # interaction. A plain dict, not a nested dataclass, so it round-trips through
    # json.dumps(asdict(...)) untouched and so `Recorder.retag_interaction` can mutate the id's
    # `type` in every already-appended record that shares it (see that method's docstring).
    interaction: dict | None = None
    # source -> text this step rendered/observed (e.g. "stage_screen", "agent_echo", "display"),
    # folded by harness/interactions.py into the owning interaction's captured_text -- the
    # substrate the ORIENTATION/GUIDANCE/CLARITY/FIDELITY checks read. Empty for steps that
    # capture nothing (most protocol/assert plumbing).
    captured_text: dict[str, str] = field(default_factory=dict)


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
    interaction: dict | None = None
    captured_text: dict[str, str] = field(default_factory=dict)

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

    def capture_text(self, source: str, text: str | None) -> None:
        """Stashes one piece of rendered/observed text under `source` for
        harness/interactions.py to fold into the owning interaction's captured_text. Appends
        (newline-joined) rather than overwrites, so a step that captures the same source twice
        (e.g. a page visited, then re-visited after an approval) keeps both observations rather
        than silently dropping the first.
        """
        text = (text or "").strip()
        if not text:
            return
        existing = self.captured_text.get(source)
        self.captured_text[source] = f"{existing}\n{text}" if existing else text

    def fail(self, error: str) -> None:
        self.ok = False
        self.error = error


@dataclass
class _InteractionTag:
    id: str
    type: str


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
        self._interaction_seq = itertools.count(1)
        self.failed_step: str | None = None
        self._active_interaction: _InteractionTag | None = None
        # Mirrors every appended record (dict form) so `retag_interaction` can patch a tag after
        # the fact and rewrite the file -- needed because an agent-cycle vs. agent-handoff
        # interaction is only knowable once get_next's response has already been durably
        # appended (see harness/driver.py's `advance_one`).
        self._records: list[dict] = []

    def next_screenshot_name(self, slug: str) -> str:
        n = next(self._shot_seq)
        safe = "".join(c if (c.isalnum() or c in "-_") else "-" for c in slug).strip("-")[:60] or "step"
        return f"{n:03d}-{safe}.png"

    def screenshot_path(self, filename: str) -> Path:
        return self.screenshots_dir / filename

    def _append(self, record: StepRecord) -> None:
        record_dict = asdict(record)
        self._records.append(record_dict)
        with self.transcript_path.open("a") as f:
            f.write(json.dumps(record_dict, default=str) + "\n")
        if not record.ok and self.failed_step is None:
            self.failed_step = record.name

    def _rewrite_file(self) -> None:
        with self.transcript_path.open("w") as f:
            for record_dict in self._records:
                f.write(json.dumps(record_dict, default=str) + "\n")

    @contextmanager
    def step(self, name: str, *, party: str = "stack", kind: str = "note") -> Iterator[StepHandle]:
        """Appends one transcript entry when the `with` block exits, pass or fail. An exception
        raised inside the block is recorded (ok=False, error=str(exc)) and then re-raised, so a
        crashed scenario still leaves a partial, honest transcript.
        """
        seq = next(self._seq)
        started = time.monotonic()
        tag = ({"id": self._active_interaction.id, "type": self._active_interaction.type}
               if self._active_interaction else None)
        handle = StepHandle(name=name, party=party, kind=kind, interaction=tag)
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
                interaction=handle.interaction, captured_text=handle.captured_text,
            ))

    def note(self, name: str, *, party: str = "stack", ok: bool = True, error: str | None = None) -> None:
        """A one-line record with no request/response/screenshot -- e.g. a scenario milestone."""
        with self.step(name, party=party, kind="note") as h:
            if not ok:
                h.fail(error or "unspecified failure")

    # ------------------------------------------------------------------------------ interactions

    def new_interaction_id(self) -> str:
        return f"I{next(self._interaction_seq):03d}"

    @contextmanager
    def interaction(self, type: str, interaction_id: str | None = None) -> Iterator[str]:
        """Opens an interaction scope (data-model.md): every step recorded inside -- including
        steps recorded by helper objects that hold this same Recorder -- is tagged `{id, type}`.
        Yields the id, so the caller can pass it to `retag_interaction` if the provisional type
        turns out to be wrong, or reuse it in a later `with recorder.interaction(..., id):` to
        fold more steps into the same interaction (e.g. a stage screen's open + its approve
        click are one reviewable interaction, not two).

        Scopes do not nest here (S-001 never opens one interaction while another is active), but
        restoring the previous value on exit keeps that possible without this module knowing
        about it.
        """
        interaction_id = interaction_id or self.new_interaction_id()
        previous = self._active_interaction
        self._active_interaction = _InteractionTag(interaction_id, type)
        try:
            yield interaction_id
        finally:
            self._active_interaction = previous

    def retag_interaction(self, interaction_id: str, new_type: str) -> None:
        """Fixes up every already-appended step tagged `interaction_id` to carry `new_type`
        instead. Exists for exactly one ambiguity: `get_next`'s response tells you whether this
        was an agent-cycle (an action to run) or an agent-handoff (nothing left for the agent to
        do) only *after* the call returns -- by which point that step is already durably
        appended. `harness/driver.py.advance_one` opens every cycle provisionally as
        "agent-cycle" and calls this to correct it to "agent-handoff" on the branch that turns
        out to be a handoff.
        """
        changed = False
        for record_dict in self._records:
            tag = record_dict.get("interaction")
            if tag and tag.get("id") == interaction_id and tag.get("type") != new_type:
                tag["type"] = new_type
                changed = True
        if changed:
            self._rewrite_file()
        if self._active_interaction is not None and self._active_interaction.id == interaction_id:
            self._active_interaction = _InteractionTag(interaction_id, new_type)
