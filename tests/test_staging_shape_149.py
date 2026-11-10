"""Spec 149 FR-4 -- the regression shape at this layer: the founder's staging find of 2026-11-09 (Importance's Check: the
own row and three handed, the review answering `drop` at 2, 3 and 4 with three distinct reasons -- it counted from 1).
keel-cloud 243 guards it on the cloud (`TheReadBackIndexIsNeverMisappliedTest`), keel-web 184 on the page; here:

- **the mirror** (`vectors_script`): the context numbered, the answer read shifted (`review.shift: 1`), each reason on
  its own row, the three struck, a Keel row in each place, the band counting both -- and the misread (the same answer
  read from 0, the staging bug) named by `in_place_faults`;
- **the scripted Importance journey**: S-005 (01-countly, the corridor) and S-015 (its problem study) walk Importance's
  Check through `leg_calibrate` -> `_after_the_review` -> `_hold_in_place`, which on a strict walk asserts the list in a
  named step and on a back-test files each fault as a finding. Run here against the mirror's wire (no stack, no model,
  no key, no paid run).

The study is keel-cloud 243's invented one (a payroll-shaped study, an invented idea); no trade is named in code.
"""

from __future__ import annotations

import inspect
import json
from types import SimpleNamespace

import pytest

from evals import corpus_scenario as cs
from harness import vectors_script as vs
from harness.steps import Recorder
from tests.test_check_pattern_184_149 import staging_saved
from tests.test_read_back_rows_149 import (EXPLAINING, GAMES, GAMES_WHY, NEW_HIRE, NEW_HIRE_WHY, OVERTIME,
                                           OVERTIME_WHY, OWN, RECONCILING, RERUNNING, STAGING, STAGING_BAND,
                                           staging_answer)

IMPORTANCE = "problem.importance"


def misread_saved() -> dict:
    """The staging bug as it reached the founder (keel-cloud before 243): the 1-based answer read from 0 -- the first
    reason on the second rival, the second on the third, the third out of range, the floor keeping a row with the wrong
    reason, the row judged outside the work left standing."""
    readings = [{"at": n["index"], "note": n["note"], "label": None, "drop": True, "suggest": None}
                for n in staging_answer(1)["notes"] if n["index"] < len(STAGING)]
    listed = vs.in_place_applied(STAGING, readings, floor=3)
    return {"items": listed["items"], "putAside": listed["putAside"], "notes": listed["notes"],
            "changed": {"line": vs.band_line(IMPORTANCE, listed), "why": readings[0]["note"]}}


# ------------------------------------------------------------------------------------------- the mirror

def test_the_staging_shape_of_2026_11_09_through_the_mirror():
    """FR-4: own + 3 handed numbered from 0; the answer counted from 1 (drops at 2, 3, 4, three distinct reasons) is
    read shifted; the right rows are struck (the three rivals, never the own row), each reason on its own row, a Keel row
    in each place, the band counting both -- and `in_place_faults` finds nothing."""
    assert vs.read_back_context(IMPORTANCE, STAGING)["rows"][0] == {"index": 0, "label": OWN}
    answer = vs.read_back_answer(staging_answer(1), STAGING)
    assert answer["shift"] == 1 and answer["refused"] == []
    assert len({r["note"] for r in answer["readings"]}) == 3, "three distinct reasons"
    saved = staging_saved()
    assert [(a["typed"], a["why"]) for a in saved["putAside"]] == [(GAMES, GAMES_WHY), (OVERTIME, OVERTIME_WHY),
                                                                   (NEW_HIRE, NEW_HIRE_WHY)]
    assert [(i["label"], vs.in_place_of(i)) for i in saved["items"]] == [
        (OWN, None), (RECONCILING, GAMES), (RERUNNING, OVERTIME), (EXPLAINING, NEW_HIRE)]
    assert vs.band_counts(saved["changed"]["line"]) == {"changed": 0, "put_aside": 3, "in_place": 3}
    assert vs.in_place_faults(STAGING, saved) == []


def test_the_staging_misread_is_named():
    """FR-4: the same answer read from 0 -- the bug the founder met -- is named: the first reason (*Playing video games
    is no difficulty ...*) sits on the overtime row, the second (*Overtime hours ...*) as a note under the new hire row."""
    saved = misread_saved()
    assert [a["typed"] for a in saved["putAside"]] == [OVERTIME] and saved["putAside"][0]["why"] == GAMES_WHY
    notes = [(n["row"], n["note"]) for n in saved["notes"]]
    faults = vs.in_place_faults(STAGING, saved, notes=notes)
    assert [f["what"] for f in faults] == ["a reason on the wrong row", "a note on the wrong row"]
    assert faults[0]["typed"] == OVERTIME and faults[0]["about"] == GAMES
    assert faults[1]["row"] == NEW_HIRE and faults[1]["about"] == OVERTIME


def test_the_pairs_reasons_and_band_are_each_held():
    """FR-4: each rule of `in_place_faults` on its own -- the own row struck, a reason said twice, a Keel row out of its
    place, a Keel row for a row not struck, a row lost, a band that miscounts."""
    good = staging_saved()

    def faults(mutate):
        saved = json.loads(json.dumps(good))
        mutate(saved)
        return [f["what"] for f in vs.in_place_faults(STAGING, saved)]

    assert "the own row put aside" in faults(lambda s: s["putAside"].append({"typed": OWN, "why": "x y z"}))
    assert "two rows put aside with one reason" in faults(
        lambda s: s["putAside"][1].update(why=s["putAside"][0]["why"]))
    assert "Keel's row does not stand where the row put aside stood" in faults(
        lambda s: s["items"].__setitem__(slice(1, 3), [s["items"][2], s["items"][1]]))
    assert "a Keel row in place of a row not put aside" in faults(lambda s: s["items"].append(
        {"label": "Filing the run's report", "suggested": True, "suggestedWhy": "w", "inPlaceOf": "Lunch"}))
    assert "a row the founder saved is lost" in faults(lambda s: s["putAside"].pop())
    assert "the band does not count the list" in faults(
        lambda s: s["changed"].update(line="Keel put three rows aside so the rest sit at the moment your problem names."))


# --------------------------------------------------------------------------- the scripted Importance journey

def _journey(tmp_path, *, strict: bool, saved: dict):
    view = {"questions": [{"dimension": IMPORTANCE, "answer": {"list": saved}}]}
    j = SimpleNamespace(strict=strict, findings=[], review_holds={}, recorder=Recorder(tmp_path),
                        get=lambda *_a, **_k: view)
    return j, view


def _check(saved: dict) -> dict:
    """The Check as the walk read it: the rows as saved (the own row locked first), then -- after the hold -- as 184
    draws the list the review left (notes under the rows they were served for)."""
    rows = [{"text": OWN, "tag": "yours", "locked": True}] + [{"text": r, "locked": False} for r in STAGING[1:]]
    reviewed = [{"text": i["label"], **({"keel": "in-place", "n": n, "in_place_of": vs.in_place_of(i), "put_back": True,
                                         "suggested": True} if vs.in_place_of(i) else {})}
                for n, i in enumerate(saved["items"])]
    for row in reviewed:
        row.update({"note": n["note"] for n in saved.get("notes") or [] if n["row"] == row["text"]})
    record = [{"kind": "replaced" if a.get("replacedBy") else "aside", "whose": "yours", "struck": [a["typed"]],
               "why": a["why"], "now": a.get("replacedBy"), "put_back": not a.get("replacedBy"),
               **({"n": k} if a.get("replacedBy") else {})} for k, a in enumerate(saved["putAside"], start=1)]
    for row in reviewed:
        if row.get("keel"):
            row["n"] = next(e["n"] for e in record if e["now"] == row["text"])
    return {"rows": rows, "review_hold": {"review": "r1", "outcome": "stayed", "held": True},
            "reviewed": {"rows": reviewed, "keel_changed": record, "band": saved["changed"]}}


def test_the_scripted_importance_journey_asserts_the_staging_shape(tmp_path, monkeypatch):
    """FR-4: on the strict walk (S-005 / S-015) a Check that stayed with the band is held in a named step -- the staging
    shape as 243 applies it passes; the misread fails the step by name."""
    saved = staging_saved()
    j, view = _journey(tmp_path, strict=True, saved=saved)
    monkeypatch.setattr(cs, "_wait_calibration", lambda _j, _v: view)
    question = {"dimension": IMPORTANCE, "draft": {"items": [{"label": r} for r in STAGING]}}
    assert cs._after_the_review(j, "PROBLEM", question, _check(saved)) is question
    step = json.loads((tmp_path / "transcript.jsonl").read_text().splitlines()[-1])
    assert step["ok"] is True and "the right rows struck, each reason on its own row, a Keel row in each place" \
        in step["name"]

    bad = misread_saved()
    j, view = _journey(tmp_path / "bad", strict=True, saved=bad)
    monkeypatch.setattr(cs, "_wait_calibration", lambda _j, _v: view)
    with pytest.raises(AssertionError, match="a reason on the wrong row"):
        cs._after_the_review(j, "PROBLEM", question, _check(bad))
    assert j.recorder.failed_step.startswith(f"{IMPORTANCE}: the review's list holds")


def test_on_the_back_test_the_misread_is_a_finding_never_a_stop(tmp_path, monkeypatch):
    """FR-4: the cycle's walk (a back-test, `strict` False) files each fault as a finding naming its layer."""
    bad = misread_saved()
    j, view = _journey(tmp_path, strict=False, saved=bad)
    monkeypatch.setattr(cs, "_wait_calibration", lambda _j, _v: view)
    cs._after_the_review(j, "PROBLEM", {"dimension": IMPORTANCE}, _check(bad))
    assert [f["what"] for f in j.findings] == ["Importance: a reason on the wrong row (keel-cloud 243)",
                                               "Importance: a note on the wrong row (keel-cloud 243)"]


def test_s005_and_s015_reach_the_hold_through_importances_check():
    """FR-4: where the assertion lives -- `leg_calibrate` hands each reviewed Check to `_after_the_review`, which holds a
    Check that stayed (`_hold_in_place`) before anything else; S-005 walks 01-countly's corridor (`corpus_scenario.run`)
    and S-015 its problem study (`scope_journey.walk` -> `leg_calibrate(j, "PROBLEM")`), Importance's Check on both."""
    from evals import scope_journey                                    # noqa: PLC0415
    assert "_after_the_review(j, vector, question, seen[-1])" in inspect.getsource(cs.leg_calibrate)
    assert "_hold_in_place(j, key, check, saved)" in inspect.getsource(cs._after_the_review)
    assert 'cs.leg_calibrate(j, "PROBLEM")' in inspect.getsource(scope_journey.walk)
    assert IMPORTANCE in cs.FIRST_FIXED, "the own row is never struck"
