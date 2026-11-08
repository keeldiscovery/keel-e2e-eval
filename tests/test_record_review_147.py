"""Spec 147 FR-4 -- the record: the review line counts four dimensions (Relative advantage beside Importance, Current
solution and Compatibility, keel-cloud 237), names the fourth screenshot (`check-solution.relative_advantage-reviewed`),
and says beside the benefits put aside whether the hard case was changed (the band's second line, read from
`changed.line`); `review_holds` keyed by dimension as before. A record of walks before 147 reads as 145 wrote it.

No model, no stack, no network: fixture bundles (`backtest.json`) through `walk_one` with a fake runner, composed and
rendered.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from evals import backtest as bt
from harness import vectors_screens as vs_screens
from quality import cycle
from tests.test_cloud_235_mirror_145 import CS, LADDER
from tests.test_record_review_145 import _hold, _reviewed
from tests.test_relative_advantage_review_147 import MOMENT_ONLY, SAVED

RA = "solution.relative_advantage"
IMP = "problem.importance"
COMPAT = "solution.compatibility"
FOUR = list(vs_screens.REVIEWED_LISTS)

#: Two walks of 147's: Expanse's benefits, three put aside and the moment changed (237's cluster Check), the Save held
#: 18.4 s; Codyco's, the moment alone changed (no row moved), and its ladder rewritten whole on PROBLEM.
BUNDLES = {
    "17-expanse": {"scope": "SOLUTION", "reviewed_lists": FOUR, "lists_reviewed": {RA: _reviewed(SAVED)},
                   "review_holds": {COMPAT: _hold(None, "moved", None), RA: _hold(18.4)},
                   "founder_screens": [{"screen": f"check-{RA}"}, {"screen": f"check-{RA}-reviewed"}]},
    "21-codyco": {"scope": "SOLUTION", "reviewed_lists": FOUR,
                  "lists_reviewed": {RA: _reviewed(MOMENT_ONLY), CS: _reviewed(LADDER)},
                  "review_holds": {RA: _hold(7.0), CS: _hold(30.1)},
                  "founder_screens": [{"screen": f"check-{CS}-reviewed"}, {"screen": f"check-{RA}-reviewed"}]},
}


def _walk(tmp_path, entry: str, bundle: dict) -> cycle.Study:
    runs = tmp_path / "runs"

    def fake(argv, stdout=None, stderr=None):
        if argv[4] == "backtest":
            run = runs / f"20261108T100000Z-backtest-{entry}"
            run.mkdir(parents=True)
            (run / bt.RECORD).write_text(json.dumps({"run": run.name, "passed": True, "review_switch": "ON", **bundle}))
            stdout.write(f"run bundle: {run}\n")
        return SimpleNamespace(returncode=0)

    steps = [s for s in cycle.plan_steps([entry], ["SOLUTION"], "keel", tmp_path / "work" / entry) if s["study"]]
    return cycle.walk_one(entry, "SOLUTION", steps, door="keel", runner=fake, runs_dir=runs)


def test_the_bundle_records_the_four_lists_it_waits_on():
    assert bt.reviewed_lists() == ["problem.importance", "problem.current_solution_satisfaction",
                                   "solution.compatibility", RA]


def test_a_walk_reads_the_fourth_dimension_off_its_bundle(tmp_path):
    expanse, codyco = (_walk(tmp_path, e, b) for e, b in BUNDLES.items())
    assert expanse.review_dims[RA] == {"changed": 0, "put_aside": 3}
    assert codyco.review_dims[RA] == {"changed": 0, "put_aside": 0}
    assert (expanse.review_moments, codyco.review_moments) == (1, 1)
    assert expanse.review_held == {RA: {"held_s": 18.4, "outcome": "stayed"}}
    assert codyco.review_held == {CS: {"held_s": 30.1, "outcome": "stayed"}, RA: {"held_s": 7.0, "outcome": "stayed"}}
    assert cycle._study_data(expanse)["review_moments"] == 1
    assert "review_moments" not in cycle._study_data(cycle.Study("a", "SOLUTION")), "a study before 147 keeps its shape"
    # a bundle before 147 (no `reviewed_lists`) counts the three, as 145 did
    before = cycle.study_review(cycle.Study("a", "SOLUTION"), {"review_switch": "ON", "review_holds": {},
                                                             "lists_reviewed": {RA: _reviewed(SAVED)}})
    assert RA not in before.review_dims and before.review_moments is None


def test_the_moment_is_read_off_the_band_as_served():
    assert cycle.review_moments({RA: _reviewed(SAVED)}) == 1
    assert cycle.review_moments({RA: _reviewed(MOMENT_ONLY)}) == 1
    only_benefits = {**SAVED, "changed": {"line": "Keel put three benefits aside so what is left is what only your idea "
                                                   "would have given them.", "why": "w"}}
    assert cycle.review_moments({RA: _reviewed(only_benefits)}) == 0
    assert cycle.review_moments({}) == cycle.review_moments(None) == 0


def test_the_record_counts_four_and_names_the_fourth_screenshot(tmp_path):
    kw = dict(name="20261108-7662026", why="spec 147", door="keel", cloud_sha="7662026", web_sha="b8682c4",
              started="s", ended="e", seconds=1.0, cfg=cycle.load_config(), baseline_path=tmp_path / "BASELINE.md",
              cycles_dir=tmp_path, decisions=[])
    studies = [_walk(tmp_path, e, b) for e, b in BUNDLES.items()]
    text, _ = cycle.compose(studies, review="ON", **kw)
    line = next(x for x in text.splitlines() if x.startswith("  - the review (spec 209"))
    assert line == (
        "  - the review (spec 209, keel-cloud 232, 233, 235, 236, 237): 3 founder rows changed and 3 put aside over 2 "
        "walks (each bundle's `lists_reviewed`) -- Importance 0 changed / 0 put aside, Current solution 3 changed / 0 "
        "put aside, Compatibility 0 changed / 0 put aside, Relative advantage 0 changed / 3 put aside (the hard case "
        "changed on 2 walks: the band's *... changed the moment the question asks about ...*, keel-cloud 237); 1 "
        "Current solution ladder rewritten whole as one scale (the band's *Keel rewrote the scale ...*, keel-cloud "
        "235); the longest hold on Save (each bundle's `review_holds`): Importance none, Current solution 30.1 s "
        "(21-codyco · SOLUTION), Compatibility none, Relative advantage 18.4 s (17-expanse · SOLUTION); the Check shot "
        "again after the band (keel-cloud 233, spec 144) on 3 screens (Relative advantage's, the fourth, on 2): "
        f"17-expanse · SOLUTION `check-{RA}-reviewed`, 21-codyco · SOLUTION `check-{CS}-reviewed`, 21-codyco · "
        f"SOLUTION `check-{RA}-reviewed`; the readers scored the screens as served, the second shots under their "
        "dimension")
    path = tmp_path / "20261108-7662026.md"
    path.write_text(text, encoding="utf-8")
    assert line in cycle.render_record(cycle.load_record(path)).splitlines()


def test_a_record_of_walks_before_147_reads_as_145_wrote_it():
    studies = [{"entry": "21-codyco", "scope": "PROBLEM", "review_rows": {"changed": 3, "put_aside": 0},
                "review_dims": cycle.review_dims({CS: _reviewed(LADDER)}), "review_shots": [], "review_scales": 1,
                "review_held": {}}]
    line = cycle.review_line({"review_switch": "ON", "studies": studies})[0]
    assert line.startswith("  - the review (spec 209, keel-cloud 232, 233, 235): ")
    assert "Relative advantage" not in line and "the fourth" not in line
