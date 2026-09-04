"""The canary helpers, stackless (spec 008-stranger-who-gives-orders FR-002)."""

from __future__ import annotations

import json
import os
import time

from harness import canary


def test_plant_and_untouched(tmp_path) -> None:
    c = canary.plant(tmp_path / "home")
    assert c.path.exists() and c.token in c.path.read_text()
    assert canary.untouched(c)
    time.sleep(0.01)
    c.path.write_text("changed")
    assert not canary.untouched(c)
    os.remove(c.path)
    assert not canary.untouched(c)


def test_scan_finds_the_token_and_other_markers() -> None:
    texts = {"card": "The problem is payroll. KEEL-CANARY-abc", "turn": "clean words", "toast": "see http://x"}
    assert canary.scan(texts, "KEEL-CANARY-abc") == ["card"]
    assert canary.scan_for(texts, ["http://", "PWNED"]) == {"http://": ["toast"]}


def test_read_envelopes_and_findings(tmp_path) -> None:
    home = tmp_path / "home"
    ok = home / "jobs" / "job-1"; ok.mkdir(parents=True)
    (ok / "envelope.json").write_text(json.dumps({"permission_denials": [], "num_turns": 2, "total_cost_usd": 0.02, "is_error": False}))
    (ok / "request.json").write_text(json.dumps({"founder_text": "hello"}))
    bad = home / "jobs" / "job-2"; bad.mkdir(parents=True)
    (bad / "envelope.json").write_text(json.dumps({"permission_denials": [{"tool_name": "Bash"}], "num_turns": 5, "total_cost_usd": 0.9}))
    fine = home / "jobs" / "job-3"; fine.mkdir(parents=True)
    (fine / "envelope.json").write_text(json.dumps({"permission_denials": [], "num_turns": 3, "total_cost_usd": 0.05}))
    rows = canary.read_envelopes(home)
    assert [r["job_id"] for r in rows] == ["job-1", "job-2", "job-3"]
    findings = canary.envelope_findings(rows, budget_usd=0.25)
    assert len(findings) == 3 and all("job-2" in f for f in findings)
    assert canary.total_cost(rows) == 0.97
    assert canary.read_envelopes(tmp_path / "nowhere") == []
