"""T010 (SC-001 mechanics): a fixture transcript groups into interactions in transcript order,
and every check's evidence refs (step seqs, screenshot files) resolve inside the same bundle.

spec 005-connect-stack FR-009: fixtures use the current interaction kinds (`ui_visit`,
`agent_turn`, `arrival`) -- there is no more wire protocol to fixture a `get_next`/`submit`
exchange for.
"""

from __future__ import annotations

from evals.facts import Fact
from harness import scoring
from harness.evidence import _read_transcript
from harness.interactions import derive_interactions
from harness.steps import Recorder


def _build_fixture(run_dir):
    recorder = Recorder(run_dir)
    with recorder.interaction("arrival"):
        with recorder.step("founder arrives", party="founder", kind="browser") as h:
            h.capture_text("arrival_display", "Welcome back to Payroll Exceptions. Let's start.")

    with recorder.interaction("agent_turn"):
        with recorder.step("the agent answers the problem framing", party="agent", kind="browser") as h:
            h.capture_text("chat_state", "Connected · on your machine")
            h.capture_text("agent_reply", "Here's what we understood: Payroll managers lose "
                                           "hours chasing exceptions.")

    with recorder.interaction("ui_visit"):
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

    assert [ix.type for ix in interactions] == ["arrival", "agent_turn", "ui_visit"]
    assert interactions[0].conversation["outcome"].startswith("Welcome back")
    assert interactions[1].conversation["reply_summary"].startswith("Here's what we understood")
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
            hops=["stage_screen", "brief"],
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
