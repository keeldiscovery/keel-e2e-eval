"""The bridge loop (design §12 item 1): THE production host shape, mirrored -- keel-skill's own
SKILL.md ("The relay" section, M15) teaches an agent host exactly this cycle: "The relay's poll is
the host's own mechanical loop, never something your reasoning drives... wakes your reasoning only
once a founder turn has actually arrived." `BridgeLoop.step` is that cycle: one mechanical
long-poll (no model tokens spent, design §8's hard rule), then -- only for founder turns the poll
actually surfaced -- one call to a `reasoning` callable per turn, then post whatever it replies.

`reasoning` is supplied by the caller and is the only thing that differs between contexts (module
docstring, design §12 item 1): a scenario's own deterministic payload builders in
`evals/test_s001_smoke.py` and friends (scripted, no LLM -- FR-003's rule extends to the relay), or
the real `claude` CLI in the gauntlet (`harness.agent_session.AgentSession.send`, wrapped by
`harness.gauntlet_bridge` -- see that module).

A lease refusal never retries (keel-skill's own words: "say so to the founder, and stop... never
contend for the lease") -- `LeaseRefused` is raised the moment either half of one `step()` is
refused, carrying the remedy prose so a caller can report it plainly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from harness.relay import AgentRelay, RelayError, RelayTurn


@dataclass
class BridgeReply:
    text: str
    kind: str = "message"
    payload: Any = None

    @classmethod
    def playback(cls, display: str, recorded: Any) -> "BridgeReply":
        """keel-skill SKILL.md's own words: "post `display` together with `recorded` as one
        playback turn" -- the same relay discipline M13's terminal-conversation playback already
        follows, new venue."""
        return cls(text=display, kind="playback", payload=recorded)

    def to_turn_input(self) -> dict:
        d: dict[str, Any] = {"kind": self.kind, "text": self.text}
        if self.payload is not None:
            d["payload"] = self.payload
        return d


ReasoningFn = Callable[[str], "BridgeReply | list[BridgeReply]"]


class LeaseRefused(RuntimeError):
    """A competing host session already holds this project's relay lease -- never contended,
    per keel-skill's own M15 ("stop rather than contend for the lease"). Carries the remedy prose
    the refusal itself named, so a caller can report it plainly (design §12 item 3's own words:
    "the lease refusing a second bridge plainly")."""

    def __init__(self, remedy: str):
        self.remedy = remedy
        super().__init__(remedy)


class BridgeLoop:
    """One bridge, one project. `step()` is the one mechanical/reasoning cycle a real host repeats
    forever; `run_until` repeats it until a caller-supplied condition is met."""

    def __init__(self, agent_relay: AgentRelay, reasoning: ReasoningFn):
        self.agent_relay = agent_relay
        self.reasoning = reasoning
        self.cursor = 0
        self.stopped = False
        self.stop_reason: str | None = None

    def poll_once(self) -> list[RelayTurn]:
        """One mechanical long-poll -- no model tokens spent here regardless of what it returns
        (design §8's hard rule). Returns only the founder turns this poll surfaced (an agent's own
        prior replies also ride the same turn stream once read back, but this loop never reacts to
        its own words)."""
        turns, self.cursor = self.agent_relay.poll(self.cursor)
        return [t for t in turns if t.author == "founder"]

    def process(self, founder_turns: list[RelayTurn]) -> list[RelayTurn]:
        """Wakes `self.reasoning` once per founder turn -- never per empty poll, the mechanical/
        model-driven boundary keel-skill's SKILL.md itself teaches (M15) -- and posts every reply
        this loop's own reasoning returns."""
        posted: list[RelayTurn] = []
        for turn in founder_turns:
            reply = self.reasoning(turn.text)
            replies = reply if isinstance(reply, list) else [reply]
            turn_inputs = [r.to_turn_input() for r in replies]
            if turn_inputs:
                posted.extend(self.agent_relay.post_turns(turn_inputs))
        return posted

    def step(self) -> list[RelayTurn]:
        try:
            founder_turns = self.poll_once()
        except RelayError as err:
            raise self._refusal_or_reraise(err) from err
        try:
            return self.process(founder_turns)
        except RelayError as err:
            raise self._refusal_or_reraise(err) from err

    def _refusal_or_reraise(self, err: RelayError) -> Exception:
        if err.rule == "relay-lease":
            self.stopped = True
            self.stop_reason = err.remedy or err.problem
            return LeaseRefused(self.stop_reason or "the relay lease was refused")
        return err

    def run_until(self, done: Callable[[], bool], *, max_steps: int = 200) -> None:
        """Repeats `step()` until `done()` is true. Raises `LeaseRefused` immediately (never
        retries) if a step is refused the lease, and `TimeoutError` if `max_steps` mechanical
        cycles pass without `done()` ever becoming true -- a caller bug (or a founder turn this
        loop's `reasoning` never actually answers), not a relay problem."""
        for _ in range(max_steps):
            if done():
                return
            self.step()
        raise TimeoutError(f"bridge loop did not satisfy its stop condition within {max_steps} steps")
