"""Spec 128 -- the confirmed context is read as spelt: the typed fields held to the served ones word by word through
125's mirror of keel-cloud's `Spelling.sameWord`, and the typos the cloud corrected recorded as `respelled`."""
from __future__ import annotations

import inspect

import pytest

from evals import corpus_scenario as cs
from harness import typist as tp

#: Cycle 8's 08-fresco walk (`runs/20261102T050840Z-backtest-08-fresco`, transcript seq 21): the four fields as the
#: founder typed them, and `GET context`'s `fields` as keel-cloud 196 served them, respelled.
TYPED = {"actor": "construction superintendent",
         "job": "keep an accurate rcord of the day's work on site",
         "circumstance": "the day's site walks are done and the photoss and notes still have to go into the dailyy log",
         "segment": "superintendents at US generall contractors whose jobs run on Procore or ACC"}
SERVED = {"actor": "construction superintendent",
          "job": "keep an accurate record of the day's work on site",
          "circumstance": "the day's site walks are done and the photos and notes still have to go into the daily log",
          "segment": "superintendents at US general contractors whose jobs run on Procore or ACC",
          "recallWindow": {"count": 5, "unit": "WORKING_DAYS"}, "occasion": "daily log"}


# ------------------------------------------------------------------------------------------------ FR-1 held as spelt

def test_a_served_field_with_one_corrected_typo_passes():
    assert tp.as_spelt(TYPED["job"], SERVED["job"])
    assert tp.spelt_faults({"job": TYPED["job"]}, {"job": SERVED["job"]}) == []


def test_cycle_8s_fresco_fields_are_read_as_spelt():
    assert tp.spelt_faults(TYPED, SERVED) == []
    # the letter-for-letter compare it replaces stopped the walk on the first field the cloud respelled
    assert [k for k, v in TYPED.items() if SERVED.get(k) != v] == ["job", "circumstance", "segment"]


@pytest.mark.parametrize("served", [
    "keep an accurate report of the day's work on site",       # a different word where the typo stood
    "keep a precise record of the day's work on site",          # a word swapped for another
    "keep an accurate record of the day's work on the site",    # a word added
])
def test_a_different_or_added_word_fails(served):
    assert not tp.as_spelt(TYPED["job"], served)
    assert tp.spelt_faults({"job": TYPED["job"]}, {"job": served}) == [
        {"field": "job", "typed": TYPED["job"], "served": served}]


def test_a_swapped_word_fails():
    assert not tp.as_spelt("keep an accurate rcord of the work", "keep an accurate record of the job")


def test_a_dropped_word_fails():
    assert not tp.as_spelt(TYPED["job"], "keep an accurate record of the day's work")
    assert not tp.as_spelt(TYPED["job"], "keep accurate record of the day's work on site")


def test_with_no_typos_the_exact_text_passes():
    assert tp.as_spelt(SERVED["job"], SERVED["job"])
    assert tp.spelt_faults(SERVED, SERVED) == []
    assert tp.respelled(SERVED, SERVED) == []


@pytest.mark.parametrize("typed, served", [
    ("run on Procore", "run on Procure"),           # within the allowance (the typist never types a name wrong)
    ("at 6 every evening", "at 7 every evening"),   # a number is never corrected
    ("for the dog", "for the dot"),                 # under four letters, only the same word
    ("the photos", "the fotos"),                    # the first letter the same
])
def test_the_allowance_is_125s_mirror(typed, served):
    from instructions import spelling
    words = list(zip(typed.split(), served.split()))
    assert tp.as_spelt(typed, served) == all(a == b or spelling.same_word(a, b) for a, b in words)


def test_the_punctuation_between_the_words_is_held():
    assert not tp.as_spelt("the photos, and notes", "the photos and notes")
    assert tp.as_spelt("the photoss,  and notes ", "the photos, and notes")


def test_a_value_that_is_not_text_is_held_exactly():
    assert tp.as_spelt({"count": 5}, {"count": 5}) and not tp.as_spelt({"count": 5}, {"count": 6})
    assert not tp.as_spelt("record", None)
    assert tp.spelt_faults({"job": "x y"}, {}) == [{"field": "job", "typed": "x y", "served": None}]


def test_whole_holds_the_key_sets_as_the_dict_compare_did():
    four = {k: SERVED[k] for k in TYPED}
    assert tp.spelt_faults(TYPED, four, whole=True) == []
    assert tp.spelt_faults(TYPED, {**four, "occasion": "daily log"}, whole=True) == [
        {"field": "occasion", "typed": None, "served": "daily log"}]
    assert tp.spelt_faults(TYPED, SERVED) == []                # the confirmed view carries more; only typed are held


# ------------------------------------------------------------------------------------------------ FR-2 recorded

def test_respelled_carries_the_corrected_pairs():
    assert tp.respelled(TYPED, SERVED) == [
        {"field": "job", "typed": "rcord", "served": "record"},
        {"field": "circumstance", "typed": "photoss", "served": "photos"},
        {"field": "circumstance", "typed": "dailyy", "served": "daily"},
        {"field": "segment", "typed": "generall", "served": "general"}]


def test_a_field_that_does_not_line_up_is_given_whole():
    served = "keep an accurate record of the day's work"
    assert tp.respelled({"job": TYPED["job"]}, {"job": served}) == [
        {"field": "job", "typed": TYPED["job"], "served": served}]


def test_a_typed_word_served_letter_for_letter_is_still_a_leak():
    """126 FR-3 unchanged: `leaks` reads the typed form, not 128's allowance."""
    bundle = {"founder_screens": [{"screen": "context-card", "understands": "they want to keep an accurate rcord"}]}
    typed = [{"field": "job", "meant": "record", "typed": "rcord", "kind": "dropped"}]
    assert [x["typed"] for x in tp.leaks(bundle, typed)] == ["rcord"]
    assert tp.leaks({"founder_screens": [{"screen": "context-card", "understands": "an accurate record"}]}, typed) == []


# ------------------------------------------------------------------------------------------------ the two steps

def test_the_confirmed_step_holds_the_fields_as_spelt_and_records_respelled():
    source = inspect.getsource(cs.leg_context)
    assert "assert fields.get(key) == value" not in source
    assert "typist.spelt_faults(founder.context_fields, fields)" in source
    assert '{**view, "respelled": respelled}' in source
    assert "typist.as_spelt(drawn_occasion, fields.get(\"occasion\"))" in source


def test_the_reopened_step_holds_the_refilled_form_as_spelt():
    source = inspect.getsource(cs.context_reopened)
    assert 'edited.get("fields") == founder.context_fields' not in source
    assert 'typist.spelt_faults(founder.context_fields, edited.get("fields") or {}, whole=True)' in source
