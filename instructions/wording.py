"""The window frame's and the wording rules' code half, mirrored (spec 031 FR-003; judgement calls 52,
54, 55 and 56; keel-cloud 072 / 073; the recall words, call 62, keel-cloud 074; W10 retired at v13, call 67).

**Mirrors, never re-derivations.** keel-cloud decides what it refuses (`validate.py` shells its
aggregate for every answer); `option_validity` scores the accepted answer the way the product reads
it, so the structural rules it checks are ported here line for line, each beside the Java it comes
from -- the same arrangement the v9 checks have with C2-C4:

- `event_fault` is `WindowFrame.fault` (E1-E3) with `WindowFrame.clause`; since keel-cloud 212 (spec 136 FR-2) E2's
  cap is the window's (`event_max_words`, the founder's Prevalence clause) or `CLAUSE_MAX_WORDS` (a clause code
  takes in its place, the respondent writer's), and `packed_fault` (E8) / `routine_fault` (E7) are
  `WindowFrame.packedFault` / `routineFault`, the act that hurts; since keel-cloud 216 (spec 139 FR-2) `no_sayer_fault`
  (E9) is `WindowFrame.noSayerFault`, the one of them who truly answers No;
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


#: `Vocabulary.PRONOUN_ONE` (keel-cloud 114 FR-1): the phrases where *one* is a pronoun, never a count.
PRONOUN_ONE = ("no one", "one another", "one-on-one", "one-to-one", "each one", "which one", "find one", "the one",
               "this one", "that one", "one of")
_COUNTED_UNITS = frozenset(("second", "seconds", "minute", "minutes", "hour", "hours", "day", "days", "night", "nights",
                            "week", "weeks", "month", "months", "year", "years", "time", "times"))
_LN = r"[^\W_]"
_PRONOUN_ONE = [re.compile(r"(?<!" + _LN + r")" + r"[\s-]+".join(re.escape(p) for p in re.split(r"[ -]", phrase))
                           + r"(?!" + _LN + r")") for phrase in PRONOUN_ONE]


def _pronoun_one(lower: str, start: int, end: int) -> bool:
    after = re.match(r"^[\s-]+([^\W_]+)(?:[\s-]+([^\W_]+))?", lower[end:])
    if after:
        nxt, then = after.group(1), after.group(2)
        if nxt in _COUNTED_UNITS or (nxt == "in" and then is not None and (then.isdigit() or then in NUMBER_WORDS)):
            return False
    return any(m.start() <= start and end <= m.end() for p in _PRONOUN_ONE for m in p.finditer(lower))


def numbers(text) -> list[str]:
    """`Vocabulary.numbers` (spec 141 FR-8, for keel-cloud 229's A4): every digit run and number word in `text`,
    lower-cased, in the order they stand -- a pronoun *one* is none."""
    if text is None:
        return []
    lower = str(text).lower()
    found = {m.start(): m.group() for m in re.finditer(r"\d+", lower)}
    for word in NUMBER_WORDS:
        for m in re.finditer(r"(?<!" + _LN + r")" + re.escape(word) + r"(?!" + _LN + r")", lower):
            if word != "one" or not _pronoun_one(lower, m.start(), m.end()):
                found[m.start()] = word
    return [found[k] for k in sorted(found)]


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
    12 on working days (so 8). No floor. Spec 139 FR-2 (keel-cloud 216 FR-3, the coordinator's correction): the frame
    served is now *On how many of {window} did you {event}?*, a word shorter; the cap keeps 212's numbers, measured on the
    frame they were set on (174's, `frequency_respondent_before216`), so the question at the cap is 19 words."""
    return SPOKEN_STEM_MAX_WORDS - len(f"{window_first_before216(window)}did you".split())


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


# ------------------------------------------------- keel-cloud 224: the event is a moment, and says no verdict (spec 141)

#: keel-cloud 224 FR-1 (`WindowFrame.STATE_VERBS`): the verbs of state -- a clause headed by one says where a thing
#: stood, not a moment it cost them.
STATE_VERBS = ("keep", "hold", "have", "leave", "sit", "stay", "remain", "lie", "rest", "own", "possess")
#: keel-cloud 224 FR-1 (`WindowFrame.STATE_FORMS`): each form of a verb of state, in any tense, to its base.
STATE_FORMS = {form: row[0] for row in (
    ("keep", "keeps", "kept", "keeping"), ("hold", "holds", "held", "holding"), ("have", "has", "had", "having"),
    ("leave", "leaves", "left", "leaving"), ("sit", "sits", "sat", "sitting"), ("stay", "stays", "stayed", "staying"),
    ("remain", "remains", "remained", "remaining"), ("lie", "lies", "lay", "lain", "lying"),
    ("rest", "rests", "rested", "resting"), ("own", "owns", "owned", "owning"),
    ("possess", "possesses", "possessed", "possessing")) for form in row}
#: keel-cloud 224 FR-2 (`WindowFrame.VERDICT_WORDS`): the verdict words -- the gate rule's list in
#: respondent-questions.md, in its order, word for word.
VERDICT_WORDS = ("idle", "sitting", "still", "stay", "have to", "fail to", "waste", "struggle", "by hand", "manually",
                 "could have", "would have", "more than it could", "better")
#: keel-cloud 224 FR-2 (`WindowFrame.VERDICT_VERB_FORMS`): a verdict word's verb in any tense -- its first word's.
_VERDICT_VERB_FORMS = {"idle": "idle|idles|idled|idling", "stay": "stay|stays|stayed|staying",
                       "have": "have|has|had|having", "fail": "fail|fails|failed|failing",
                       "waste": "waste|wastes|wasted|wasting",
                       "struggle": "struggle|struggles|struggled|struggling"}
#: `\p{L}` as the cloud reads it, Latin letters (a clause is English).
_L = "A-Za-z\u00c0-\u024f"


def _verdict_pattern(word: str):
    parts = word.split(" ")
    regex = r"(?i)(?<![" + _L + "'])(?:" + _VERDICT_VERB_FORMS.get(parts[0], re.escape(parts[0])) + ")"
    for part in parts[1:]:
        regex += r"\s+" + re.escape(part)
    if word == "still":
        regex += r"(?!\s+(?:have|has|had|having)(?![" + _L + "']))"         # 212's allowance, read by _STILL_HAVE
    return re.compile(regex + r"(?![" + _L + "'])")


#: Each verdict word as a pattern of its forms, in the list's order.
_VERDICT = {word: _verdict_pattern(word) for word in VERDICT_WORDS}
#: `WindowFrame.LEADING_ADVERBS`: the adverbs a clause may open on before its verb.
LEADING_ADVERBS = ("already", "still", "just", "also", "often", "always", "never", "usually", "only", "really", "ever")
#: `WindowFrame.SUBJECT_OPENERS` (224 FR-1): the words a clause opens its own subject on.
SUBJECT_OPENERS = frozenset(("a", "an", "the", "their", "your", "his", "her", "its", "our", "my", "this", "that",
                             "these", "those", "some", "one", "every", "each", "no", "any", "you", "they", "he", "she",
                             "it", "we", "i"))
#: `WindowFrame.OBJECT_ENDS` (224 FR-1): the small words that end the object after *have*.
OBJECT_ENDS = frozenset(("to", "in", "on", "at", "for", "from", "with", "into", "of", "by", "after", "before", "when",
                         "while", "because", "that", "which", "who", "and", "or", "until", "since", "as", "about",
                         "over", "under", "through"))
#: `WindowFrame.HAPPENED_VERBS` (224 FR-1): verbs of what happened to a thing, said bare after *had {it}*.
HAPPENED_VERBS = frozenset(("fail", "crash", "bounce", "drop", "die", "freeze", "jam", "stall", "stop", "slip",
                            "expire", "lapse", "happen", "turn", "show", "end", "return", "arrive", "disappear",
                            "vanish", "leak", "overflow", "spill", "burst", "collapse"))
#: `WindowFrame.PARTICIPLES` (224 FR-1): the irregular participles a perfect or a passive after *had* carries.
PARTICIPLES = frozenset((
    "been", "done", "gone", "got", "gotten", "made", "seen", "taken", "given", "known", "written", "spoken", "stolen",
    "broken", "frozen", "thrown", "shown", "lost", "sent", "spent", "paid", "built", "brought", "bought", "found", "told",
    "put", "cut", "set", "run", "hit", "hurt", "shut", "let", "won", "eaten", "fallen", "forgotten", "beaten", "bitten",
    "driven", "ridden", "chosen", "woken", "worn", "torn", "caught", "met", "read", "heard", "said", "kept", "held",
    "left", "sat", "lain", "had"))


def _clause_words(text: str) -> list[str]:
    """`WindowFrame.clauseWords`: the clause's words, lower case, every non-letter off each end."""
    out = []
    for raw in str(text).lower().split():
        word = re.sub("^[^" + _L + "]+|[^" + _L + "]+$", "", raw)
        if word:
            out.append(word)
    return out


def _head_at(words: list[str]) -> int:
    at = 0
    while at < len(words) - 1 and words[at] in LEADING_ADVERBS:
        at += 1
    return -1 if not words else at


def _participle(word: str) -> bool:
    return word in PARTICIPLES or (len(word) > 3 and word.endswith("ed"))


def _bare_verb(word: str) -> bool:
    return word in HAPPENED_VERBS or STATE_FORMS.get(word) == word or present_verb(word)


def state_head(event) -> str | None:
    """keel-cloud 224 FR-1 (`WindowFrame.stateHead`): the clause's head verb where it is a verb of state, or None --
    *have* read whole: *have to* + a verb is an obligation, *had* + a participle a perfect, *had* + its object + a bare
    verb or a participle what happened to them; only *have* as having is the state."""
    from instructions import spoken as spoken_mod                       # noqa: PLC0415 - `StrangerGrammar.baseOfPast`
    words = _clause_words(clause(event))
    at = _head_at(words)
    if at < 0:
        return None
    if words[at] in SUBJECT_OPENERS:
        verb = -1
        for i in range(at + 1, len(words)):
            word = words[i]
            if words[i - 1] not in SUBJECT_OPENERS and (word in STATE_FORMS or spoken_mod.base_of_past(word) is not None
                                                        or _participle(word)):
                verb = i
                break
        if verb < 0:
            return None
        at = verb
    return _state_head_at(words, at)


def _state_head_at(words: list[str], at: int) -> str | None:
    head = words[at]
    base = STATE_FORMS.get(head)
    if base is None:
        return None
    if base != "have":
        return head
    nxt = words[at + 1] if at + 1 < len(words) else ""
    if nxt == "to":
        return None
    if _participle(nxt):
        return _state_head_at(words, at + 1)
    for i in range(at + 2, min(len(words), at + 7)):
        word = words[i]
        if word in OBJECT_ENDS:
            break
        if words[i - 1] in SUBJECT_OPENERS:
            continue
        if _bare_verb(word) or _participle(word):
            return _state_head_at(words, i)
    return head


def _carries_verb(went_wrong, head: str) -> bool:
    """`WindowFrame.carriesVerb`: whether `went_wrong` names the head's verb, in any form -- *have* not in *have to*."""
    if went_wrong is None or not str(went_wrong).strip():
        return False
    base = STATE_FORMS[head]
    words = _clause_words(went_wrong)
    return any(STATE_FORMS.get(w) == base and not (base == "have" and i + 1 < len(words) and words[i + 1] == "to")
               for i, w in enumerate(words))


def verdict_word(event) -> str | None:
    """keel-cloud 224 FR-2 (`WindowFrame.verdictWord`): the first verdict word the clause carries, in the list's order,
    in any tense -- *have to* at its head not (the act's own frame)."""
    text = clause(event)
    words = _clause_words(text)
    at = _head_at(words)
    obliged = at >= 0 and at + 1 < len(words) and STATE_FORMS.get(words[at]) == "have" and words[at + 1] == "to"
    for word, pattern in _VERDICT.items():
        for match in pattern.finditer(text):
            if obliged and word == "have to" and len(_clause_words(text[:match.start()])) == at:
                continue
            return word
    return None


def left_standing(unit: str) -> str:
    """keel-cloud 231 FR-2 (`WindowFrame.leftStanding`): the tail 212's state words and 224's head verb end on -- the
    moment of a thing left standing, inside one `unit`."""
    return (f"; where a thing was left standing, write what it did or cost them inside one {unit}, its subject first "
            "after had (had {the thing} {do} ...), never where it sat")


#: keel-cloud 232 FR-7 (`ItemFrames.LAST_OPENINGS`): the openings an occasion that already says *last* may carry.
LAST_OPENINGS = ("your last ", "the last ", "their last ", "last ")


def think_of(whose: str, occasion) -> str:
    """keel-cloud 232 FR-7 (`ItemFrames.thinkOf`; cycle 15, Palus' *Think of your last last 3 months holding raise
    cash*): *Think of {whose} last {occasion}.* -- `whose` *your* or *the* -- or *Think of the last {rest}.* where the
    occasion already opens on *last*, *the last*, *their last* or *your last* (a window occasion: *the last 3 months*),
    so *last* is said once. English's words only."""
    noun = "" if occasion is None else str(occasion).strip()
    lower = noun.lower()
    for opening in LAST_OPENINGS:
        if lower.startswith(opening) and len(noun) > len(opening):
            return "Think of the last " + noun[len(opening):].strip() + "."
    return f"Think of {whose} last {noun}."


def packed_fault(event, went_wrong, window=None) -> str | None:
    """`WindowFrame.packedFault` (E8): the founder's event is one act, seen on a given unit or not -- never a cause or a
    result packed in, never a judgement, never a lasting state (*still have* only where `went_wrong` carries it). Since
    keel-cloud 224 (spec 141 FR-5) then the head verb -- a verb of state (`STATE_VERBS`) unless `went_wrong` carries the
    same verb -- and the verdict words (`VERDICT_WORDS`); `window`'s unit names the moment (*day* where none is in
    hand). Since keel-cloud 231 FR-2 (spec 142 FR-2) 212's state words and 224's head verb also say the moment of a
    thing left standing (`left_standing`), in the window's unit. The first fault, naming the field; `None` when the
    event passes."""
    text = clause(event)
    if not text.strip():
        return None
    unit = "day" if window is None else window.singular
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
                f"act a person sees happen on a given {unit} or not" + left_standing(unit))
    still = _STILL_HAVE.search(text)
    if still and (went_wrong is None or not _STILL_HAVE.search(str(went_wrong))):
        return (f"E8: event '{text}' says '{still.group()}', a lasting state unless went_wrong names it as the act; "
                "write event from went_wrong")
    head = state_head(text)
    if head is not None and not _carries_verb(went_wrong, head):
        return (f"E8: event '{text}' is a standing state ('{head}'); write the moment inside the window where it "
                f"showed -- what they did, or what happened to the thing, on a given {unit}" + left_standing(unit))
    verdict = verdict_word(text)
    if verdict is not None:
        return (f"E8: event '{text}' carries '{verdict}', a verdict on the act -- the way it was done or what might have "
                f"been -- not the act; write the act alone, from went_wrong, as a person saw it on a given {unit}")
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


#: `WindowFrame.NO_SAYER_TEST` (keel-cloud 216 FR-1, E9): the card's test, said in its words in every E9 refusal.
NO_SAYER_TEST = ("the test: would every one of them who did the day's work in the window say Yes to event? If every one "
                 "would, it is the routine; write the part that hurt instead -- the thing that failed, was lost, came "
                 "back wrong, sat idle or had to be done twice -- and no_sayer, one of them who did the day's work and "
                 "truly answers No, naming what was different for them")
#: `WindowFrame.NEGATION` (E9): the words that turn the no-sayer outside the segment.
_NEGATION = re.compile(r"(?i)(?<![^\W\d_'])(?:no longer|not|no|never|without|nothing|none|[^\W\d_]+n['\u2019]t)"
                       r"(?![^\W\d_'])")


def _upper(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def no_sayer_fault(no_sayer, routine, went_wrong, circumstance, *people) -> str | None:
    """`WindowFrame.noSayerFault` (keel-cloud 216 FR-1, `E9`; cycle 13's Fresco, Expanse and Codyco shapes): the writer
    names one of the people who did the day's work and truly answers *No* to the event (`no_sayer`), refused where it is
    empty (a breach, noted past the repair turn); where its verbs (`writers_rules.verb_roots`) share a root with the
    routine's own words and none with `went_wrong`'s own -- each field's own words what it says beyond the other; or
    where a negation comes before a root of the circumstance or of the people's own words (someone outside the segment).
    The fault says the card's test in its words; None when the no-sayer passes or a field it is read against is blank.
    Persona-free: English's small words and the writer's own fields."""
    from instructions import writers_rules as writers_mod               # noqa: PLC0415 - writers_rules reads this
    if no_sayer is None or not str(no_sayer).strip():
        return "E9: write no_sayer beside event -- " + NO_SAYER_TEST
    text = str(no_sayer).strip()
    who: list[str] = []
    for one in people:
        who += [r for r in writers_mod.roots(one) if r not in who]
    negation = _NEGATION.search(text)
    if negation:
        after = writers_mod.roots(text[negation.end():])
        outside = set(writers_mod.roots(circumstance)) | set(who)
        hit = [r for r in after if r in outside]
        if hit:
            return (f"E9: no_sayer '{text}' says '{negation.group()}' before '{hit[0]}' -- someone outside the segment, "
                    "who does not do the work; the no-sayer did the day's work and still truly answers No. "
                    + _upper(NO_SAYER_TEST))
    if not routine or not str(routine).strip() or not went_wrong or not str(went_wrong).strip():
        return None
    verbs = [v for v in writers_mod.verb_roots(text) if v not in who]
    routine_own = set(writers_mod.roots(routine)) - set(writers_mod.roots(went_wrong))
    went_wrong_own = set(writers_mod.roots(went_wrong)) - set(writers_mod.roots(routine))
    shared = [v for v in verbs if v in routine_own]
    hurt = [v for v in verbs if v in went_wrong_own]
    if shared and not hurt:
        return (f"E9: no_sayer '{text}' differs from the rest by the routine ('{str(routine).strip()}': '{shared[0]}'), "
                f"not by what went wrong ('{str(went_wrong).strip()}') -- so every one of them who did the day's work "
                "would answer Yes to event. " + _upper(NO_SAYER_TEST))
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


def window_first(window) -> str:
    """keel-cloud 216 FR-3 (`WindowFrame.windowFirst`; spec 139 FR-2): the Frequency frames' opening -- the unit said
    once, in the window phrase: *On how many of the last 3 months *, *On how many of the last 5 working days *."""
    return f"On how many of {window.words()} "


def window_first_before216(window) -> str:
    """keel-cloud 216 FR-3 (`WindowFrame.windowFirstBefore216`): the opening from keel-cloud 174 to 215 -- *In the last 3
    months, in how many months *, a two-word unit in its short form (*on how many days*) -- read on stored items and the
    frame the event's cap and E4 are measured on, never composed for a new item."""
    return f"In {window.words()}, {counted_in(window)} how many {short_unit(window)} "


def frequency_respondent(window, event) -> str:
    """`WindowFrame.frequencyRespondent(window, event)`: Frequency carries the gate's own clause -- since keel-cloud 160
    (FR-2, spec 089 FR-5) the window first and plainly, then the event. Spec 139 FR-2 (keel-cloud 216 FR-3, cycle 13's
    Palus: *In the last 3 months, in how many months did ...*, the card's named pitfall): the unit said once, in the
    window phrase -- *On how many of the last 4 weeks did you lose your keys?*, *On how many of the last 5 working days
    did ...?*; with no clause *... did that happen?* (it read *On how many of those 4 weeks did ...?* before 160, *on
    how many weeks* from 160 to 173, *In the last 4 weeks, in how many weeks* from 174 to 215:
    `frequency_respondent_before216`)."""
    text = clause(event)
    lead = f"{window_first(window)}did "
    if not text.strip():
        return f"{lead}that happen?"
    return f"{lead}{subject_led(text)}?"


def frequency_respondent_before216(window, event) -> str:
    """keel-cloud 216 FR-3 (`WindowFrame.frequencyRespondentBefore216`): the respondent frame as it read from 174 to 215
    -- *In the last 3 months, in how many months did you ...?* -- read on a stored item (served in it, as its recorded
    clip says it) and the frame E4 and the event's cap measure a clause on (`RespondentQuestionsRules
    .measuredFrequency`)."""
    text = clause(event)
    lead = f"{window_first_before216(window)}did "
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
    never cut. Spec 139 FR-2 (keel-cloud 216 FR-3): measured on the frame the cap was set on (174's,
    `frequency_respondent_before216`), so a clause keeps 212's numbers; the frame served is a word shorter."""
    g, f = gate(window, event), frequency_respondent_before216(window, event)
    longest = max(len(g.split()), len(f.split()))
    if longest > SPOKEN_STEM_MAX_WORDS:
        gate_longest = len(g.split()) >= longest
        which = "the gate" if gate_longest else "the Frequency question, as the cap measures it,"
        return (f"E4: framed, the clause makes {which} "
                f"{longest} words ('{g if gate_longest else f}'); every question a stranger hears is at most "
                f"{SPOKEN_STEM_MAX_WORDS} words, so shorten the clause, keeping its verb and its object")
    return None
