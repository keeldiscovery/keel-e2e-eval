"""The window frame's and the wording rules' code half, mirrored (spec 031 FR-003; judgement calls 52,
54, 55 and 56; keel-cloud 072 / 073; W10, call 62, keel-cloud 074).

**Mirrors, never re-derivations.** keel-cloud decides what it refuses (`validate.py` shells its
aggregate for every answer); `option_validity` scores the accepted answer the way the product reads
it, so the structural rules it checks are ported here line for line, each beside the Java it comes
from -- the same arrangement the v9 checks have with C2-C4:

- `event_fault` is `WindowFrame.fault` (E1-E3) with `WindowFrame.clause`;
- `money` is `Wording.money` (W9), `tick_all` is `Wording.tickAll` (W7), `carries` is
  `Wording.carries` (W3 / W8's *verbatim*);
- `NUMBER_WORDS` is `Vocabulary.NUMBER_WORDS`, `first_word` is `Vocabulary.firstWord`;
- `recall_words` / `recall_fault` are `Period.recallWords` and `RespondentQuestionsRules.checkRecall` (W10).

**And the rules the subject only instructs are counted here, never marked** (call 56;
`window-frame-design.md` §3.6-§3.8: *"checked by the eval's judge-free length counts ... reported,
not refused"*): `reported(text, founder=…)` returns one question's words and its W1 / W2 / W6 / S1
flags, and `long_options` its W5 count. `score.py` adds them up; `marks.judge` never reads them.
"""

from __future__ import annotations

import re
import unicodedata

# -------------------------------------------------------------------------- Vocabulary (mirrored)

#: `Vocabulary.NUMBER_WORDS`.
NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty", "sixty",
                "seventy", "eighty", "ninety", "hundred", "thousand", "million", "dozen")


def first_word(text, words):
    """`Vocabulary.firstWord`: the first of `words`, in list order, standing whole in `text`
    (lower-cased; no letter or digit either side), or `None`."""
    if text is None:
        return None
    lower = str(text).lower()
    for word in words:
        if re.search(r"(?<![^\W_])" + re.escape(word) + r"(?![^\W_])", lower):
            return word
    return None


def first_number(text):
    """`Vocabulary.firstNumber`: the first digit run, else the first number word."""
    if text is None:
        return None
    digit = re.search(r"\d+", str(text))
    return digit.group() if digit else first_word(text, NUMBER_WORDS)


# ------------------------------------------------------------------- WindowFrame (E1-E3, mirrored)

#: `WindowFrame.EVENT_MAX_WORDS` (E2).
EVENT_MAX_WORDS = 25
#: `WindowFrame.TIME_WORDS` (E1): the frame owns the period.
TIME_WORDS = ("last", "past", "recent", "recently", "ago", "today", "yesterday", "week", "weeks",
              "month", "months", "year", "years", "day", "days", "night", "nights", "shift",
              "shifts", "cycle", "cycles")
#: `WindowFrame.FRAME_OPENINGS` (E3): the frame's own opening words.
FRAME_OPENINGS = ("in", "how many", "did you", "out of", "do you think")


def clause(event) -> str:
    """`WindowFrame.clause`: trimmed, runs of space as one, no closing full stop, a leading capital
    lowered (unless the second letter is a capital too -- an acronym)."""
    text = re.sub(r"\s+", " ", str(event or "").strip())
    while text.endswith("."):
        text = text[:-1].strip()
    if len(text) > 1 and text[0].isupper() and not text[1].isupper():
        text = text[0].lower() + text[1:]
    return text


def event_fault(event, window) -> str | None:
    """`WindowFrame.fault`: E1-E3 on one model-written clause, the first fault with its rule id, or
    `None`. E1: no digit, no number word, no time word and none of the window unit's words. E2: one
    clause, not a question -- no `?`, no sentence break, at most 25 words. E3: it does not open
    with the frame's words."""
    text = clause(event)
    if not text.strip():
        return ("E2: the clause is empty; write what happened, as one clause that completes the "
                "frame")
    number = first_number(text)
    if number is not None:
        return (f"E1: '{number}' is a number; the frame says the period, and the clause says only "
                "what happened")
    time = list(TIME_WORDS) + [window.singular, window.plural]
    word = first_word(text, time)
    if word is not None:
        return (f"E1: '{word}' is a time word; the frame says the period ({window.words()}), and "
                "the clause says only what happened")
    if "?" in text:
        return "E2: the clause is a question; it completes the frame, which asks the question"
    if re.search(r"[.!;:]\s+\S", text, re.DOTALL) or "\n" in text:
        return "E2: the clause is more than one sentence; write one clause"
    words = len(text.split())
    if words > EVENT_MAX_WORDS:
        return f"E2: the clause is {words} words; at most {EVENT_MAX_WORDS}"
    lower = text.lower()
    for opening in FRAME_OPENINGS:
        if lower == opening or lower.startswith(opening + " ") or lower.startswith(opening + ","):
            return (f"E3: the clause begins with '{opening}', the frame's own words; begin with "
                    "what happened")
    return None


# -------------------------------------------------------------------- Wording (W3/W7/W8/W9, mirrored)

_ISO = ("USD|GBP|EUR|CHF|SEK|NOK|DKK|PLN|INR|CAD|AUD|MXN|JPY|SGD|KRW|CNY|HKD|IDR|MYR|PHP|THB|VND|"
        "AED")
#: `Wording.MONEY` (W9).
_MONEY = re.compile(
    r"[$£€¥₹₩₱฿₫]"
    r"|\b(" + _ISO + r")\b"
    r"|\b\d[\d,.]*\s*(k\s+)?(dollars?|euros?|bucks|quid|rupees?|yen|francs?|kronor|kroner|zloty|"
    r"pesos?|pounds sterling|cents?|pence)\b",
    re.IGNORECASE)
#: `Wording.ISO_CODES`: an ISO 4217 code in capitals.
_ISO_CODES = re.compile(r"\b(" + _ISO + r")\b")
#: `Wording.TICK_ALL` (W7).
_TICK_ALL = re.compile(r"\b(tick|select|choose)\s+(all|every)\b|\bpick\s+all\b"
                       r"|\ball\s+that\s+appl(y|ies)\b", re.IGNORECASE)


def money(text) -> str | None:
    """`Wording.money` (W9): a currency symbol, an ISO code in capitals or an amount with a currency
    word -- the first, or `None`. A lower-case *eur* or *aud* is a word, not a code."""
    if text is None:
        return None
    iso = _ISO_CODES.search(str(text))
    if iso:
        return iso.group()
    for match in _MONEY.finditer(str(text)):
        hit = match.group()
        if re.fullmatch(r"[a-zA-Z]{3}", hit):
            continue
        return hit
    return None


def tick_all(question) -> str | None:
    """`Wording.tickAll` (W7): the words of a tick-all instruction in a question, or `None`."""
    if question is None:
        return None
    match = _TICK_ALL.search(str(question))
    return match.group() if match else None


def normal(text) -> str:
    """`Wording.normal`: NFKC, lower case, apostrophes dropped, every run of non-letters and
    non-digits one space."""
    if text is None:
        return ""
    folded = re.sub(r"['‘’ʼ]", "", unicodedata.normalize("NFKC", str(text)).lower())
    return re.sub(r"[\W_]+", " ", folded).strip()


def _without_article(text: str) -> str:
    for article in ("a ", "an ", "the "):
        if text.startswith(article):
            return text[len(article):]
    return text


def carries(text, name) -> bool:
    """`Wording.carries` (W3 / W8, keel-cloud D-4): `name` verbatim in `text` -- case, accents,
    apostrophes and punctuation aside, a leading article free. A blank name is carried by
    anything (a card with no name is held to none)."""
    if name is None or not str(name).strip():
        return True
    needle = _without_article(normal(name))
    return not needle or f" {needle} " in f" {normal(text)} "


# ------------------------------------------------------------------- W10 (call 62; keel-cloud 074)

#: `Period.recallWords` (keel-cloud 074): the words a respondent recalls what the problem cost over, by the
#: founder's cost period -- a day is asked over last week (and scaled), a year over the last three months.
RECALL_WORDS = {"day": "last week", "week": "last week", "month": "last month",
                "quarter": "the last three months", "year": "the last three months"}


def recall_words(period) -> str:
    """`ScreenContextBuilder.costRecall`: the recall words of the founder's cost period, *the last three
    months* where there is no cost estimate (spec 073's one period)."""
    return RECALL_WORDS.get(period, RECALL_WORDS["quarter"])


def recall_fault(text, period) -> str | None:
    """`RespondentQuestionsRules.checkRecall` (W10): the part-3 Existing sacrifice question carries the recall
    words verbatim (`carries`), because the amounts are normalised from them; `None` when it does."""
    words = recall_words(period)
    if carries(text, words):
        return None
    return (f"W10: the Existing sacrifice question asks over {words!r}, the period the amounts are "
            "read over, word for word; this one does not")


# --------------------------------------------------------------- the reported rules (call 56)

#: W1: at most 20 words in a question, 25 where a scene sentence comes first.
W1_MAX, W1_SCENE_MAX = 20, 25
#: W5: an option of at most 8 words.
W5_MAX = 8
_W2 = re.compile(r"\bdo you (think|believe)\b", re.IGNORECASE)
_SECOND_PERSON = re.compile(r"\b(you|your|yours|yourself|you're|youre)\b", re.IGNORECASE)
_SENTENCES = re.compile(r"(?<=[.!?])\s+")


def reported(text, *, founder: bool) -> dict:
    """One model-written question's reported wording (call 56) -- never a fault, never a mark:
    `words`; `w1` over 20 words (25 with a scene sentence first); on the founder's side `w2` (*do
    you think / believe*) and `w6` (second person: the founder's questions are about others); and
    `s1`, a one-sentence question over 20 words with a clause in front of it (*When a payroll has
    been run ..., at what point ...?*) where S1 asks for the scene as its own sentence."""
    text = str(text or "").strip()
    words = len(text.split())
    sentences = [s for s in _SENTENCES.split(text) if s.strip()]
    scene = len(sentences) > 1 and not sentences[0].rstrip().endswith("?")
    out = {"words": words, "w1": words > (W1_SCENE_MAX if scene else W1_MAX),
           "s1": len(sentences) == 1 and words > W1_MAX and "," in text.split("?")[0]}
    if founder:
        out["w2"] = bool(_W2.search(text))
        out["w6"] = bool(_SECOND_PERSON.search(text))
    return out


def long_options(labels) -> int:
    """W5's count: the options over 8 words (reported, call 56)."""
    return sum(1 for label in labels or () if len(str(label or "").split()) > W5_MAX)
