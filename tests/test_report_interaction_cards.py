"""T017: report.html renders exactly one card per scored interaction, and an agent-cycle's card
shows the conversation (instruction/requirements/outcome) as prose, not the raw JSON blob (which
stays available, collapsed, per scorecard-contract.md)."""

from __future__ import annotations

import json

from evals.scenario import Scenario
from harness.evidence import finalize_run
from harness.steps import Recorder


class _FixtureScenario(Scenario):
    slug = "fixture-report"

    def facts(self):
        return {}


def _build_bundle(run_dir):
    recorder = Recorder(run_dir)
    with recorder.interaction("agent-cycle"):
        with recorder.step("get_next (before any project)", party="agent", kind="protocol") as h:
            h.record_wire({"path": "/v2/agent/next"}, {"status": 200, "body": {
                "kind": "action", "action": "CREATE", "token": "t1",
                "requirements": ["the problem, in the founder's own words"],
                "instruction": {"purpose": "State the problem, not the solution.",
                                "content": "Write it plainly, in the founder's words."},
                "context": [], "detail": {},
            }})
        with recorder.step("submit CREATE", party="agent", kind="protocol") as h:
            h.record_wire(
                {"body": {"token": "t1", "payload": {"statement": "Payroll managers lose hours chasing exceptions."}}},
                {"status": 200, "body": {"projectId": "p1", "state": "OPEN", "revision": 1}})

    with recorder.interaction("agent-cycle") as handoff_id:
        with recorder.step("get_next (project p1)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {
                "kind": "handoff", "reason": "REVIEW",
                "display": "The problem card is waiting for your approval -- read it first.",
                "detail": {"stage": "PROBLEM"},
            }})
        recorder.retag_interaction(handoff_id, "agent-handoff")

    with recorder.interaction("ui-visit"):
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
    scenario = _FixtureScenario()
    _build_bundle(tmp_path)
    finalize_run(tmp_path, scenario=scenario, passed=True, failed_step=None, duration_s=1.0)

    scorecard = json.loads((tmp_path / "scorecard.json").read_text())
    report = (tmp_path / "report.html").read_text()

    for entry in scorecard["interactions"]:
        assert entry["title"] in report, f"no card found for interaction {entry['id']} ({entry['title']!r})"
    # Every interaction's card links back to its own raw steps -- a proxy for "one card each"
    # beyond just "the title string appears somewhere".
    assert report.count("raw steps:") == len(scorecard["interactions"])


def test_agent_cycle_card_shows_prose_not_raw_json(tmp_path):
    scenario = _FixtureScenario()
    _build_bundle(tmp_path)
    finalize_run(tmp_path, scenario=scenario, passed=True, failed_step=None, duration_s=1.0)
    report = (tmp_path / "report.html").read_text()

    assert "State the problem, not the solution." in report
    assert "Write it plainly, in the founder&#x27;s words." in report or \
        "Write it plainly, in the founder's words." in report
    assert "the problem, in the founder&#x27;s own words" in report or \
        "the problem, in the founder's own words" in report
    # The handoff's conversation card shows the display text as prose.
    assert "waiting for your approval" in report
    # Raw JSON is still there, but inside a collapsible <details> block, not inline prose.
    assert "<details>" in report
