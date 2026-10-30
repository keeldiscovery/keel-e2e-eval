"""Spec 093 -- the harness mirrors keel-cloud 161 (and 163's frame): the bare phrase, the follow-up rung, L1 in 161's
words and L5 admitting `suggested` on Compatibility, the adoption-friction frame as the cloud's `ItemFrames`, K3 on the
framed line.

FR-1 the scripted Current solution phrase is bare (the corpus's *your way of ...* read as `ItemFrames.bare` reads it).
"""

from __future__ import annotations

import pytest

from harness import vectors_script as vs
from stack.config import load_config

GOLDEN = ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly", "06-repeatline", "07-mulchrun")
CUR = "problem.current_solution_satisfaction"


def _entry(name: str):
    return vs.entry_for(load_config(validate=False).keel_cloud, name)[1]


@pytest.mark.parametrize("stored, bare", [
    ("your way of working out what the baby needed", "working out what the baby needed"),
    ("  Your   Way  of checking for errors ", "checking for errors"),
    ("checking for errors", "checking for errors"),
    ("the way your team logs it", "the way your team logs it"),        # only the opening is Keel's
    (None, None),
])
def test_bare_is_the_clouds_helper(stored, bare):
    """keel-cloud 161 `ItemFrames.bare`: the opening *your way of* (any case, any spacing) and nothing else."""
    assert vs.bare_phrase(stored) == bare


@pytest.mark.parametrize("stored, said", [
    ("your way of finding the fix and logging it", "finding the fix"),            # 128's one act
    ("your way of catching and fixing that failure", "catching that failure"),
    ("your way of checking for errors.", "checking for errors"),
    ("", None),
])
def test_said_is_bare_then_one_act(stored, said):
    """keel-cloud 161 `ItemFrames.said`: bare, one act (128), no closing stop or question mark."""
    assert vs.said_phrase(stored) == said


@pytest.mark.parametrize("name", GOLDEN)
def test_every_scripted_draft_writes_the_phrase_bare(name):
    """FR-1: no scripted PROBLEM draft opens on *your way of* -- keel-cloud 161's `L1` never fires on the script; the
    saved list (what the founder saves from the draft) says the same bare words, and the corpus still records the
    stored *your way of ...* (never edited)."""
    entry = _entry(name)
    stored = entry.founder_list(CUR)["phrase"]
    assert stored.lower().startswith("your way of"), "the corpus is not edited"
    draft = vs.drafted_list(entry, CUR)
    assert draft["phrase"] == vs.bare_phrase(stored) and not draft["phrase"].lower().startswith("your way of")
    assert vs.saved_list(entry, CUR)["phrase"] == draft["phrase"]
    problem = next(q for q in vs.calibration_result(entry, "PROBLEM")["questions"] if q["key"] == CUR)
    assert problem["list"]["phrase"] == draft["phrase"]


# ------------------------------------------------------------------------------------------------- FR-2: the rung

from harness import interviewer_fake as fake                             # noqa: E402


def test_the_rung_is_161s_and_says_the_phrase():
    """keel-cloud 161 T003: *You said {phrase} works for you. What keeps it working?*, text and spoken; `{phrase}` the
    locked phrase as the question says it, *the way you do it* where there is none."""
    rung = fake.rung(CUR)
    assert rung[2] == rung[3] == "You said {phrase} works for you. What keeps it working?"
    assert fake.FILL_DEFAULTS["{phrase}"] == "the way you do it"
    assert fake.LADDER_SHA == "b009fac8"


def test_lullabys_rung_is_161s_worked_example():
    """161's table: a stored *your way of working out what the baby needed* and a bare one say the same rung."""
    entry = _entry("03-lullaby")
    values = vs.lock_values(entry, {"occasion": "night"}, CUR)
    assert values["{phrase}"] == "working out what the baby needed"
    assert vs.follow_up_clip(entry, {"occasion": "night"}, CUR) == \
        "You said working out what the baby needed works for you. What keeps it working?"


# ------------------------------------------------------------------------- FR-3: the harness's own rules say the cloud's

from instructions import marks as marks_mod                              # noqa: E402
from instructions import score as score_mod                              # noqa: E402
from tests import v9_fixtures as fx                                      # noqa: E402


def _list_faults(key, draft):
    return score_mod.list_faults({"key": key, "list": draft}, fx.registry().by_key(key))


def test_l1_is_161s():
    """keel-cloud 161 T002: a blank phrase in 161's words; a drafted *your way of* faults, naming the bare act."""
    good = fx.GOOD_LISTS[CUR]
    assert _list_faults(CUR, good) == []
    assert any("the act in the people's words ('checking for errors')" in f
               for f in _list_faults(CUR, {**good, "phrase": " "}))
    faults = _list_faults(CUR, {**good, "phrase": "Your way of finding them"})
    assert faults == ["L1: 'Your way of finding them' opens on 'your way of'; write the act alone, in the people's "
                      "words ('finding them')"]


def test_l5_admits_compatibility_never_elsewhere():
    """keel-cloud 121 FR-3 / 161 FR-3: one `suggested` on Purchase friction or Compatibility; never on Adoption."""
    assert score_mod.SUGGESTED_ON == ("commercial.purchase_friction", "solution.compatibility")
    compat = "solution.compatibility"
    one = {**fx.GOOD_LISTS[compat], "items": [{**fx.GOOD_LISTS[compat]["items"][0], "suggested": True}]
           + fx.GOOD_LISTS[compat]["items"][1:]}
    assert not [f for f in _list_faults(compat, one) if f.startswith("L5")]
    adoption = "solution.adoption_friction"
    tagged = {**fx.GOOD_LISTS[adoption], "items": [{**fx.GOOD_LISTS[adoption]["items"][0], "suggested": True}]
              + fx.GOOD_LISTS[adoption]["items"][1:]}
    assert [f for f in _list_faults(adoption, tagged) if f.startswith("L5")]


def test_the_marks_version_moved_with_its_note():
    """FR-3: the reading of `option_validity` moved both ways, so MARKS_VERSION moved (calls 124-125)."""
    assert marks_mod.MARKS_VERSION == 22 and "124. **v22**" in marks_mod.__doc__ and "125. **v22**" in marks_mod.__doc__
