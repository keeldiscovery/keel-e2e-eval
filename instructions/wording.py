"""The window frame's and the wording rules' code half, mirrored (spec 031 FR-003; judgement calls 52,
54, 55 and 56; keel-cloud 072 / 073; the recall words, call 62, keel-cloud 074; W10 retired at v13, call 67).

**Mirrors, never re-derivations.** keel-cloud decides what it refuses (`validate.py` shells its
aggregate for every answer); `option_validity` scores the accepted answer the way the product reads
it, so the structural rules it checks are ported here line for line, each beside the Java it comes
from -- the same arrangement the v9 checks have with C2-C4:

- `event_fault` is `WindowFrame.fault` (E1-E3) with `WindowFrame.clause`; since keel-cloud 212 (spec 136 FR-2) E2's
  cap is the window's (`event_max_words`, the founder's Prevalence clause) or `CLAUSE_MAX_WORDS` (a clause code
  takes in its place, the respondent writer's), and `packed_fault` (E8) / `routine_fault` (E7) are
  `WindowFrame.packedFault` / `routineFault`, the act that hurts;
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

#: `WindowFrame.CLAUSE_MAX_WORDS` (E2; keel-cloud 212 FR-3): the cap of a clause code takes in the founder's place, and of
#: the respondent writer's clause where the study holds no founder's clause -- `EVENT_MAX_WORDS` (25) before 212. The
#: founder's Prevalence clause is held to `event_max_words(window)`.
CLAUSE_MAX_WORDS = 25
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


def event_max_words(window) -> int:
    """keel-cloud 212 FR-3 (amended; `WindowFrame.eventMaxWords`): the founder's Prevalence clause is at most the words the
    project's own window's frame leaves of the spoken cap -- the longest question it fills is the strangers' Frequency
    item, *In {window}, on how many {unit} did you {event}?*: 11 words of frame on nights, days, weeks and months (so 9),
    12 on working days (so 8). No floor."""
    return SPOKEN_STEM_MAX_WORDS - len(f"In {window.words()}, {counted_in(window)} how many {short_unit(window)} "
                                       "did you".split())


def event_fault(event, window, max_words: int | None = None) -> str | None:
    """`WindowFrame.fault`: E1-E3 on one model-written clause, the first fault with its rule id, or
    `None`. E1: no digit, no number word, no time word and none of the window unit's words. E2: one
    clause, not a question -- no `?`, no sentence break, at most `max_words` words: since keel-cloud 212 (FR-3)
    `event_max_words(window)` when none is given (`fault(event, window)`), `CLAUSE_MAX_WORDS` on a clause code takes in
    the founder's place. E3: it does not open with the frame's words."""
    cap = event_max_words(window) if max_words is None else max_words
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
    if words > cap:
        return (f"E2: the clause is {words} words; at most {cap}"
                + (f" in {window.words()}, so the strangers' question '{frequency_respondent(window, '{event}')}' is "
                   f"within {SPOKEN_STEM_MAX_WORDS} spoken words" if cap == event_max_words(window) else ""))
    lower = text.lower()
    for opening in FRAME_OPENINGS:
        if lower == opening or lower.startswith(opening + " ") or lower.startswith(opening + ","):
            return (f"E3: the clause begins with '{opening}', the frame's own words; begin with "
                    "what happened")
    return None


# ------------------------------------------------- keel-cloud 212: the act that hurts (E7, E8; spec 136 FR-2)

#: `WindowFrame.STATE_WORDS` (E8): the words that make a clause a lasting state, not an act seen on a given unit.
STATE_WORDS = ("sitting", "idle", "left", "stay", "stays", "stayed", "staying")
#: `WindowFrame.PACKED` (E8): a cause, a purpose, a time beside the act -- *after* or *from* only before an *-ing* word.
_PACKED = re.compile(r"\b(because|so that|while)\b|\b(?:after|from)\s+[a-z]+ing\b", re.IGNORECASE)
#: `WindowFrame.JUDGEMENT` (E8): a judgement on the act -- *found it too fast*, *too noisy to follow*.
_JUDGEMENT = re.compile(r"\b(?:found|find|felt|feel|thought|seemed|considered)\b.*\btoo\b|\btoo\s+[a-z]+\s+to\b",
                        re.IGNORECASE)
#: `WindowFrame.STILL_HAVE` (E8): *still have* in any tense, the act's own words only where `went_wrong` says it.
_STILL_HAVE = re.compile(r"\bstill\s+(?:have|has|had|having)\b", re.IGNORECASE)

#: keel-cloud 212 FR-4 (`SavedList.SETTLED_BY`, L35): the three answers a Compatibility row's `settled_by` takes.
SETTLED_BY = ("nobody", "the segment", "the usual way")


def packed_fault(event, went_wrong) -> str | None:
    """`WindowFrame.packedFault` (E8): the founder's event is one act, seen on a given unit or not -- never a cause or a
    result packed in, never a judgement, never a lasting state (*still have* only where `went_wrong` carries it). The
    first fault, naming the field; `None` when the event passes."""
    text = clause(event)
    if not text.strip():
        return None
    packed = _PACKED.search(text)
    if packed:
        return (f"E8: event '{text}' packs a cause or a result in ('{packed.group()}'); write event from went_wrong: "
                "the one act, in the simple past, seen on a given day or not")
    judged = _JUDGEMENT.search(text)
    if judged:
        return (f"E8: event '{text}' is a judgement on the act ('{judged.group().strip()}'), not the act; write event "
                "from went_wrong: what they did or had to put up with, one act a person sees happen on a given day or "
                "not")
    state = first_word(text, STATE_WORDS)
    if state is not None:
        return (f"E8: event '{text}' says '{state}', a lasting state, not an act; write event from went_wrong: the one "
                "act a person sees happen on a given day or not")
    still = _STILL_HAVE.search(text)
    if still and (went_wrong is None or not _STILL_HAVE.search(str(went_wrong))):
        return (f"E8: event '{text}' says '{still.group()}', a lasting state unless went_wrong names it as the act; "
                "write event from went_wrong")
    return None


def base_of(past: str) -> str | None:
    """`WindowFrame.baseOf`: the base of a past -- `StrangerGrammar.baseOfPast` where code is sure, else a regular *-ed*
    undone (a doubled consonant single, an *-e* put back where English drops it), `None` where it is no *-ed* word."""
    from instructions import spoken as spoken_mod                       # noqa: PLC0415
    sure = spoken_mod.base_of_past(past)
    if sure is not None:
        return sure
    if not past.endswith("ed") or len(past) < 4:
        return None
    stem = past[:-2]
    if len(stem) > 3 and re.fullmatch(r".*([bdgmnprt])\1", stem):
        return stem[:-1]
    if re.fullmatch(r".*(eed|ored|ared|ured|ired|ated|ized|ised|uced|aded|oded|ided|uded|iked|aked|oked|aved|ived"
                    r"|oved|ased|used|nged|aged|dged|iced|nced|uged)", past):
        return past[:-1]
    if len(re.findall(r"[aeiouy]+", stem)) == 1 and re.fullmatch(r"[^aeiouy]*[aeiouy][^aeiouywx]", stem):
        return stem + "e"
    return stem


def _based(words_: list[str]) -> list[str]:
    """`WindowFrame.based` (E7): each word in its base where it is a past code knows (*wrote* *write*, *rang*)."""
    from instructions import spoken as spoken_mod                       # noqa: PLC0415
    out = []
    for word in words_:
        base = base_of(word) if word.endswith("ed") or spoken_mod.base_of_past(word) is not None else None
        out.append(word if base is None else base)
    return out


def routine_fault(event, routine, went_wrong, actor_plural) -> str | None:
    """`WindowFrame.routineFault` (E7): the event is the routine -- every content word of it (`FounderWords`' stop words
    and `actor_plural`'s own out, each in its base) is in `routine`, and none is in what `went_wrong` says beyond the
    routine (212 plan, call 9). The fault names both fields; `None` when the event is not the routine or a field is
    blank."""
    from harness import qualifiers                                      # noqa: PLC0415
    if not all(isinstance(t, str) and t.strip() for t in (event, routine, went_wrong)):
        return None
    own = _based(qualifiers.dropped(event, actor_plural or ""))
    if not own:
        return None
    joined = " ".join(own)
    routine_words = " ".join(_based(qualifiers.words(routine)))
    all_routine = not qualifiers.dropped(joined, routine_words)
    went_wrong_own = qualifiers.dropped(" ".join(_based(qualifiers.words(went_wrong))), routine_words)
    none_went_wrong = not went_wrong_own or len(qualifiers.dropped(joined, " ".join(went_wrong_own))) == len(own)
    if all_routine and none_went_wrong:
        return (f"E7: event '{clause(event)}' is the routine ('{routine.strip()}'), what every one of them does whether "
                "or not the problem struck -- everyone would answer Yes; write event from went_wrong "
                f"('{went_wrong.strip()}'), the act that hurts")
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


def money_all(text) -> list[str]:
    """keel-cloud 214 FR-5 (`Wording.moneyAll`): every money word in `text` as `money` reads them (a symbol, an
    upper-case ISO code, an amount in words), in order -- the founder's own, which a Commitment step keeps as typed."""
    if text is None:
        return []
    return [m.group() for m in _MONEY.finditer(str(text))
            if not re.fullmatch(r"[a-zA-Z]{3}", m.group()) or m.group() == m.group().upper()]


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
    are each at most 20 words. Spec 123 FR-2 (keel-cloud 193 FR-2): the Frequency question **served**
    (`frequency_respondent`, window first) -- no longer the shorter frame of 160 (`frequency_measured`, read on an item
    stored before 160 only); past the cap the writer is asked to shorten the clause, keeping its verb and its object,
    never cut."""
    g, f = gate(window, event), frequency_respondent(window, event)
    longest = max(len(g.split()), len(f.split()))
    if longest > SPOKEN_STEM_MAX_WORDS:
        gate_longest = len(g.split()) >= longest
        return (f"E4: framed, the clause makes {'the gate' if gate_longest else 'the Frequency question served'} "
                f"{longest} words ('{g if gate_longest else f}'); every question a stranger hears is at most "
                f"{SPOKEN_STEM_MAX_WORDS} words, so shorten the clause, keeping its verb and its object")
    return None
