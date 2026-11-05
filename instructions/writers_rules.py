"""Spec 137 FR-2 (keel-cloud 214, `domain.vectors.WritersRules`): the writers keep the rules the cards state, a
read-only port.

Each rule names a fault in the writer's own words, or none -- the cloud refuses on it once with the rule named, then
notes it and serves the draft as written (spec 114). Persona-free: the engine's own grammar words and the short stand-in
lists 214 names, never a trade's word. `L37` Importance's own row is never the job or the circumstance said again (and, keel-cloud 216 `L37b`, is
`went_wrong` said as the difficulty, on its verb);
`X14` the occasion is the hard case (never a *decision*, a bare *call*, *time* where the circumstance names a moment,
and its stem names the circumstance); `L38` a Keel rung never joins two outcomes, `L39` no two rungs are one set of
words; `L40` Purchase friction's suggested step is the buyer's brake, never the idea, the product or the founder's paper.
Every word list is the cloud's; `tests/test_cloud_214_mirror_137.py` holds them to its source.
"""

from __future__ import annotations

import re

from harness import qualifiers as founder_words
from instructions import spoken as spoken_mod
from instructions import wording as wording_mod

#: Any letter (Java's `\p{L}`).
_L = r"[^\W\d_]"

#: `WritersRules.SMALL`: words beside `FounderWords.STOP` that carry no noun or act of their own here.
SMALL = frozenset({
    "after", "before", "until", "during", "since", "other", "more", "less", "most", "least", "too", "much", "many",
    "very", "own", "really", "way", "ways", "where", "why", "how", "whether", "because", "though", "although", "once",
    "again", "only", "even", "both", "either", "neither", "such", "same", "lot", "lots", "thing", "things", "something",
    "anything", "everything", "nothing", "someone", "anyone", "everyone", "she's", "he's", "they're", "you're", "i'm",
    "we're", "don't", "doesn't", "didn't", "won't", "can't", "couldn't", "wasn't", "weren't", "isn't", "aren't", "i",
    "me", "my", "mine", "us", "we", "our"})


def root(word: str | None) -> str:
    """`WritersRules.root`: a word's root, so the forms of one word read as one -- the possessive off, an irregular past
    in its base, then a plural, an *-ing* or *-ed*, an *-er*, a final *e* and a doubled last letter."""
    w = (word or "").lower().replace("’", "'").strip()
    w = re.sub(r"'s$", "", w)
    w = re.sub(r"^['-]+|['-]+$", "", w)
    if len(w) < 3:
        return w
    past = spoken_mod.base_of_past(w)
    if past is not None:
        w = past
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif re.fullmatch(r".*(ss|x|z|ch|sh)es", w) and len(w) > 4:
        w = w[:-2]
    elif w.endswith("s") and not w.endswith("ss") and ((not w.endswith("us") and not w.endswith("is"))
                                                       or len(w) <= 4) and len(w) > 3:
        w = w[:-1]
    if w.endswith("ing") and len(w) > 5:
        w = w[:-3]
    elif w.endswith("ied") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("ed") and len(w) > 4:
        w = w[:-2]
    if w.endswith("er") and len(w) > 4:
        w = w[:-2]
    if w.endswith("e") and len(w) > 3:
        w = w[:-1]
    if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "aeiou":
        w = w[:-1]
    return w


def roots(text: str | None) -> list[str]:
    """`WritersRules.roots`: a text's content words as roots, in order, once each -- no stop word, no small word, no
    number, nothing under three letters."""
    out: list[str] = []
    for word in founder_words.words(text):
        bare = re.sub(r"'s$", "", word)
        if len(bare) < 3 or bare in founder_words.STOP or bare in SMALL or re.fullmatch(r"\d+", bare):
            continue
        r = root(bare)
        if r not in out:
            out.append(r)
    return out


#: `WritersRules.ING_NOUNS` (keel-cloud 216): the *-ing* words that are no verb's form (a time of day, a pronoun of
#: things).
ING_NOUNS = frozenset({"morning", "evening", "nothing", "something", "anything", "everything", "during", "ceiling",
                       "string", "thing", "king", "ring", "spring", "wing", "bring"})


def verb_roots(text: str | None) -> list[str]:
    """`WritersRules.verbRoots` (keel-cloud 216, E9 and `L37b`): a text's verbs as roots, in order, once each -- its
    content words (`roots`') that read as a verb's form: a present verb or a past code knows, a regular *-ed* or an
    *-ing*. No part of speech is tagged: a noun spelt as a verb (*log*, *call*) reads as one, so the rules that read these
    compare each field's own words, never the words two fields share."""
    out: list[str] = []
    for word in founder_words.words(text):
        bare = re.sub(r"'s$", "", word)
        if len(bare) < 3 or bare in founder_words.STOP or bare in SMALL or re.fullmatch(r"\d+", bare):
            continue
        verb = founder_words.present_verb(bare) or spoken_mod.base_of_past(bare) is not None \
            or (bare.endswith("ed") and len(bare) > 4 and not bare.endswith("eed")) \
            or (bare.endswith("ing") and len(bare) > 5 and bare not in ING_NOUNS)
        if verb:
            r = root(bare)
            if r not in out:
                out.append(r)
    return out


def head_verb(row: str | None) -> str | None:
    """`WritersRules.headVerb` (keel-cloud 216 FR-2, `L37b`): the own row's head verb as a root -- its first content word
    that reads as a verb (`verb_roots`), past an opening of *having*, *getting*, *being* (both STOP words: *Having a job
    killed for memory* reads *kill*); None where it has none."""
    for word in founder_words.words(row):
        one = verb_roots(word)
        if one:
            return one[0]
    return None


def own_row_hurt_fault(own_row: str | None, routine: str | None, went_wrong: str | None) -> str | None:
    """`WritersRules.ownRowHurtFault` (keel-cloud 216 FR-2, `L37b`; cycle 13's *Choosing where the raise cash sits*,
    *Guessing memory, GPUs and run time*, *Following and joining the conversation*): Importance's own row is `went_wrong`
    said as the difficulty -- refused where the row's head verb is no root of `went_wrong`, or is a root of the routine's
    own words alone (what `routine` says beyond `went_wrong`). None where either field is blank or the row has no verb
    (L20 and L22 hold its shape); L37 stands beside it. Refused once, then noted and served as drafted."""
    if own_row is None or not own_row.strip() or went_wrong is None or not went_wrong.strip():
        return None
    verb = head_verb(own_row)
    if verb is None:
        return None
    hurt = set(roots(went_wrong))
    routine_own = (set(roots(routine)) if routine else set()) - hurt
    if verb in hurt and verb not in routine_own:
        return None
    return (f"L37b: the own row '{own_row.strip()}' is not the hurt Prevalence tests (went_wrong: '{went_wrong.strip()}')"
            + (f" -- its verb is the routine's ('{(routine or '').strip()}')" if verb in routine_own else "")
            + "; the own row is went_wrong said as the difficulty, in its -ing form, at most six words -- the part that "
              "hurt, never the circumstance and never the whole job (the test: would every one of them who did the "
              "day's work say it was hard? then it is the routine)")


# ------------------------------------------------------------------------------------------ L37: Importance's own row

def own_row_fault(own_row: str | None, job: str | None, circumstance: str | None, *people: str) -> str | None:
    """`WritersRules.ownRowFault` (keel-cloud 214 FR-1, `L37`): Importance's own row is the difficulty with its verb at
    that moment, never the job or the circumstance said again -- refused where every content word of it (the people's
    own words aside) is in the context's `job`, or every one is in its `circumstance`; words merely shared with both are
    no fault. None where it holds."""
    if own_row is None or not own_row.strip() or ((job is None or not job.strip())
                                                   and (circumstance is None or not circumstance.strip())):
        return None
    own = set(roots(own_row))
    for who in people:
        own -= set(roots(who))
    if not own:
        return None
    if not own <= set(roots(job)) and not own <= set(roots(circumstance)):
        return None
    return (f"L37: the own row '{own_row.strip()}' is the job or the circumstance said again (\""
            f"{(job or '').strip()}\"; \"{(circumstance or '').strip()}\"); it is the difficulty with its verb at that "
            "moment -- the one part that is hard, in the people's words, at most six words -- never the whole job")


# ------------------------------------------------------------------------------------------ X14: the occasion

#: `WritersRules.DECISIONS`, `CALLS`, `TIMES`: the stand-ins for the act an occasion's head never is.
DECISIONS = frozenset({"decision", "decisions"})
CALLS = frozenset({"call", "calls"})
TIMES = frozenset({"time", "times"})
#: `WritersRules.PLURAL_VERBS`: the plural verbs a circumstance's subject agrees with.
PLURAL_VERBS = frozenset({"are", "were", "have", "come", "go", "get", "pile", "run", "arrive", "ring", "happen", "need",
                          "keep", "stay", "fail", "start", "end", "land", "build", "stack"})
_LW = rf"(?:{_L}|['-])+"
_LH = rf"(?:{_L}|-)+"
ONE_OF_MANY = re.compile(rf"(?i)^(?:(?:the|their|your)\s+{_LW}'s\s+)?(?:a|an|every|each)\s+({_LH}(?:\s+{_LH})?)")


def moment(circumstance: str | None) -> str | None:
    """`WritersRules.moment` (214 FR-2): the moment a circumstance names -- its subject where it is one of many (opened
    by *a*, *an*, *every*, *each*, or a plural its plural verb agrees with); None for a single standing thing."""
    if circumstance is None or not circumstance.strip():
        return None
    text = circumstance.strip()
    one = ONE_OF_MANY.search(text)
    if one:
        noun = one.group(1).strip()
        two = noun.split()
        if len(two) == 2:
            second = two[1].lower()
            if second in founder_words.STOP or second in SMALL or second in PLURAL_VERBS or second.endswith("s"):
                noun = two[0]
        return noun
    words = text.split()
    for i in range(1, min(len(words), 6)):
        verb = re.sub(r"[^a-z']", "", words[i].lower())
        before = re.sub(r"[^a-z']", "", words[i - 1].lower())
        if verb in PLURAL_VERBS and before.endswith("s") and not before.endswith("ss") and not before.endswith("'s") \
                and before not in founder_words.STOP and before not in SMALL:
            noun = []
            for k in range(max(0, i - 2), i):
                w = re.sub(rf"(?!{_L}|['-]).", "", words[k])
                lower = w.lower()
                if lower and lower not in founder_words.STOP and not lower.endswith("'s"):
                    noun.append(w)
            return before if not noun else " ".join(noun)
    return None


#: `OccasionStem.ATTEMPT`.
ATTEMPT = "the last time you tried to "


def when_clause(stem: str | None) -> str | None:
    """`OccasionStem.whenClause` (keel-cloud 120): the stem's *when* clause, read back; None where the stem opens no way
    code wrote."""
    if stem is None:
        return None
    text = wording_mod.clause(stem)
    lower = text.lower()

    def blank_to_none(t: str) -> str | None:
        t = t.strip()
        return t or None
    if lower.startswith(ATTEMPT):
        return text[len("the last time "):]
    if lower.startswith("the last time "):
        return blank_to_none(text[len("the last time "):])
    if lower.startswith("last week, when "):
        return blank_to_none(text[len("last week, when "):])
    if lower.startswith("over the last "):
        at = lower.find(", when ")
        return None if at < 0 else blank_to_none(text[at + len(", when "):])
    return None


def occasion_fault(noun: str | None, stem: str | None, circumstance: str | None, founders_noun: bool) -> str | None:
    """`WritersRules.occasionFault` (214 FR-2, `X14`): the occasion strangers are asked about is the hard case, never a
    stand-in for the act -- refused where the noun's head is a *decision*, a bare *call*, *time* alone where the
    circumstance names a moment (`moment`), or where the stem names no word of the circumstance. A noun the founder
    typed is theirs: only the stem is read then. None where it holds."""
    def clean(t):
        return "" if t is None else t.strip()
    if not founders_noun and noun is not None and noun.strip():
        words = founder_words.words(noun)
        head = words[-1] if words else ""
        if head in DECISIONS:
            return (f"X14: occasion '{noun.strip()}' is a decision, a stand-in for the act; the occasion is the hard "
                    "case strangers can picture -- the thing the job is done on or for, where the circumstance strikes "
                    f"(\"{clean(circumstance)}\")")
        if len(words) == 1 and head in CALLS:
            return (f"X14: occasion '{noun.strip()}' alone reads as a judgement call; name the kind of call as the "
                    f"people say it, the one where the circumstance strikes (\"{clean(circumstance)}\")")
        at = moment(circumstance)
        if len(words) == 1 and head in TIMES and at is not None:
            return (f"X14: occasion 'time' alone, where the circumstance names a moment ('{at}'); the occasion is that "
                    "moment, singular, in the people's words")
    if stem is not None and stem.strip() and circumstance is not None and circumstance.strip():
        when = when_clause(stem)
        said = set(roots(stem if when is None else when))
        if said and not said & set(roots(circumstance)):
            return (f"X14: the stem '{clean(stem)}' names no word of the circumstance (\"{clean(circumstance)}\"); the "
                    "stem is the circumstance said to them, the hard case the questions are about")
    return None


# ------------------------------------------------------------------------------------------ L38, L39: the rungs

#: `WritersRules.STATE_VERBS`: the words that may open a second state after *or* / *and*.
STATE_VERBS = frozenset({
    "was", "were", "is", "are", "had", "has", "have", "did", "do", "does", "got", "get", "gets", "went", "go", "goes",
    "could", "couldn't", "can", "can't", "would", "will", "didn't", "wasn't", "weren't", "never", "ended", "left",
    "lost", "stayed", "sat", "took", "ran", "made", "kept", "felt", "came", "gave", "fell", "missed", "needed"})
#: `WritersRules.SUBJECTS`: a subject a second state may open on before its verb.
SUBJECTS = frozenset({"i", "it", "they", "we", "you", "he", "she", "someone", "everyone", "nobody", "that", "this"})
_JOIN = re.compile(r"(?i),?\s+\b(or|and)\b\s+")


def _verb_like(word: str | None) -> bool:
    if word is None or len(word) < 2:
        return False
    return word in STATE_VERBS or spoken_mod.base_of_past(word) is not None or \
        (word.endswith("ed") and len(word) > 4 and not word.endswith("eed"))


def _has_verb(text: str) -> bool:
    return any(_verb_like(w) for w in re.split(r"[^a-z']+", text.lower().replace("’", "'")))


def joined_fault(rung: str | None) -> str | None:
    """`WritersRules.joinedFault` (214 FR-3, `L38`): a rung of Keel's that joins two outcomes with *or* / *and* -- the
    words after the join open a verb of their own (an adverb and a subject may come first); *and still* / *and yet* is
    one outcome; a join inside one outcome (*a try or two*) is none. None where it holds."""
    if rung is None or not rung.strip():
        return None
    text = re.sub(r"[.!]+$", "", rung.strip())
    for join in _JOIN.finditer(text):
        left, right = text[:join.start()], text[join.end():]
        if not _has_verb(left):
            continue
        after = re.split(r"[^a-z']+", right.lower().replace("’", "'"))
        if after and after[0] in ("still", "yet"):
            continue
        k = 0
        while k < len(after) and (not after[k] or (after[k].endswith("ly") and len(after[k]) > 3)
                                  or after[k] in SUBJECTS):
            k += 1
        if k < len(after) and _verb_like(after[k]):
            return (f"L38: '{rung.strip()}' joins two outcomes with '{join.group(1).lower()}' ('{left.strip()}' and "
                    f"'{right.strip()}'); each rung is one outcome, one state on the list's one scale -- keep one, or "
                    "say the worse one alone")
    return None


def same_words(a: str | None, b: str | None) -> bool:
    """`WritersRules.sameWords` (214 FR-3, `L39`): two rungs whose content words are one set (by root)."""
    ra = set(roots(a))
    return bool(ra) and ra == set(roots(b))


def rung_faults(rows: list[str], keels: list[bool]) -> list[str]:
    """`ScreenResultApplier`'s ladder read (214 FR-3): `L38` on each of Keel's rungs, `L39` on each pair one of which is
    Keel's -- the faults in the cloud's words, in its order."""
    faults: list[str] = []
    for j, rung in enumerate(rows):
        if keels[j]:
            fault = joined_fault(rung)
            if fault:
                faults.append(fault)
        for i in range(j):
            if (keels[i] or keels[j]) and same_words(rows[i], rows[j]):
                at, other = (j, i) if keels[j] else (i, j)
                faults.append(f"L39: '{rows[at]}' says what '{rows[other]}' says, in the same words; each rung is one "
                              "distinct outcome on the one scale -- write another, worse or better")
    return faults


def typed_in_answer(rung: str | None, answer: str | None) -> bool:
    """`ScreenResultApplier.typedInAnswer` (214 FR-3): a rung the founder typed in the Answer is theirs, never Keel's."""
    if rung is None or not rung.strip() or answer is None or not answer.strip():
        return False
    said = re.sub(r"\s+", " ", re.sub(r"[.!]+$", "", rung.strip())).lower()
    return said in re.sub(r"\s+", " ", answer).lower()


# ------------------------------------------------------------------------------------------ L40: Purchase friction

PRODUCT = re.compile(rf"(?i)(?<!{_L})(?<!-)(products?|product's)(?!{_L}|-)")
FORMALITY = re.compile(rf"(?i)(?<!{_L})(?<!-)(contracts?|terms|agreements?|purchase orders?|order forms?|invoices?)"
                       rf"(?!{_L}|-)")


def _l40(step: str, what: str) -> str:
    return (f"L40: Keel's suggested step '{step.strip()}' {what}; a suggested step is the buyer's own brake -- the review "
            "or approval this buyer's own process has -- never the idea, the product or the founder's contract")


def founders_side_fault(step: str | None, names: list[str] | None) -> str | None:
    """`WritersRules.foundersSideFault` (214 FR-4, `L40`): Purchase friction's one suggested step names the idea, the
    founder's product or a formality of the founder's own paper. None where it names none."""
    if step is None or not step.strip():
        return None
    for name in names or []:
        if name and name.strip() and re.search(rf"(?i)(?<!{_L}){re.escape(name.strip())}(?!{_L})", step):
            return _l40(step, f"names the idea ('{name.strip()}')")
    product = PRODUCT.search(step)
    if product:
        return _l40(step, f"checks the founder's product ('{product.group(1)}')")
    formality = FORMALITY.search(step)
    if formality:
        return _l40(step, f"is a formality of the founder's own paper ('{formality.group(1)}')")
    return None
