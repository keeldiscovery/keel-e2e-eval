"""The window frame's and the wording rules' code half, mirrored (spec 031 FR-003; judgement calls 52,
54, 55 and 56; keel-cloud 072 / 073; the recall words, call 62, keel-cloud 074; W10 retired at v13, call 67).

**Mirrors, never re-derivations.** keel-cloud decides what it refuses (`validate.py` shells its
aggregate for every answer); `option_validity` scores the accepted answer the way the product reads
it, so the structural rules it checks are ported here line for line, each beside the Java it comes
from -- the same arrangement the v9 checks have with C2-C4:

- `event_fault` is `WindowFrame.fault` (E1-E3) with `WindowFrame.clause`;
- `money` is `Wording.money` (W9). `tick_all` (W7) and `carries` (W3 / W8's *verbatim*) retired at v18 (call 83):
  the model writes no question text for them to read;
- `NUMBER_WORDS` is `Vocabulary.NUMBER_WORDS`, `first_word` is `Vocabulary.firstWord`;
- `recall_words` is `Period.recallWords`: the registry's `{cost_period}` is filled with it. `RespondentQuestionsRules.checkRecall`
  (W10) went with the model's Existing sacrifice question (keel-cloud 077, call 67); nothing here mirrors it.

- `gate`, `frequency_respondent` and `framed_fault` are `WindowFrame.gate` / `frequencyRespondent` and keel-cloud
  088's `E4`: the framed gate and Frequency question at most 20 words each. Each frames its clause as
  `WindowFrame.subjectLed` does (`subject_led`, spec 110 FR-2): *did you {clause}*, or *did {clause}* where the clause
  names its own subject -- *you* / *your* (116), a subject before a present verb (129, 130), a determiner (131) and,
  since keel-cloud 170, *any* / *some* (*did any of the cash from your raise stay in ...?*, never *did you any of*).

The reported wording counts of call 56 (W1 / W2 / W5 / W6 / S1 over the model's question text) retired at v18 with the
text they counted (call 83): since keel-cloud 087 / 088 the model writes no question at all -- the founder's Answer
prompts and every respondent word are code's.
"""

from __future__ import annotations

import re

from harness.qualifiers import present_verb

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


# --------------------------------------------------------------------------- Wording (W9, mirrored)

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


# ------------------------------------------------------------- the recall words (call 62; keel-cloud 074)

#: `Period.recallWords` (keel-cloud 074): the words a respondent recalls what the problem cost over, by the
#: founder's cost period -- a day is asked over last week (and scaled), a year over the last three months.
RECALL_WORDS = {"day": "last week", "week": "last week", "month": "last month",
                "quarter": "the last three months", "year": "the last three months"}


def recall_words(period) -> str:
    """`ScreenContextBuilder.costRecall`: the recall words of the founder's cost period, *the last three
    months* where there is no cost estimate (spec 073's one period)."""
    return RECALL_WORDS.get(period, RECALL_WORDS["quarter"])


# ----------------------------------------------------------- the respondent's frames (E4, mirrored)

#: `SpokenForm.STEM_MAX_WORDS` (keel-cloud 088 E4; the spoken guidelines §2).
SPOKEN_STEM_MAX_WORDS = 20


#: `WindowFrame.subjectLed`'s determiners (spec 131 FR-1; *any* and *some* since keel-cloud 170 FR-3b): a clause of
#: three words or more opening on one names its own subject.
SUBJECT_DETERMINERS = ("the", "a", "an", "their", "our", "its", "every", "each", "any", "some")
#: ... and the articles a subject may open on before its noun (129 FR-1), and the words that open no subject.
_ARTICLES = ("the", "a", "an", "their", "our", "its")
_NO_SUBJECT = ("already", "still", "just", "also", "often", "always", "never", "usually", "only", "really", "ever",
               "not")


def subject_led(event) -> str:
    """`WindowFrame.subjectLed`: the clause as it follows *did* -- unchanged where it names its own subject, else with
    *you* before it. Its own subject: *you* / *your ...* (116); a determiner and two words more (131, and *any* /
    *some* since keel-cloud 170: *any of the cash from your raise stay in your bank's money market fund*); a first word
    no verb before a present verb, after an article where there is one (129: *freight cross the dock*); a plural noun
    then a present verb (130: *booking calls come in on every shift*)."""
    text = clause(event)
    lower = text.lower()
    if lower == "you" or lower.startswith("you ") or lower.startswith("your "):
        return text
    words = lower.split()
    if len(words) > 2 and words[0] in SUBJECT_DETERMINERS:
        return text
    at = 2 if len(words) > 2 and words[0] in _ARTICLES else 1
    if len(words) > at and not present_verb(words[0]) and not words[0].endswith("ing") \
            and words[0] not in _NO_SUBJECT and present_verb(words[at]):
        return text
    if len(words) > at + 1 and words[at].endswith("s") and not words[at].endswith("ss") \
            and not present_verb(words[at - 1]) and present_verb(words[at + 1]) and words[0] not in _NO_SUBJECT:
        return text
    return f"you {text}"


def gate(window, event) -> str:
    """`WindowFrame.gate`: the respondent's gate around the model's clause -- *did {subjectLed(clause)}* (spec 110
    FR-2: it always wrote *did you*, so a subject-led clause was measured as *did you any of the cash ...*)."""
    return f"In {window.words()}, did {subject_led(event)}?"


def counted_in(window) -> str:
    """keel-cloud 174 FR-5 (`WindowFrame.countedIn`, spec 115 FR-2): *on* a day or a night, *in* a week or a month."""
    return "in" if window.plural in ("weeks", "months") else "on"


def short_unit(window) -> str:
    """keel-cloud 174 FR-5 (`WindowFrame.shortUnit`): the plural's last word (*working days*: *days*)."""
    return window.plural.split(" ")[-1]


def frequency_respondent(window, event) -> str:
    """`WindowFrame.frequencyRespondent(window, event)`: Frequency carries the gate's own clause -- since keel-cloud 160
    (FR-2, spec 089 FR-5) the window first and plainly, then the event; since keel-cloud 174 FR-5 (spec 115 FR-2) the
    unit as it is counted and said short the second time: *In the last 4 weeks, in how many weeks did you lose your
    keys?*, *In the last 5 working days, on how many days did ...?*; with no clause *... did that happen?* (it read *On
    how many of those 4 weeks did ...?* before 160, *on how many weeks* from 160 to 173)."""
    text = clause(event)
    lead = f"In {window.words()}, {counted_in(window)} how many {short_unit(window)} did "
    if not text.strip():
        return f"{lead}that happen?"
    return f"{lead}{subject_led(text)}?"


def frequency_measured(window, event) -> str:
    """`WindowFrame.frequencyMeasured` (keel-cloud 160 judgement call 2): the frame E4 and the gate's fallbacks measure
    a clause on -- the one E4 was set against (spec 088), *On how many of those {count} {unit} did you {clause}?* --
    so no gate moves with the window-first frame; what is served is held to the cap on its own."""
    text = clause(event)
    if not text.strip():
        return f"On how many of those {window.count} {window.plural} did that happen?"
    return f"On how many of those {window.count} {window.plural} did {subject_led(text)}?"


def framed_fault(event, window) -> str | None:
    """E4 (keel-cloud 088 `RespondentQuestionsRules.gate`): framed, the gate and the Frequency question it frames
    are each at most 20 words -- the Frequency question as E4 measures it (`frequency_measured`, keel-cloud 160)."""
    questions = (gate(window, event), frequency_measured(window, event))
    longest = max(questions, key=lambda q: len(q.split()))
    count = len(longest.split())
    if count > SPOKEN_STEM_MAX_WORDS:
        return (f"E4: framed, the clause makes a question of {count} words ('{longest}'); every question a "
                f"stranger hears is at most {SPOKEN_STEM_MAX_WORDS} words, so shorten the clause")
    return None
