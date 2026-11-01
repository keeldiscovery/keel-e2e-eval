"""Spelling corrected, words kept (spec 125 FR-1; keel-cloud 195 FR-2, keel-cloud-docs `2d848360`).

A port of keel-cloud's `domain/vectors/Spelling.java`, word for word: since 195 the instructions let the model write a
misspelt word of the founder's in its dictionary spelling (*withot* -> *without*, *erros* -> *errors*), so a check that
holds a word of the model's to the founder's typed text reads the two as one word through `same_word`.

**The rule.** Case-folded, two words match when they are equal, or when both are at least four letters long, no token
carries a digit, **the first letter is the same** (195's first-letter guard: *apps* / *maps*, *device* / *advice*,
*night* / *light*, *four* / *your* stay two words), and they are within the optimal-string-alignment distance
(Levenshtein with an adjacent swap as one edit, so *recieve* is one from *receive*) the shorter allows: one edit at four
letters, two from five. Under four letters, or with a digit in either, only the same word matches -- a number is never
corrected. Names are not words of the dictionary: nothing that holds a name reads through this.

`no_leak`'s vocabulary (`corpus.Entry.vocabulary`, call 44a) is its caller beside `chain._same_words`
(`CommercialChain.sameWords`, which 195 routed through it too). No mark number moves.
"""

from __future__ import annotations

import re

#: `Spelling.words`: runs of letters, digits, apostrophes and hyphens (`[^\p{L}\p{N}'-]+` splits; `_` is no letter).
_SPLIT = re.compile(r"[^\w'\-]+|_+")
_EDGE = re.compile(r"^['\-]+|['\-]+$")


def allowed(length: int) -> int:
    """`Spelling.allowed`: the edits a word of `length` letters may differ by -- none under four, one at four, two from
    five."""
    return 0 if length < 4 else 1 if length == 4 else 2


def distance(a: str, b: str) -> int:
    """`Spelling.distance`: the optimal string alignment distance -- insertions, deletions, substitutions and adjacent
    swaps, one edit each."""
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[len(a)][len(b)]


def _has_digit(word: str) -> bool:
    return any(c.isdigit() for c in word)


def same_word(a, b) -> bool:
    """`Spelling.sameWord`: whether `a` and `b` are one word, its spelling aside."""
    if a is None or b is None:
        return False
    x, y = str(a).strip().lower(), str(b).strip().lower()
    if not x or not y:
        return False
    if x == y:
        return True
    if _has_digit(x) or _has_digit(y):
        return False
    most = allowed(min(len(x), len(y)))
    return most > 0 and x[0] == y[0] and abs(len(x) - len(y)) <= most and distance(x, y) <= most


def words(text) -> list[str]:
    """`Spelling.words`: the words of `text` -- runs of letters, digits, apostrophes and hyphens, case-folded, an
    apostrophe or hyphen at either edge taken off."""
    if text is None:
        return []
    out = []
    for raw in _SPLIT.split(str(text).lower().replace("’", "'")):
        word = _EDGE.sub("", raw)
        if word:
            out.append(word)
    return out


def in_text(word, text) -> bool:
    """`Spelling.inText`: whether some word of `text` is `same_word` `word`."""
    if word is None or not str(word).strip() or text is None:
        return False
    return any(same_word(word, own) for own in words(text))


def run_in(phrase, text) -> bool:
    """`Spelling.runIn`: whether the words of `phrase` stand in `text` one after another, each `same_word` its own
    (*evry evening* in *at about 6 every evening*); an empty phrase never does."""
    said, typed = words(phrase), words(text)
    if not said or len(said) > len(typed):
        return False
    return any(all(same_word(said[j], typed[i + j]) for j in range(len(said)))
               for i in range(len(typed) - len(said) + 1))
