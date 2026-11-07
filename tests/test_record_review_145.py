"""Spec 145 FR-2 -- the record: the review line says, beside the rows changed and put aside per dimension, how many
Current solution ladders were rewritten whole as one scale (a band whose line opens *Keel rewrote the scale*, keel-cloud
235 FR-4) and the longest Save hold per dimension (`review_holds`' `held_s`, spec 144 FR-1) -- so keel-cloud 235's second
read-back turn, which runs inside that hold, shows in the record without a new wire field. A hold that reached the
page's cap stays 144's DEFECT stop.

No model, no stack, no network: the record is built from fixture bundles (`backtest.json`) through `walk_one` with a
fake runner, then composed and rendered.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from evals import backtest as bt
from harness import vectors_screens as vs_screens
from quality import cycle
from tests.test_cloud_235_mirror_145 import COUNTED, CS, LADDER

IMP = "problem.importance"
COMPAT = "solution.compatibility"
IMPORTANCE = {"review_changed": [{"typed": "Choosing a seat where they can see every face", "label": None, "why": "w"}],
              "band": {"line": "Keel put one row aside so the rest sit at the moment your problem names.", "why": "w"}}


def _reviewed(saved: dict) -> dict:
    """A bundle's `lists_reviewed` entry for a served list (`vectors_script.lists_reviewed`'s shape)."""
    from harness import vectors_script as vs                       # noqa: PLC0415
    return {"review_changed": vs.review_changed(saved), "band": vs.review_band(saved)}


def _hold(held_s, outcome="stayed", review="0b0b0b0b-0000-4000-8000-000000000001") -> dict:
    return {"review": review, "held": held_s is not None, "held_s": held_s, "outcome": outcome, "picked_sent": False,
            "continue_put": 0}


#: Three walks with the switch on, as 144's walk writes their bundles: Codyco's ladder rewritten whole (235's band, the
#: Save held 41.3 s over two read-back turns), Fresco's with the measure dropped (232's count line), Palus's Importance
#: hold that ran to the page's cap (the DEFECT stop; the walk stopped there).
BUNDLES = {
    "21-codyco": {"lists_reviewed": {CS: _reviewed(LADDER)},
                  "review_holds": {IMP: _hold(6.2, "moved"), CS: _hold(41.3)},
                  "founder_screens": [{"screen": f"check-{CS}"}, {"screen": f"check-{CS}-reviewed"}]},
    "08-fresco": {"lists_reviewed": {CS: _reviewed(COUNTED), IMP: IMPORTANCE},
                  "review_holds": {IMP: _hold(9.0), CS: _hold(12.5), COMPAT: _hold(None, "moved", None)},
                  "founder_screens": [{"screen": f"check-{IMP}-reviewed"}, {"screen": f"check-{CS}-reviewed"}]},
    "10-palus": {"lists_reviewed": {},
                 "review_holds": {IMP: _hold(88.4, "timeout")}, "failed_step": "check",
                 "founder_screens": [{"screen": f"check-{IMP}"}]},
}


def _walk(tmp_path, entry: str, bundle: dict) -> cycle.Study:
    runs = tmp_path / "runs"

    def fake(argv, stdout=None, stderr=None):
        if argv[4] == "backtest":
            run = runs / f"20261107T100000Z-backtest-{entry}"
            run.mkdir(parents=True)
            (run / bt.RECORD).write_text(json.dumps({"run": run.name, "passed": True, "scope": "PROBLEM",
                                                     "review_switch": "ON", **bundle}))
            stdout.write(f"run bundle: {run}\n")
        return SimpleNamespace(returncode=0)

    steps = [s for s in cycle.plan_steps([entry], ["PROBLEM"], "keel", tmp_path / "work" / entry) if s["study"]]
    return cycle.walk_one(entry, "PROBLEM", steps, door="keel", runner=fake, runs_dir=runs)


def _studies(tmp_path) -> list[cycle.Study]:
    return [_walk(tmp_path, entry, bundle) for entry, bundle in BUNDLES.items()]


def test_a_walk_reads_the_ladder_and_the_holds_off_its_bundle(tmp_path):
    codyco, fresco, palus = _studies(tmp_path)
    assert (codyco.review_scales, fresco.review_scales, palus.review_scales) == (1, 0, 0), \
        "the band's line as served: 235's on Codyco, 232's count on Fresco (the measure dropped)"
    assert codyco.review_held == {IMP: {"held_s": 6.2, "outcome": "moved"}, CS: {"held_s": 41.3, "outcome": "stayed"}}
    assert fresco.review_held == {IMP: {"held_s": 9.0, "outcome": "stayed"}, CS: {"held_s": 12.5, "outcome": "stayed"}}, \
        "a Save that never held is not a hold"
    assert palus.review_held == {IMP: {"held_s": 88.4, "outcome": "timeout"}}
    assert codyco.review_dims[CS] == {"changed": 3, "put_aside": 0}, "144's counts stand beside it"
    data = cycle._study_data(codyco)
    assert data["review_scales"] == 1 and data["review_held"][CS]["held_s"] == 41.3
    before = cycle._study_data(cycle.Study("a", "PROBLEM"))
    assert "review_scales" not in before and "review_held" not in before, "a study before 145 keeps its shape"


def test_a_bundle_before_144_carries_neither(tmp_path):
    study = cycle.study_review(cycle.Study("a", "PROBLEM"), {"review_switch": "ON", "lists_reviewed": {CS: _reviewed(LADDER)}})
    assert study.review_rows == {"changed": 3, "put_aside": 0}
    assert study.review_scales is None and study.review_held is None and study.review_dims is None
    off = cycle.study_review(cycle.Study("a", "PROBLEM"), {"review_switch": "OFF", **BUNDLES["21-codyco"]})
    assert off.review_scales is None and off.review_held is None




def test_the_record_says_the_ladders_and_the_longest_hold(tmp_path):
    kw = dict(name="20261107-74a04fb", why="spec 235", door="keel", cloud_sha="74a04fb", web_sha="fbfe96a",
              started="s", ended="e", seconds=1.0, cfg=cycle.load_config(), baseline_path=tmp_path / "BASELINE.md",
              cycles_dir=tmp_path, decisions=[])
    text, data = cycle.compose(_studies(tmp_path), review="ON", **kw)
    line = next(x for x in text.splitlines() if x.startswith("  - the review (spec 209"))
    assert line == (
        "  - the review (spec 209, keel-cloud 232, 233, 235): 6 founder rows changed and 1 put aside over 3 walks (each "
        "bundle's `lists_reviewed`) -- Importance 0 changed / 1 put aside, Current solution 6 changed / 0 put aside, "
        "Compatibility 0 changed / 0 put aside; 1 Current solution ladder rewritten whole as one scale (the band's "
        "*Keel rewrote the scale ...*, keel-cloud 235); the longest hold on Save (each bundle's `review_holds`): "
        "Importance 88.4 s (10-palus · PROBLEM -- the page's cap: DEFECT (keel-cloud 233), the walk stopped), "
        "Current solution 41.3 s (21-codyco · PROBLEM), Compatibility none; the Check shot again after the band "
        f"(keel-cloud 233, spec 144) on 3 screens: 21-codyco · PROBLEM `check-{CS}-reviewed`, 08-fresco · PROBLEM "
        f"`check-{IMP}-reviewed`, 08-fresco · PROBLEM `check-{CS}-reviewed`; the readers scored the screens as served, "
        "the second shots under their dimension")
    # the record read back (its data block) renders the same line
    path = tmp_path / "20261107-74a04fb.md"
    path.write_text(text, encoding="utf-8")
    assert line in cycle.render_record(cycle.load_record(path)).splitlines()


def test_a_record_of_walks_before_145_reads_as_144_wrote_it():
    studies = [{"entry": "21-codyco", "scope": "ALL", "review_rows": {"changed": 1, "put_aside": 0},
                "review_dims": cycle.review_dims({CS: _reviewed(LADDER)}), "review_shots": []}]
    line = cycle.review_line({"review_switch": "ON", "studies": studies})[0]
    assert line.startswith("  - the review (spec 209, keel-cloud 232, 233): ")
    assert "rewritten whole" not in line and "longest hold" not in line


def test_two_ladders_and_no_hold():
    studies = [{"entry": e, "scope": "PROBLEM", "review_rows": {"changed": 3, "put_aside": 0},
                "review_dims": cycle.review_dims({CS: _reviewed(LADDER)}), "review_shots": [], "review_scales": 1,
                "review_held": {}} for e in ("21-codyco", "08-fresco")]
    line = cycle.review_line({"review_switch": "ON", "studies": studies})[0]
    assert "; 2 Current solution ladders rewritten whole as one scale (the band's *Keel rewrote the scale ...*, " \
           "keel-cloud 235); the longest hold on Save (each bundle's `review_holds`): Importance none, Current " \
           "solution none, Compatibility none; no Check stayed with the band" in line


def test_the_scale_is_read_by_the_line_served_never_built():
    assert cycle.review_scales({CS: _reviewed(LADDER)}) == 1
    assert cycle.review_scales({CS: _reviewed(COUNTED)}) == 0, "the measure dropped: 232's line"
    assert cycle.review_scales({IMP: {"band": {"line": "Keel rewrote the scale so ..."}}}) == 0, "Current solution's alone"
    assert cycle.review_scales({}) == cycle.review_scales(None) == 0
    assert LADDER["changed"]["line"].startswith(cycle.SCALE_REWRITTEN)


def test_a_hold_at_the_cap_stays_144s_defect_stop():
    """FR-2: the cap and the stop are 144's, untouched -- the page's 90 s, the grace, the walk's ceiling, the stop's
    words in the bundle's transcript."""
    assert (vs_screens.REVIEW_HOLD_CAP_S, vs_screens.REVIEW_HOLD_GRACE_S, vs_screens.REVIEW_HOLD_CEILING_S) == (90, 5, 120)
    assert issubclass(vs_screens.ReviewHoldStop, AssertionError)
    assert bt.review_hold_said(_hold(88.4, "timeout")).startswith(
        "held on *Keel is reading your answers* 88.4 s, past the cap: DEFECT (keel-cloud 233), the walk stopped")
