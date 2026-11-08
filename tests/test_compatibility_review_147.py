"""Spec 147 FR-3 -- the walk on Compatibility after keel-cloud 236: the review reads every row, Keel's included -- a row
Keel drafted may come back changed (its `typed` Keel's words) or put aside; where it puts the suggestion aside it may
suggest another at the end (`suggested` with `suggestedWhy`, absent from the Answer's draft), Keel's own and a valid
pick. On 236's cluster shape (tasks.md, *A cluster's list*). No stack, no model, no key.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from evals import corpus_scenario as cs
from harness import vectors_script as vs

COMPAT = "solution.compatibility"
FOUNDER = "could tell within the hour that a training run had stalled"
KEELS = "could run a monitoring agent on the job's node"
KEELS_SUGGESTED = "had their jobs queued through the cluster's scheduler"
CHANGED = "were allowed to have a monitoring agent run on the job's node"
NEW = "were allowed to let an outside tool read the job's source code"
NEW_WHY = "No row asks whether they may let an outside tool read the job's code, the step the idea needs first."
SETTLED = "Most of your segment already has this: every job on a shared cluster is queued by its scheduler."
WHY = "Running an agent on a node is set by the cluster's admins, not the researcher."
BAND = ("Keel changed one condition so strangers are asked what they can do themselves, and put one condition aside "
        "because your segment already has it.")

DRAFT = {"items": [{"code": "condition_1", "label": FOUNDER}, {"code": "condition_2", "label": KEELS},
                   {"code": "condition_3", "label": KEELS_SUGGESTED, "suggested": True,
                    "suggestedWhy": "The step most likely to be missing."}]}
SAVED = {"items": [{"code": "condition_1", "label": FOUNDER},
                   {"code": "condition_2", "label": CHANGED, "typed": KEELS, "why": WHY},
                   {"code": "condition_3", "label": NEW, "suggested": True, "suggestedWhy": NEW_WHY}],
         "putAside": [{"typed": KEELS_SUGGESTED, "why": SETTLED}], "changed": {"line": BAND, "why": WHY}}


def _answer(*typed: str, picked: int = 0):
    return SimpleNamespace(listed={"items": [{"label": t} for t in typed], "pickedIndex": picked}, unsure=False)


def _reviewed(saved=SAVED, draft=DRAFT) -> dict:
    """The question as `_after_the_review` hands it to Choose."""
    j = SimpleNamespace(findings=[], review_holds={})
    view = {"questions": [{"dimension": COMPAT, "answer": {"list": saved}}]}
    original = cs._wait_calibration
    cs._wait_calibration = lambda _j, _v: view
    try:
        return cs._after_the_review(j, "SOLUTION", {"dimension": COMPAT, "draft": draft},
                                    {"review_hold": {"review": "r1", "outcome": "stayed"}})
    finally:
        cs._wait_calibration = original


def test_the_review_suggestion_is_read_off_the_saved_list():
    """FR-3 (236 FR-2): a saved row `suggested` with a why that the Answer's draft does not carry -- never the draft's
    own suggested row (121's mark)."""
    assert vs.review_suggested(SAVED, DRAFT) == [{"label": NEW, "why": NEW_WHY}]
    assert vs.review_suggested(DRAFT, DRAFT) == []
    assert vs.review_suggested({**SAVED, "items": SAVED["items"][:2]}, DRAFT) == []
    assert vs.as_drafted(SAVED) == [FOUNDER, KEELS, NEW, KEELS_SUGGESTED]


def test_choose_walks_the_saved_list_and_knows_the_suggestion():
    question = _reviewed()
    assert question["draft"] is SAVED and question["answer_draft"] is DRAFT
    assert question["review_suggested"] == [NEW]
    # a suggestion alone (236: no band where nothing else changed) still moves Choose onto the saved list
    alone = {"items": [{"code": "condition_1", "label": FOUNDER}, {"code": "condition_2", "label": KEELS},
                       {"code": "condition_3", "label": NEW, "suggested": True, "suggestedWhy": NEW_WHY}]}
    draft = {"items": DRAFT["items"][:2]}
    moved = _reviewed(alone, draft)
    assert moved["draft"] is alone and moved["review_suggested"] == [NEW]
    untouched = _reviewed(draft, draft)
    assert untouched["draft"] is draft and "review_suggested" not in untouched


def test_keels_changed_and_put_aside_rows_are_keels_and_present():
    """FR-3: `keel_added` names Keel's changed row as served and Keel's put-aside row by its words, never the review's
    suggestion (named apart); `keel_left_out` finds nothing left out."""
    question = _reviewed()
    answer = _answer(FOUNDER)
    assert cs.keel_added(question, answer) == [CHANGED, f"{KEELS_SUGGESTED} (put aside)"]
    assert cs.keel_left_out(question, answer) == []
    assert cs._founders_rows(question) == [FOUNDER, CHANGED]


def test_a_founder_row_keel_reworded_then_the_review_changed_is_found_by_its_typed():
    """FR-3 (236 FR-1, read with 108 FR-1): Keel's draft moved the founder's *can* to *could* and the review then rewrote
    the row -- found by the words it was saved with (its `typed`), never left out, never Keel's."""
    question = _reviewed()
    answer = _answer(FOUNDER, "can run a monitoring agent on the job's node")
    assert cs.keel_left_out(question, answer) == []
    assert cs.keel_added(question, answer) == [f"{KEELS_SUGGESTED} (put aside)"]


def test_the_review_suggestion_is_named_never_a_stop():
    """FR-3: the review's suggestion is a finding naming it and its why, beside *Keel added*."""
    j = SimpleNamespace(findings=[])
    cs._name_keel_added(j, COMPAT, _reviewed(), _answer(FOUNDER))
    whats = [f["what"] for f in j.findings]
    assert whats[0] == f"Compatibility: Keel added: '{CHANGED}', '{KEELS_SUGGESTED} (put aside)'"
    assert whats[1] == f"Compatibility: Keel's review suggested at the Check: '{NEW}' -- {NEW_WHY} (keel-cloud 236 FR-2)"


def test_the_pick_by_label_as_served_and_the_suggestion_a_valid_pick():
    """FR-3 (144 FR-2): the founder's pick by its label as served; where the review put the planned pick aside and no
    founder row is left, the pick falls to the review's suggestion (recorded), never a stop."""
    j = SimpleNamespace(strict=False, findings=[], review_picks={})
    question = _reviewed()
    assert cs._choose_label(j, question, _answer(FOUNDER)) == (FOUNDER, 0)
    gone = {"items": [{"code": "condition_1", "label": CHANGED, "typed": KEELS, "why": WHY},
                      {"code": "condition_2", "label": NEW, "suggested": True, "suggestedWhy": NEW_WHY}],
            "putAside": [{"typed": FOUNDER, "why": SETTLED}], "changed": {"line": BAND, "why": WHY}}
    question = _reviewed(gone)
    assert cs.first_founder_row(question, [FOUNDER]) is None
    assert cs._choose_label(j, question, _answer(FOUNDER)) == (NEW, 1)
    assert j.review_picks[COMPAT]["picked"] == NEW
    assert "fell to Keel's review suggested in its place (keel-cloud 236 FR-2)" in j.findings[-1]["what"]
    # Choose offers the rows as served -- the suggestion among them, no put-aside row
    choose = {"options": [CHANGED, NEW], "writes": []}
    assert cs.choose_after_review_faults(question, choose) == []


def test_without_a_suggestion_nothing_is_left_to_pick_and_the_walk_stops_by_name():
    j = SimpleNamespace(strict=False, findings=[], review_picks={})
    gone = {"items": [{"code": "condition_1", "label": CHANGED, "typed": KEELS, "why": WHY}],
            "putAside": [{"typed": FOUNDER, "why": SETTLED}], "changed": {"line": BAND, "why": WHY}}
    question = {"dimension": COMPAT, "draft": gone}
    with pytest.raises(vs.VectorsScriptError, match="no founder row is left"):
        cs._choose_label(j, question, _answer(FOUNDER))
