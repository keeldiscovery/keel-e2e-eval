"""Spec 149 FR-6 -- the record: on a record of 149's walks the review line cites keel-cloud 243 and counts Keel's rows
*suggested in place* (each bundle's `lists_reviewed[dim].in_place`) beside the rows changed and put aside, per dimension
and in all; a record of walks before 149 reads as 148 wrote it.

No model, no stack, no network: fixture bundles (`backtest.json`) through `walk_one` with a fake runner, composed and
rendered -- the lists are keel-cloud 243's invented studies as the mirror applies them.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from evals import backtest as bt
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from quality import cycle
from tests.test_check_pattern_184_149 import COMPAT_SAVED, staging_saved

IMP, COMPAT = "problem.importance", "solution.compatibility"
FOUR = list(vs_screens.REVIEWED_LISTS)


def _lists(dimension: str, saved: dict) -> dict:
    return vs.lists_reviewed({"V": {"questions": [{"dimension": dimension, "answer": {"list": saved}}]}})


#: Two walks of 149's (they record `reached_end`): the staging shape on Importance (three put aside, three in place), and
#: Compatibility's every kind (two changed, one put aside, one in place).
BUNDLES = {
    "08-fresco": {"scope": "PROBLEM", "lists_reviewed": _lists(IMP, staging_saved()),
                  "founder_screens": [{"screen": f"check-{IMP}"}, {"screen": f"check-{IMP}-reviewed"}],
                  "review_holds": {IMP: {"review": "r1", "held": True, "held_s": 9.5, "outcome": "stayed"}}},
    "17-expanse": {"scope": "SOLUTION", "lists_reviewed": _lists(COMPAT, COMPAT_SAVED),
                   "founder_screens": [{"screen": f"check-{COMPAT}-reviewed"}],
                   "review_holds": {COMPAT: {"review": "r2", "held": True, "held_s": 6.0, "outcome": "stayed"}}},
}


def _walk(tmp_path, entry: str, bundle: dict, *, of_149: bool = True) -> cycle.Study:
    runs = tmp_path / "runs"
    scope = bundle["scope"]

    def fake(argv, stdout=None, stderr=None):
        if argv[4] == "backtest":
            run = runs / f"20261110T100000Z-backtest-{entry}"
            run.mkdir(parents=True)
            extra = {"reached_end": True, "gate_refusals": []} if of_149 else {"gate_refusals": []}
            (run / bt.RECORD).write_text(json.dumps({"run": run.name, "passed": True, "review_switch": "ON",
                                                     "reviewed_lists": FOUR, **extra, **bundle}))
            stdout.write(f"run bundle: {run}\n")
        return SimpleNamespace(returncode=0)

    steps = [s for s in cycle.plan_steps([entry], [scope], "keel", tmp_path / "work" / entry) if s["study"]]
    return cycle.walk_one(entry, scope, steps, door="keel", runner=fake, runs_dir=runs)


def test_a_walk_of_149_counts_keels_rows_in_place_per_dimension(tmp_path):
    """FR-6: `review_in_place` off the bundle's `lists_reviewed` -- set only on a bundle of 149's walk."""
    fresco, expanse = (_walk(tmp_path, e, b) for e, b in BUNDLES.items())
    assert fresco.review_in_place[IMP] == 3 and expanse.review_in_place[COMPAT] == 1
    assert fresco.review_dims[IMP] == {"changed": 0, "put_aside": 3}
    assert expanse.review_dims[COMPAT] == {"changed": 2, "put_aside": 1}
    assert fresco.reached_end is True and fresco.stop is None
    before = _walk(tmp_path / "before", "08-fresco", BUNDLES["08-fresco"], of_149=False)
    assert before.review_in_place is None and "review_in_place" not in cycle._study_data(before)


def test_the_review_line_cites_243_and_counts_suggested_in_place(tmp_path):
    """FR-6: the review line on a record of 149's walks."""
    kw = dict(name="20261110-c87d106", why="spec 149", door="keel", cloud_sha="c87d106", web_sha="82a746d",
              started="s", ended="e", seconds=1.0, cfg=cycle.load_config(), baseline_path=tmp_path / "BASELINE.md",
              cycles_dir=tmp_path, decisions=[])
    studies = [_walk(tmp_path, e, b) for e, b in BUNDLES.items()]
    text, _ = cycle.compose(studies, review="ON", **kw)
    line = next(x for x in text.splitlines() if x.startswith("  - the review (spec 209"))
    assert line.startswith(
        "  - the review (spec 209, keel-cloud 232, 233, 235, 236, 237, 238, 239, 240, 241, 243): 2 founder rows "
        "changed, 4 put aside and 4 suggested in place (keel-cloud 243) over 2 walks (each bundle's `lists_reviewed`) "
        "-- Importance 0 changed / 3 put aside / 3 suggested in place, Current solution 0 changed / 0 put aside / 0 "
        "suggested in place, Compatibility 2 changed / 1 put aside / 1 suggested in place, Relative advantage 0 "
        "changed / 0 put aside / 0 suggested in place (the hard case changed on 0 walks")
    path = tmp_path / "20261110-c87d106.md"
    path.write_text(text, encoding="utf-8")
    assert line in cycle.render_record(cycle.load_record(path)).splitlines()


def test_a_record_of_148s_walks_reads_as_148_wrote_it(tmp_path):
    """FR-6: no `reached_end` on the bundles -- no in-place count, round A's citation, the head as before."""
    kw = dict(name="20261109-76c633d", why="spec 148", door="keel", cloud_sha="76c633d", web_sha="36d069e",
              started="s", ended="e", seconds=1.0, cfg=cycle.load_config(), baseline_path=tmp_path / "BASELINE.md",
              cycles_dir=tmp_path, decisions=[])
    studies = [_walk(tmp_path, e, b, of_149=False) for e, b in BUNDLES.items()]
    text, _ = cycle.compose(studies, review="ON", **kw)
    line = next(x for x in text.splitlines() if x.startswith("  - the review (spec 209"))
    assert line.startswith(f"  - the review {cycle.ROUND_A_CITED}: 2 founder rows changed and 4 put aside over 2 walks")
    assert "suggested in place" not in line
