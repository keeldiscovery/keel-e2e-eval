"""Every module in `instructions/` imports, and the two HTML pages render (spec 009 FR-018; spec 029
T017, T058).

Trivial, and it earned its place immediately: an unterminated string in `report.py`'s
`register.html` CSS survived a green `make unit` and killed a run at import -- after the pre-flight
had already probed the model, and one keystroke before 124 paid calls. Nothing under `tests/`
imported `instructions.report` at all, so nothing could have caught it.

At `MARKS_VERSION` 9 the map moved (research R15): `align` retired with the subject it aligned
(judgement call 29); `compare`, `registry` and `text` joined. The scorecard below is the v9 totals
shape of data-model §6, made by `score.totals` itself so it can never drift from what a run writes.
"""

from __future__ import annotations

import importlib
import types

import pytest

from instructions import score as score_mod

MODULES = ["brief", "compare", "context", "contract", "corpus", "instruction", "judge", "marks",
           "models", "prompts", "registry", "report", "rescore", "run", "runner", "score", "text",
           "validate", "why"]


@pytest.mark.parametrize("name", MODULES)
def test_every_instruction_module_imports(name):
    importlib.import_module(f"instructions.{name}")


def test_align_is_retired():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("instructions.align")


def _question(entry, subject, hit, of, valid, written, clean, swept):
    return types.SimpleNamespace(entry_id=entry, subject=subject, coverage_hit=hit, coverage_of=of,
                                 validity_hit=valid, validity_of=written, leak_clean=clean,
                                 leak_of=swept, leak_hits=0, leak_judged=0)


def _totals(*, compare_measured=True) -> dict:
    compare = types.SimpleNamespace(entry_id="03-lullaby", checks=28, agreed=28,
                                    reported_diffs=[], measured=compare_measured,
                                    reason=None if compare_measured else "no engine")
    reading = types.SimpleNamespace(given=1, answered=1, agreed=1,
                                    confusion={"aa": 1, "ag": 0, "ga": 0, "gg": 0},
                                    missing_ids=[], extra_ids=[], shape_fault=0)
    return score_mod.totals(
        [_question("03-lullaby", "PROBLEM", 9, 9, 9, 9, 9, 9)],
        [_question("03-lullaby", "PART1", 8, 8, 8, 8, 16, 16)],
        [reading], [compare], refusals_by_rule={}, refusals_measured=True, refusals_shown=12)


_SCORECARD = {
    "marks_version": 9,
    "model": {"host": "claude", "cli": "claude", "cli_version": "2.1.284",
              "pinned_model": None, "reported_model": "a-model",
              "job_timeout_seconds": 300.0, "job_max_turns": 6, "job_budget_usd": 1.0,
              "max_ai_credits": None, "judge": "on", "judge_host": "claude"},
    "contract_manifest": {"keel_cloud_commit": "abc1234", "keel_cloud_dirty": False,
                          "generated_at": "2026-10-07T00:00:00Z"},
    "registry_version": 1,
    "compare": [], "calibration": [], "respondent": [], "interpret": [], "brief": [],
    "prompts": [], "spread": {},
    "totals": _totals(),
}


def test_the_report_renders_the_eight_marks_and_what_it_cannot_measure(tmp_path):
    from instructions import marks as marks_mod
    from instructions import report as report_mod

    verdict = {"scenario": "instructions", "baseline": False, "n_runs": 1, "cases": 2,
               "errored": 0, "duration_s": 1.0, "total_cost_usd": 0.1,
               "marks": marks_mod.judge(_SCORECARD["totals"], marks_mod.load())}
    path = report_mod.render_report(tmp_path, verdict=verdict, scorecard=_SCORECARD,
                                    versions={"keel-cloud": {"commit": "abc", "dirty": False}})
    html = path.read_text(encoding="utf-8")

    assert f"MARKS_VERSION {marks_mod.MARKS_VERSION}" in html
    assert "a-model" in html, "a run must always name the model it was judged under"
    assert "300.0s" in html, "and the wall clock it ran production's own"
    for label in ("dimension coverage", "option validity", "no leak", "anchoring accuracy",
                  "compare correctness", "rule refusals", "shape refusals", "BRIEF paragraphs"):
        assert label in html, label
    assert "golden-belief recall" not in html, "retired at v9 (call 29)"
    assert "register is not scored" in html
    assert "rendered, never scored" in html
    assert "28 of 28" in html


def test_a_scorecard_with_one_unmeasured_mark_says_so_in_words(tmp_path):
    from instructions import marks as marks_mod
    from instructions import report as report_mod

    scorecard = dict(_SCORECARD, totals=_totals(compare_measured=False))
    verdict = {"scenario": "instructions", "n_runs": 1, "cases": 2, "errored": 0,
               "duration_s": 1.0, "total_cost_usd": 0.0,
               "marks": marks_mod.judge(scorecard["totals"], marks_mod.load())}
    html = report_mod.render_report(tmp_path, verdict=verdict, scorecard=scorecard,
                                    versions={}).read_text(encoding="utf-8")
    assert "NOT measured" in html
    assert "no engine" in html, "the reason the engine was not asked is on the page"
    assert verdict["marks"]["passed"] is False


def test_the_register_renders_a_compare_only_bundle_and_says_nothing_on_it_is_scored(tmp_path):
    from instructions import report as report_mod

    path = report_mod.render_register(tmp_path, entries_by_market={}, paragraphs={})
    html = path.read_text(encoding="utf-8")
    assert "Nothing on this page is scored" in html


def test_the_register_carries_every_brief_paragraph_whole_beside_the_standings(tmp_path):
    from instructions import report as report_mod

    paragraphs = {"GB · en-GB": {"03-lullaby": {
        "title": "Lullaby", "paragraph": "Your problem is not holding up on how long it takes.",
        "verdicts": {"PROBLEM": "NOT_HOLDING_UP"},
        "vector_verdicts": {"PROBLEM": {"verdict": "NOT_HOLDING_UP",
                                        "deciding": "problem.duration"}},
        "standings": {"problem.duration": {"status": "NOT_HOLDING_UP", "drift": "below",
                                           "n": 7, "median": 11}}}}}
    html = report_mod.render_register(tmp_path, entries_by_market={},
                                      paragraphs=paragraphs).read_text(encoding="utf-8")
    assert "Your problem is not holding up on how long it takes." in html
    assert "problem.duration" in html and "NOT_HOLDING_UP" in html
