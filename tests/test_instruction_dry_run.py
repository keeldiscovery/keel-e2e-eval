"""`make instruction-eval DRY=1` at `MARKS_VERSION` 9 (spec 029 research R7, judgement call 34; T026).

The dry run spends nothing and, at v9, measures one mark for real: `COMPARE` is keel-cloud's engine
and needs no model. So the dry run writes a bundle -- a scorecard and a verdict -- with
`compare_correctness` measured and every model-scored mark **unmeasured**, `passed: false`, and the
reason in words. Here the export, the templates and the engine are fixtures (a fake `gradlew` that
answers with the agreeing output); nothing is called and nothing is spent.
"""

from __future__ import annotations

import json
import stat
import types

import pytest

from instructions import corpus as corpus_mod
from instructions import run as run_mod
from tests import v9_fixtures as fx


def _checkout(tmp_path, *, engine_ok=True):
    checkout = tmp_path / "keel-cloud"
    checkout.mkdir()
    gradlew = checkout / "gradlew"
    agree = fx.COMPARE / "09-fixture.agree.out.json"
    gradlew.write_text("#!/bin/sh\n" + (f'cp "{agree}" "$(echo "$3" | sed \'s/^.* //\')"\n'
                                         if engine_ok else "echo 'no compare' >&2\nexit 1\n"))
    gradlew.chmod(gradlew.stat().st_mode | stat.S_IEXEC)
    return checkout


@pytest.fixture()
def dry(tmp_path, monkeypatch):
    def go(*, needle="09-fixture", engine_ok=True, instructions=None):
        checkout = _checkout(tmp_path, engine_ok=engine_ok)
        bundle = tmp_path / "bundle"
        bundle.mkdir(exist_ok=True)
        monkeypatch.setattr(run_mod.report_mod, "start_bundle", lambda *a, **k: bundle)
        monkeypatch.setattr(run_mod.contract_mod, "export",
                            lambda keel_cloud, into: fx.exported(tmp_path / "x"))
        monkeypatch.setattr(run_mod, "_instructions_for",
                            lambda config: instructions or fx.instructions())
        corpus = corpus_mod.Corpus(entries=[corpus_mod.load_file(fx.ENTRY)],
                                   directory=fx.ENTRY.parent)
        args = types.SimpleNamespace(baseline=False, host="claude", filter=needle, n_runs=1,
                                     marks=None, models=None, no_judge=False)
        code = run_mod._dry_run(types.SimpleNamespace(keel_cloud=checkout), corpus,
                                fx.FakeRuntime, {"cli": "claude"}, args)
        return code, bundle
    return go


def test_a_dry_run_measures_compare_and_nothing_else_and_never_passes(dry, capsys):
    code, bundle = dry()
    out = capsys.readouterr().out
    assert code == 0
    scorecard = json.loads((bundle / "scorecard.json").read_text())
    verdict = json.loads((bundle / "verdict.json").read_text())
    assert scorecard["totals"]["compare_correctness"] == 1.0
    entry = corpus_mod.load_file(fx.ENTRY)
    assert scorecard["totals"]["compare_checks"] == \
        len(entry.calibrated_keys()) + len(entry.expected["vector_verdicts"])
    assert verdict["passed"] is False and verdict["dry_run"] is True
    marks = verdict["marks"]
    assert marks["compare_correctness"]["measured"] and marks["compare_correctness"]["met"]
    for name in ("dimension_coverage", "option_validity", "no_leak", "anchoring_accuracy",
                 "refusals", "shape_refusals", "brief_paragraphs"):
        assert marks[name]["measured"] is False, name
    assert "19 cases" in out and "1 COMPARE row" in out
    assert "nothing was called and nothing was spent" in out
    assert (bundle / "compare" / "09-fixture.in.json").is_file()


def test_a_dry_run_prints_one_prompt_per_kind(dry, capsys):
    dry()
    out = capsys.readouterr().out
    for case_id in ("09-fixture/CONTEXT_INTERPRET/run1", "09-fixture/PROBLEM_INTERPRET/run1",
                    "09-fixture/CALIBRATION_PROBLEM/run1", "09-fixture/RESPONDENT_PART1/run1",
                    "09-fixture/BRIEF/run1"):
        assert case_id in out, case_id
    assert "09-fixture/SOLUTION_MECHANISM/run1   (" not in out, "FRAME is printed once"


def test_an_engine_that_cannot_be_asked_is_unmeasured_by_name_in_the_dry_verdict(dry):
    _code, bundle = dry(engine_ok=False)
    verdict = json.loads((bundle / "verdict.json").read_text())
    assert verdict["marks"]["compare_correctness"]["measured"] is False
    assert any("058" in reason for reason in verdict["unmet_prerequisites"])


def test_a_needle_matching_nothing_says_so_and_spends_nothing(dry, capsys):
    code, bundle = dry(needle="no-such-entry")
    assert code == 2
    assert "no case matches" in capsys.readouterr().out
    assert not (bundle / "scorecard.json").exists()


def test_a_compare_only_needle_runs_before_any_template_exists(dry):
    none = {screen: None for screen in run_mod.SCREENS}
    code, bundle = dry(needle="compare", instructions=none)
    assert code == 0
    assert json.loads((bundle / "scorecard.json").read_text())["totals"]["compare_measured"]


def test_a_selected_screen_without_its_template_is_refused_by_name(dry, capsys):
    none = {screen: None for screen in run_mod.SCREENS}
    code, _bundle = dry(needle="09-fixture/CALIBRATION", instructions=none)
    assert code == 2
    err = capsys.readouterr().err
    assert "CALIBRATION_QUESTIONS" in err and "calibration-questions.md" in err


def test_a_dry_run_prints_every_structural_marks_denominator_read_off_the_registry(dry, capsys):
    """Spec 030 US3, call 47; spec 031 calls 52-55; spec 032 call 61: no answer exists to score, so the three
    structural marks stay unmeasured (call 13) -- but the denominator each would be counted over
    is read off the registry and the entry and written down: calibration 4 / 3 / 4 (B2C),
    respondent 4 / 3 / 3 (the founder left one out), sweep A on the 3 PROBLEM questions and the 3
    Part 1 items with model text (Frequency is framed on 7 nights), sweep B on every item but
    framed Frequency and Price -- and the names W3 / W8 are held to (none, at r5)."""
    code, bundle = dry()
    assert code == 0
    scorecard = json.loads((bundle / "scorecard.json").read_text())
    entry = corpus_mod.load_file(fx.ENTRY, registry=fx.registry())
    plan = entry.plan()
    assert scorecard["denominators"] == {"09-fixture": {
        "calibration": len(fx.registry().answered(False)),      # call 61: less the derived one
        "respondent": {"PRIMARY": sum(len(keys) for keys in plan.values())},
        "sweep_a": (len(fx.registry().calibrated_slice("PROBLEM", False)) - 1)
        + (len(plan[1]) - 1),
        "sweep_b": sum(len(keys) for keys in plan.values()) - 2,
        "short_name": None, "offer_name": None}}
    out = capsys.readouterr().out
    assert "denominators read off the registry, per N: dimension_coverage 11 calibration + 10 " \
           "respondent" in out
    assert "W3 held to no name · W8 held to no name" in out
