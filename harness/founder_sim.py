"""The scripted founder simulator for the shaping gauntlet's Layer 2 (specs/shaping-eval-design.md
§1). Speaks only vague openers and a small fact bank released strictly on keyword-matched probes
-- design's own words: "A fact never asked for is never given. A founder simulator never
volunteers."

This module never sees harness/scenario/stack state -- it reads only the agent's own turn text
(design §2's contamination pass: "the simulator's script and fact bank are never in its
context" -- meaning the *agent's*; this module is the script, and it must stay ignorant of
anything except what the agent itself just said).

Judgement calls (recorded here, not tuned later to make a run pass -- design §2 names exactly
this temptation as the thing to guard against):

- The five fact categories are the design's own ("who/segment", "frequency/how often/when",
  "cost/time/long", "mechanism/how/what does it do", "price/pay/charge"); the literal keyword
  lists inside each category are this module's own choice, not quoted from the design doc.
- Checked in priority order (mechanism, frequency, cost, price, who) so a turn naming several
  cues resolves to the most specific one -- "how does it work" should earn mechanism, not
  accidentally read as a frequency probe because it contains "how".
- A fact already earned is not re-released as "new": a repeat probe gets a short echo of the
  same fact (`ProbeOutcome.newly_earned=False`), so a transcript honestly shows exactly one earn
  per fact -- SHP-1/SHP-2 (harness/shaping_scoring.py) both key off "earned", not "matched".
- Unmatched turns deflect through a small, fixed, cycling set of natural non-answers -- never
  random (a stackless test needs a deterministic simulator) -- and never volunteer anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PROBLEM = "PROBLEM"
SOLUTION = "SOLUTION"
COMMERCIAL = "COMMERCIAL"
ASSUMPTIONS = "ASSUMPTIONS"

STAGE_OPENERS: dict[str, str] = {
    PROBLEM: "Restaurants struggle with inventory.",
    SOLUTION: "I'll build an app for it.",
    COMMERCIAL: "I guess people would pay for it.",
    ASSUMPTIONS: "Sure, whatever you think is worth checking -- you're the expert here.",
}


@dataclass(frozen=True)
class Probe:
    fact_id: str
    patterns: tuple[str, ...]
    fact_text: str


# Priority order matters (module docstring): mechanism before frequency before cost before price
# before who, so an overlapping cue like "how" resolves to the most specific probe a turn's own
# phrasing actually intends, never to a generic one that merely happens to come first.
PROBES: tuple[Probe, ...] = (
    Probe("mechanism", (
        "mechanism", "how does it work", "how would it work", "how does the tool",
        "how does this work", "walk me through how", "what does it do", "what would it do",
    ), "It scans the shelf counts and compares them against what the POS system already "
       "recorded, and flags whatever doesn't match."),
    Probe("frequency", (
        "how often", "frequency", "how frequently", "how many times a", "when does",
        "when do they", "when it happens", "when this happens",
    ), "Every month-end close."),
    Probe("cost", (
        "how long", "how much time", "time does it take", "how many hours", "what does it cost",
        "how much does it cost",
    ), "About 90 minutes each time."),
    Probe("price", (
        "price", "pricing", "pay", "charge", "willing to pay", "how much would they pay",
    ), "Maybe $99 a month, honestly not sure."),
    Probe("who", (
        "who ", "who's", "who is", "which segment", "which customer", "target customer",
        "target market", "which restaurant", "what kind of restaurant", "what type of restaurant",
    ), "Independent restaurant managers."),
)

FACT_IDS: tuple[str, ...] = tuple(p.fact_id for p in PROBES)

DEFLECTIONS: tuple[str, ...] = (
    "I'm not sure.",
    "You tell me, you're the expert here.",
    "Hmm, good question -- I don't really know.",
    "Not sure, honestly.",
    "I haven't thought about it that precisely.",
)


@dataclass
class ProbeOutcome:
    reply: str
    fact_id: str | None  # the fact this turn's probe targeted, if any pattern matched
    newly_earned: bool  # True only the first time this fact is ever released this run


@dataclass
class FounderSimulator:
    """One instance per gauntlet run. Stateful: tracks which facts have already been earned (and
    on which turn) so a repeat probe echoes rather than re-"reveals", and cycles deflections
    deterministically rather than randomly (a stackless test needs a reproducible simulator).
    """

    earned: dict[str, int] = field(default_factory=dict)  # fact_id -> turn index first earned
    _deflection_i: int = field(default=0, repr=False)
    turn_index: int = 0

    def opener(self, stage: str) -> str:
        """The vague line this stage opens with -- never itself a probe match (design's "opens
        vague, per stage"), and never containing any fact text (checked by
        tests/test_founder_sim.py)."""
        return STAGE_OPENERS[stage]

    def respond(self, agent_turn: str) -> ProbeOutcome:
        """One founder reply to the agent's last message. `agent_turn` is the agent's own words
        -- the only thing this method ever reads."""
        self.turn_index += 1
        lowered = (agent_turn or "").lower()
        # M14's continue-or-new question is a real founder decision, not a fact -- answering it
        # is fidelity (a mute founder here strands the agent on whatever project already exists,
        # which is exactly how the second gauntlet run scored a dirty-stack ghost).
        if ("new project" in lowered or "existing project" in lowered
                or "continue with" in lowered or "start a new" in lowered):
            return ProbeOutcome("A new project, please -- this is a fresh idea.", None, False)
        for probe in PROBES:
            if any(pattern in lowered for pattern in probe.patterns):
                if probe.fact_id in self.earned:
                    return ProbeOutcome(f"Like I said -- {probe.fact_text}", probe.fact_id, False)
                self.earned[probe.fact_id] = self.turn_index
                return ProbeOutcome(probe.fact_text, probe.fact_id, True)
        deflection = DEFLECTIONS[self._deflection_i % len(DEFLECTIONS)]
        self._deflection_i += 1
        return ProbeOutcome(deflection, None, False)

    def fact_text(self, fact_id: str) -> str:
        return next(p.fact_text for p in PROBES if p.fact_id == fact_id)

    def never_released(self) -> dict[str, str]:
        """Facts this simulator holds that were never earned this run -- SHP-2/SHP-7's own "never
        -released knowledge" (design's scoring table)."""
        return {p.fact_id: p.fact_text for p in PROBES if p.fact_id not in self.earned}
