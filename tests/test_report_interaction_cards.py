"""T017: report.html renders exactly one card per scored interaction, and an agent_turn's card
shows the conversation (screen state / agent reply / outcome) as prose, not a raw JSON blob (which
stays available, collapsed, per scorecard-contract.md).

spec 005-connect-stack FR-006/FR-013: `finalize_run` takes a plain `slug` + `facts` dict now,
never a `Scenario` object (`evals/scenario.py` is retired) -- and the fixture below uses the
current interaction kinds (`agent_turn`, `arrival`, `ui_visit`), not the retired agent-protocol
ones.
"""

from __future__ import annotations

import json

from harness.evidence import finalize_run
from harness.steps import Recorder


def _build_bundle(run_dir):
    recorder = Recorder(run_dir)
    with recorder.interaction("arrival"):
        with recorder.step("founder arrives", party="founder", kind="browser") as h:
            h.capture_text("arrival_display", "Welcome back to Payroll Exceptions.")

    with recorder.interaction("agent_turn"):
        with recorder.step("the agent answers the problem framing", party="agent", kind="browser") as h:
            h.capture_text("chat_state", "Reading what you wrote...")
            h.capture_text("agent_reply", "Here's what we understood: Payroll managers lose "
                                           "hours chasing exceptions.")
            h.capture_text("agent_turn_outcome", "COMPLETED")

    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            h.capture_text("identity", "p1")
            h.capture_text("stage_identity", "THE PROBLEM")
            h.capture_text("stage_screen", "THE PROBLEM\nPayroll managers lose hours chasing exceptions.")
            shot = recorder.next_screenshot_name("stage")
            recorder.screenshot_path(shot).write_bytes(b"\x89PNG\r\n\x1a\nfake")
            h.add_screenshot(shot)
    return recorder


def test_report_has_exactly_one_card_per_scorecard_interaction(tmp_path):
    _build_bundle(tmp_path)
    finalize_run(tmp_path, slug="fixture-report", passed=True, failed_step=None, duration_s=1.0)

    scorecard = json.loads((tmp_path / "scorecard.json").read_text())
    report = (tmp_path / "report.html").read_text()

    for entry in scorecard["interactions"]:
        assert entry["title"] in report, f"no card found for interaction {entry['id']} ({entry['title']!r})"
    # Every interaction's card links back to its own raw steps -- a proxy for "one card each"
    # beyond just "the title string appears somewhere".
    assert report.count("raw steps:") == len(scorecard["interactions"])


def test_agent_turn_card_shows_prose_not_raw_json(tmp_path):
    _build_bundle(tmp_path)
    finalize_run(tmp_path, slug="fixture-report", passed=True, failed_step=None, duration_s=1.0)
    report = (tmp_path / "report.html").read_text()

    assert "Reading what you wrote" in report
    assert "Here&#x27;s what we understood" in report or "Here's what we understood" in report
    # The arrival's own conversation card shows its greeting as prose.
    assert "Welcome back to Payroll Exceptions" in report
    # Raw JSON is still there, but inside a collapsible <details> block, not inline prose.
    assert "<details>" in report
