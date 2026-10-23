"""keel-cloud's pre-rendered AI interviewer, restated where this eval reads it (spec 044; keel-cloud 094, contract 16,
`InferenceCharge` 9, document 22): the charge rows, the faces (four since keel-cloud 110), the refusal codes, the
spoken order of a role's clips, the fixed lines code writes (design `ai-interviewer-prerendered-2026-10-15.md` FR-B),
and what the stack's fake renderer does (`FakeInterviewerRenders`: a one-second silent mp4 per clip after a 3 s virtual delay, 0.1 s a word, one
vendorRef failed once on request).

**No vendor is called and no money is spent.** The stack runs keel-cloud's defaults (`keel.v2.interviewer.renders =
fake`, `transcriber = fake`); the one live render test lives in keel-cloud (`HeyGenRenderLiveTest`, tag `live`) and is
never run here.

Spec 050 (keel-cloud 101): the framing lines -- the opening says whose idea it is and the route, the problem and the
idea passages close on *Take a moment* and the count -- restated from `PassageComposer` (cloud-docs `3a6b045`).

Spec 051 (keel-cloud 103, contract 19, the interview side): **the ladder** -- the eight rungs of design §2 that carry
the one follow-up, in registry order, copied from the registry's `follow_up` blocks (cloud-docs `4cda99a`) -- and
`first_rung`, which walks a person's own picks up it the way `Ladder.rungOf` does. Since 103's amendment the server
walks and composes (`POST .../interview/follow-up`); this copy is the **independent check** of that walk, not a mirror
of the page (the page walks nothing). `fill` composes the question's text the way `FollowUpComposer` fills it, from
the served labels and the founder's own words, so the walk can hold the route's `text` (and the screen's) to it. The
FOLLOW_UP clip kind (one a rung a role's link walks: *One last thing.* and the rung's spoken wording) is unspoken --
it plays only when the walk finds its rung.

This module is machinery: it asserts nothing. `evals/interviewer_leg.py` and `evals/interviewer_marks.py` judge with it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# ------------------------------------------------------------------------------------- charge v9 (FR-F)

#: keel-cloud `InferenceCharge.VERSION`, which every HOLD written carries: 9 since 094, 10 since 104 (BRIEF out,
#: THEMES in; spec 052 -- the interviewer's two rows did not move), **11** since 125 (EXAMPLE_MATCH at 0, never held;
#: no price moved).
PRICE_VERSION = 11
#: The first recording, written at lock (or, on a project with none, at the first face chosen) -- and the change.
RECORDING = "INTERVIEWER_RECORDING"
CHANGE = "INTERVIEWER_CHANGE"
ACTIONS = (RECORDING, CHANGE)
#: Both rows are a flat 400 credits (094 judgement call 2) and pass through 2,000,000 µUSD.
CREDITS = 400
COST_MICRO_USD = 2_000_000
#: `InterviewerView.changePrice` / `InterviewerFaces.changePrice`: the one price the wire carries.
CHANGE_PRICE = CREDITS

# ------------------------------------------------------------------------------------------ faces (FR-A)

#: Spec 058 (keel-cloud 110, contract 23): four photo avatars, each with its own voice, LIVIA preselected where JUDY
#: was. 094's five studio faces are retired: a pick of one is 422 FACE_UNKNOWN (`RETIRED`).
FACES = ("LIVIA", "JIA", "MARIEKE", "CHUKWU")
FACE_NAMES = {"LIVIA": "Livia", "JIA": "Jia", "MARIEKE": "Marieke", "CHUKWU": "Chukwu"}
PRESELECTED = "LIVIA"
RETIRED = ("JUDY", "JIN", "ANNA", "DAPHNE", "TITO")
#: Spec 058 FR-2 / FR-3 (keel-web 087): each face's hello is one clip of 4.6-5.4 s; one longer than this is not it.
HELLO_MAX_S = 8.0


def preview_path(face: str) -> str:
    """`InterviewerFace.previewPath`: the still keel-web ships, never a vendor URL."""
    return f"/interviewer/faces/{face.lower()}.webp"


def hello_path(face: str) -> str:
    """`InterviewerFace.helloPath` (keel-cloud 110): the face's hello clip keel-web ships, served as `helloUrl`."""
    return f"/interviewer/faces/{face.lower()}.mp4"


# ------------------------------------------------------------------------------ refusals (contract 16)

NOT_READY = "INTERVIEWER_NOT_READY"              # 409: an AI_INTERVIEWER / CHOICE link, or Try it yourself, too early
NEEDS_CREDITS = "INTERVIEWER_NEEDS_CREDITS"      # 422: the AI interviewer on an account on its own AI
FACE_UNKNOWN = "FACE_UNKNOWN"                    # 422: a face not in GET interviewer/faces
IN_FLIGHT = "INTERVIEWER_FAILED"                 # 409: changing who asks while a recording is still in flight
INSUFFICIENT = "INSUFFICIENT_CREDITS_FOR_INTERVIEWER"  # 422 CreditRefusal at POST interviewer/face
REFUSAL_STATUS = {NOT_READY: 409, NEEDS_CREDITS: 422, FACE_UNKNOWN: 422, IN_FLIGHT: 409, INSUFFICIENT: 422}
#: contract 16 `CreditRefusal.remedy` for the change.
INSUFFICIENT_REMEDY = "Changing who asks records the interviewer again, which is {required} credits. You have {available}."

# ---------------------------------------------------------------------------- the wire's fixed words

MARK = "Keel · AI interviewer"
FAILURE = "One of the clips could not be recorded."
RECORDING_STATES = ("NOT_RECORDED", "RECORDING", "READY", "FAILED")

# -------------------------------------------------------------------------- the scripts (FR-B, code)

#: keel-cloud 101 (cloud-docs master `3a6b045`, `PassageComposer`): the framing lines, copied word for word -- one
#: source, the composer's own constants (`tests/test_interviewer_marks.py` holds them to its source). The opening says
#: who speaks, whose idea it is (`{First}`: `Interview.founderFirstName` as served, else *The founder*), the route the
#: link takes and how to answer; the problem and the idea passages close on a beat to think, then the count.
INTRODUCED = "I'm Keel's interviewer. I'm an AI, not a person."
HOW_TO_ANSWER = "Say the answer that fits, or tap it."
FULL_ROUTE = "First the problem, then the idea, with a few questions about each."
#: 101 judgement call 3: the decision-maker's link opens with the idea, then the money side.
COMMERCIAL_ROUTE = "First the idea, then a few questions on the money side."
PROBLEM_CLOSE = "That's the problem. Take a moment with it."
SOLUTION_CLOSE = "That's the idea. Take a moment."
SOLUTION_OPENING = "Now the idea."
COMMERCIAL_OPENING = "Last, the money side."
FOUNDER_FALLBACK = "The founder"
#: `PassageComposer.NUMBER_WORDS`: the count said as a word up to twelve, digits above.
NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
                "twelve")
#: The opening before keel-cloud 101 (094's `OPENING`): what a recording made before it says -- the words the
#: backfill check seeds (spec 050 FR-5).
OPENING_BEFORE_101 = ("I'm Keel's interviewer. I'm an AI, not a person. I'll read each question and a few options. "
                      "Say the one that fits, or tap it.")


def _join(*parts: str | None) -> str:
    return " ".join(p.strip() for p in parts if p and p.strip())


def number(n: int) -> str:
    return NUMBER_WORDS[n] if 0 <= n < len(NUMBER_WORDS) else str(n)


def opening(first: str | None, commercial_link: bool = False) -> str:
    """`PassageComposer.opening`: *I'm Keel's interviewer. I'm an AI, not a person. {First} has an idea for a problem
    you may know. First the problem, then the idea, with a few questions about each. Say the answer that fits, or tap
    it.* -- the decision-maker's link says its own route."""
    founder = (first or "").strip() or FOUNDER_FALLBACK
    return _join(INTRODUCED, f"{founder} has an idea for a problem you may know.",
                 COMMERCIAL_ROUTE if commercial_link else FULL_ROUTE, HOW_TO_ANSWER)


def then(count: int, about: str) -> str:
    """`PassageComposer.then`: *Then I'll ask you four questions about it.* -- one question singular."""
    return f"Then I'll ask you {number(count)} {'question' if count == 1 else 'questions'} {about}."


def problem_passage(topic: str, count: int) -> str:
    """The PROBLEM clip: `{topic} That's the problem. Take a moment with it. Then I'll ask you {N} questions about it.`
    (`{N}`: part 1's items with the gate)."""
    return _join(topic, PROBLEM_CLOSE, then(count, "about it"))


def solution_close(count: int) -> str:
    """The SOLUTION clip's close, on the full link and the decision-maker's alike: `That's the idea. Take a moment.
    Then I'll ask you {N} questions on whether it would help you.` (it opens `Now the idea. {what} {how} {belief}`)."""
    return _join(SOLUTION_CLOSE, then(count, "on whether it would help you"))


#: 101's closes, as a recording made before 101 did not say them: `... I'll ask you {N} questions about that.`
_CLOSE_101 = re.compile(r"\s*That's the (problem|idea)\. Take a moment(?: with it)?\. Then I'll ask you (\S+) "
                        r"(questions?) .*$", re.S)


def before_101(kind: str, script: str) -> str:
    """What a passage of `kind` said before keel-cloud 101 (094 / 099's composer): the old opening; a problem or idea
    passage with its 101 close put back to *I'll ask you {N} questions about that.* The backfill check (spec 050
    FR-5) seeds these into a stored recording and watches the first read re-render them."""
    if kind == "OPENING":
        return OPENING_BEFORE_101
    m = _CLOSE_101.search(script or "")
    if not m:
        return script
    return f"{script[:m.start()]} I'll ask you {m.group(2)} {m.group(3)} about that."


#: The full link's opening when the interview serves no first name.
OPENING = opening(None)
DIDNT_CATCH = "I didn't catch that, could you say it again?"
PILOT_ASK = "Would you like to take part in the pilot?"
MORE = "And which one more?"
#: keel-cloud 099 FR-6 (contract 18): the generic "Is that right?" line, one a role, asked when the classifier is unsure.
IS_THAT_RIGHT = "Is that right?"

#: `ClipKind`, and the spoken order of one role's set (design §2.4; `ClipKind`'s own javadoc): the opening, then per
#: part its passage and its items (an item's follow-up right after it), the pilot ask, thanks. DIDNT_CATCH and, since
#: keel-cloud 099 (contract 18), IS_THAT_RIGHT have no place in the order; the composer writes them last.
#: Spec 051 (keel-cloud 103): FOLLOW_UP, last in the enum; the composer writes a role's between PILOT and THANKS.
KINDS = ("OPENING", "PROBLEM", "ITEM", "ITEM_MORE", "SOLUTION", "COMMERCIAL", "DIDNT_CATCH", "PILOT", "THANKS",
         "IS_THAT_RIGHT", "FOLLOW_UP")
#: The clips said only when an answer asks for them -- never in the spoken order (103: the follow-up, only when the
#: walk finds its rung).
UNSPOKEN = ("DIDNT_CATCH", "IS_THAT_RIGHT", "FOLLOW_UP")
PASSAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")
#: Which passage introduces a part, by the part's vector (`InterviewPart.vector` on the wire, or its number).
PASSAGE_OF_VECTOR = {"PROBLEM": "PROBLEM", "SOLUTION": "SOLUTION", "COMMERCIAL": "COMMERCIAL"}
PASSAGE_OF_PART = {1: "PROBLEM", 2: "SOLUTION", 3: "COMMERCIAL"}
#: The roles a clip is for (`RespondentLink`): the primary link's, and the decision-maker's commercial link's.
ROLES = ("PRIMARY", "COMMERCIAL_B2B")

# ------------------------------------------------------------------------------ the fake renderer (FR-C)

#: The stack's virtual delay (`application.yml` default for the stack) and the recorder's poll (FR-E).
FAKE_DELAY_S = 3
POLL_S = 10
#: Spec 044 judgement call 2: the fake's 3 s and the 10 s poll fit in this, so the leg waits no longer.
READY_WITHIN_S = 30
SECONDS_PER_WORD = 0.1
FAKE_CLIP = Path("src/main/resources/keel/interviewer/fake-clip.mp4")


def fake_clip_bytes(keel_cloud: Path) -> int | None:
    """The size of the one mp4 the fake hands back for every clip, read from keel-cloud's own resource."""
    path = Path(keel_cloud) / FAKE_CLIP
    return path.stat().st_size if path.is_file() else None


def words(text: str) -> int:
    return len([w for w in re.split(r"\s+", text or "") if w])


def fake_seconds(script: str) -> float:
    """What the fake reports as a clip's length (`FakeInterviewerRenders.seconds`): 0.1 s a word, to a tenth, never
    under the one second its file holds."""
    return max(1.0, round(words(script) * SECONDS_PER_WORD * 10) / 10.0)


# --------------------------------------------------------------------------------- reading a recording

# ------------------------------------------------------------------------- the ladder (spec 051, keel-cloud 103)

#: The registry's word for a rung whose against set is the founder's lock, read as `Compare` scores it (Price's
#: `ordinal_band`, Buyer and payer's `first_supports`): `FollowUpBlock.LOCK_RULE`.
LOCK_RULE = "lock_rule"
#: The keel-cloud commit of `Ladder.java` the copy below follows (spec 064 FR-7: keel-cloud 118's ladder, the
#: registry's `follow_up` blocks with their `also` stems; `tests/test_follow_up_ladder.py` holds it to the registry export
#: the stack runs).
LADDER_SHA = "f280c5ae"
#: Design §2, as the registry carries it since keel-cloud 118: `(dimension, against, text template, spoken wording)`, in
#: registry order. Purchase friction is a rung now (its quick / not-needed answers are against the fear); Adoption
#: friction's and Commitment's stems are the plain questions of 118 FR-4.
LADDER: tuple[tuple[str, tuple[str, ...] | str, str, str], ...] = (
    ("problem.importance", ("none_of_these",),
     "You picked {their_picks} over {founder_item}. What makes those more pressing?",
     "You put other difficulties ahead of this one. What makes those more pressing?"),
    ("problem.current_solution_satisfaction", ("outcome_1", "outcome_2"),
     "You said {their_answer}. What do you do today that makes it work?",
     "You said today's way works for you. What do you do that makes it work?"),
    ("solution.compatibility", ("only_with_help", "no"),
     "You said you couldn't {condition}. What got in the way?",
     "You said that step would be hard in your setup. What gets in the way?"),
    ("solution.relative_advantage", ("neutral", "negative"),
     "You said {benefit} would have made no difference to your last {occasion}. What would have?",
     "You said it would not have made much difference. What would have?"),
    ("solution.adoption_friction", ("probably_not", "no"),
     "What makes that too much?",
     "What makes that too much?"),
    ("commercial.price", LOCK_RULE,
     "You put it at {band}. What would make it worth more?",
     "You put it below what we asked. What would make it worth more?"),
    ("commercial.buyer_payer_alignment", LOCK_RULE,
     "Who had to agree, and what did they need to see?",
     "Who had to agree, and what did they need to see?"),
    ("commercial.purchase_friction", ("yes_quick", "not_needed"),
     "What did slow it down, if anything?",
     "What did slow it down, if anything?"),
    ("commercial.commitment", ("probably_not", "no"),
     "What would you start with instead?",
     "What would you start with instead?"),
)
RUNGS = tuple(r[0] for r in LADDER)
#: Keel-cloud 118 FR-4 (`FollowUpBlock.Also`): a rung's second stem, asked on the answers it names (the conditional yes,
#: the long purchase) -- `{dimension: (on, text template, spoken wording, heading)}`.
ALSO: dict[str, tuple[tuple[str, ...], str, str, str]] = {
    "solution.adoption_friction": (("yes_if_worth_it",), "What would make it clearly worth it to you?",
                                   "What would make it clearly worth it to you?", "What would make it clearly worth it?"),
    "commercial.purchase_friction": (("yes_long",), "What took the time?", "What took the time?",
                                     "What took the time?"),
    "commercial.commitment": (("yes_after_trying",), "What would {smaller_step} have to show you?",
                              "What would that first step have to show you?",
                              "What would the first step have to show?"),
}
#: Design §2's rungs with no question since keel-cloud 118 (a gate No ends the interview; a number has no why; derived).
NO_FOLLOW_UP = ("problem.prevalence", "problem.frequency", "commercial.existing_sacrifice", "commercial.ability_to_pay")
#: `PassageComposer.ONE_LAST_THING`: the FOLLOW_UP clip opens on it; the screens' kicker is *One last thing*.
ONE_LAST_THING = "One last thing."
FOLLOW_UP_KICKER = "One last thing"
#: Buyer and payer's fixed answers and the one that supports when "Nobody else" is tested (`Compare.BUYER_DECIDED_ALONE`)
#: -- with a named role tested the registry's `supports` (`had_to_agree`).
BUYER_ANSWERS = ("had_to_agree", "decided_alone", "someone_else_agreed", "someone_else_decided")
BUYER_ALONE = "decided_alone"
BUYER_SUPPORTS = ("had_to_agree",)
#: `PriceLadder.POINTS` and its escape below every band.
PRICE_POINTS = (1, 2, 5, 10, 20, 50, 100, 250, 500, 1_000, 2_500, 5_000, 10_000)
WOULD_NOT_PAY = "would_not_pay"
#: `FollowUpComposer.DEFAULTS` / `WOULD_NOT_PAY_BAND`: what a placeholder says when its words are missing.
FILL_DEFAULTS = {"{their_picks}": "other difficulties", "{founder_item}": "this one",
                 "{their_answer}": "today's way works", "{condition}": "do that", "{would}": "be hard",
                 "{benefit}": "it", "{occasion}": "time", "{effort}": "do that", "{band}": "less than we asked",
                 "{smaller_step}": "that first step"}   # keel-cloud FollowUpComposer.DEFAULTS (126 FR-5b: do that)
#: Design §2 *Rungs with no question* (`no_follow_up`), as the registry carries them since keel-cloud 118 / 115.
NO_FOLLOW_UP_WHY = {
    "problem.prevalence": "a No at the gate ends the interview",
    "problem.frequency": "a number has no why worth a question",
    "commercial.existing_sacrifice": "a number has no why worth a question",
    "commercial.ability_to_pay": "it is read from the cost and the price (or the budget item), never asked of the "
                                 "founder",
}
SPLIT_NOTE = "A split, not a no: it fits one group and not the other."
#: keel-web 095 (spec 064 FR-8b): *In their words* became *In their own words* (RAW only, with the served note);
#: *Keel is grouping what they said…* while GROUPING; *On their own* for the leftovers; the side marks.
IN_THEIR_WORDS = "In their own words"
GROUPING_LINE = "Keel is grouping what they said\u2026"
ON_THEIR_OWN_WORDS = "On their own"
SIDE_WORDS = {"FOR": "for", "AGAINST": "against", "APART": "apart"}
NOTHING_TO_READ_YET = "Nothing to read into yet"
NOTHING_FAILING = "Nothing is failing"
NOTHING_FAILING_LINE = "Every dimension holds on 10 or more people. There is nothing to add to the overview."
NO_WORDS_LINE = "No follow-up answer landed on the lines that did not hold:"


def nothing_to_read_line(n: int) -> str:
    return (f"{n} {'person has' if n == 1 else 'people have'} answered. A card needs 5 to say anything and 10 to be "
            "sure. The follow-up answers are kept and appear here once a card is called.")


def took_by(asked: int, against: int, rungs) -> str:
    """keel-web 077 `TOOK_BY`: *Only {asked} of the {against} were asked here: {k} had already been asked about {Rung}
    [and {k} about {Rung}], the first rung they failed.* (`tookBy[]`, in the served order; 077 call 12)."""
    rungs = list(rungs or [])
    if not rungs:
        return ""
    earlier = " and ".join([f"{rungs[0].get('count')} had already been asked about {rungs[0].get('name')}"]
                           + [f"{r.get('count')} about {r.get('name')}" for r in rungs[1:]])
    return f"Only {asked} of the {against} were asked here: {earlier}, the first rung they failed."


def not_asked_line(entry: dict) -> str:
    """keel-web 095: one muted line per `notAsked` entry -- *<Name>: <why>.*"""
    return f"{entry.get('name')}: {str(entry.get('why') or '').rstrip('.')}."


def quote_words(quote: dict) -> str:
    """A quote as the view draws it: the words in curly quotes, then *— {Name}* (design D7, D17)."""
    return f"“{quote.get('text')}” — {quote.get('name')}"
