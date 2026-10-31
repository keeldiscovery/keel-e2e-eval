"""keel-cloud 146 (`domain.vectors.Qualifiers`, `FounderWords`, `ReadBack.withWhen`), 148 and 149, mirrored: the
qualifiers of the founder's WHICH PEOPLE that a stranger answers about themselves, and the two seams 146 closed on the
lines composed from the segment and its condition -- a qualifier is said once (`in_core`), and the decision-maker's
chip names the people once (`head`, `says`) -- with "when" said once before a circumstance (`with_when`).

Mirrored character for character so the harness predicts what the cloud serves (spec 077); every pattern is the
cloud's, compiled ASCII as Java's `\\w` and `\\b` read ASCII text. 146's judgement calls are the cloud's and are kept:
the "said once" rule is read from the core and the condition alone (Issen's *not starting from zero* against *are past
the beginner stage* shares no words and keeps its clause); `says` allows one content word of difference
(`MOST_DROPPED`) and reads an *-ing* verb as its stem (*working* / *work*); `head` cuts at the last relative pronoun or
preposition at or before the qualifier (*learners at intermediate level* -> *learners*).

keel-cloud 149 (spec 085): a list *A, B or C* is one part (`parts`), a participle names its verb (`bare`), the job is
said on the people's verb (`they`), and the condition code draws keeps the founder's subject (`thing_of_theirs`,
`organisations_clause`, read by `vectors_script.condition_from` before its tool branch).
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

#: keel-cloud `Qualifiers.ITEM_OPENS` (149 FR-3): a word that opens a clause of its own, never a list's item -- a
#: relative pronoun, a preposition, a negation, a conjunction, a participle or an adverb (lower case: *Beijing* and
#: *Italy* are items).
_ITEM_OPENS = (r"(?!(?:who|whose|that|which|where|when|while|with|without|in|at|on|of|for"
               r"|from|by|to|into|across|within|not|no|never|but|and|or)\b|(?-i:[a-z]+(?:ing|ly))\b)")
#: `Qualifiers.ITEM`: one item of a list before its closing *or* / *and* -- one to three words.
_ITEM = _ITEM_OPENS + r"[^,;\s]+(?:\s+(?!(?:and|or)\b)[^,;\s]+){0,2}"
#: `Qualifiers.LIST`: a list's run after a comma -- items of one to three words, the last joined by *or* or *and*
#: (*Mercury, Brex or similar*; *OPERA Cloud, Sihot and Apaleo*): its commas and its closing *and* stay in the part.
LIST = re.compile(r"(?i)(?:,\s*" + _ITEM + r")*,\s*" + _ITEM + r"\s+(?:or|and)\s+" + _ITEM_OPENS
                  + r"[^,;]+?(?=\s+and\b|\s*[,;]|\s*$)", re.ASCII)


def _java_split(pattern: str, text: str) -> list[str]:
    """`String.split(regex)`: the trailing empty strings dropped, the text whole where nothing matches."""
    pieces = re.split(pattern, text)
    if len(pieces) == 1:
        return pieces
    while pieces and pieces[-1] == "":
        pieces.pop()
    return pieces


def parts(text: str | None) -> list[str]:
    """`Qualifiers.parts` (130 FR-8, 149 FR-3): the parts of a people phrase -- split as X8 reads them (commas,
    semicolons, *and*), never inside a list (`LIST`): *venture-backed startups in the US within two years of a raise,
    banking with Mercury, Brex or similar* is two parts, the second *banking with Mercury, Brex or similar*. `in_core`
    and the draw (`vectors_script.drawn_condition`) read the same parts. Unstripped, as `String.split` gives them."""
    if text is None:
        return []
    kept: list[str] = []
    at = 0
    for found in LIST.finditer(text):
        kept.append(text[at:found.start()])
        kept.append(re.sub(r"\band\b", "\u0002", found.group().replace(",", "\u0001")))
        at = found.end()
    kept.append(text[at:])
    return [part.replace("\u0001", ",").replace("\u0002", "and")
            for part in _java_split(r"[,;]|\band\b", "".join(kept))]


def bare(text: str) -> str:
    """`Qualifiers.bare` (149 FR-3): the qualifier verbs a participle says (*banking with* is *bank with*), so a
    condition that says the verb in its own person names the same qualifier."""
    text = re.sub(r"(?i)\b(bank|work|own|employ)ing\b", r"\1", text)
    text = re.sub(r"(?i)\brunning\b", "run", text)
    return re.sub(r"(?i)\boperating\b", "operate", text)


# ------------------------------------------------------------------------------------------- the drawn condition
# keel-cloud 149 FR-3 (`ScreenResultApplier.thingOfTheirs`, `organisationsClause`, 131's frame, `ORGANISATIONS`,
# `singular`, `article`; `StrangerGrammar.presentVerb`): what `vectors_script.condition_from` draws before its tool
# branch, so the tool branch draws only where the people are the subject.

#: keel-cloud `StrangerGrammar.VERBS`: the present verbs code turns.
_VERBS = frozenset((
    "want", "need", "have", "try", "must", "can", "get", "go", "make", "take", "lose", "pay", "spend", "wait", "decide",
    "convert", "move", "check", "call", "ask", "look", "hold", "keep", "send", "start", "stop", "feel", "fall", "run",
    "sit", "stand", "work", "practise", "practice", "talk", "type", "upload", "sort", "choose", "buy", "find", "miss",
    "struggle", "answer", "pass", "sell", "use", "open", "close", "fill", "file", "book", "log", "track", "review",
    "plan", "prepare", "write", "read", "update", "chase", "fix", "learn", "give", "tell", "hire", "end", "finish",
    "leave", "come", "see", "cross", "arrive", "land", "reach", "break", "slip", "pile", "cry", "wake", "ring", "bank",
    "raise", "earn", "own", "rent", "drive"))
#: keel-cloud `StrangerGrammar.IRREGULAR`'s presents.
_IRREGULAR = frozenset((
    "are", "is", "have", "has", "do", "does", "go", "get", "make", "take", "see", "come", "know", "find", "give", "tell",
    "feel", "leave", "keep", "begin", "run", "sit", "stand", "lose", "pay", "send", "spend", "buy", "bring", "think",
    "hold", "can", "will", "may", "must", "put", "set", "cut", "let", "read", "write", "speak", "meet", "sell", "wake",
    "eat", "fall", "drive", "ride", "build", "hear", "mean", "say", "become", "choose", "win", "fly", "grow", "wear",
    # keel-cloud 170 FR-5 (spec 110): a founder's loss line said in the past (*rang*, *caught*)
    "ring", "catch"))


def present_verb(word: str | None) -> bool:
    """`StrangerGrammar.presentVerb`: a present verb code turns (*must*, *can*, *will*, *may* only by `_VERBS`)."""
    if word is None or not word.strip():
        return False
    lower = word.strip().lower()
    return lower in _VERBS or (lower in _IRREGULAR and lower not in ("must", "can", "will", "may"))


def _verb_form(word: str) -> bool:
    """`ScreenResultApplier.verbForm` (149 FR-3.1): a present verb in either person (*run*, *runs*, *is*, *has*)."""
    lower = word.lower()
    return (lower in ("is", "are", "has", "have") or present_verb(lower)
            or (lower.endswith("es") and present_verb(lower[:-2]))
            or (lower.endswith("s") and present_verb(lower[:-1])))


#: keel-cloud `ScreenResultApplier.ORGANISATIONS` (145 FR-4a): the nouns that name an organisation the person works at.
ORGANISATIONS = frozenset((
    "company", "business", "firm", "organization", "organisation", "agency", "department", "practice", "clinic",
    "hospital", "school", "district", "plant", "factory", "warehouse", "store", "shop", "restaurant", "hotel", "office",
    "studio", "startup", "team", "group", "bank", "lab", "site", "branch", "location", "employer", "brand", "retailer",
    "chain", "fleet", "venue", "property", "farm", "center", "centre", "institution", "university", "college",
    "charity", "nonprofit", "council", "carrier", "airline", "insurer", "manufacturer", "distributor", "operator",
    "provider", "network", "enterprise", "corporation"))


def singular(noun: str) -> str:
    """`ScreenResultApplier.singular` (145 FR-4a): one of a plural noun (*companies* -> *company*)."""
    if noun.endswith("ies") and len(noun) > 3:
        return noun[:-3] + "y"
    if noun.endswith(("sses", "ches", "shes", "xes")):
        return noun[:-2]
    return noun[:-1] if noun.endswith("s") and not noun.endswith("ss") else noun


def article(noun: str) -> str:
    """`ScreenResultApplier.article`."""
    return "an " if re.match(r"[aeiou]", noun) else "a "


def thing_of_theirs(text: str) -> str | None:
    """`ScreenResultApplier.thingOfTheirs` (149 FR-3.1): a thing of the people's -- *whose {thing} {verb} ...* -- said
    of that thing: *whose jobs run on Procore or ACC* -> *have jobs that run on Procore or ACC*, a singular thing with
    its article (*whose team shares a cluster* -> *have a team that shares a cluster*); None where the part says none.
    The thing is the word after *whose*, or the two where the third is the verb."""
    whose = re.search(r"(?i)\bwhose\s+(.+)$", text)
    if not whose:
        return None
    said = whose.group(1).strip().split()
    if len(said) < 2:
        return None
    verb = 2 if len(said) > 2 and not _verb_form(said[1]) and _verb_form(said[2]) else 1
    thing, rest = " ".join(said[:verb]), " ".join(said[verb:])
    last = said[verb - 1].lower()
    plural = last.endswith("s") and not last.endswith("ss")
    return "have " + ("" if plural else article(thing.lower())) + thing + " that " + rest


def organisation_frame(text: str) -> str | None:
    """`ScreenResultApplier.conditionFrom`'s 131 FR-6 branch: the people's organisation qualified by a relative clause,
    said of one person -- *reservation agents at hotel groups in Germany that run a central reservations office* ->
    *work at a hotel group in Germany that runs a central reservations office*; None otherwise."""
    org = re.search(r"(?i)\bat\s+(.+?)\s+(?:that|which)\s+(run|operate|own|employ)s?\s+(.+)$", text)
    if not org or re.search(r"(?i)\b(?:that|which|who)\b", org.group(1)):
        return None
    split = re.split(r"(?i)\s+(?=(?:in|across|from|on)\s)", org.group(1).strip(), maxsplit=1)
    head = split[0].strip()
    one = head[:-3] + "y" if head.endswith("ies") else head[:-1] if head.endswith("s") and not head.endswith("ss") \
        else head
    rest = re.sub(r"(?i)\btheir\b", "its", org.group(3).strip())
    if re.match(r"[A-Z]{2,}\b", one):
        said = "an " if re.match(r"[AEFHILMNORSX]", one) else "a "
    else:
        said = "an " if re.match(r"[aeiou]", one.lower()) else "a "
    return ("work at " + said + one + (" " + split[1].strip() if len(split) > 1 else "") + " that "
            + org.group(2).lower() + "s " + rest)


#: `ScreenResultApplier.ORGANISATION_RELATIVE` (149 FR-3.2): the verbs an organisation is qualified by.
_ORGANISATION_RELATIVE = re.compile(r"(?i)\b(?:that|which)\s+(bank|run|work|operate|own|employ)s?\s+(.+)$")
#: `ScreenResultApplier.ORGANISATION_PARTICIPLE`: the same verbs as a participle (*banking with*, *running on*).
_ORGANISATION_PARTICIPLE = re.compile(r"(?i)(?:^|\s)(banking|running|working|operating|owning|employing)\s+(.+)$")


def organisations_clause(part: str, before: str | None) -> str | None:
    """`ScreenResultApplier.organisationsClause` (149 FR-3.2): a part that qualifies the people's organisation by a
    relative clause or a participle, without 131's *at X that run Y* frame, draws that frame on the organisation's head
    noun -- the last noun of `ORGANISATIONS` said before the clause, in the part or the parts ahead of it (`before`):
    *venture-backed startups in the US within two years of a raise, banking with Mercury, Brex or similar* -> *work at a
    startup that banks with Mercury, Brex or similar*. None where no organisation is named before it (the people are
    the subject: the tool branch's)."""
    clause = _ORGANISATION_RELATIVE.search(part) or _ORGANISATION_PARTICIPLE.search(part)
    if not clause:
        return None
    said = (before or "") + " " + part[:clause.start()]
    head = None
    for word in re.split(r"[^a-z]+", said.lower()):
        if word and singular(word) in ORGANISATIONS:
            head = singular(word)
    if head is None:
        return None
    verb = clause.group(1).lower()
    base = "run" if verb == "running" else "operate" if verb == "operating" else \
        verb[:-3] if verb.endswith("ing") else verb
    return f"work at {article(head)}{head} that {base}s {clause.group(2).strip()}"


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
    """`Qualifiers.sameQualifier` (145 FR-4a, 149 FR-3): `condition` names the same qualifier as the founder's `part` --
    the qualifier (the part from its first DRAWN_QUALIFIER match on, a leading *who / that / which* off) has every number
    and capitalised word in the condition and no content word lost, a participle read as its verb (`bare`)."""
    if condition is None or not condition.strip() or part is None:
        return False
    at = DRAWN_QUALIFIER.search(part)
    qualifier = part[at.start():].strip() if at else part.strip()
    qualifier = re.sub(r"(?i)^(?:who|that|which)\s+", "", qualifier, count=1)
    # keel-cloud 149 FR-3: a participle is its verb (*banking with Mercury* is named by *banks with Mercury*)
    return _carries(condition, qualifier) and not dropped(bare(qualifier), bare(condition))


def in_core(core: str | None, condition: str | None) -> bool:
    """`Qualifiers.inCore` (146 FR-2): the segment `core` already says the `condition`, so a line composed from the two
    states it in the core alone. Read from the two alone (146 judgement call 1): (a) the condition with code's frame off
    has its numbers and names in the core, no content word lost and no negation dropped; or (b) it names the qualifier of
    one of the core's comma-, semicolon- or *and*-separated parts (`same_qualifier`, numbers and names held to the core,
    judgement call 2) -- since keel-cloud 149 FR-3 never inside a list (`parts`)."""
    if core is None or not core.strip() or condition is None or not condition.strip():
        return False
    said = _framed_off(condition)
    if negation_dropped(said, core) or not _carries(core, said):
        return False
    anything = bool(dropped(said, "")) or bool(re.search(r"\d", said)) or bool(re.search(r"\b[A-Z]", said, re.ASCII))
    if anything and not dropped(said, core):
        return True
    return any(DRAWN_QUALIFIER.search(part) and same_qualifier(condition, part) for part in parts(core))


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


#: keel-cloud `ReadBack.OWN_PRONOUN` (148 FR-2): a condition that opens with a relative pronoun of its own other than
#: *who* keeps it, after a comma, never after the sentence's *who*.
_OWN_PRONOUN = re.compile(r"(?i)^(?:whose|that|which)\s", re.ASCII)


def segment(core: str | None, condition: str | None) -> str:
    """`ReadBack.segment` (120, 146 FR-2, 148 FR-2): the core, and the condition after *, who* (after *and* where the
    core has a *who* clause of its own) unless the core already says it (`in_core`) -- a qualifier is said once; a
    condition that opens with *whose*, *that* or *which* keeps its own pronoun after a comma (*and whose ...* after a
    core's own *who* clause), never *who whose*."""
    seg = phrase(core)
    who = phrase(condition)
    if who.lower().startswith("who "):
        who = who[4:].strip()
    if not who or not seg or in_core(seg, who):
        return seg
    if _RELATIVE.search(seg):
        return seg + " and " + who
    return seg + (", " if _OWN_PRONOUN.match(who) else ", who ") + who


def segment_line(core: str | None, condition: str | None) -> str | None:
    """`ContextSlots.segmentLine` (120, 146 FR-2, 148 FR-2; 149 does not move it): the core where there is no condition
    or the core already says it, else the segment whole as `segment` composes it (*{core}, who {condition}*, *and* after
    the core's own *who* clause, a condition's own *whose* / *that* / *which* kept) -- no capital, no full stop."""
    if condition is None or not condition.strip() or core is None or in_core(core, condition):
        return core
    return segment(core, condition)


# keel-cloud 149 FR-2 (`ReadBack.they`): the job on a verb of the people's own -- *they want to {job}*, or *they {job}*
# where the job already says its want.

#: `ReadBack.OWN_WANT`: a job that opens with a want of its own (*need to keep the money ...*, *must file*).
_OWN_WANT = re.compile(r"(?i)^(?:(?:want|need|try|have)\s+to|must)\s.*", re.ASCII)
#: `ReadBack.THIRD_PERSON_WANT`: the same said of one (*needs to*, *tries to*, *has to*).
_THIRD_PERSON_WANT = re.compile(r"(?i)^(wants|needs|tries|has)\s+to\s+(.*)$", re.ASCII)
#: `ReadBack.TRYING`: a job that opens on *trying to* or *are trying to*.
_TRYING = re.compile(r"(?i)^(?:are\s+)?trying\s+to\s+(.*)$", re.ASCII)


def they(job: str) -> str:
    """`ReadBack.they` (149 FR-2): a job that already says its own want -- *want to*, *need to*, *try to*, *have to*,
    *must*, and (149's judgement call 1) the third-person *wants to* / *needs to* / *tries to* / *has to*, said of the
    people as theirs -- takes *they* alone; *trying to* or *are trying to* takes *they are trying to*; a job that
    already opens with *they* is kept; a bare *to ...* takes *they want*; every other job *they want to {job}*. *must*
    opens a want only as a word (*mustard* does not)."""
    lower = job.lower()
    if lower.startswith("they "):
        return job
    trying = _TRYING.fullmatch(job)
    if trying:
        return "they are trying to " + trying.group(1)
    third = _THIRD_PERSON_WANT.fullmatch(job)
    if third:
        verb = third.group(1).lower()
        said = {"tries": "try", "has": "have"}.get(verb, verb[:-1])
        return f"they {said} to {third.group(2)}"
    if _OWN_WANT.fullmatch(job):
        return "they " + job
    if lower.startswith("to "):
        return "they want " + job
    return "they want to " + job


def interview_topic(first: str, actor_plural: str, circumstance: str) -> str:
    """`InterviewComposer.topic` (146 FR-4): *{first} is exploring what it is like for {actor_plural} when
    {circumstance}.*, *when* said once."""
    return f"{first} is exploring what it is like for {actor_plural} {with_when(circumstance)}."


def default_about(circumstance: str) -> str:
    """`Project.defaultAbout` (145 FR-3, 146 FR-4): the primary role's default line."""
    return "what it is like " + with_when(circumstance)
