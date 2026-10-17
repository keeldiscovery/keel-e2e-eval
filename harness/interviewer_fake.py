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

This module is machinery: it asserts nothing. `evals/interviewer_leg.py` and `evals/interviewer_marks.py` judge with it.
"""

from __future__ import annotations

import re
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
KINDS = ("OPENING", "PROBLEM", "ITEM", "ITEM_MORE", "SOLUTION", "COMMERCIAL", "DIDNT_CATCH", "PILOT", "THANKS",
         "IS_THAT_RIGHT")
#: The clips said only when an answer asks for them -- never in the spoken order.
UNSPOKEN = ("DIDNT_CATCH", "IS_THAT_RIGHT")
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
