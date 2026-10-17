"""`make instruction-eval DRY=1` at `MARKS_VERSION` 18 (spec 029 research R7, judgement call 34; T026; spec 040,
calls 79 and 82).

The dry run spends nothing and measures the three deterministic marks for real: `COMPARE` is keel-cloud's engine,
and `spoken_form` / `brief_facts` read keel-cloud's corpus tests' files -- none needs a model. So the dry run writes
a bundle -- a scorecard and a verdict -- with those three measured and every model-scored mark **unmeasured**,
`passed: false`, and the reason in words. Here the export, the templates, the engine and the corpus tests are
fixtures (a fake `gradlew` that answers `screenContracts compare` with the agreeing output and `test` by writing the
two files); nothing is called and nothing is spent.
"""

from __future__ import annotations

import json
import stat
import types

import pytest

from instructions import corpus as corpus_mod
from instructions import run as run_mod
from tests import v9_fixtures as fx


#: One composed item the fixture entry's Commitment would be, in `build/spoken-corpus.txt`'s own lines.
SPOKEN = """
== 09-fixture
commercial.commitment [part 3]
  Q: If it were ready today, would you install the app, or not?
  options: [Yes, I'd start one, Yes, after trying it first, Probably not, No]
  escape: null
  spoken: anchor=null | stem=If it were ready today, would you install the app, or not? | count=I'll read four options. | options=Yes, you'd start one; yes, after trying it first; probably not; or no. | escape=null | transform=none
"""


def _checkout(tmp_path, *, engine_ok=True, cloud_ok=True):
    from instructions import brief_facts as bf                              # noqa: PLC0415
    checkout = tmp_path / "keel-cloud"
    checkout.mkdir()
    (checkout / "spoken.txt").write_text(SPOKEN)
    (checkout / "facts.json").write_text(json.dumps(bf.facts_for(fx.entry(), fx.registry())))
    gradlew = checkout / "gradlew"
    agree = fx.COMPARE / "09-fixture.agree.out.json"
    test = ('if [ "$2" = "test" ]; then mkdir -p build/brief-facts && cp spoken.txt build/spoken-corpus.txt '
            '&& cp facts.json build/brief-facts/09-fixture.json; exit 0; fi\n') if cloud_ok else \
        'if [ "$2" = "test" ]; then echo "tests failed" >&2; exit 1; fi\n'
    gradlew.write_text("#!/bin/sh\ncd \"$(dirname \"$0\")\"\n" + test
                       + (f'cp "{agree}" "$(echo "$3" | sed \'s/^.* //\')"\n'
                          if engine_ok else "echo 'no compare' >&2\nexit 1\n"))
    gradlew.chmod(gradlew.stat().st_mode | stat.S_IEXEC)
    return checkout


@pytest.fixture()
def dry(tmp_path, monkeypatch):
    def go(*, needle="09-fixture", engine_ok=True, cloud_ok=True, instructions=None):
        checkout = _checkout(tmp_path, engine_ok=engine_ok, cloud_ok=cloud_ok)
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


def test_a_dry_run_measures_the_four_deterministic_marks_and_never_passes(dry, capsys):
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
    for name in ("compare_correctness", "spoken_form", "brief_facts", "report_overview"):
        assert marks[name]["measured"] and marks[name]["met"], name
    for name in ("dimension_coverage", "option_validity", "no_leak", "anchoring_accuracy",
                 "refusals", "shape_refusals"):
        assert marks[name]["measured"] is False, name
    assert "brief_answers" not in marks, "retired at v20 (call 116)"
    assert scorecard["totals"]["brief_facts_checks"] == 14, "twelve cards, the pilot and the price median"
    assert scorecard["totals"]["report_overview_checks"] == 7, "the hero, two tiles, three panels, the foot"
    assert scorecard["totals"]["spoken_units"] == 4, "one composed item and the entry's three faces"
    assert "20 cases" in out and "2 asked" in out and "1 COMPARE row" in out
    assert "spoken_form: 4 of 4" in out and "brief_facts: 14 of 14" in out and "report_overview: 7 of 7" in out
    assert (bundle / "cloud-corpus" / "spoken-corpus.txt").is_file(), "kept in the bundle for a re-score"
    assert "nothing was called and nothing was spent" in out
    assert (bundle / "compare" / "09-fixture.in.json").is_file()


def test_a_dry_run_prints_one_prompt_per_kind(dry, capsys):
    dry()
    out = capsys.readouterr().out
    for case_id in ("09-fixture/CONTEXT_INTERPRET/run1", "09-fixture/PROBLEM_INTERPRET/run1",
                    "09-fixture/CALIBRATION_PROBLEM/run1", "09-fixture/ASKED_COMPATIBILITY/run1",
                    "09-fixture/RESPONDENT_PART1/run1"):
        assert case_id in out, case_id
    assert "09-fixture/BRIEF" not in out, "no BRIEF case since keel-cloud 104 (call 116)"
    assert "09-fixture/SOLUTION_MECHANISM/run1   (" not in out, "FRAME is printed once"


def test_an_engine_that_cannot_be_asked_is_unmeasured_by_name_in_the_dry_verdict(dry):
    _code, bundle = dry(engine_ok=False)
    verdict = json.loads((bundle / "verdict.json").read_text())
    assert verdict["marks"]["compare_correctness"]["measured"] is False
    assert any("058" in reason for reason in verdict["unmet_prerequisites"])


def test_corpus_tests_that_cannot_run_leave_spoken_form_and_brief_facts_unmeasured_by_name(dry, capsys):
    _code, bundle = dry(cloud_ok=False)
    verdict = json.loads((bundle / "verdict.json").read_text())
    for name in ("spoken_form", "brief_facts"):
        assert verdict["marks"][name]["measured"] is False, name
    assert any("SpokenGuidelinesCorpusTest" in reason for reason in verdict["unmet_prerequisites"])
    assert verdict["marks"]["compare_correctness"]["met"], "the engine is asked all the same"
    out = capsys.readouterr().out
    assert "spoken_form: NOT measured" in out and "brief_facts: NOT measured" in out


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
    assert "CALIBRATION_QUESTIONS" in err and "founder-lists.md" in err


def test_a_dry_run_prints_every_structural_marks_denominator_read_off_the_registry(dry, capsys):
    """Spec 030 US3, call 47; spec 040 calls 83-85: no answer exists to score, so the three structural marks stay
    unmeasured (call 13) -- but the denominator each would be counted over is read off the registry and the entry
    and written down: coverage 4 / 3 / 4 calibration (B2C, less the derived one), 4 / 3 / 3 respondent (the founder
    left one out) and 3 asked faces (two conditions, one effort); validity one a calibration dimension, one a face
    and the gate alone on the respondent side; sweep A on the PROBLEM job's three written entries (Prevalence and
    the two lists) and the gate's clause, sweep B on the gate's clause."""
    code, bundle = dry()
    assert code == 0
    scorecard = json.loads((bundle / "scorecard.json").read_text())
    entry = corpus_mod.load_file(fx.ENTRY, registry=fx.registry())
    plan = entry.plan()
    calibration = len(fx.registry().answered(False))           # call 61: less the derived one
    assert scorecard["denominators"] == {"09-fixture": {
        "calibration": calibration,
        "respondent": {"PRIMARY": sum(len(keys) for keys in plan.values())},
        "asked": 3, "validity": calibration + 3 + 1,
        "sweep_a": 3 + 1, "sweep_b": 1}}
    out = capsys.readouterr().out
    assert "denominators read off the registry, per N: dimension_coverage 11 calibration + 10 " \
           "respondent + 3 asked · option_validity 15 · no_leak 5 sweeps" in out
