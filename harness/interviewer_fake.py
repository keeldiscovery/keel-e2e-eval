"""keel-cloud's pre-rendered AI interviewer, restated where this eval reads it (spec 044; keel-cloud 094, contract 16,
`InferenceCharge` 9, document 22): the charge rows, the faces (two since keel-cloud 143), the refusal codes, the
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
FOLLOW_UP clip kind (one a rung a role's link walks: *One more thing.* -- keel-cloud 144 -- and the rung's spoken
wording) is unspoken --
it plays only when the walk finds its rung.

This module is machinery: it asserts nothing. `evals/interviewer_leg.py` and `evals/interviewer_marks.py` judge with it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# ------------------------------------------------------------------------------------- charge v9 (FR-F)

#: keel-cloud `InferenceCharge.VERSION`, which every HOLD written carries: 9 since 094, 10 since 104 (BRIEF out,
#: THEMES in; spec 052 -- the interviewer's two rows did not move), 11 since 125 (EXAMPLE_MATCH at 0, never held;
#: no price moved), **12** since 156 (spec 088: INTERVIEW 30 at Begin added, INTERPRET 10 -> 0 and THEMES 8 -> 0; the
#: interviewer's two rows did not move -- `harness/interview_charge.py`).
PRICE_VERSION = 12
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

#: Spec 083 (keel-cloud 143, contract 44, cloud-docs master `f48f256e`; 2026-10-28): two studio avatars, DAPHNE
#: (preselected, the default) and SASKIA -- `InterviewerFace.OFFERED`, the constants whose last flag is true, in the
#: order served. Spec 058 (keel-cloud 110, contract 23) had the four photo avatars, LIVIA preselected where JUDY was;
#: 143 retires them (still constants, so a project that recorded one keeps her clips, name and still, its `helloUrl`
#: null) and supersedes 094's DAPHNE with the new studio look, so DAPHNE is offered again. A pick of any retired face
#: is 422 FACE_UNKNOWN (`RETIRED`).
FACES = ("DAPHNE", "SASKIA")
FACE_NAMES = {"DAPHNE": "Daphne", "SASKIA": "Saskia"}
PRESELECTED = "DAPHNE"
#: 094's faces retired by keel-cloud 110 (not constants since: keel-web ships their stills, no hello).
RETIRED_110 = ("JUDY", "JIN", "ANNA", "TITO")
#: 110's photo faces retired by keel-cloud 143 (still constants; keel-web 125 keeps their stills and hellos, but
#: keel-cloud serves a recording of one with `helloUrl` null -- `served_hello`).
RETIRED_143 = ("LIVIA", "JIA", "MARIEKE", "CHUKWU")
RETIRED = RETIRED_110 + RETIRED_143
#: Spec 058 FR-2 / FR-3 (keel-web 087): each face's hello is one clip of 4.6-5.4 s; one longer than this is not it
#: (143's two are 4.6 s each).
HELLO_MAX_S = 8.0


def preview_path(face: str) -> str:
    """`InterviewerFace.previewPath`: the still keel-web ships, never a vendor URL."""
    return f"/interviewer/faces/{face.lower()}.webp"


def hello_path(face: str) -> str:
    """`InterviewerFace.helloPath` (keel-cloud 110): the face's hello clip keel-web ships, served as `helloUrl`."""
    return f"/interviewer/faces/{face.lower()}.mp4"


def served_hello(face: str) -> str | None:
    """The `helloUrl` keel-cloud serves for a face on the wire (143 FR-4, `InterviewerPlayer.Face`): an offered face's
    hello; null for a retired one a recording still carries."""
    return hello_path(face) if face in FACES else None


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


def passage_said(text: str | None) -> str:
    """`PassageComposer.said`: a served line as the passage says it -- a spaced double dash a comma."""
    return (text or "").replace(" -- ", ", ").replace("--", ",").strip()


def solution_opening(problem: str | None = None) -> str:
    """The SOLUTION clip's opening: `Now the idea.` -- since keel-cloud 133 FR-6 (T018) after the problem in one sentence
    wherever the link serves one (`Idea.problem` on every decision-maker's link, ALL included; `Reveal.problem` on a
    person's link that serves no part 1)."""
    return _join(passage_said(problem), SOLUTION_OPENING)


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
#: keel-cloud 158 T013 (`ItemFrames.ONE_MORE`, `PassageComposer.ONE_MORE`): the ITEM_MORE clip and the written second
#: ask of Importance's one-then-one-more -- *And one more?* (it said *And which one more?*, spec 094 / 136).
MORE = "And one more?"
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
#: the stack runs). Spec 086 FR-5: keel-cloud 154's rows (`9f78b765`), every rung naming the thing.
#: Spec 089 FR-4: keel-cloud 159's Relative advantage rung (`1cf2ebc3`) -- against the scale's last two, *... wouldn't
#: make much difference on your last {occasion}. What would make {job} better for you, if anything?*, a *worse* said as
#: worse. Spec 093 FR-2: keel-cloud 161's Current solution rung (`b009fac8`) -- *You said {phrase} works for you. What
#: keeps it working?*, `{phrase}` the locked phrase as the question says it.
LADDER_SHA = "b009fac8"
#: Design §2, as the registry carries it since keel-cloud 118: `(dimension, against, text template, spoken wording)`, in
#: registry order. Purchase friction is a rung now (its quick / not-needed answers are against the fear); Adoption
#: friction's and Commitment's stems are the plain questions of 118 FR-4. Since keel-cloud 154 (spec 086 FR-5) every rung
#: names the thing -- `{job}` (the job as an -ing phrase), `{solution_name}` (the idea's name, *it* where none), `{step}`
#: (Commitment's step as an -ing phrase), `{effort}` (the tested effort as an -ing phrase) -- and a spoken line may hold
#: the project's words (`FollowUpBlock.SPOKEN_PLACEHOLDERS`), filled as the clip recorded at the lock says them.
LADDER: tuple[tuple[str, tuple[str, ...] | str, str, str], ...] = (
    ("problem.importance", ("none_of_these",),
     "You did not pick {founder_item} as one to make easier. What made the others more pressing for you?",
     "You did not pick {founder_item} as one to make easier. What made the others more pressing for you?"),
    # spec 093 FR-2 (keel-cloud 161 T003): the rung says the founder's phrase, `{phrase}` (was *your way of {job}*)
    ("problem.current_solution_satisfaction", ("outcome_1", "outcome_2"),
     "You said {phrase} works for you. What keeps it working?",
     "You said {phrase} works for you. What keeps it working?"),
    ("solution.compatibility", ("only_with_help", "no"),
     "You said you couldn't {condition}. What got in the way?",
     "You said {solution_name} would be hard to fit into your setup. What gets in the way?"),
    ("solution.relative_advantage", ("no_difference", "worse"),
     "You said {solution_name} wouldn't make much difference on your last {occasion}. What would make {job} better for "
     "you, if anything?",
     "You said {solution_name} wouldn't make much difference on your last {occasion}. What would make {job} better for "
     "you, if anything?"),
    ("solution.adoption_friction", ("probably_not", "no"),
     "What makes {effort} too much trouble for you?",
     "What makes {effort} too much trouble for you?"),
    ("commercial.price", LOCK_RULE,
     "You put {solution_name} at {band}. What would make it worth more to you?",
     "You put {solution_name} below what we asked. What would make it worth more to you?"),
    ("commercial.buyer_payer_alignment", LOCK_RULE,
     "Who had to agree when you paid for something like {solution_name}, and what did they need to see?",
     "Who had to agree when you paid for something like {solution_name}, and what did they need to see?"),
    ("commercial.purchase_friction", ("yes_quick", "not_needed"),
     "What would slow down buying {solution_name}, if anything?",
     "What would slow down buying {solution_name}, if anything?"),
    ("commercial.commitment", ("probably_not", "no"),
     "What would you start with instead of {step}?",
     "What would you start with instead of {step}?"),
)
RUNGS = tuple(r[0] for r in LADDER)
#: Keel-cloud 118 FR-4 (`FollowUpBlock.Also`): a rung's second stem, asked on the answers it names (the conditional yes,
#: the long purchase) -- `{dimension: (on, text template, spoken wording, heading)}`.
ALSO: dict[str, tuple[tuple[str, ...], str, str, str]] = {
    "solution.adoption_friction": (("yes_if_worth_it",), "What would make {solution_name} clearly worth it to you?",
                                   "What would make {solution_name} clearly worth it to you?",
                                   "What would make it clearly worth it?"),
    "commercial.purchase_friction": (("yes_long",), "What would take the time in buying {solution_name}?",
                                     "What would take the time in buying {solution_name}?", "What took the time?"),
    "commercial.commitment": (("yes_after_trying",), "What would {smaller_step} have to show you?",
                              "What would {smaller_step} have to show you?",
                              "What would the first step have to show?"),
}
#: Design §2's rungs with no question since keel-cloud 118 (a gate No ends the interview; a number has no why; derived).
NO_FOLLOW_UP = ("problem.prevalence", "problem.frequency", "commercial.existing_sacrifice", "commercial.ability_to_pay")
#: `PassageComposer.ONE_MORE_THING` (keel-cloud 144 FR-2, spec 075 FR-5): every FOLLOW_UP clip opens on it, first or
#: second, on the spot or at the end (the ALSO stems too); the screens' one kicker is *One more thing* (keel-web 126
#: FR-5: *About that* and *One last thing* are gone).
ONE_MORE_THING = "One more thing."
FOLLOW_UP_KICKER = "One more thing"
#: The lead-in before keel-cloud 144 (`ONE_LAST_THING`): a READY recording whose FOLLOW_UP clips still say it is
#: re-rendered once each, at no charge (144 FR-2); no clip composed since says it.
RETIRED_LEAD_IN = "One last thing."
#: Spec 075 (keel-cloud 142 `MAX_FOLLOW_UPS`, keel-web 124): at most two follow-ups an interview, a skipped one counted.
MAX_FOLLOW_UPS = 2
#: Buyer and payer's fixed answers and the one that supports when "Nobody else" is tested (`Compare.BUYER_DECIDED_ALONE`)
#: -- with a named role tested the registry's `supports`: since keel-cloud 145 FR-2 (spec 076 FR-2) direction-aware,
#: `had_to_agree` and `decided_alone` both (the two *someone else* answers count against).
BUYER_ANSWERS = ("had_to_agree", "decided_alone", "someone_else_agreed", "someone_else_decided")
BUYER_ALONE = "decided_alone"
BUYER_SUPPORTS = ("had_to_agree", "decided_alone")
#: `PriceLadder.POINTS` and its escape below every band.
PRICE_POINTS = (1, 2, 5, 10, 20, 50, 100, 250, 500, 1_000, 2_500, 5_000, 10_000)
WOULD_NOT_PAY = "would_not_pay"
#: `FollowUpComposer.DEFAULTS` / `WOULD_NOT_PAY_BAND`: what a placeholder says when its words are missing. keel-cloud 154
#: (spec 086 FR-5): `{job}` *doing this*, `{solution_name}` *it*, `{step}` *that step*; `{effort}` *doing that* (its slot
#: is an -ing phrase now; it read *do that*).
FILL_DEFAULTS = {"{their_picks}": "other difficulties", "{founder_item}": "this one",
                 "{their_answer}": "today's way works", "{condition}": "do that", "{would}": "be hard",
                 "{benefit}": "it", "{occasion}": "time", "{effort}": "doing that", "{band}": "less than we asked",
                 "{smaller_step}": "that first step", "{job}": "doing this", "{solution_name}": "it",
                 "{step}": "that step", "{phrase}": "the way you do it"}
WOULD_NOT_PAY_BAND = "nothing"
#: keel-cloud 130 FR-7 (`FollowUpComposer.WORTH_MORE`): Price's follow-up question after its said-back pick; 154 FR-2:
#: *to you*.
WORTH_MORE = "What would make it worth more to you?"
#: keel-cloud 154 FR-1 (`FollowUpComposer.NO_NAME`): `{solution_name}` where the founder typed no name for the idea.
NO_NAME = "it"


def named(name: str | None) -> str:
    """keel-cloud 154 (`FollowUpComposer.named`): the idea's name as typed, or *it* where there is none."""
    return name.strip() if name and name.strip() else NO_NAME


def would_not_pay_text(name: str | None) -> str:
    """keel-cloud 154 FR-2 (`FollowUpComposer.wouldNotPayText`): *You said you wouldn't pay for {name}. What would change
    your mind?* -- never *this*; *it* where the idea has no name (it read *... for this. What would change that?*)."""
    return f"You said you wouldn't pay for {named(name)}. What would change your mind?"
_SHOWN_PRICE = re.compile(r"[$\u20ac\u00a3\u00a5\u20b9]\s?\d[\d,]*(?:\.\d+)?")


def price_said_back(question: str | None, band: str | None, name: str | None = None) -> str:
    """keel-cloud 130 FR-7 (`FollowUpComposer.priceSaidBack`): Price's follow-up composed whole, text and spoken alike --
    *You put it below €3,000.* where the served stem showed a price (its first figure), *You put it at {band}.* where a
    band was picked, *You put it low.* otherwise -- never *less than we asked* where no price was shown. keel-cloud 154
    FR-2: the idea named where it has a name (*You put Lullaby at $2 to $5.*), *it* where none."""
    idea = named(name)
    shown = _SHOWN_PRICE.search(question or "")
    if shown:
        return f"You put {idea} below {shown.group()}. {WORTH_MORE}"
    if band and band.strip() and band != WOULD_NOT_PAY_BAND:
        return f"You put {idea} at {band}. {WORTH_MORE}"
    return f"You put {idea} low. {WORTH_MORE}"


def follow_up_script(spoken_words: str) -> str:
    """`PassageComposer.followUp`: a rung's FOLLOW_UP clip says *One more thing.* (keel-cloud 144) and its one spoken
    wording."""
    return f"{ONE_MORE_THING} {spoken_words.strip()}"


def rung(dimension: str) -> tuple | None:
    return next((r for r in LADDER if r[0] == dimension), None)


@dataclass(frozen=True)
class Founder:
    """What the walk reads off the founder's side (keel-cloud `Ladder.Founder`): Importance's own item's code (`own`,
    the saved list's item 0; None when Importance was left out), the price's low (None: no price), and Buyer and
    payer's supporting codes as `Compare.supportingCodes` reads the tested item (None: not calibrated)."""
    importance_item: str | None = "own"
    price_low: float | None = None
    buyer_supports: tuple[str, ...] | None = None
    #: Spec 064 FR-7 (keel-cloud 115 `Ladder.Founder.chainPrice`): a chain price is held to its own rung edge -- a pick
    #: at the founder's low or above (`CommercialChain.atOrAbove`), not spec 073's ladder floor; a two-step pick has no
    #: rung (115 judgement call 8).
    chain_price: bool = False
    #: Spec 067 FR-4 (keel-cloud 117 FR-3, `Ladder.Founder.of`): Current solution's line on the founder's saved list as
    #: served -- the outcomes above it (`outcome_1` .. `outcome_{line}`) are against; None keeps the registry's
    #: `outcome_1, outcome_2` (D4's line, 2 on every golden entry).
    current_line: int | None = None
    #: keel-cloud 128 FR-21 (`Ladder.Founder.upfrontLow`): an up-front-then price's up-front low, so a two-step pick
    #: below the founder's price on either step is against; None off that shape.
    upfront_low: float | None = None


def _founder_floor(low: float) -> float:
    for point in reversed(PRICE_POINTS[:-1]):
        if low >= point:
            return point
    return PRICE_POINTS[0]


def price_floor(code: str | None) -> float | None:
    """`PriceLadder.floorOf`: 0 for "under", the low for a band or "over", None otherwise (`would_not_pay`)."""
    code = (code or "")
    code = code[len("upfront."):] if code.startswith("upfront.") else code
    parts = code.split("_")
    if parts[0] == "under":
        return 0.0
    if parts[0] in ("band", "over") and len(parts) > 1:
        try:
            return float(parts[1])
        except ValueError:
            return None
    return None


def _value(pick) -> dict:
    """A pick's `{dimension, codes, chip}`, from a `harness.vectors_script.Pick` or a plain dict."""
    if isinstance(pick, dict):
        return {"dimension": pick.get("dimension"), "codes": list(pick.get("codes") or []), "chip": pick.get("chip")}
    return {"dimension": pick.dimension, "codes": list(pick.codes or []), "chip": pick.chip}


def against(dimension: str, pick, founder: Founder) -> bool:
    """`Ladder.against`: whether one stored answer is against the founder on `dimension`'s rung. An escape is apart
    but for the one the rung names (Importance's *None of these*); a lock-rule rung reads the founder's lock; a rung held
    to a founder's answer the lock does not have (Importance left out, no price) is never found."""
    entry = rung(dimension)
    if entry is None:
        return False
    _, codes_against, _, _ = entry
    v = _value(pick)
    if dimension == "problem.importance" and founder.importance_item is None:
        return False
    if dimension == "commercial.price" and founder.price_low is None:
        return False
    if v["chip"]:
        return codes_against != LOCK_RULE and str(v["chip"]).lower() in codes_against
    codes = v["codes"]
    if dimension == "commercial.price" and founder.chain_price and len(codes) == 2:
        # keel-cloud 128 FR-21: up front then a plan -- below the founder's price on either step is against, as on one
        # ladder (AirCaps: Diego and Amaka, under the price, were owed no follow-up)
        def below(code: str, low) -> bool:
            floor = price_floor(code)
            return low is not None and not (floor is not None and floor >= float(low))
        return any(below(c, founder.upfront_low) if c.startswith("upfront.") else below(c, founder.price_low)
                   for c in codes)
    if dimension == "problem.current_solution_satisfaction" and founder.current_line is not None:
        # keel-cloud 117 FR-3 / spec 067 FR-4: an outcome above the founder's own line is against; below it, or no
        # outcome, is not -- read off the served bar, never the registry's two codes
        code = codes[0] if len(codes) == 1 else ""
        return code.startswith("outcome_") and code[len("outcome_"):].isdigit() \
            and int(code[len("outcome_"):]) <= int(founder.current_line)
    if codes_against == LOCK_RULE:
        if len(codes) != 1:
            return False
        if dimension == "commercial.price":
            floor = price_floor(codes[0])
            if founder.chain_price:
                return not (floor is not None and floor >= float(founder.price_low))
            return not (floor is not None and floor >= _founder_floor(float(founder.price_low)))
        supports = founder.buyer_supports
        return supports is not None and codes[0] in BUYER_ANSWERS and codes[0] not in supports
    if dimension == "problem.importance":
        return bool(codes) and founder.importance_item not in codes
    return bool(codes) and codes[0] in codes_against


def walks(link: str, b2b: bool) -> tuple[str, ...]:
    """`Ladder.walks(link, b2b)`: the decision-maker's link walks the three commercial rungs, a B2B study's primary
    link the five of parts 1 and 2, a B2C study's primary link all eight."""
    if link == "COMMERCIAL_B2B":
        return tuple(r for r in RUNGS if r.startswith("commercial."))
    if b2b:
        return tuple(r for r in RUNGS if not r.startswith("commercial."))
    return RUNGS


def ordered(rungs, first=()) -> tuple[str, ...]:
    """`Ladder.ordered(first)` (keel-cloud 118 FR-4): the deciding lines `first` (each called stage's, in the stages'
    order) first, then every other rung in registry order."""
    out = [d for d in (first or ()) if d in rungs]
    out = list(dict.fromkeys(out))
    return tuple(out + [r for r in rungs if r not in out])


def apart(dimension: str, pick) -> bool:
    """`Ladder.apart`: the answer is one a rung's second stem is asked on (the conditional yes, the long purchase)."""
    also = ALSO.get(dimension)
    v = _value(pick)
    return also is not None and not v["chip"] and len(v["codes"]) == 1 and v["codes"][0] in also[0]


def closes(dimension: str, pick) -> bool:
    """keel-cloud 128 FR-20 (`FollowUpComposer.closes`): a pick that closes its line owes no follow-up -- Buyer and
    payer's *No, I decided on my own* was asked *Who had to agree ...?* (Codyco): nobody had to."""
    v = _value(pick)
    return dimension == "commercial.buyer_payer_alignment" and v["codes"][:1] == [BUYER_ALONE] and not v["chip"]


def owed(picks, founder: Founder, link: str = "PRIMARY", *, b2b: bool = False, served: set[str] | None = None,
         first=(), asked=()) -> list[tuple[str, bool]]:
    """`Ladder.owed` (keel-cloud 118): every question these answers are owed, `(dimension, apart)`, in the walk's order
    -- the deciding lines first, then registry order -- on the rungs the link walks (and, given, the interview serves).
    Spec 075 (keel-cloud 142 FR-1, `FollowUpComposer.ask(..., asked)`): a rung in `asked` is left out."""
    by_dimension = {_value(p)["dimension"]: p for p in picks}
    out = []
    for dimension in ordered(walks(link, b2b), first):
        if served is not None and dimension not in served:
            continue
        if dimension in (asked or ()):
            continue
        pick = by_dimension.get(dimension)
        if pick is None or closes(dimension, pick):
            continue
        if against(dimension, pick, founder):
            out.append((dimension, False))
        elif apart(dimension, pick):
            out.append((dimension, True))
    return out


def first_stem(picks, founder: Founder, link: str = "PRIMARY", *, b2b: bool = False,
               served: set[str] | None = None, first=(), asked=()) -> tuple[str, bool] | None:
    """`Ladder.stemOf`: the question the route returns -- the first owed not in `asked` (keel-cloud 142) -- or None."""
    stems = owed(picks, founder, link, b2b=b2b, served=served, first=first, asked=asked)
    return stems[0] if stems else None


def first_rung(picks, founder: Founder, link: str = "PRIMARY", *, b2b: bool = False,
               served: set[str] | None = None, first=(), asked=()) -> str | None:
    """The rung of the question the route returns (`first_stem`), or None (nothing owed). Since keel-cloud 118 the
    deciding lines (`first`) are walked first, and an answer a second stem is asked on is owed too; since 142 a rung
    in `asked` is passed over."""
    stem = first_stem(picks, founder, link, b2b=b2b, served=served, first=first, asked=asked)
    return stem[0] if stem else None


def asks(picks, founder: Founder, order, link: str = "PRIMARY", *, b2b: bool = False, served: set[str] | None = None,
         first=(), rungs=None, late=()) -> list[dict]:
    """Spec 075 (keel-cloud 142 FR-1, keel-web 124 FR-1 / FR-2): the follow-ups the page asks these answers, in the order
    asked -- `[{dimension, also, on}]`, `on` the item's dimension it hangs on (asked on the spot) or None (the end's);
    since keel-web 126 both under the one kicker *One more thing*. The page's own walk, every route answered inside the beat: after each answered item
    whose dimension is a rung the link walks (`rungs`, the served `followUps[]`; default `walks`), while fewer than two
    were asked, the route is asked with the answers so far (`order`, the items' dimensions as served, cut at that item)
    and `asked`; a rung on that very item is asked there and then. After the last item one call more (not raced): a rung
    on the last item is asked on the spot, then -- fewer than two asked -- once more for the end. A skip counts as
    asked (124 J-4), so nothing here reads what was said. `late`: the items (dimensions) whose call the walk holds past
    the beat -- the page goes on, the rung stays owed, and the end asks it (124 FR-1's latency rule)."""
    by_dimension = {_value(p)["dimension"]: p for p in picks}
    rungs = set(walks(link, b2b) if rungs is None else rungs)
    order = [d for d in order]
    out: list[dict] = []

    def route(upto: int):
        so_far = [by_dimension[d] for d in order[:upto + 1] if d in by_dimension]
        return first_stem(so_far, founder, link, b2b=b2b, served=served, first=first,
                          asked=tuple(a["dimension"] for a in out))

    for i, dimension in enumerate(order):
        last = i == len(order) - 1
        answered = dimension in by_dimension
        if len(out) >= MAX_FOLLOW_UPS:
            break
        if not last:
            if not answered or dimension not in rungs:
                continue
            stem = route(i)
            if stem and stem[0] == dimension and dimension not in (late or ()):
                out.append({"dimension": stem[0], "also": stem[1], "on": dimension})
            continue
        stem = route(i)
        if stem is None:
            break
        if answered and stem[0] == dimension:
            out.append({"dimension": stem[0], "also": stem[1], "on": dimension})
            if len(out) >= MAX_FOLLOW_UPS:
                break
            stem = route(i)
            if stem is None:
                break
        out.append({"dimension": stem[0], "also": stem[1], "on": None})
    return out


def deciding_lines(standings: dict | None) -> list[str]:
    """`FollowUpComposer.deciding` read off the served standings (no arithmetic of the eval's own): each stage whose
    verdict is called -- not holding up, or people disagree -- gives the first of its dimensions, in registry order,
    whose status is the verdict (the engine's rule: the worst status, the first on a tie), in the stages' order."""
    out = []
    for vector in (standings or {}).get("vectors") or []:
        verdict = vector.get("verdict")
        if verdict not in ("NOT_HOLDING_UP", "PEOPLE_DISAGREE"):
            continue
        hit = next((d.get("dimension") for d in vector.get("dimensions") or [] if d.get("status") == verdict), None)
        if hit:
            out.append(hit)
    return out


def lower(label: str | None) -> str | None:
    """`BeliefSentence.lower`: a label as it reads mid-sentence -- the first letter lower-cased, unless the second is a
    capital (an acronym)."""
    if label is None:
        return None
    label = label.strip()
    if not label or (len(label) > 1 and label[1].isupper()):
        return label
    return label[0].lower() + label[1:]


def joined(labels: list[str | None], word: str) -> str | None:
    """`FollowUpComposer.joined`: "a", "a and b", "a, b and c", each lower-cased."""
    kept = [lower(x) for x in labels if x and x.strip()]
    if not kept:
        return None
    return kept[0] if len(kept) == 1 else ", ".join(kept[:-1]) + f" {word} " + kept[-1]


def fill(dimension: str, values: dict[str, str | None], *, also: bool = False) -> str:
    """`FollowUpComposer.fill`: the stem's text (the rung's, or its second `also`) with each placeholder replaced, a
    missing value its plain default."""
    text = ALSO[dimension][1] if also else rung(dimension)[2]
    for placeholder in re.findall(r"\{[a-z_]+\}", text):
        value = values.get(placeholder)
        text = text.replace(placeholder, value if value and value.strip() else FILL_DEFAULTS[placeholder])
    return text


def spoken_of(dimension: str, *, also: bool = False) -> str:
    """The stem's spoken wording (the rung's, or its second stem's), as the registry writes it (placeholders kept)."""
    return ALSO[dimension][2] if also else rung(dimension)[3]


def spoken_filled(dimension: str, values: dict[str, str | None], *, also: bool = False) -> str:
    """keel-cloud 154 FR-1 (`FollowUpComposer.spoken`): the stem's spoken line with the project's words filled, a missing
    value its plain default -- what `ask` serves as `spoken` and the clip recorded at the lock says."""
    text = spoken_of(dimension, also=also)
    for placeholder in re.findall(r"\{[a-z_]+\}", text):
        value = values.get(placeholder)
        text = text.replace(placeholder, value if value and value.strip() else FILL_DEFAULTS[placeholder])
    return text


def role_sets(recording: dict) -> dict[str, list[dict]]:
    """A stored recording's clips (document 22 `ClipDocument`), by role, in the order the composer wrote them."""
    out: dict[str, list[dict]] = {}
    for clip in (recording or {}).get("clips") or []:
        out.setdefault(clip.get("role"), []).append(clip)
    return out


def spoken(clips: list[dict]) -> list[dict]:
    """One role's clips as spoken (DIDNT_CATCH and IS_THAT_RIGHT have no place in the order)."""
    return [c for c in clips if c.get("kind") not in UNSPOKEN]


def first_sentence(text: str) -> str:
    m = re.match(r"\s*(.+?[.!?])(\s|$)", text or "", re.S)
    return (m.group(1) if m else (text or "")).strip()


#: `Reveal.belief` opens on the founder's attribution; the solution passage says the benefit itself (FR-B: "and the
#: benefit is {belief}").
_BELIEF_LEAD = re.compile(r"^\s*the people building it believe(s)?\s+(that\s+)?", re.I)


def benefit(belief: str) -> str:
    """The belief line without its attribution: *it would get translators paid on time.*"""
    return _BELIEF_LEAD.sub("", belief or "").strip()


def normal(text: str) -> str:
    """Lower case, curly quotes straightened, every run of non-word characters one space."""
    text = (text or "").replace("’", "'").replace("‘", "'").lower()
    return " ".join(re.findall(r"[a-z0-9']+", text))


# ------------------------------------------------------------------------------- the themes fake (spec 052)
#
# keel-cloud 104 (FR-9, design §7 "Fake"): the THEMES job is answered for the eval founders by a deterministic
# grouping, test scope in the cloud (`support.FakeThemes`), exported whole as `themes-cases.json` (its rule, its
# stop-word list, C3 Compatibility's and S03 Importance's cases) so this copy is held to it word for word
# (`tests/test_report_marks.py`). The eval predicts the Insights view from the people's follow-up answers with it.

#: `FakeThemes.MAX`: at most three themes, as the real job.
THEMES_MAX = 3
#: `FakeThemes.STOP_WORDS`, the words a first noun is never (cloud-docs `9a033fe`; held to the export's list).
THEMES_STOP_WORDS = frozenset((
    "a", "about", "all", "also", "always", "am", "an", "and", "another", "any", "anything", "are", "as", "at", "be",
    "been", "being", "but", "by", "can", "can't", "cannot", "could", "did", "didn't", "do", "does", "don't", "done",
    "down", "each", "else", "every", "everything", "for", "from", "get", "got", "had", "has", "have", "he", "her",
    "here", "his", "how", "i", "i'm", "idea", "if", "in", "into", "is", "isn't", "it", "it's", "its", "just", "made",
    "make", "many", "me", "more", "most", "much", "my", "need", "needed", "needs", "never", "no", "nor", "not",
    "nothing", "of", "on", "one", "only", "or", "other", "our", "out", "over", "own", "really", "she", "should", "so",
    "some", "something", "still", "take", "takes", "than", "that", "that's", "the", "their", "them", "then", "there",
    "there's", "these", "they", "this", "those", "to", "too", "took", "under", "up", "us", "very", "was", "wasn't",
    "we", "were", "what", "when", "where", "which", "who", "whom", "why", "will", "with", "won't", "would", "yet",
    "you", "your"))

_SPLIT = re.compile(r"[^\w']+|[\d_]+", re.UNICODE)


def _theme_words(text: str) -> list[str]:
    """`FakeThemes.words`: lower-cased, split on anything not a letter or an apostrophe, edge apostrophes stripped."""
    out = []
    for raw in _SPLIT.split((text or "").lower()):
        word = raw.strip("'")
        if word:
            out.append(word)
    return out


def first_noun(text: str, name_words=frozenset()) -> str | None:
    """`FakeThemes.firstNoun`: the first word of three letters or more (apostrophes not counted) that is no stop word
    and no word of the dimension's name."""
    for word in _theme_words(text):
        if len(word.replace("'", "")) >= 3 and word not in THEMES_STOP_WORDS and word not in name_words:
            return word
    return None


#: keel-cloud 119 (`Insight.ON_THEIR_OWN`): the leftovers' group, last; keel-web says it *On their own*.
ON_THEIR_OWN = "ON_THEIR_OWN"


def themes(answers, name: str = "") -> dict:
    """`FakeThemes.themes(name, answers)`: `answers` is `[{id, text}]` in the job's order; the result is
    `{themes: [{label, answerIds}]}` -- piles by first noun, by size descending, ties by first appearance, the first
    three; since keel-cloud 119 every other answer, in the order handed, in one last `ON_THEIR_OWN` group, so every
    answer is in exactly one group."""
    name_words = frozenset(_theme_words(name))
    piles: dict[str, list[str]] = {}
    for answer in answers or []:
        noun = first_noun(answer.get("text"), name_words)
        if noun is not None:
            piles.setdefault(noun, []).append(answer.get("id"))
    ordered_piles = sorted(piles.items(), key=lambda pile: -len(pile[1]))  # stable: first pile first on a tie
    out = [{"label": label, "answerIds": list(ids)} for label, ids in ordered_piles[:THEMES_MAX]]
    grouped = {i for t in out for i in t["answerIds"]}
    leftovers = [a.get("id") for a in answers or [] if a.get("id") not in grouped]
    if leftovers:
        out.append({"label": ON_THEIR_OWN, "answerIds": leftovers})
    return {"themes": out}


#: keel-cloud 145 FR-6 (`Insight.NOT_ABOUT_THIS`, themes.md): the fixed group for an answer that is junk, abuse or has
#: nothing to do with the question -- kept off the Insights box (not a theme, not ON_THEIR_OWN, not in `answered` or
#: `quotes`), counted in `notAboutThis`; still stored and served under the person.
NOT_ABOUT_THIS = "NOT_ABOUT_THIS"
#: Spec 076 FR-6: the answers the eval's THEMES script places in NOT_ABOUT_THIS -- the founder's walk of 2026-10-27
#: met one; `FakeThemes` (test scope in the cloud) has no such group, so this is the script's rule, not the export's.
NOT_ABOUT_THIS_TEXTS = ("Meow, you are a fool.",)


def themes_with_junk(answers, name: str = "") -> dict:
    """Spec 076 FR-6: the script's grouping -- every answer whose text is one of `NOT_ABOUT_THIS_TEXTS` in one last
    NOT_ABOUT_THIS group (keel-cloud's `ThemesReading` sorts it last, at most once), every other answer grouped by
    `themes` (the cloud's `FakeThemes`, untouched); every answer in exactly one group."""
    junk = [a for a in answers or [] if a.get("text") in NOT_ABOUT_THIS_TEXTS]
    rest = [a for a in answers or [] if a.get("text") not in NOT_ABOUT_THIS_TEXTS]
    out = themes(rest, name)["themes"] if rest else []
    if junk:
        out.append({"label": NOT_ABOUT_THIS, "answerIds": [a.get("id") for a in junk]})
    return {"themes": out}


def not_about_this_line(n: int) -> str:
    """keel-web 127 FR-4 (`notAboutThisLine`): the Insights box's muted line -- *1 answer was not about this.* / *{n}
    answers were not about this.*"""
    return "1 answer was not about this." if n == 1 else f"{n} answers were not about this."


#: keel-cloud 104 capped a theme at three quotes; keel-cloud 119 serves every quote (uncapped), shortest first.
QUOTES_MAX = None


def served_quotes(ids, by_id: dict) -> list[dict]:
    """A theme's quotes as the standings serve them since keel-cloud 119: `[{invitationId, name, text}]`, every one, by
    length ascending (the job's order on a tie). `by_id` is `{invitationId: {name, text}}`."""
    rows = [{"invitationId": i, "name": (by_id.get(i) or {}).get("name"), "text": (by_id.get(i) or {}).get("text")}
            for i in ids if i in by_id]
    return sorted(rows, key=lambda q: len(q["text"] or ""))


# ---------------------------------------------------------------- the Insights view's words (spec 052 FR-4)
#
# Copied once, beside the ladder (051's): the rung headings and the no-question reasons are keel-cloud registry data
# (`follow_up.heading`, `no_follow_up`; registry decision 23, cloud-docs `9a033fe`), held to the export by a unit
# test; the view's own strings are keel-web 077's (`InsightsView.tsx`, as 077's spec words them), held to its source
# by a source check once 077 is on master.

#: Design §4.2 (registry `follow_up.heading`; keel-cloud 118: the stem asked on the three friction / commitment rungs):
#: the rung's heading over its quotes, one a dimension with a question.
RUNG_HEADINGS = {
    "problem.importance": "Why other things come first",
    "problem.current_solution_satisfaction": "What makes today's way work for them",
    "solution.compatibility": "What gets in the way",
    "solution.relative_advantage": "What would have made a difference",
    "solution.adoption_friction": "What makes that too much?",
    "commercial.price": "What would make it worth more",
    "commercial.buyer_payer_alignment": "Who had to agree",
    "commercial.purchase_friction": "What did slow it down?",
    "commercial.commitment": "What would you start with instead?",
}
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
    if not rungs or asked >= against:
        return ""                                         # keel-web 102 FR-2: everyone asked here draws no line
    if asked <= 0:
        # keel-web 102 FR-2 (`TOOK_BY`): *None of the 3 were asked here: all 3 had already been asked about
        # Importance.* -- one earlier rung that took them all reads *all n*; several read their counts
        first = rungs[0]
        count = f"all {first.get('count')}" if len(rungs) == 1 and first.get("count") == against else f"{first.get('count')}"
        earlier = " and ".join([f"{count} had already been asked about {first.get('name')}"]
                               + [f"{r.get('count')} about {r.get('name')}" for r in rungs[1:]])
        return f"None of the {against} were asked here: {earlier}."
    earlier = " and ".join([f"{rungs[0].get('count')} had already been asked about {rungs[0].get('name')}"]
                           + [f"{r.get('count')} about {r.get('name')}" for r in rungs[1:]])
    return f"Only {asked} of the {against} were asked here: {earlier}, the first rung they failed."


def not_asked_line(entry: dict) -> str:
    """keel-web 095: one muted line per `notAsked` entry -- *<Name>: <why>.*"""
    return f"{entry.get('name')}: {str(entry.get('why') or '').rstrip('.')}."


def quote_words(quote: dict) -> str:
    """A quote as the view draws it: the words in curly quotes, then *— {Name}* (design D7, D17)."""
    return f"“{quote.get('text')}” — {quote.get('name')}"
