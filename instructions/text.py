"""Words, normalised and stemmed, in one place (spec 029, research R15).

**What moved here, and what did not survive** (`MARKS_VERSION` 9, judgement call 29). `normalise`
and `normalise_phrase` came from `instructions/align.py` unchanged, with the tests that held them
(`tests/test_instruction_align.py` → `tests/test_instruction_text.py`). Everything else `align.py`
held retired with the subject it aligned: `resolve_reads` (call 27), the eight `FIELDS`, the
structural matcher and the judge's three old questions -- a calibration answer is a typed pick
against the registry now, and there is no structure left to align. `tests/test_instruction_reads.py`
retired with `resolve_reads`; `tests/test_instruction_questions.py` retired with the `QUESTIONS`
screen, whose place in the case order `tests/test_instruction_prompts.py` now pins.

**The stemmer is deliberately small.** Five suffix rules -- `-ification`, `-ing`, `-ed`, `-ion`,
then `-es`/`-s` -- one rule a word, first match wins, and never below a three-letter stem. It exists
for one job: `no_leak` (call 32) asks whether a word from the golden mechanism appears in a
question, and *listens*, *listened* and *listening* must be one word for that question to mean
anything. A cleverer stemmer would be a ruler that moved for reasons nobody wrote down; a wrong
stem is a `runs/DRIFT.md` finding about the ruler, fixed with a bump.
"""

from __future__ import annotations

import re


def normalise(text) -> str:
    """Case- and whitespace-normalised, for every string comparison the scorers make."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def normalise_phrase(text) -> str:
    """A founder's phrase, with the corpus author's own annotations taken off first.

    A trailing parenthetical written for a human reviewer rather than by the founder -- *"£40 a
    month per site (proxied by comparable spend)"* -- is stripped **on the golden side, at
    comparison time**, so the two sides are compared as the same kind of thing. Only a trailing
    parenthetical is removed, and only when something is left in front of it.
    """
    stripped = re.sub(r"\s*\([^()]*\)\s*$", "", str(text or "")).strip()
    return normalise(stripped or text)


#: Words no question can leak a mechanism through, because every question uses them: articles,
#: pronouns, prepositions, auxiliaries, quantities and clock words. Stemmed membership is checked
#: on the raw lower-cased word, before stemming, so the list reads as English.
STOPLIST = frozenset("""
a about above after again all also am an and any are around as at
be been before being both but by
can could did do does doing done down during
each either else even ever every
few for from
get gets got
had has have having he her here hers him his how
i if in into is it its itself
just
least less like lot lots
many may me might more most much must my
near never next no nor not now
of off often on once one only or other our out over own
per
quite
rather really right
same say says said see seen she should since so some something soon still such
than that the their theirs them then there these they thing things this those though through to too
under until up upon us usually
very
was way we well were what when where whether which while who whom whose why will with within
without would
yes yet you your yours
zero two three four five six seven eight nine ten eleven twelve twenty hundred
first second third last
second seconds minute minutes hour hours day days week weeks month months year years night nights
time times
""".split())

_WORD_RE = re.compile(r"[a-z]+")


def words(text) -> list[str]:
    """Every alphabetic run in `text`, lower-cased, in order. Hyphens and apostrophes split."""
    return _WORD_RE.findall(str(text or "").lower())


def content_words(text) -> list[str]:
    """`words(text)` less the `STOPLIST`, in order."""
    return [w for w in words(text) if w not in STOPLIST]


def stem(word: str) -> str:
    """One word's stem by the five rules above; a word the rules would cut below three letters is
    left whole (*need*, *feed*, *fed* stay themselves). Two spelling folds follow, so a base and
    its inflection meet: a final *-e* goes (*settle*/*settled* → *settl*) and a consonant's final
    *-y* becomes *-i* (*nappy*/*nappies* → *nappi*)."""
    return _fold(_strip_suffix(word.lower()))


def _strip_suffix(word: str) -> str:
    for suffix, keep in (("ification", "if"), ("ing", ""), ("ed", ""), ("ion", "")):
        if word.endswith(suffix):
            candidate = word[: -len(suffix)] + keep
            return candidate if len(candidate) >= 3 else word
    if word.endswith("es") and len(word) > 4 and word[-3] in "sxz":
        return word[:-2]
    if word.endswith(("ches", "shes")) and len(word) > 5:
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _fold(word: str) -> str:
    if word.endswith("e") and len(word) > 3:
        word = word[:-1]
    if word.endswith("y") and len(word) >= 3 and word[-2] not in "aeiou":
        word = word[:-1] + "i"
    return word


def stems(text) -> set[str]:
    """The stems of `text`'s content words, as a set."""
    return {stem(w) for w in content_words(text)}


def stem_sequence(text) -> list[str]:
    """The stems of **every** word of `text`, stoplisted or not, in order -- for matching a
    multi-word term (*most likely*) as a phrase rather than as two loose words."""
    return [stem(w) for w in words(text)]


def phrase_in(phrase_stems: tuple[str, ...], text) -> bool:
    """Whether the stemmed phrase occurs, contiguous and in order, in `text`."""
    sequence = stem_sequence(text)
    n = len(phrase_stems)
    return n > 0 and any(tuple(sequence[i:i + n]) == tuple(phrase_stems)
                         for i in range(len(sequence) - n + 1))
