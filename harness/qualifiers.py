"""keel-cloud 146 (`domain.vectors.Qualifiers`, `FounderWords`, `ReadBack.withWhen`), mirrored: the qualifiers of the
founder's WHICH PEOPLE that a stranger answers about themselves, and the two seams 146 closed on the lines composed from
the segment and its condition -- a qualifier is said once (`in_core`), and the decision-maker's chip names the people
once (`head`, `says`) -- with "when" said once before a circumstance (`with_when`).

Mirrored character for character so the harness predicts what the cloud serves (spec 077); every pattern is the
cloud's, compiled ASCII as Java's `\\w` and `\\b` read ASCII text. 146's judgement calls are the cloud's and are kept:
the "said once" rule is read from the core and the condition alone (Issen's *not starting from zero* against *are past
the beginner stage* shares no words and keeps its clause); `says` allows one content word of difference
(`MOST_DROPPED`) and reads an *-ing* verb as its stem (*working* / *work*); `head` cuts at the last relative pronoun or
preposition at or before the qualifier (*learners at intermediate level* -> *learners*).
"""

from __future__ import annotations

import re

# ------------------------------------------------------------------------------------------- FounderWords

#: keel-cloud `FounderWords.MOST_DROPPED`: a paraphrase may drop at most this many of the founder's content words.
MOST_DROPPED = 1

#: keel-cloud `FounderWords.STOP`: function words and the commonest verbs -- they carry no noun of the founder's.
STOP = frozenset((
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "at", "for", "with", "from", "by", "as", "is", "are",
    "was", "were", "be", "been", "being", "it", "its", "it's", "they", "their", "them", "theirs", "you", "your", "he",
    "she", "his", "her", "we", "our", "that", "this", "these", "those", "there", "here", "when", "then", "than", "so",
    "if", "into", "onto", "out", "up", "down", "over", "under", "about", "some", "each", "every", "all", "any", "one",
    "has", "have", "had", "having", "get", "gets", "got", "getting", "come", "comes", "came", "coming", "go", "goes",
    "went", "going", "make", "makes", "made", "take", "takes", "took", "do", "does", "did", "done", "still", "just",
    "yet", "also", "very", "can", "could", "would", "should", "will", "may", "might", "must", "need", "needs", "who",
    "what", "which", "while", "first", "time", "times", "who's", "not", "no", "never", "without"))

#: keel-cloud `FounderWords.NEGATIONS`.
NEGATIONS = frozenset(("not", "no", "never", "without", "nobody", "nothing", "none"))


def words(text: str | None) -> list[str]:
    """`FounderWords.words`: lower-cased, split on anything but a letter, a digit, an apostrophe or a hyphen, each
    word's leading and trailing apostrophes and hyphens off."""
    out: list[str] = []
    if text is None:
        return out
    for raw in re.split(r"[^a-z0-9'-]+", text.lower().replace("\u2019", "'")):
        word = re.sub(r"^['-]+|['-]+$", "", raw)
        if word:
            out.append(word)
    return out


def stem(word: str) -> str:
    """`FounderWords.stem`: a plural's *ies*, *es* or *s* off first, then the first five letters."""
    if word.endswith("ies") and len(word) > 4:
        w = word[:-3] + "y"
    elif word.endswith("es") and len(word) > 4:
        w = word[:-2]
    elif word.endswith("s") and len(word) > 3:
        w = word[:-1]
    else:
        w = word
    return w[:5] if len(w) > 5 else w


def dropped(founder: str | None, *kept: str | None) -> list[str]:
    """`FounderWords.dropped`: the founder's content words none of `kept` carries (by stem), in the founder's order."""
    missing: list[str] = []
    if founder is None or not founder.strip():
        return missing
    stems = {stem(w) for text in kept for w in words(text)}
    for word in words(founder):
        if len(word) < 3 or word in STOP or re.fullmatch(r"\d+", word):
            continue
        if stem(word) not in stems and word not in missing:
            missing.append(word)
    return missing


def _negated(text: str | None) -> bool:
    return text is not None and any(w in NEGATIONS or w.endswith("n't") for w in words(text))


def negation_dropped(founder: str | None, *kept: str | None) -> bool:
    """`FounderWords.negationDropped`: the founder's clause turns on a negation none of `kept` carries."""
    return _negated(founder) and not any(_negated(text) for text in kept)


# ------------------------------------------------------------------------------------------- Qualifiers

#: keel-cloud `Qualifiers.QUALIFIER` (specs 128, 129, 131): the words of a WHICH PEOPLE that qualify who counts.
QUALIFIER_PATTERN = (r"(?i)\b(not starting|or above|or more|at least|with no|without|already|beyond the|past the|"
                     r"no longer|level)\b"
                     r"|\b\d[\d,]*\s*(?:to|-|\u2013)\s*\d[\d,]*\b|\b(?:bank|banks|banking|run|runs|work|works) (?:with|on)\b"
                     r"|\b(?:that|which) (?:run|runs|operate|operates|own|owns|employ|employs)\b")

#: keel-cloud `Qualifiers.DRAWN_QUALIFIER` (spec 145 FR-4a): QUALIFIER's, an amount, a relative clause and a place --
#: the place case-sensitive (*in the Dallas*, *in Texas*), the rest not.
DRAWN_QUALIFIER = re.compile(
    QUALIFIER_PATTERN
    + r"|(?i:\bmore than \d|\bover \d|\b\d[\d,]*\s*\+|\bwith (?:at least |more than |over )?\d|\bwho\b)"
    + r"|(?-i:\bin (?:the )?[A-Z][\w.]*)", re.ASCII)

#: keel-cloud `Qualifiers.OPENS_QUALIFIER` (146 FR-3): the word a people phrase's qualifier opens on.
OPENS_QUALIFIER = re.compile(r"(?i)\s(?:who|whose|that|which|in|at|with|of|from|across|on|for)\b", re.ASCII)

#: keel-cloud `Qualifiers.FRAME` (146 FR-2): the frame code writes a condition in, which the founder's own words never
#: carry -- *are based in*, *work at a*, *have*, *are*, *who*.
FRAME = re.compile(r"(?i)^(?:who\s+)?(?:are\s+based\s+in|works?\s+at(?:\s+an?)?|are|is|have|has)\s+", re.ASCII)

_NUMBER = re.compile(r"\d[\d,]*", re.ASCII)
_CAPITAL = re.compile(r"\b[A-Z][\w.]*", re.ASCII)


def _carries(text: str, said: str) -> bool:
    """`Qualifiers.carries`: every number and every capitalised word (but *The*) of `said` in `text`."""
    for number in _NUMBER.finditer(said):
        if not re.search(r"\b" + re.escape(number.group()) + r"\b", text, re.ASCII):
            return False
    for capital in _CAPITAL.finditer(said):
        word = capital.group()
        if word != "The" and not re.search(r"\b" + re.escape(word) + r"(?!\w)", text, re.ASCII):
            return False
    return True


def _framed_off(condition: str) -> str:
    return FRAME.sub("", condition.strip(), count=1)


def same_qualifier(condition: str | None, part: str | None) -> bool:
    """`Qualifiers.sameQualifier` (145 FR-4a): `condition` names the same qualifier as the founder's `part` -- the
    qualifier (the part from its first DRAWN_QUALIFIER match on, a leading *who / that / which* off) has every number and
    capitalised word in the condition and no content word lost."""
    if condition is None or not condition.strip() or part is None:
        return False
    at = DRAWN_QUALIFIER.search(part)
    qualifier = part[at.start():].strip() if at else part.strip()
    qualifier = re.sub(r"(?i)^(?:who|that|which)\s+", "", qualifier, count=1)
    return _carries(condition, qualifier) and not dropped(qualifier, condition)


def in_core(core: str | None, condition: str | None) -> bool:
    """`Qualifiers.inCore` (146 FR-2): the segment `core` already says the `condition`, so a line composed from the two
    states it in the core alone. Read from the two alone (146 judgement call 1): (a) the condition with code's frame off
    has its numbers and names in the core, no content word lost and no negation dropped; or (b) it names the qualifier of
    one of the core's comma-, semicolon- or *and*-separated parts (`same_qualifier`, numbers and names held to the core,
    judgement call 2)."""
    if core is None or not core.strip() or condition is None or not condition.strip():
        return False
    said = _framed_off(condition)
    if negation_dropped(said, core) or not _carries(core, said):
        return False
    anything = bool(dropped(said, "")) or bool(re.search(r"\d", said)) or bool(re.search(r"\b[A-Z]", said, re.ASCII))
    if anything and not dropped(said, core):
        return True
    return any(DRAWN_QUALIFIER.search(part) and same_qualifier(condition, part)
               for part in re.split(r"[,;]|\band\b", core))


def head(people: str | None) -> str | None:
    """`Qualifiers.head` (146 FR-3): the people's head -- `people` cut at the last relative pronoun or preposition at or
    before its first DRAWN_QUALIFIER match, at least one word before it (judgement call 5: *learners at intermediate
    level* is cut at *at*, never inside the level); None where there is nothing to cut."""
    if people is None or not people.strip():
        return None
    text = people.strip()
    qualifier = DRAWN_QUALIFIER.search(text)
    if not qualifier:
        return None
    cut = -1
    for opens in OPENS_QUALIFIER.finditer(text):
        if opens.start() > qualifier.start():
            break
        cut = opens.start()
    if cut < 0 and qualifier.start() > 0 and text[qualifier.start() - 1].isspace():
        cut = qualifier.start() - 1
    out = text[:cut].strip() if cut >= 0 else ""
    return out or None


def says(people: str | None, condition: str | None) -> bool:
    """`Qualifiers.says` (146 FR-3, judgement call 4): the `condition` says what the `people` phrase already says -- its
    numbers and names in the phrase, at most one content word not (MOST_DROPPED), more in than out, an *-ing* verb read
    as its stem, no negation dropped. *work mostly for agencies* says what *freelance translators working for
    agencies* says."""
    if people is None or condition is None or not condition.strip():
        return False
    said = _framed_off(condition)
    if not _carries(people, said) or negation_dropped(said, people):
        return False
    phrase = re.sub(r"(?i)\b(\w{3,}?)ing\b", r"\1", people, flags=re.ASCII)
    content = dropped(said, "")
    lost = dropped(said, phrase, people)
    kept = len(content) - len(lost)
    return bool(content) and len(lost) <= MOST_DROPPED and kept > len(lost)


# ------------------------------------------------------------------------------------------- ReadBack

#: keel-cloud `ReadBack.OPENS_WITH_CONJUNCTION` (145 FR-3, moved by 146 FR-4, not widened): a circumstance that opens
#: with one of these five takes no second *when*.
OPENS_WITH_CONJUNCTION = re.compile(r"(?i)^(?:while|when|whenever|during|as)\b", re.ASCII)


def with_when(circumstance: str | None) -> str:
    """`ReadBack.withWhen` (146 FR-4): *when {circumstance}*, or the circumstance as it is where it already opens with
    *while*, *when*, *whenever*, *during* or *as* -- *while running payroll*, never *when while running payroll*."""
    stripped = (circumstance or "").strip()
    return stripped if OPENS_WITH_CONJUNCTION.match(stripped) else "when " + stripped


_RELATIVE = re.compile(r"(?i)\bwho\b")


def phrase(text) -> str:
    """`ReadBack.phrase`: stripped, spaces collapsed, no closing punctuation of its own."""
    out = " ".join(str(text or "").split())
    while out and out[-1] in ".,;:":
        out = out[:-1].strip()
    return out


def segment(core: str | None, condition: str | None) -> str:
    """`ReadBack.segment` (120, 146 FR-2): the core, and the condition after *, who* (after *and* where the core has a
    *who* clause of its own) unless the core already says it (`in_core`) -- a qualifier is said once."""
    seg = phrase(core)
    who = phrase(condition)
    if who.lower().startswith("who "):
        who = who[4:].strip()
    if not who or not seg or in_core(seg, who):
        return seg
    return seg + (" and " if _RELATIVE.search(seg) else ", who ") + who


def segment_line(core: str | None, condition: str | None) -> str | None:
    """`ContextSlots.segmentLine` (120, 146 FR-2): the core where there is no condition or the core already says it,
    else *{core}, who {condition}* -- its own join, as before (146 judgement call 3)."""
    if condition is None or not condition.strip() or core is None or in_core(core, condition):
        return core
    return f"{core.strip()}, who {condition.strip()}"


def interview_topic(first: str, actor_plural: str, circumstance: str) -> str:
    """`InterviewComposer.topic` (146 FR-4): *{first} is exploring what it is like for {actor_plural} when
    {circumstance}.*, *when* said once."""
    return f"{first} is exploring what it is like for {actor_plural} {with_when(circumstance)}."


def default_about(circumstance: str) -> str:
    """`Project.defaultAbout` (145 FR-3, 146 FR-4): the primary role's default line."""
    return "what it is like " + with_when(circumstance)
