"""Spec 151 FR-5: three stacks behind one interface. Each takes a script (and, at the audio level, its two rendered
tracks) and yields one event a turn: `{"t_emitted", "turn", "q", "verdict", "option", "tier", "state", "parts",
"usage"}` -- `t_emitted` the seconds after the turn's end the event was shown, `parts` its split (`wait`, `transcribe`,
`classify`), `usage` what it cost."""

from evals.copilot.stacks.audio_direct import AudioDirect
from evals.copilot.stacks.base import Stack, canned_events
from evals.copilot.stacks.running_state import RunningState
from evals.copilot.stacks.turn_by_turn import TurnByTurn

STACKS = {1: TurnByTurn, 2: RunningState, 3: AudioDirect}


def parse_stacks(raw: str | None) -> list[int]:
    if not raw:
        return [1, 2, 3]
    out = []
    for x in str(raw).split(","):
        x = x.strip()
        if x:
            if x not in ("1", "2", "3"):
                raise SystemExit(f"copilot-bench refuses: STACKS={raw!r} -- name stacks 1, 2 and/or 3")
            out.append(int(x))
    return sorted(set(out))


__all__ = ["STACKS", "Stack", "TurnByTurn", "RunningState", "AudioDirect", "canned_events", "parse_stacks"]
