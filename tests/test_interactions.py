"""T010 (SC-001 mechanics): a fixture transcript groups into interactions in transcript order,
and every check's evidence refs (step seqs, screenshot files) resolve inside the same bundle."""

from __future__ import annotations

import itertools

from evals.scenario import Fact
from harness import scoring
from harness.evidence import _read_transcript
from harness.interactions import derive_interactions
from harness.steps import Recorder


def _build_fixture(run_dir):
    recorder = Recorder(run_dir)
    with recorder.interaction("agent-cycle"):
        with recorder.step("get_next (before any project)", party="agent", kind="protocol") as h:
            h.record_wire({"path": "/v2/agent/next"}, {"status": 200, "body": {
                "kind": "action", "action": "CREATE", "token": "t1",
                "requirements": ["the problem, in the founder's own words"],
                "instruction": {"purpose": "State the problem.", "content": "Write it plainly."},
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
                "display": "The problem card is waiting for your approval -- read the questions first.",
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
            (recorder.screenshot_path(shot)).write_bytes(b"\x89PNG\r\n\x1a\nfake")
            h.add_screenshot(shot)
    return recorder


def test_interactions_group_tagged_steps_in_transcript_order(tmp_path):
    _build_fixture(tmp_path)
    entries = _read_transcript(tmp_path)
    interactions = derive_interactions(entries)

    assert [ix.type for ix in interactions] == ["agent-cycle", "agent-handoff", "ui-visit"]
    assert interactions[0].step_seqs == [1, 2]
    assert interactions[0].conversation["action"] == "CREATE"
    assert interactions[1].conversation["outcome"].startswith("The problem card is waiting")
    assert interactions[2].captured_text["stage_screen"].startswith("THE PROBLEM")


def test_untagged_transcript_derives_to_no_interactions(tmp_path):
    """analysis finding A2: a pre-002 (or otherwise untagged) transcript re-scores gracefully --
    empty interactions, not a crash."""
    recorder = Recorder(tmp_path)
    with recorder.step("stack attached", party="stack", kind="note"):
        pass
    entries = _read_transcript(tmp_path)
    assert derive_interactions(entries) == []


def test_every_checks_evidence_resolves_inside_the_bundle(tmp_path):
    _build_fixture(tmp_path)
    facts = {
        "problem_statement": Fact(
            text="Payroll managers lose hours chasing exceptions.", kind="statement",
            hops=["agent_echo", "stage_screen", "brief"],
        ),
    }
    scoring.write_facts(tmp_path, facts)
    scorecard = scoring.score_bundle(tmp_path, scenario="fixture", complete=True)

    entries = _read_transcript(tmp_path)
    known_seqs = {e["seq"] for e in entries}
    known_screenshots = {name for e in entries for name in (e.get("screenshots") or [])}

    assert scorecard["interactions"], "expected at least one scored interaction"
    checked_any = False
    for interaction_entry in scorecard["interactions"]:
        for check in interaction_entry["checks"]:
            checked_any = True
            for seq in check["evidence"].get("steps", []):
                assert seq in known_seqs, f"{check['check_id']} points at a step seq not in the transcript"
            for shot in check["evidence"].get("screenshots", []):
                assert shot in known_screenshots, f"{check['check_id']} points at an unknown screenshot"
    assert checked_any
