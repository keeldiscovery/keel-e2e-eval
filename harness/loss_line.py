"""keel-cloud 170 FR-5 (`LossLine`, with the parts of `StrangerGrammar`, `BeliefSentence`, `OccasionNoun` and
`CostEstimate` it stands on), ported line for line for the referee (keel-e2e-eval spec 110 FR-3).

The founder's loss line -- what they typed to *what do they lose?* on a rate -- read for the stranger's cost question:
the thing lost and the line's own verb, turned to the stranger's person and the window's past by code, never a model.
Four shapes, by where the line's own verb stands: `DOES` (*Runs that fail in front of customers ...*), `DONE_BY` (*GPU
hours and memory that jobs reserve and never use*), `DONE` (*Bookings lost when a call rings out ...*), `NONE` (*Interest
on cash that sits in the operating account*). No list of trades: only English's small words and the common verbs
`StrangerGrammar` already turns. `harness.vectors_script.cost_question` is `CommercialChain.costQuestion` on top of it.

**A mirror, never a re-derivation**: every function names the Java it comes from and keeps its order of tests, so a
disagreement with keel-cloud's seventeen worked cases (`src/test/resources/commercial-chain/*.json`) is a port fault to
fix here, not a judgement (`tests/test_lock_frontier_110.py` holds the port to them and to 170's own frame tests).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from harness.qualifiers import _VERBS as VERBS
from harness.qualifiers import present_verb

# ------------------------------------------------------------------------------------- StrangerGrammar (mirrored)

#: `StrangerGrammar.IRREGULAR` (keel-cloud 170 adds *ring* and *catch*).
IRREGULAR = {
    "are": "were", "is": "was", "have": "had", "has": "had", "do": "did", "does": "did", "go": "went", "get": "got",
    "make": "made", "take": "took", "see": "saw", "come": "came", "know": "knew", "find": "found", "give": "gave",
    "tell": "told", "feel": "felt", "leave": "left", "keep": "kept", "begin": "began", "run": "ran", "sit": "sat",
    "stand": "stood", "lose": "lost", "pay": "paid", "send": "sent", "spend": "spent", "buy": "bought",
    "bring": "brought", "think": "thought", "hold": "held", "can": "could", "will": "would", "may": "might",
    "must": "had to", "put": "put", "set": "set", "cut": "cut", "let": "let", "read": "read", "write": "wrote",
    "speak": "spoke", "meet": "met", "sell": "sold", "wake": "woke", "eat": "ate", "fall": "fell", "drive": "drove",
    "ride": "rode", "build": "built", "hear": "heard", "mean": "meant", "say": "said", "become": "became",
    "choose": "chose", "win": "won", "fly": "flew", "grow": "grew", "wear": "wore", "ring": "rang", "catch": "caught"}
#: `StrangerGrammar.KEEP`: words after a subject that are no present verb to turn.
KEEP = frozenset(("could", "would", "should", "might", "had", "were", "was", "did", "already", "still", "also", "just",
                  "often", "always", "never", "usually", "only", "all", "both", "each", "then", "really", "not"))
_THIRD = re.compile(r"\b(they're|they've|they'd|they'll|they|their|theirs|themselves)\b", re.IGNORECASE)
_TURNED = {"they're": ("you were", "you're"), "they've": ("you've",) * 2, "they'd": ("you'd",) * 2,
           "they'll": ("you'll",) * 2, "their": ("your",) * 2, "theirs": ("yours",) * 2,
           "themselves": ("yourself",) * 2}


def java_split(text: str) -> list[str]:
    """Java's `text.split("\\\\s+")`: a leading run of space gives a leading empty string, trailing ones none."""
    parts = re.split(r"\s+", text)
    while len(parts) > 1 and parts[-1] == "":
        parts.pop()
    return parts


def words(text) -> int:
    """`SpokenForm.words`."""
    return 0 if text is None or not str(text).strip() else len(str(text).strip().split())


def third_person(clause) -> bool:
    """`StrangerGrammar.thirdPerson`: whether a clause speaks of *they* / *their*."""
    return clause is not None and _THIRD.search(clause) is not None


def past_of(verb: str):
    """`StrangerGrammar.pastOf`: the past of a present verb, or `None` for a word that is not one this turns."""
    lower = verb.lower()
    if lower in KEEP or lower.endswith("ed") or len(lower) < 2:
        return None
    if lower in IRREGULAR:
        return IRREGULAR[lower]
    if lower.endswith("e"):
        past = lower + "d"
    elif lower.endswith("y") and len(lower) > 2 and lower[-2] not in "aeiou":
        past = lower[:-1] + "ied"
    elif lower.endswith("s") and not lower.endswith("ss"):
        if lower.endswith("ies"):
            base = lower[:-3] + "y"
        elif lower.endswith("es") and (lower.endswith("shes") or lower.endswith("ches") or lower.endswith("xes")):
            base = lower[:-2]
        else:
            base = lower[:-1]
        return past_of(base)
    else:
        past = lower + "ed"
    return past[:1].upper() + past[1:] if verb[:1].isupper() else past


def _past_after(text: str, at: int) -> str:
    """`StrangerGrammar.pastAfter`: the verb just after a subject *you*, and one known verb joined to it by *and*."""
    head, rest = text[:at], text[at:]
    word = re.match(r"(\s+)([A-Za-z']+)", rest)
    if not word:
        return text
    past = past_of(word.group(2))
    if past is None:
        return text
    after = rest[word.end():]
    joined = re.match(r"(.*?\band\s+)([A-Za-z]+)\b", after)
    if joined and len(java_split(joined.group(1))) <= 6 and joined.group(2).lower() in VERBS:
        second = past_of(joined.group(2))
        if second is not None:
            after = joined.group(1) + second + after[joined.end():]
    return head + word.group(1) + past + after


def second_person(clause, past: bool):
    """`StrangerGrammar.secondPerson`: every *they* / *their* is *you* / *your*; with `past`, the verb the first turned
    *they* governs (and one joined by *and*) in the past."""
    if clause is None or not clause.strip():
        return clause
    out, subject, last = [], None, 0
    for m in _THIRD.finditer(clause):
        word = m.group(1)
        lower = word.lower()
        pair = _TURNED.get(lower, ("you", "you"))
        turned = pair[0] if past else pair[1]
        if word[:1].isupper():
            turned = turned[:1].upper() + turned[1:]
        out.append(clause[last:m.start()] + turned)
        last = m.end()
        if lower == "they" and subject is None:
            subject = len("".join(out))
    out.append(clause[last:])
    text = "".join(out)
    if not past or subject is None:
        return text
    return _past_after(text, subject)


def lower_first(label) -> str:
    """`BeliefSentence.lower`: the first letter lowered unless the second is a capital (an acronym)."""
    if not label:
        return "" if label is None else label
    if len(label) > 1 and label[1].isupper():
        return label
    return label[0].lower() + label[1:]


# --------------------------------------------------------------------------- OccasionNoun, CostEstimate (mirrored)

#: `RecallWindow.Unit`'s words: never an occasion noun (keel-cloud 126 FR-2a).
WINDOW_UNIT_WORDS = frozenset(("night", "nights", "day", "days", "working day", "working days", "week", "weeks",
                               "month", "months"))
_PLURAL_PREPOSITIONS = ("on", "of", "in", "at", "for", "with", "to", "from")


def occasion_noun(noun):
    """`OccasionNoun.of`: the noun as a thing a frame can name -- `None` blank, the window's unit, or *time*."""
    if noun is None or not str(noun).strip():
        return None
    stored = str(noun).strip()
    if re.sub(r"\s+", " ", stored.lower()) in WINDOW_UNIT_WORDS:
        return None
    return None if stored.lower() in ("time", "times") else stored


def plural(occasion: str) -> str:
    """`CostEstimate.plural`: the occasion's head noun made plural (*pole inspection patrols*)."""
    parts = java_split(occasion)
    head = len(parts) - 1
    for i in range(1, len(parts)):
        if parts[i].lower() in _PLURAL_PREPOSITIONS:
            head = i - 1
            break
    noun = parts[head]
    lower = noun.lower()
    if re.fullmatch(r".*(s|x|z|ch|sh)", lower):
        noun += "es"
    elif re.fullmatch(r".*[^aeiou]y", lower):
        noun = noun[:-1] + "ies"
    else:
        noun += "s"
    parts[head] = noun
    return " ".join(parts)


# ------------------------------------------------------------------------------------------- LossLine (mirrored)

DOES, DONE_BY, DONE, NONE = "DOES", "DONE_BY", "DONE", "NONE"
RELATIVE = frozenset(("that", "which", "who"))
PREPOSITIONS = frozenset(("on", "from", "in", "of", "at", "for", "with", "to", "by", "over", "under", "during", "after",
                          "into", "across", "through", "between", "about", "within", "without", "per"))
SUBJECTS = frozenset(("they", "you", "we", "people", "i", "it", "he", "she"))
DETERMINERS = frozenset(("the", "a", "an", "their", "your", "our", "its", "his", "her"))
JOINERS = frozenset(("and", "or", "but", "plus"))
SUBORDINATORS = frozenset(("when", "because", "before", "after", "until", "if", "while", "since", "than", "as", "that",
                           "which", "who", "where", "once", "unless"))
AUXILIARIES = frozenset(("are", "is", "was", "were", "have", "has", "had", "do", "does", "did", "can", "could", "will",
                         "would", "should", "may", "might", "must"))
MORE_VERBS = frozenset(("fail", "notice", "show", "reserve", "solve", "merge", "catch", "ring", "happen", "bounce",
                        "drop", "expire", "lapse", "stay", "ship", "default", "churn", "cancel", "quit", "return",
                        "slip", "sit", "wait", "reach", "spoil", "rot", "die", "turn", "break"))
PARTICIPLES = frozenset(("lost", "paid", "spent", "taken", "given", "done", "made", "held", "kept", "left", "sent",
                         "sold", "built", "brought", "bought", "found", "told", "put", "run", "seen", "known",
                         "written", "caught", "forgotten", "thrown", "broken", "stolen", "won", "shown", "gone", "cut",
                         "hit", "set"))
_NOT_PARTICIPLES = frozenset(("hundred", "speed", "breed", "proceed", "exceed", "succeed", "indeed", "need", "feed",
                              "seed", "bed", "shed", "red", "bread"))
_FREE_RELATIVES = frozenset(("what", "how", "why", "where", "when", "whatever", "which", "whichever", "whoever"))
_MODALS = frozenset(("can", "could", "will", "would", "should", "may", "might", "must"))


@dataclass(frozen=True)
class Read:
    """`LossLine.Read`: the shape, the thing (first letter lowered), who does it on DONE_BY, the clause from the verb on
    (or on NONE what follows the thing, possibly empty)."""
    shape: str
    thing: str
    subject: str | None
    clause: str

    def rest_is_a_place(self) -> bool:
        first = "" if not self.clause.strip() else clean(self.clause.strip().split()[0])
        return first in PREPOSITIONS


def clean(word: str) -> str:
    return re.sub(r"[,;:.!?]+$", "", word.lower())


def _join(w: list[str], start: int, end: int) -> str:
    return " ".join(w[start:max(start, end)]).strip()


def _trim_comma(text: str) -> str:
    t = text.strip()
    return t[:-1].strip() if t.endswith(",") else t


def _trim_stop(text: str) -> str:
    t = text.strip()
    while t.endswith("."):
        t = t[:-1].strip()
    return t


def base(x: str) -> str:
    """`LossLine.base`: the third person's base (*reads* read, *catches* catch, *tries* try)."""
    if x.endswith("ies") and len(x) > 4:
        return x[:-3] + "y"
    if x.endswith(("ches", "shes", "sses", "xes")):
        return x[:-2]
    if x.endswith("s") and not x.endswith("ss") and len(x) > 2:
        return x[:-1]
    if x in ("is", "are"):
        return "be"
    return x


def _known(x: str) -> bool:
    return present_verb(x) or x in MORE_VERBS


def verb_like(x) -> bool:
    """`LossLine.verbLike`: a present verb, as typed or in the third person, or an auxiliary."""
    if not x or not x.strip():
        return False
    if x in AUXILIARIES and x not in ("can", "will", "may", "must"):
        return True
    if _known(x):
        return True
    b = base(x)
    return b != x and _known(b)


def participle(x: str) -> bool:
    return x in PARTICIPLES or (len(x) > 4 and x.endswith("ed") and x not in _NOT_PARTICIPLES)


def is_plural(noun: str) -> bool:
    """`LossLine.plural`: as the line types it (*runs*, *crimes*; never *loss*)."""
    return noun.endswith("s") and not noun.endswith("ss") and not noun.endswith("us") and len(noun) > 2


def first_verb(w: list[str], start: int, most: int) -> int:
    """`LossLine.firstVerb`: the first verb from `start` within `most`, never one straight after a determiner."""
    for j in range(start, min(len(w), start + most)):
        x = clean(w[j])
        if j > 0 and clean(w[j - 1]) in DETERMINERS:
            continue
        if verb_like(x) or x in AUXILIARIES or x == "never":
            return j
    return -1


def _agrees_with_the_thing(w: list[str], prep: int, relative: int) -> bool:
    """`LossLine.agreesWithTheThing`: a relative clause after the thing's place says what the thing does."""
    if relative + 1 >= len(w):
        return False
    head, before, verb = clean(w[prep - 1]), clean(w[relative - 1]), clean(w[relative + 1])
    plural_verb = verb in ("are", "were", "have", "do") or (verb_like(verb) and not verb.endswith("s")
                                                             and verb not in AUXILIARIES)
    singular_verb = verb in ("is", "was", "has", "does") or (verb.endswith("s") and verb_like(verb))
    return (is_plural(head) and not is_plural(before) and plural_verb) or (
        not is_plural(head) and is_plural(before) and singular_verb)


def read(loss_phrase) -> Read | None:
    """`LossLine.read`: the founder's loss line read, or `None` where none was typed or it names no thing."""
    if loss_phrase is None or not str(loss_phrase).strip():
        return None
    text = lower_first(_trim_stop(str(loss_phrase).strip()))
    w = java_split(text)
    if clean(w[0]) in _FREE_RELATIVES:
        return None
    if len(w) < 2:
        return Read(NONE, text, None, "")
    prep = -1
    for i in range(1, len(w)):
        x = clean(w[i])
        if prep < 0 and w[i - 1].endswith(","):
            return Read(NONE, _trim_comma(_join(w, 0, i)), None, _join(w, i, len(w)))
        if x in RELATIVE and i + 1 < len(w):
            if prep >= 0 and not _agrees_with_the_thing(w, prep, i):
                break
            thing = _join(w, 0, i)
            if verb_like(clean(w[i + 1])) or clean(w[i + 1]) in ("never", "not"):
                return Read(DOES, thing, None, _join(w, i + 1, len(w)))
            v = first_verb(w, i + 1, 4)
            if v < 0:
                break
            return Read(DONE_BY, thing, _join(w, i + 1, v), _join(w, v, len(w)))
        if prep >= 0:
            continue
        if x in PREPOSITIONS:
            prep = i
            continue
        if x in SUBJECTS or (x in DETERMINERS and clean(w[i - 1]) not in JOINERS):
            v = first_verb(w, i + 1, 4)
            if v > i:
                return Read(DONE_BY, _join(w, 0, i), _join(w, i, v), _join(w, v, len(w)))
            break
        if (x in ("never", "not") and i + 1 < len(w) and participle(clean(w[i + 1]))) or participle(x):
            return Read(DONE, _join(w, 0, i), None, _join(w, i, len(w)))
    if prep < 0:
        return Read(NONE, text, None, "")
    end = prep
    if clean(w[prep]) == "of":
        end = prep + 1
        while end < len(w) and not w[end - 1].endswith(",") and clean(w[end]) not in PREPOSITIONS \
                and clean(w[end]) not in RELATIVE and clean(w[end]) not in SUBJECTS:
            end += 1
    return Read(NONE, _trim_comma(_join(w, 0, end)), None, _join(w, end, len(w)))


def _keep_punctuation(original: str, turned: str) -> str:
    tail = re.search(r"[,;:.!?]*$", original).group()
    word = turned[:1].upper() + turned[1:] if original[:1].isupper() else turned
    return word + tail


def _turn_run(w: list[str], out: list[str], at: int, did: bool) -> None:
    """`LossLine.turnRun`: the verb at `at` (after any *never* / *not*), and each verb joined to it."""
    while at < len(w):
        x = clean(w[at])
        if x in ("never", "not", "still", "also"):
            at += 1
            continue
        if not verb_like(x) and not participle(x):
            return
        if not participle(x) and x not in _MODALS:
            out[at] = _keep_punctuation(w[at], base(x) if did else (past_of(x) or x))
        nxt = at + 1
        while nxt < len(w) and clean(w[nxt]) not in JOINERS and clean(w[nxt]) not in SUBORDINATORS:
            nxt += 1
        if nxt < len(w) and clean(w[nxt]) in JOINERS and nxt - at <= 6 and nxt + 1 < len(w) \
                and (verb_like(clean(w[nxt + 1])) or participle(clean(w[nxt + 1]))
                     or clean(w[nxt + 1]) in ("never", "not")):
            at = nxt + 1
            continue
        return


def _turn(clause, did: bool):
    if clause is None or not clause.strip():
        return clause
    w = clause.strip().split()
    out = list(w)
    if not any(clean(word) == "now" for word in w):
        _turn_run(w, out, 0, did)
    for i in range(1, len(w)):
        if clean(w[i]) not in SUBORDINATORS:
            continue
        segment_end = i + 1
        while segment_end < len(w) and clean(w[segment_end]) not in SUBORDINATORS:
            segment_end += 1
        segment_now = any(clean(w[j]) == "now" for j in range(i + 1, segment_end))
        v = first_verb(w, i + 1, 4)
        if v == i + 1 and v + 1 < segment_end and (clean(w[v + 1]) in AUXILIARIES or (
                verb_like(clean(w[v + 1])) and clean(w[v + 1]) not in JOINERS)):
            v += 1
        if i < v < segment_end and not segment_now and clean(w[v - 1]) != "to":
            _turn_run(w, out, v, False)
    return " ".join(out)


def past(clause):
    """`LossLine.past`: the clause's verb in the window's past, and the first verb of each clause it opens."""
    return _turn(clause, False)


def after_did(clause):
    """`LossLine.afterDid`: the same after *did* -- the clause's own verb in the base form."""
    return _turn(clause, True)


def without_its_clause(clause: str):
    """`LossLine.withoutItsClause`: the line cut before the first clause it opens, else `None`."""
    w = clause.strip().split()
    for i in range(1, len(w)):
        if clean(w[i]) in SUBORDINATORS and clean(w[i]) not in RELATIVE:
            return _trim_comma(_join(w, 0, i))
    return None
