"""Spec 149 FR-5 -- a walk is *stopped early* only when it did not reach its end, and its stop is named; a refusal the
walk retried is never a stop (the gate line counts it, spec 148 FR-7).

Cycle 19 (`quality/cycles/20261109-76c633d.md`, committed, never rewritten) listed `08-fresco · PROBLEM` and
`17-expanse · PROBLEM` as *stopped early -- no step named (stopped outside a step)*. Their bundles
(`tests/fixtures/cycle19/`, the fields the record reads copied verbatim from `runs/<bundle>/backtest.json`, each file's
sha256 kept) say the walks did NOT reach their end: the last lap is `leg_interpret_problem` (no calibration screen, no
lock, no export), three refusals of Keel's AI at the PROBLEM calibration were retried (all `gate_refusals` `stopped:
false`, `failure_screens` three -- the walk's three retries spent), and the walk ended there. (The walks' own logs,
`runs/quality-walk/20261109T194106Z-20261109-76c633d/*-PROBLEM.backtest.log`, name the fourth refusal: E2, the event
over eight words -- raised by `_wait_calibration` outside any step, so no step was named.) So the re-read pins the
truth: **13 of 15 reached their end; the two stopped after `leg_interpret_problem`, a product stop past the retries**,
with **5** retried refusals on the gate line and no walk stopped by rule -- never *no step named*. (The spec's *15 of 15*
is not what the bundles say; see tasks.md.)

No stack, no model, no key.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

from evals import backtest as bt
from evals import corpus_scenario as cs
from quality import cycle, table

ROOT = Path(__file__).resolve().parents[1]
CYCLE_19 = ROOT / "quality/cycles/20261109-76c633d.md"
FIXTURES = ROOT / "tests/fixtures/cycle19"
BUNDLES = {"08-fresco · PROBLEM": "20261109T194118Z-backtest-08-fresco",
           "17-expanse · PROBLEM": "20261109T211406Z-backtest-17-expanse"}
UP_TO_PROBLEM = [{"leg": n, "seconds": 1.0} for n in ("leg_project", "teaching", "leg_context",
                                                       "leg_interpret_problem")]
E2_PAST_THE_RETRIES = ("PROBLEM's calibration questions FAILED: RESULT_INVALID: result.questions[0].event: E2: event "
                       "'found photos or notes missing from the daily log' is 9 words; at most 8 in the last 5 working "
                       "days")


def _bundle(name: str) -> dict:
    return json.loads((FIXTURES / f"{BUNDLES[name]}.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------ the rule, on one walk

def test_a_walk_that_reached_its_end_has_no_stop():
    """FR-5: a walk that passed, or whose last lap is an end (`END_LEGS`: the report, the export) -- even one that failed
    after it (spec 064's deferred golden readings) -- is never *stopped early*."""
    assert bt.walk_stop(passed=True, failed_step=None, legs=UP_TO_PROBLEM) is None
    ended = UP_TO_PROBLEM + [{"leg": "leg_calibrate PROBLEM"}, {"leg": "leg_lock"}, {"leg": "leg_scoped_report"},
                             {"leg": "export"}]
    assert bt.reached_end(False, ended) is True
    assert bt.walk_stop(passed=False, failed_step="spec 064: 1 golden reading(s) the build moved", legs=ended) is None
    assert bt.reached_end(False, UP_TO_PROBLEM) is False and bt.reached_end(False, []) is False


def test_a_stop_is_named_rule_product_or_harness():
    """FR-5: a gate rule past the repair turn (`stop_rule`) is a *rule* stop; Keel's AI refused past the retries (raised
    outside any step) a *product* stop, in the leg after the last lap; anything else the walk raised a *harness* stop."""
    rule = bt.walk_stop(passed=False, failed_step=None, legs=UP_TO_PROBLEM,
                        stop_rule={"rule": "E9", "refusal": "the no-sayer names no word of the hurt"},
                        ended_by=AssertionError("PROBLEM's calibration questions FAILED -- stopped by E9"))
    assert rule["kind"] == "rule" and rule["after"] == "leg_interpret_problem"
    product = bt.walk_stop(passed=False, failed_step=None, legs=UP_TO_PROBLEM,
                           ended_by=AssertionError(E2_PAST_THE_RETRIES))
    assert product == {"kind": "product", "step": None, "after": "leg_interpret_problem", "said": E2_PAST_THE_RETRIES}
    assert bt.stop_said(product) == f"after leg_interpret_problem -- a product stop: {E2_PAST_THE_RETRIES}"
    harness = bt.walk_stop(passed=False, failed_step="founder saves problem.importance: waits", legs=UP_TO_PROBLEM,
                           ended_by=TimeoutError("Timeout 30000ms exceeded"))
    assert harness["kind"] == "harness"
    assert bt.stop_said(harness).startswith("in founder saves problem.importance -- a harness stop: ")
    defect = bt.walk_stop(passed=False, failed_step=None, legs=UP_TO_PROBLEM,
                          ended_by=AssertionError("DEFECT (keel-cloud 233): held past 120 s"))
    assert defect["kind"] == "product"


def test_the_walk_hands_what_ended_it_to_the_record():
    """FR-5: `corpus_scenario.run` keeps the exception that ended a walk (`ended_by`) and hands it to `Backtest.finish`,
    which writes `reached_end` and `stop` -- so a stop raised outside any step is named in `backtest.json`."""
    run = inspect.getsource(cs.run)
    assert "except BaseException as stop:" in run and "ended_by = stop" in run
    assert "backtest.finish(journey, passed=passed, failed_step=recorder.failed_step, ended_by=ended_by)" in run
    finish = inspect.getsource(bt.Backtest.finish)
    assert 'record["reached_end"] = reached_end(passed, record["legs"])' in finish
    assert 'record["stop"] = stop' in finish


def test_backtest_md_says_where_and_why_the_walk_stopped():
    """FR-5: `backtest.md`'s run line -- *stopped after {leg} -- a product stop: ...* -- and a walk that reached its end
    and failed after it says so; a bundle before 149 reads as 148 wrote it."""
    stop = bt.walk_stop(passed=False, failed_step=None, legs=UP_TO_PROBLEM, ended_by=AssertionError(E2_PAST_THE_RETRIES))
    md = bt.markdown({"entry": {"id": "x"}, "run": "r", "passed": False, "failed_step": None, "reached_end": False,
                      "stop": stop})
    assert f"- Run: `r` -- stopped after leg_interpret_problem -- a product stop: {E2_PAST_THE_RETRIES}" in md
    md = bt.markdown({"entry": {"id": "x"}, "run": "r", "passed": False, "failed_step": "spec 064: golden",
                      "reached_end": True})
    assert "- Run: `r` -- walked to the end; failed at: spec 064: golden" in md
    md = bt.markdown({"entry": {"id": "x"}, "run": "r", "passed": False, "failed_step": None})
    assert "- Run: `r` -- stopped at: --" in md


# ---------------------------------------------------------------------------- cycle 19, re-read on its bundles

def test_the_two_bundles_did_not_reach_their_end_and_say_why():
    """FR-5 on the bundles' json: neither passed, no step was named, the last lap `leg_interpret_problem`, no founder
    screen past the problem card, three refusals retried each (all `gate_refusals` `stopped: false`) -- a product stop
    past the retries, inferred from what the bundle records (`stop_of_bundle`)."""
    refused = 0
    for name in BUNDLES:
        record = _bundle(name)
        assert record["passed"] is False and record["failed_step"] is None
        assert record["legs"][-1]["leg"] == "leg_interpret_problem"
        assert record["founder_screens"][-1]["screen"] == "problem-card"
        assert len(record["failure_screens"]) == bt.RETRIES == 3
        assert all(g["stopped"] is False for g in record["gate_refusals"])
        refused += len(record["gate_refusals"])
        stop = bt.stop_of_bundle(record)
        assert stop["kind"] == "product" and stop["after"] == "leg_interpret_problem" and stop["inferred"] is True
        assert stop["said"].startswith("3 refusals of Keel's AI retried (the walk's 3 retries spent), the last at "
                                       "failed-problem-calibration-RESULT_INVALID")
    assert refused == 5


def test_cycle_19_reread_names_both_stops_and_counts_five_refusals_on_the_gate_line():
    """FR-5: cycle 19's committed record re-read with the two bundles' stops -- 13 of 15 reached their end, the two named
    *after leg_interpret_problem -- a product stop: ...* (never *no step named*), and the gate line's 5 retried E7 / E9
    refusals with no walk stopped by rule. The committed record is never rewritten."""
    text = CYCLE_19.read_text(encoding="utf-8")
    assert ("13 of 15 walks reached their end; 2 stopped early (08-fresco · PROBLEM -- no step named (stopped outside a "
            "step); 17-expanse · PROBLEM -- no step named (stopped outside a step))") in text, "the record as committed"
    record = cycle.load_record(CYCLE_19)
    for s in record["studies"]:
        name = f"{s['entry']} · {s['scope']}"
        if name in BUNDLES:
            study = cycle.study_stop(cycle.Study(s["entry"], s["scope"]), _bundle(name))
            s.update(reached_end=study.reached_end, stop=study.stop)
    walks = cycle.walks_of(record, ROOT)
    assert (walks["walks"], walks["ended"]) == (15, 13)
    steps = {w["study"]: w["step"] for w in walks["stopped"]}
    assert set(steps) == set(BUNDLES)
    for step in steps.values():
        assert step.startswith("after leg_interpret_problem -- a product stop: 3 refusals of Keel's AI retried")
    line = table.walks_lines(walks)[0]
    assert "no step named" not in line and line.startswith("  - 13 of 15 walks reached their end; 2 stopped early")
    gate = cycle.gate_line(record)
    assert gate == ["  - the gate (keel-cloud 238, 239, 240, 241: the round's mirrors, spec 148): 5 E7 / E9 refusals of "
                    "Keel's AI over 15 walks (each bundle's `gate_refusals`, retried as the founder's screen retries); no "
                    "walk stopped by rule"]
    assert sum(int(s.get("gate_refused") or 0) for s in record["studies"]) == 5


def test_a_record_before_149_reads_as_it_was_written():
    """FR-5: a study with no `reached_end` reads as before -- stopped where it did not pass, *no step named* where none."""
    record = {"studies": [{"entry": "a", "scope": "PROBLEM", "bundle": "b", "passed": False, "failed_step": None},
                          {"entry": "c", "scope": "PROBLEM", "bundle": "d", "passed": True}]}
    walks = cycle.walks_of(record)
    assert walks["ended"] == 1 and walks["stopped"] == [{"study": "a · PROBLEM",
                                                        "step": "no step named (stopped outside a step)"}]
    data = cycle._study_data(cycle.Study("a", "PROBLEM"))
    assert "reached_end" not in data and "stop" not in data
