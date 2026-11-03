"""The hidden short name (spec 129, keel-cloud 200 -- the follow-up refers back in the people's words).

keel-cloud 200 gives the Check rows a follow-up refers back to (`ShortName.ROWS`: Importance, Compatibility, Adoption
friction, Commitment's step and smaller step) a hidden **short name** -- two to five words in the persona's own words,
written by the founder-lists call beside the row (and by the `asked` job for a row the founder rewords or adds), never
shown to the founder -- and Current solution's phrase and Relative advantage's job a list-level one (`ShortName.LISTS`).
The follow-up says it in the row's place (`follow_up.named` in the registry); where a row has none it reads today's
wording (a project confirmed before 200, a row the job could not name).

Two things live here:

- `fault` -- `ShortName.fault` restated (`L29` on the draft, `K9` on the `asked` job): 2-5 words, no pronoun, no
  product word the founder did not type, no claim word, not the idea's name, not the row repeated, and every word but
  a word of grammar the row's, the founder's or the persona's (a plain stem and `Spelling.sameWord` read as one word).
- `compose` -- **the scripted writer's** short name (the harness's fake founder-lists and asked writers): the row cut
  down, never a new word -- a leading article off, its trailing phrases cut (the rightmost first) to five words or
  fewer, and a row that would only repeat itself cut once more; `None` where no cut names it, and then the row reads
  today's wording. Every name it gives passes `fault` against the row alone, so a scripted draft is never refused.
"""

from __future__ import annotations

import re

from instructions import spelling

#: `ShortName.MIN_WORDS` / `MAX_WORDS`.
MIN_WORDS = 2
MAX_WORDS = 5
#: Screen response contract 25 (keel-cloud 200, `SHORT_NAME_MAX`): the schema's cap in characters.
MAX_CHARS = 60
#: `ShortName.ROWS` / `ShortName.LISTS`.
ROWS = ("problem.importance", "solution.compatibility", "solution.adoption_friction", "commercial.commitment")
LISTS = ("problem.current_solution_satisfaction", "solution.relative_advantage")
#: `ShortName.PRONOUNS`.
PRONOUNS = ("it", "its", "this", "that", "these", "those", "they", "them", "he", "she", "him", "her")
#: `ShortName.GRAMMAR`.
GRAMMAR = frozenset(("a", "an", "the", "your", "you", "my", "our", "of", "on", "in", "at", "to", "for", "from", "with",
                     "without", "by", "into", "onto", "out", "up", "off", "over", "under", "and", "or", "not", "no",
                     "own", "after", "before", "per", "each", "every", "all", "more", "less"))
#: keel-cloud `Vocabulary.PRODUCT_WORDS` and `CLAIM_WORDS`.
PRODUCT_WORDS = ("app", "apps", "platform", "dashboard", "portal", "plugin", "api", "saas", "website", "algorithm",
                 "device", "automate", "automates", "automated", "automating", "automation", "integrate",
                 "integrates", "integrated", "integration", "integrations", "sync", "syncs", "synced", "syncing")
CLAIM_WORDS = ("works", "accurate", "accurately", "saves", "faster", "better", "reliable", "reliably", "trusted",
               "improves", "helps")

_WORD = re.compile(r"[^\W_]+(?:['’][^\W\d_]+)?")

#: The words the scripted writer cuts a trailing phrase at: keel-cloud 202's `TRAILING` (a preposition, a relative,
#: *due*) and a few more prepositions a row runs on with.
_CUT = frozenset(("with", "on", "at", "for", "in", "from", "after", "before", "by", "during", "over", "across",
                  "within", "who", "that", "which", "where", "when", "due", "under", "against", "as", "between",
                  "through", "about", "into", "without", "while", "so"))
#: A particle a row of five words or fewer may end on, dropped where nothing else cuts it (*breaking down*).
_TAIL = frozenset(("down", "up", "out", "off", "away", "again", "late", "early", "together"))
#: A finite verb: a row that is a clause (*Their phone was within reach of the cot*) is no noun or -ing phrase, and the
#: contract's rule asks one (*read after 'instead of'*) -- the scripted writer names none there.
_FINITE = frozenset(("could", "can", "would", "will", "was", "were", "is", "are", "had", "has", "have", "did", "does",
                     "do", "should", "must", "may", "might", "came", "knew", "allowed", "accepted"))


def words(text: str | None) -> list[str]:
    """`ShortName.words`: the words of `text`, lower-cased, a possessive's *'s* off."""
    return [re.sub(r"['’]s$", "", w) for w in _WORD.findall(str(text or "").lower())]


def folded(text: str | None) -> str:
    """`ShortName.folded`: case-folded, punctuation and space one space."""
    return " ".join(words(text))


def stem(word: str) -> str:
    """`ShortName.stem`: a plural's s, an -ing or an -ed off, a doubled last consonant once, a closing e off."""
    w = word
    if len(w) > 5 and w.endswith("ing"):
        w = w[:-3]
    elif len(w) > 4 and w.endswith("ied"):
        w = w[:-3] + "y"
    elif len(w) > 4 and w.endswith("ed"):
        w = w[:-2]
    elif len(w) > 4 and w.endswith("ies"):
        w = w[:-3] + "y"
    elif len(w) > 3 and w.endswith("es") and not w.endswith("ses"):
        w = w[:-1]
    elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    if len(w) > 3 and w[-1] == w[-2] and w[-1] in "bdfgklmnprtz":
        w = w[:-1]
    if len(w) > 3 and w.endswith("e"):
        w = w[:-1]
    return w


def same(word: str, given: str) -> bool:
    """`ShortName.same`: the same word, the same stem, or the same word misspelt (`Spelling.sameWord`)."""
    return word == given or stem(word) == stem(given) or spelling.same_word(word, given)


def _whole(word: str, text: str) -> bool:
    return re.search(r"\b" + re.escape(word) + r"\b", text) is not None


def fault(rule: str, name: str | None, row: str | None, vocabulary: str = "", idea_names=()) -> str | None:
    """`ShortName.fault`: the first fault of `name` as the short name of `row` under `rule` (`L29`, `K9`), or None."""
    said = str(name or "").strip()
    count = len(said.split())
    if count < MIN_WORDS or count > MAX_WORDS:
        return (f"{rule}: '{said}' is {count} words; a short name is {MIN_WORDS} to {MAX_WORDS} words in the people's "
                "own words")
    own = words(said)
    for word in own:
        if word in PRONOUNS:
            return f"{rule}: '{said}' says '{word}'; a short name names the thing itself, never a pronoun"
    typed = str(vocabulary or "").lower()
    for word in own:
        if word in PRODUCT_WORDS and not _whole(word, typed) and not spelling.in_text(word, typed):
            return f"{rule}: '{said}' says '{word}', a product word; name the row in the people's words"
    for word in own:
        if word in CLAIM_WORDS:
            return f"{rule}: '{said}' says '{word}', a claim word; name the row, never what it does for them"
    for idea in idea_names or ():
        if idea and idea.strip() and re.search(r"(?i)(?<![^\W_])" + re.escape(idea.strip()) + r"(?![^\W_])", said):
            return (f"{rule}: '{said}' says the idea's name, '{idea.strip()}'; a short name names the row in the "
                    "people's words")
    if folded(said) == folded(row):
        return (f"{rule}: '{said}' is the row repeated; a short name is the row as the people would say it in two to "
                "five words")
    pool = words(f"{row or ''} {vocabulary or ''}")
    for word in own:
        if word in GRAMMAR or word.isdigit():
            continue
        if not any(same(word, given) for given in pool):
            return (f"{rule}: '{said}' says '{word}', which neither the row, the founder nor the people's own words "
                    "say; name the row in words they gave")
    return None


def _lower(text: str) -> str:
    return text if len(text) > 1 and text[1].isupper() else text[:1].lower() + text[1:]


def _cut(tokens: list[str]) -> list[str] | None:
    at = next((i for i in range(len(tokens) - 1, 1, -1) if tokens[i].lower().strip(",;:") in _CUT), -1)
    return tokens[:at] if at >= 0 else None


def compose(row: str | None, idea_names=(), *, gerund=None) -> str | None:
    """The scripted writer's short name for `row`: the row cut down to two to five of its own words, said mid-sentence
    (*Matching deliveries against their invoices* -> *matching deliveries*), or None where no cut names it or the row
    is a clause. `gerund` (Adoption friction's efforts, Commitment's steps: imperatives) turns the name's first verb to
    its -ing form (*Scan each delivery on arrival* -> *scanning each delivery*)."""
    if any(w in _FINITE for w in words(row)):
        return None
    tokens = str(row or "").strip().rstrip(".").split()
    if tokens and tokens[0].lower() in ("the", "a", "an"):
        tokens = tokens[1:]
    if tokens and gerund is not None and not tokens[0].lower().endswith("ing"):
        tokens = gerund(" ".join(tokens)).split()
    while len(tokens) > MAX_WORDS:
        tokens = _cut(tokens)                       # never a row's first five words cut mid-phrase: a phrase or none
        if tokens is None:
            return None
    if folded(" ".join(tokens)) == folded(row):
        cut = _cut(tokens)
        if cut is None and tokens and tokens[-1].lower() in _TAIL:
            cut = tokens[:-1]
        if cut is None:
            return None
        tokens = cut
    while tokens and (tokens[-1].lower().strip(",;:") in GRAMMAR or tokens[-1].lower().strip(",;:") in _CUT
                      or re.search(r"['\u2019]s$", tokens[-1])):
        tokens = tokens[:-1]
    name = re.sub(r"[,;:]+$", "", " ".join(tokens)).strip()
    if not name or len(name) > MAX_CHARS:
        return None
    name = _lower(name)
    return None if fault("L29", name, row, "", idea_names) else name
