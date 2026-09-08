"""Every module in `instructions/` imports, and the two HTML pages render (spec 009 FR-018).

Trivial, and it earned its place immediately: an unterminated string in `report.py`'s
`register.html` CSS survived a green `make unit` and killed a run at import — after the pre-flight
had already probed the model, and one keystroke before 124 paid calls. Nothing under `tests/`
imported `instructions.report` at all, so nothing could have caught it.

These are smoke tests on purpose. They assert that the code parses, that a report and a register
render from a minimal scorecard without raising, and that the pages say the things a reader must
never be without — the model, the marks version, and what is not being measured.
"""

from __future__ import annotations

import importlib

import pytest

MODULES = ["align", "brief", "context", "contract", "corpus", "instruction", "judge", "marks",
           "prompts", "report", "rescore", "run", "runner", "score", "validate"]


@pytest.mark.parametrize("name", MODULES)
def test_every_instruction_module_imports(name):
    importlib.import_module(f"instructions.{name}")


_SCORECARD = {
    "marks_version": 4,
    "model": {"claude_version": "2.1.263", "reported_model": "a-model",
              "job_timeout_seconds": 300.0, "job_max_turns": 6, "job_budget_usd": 1.0,
              "judge": "on"},
    "contract_manifest": {"keel_cloud_commit": "abc1234", "keel_cloud_dirty": False,
                          "generated_at": "2026-09-06T00:00:00Z"},
    "reading": [], "assumptions": [], "brief": [], "prompts": [],
    "spread": {"recall": {}, "anchoring": {}},
    "totals": {
        "anchoring_accuracy": 0.95, "guessed_precision": 0.8, "guessed_recall": 1.0,
        "confusion": {"aa": 1, "ag": 0, "ga": 0, "gg": 1},
        "anchors_given": 2, "anchors_answered": 2, "reading_missing_ids": 0, "reading_extra_ids": 0,
        "golden_belief_recall": 0.5, "golden_beliefs": 2, "matched_beliefs": 1,
        "exact_match": {"type": 1.0, "kind": None, "unit": None, "per": None,
                        "expected_or_band": 1.0, "risk": 1.0, "mark": 1.0, "founder_phrase": None},
        "exact_match_counts": {k: {"agreed": 1, "applicable": 1} for k in
                               ("type", "kind", "unit", "per", "expected_or_band", "risk", "mark",
                                "founder_phrase")},
        "phrase_band": {"phrase_band": 1, "phrase_only": 0, "band_only": 0, "neither": 0},
        "extra_beliefs": 0, "needs_input_cases": 0, "judged_fraction": 0.0, "judged_pairs": 0,
        "judged_candidacy_pairs": 0, "judged_any_fraction": 0.0, "judge_calls": 0,
        "refusals_by_rule": {}, "refusals_measured": True, "shape_refusals": 0,
        "schema_invalid": 0, "errored": 0,
        "brief_cases": 1, "brief_paragraphs": 1.0, "brief_needs_input": 0, "brief_measured": True,
        "brief_by_mark": {n: {"met": 1, "of": 1} for n in
                          ("shape", "coverage", "register", "source_material")},
    },
}


def test_the_report_renders_and_never_omits_what_it_cannot_measure(tmp_path):
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
    assert "register is not scored" in html
    assert "option list leads is not scored" in html
    assert "Wording is free" in html
    # MARKS_VERSION 4: the BRIEF subject's own section, and the deviation it must always name.
    assert "What this says (the BRIEF screen)" in html
    assert "Measure.say" in html, "the one field this subject does not send as production sends it"


def test_the_register_carries_every_brief_paragraph_whole_and_unscored(tmp_path):
    from instructions import report as report_mod

    paragraphs = {"GB · en-GB": {"01-countly": {
        "title": "Countly", "paragraph": "Your problem claim is not holding up.",
        "stages": {"PROBLEM": "CONTRADICTED"},
        "standings": {"P1": {"verdict": "SUPPORTED", "drift": "NONE", "inside": 9, "outside": 0}}}}}

    path = report_mod.render_register(tmp_path, entries_by_market={}, paragraphs=paragraphs)
    html = path.read_text(encoding="utf-8")

    assert "Your problem claim is not holding up." in html
    assert "Nothing here is scored" in html
    assert "PROBLEM CONTRADICTED" in html


def test_the_register_renders_and_says_that_nothing_on_it_is_scored(tmp_path):
    from instructions import report as report_mod

    blocks = {"GB · en-GB": {"01-countly": {"PROBLEM": {
        "produced": [{"id": "A1", "prompt": "Think of the last delivery.", "selections": [
            {"id": "S1", "prompt": "Who took it in?", "control": "OPTIONS",
             "options": ["me", "a member of staff"], "escape": ["can't recall"]}]}],
        "golden": [{"id": "A1", "prompt": "Think of the last delivery.", "selections": []}]}}}}

    path = report_mod.render_register(tmp_path, entries_by_market=blocks)
    html = path.read_text(encoding="utf-8")

    assert "Nothing on this page is scored" in html
    assert "a member of staff" in html
    assert "GB · en-GB" in html
