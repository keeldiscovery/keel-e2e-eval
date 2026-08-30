"""Stackless: report.html generation from a fixture transcript.jsonl, including the crashed-run
case (no verdict.json at all) -- T007, contracts/evidence-contract.md."""

import json

from harness.evidence import generate_report, write_verdict


def _write_transcript(run_dir, entries):
    path = run_dir / "transcript.jsonl"
    with path.open("w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def test_report_renders_every_step_with_thumbnails_and_wire_json(tmp_path):
    run_dir = tmp_path / "20260829T000000Z-s001-smoke"
    run_dir.mkdir()
    (run_dir / "screenshots").mkdir()
    (run_dir / "screenshots" / "001-overview.png").write_bytes(b"\x89PNG\r\n\x1a\nfakepngbytes")

    _write_transcript(run_dir, [
        {"seq": 1, "ts": "2026-08-29T00:00:00Z", "kind": "protocol", "name": "get_next",
         "party": "agent", "ok": True, "duration_s": 0.01,
         "request": {"token": None}, "response": {"kind": "action", "action": "CREATE"},
         "screenshots": []},
        {"seq": 2, "ts": "2026-08-29T00:00:01Z", "kind": "browser", "name": "founder opens overview",
         "party": "founder", "ok": True, "duration_s": 0.5, "screenshots": ["001-overview.png"]},
    ])
    write_verdict(run_dir, scenario="s001-smoke", passed=True, failed_step=None, duration_s=12.3)

    out_path = generate_report(run_dir)
    content = out_path.read_text()

    assert "get_next" in content
    assert "founder opens overview" in content
    assert "001-overview.png" in content
    assert "PASSED" in content
    assert "CREATE" in content  # wire JSON is present, not just the step name


def test_report_generates_from_a_crashed_scenarios_partial_transcript(tmp_path):
    """No verdict.json at all -- the harness itself crashed mid-run. The report must still exist
    and say so, rather than raising (contracts/evidence-contract.md: absence of verdict.json is
    itself a reportable defect)."""
    run_dir = tmp_path / "20260829T000000Z-s001-smoke"
    run_dir.mkdir()
    _write_transcript(run_dir, [
        {"seq": 1, "ts": "2026-08-29T00:00:00Z", "kind": "note", "name": "stack attached",
         "party": "stack", "ok": True, "duration_s": 0.0, "screenshots": []},
    ])
    # No verdict.json written -- simulates a hard crash before the `finally:` ran.

    out_path = generate_report(run_dir)
    content = out_path.read_text()
    assert "stack attached" in content
    assert "HARNESS CRASHED" in content


def test_report_anchors_and_links_evidence_for_the_failing_step(tmp_path):
    run_dir = tmp_path / "20260829T000000Z-s001-smoke"
    run_dir.mkdir()
    (run_dir / "failure").mkdir()
    (run_dir / "failure" / "page.html").write_text("<html>broken</html>")
    (run_dir / "failure" / "console.log").write_text("console error: boom")

    _write_transcript(run_dir, [
        {"seq": 1, "ts": "2026-08-29T00:00:00Z", "kind": "browser", "name": "participant opens link",
         "party": "participant", "ok": False, "duration_s": 1.2, "error": "TimeoutError: no element",
         "screenshots": []},
    ])
    write_verdict(run_dir, scenario="s001-smoke", passed=False,
                   failed_step="participant opens link", duration_s=5.0)

    content = generate_report(run_dir).read_text()
    assert 'id="failed-step"' in content
    assert "failure/page.html" in content
    assert "failure/console.log" in content
    assert "FAILED" in content


def test_report_is_regenerable_from_transcript_alone(tmp_path):
    """make report RUN=<dir> rebuilds report.html purely from what's on disk."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_transcript(run_dir, [
        {"seq": 1, "ts": "t", "kind": "note", "name": "n", "party": "stack", "ok": True,
         "duration_s": 0.0, "screenshots": []},
    ])
    first = generate_report(run_dir).read_text()
    second = generate_report(run_dir).read_text()
    assert first == second
