"""Spec 144 FR-2 -- Compatibility's rows, changed by the review (keel-cloud 233 FR-2..FR-4, contract 63), as the walk
reads them: the strict checks of spec 104 FR-1 / 108 FR-2 count a changed or put-aside row present; Choose picks by
label as served; a planned pick the review put aside falls to the first founder row still on the list (recorded);
`review_changed` / `band` per list; a changed row over the cap a `DEFECT (keel-cloud 233)` finding, never a retype.

The list is keel-cloud 233's recorded one (tasks.md, *What a reviewed Compatibility list serves*: Codyco's forwarding
row rewritten into a permission, a settled row put aside, the pick pending). No stack, no model, no key.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import spoken as spoken_mod
from quality import cycle
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
COMPAT = "solution.compatibility"
TYPED = ["could forward unanswered calls to another number", "could take a booking call at the front desk",
         "had their phone online"]
PERMISSION = "was allowed to have unanswered calls forwarded to another number"
ASKED = "you were allowed to have unanswered calls forwarded to another number"
WHY = "Forwarding is set on the phone system, which someone else holds, not the desk."
SETTLED = "Most of your segment already has this: they work with a phone that is online."
BAND = ("Keel changed one condition so strangers are asked what they can do themselves, and put one condition aside "
        "because your segment already has it.")
REVIEWED = {"items": [{"code": "condition_1", "label": PERMISSION, "typed": TYPED[0], "why": WHY, "asked": ASKED},
                      {"code": "condition_2", "label": TYPED[1]}],
            "putAside": [{"typed": TYPED[2], "why": SETTLED}], "changed": {"line": BAND, "why": WHY}}
DRAFTED = {"items": [{"label": t} for t in TYPED]}


def _answer(picked: int) -> vs.CalibrationAnswer:
    return vs.CalibrationAnswer(COMPAT, {"dimension": COMPAT, "list": {"items": [{"label": t} for t in TYPED],
                                                                       "pickedIndex": picked}})


def _j(strict: bool = False):
    return SimpleNamespace(strict=strict, findings=[], review_picks={}, review_holds={})


def test_a_changed_and_a_put_aside_condition_are_present():
    """FR-2 (104 FR-1 / 108 FR-2): every condition the founder typed is on the reviewed list -- the permission row by its
    `typed`, the settled row in `putAside`; nothing left out, nothing called Keel's."""
    question = {"dimension": COMPAT, "draft": REVIEWED}
    assert vs.missing_rows(TYPED, REVIEWED) == []
    assert cs.keel_left_out(question, _answer(0)) == []
    assert cs.keel_added(question, _answer(0)) == []
    assert cs.keel_left_out({"dimension": COMPAT, "draft": {"items": REVIEWED["items"]}}, _answer(0)) == [TYPED[2]], \
        "without its put-aside row the settled condition is left out, as before"


@pytest.mark.parametrize("strict", [False, True])
def test_the_pick_is_by_label_as_served(strict):
    """FR-2: Choose picks the reviewed row by its label as served (the permission words), never put back; on the golden
    walk too where the list it picks on was reviewed."""
    j = _j(strict)
    question = {"dimension": COMPAT, "draft": REVIEWED}
    assert cs._choose_label(j, question, _answer(0)) == (PERMISSION, 0)
    assert "picked as served" in j.findings[0]["what"]
    assert cs._choose_label(_j(strict), question, _answer(1)) == (TYPED[1], 1)
    assert cs._choose_label(_j(True), {"dimension": COMPAT, "draft": DRAFTED}, _answer(2)) == (TYPED[2], 2), \
        "a list the review left alone: the golden walk's index, as before"


def test_a_planned_pick_put_aside_falls_to_the_first_founder_row():
    """FR-2: the planned pick (the settled row) was put aside -- the pick falls to the first founder row still on the
    list (the permission row, as served), recorded in `review_picks` and as a finding; never put back."""
    j = _j()
    question = {"dimension": COMPAT, "draft": REVIEWED}
    assert cs._choose_label(j, question, _answer(2)) == (PERMISSION, 0)
    assert j.review_picks[COMPAT] == {"planned": TYPED[2], "why": SETTLED, "picked": PERMISSION, "row": 0}
    assert j.findings[0]["what"] == (f"the review put the founder's picked row '{TYPED[2]}' aside (keel-cloud 233); the "
                                     f"pick fell to the first founder row still on the list, '{PERMISSION}'")
    assert cs.first_founder_row(question, TYPED) == (0, PERMISSION)
    keels_first = {"dimension": COMPAT, "draft": {"items": [{"label": "had a phone system", "suggested": True},
                                                            *REVIEWED["items"]], "putAside": REVIEWED["putAside"]}}
    assert cs.first_founder_row(keels_first, TYPED) == (1, PERMISSION), "a row the founder never typed is passed"
    none_left = {"dimension": COMPAT, "draft": {"items": [{"label": "had a phone system"}],
                                                "putAside": REVIEWED["putAside"]}}
    with pytest.raises(vs.VectorsScriptError, match="no founder row is left on the list"):
        cs._choose_label(_j(), none_left, _answer(2))


def test_choose_walks_on_the_list_as_the_review_left_it(monkeypatch):
    """FR-1 / FR-2: after a Compatibility Check whose Save named a review, the calibration is read again and Choose is
    walked on the saved list as served (`answer.list`); the hold recorded per list; a Check Save that sent a pick (a
    keel-web before 180) is a finding. Importance and Current solution have no Choose: their question stands."""
    view = {"state": "READY", "questions": [{"dimension": COMPAT, "draft": DRAFTED, "answer": {"list": REVIEWED}}]}
    monkeypatch.setattr(cs, "_wait_calibration", lambda j, vector, **k: view)
    j = _j()
    hold = {"review": "6f0c", "held": True, "held_s": 2.0, "outcome": "stayed", "picked_sent": True}
    question = cs._after_the_review(j, "SOLUTION", {"dimension": COMPAT, "draft": DRAFTED}, {"review_hold": hold})
    assert question["draft"] is REVIEWED and j.review_holds[COMPAT] == hold
    assert "sent a pickedIndex" in j.findings[0]["what"]
    assert cs._choose_label(j, question, _answer(0)) == (PERMISSION, 0)
    untouched = {"state": "READY", "questions": [{"dimension": COMPAT, "answer": {"list": DRAFTED}}]}
    monkeypatch.setattr(cs, "_wait_calibration", lambda j, vector, **k: untouched)
    q = {"dimension": COMPAT, "draft": DRAFTED}
    assert cs._after_the_review(_j(), "SOLUTION", q, {"review_hold": {**hold, "picked_sent": False}}) is q
    imp = {"dimension": "problem.importance", "draft": DRAFTED}
    assert cs._after_the_review(_j(), "PROBLEM", imp, {"review_hold": hold}) is imp
    moved = {"review": None, "held": False, "outcome": "moved", "picked_sent": False}
    assert cs._after_the_review(_j(), "SOLUTION", q, {"review_hold": moved}) is q, "no review, nothing re-read"


def test_what_the_review_did_to_compatibility_is_recorded_per_list():
    """FR-2: `review_changed` / `band` for Compatibility as 143 records Importance's and Current solution's."""
    views = {"SOLUTION": {"questions": [{"dimension": COMPAT, "answer": {"list": REVIEWED}}]}}
    assert vs.lists_reviewed(views) == {COMPAT: {
        "review_changed": [{"typed": TYPED[0], "label": PERMISSION, "why": WHY},
                           {"typed": TYPED[2], "label": None, "why": SETTLED}],
        "band": {"line": BAND, "why": WHY}}}
    assert cycle.review_rows(vs.lists_reviewed(views)) == {"changed": 1, "put_aside": 1}


def test_a_changed_condition_over_the_cap_is_a_233_defect_never_a_retype():
    """FR-2: a changed Compatibility row over the served cap (16) is filed `DEFECT (keel-cloud 233)`, left as served."""
    long = {"items": [{"label": "was allowed by the practice owner to have every unanswered call forwarded to another "
                                "number at any time", "typed": TYPED[0], "why": WHY}]}
    j = _j()
    assert cs.review_defects(j, COMPAT, REVIEWED, 16) == []
    over = cs.review_defects(j, COMPAT, long, 16)
    assert over and over[0]["words"] == 18
    assert j.findings[0]["what"].startswith(f"DEFECT (keel-cloud 233): the review changed the founder's row "
                                            f"'{TYPED[0]}'") and "18 words, over the 16-word cap; left as served" in \
        j.findings[0]["what"]
    j = _j()
    cs.review_defects(j, "problem.current_solution_satisfaction", {"items": [{"label": "a b c d e f g h i j",
                                                                              "typed": "x"}]}, 9)
    assert j.findings[0]["what"].startswith("DEFECT (keel-cloud 232)"), "232's lists keep their spec"


def test_the_stored_list_holds_the_pick_by_its_words():
    """FR-2: the strict stored-list check reads a reviewed Compatibility list back to the founder's words, the pick by
    its words (the picked row's `typed`), or the row it fell to."""
    want = {"items": [{"code": f"condition_{n + 1}", "label": t} for n, t in enumerate(TYPED)], "pickedIndex": 0,
            "phrase": None}
    assert cs.reviewed_as_saved(want, {**REVIEWED, "pickedIndex": 0})
    assert not cs.reviewed_as_saved(want, {**REVIEWED, "pickedIndex": 1})
    fell = {"planned": TYPED[2], "picked": PERMISSION, "row": 0}
    assert cs.reviewed_as_saved({**want, "pickedIndex": 2}, {**REVIEWED, "pickedIndex": 0}, fell)
    assert not cs.reviewed_as_saved({**want, "pickedIndex": 2}, {**REVIEWED, "pickedIndex": 1}, fell)


def test_the_stranger_hears_the_permission_four():
    """FR-2 (233 FR-3, its spoken pin): the changed row's words read as a permission by the harness's mirror of
    `ItemFrames.kindOf` (no stored kind: the kind follows the words) -- the registry's four, never the ability's -- and
    keel-cloud's own pin serves *Were you allowed to have unanswered calls forwarded to another number?*."""
    assert spoken_mod.kind_of(None, ASKED, PERMISSION) == "PERMISSION"
    assert spoken_mod.kind_of(None, None, TYPED[0]) == "ABILITY", "Put back restores the ability with the words"
    path = (KEEL_CLOUD / "src/test/java/com/keeldiscovery/cloud/application/TheReviewChangesTheConditionsTest.java")
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD}")
    source = " ".join(path.read_text(encoding="utf-8").split())
    assert ("Think of your last booking call. Were you allowed to have unanswered \" + \"calls forwarded to another "
            "number?") in source
    assert vs_screens.served_word_cap({"saves": {"maxWords": 16}}) == 16
