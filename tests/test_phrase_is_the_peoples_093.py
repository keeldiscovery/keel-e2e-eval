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
    """keel-cloud 121 FR-3: one `suggested` on Purchase friction or Compatibility. Spec 112 FR-4 (keel-cloud 171 FR-2):
    Adoption friction too -- one suggested step with its why (was *never on Adoption*, 161 FR-3); a missing why is an
    `L5` breach (`tests/test_adoption_steps_112.py` holds the rest)."""
    assert score_mod.SUGGESTED_ON == ("commercial.purchase_friction", "solution.compatibility",
                                      "solution.adoption_friction")
    compat = "solution.compatibility"
    one = {**fx.GOOD_LISTS[compat], "items": [{**fx.GOOD_LISTS[compat]["items"][0], "suggested": True}]
           + fx.GOOD_LISTS[compat]["items"][1:]}
    assert not [f for f in _list_faults(compat, one) if f.startswith("L5")]
    adoption = "solution.adoption_friction"
    tagged = {**fx.GOOD_LISTS[adoption], "items": fx.GOOD_LISTS[adoption]["items"]
              + [{"label": "Pair the tag with your phone", "asked": "pair the tag with your phone", "suggested": True}]}
    assert [f for f in _list_faults(adoption, tagged) if f.startswith("L5")] == [
        "L5: item 2: the suggested step carries suggested_why -- what in the Answer or the idea calls for it, in one "
        "sentence"]
    why = {**tagged, "items": tagged["items"][:-1] + [{**tagged["items"][-1], "suggested_why": "It needs the cot."}]}
    assert not [f for f in _list_faults(adoption, why) if f.startswith("L5")]


def test_the_marks_version_moved_with_its_note():
    """FR-3: the reading of `option_validity` moved both ways, so MARKS_VERSION moved (calls 124-125)."""
    # spec 091 moved it on (22 -> 23, calls 127-128); 093's calls stand
    assert marks_mod.MARKS_VERSION == 23 and "124. **v22**" in marks_mod.__doc__ and "125. **v22**" in marks_mod.__doc__


# ------------------------------------------------------------------------ FR-4: the adoption-friction frame is the cloud's

from instructions import spoken as spoken_mod                            # noqa: E402

ADOPTION = "solution.adoption_friction"


@pytest.mark.parametrize("asked, line, count", [
    # keel-cloud 163's recorded slip -- 20 under 123's *You'd ...*, now 23 in keel-cloud 171's frame (spec 112 FR-4)
    ("would you hold your phone near the crib for ten seconds while your baby cried",
     "To use it, you'd hold your phone near the crib for ten seconds while your baby cried. Would you do that, or not?",
     23),
    # 163's worked example (was the plain *Hold your ... seconds. Would you ...*, 15): 171's frame, 19
    ("hold your phone near the cot for ten seconds",
     "To use it, you'd hold your phone near the cot for ten seconds. Would you do that, or not?", 19),
    # 132 FR-1: a leading clause said after the step, in the present -- `K2` measures it whole (was 18 after *You'd*)
    ("When the repair was done, would you speak the fix into your phone.",
     "To use it, you'd speak the fix into your phone when the repair is done. Would you do that, or not?", 21),
    # 171's `SpokenCap.step`: *you had to* is the bare step after *you'd* (was 123's *You would have to ...*)
    ("you had to talk out loud on site", "To use it, you'd talk out loud on site. Would you do that, or not?", 15),
    ("you'd scan it.", "To use it, you'd scan it. Would you do that, or not?", 12),
    # keel-cloud 171's K2 pins (`k2MeasuresTheClauseInTheNewFrame...`): ten words fit, eleven do not
    ("let an AI answer your guests in your hotel's voice",
     "To use it, you'd let an AI answer your guests in your hotel's voice. Would you do that, or not?", 20),
    ("let an AI answer all your guests in your hotel's voice",
     "To use it, you'd let an AI answer all your guests in your hotel's voice. Would you do that, or not?", 21),
])
def test_the_frame_is_itemframes_adoption_friction(asked, line, count):
    """FR-4 (spec 112 FR-1): the harness frames an Adoption friction clause as `ItemFrames.adoptionFrame` does
    (`AskedRules.framed`, keel-cloud 171), so `K2` counts the words the cloud counts."""
    assert spoken_mod.framed(ADOPTION, None, asked) == line and spoken_mod.words(line) == count


def test_163s_slip_is_no_longer_a_k2_and_a_long_one_still_is():
    """163's *What did not hold*: the cloud passed the 20-word crib line under 123's frame. Spec 112 FR-4 (keel-cloud 171
    FR-4b, *K2 now refuses the slip*): in *To use it, you'd ...* it is 23 words and a `K2`; the 10-word clause the cloud
    pins is not, and its 11-word one is."""
    assert [f for f in spoken_mod.face_faults("would you hold your phone near the crib for ten seconds while your "
                                              "baby cried", "Hold the phone near the cot", ADOPTION, None)
            if f.startswith("K2: framed")]
    assert not [f for f in spoken_mod.face_faults("let an AI answer your guests in your hotel's voice",
                                                  "Let an AI answer guests in the hotel's voice", ADOPTION, None)
                if f.startswith("K2")]
    assert [f for f in spoken_mod.face_faults("let an AI answer all your guests in your hotel's voice",
                                              "Let an AI answer guests in the hotel's voice", ADOPTION, None)
            if f.startswith("K2: framed")]


# ------------------------------------------------------------------------------- FR-5: K3 reads the framed line

@pytest.mark.parametrize("asked", [
    "open the app before picking the baby up",                 # the 2026-10-30 screen's two K3 faults, both gone
    "open it near the cot when the crying starts",
    "would you open the app before picking the baby up",
    "they'd clip a tag to the key ring",                       # said to the stranger once framed (*You'd ...*)
])
def test_a_clause_that_reads_to_the_stranger_once_framed_passes_k3(asked):
    """FR-5: *Would you {asked}. Would you do that, or not?* addresses the person -- a base-form clause is said to the
    stranger."""
    assert not [f for f in spoken_mod.face_faults(asked, "x", ADOPTION, None) if f.startswith("K3")]


@pytest.mark.parametrize("asked", ["the cry wakes the whole house", "the room is quiet enough to hear it",
                                   "it listens near the cot all night"])
def test_a_third_person_subject_still_faults_k3(asked):
    faults = [f for f in spoken_mod.face_faults(asked, "x", ADOPTION, None) if f.startswith("K3")]
    assert faults and "framed it reads" in faults[0]


def test_compatibility_k3_is_unchanged():
    """FR-5 moves Adoption friction's K3 alone: a Compatibility clause still owes *you / your* itself."""
    assert [f for f in spoken_mod.face_faults("did the phone sit within reach", "x", "solution.compatibility", "night")
            if f.startswith("K3")]
