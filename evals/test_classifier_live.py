"""The live classifier check (spec 048 FR-2): the weekly live column's one text-only check of keel-cloud 099's answer
path against the **real** model -- the spoken-answer cases (`harness/classifier_cases.py`) carried onto an AI link's
own items and sent to staging's `POST /v2/i/{token}/interview/classify`, where a founder outside `fake-for` is read by
Keel's AI on the light tier (Haiku 4.5 today) -- held to the guard's one bar: no confident wrong answer, the
corrections right.

**Not a scenario, and no journey.** It drives no browser and builds no project: a link that answers classify for the
real model needs a READY recording on a project whose founder is outside `fake-for`, and a matrix founder is always
inside it (`stack/remote.py` registers `@keel-e2e-eval.test`) while recording a face for one outside it would pay the
renderer. So the link is **named** -- `KEEL_CLASSIFIER_LINK`, an unanswered AI-interviewer link on the remote, made once
by the founder on a project of his own -- and this check is skipped by name without it. `classify` stores nothing, so
one link serves every week.

**It spends Keel's money, a little** (AGENTS.md names this place): one Haiku call a case, about $0.0006 (keel-cloud
099 design §6), at most `classifier_guard.LIVE_BUDGET_USD` ($0.10) a run -- refused before the first call when the
plan would cost more. `-m live`: opt-in through `make eval-live K=classifier PROFILE=remote`, deselected from
`make eval`. Its bundle is `runs/<stamp>-classifier-live/classifier.json`.

A run whose every reason is one the fake writes was answered by the fake (the link's founder is in `fake-for`): it is
failed with that sentence, never passed as a measurement of the model.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
import requests

from harness import classifier_guard as guard
from stack.config import REPO_ROOT

pytestmark = pytest.mark.live

LINK_ENV = "KEEL_CLASSIFIER_LINK"


def _token(link: str) -> str:
    return link.rstrip("/").rsplit("/", 1)[-1].split("?")[0]


def test_classifier_live(stack_config):
    link = os.environ.get(LINK_ENV, "").strip()
    if not stack_config.is_remote:
        pytest.skip("the live classifier check runs on the remote profile only (PROFILE=remote): the local stack has "
                    "no model key and answers every founder with the FakeClassifier, which the AI-link leg guards")
    if not link:
        pytest.skip(f"the live classifier check needs {LINK_ENV}: an unanswered AI-interviewer link on the remote "
                    "whose founder is outside keel.v2.vendors.fake-for (a matrix founder never is)")
    token = _token(link)
    base = stack_config.cloud_base_url.rstrip("/")
    served_response = requests.get(f"{base}/v2/i/{token}/interview", timeout=20)
    assert served_response.status_code == 200, (served_response.status_code, served_response.text[:300])
    interview = served_response.json()
    assert "AI_INTERVIEWER" in (interview.get("formats") or []), interview.get("formats")
    served = guard.served_items(interview)
    asked, _ = guard.plan(served)
    budget_calls = int(guard.LIVE_BUDGET_USD / guard.COST_PER_CALL_USD)
    assert len(asked) * guard.COST_PER_CALL_USD <= guard.LIVE_BUDGET_USD, (len(asked), budget_calls)

    def post(body: dict) -> tuple[int, dict]:
        response = requests.post(f"{base}/v2/i/{token}/interview/classify", json=body, timeout=20)
        try:
            return response.status_code, response.json()
        except ValueError:
            return response.status_code, {}

    started = time.monotonic()
    report = guard.run(post, served, limit=budget_calls)
    seconds = round(time.monotonic() - started, 1)
    run_dir = REPO_ROOT / "runs" / f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-classifier-live"
    run_dir.mkdir(parents=True, exist_ok=True)
    out = {**report.to_json(), "served": [s.shape for s in served], "seconds": seconds,
           "estimated_usd": round(len(report.outcomes) * guard.COST_PER_CALL_USD, 4),
           "answered_by_fake": report.answered_by_fake, "model_never_answered": report.model_never_answered,
           "base": base}
    Path(run_dir / "classifier.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                                                 encoding="utf-8")
    summary = report.summary()
    assert not report.model_never_answered, ("every answer was keel-cloud's timeout / vendor fallback: Keel's AI never "
                                             "answered", summary)
    assert not report.answered_by_fake, ("every reason is the FakeClassifier's: the link's founder is in fake-for, so "
                                         "this run measured the fake, not Keel's AI", summary)
    assert not report.refused, summary["refused cases"]
    assert not report.wrong, summary["wrong cases"]
    assert all(v == "right" for v in report.corrections.values()), report.corrections
