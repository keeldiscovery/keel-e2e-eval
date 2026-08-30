"""Stackless: report.html generation from a fixture transcript.jsonl, including the crashed-run
case (no verdict.json at all) -- T007, contracts/evidence-contract.md."""

import json

from harness.evidence import generate_index, generate_report, write_verdict


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


# ------------------------------------------------------------------------------ index (T013)

def _bundle(tmp_path, name, *, scenario, passed, score, categories=None, not_applicable=None):
    run_dir = tmp_path / name
    run_dir.mkdir()
    (run_dir / "verdict.json").write_text(json.dumps({
        "scenario": scenario, "passed": passed, "failed_step": None, "duration_s": 1.0,
        "score": score, "policy_version": 2,
    }))
    (run_dir / "scorecard.json").write_text(json.dumps({
        "policy_version": 2, "scenario": scenario, "interactions": [],
        "categories": categories or {}, "not_applicable_categories": not_applicable or [],
        "run_score": score, "gated": not passed, "complete": passed,
    }))
    return run_dir


def test_index_lists_every_bundle_with_verdict_score_and_report_link(tmp_path):
    a = _bundle(tmp_path, "20260830T000000Z-s001-smoke", scenario="s001-smoke", passed=True, score=5.0,
                categories={"FIDELITY": 5.0, "GUIDANCE": 5.0, "ORIENTATION": 5.0, "CLARITY": 5.0})
    b = _bundle(tmp_path, "20260830T000100Z-s003-going-ahead", scenario="s003-going-ahead", passed=False,
                score=2.0, categories={"GUIDANCE": 5.0, "ORIENTATION": 5.0})

    out_path = generate_index([a, b], tmp_path / "INDEX-20260830T000200Z.html")
    content = out_path.read_text()

    assert "s001-smoke" in content
    assert "s003-going-ahead" in content
    assert "PASSED" in content
    assert "FAILED" in content
    assert "5/5" in content
    assert "2/5" in content
    assert f"{a.name}/report.html" in content
    assert f"{b.name}/report.html" in content


def test_index_marks_not_applicable_categories_distinctly_from_a_real_score(tmp_path):
    """S-007-shaped bundle: FIDELITY/CLARITY never applied (design §6.1, T003) -- the index must
    not render them as a bare 0, which would misread as a bad score rather than no evidence."""
    run_dir = _bundle(tmp_path, "20260830T000000Z-s007-hostile-wire", scenario="s007-hostile-wire",
                       passed=True, score=5.0, categories={"GUIDANCE": 5.0, "ORIENTATION": 5.0},
                       not_applicable=["FIDELITY", "CLARITY"])
    content = generate_index([run_dir], tmp_path / "INDEX.html").read_text()
    assert "N/A" in content


def test_index_handles_an_empty_batch(tmp_path):
    content = generate_index([], tmp_path / "INDEX-empty.html").read_text()
    assert "No runs" in content
