"""`instructions/text.py`: words, normalised and stemmed, in one place (spec 029 T007, research R15).

The `normalise` tests are `tests/test_instruction_align.py`'s, carried over unchanged when
`align.py` retired (judgement call 29) -- `normalise` is the one piece of it that survived, and the
tests that held it came with it. The stemmer's tests are the five rules a person can check by hand.
"""

from __future__ import annotations

import pytest

from instructions import text as text_mod


def test_normalise_folds_case_and_whitespace_and_reads_none_as_empty():
    assert text_mod.normalise("  Lost   Sleep\n") == "lost sleep"
    assert text_mod.normalise(None) == ""


def test_a_corpus_annotation_is_stripped_before_a_phrase_is_compared():
    """MARKS_VERSION 3, judgement call 15 (moved from test_instruction_align.py unchanged)."""
    assert text_mod.normalise_phrase(
        "scans each delivery on arrival (the present-tense half, per §8.1 step 3)") \
        == "scans each delivery on arrival"
    assert text_mod.normalise_phrase("£40 a month per site (proxied by comparable spend)") \
        == "£40 a month per site"
    # Nothing else is touched: no parenthetical, or one that is the whole phrase.
    assert text_mod.normalise_phrase("about a week") == "about a week"
    assert text_mod.normalise_phrase("(most weeks)") == "(most weeks)"


@pytest.mark.parametrize("word, stem", [
    ("listens", "listen"), ("listened", "listen"), ("listening", "listen"), ("listen", "listen"),
    ("classification", "classif"), ("cards", "card"), ("card", "card"),
    ("suggestion", "suggest"), ("suggests", "suggest"),
    ("settle", "settl"), ("settled", "settl"), ("settles", "settl"),
    ("nappy", "nappi"), ("nappies", "nappi"), ("boxes", "box"),
    ("need", "need"), ("feed", "feed"), ("fed", "fed"), ("glass", "glass"),
])
def test_the_five_rules_and_the_two_folds(word, stem):
    assert text_mod.stem(word) == stem


@pytest.mark.parametrize("word", ["the", "a", "when", "it", "them", "most", "ten", "seconds", "you"])
def test_the_stoplist_drops_words_every_question_uses(word):
    assert word in text_mod.STOPLIST
    assert text_mod.content_words(f"{word} card") == ["card"]


def test_stems_is_a_set_of_content_word_stems():
    assert text_mod.stems("When it listens to the cards") == {"listen", "card"}


def test_a_multi_word_term_matches_only_as_a_phrase_in_order():
    phrase = tuple(text_mod.stem_sequence("most likely"))
    assert text_mod.phrase_in(phrase, "what the baby most likely needs")
    assert not text_mod.phrase_in(phrase, "most nights it is likely")
