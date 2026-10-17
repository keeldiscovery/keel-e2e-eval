"""keel-cloud's pre-rendered AI interviewer, restated where this eval reads it (spec 044; keel-cloud 094, contract 16,
`InferenceCharge` 9, document 22): the charge rows, the five faces, the refusal codes, the spoken order of a role's
clips, the fixed lines code writes (design `ai-interviewer-prerendered-2026-10-15.md` FR-B), and what the stack's fake
renderer does (`FakeInterviewerRenders`: a one-second silent mp4 per clip after a 3 s virtual delay, 0.1 s a word, one
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

#: keel-cloud `InferenceCharge.VERSION` since 094: every HOLD written carries it.
PRICE_VERSION = 9
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

FACES = ("JUDY", "JIN", "ANNA", "DAPHNE", "TITO")
FACE_NAMES = {"JUDY": "Judy", "JIN": "Jin", "ANNA": "Anna", "DAPHNE": "Daphne", "TITO": "Tito"}
PRESELECTED = "JUDY"


def preview_path(face: str) -> str:
    """`InterviewerFace.previewPath`: the still keel-web ships, never a vendor URL."""
    return f"/interviewer/faces/{face.lower()}.webp"


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
#: The cloud-docs commit the copy below was taken from (`dimension-registry.yaml`'s `follow_up` blocks, registry
#: decision 22, invariant 9; `tests/test_interviewer_marks.py` holds it to the registry export the stack runs).
LADDER_SHA = "4cda99a"
#: Design §2, as the registry carries it: `(dimension, against, text template, spoken wording)`, in interview order.
#: Importance's `against` names its one escape that counts against; the rung's own rule is the founder's item absent
#: from the two picks. The two lock-rule rungs carry the word, not a list.
LADDER: tuple[tuple[str, tuple[str, ...] | str, str, str], ...] = (
    ("problem.importance", ("none_of_these",),
     "You picked {their_picks} over {founder_item}. What makes those more pressing?",
     "You put other difficulties ahead of this one. What makes those more pressing?"),
    ("problem.current_solution_satisfaction", ("outcome_1", "outcome_2"),
     "You said {their_answer}. What do you do today that makes it work?",
     "You said today's way works for you. What do you do that makes it work?"),
    ("solution.compatibility", ("only_with_help", "no"),
     "You said {condition} would {would}. What gets in the way?",
     "You said that step would be hard in your setup. What gets in the way?"),
    ("solution.relative_advantage", ("neutral", "negative"),
     "You said {benefit} would have made no difference to your last {occasion}. What would have?",
     "You said it would not have made much difference. What would have?"),
    ("solution.adoption_friction", ("probably_not", "no"),
     "You said you probably would not {effort}. What makes it too much?",
     "You said that would be too much to do. What makes it too much?"),
    ("commercial.price", LOCK_RULE,
     "You put it at {band}. What would make it worth more?",
     "You put it below what we asked. What would make it worth more?"),
    ("commercial.buyer_payer_alignment", LOCK_RULE,
     "Who had to agree, and what did they need to see?",
     "Who had to agree, and what did they need to see?"),
    ("commercial.commitment", ("yes_after_trying", "probably_not", "no"),
     "What would you start with instead?",
     "What would you start with instead?"),
)
RUNGS = tuple(r[0] for r in LADDER)
#: Design §2's rungs with no question (a gate No ends the interview; a number has no why; derived; the reason itself).
NO_FOLLOW_UP = ("problem.prevalence", "problem.frequency", "commercial.existing_sacrifice", "commercial.ability_to_pay",
                "commercial.purchase_friction")
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
                 "{their_answer}": "today's way works", "{condition}": "that step", "{would}": "be hard",
                 "{benefit}": "it", "{occasion}": "time", "{effort}": "do that", "{band}": "less than we asked"}
WOULD_NOT_PAY_BAND = "nothing"


def follow_up_script(spoken_words: str) -> str:
    """`PassageComposer.followUp`: a rung's FOLLOW_UP clip says *One last thing.* and its one spoken wording."""
    return f"{ONE_LAST_THING} {spoken_words.strip()}"


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


def _founder_floor(low: float) -> float:
    for point in reversed(PRICE_POINTS[:-1]):
        if low >= point:
            return point
    return PRICE_POINTS[0]


def price_floor(code: str | None) -> float | None:
    """`PriceLadder.floorOf`: 0 for "under", the low for a band or "over", None otherwise (`would_not_pay`)."""
    parts = (code or "").split("_")
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
    if codes_against == LOCK_RULE:
        if len(codes) != 1:
            return False
        if dimension == "commercial.price":
            floor = price_floor(codes[0])
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


def first_rung(picks, founder: Founder, link: str = "PRIMARY", *, b2b: bool = False,
               served: set[str] | None = None) -> str | None:
    """The first rung, in ladder order, whose own answer is against the founder -- or None (nothing owed). Only the
    rungs the link walks and, when given, the dimensions its interview serves are read."""
    by_dimension = {_value(p)["dimension"]: p for p in picks}
    for dimension in walks(link, b2b):
        if served is not None and dimension not in served:
            continue
        pick = by_dimension.get(dimension)
        if pick is not None and against(dimension, pick, founder):
            return dimension
    return None


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


def fill(dimension: str, values: dict[str, str | None]) -> str:
    """`FollowUpComposer.fill`: the rung's text with each placeholder replaced, a missing value its plain default."""
    text = rung(dimension)[2]
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
