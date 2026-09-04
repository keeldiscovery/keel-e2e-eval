"""T014 (SC-003), automated: when a browser step fails, the run bundle gets page HTML + a
console log at the moment of failure, the transcript records it, and the report still generates
-- without needing the full stack (a closed port stands in for "keel-web is down").

This is deliberately a real Playwright browser against a real (closed) port -- browser.py's
failure-capture path is exercised for real, only the product stack is stubbed out by pointing at
a port nothing is listening on.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from harness.browser import Landing
from harness.evidence import generate_report
from harness.steps import Recorder


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _closed_port() -> int:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_a_dead_keel_web_fails_the_browser_step_with_full_evidence(tmp_path, browser):
    recorder = Recorder(tmp_path)
    page = browser.new_page()
    dead_base = f"http://localhost:{_closed_port()}"
    landing = Landing(page, recorder, dead_base)

    with pytest.raises(Exception):
        landing.visit()
    page.close()

    # transcript: the step is recorded as a failure, not silently swallowed.
    import json
    lines = [json.loads(line) for line in recorder.transcript_path.read_text().splitlines()]
    failing = [e for e in lines if not e["ok"]]
    assert len(failing) == 1
    assert failing[0]["party"] == "founder"
    assert failing[0]["error"]

    # failure/ carries page HTML + console log (contracts/evidence-contract.md).
    assert (tmp_path / "failure" / "page.html").exists()
    assert (tmp_path / "failure" / "console.log").exists()

    # the report still generates, anchored at the failing step.
    from harness.evidence import write_verdict
    write_verdict(tmp_path, scenario="failure-path-check", passed=False,
                   failed_step=recorder.failed_step, duration_s=1.0)
    report = generate_report(tmp_path).read_text()
    assert 'id="failed-step"' in report
    assert "failure/page.html" in report
    assert "failure/console.log" in report
