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
