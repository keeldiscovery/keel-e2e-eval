"""Spec 105 (keel-cloud 169, routing v14, `InferenceCharge.VERSION` 13): the harness reads the frontier tier.

FR-1, the fallback mirror: a class on a tier a host has no row for stands one rung down -- `frontier` on `standard`
and nothing else -- model and effort together, as keel-cloud's `ModelRouting.FALLBACK` / `standingTier` resolve it;
the S-012 per-job model check reads `resolve_screen`, so it follows. The table is read as the file."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from instructions import models as models_mod
from instructions import prompts as prompts_mod

REPO = Path(__file__).resolve().parent.parent

#: routing v14's shape (keel-cloud 169), synthetic: `frame` on `frontier`, pinned on `claude` alone.
V14 = {
    "version": 14,
    "hosts": {
        "codex": {"light": "gpt-5.6-luna", "standard": "gpt-5.6-terra"},
        "copilot": {"light": "gpt-5.6-luna", "standard": "gpt-5.6-terra"},
        "claude": {"light": "claude-haiku-4-5-20251001", "standard": "claude-sonnet-5-5",
                   "frontier": "claude-opus-5-5"},
    },
    "efforts": {"codex": {"standard": "medium"}, "copilot": {"standard": "medium"},
                "claude": {"standard": "medium", "frontier": "medium"}},
    "_tiers": ["light", "standard", "frontier"],
    "classes": {"frame": "frontier", "reading": "light", "brief": "standard", "context": "light",
                "calibration": "standard", "respondent": "standard", "asked": "light", "example_match": "light"},
}


def _frame_case(screen="PROBLEM_INTERPRET"):
    return prompts_mod.Case(case_id=f"e/{screen}/run1", kind="FRAME", entry_id="e", screen=screen,
                            subject="PROBLEM", run_index=1,
                            payload=prompts_mod.payload_for("I", {"k": None}, {"allowed_outcomes": ["COMPLETED"]}))


# --------------------------------------------------------------------------------------- FR-1: the fallback

def test_the_mirror_is_keel_clouds_fallback():
    assert models_mod.FALLBACK == {"frontier": "standard"}


def test_claude_runs_the_frame_screens_on_its_frontier_row():
    table = models_mod.parse(V14, source="v14")
    assert table.standing_tier("claude", "frame") == "frontier"
    for screen in ("PROBLEM_INTERPRET", "SOLUTION_MECHANISM"):
        assert table.resolve_screen("claude", screen) == "claude-opus-5-5"
        assert table.resolve_effort_screen("claude", screen) == "medium"


@pytest.mark.parametrize("host", ["codex", "copilot"])
def test_a_host_with_no_frontier_row_stands_on_its_standard_row_model_and_effort_together(host):
    table = models_mod.parse(V14, source="v14")
    assert table.standing_tier(host, "frame") == "standard"
    for screen in ("PROBLEM_INTERPRET", "SOLUTION_MECHANISM"):
        assert table.resolve_screen(host, screen) == "gpt-5.6-terra"
        assert table.resolve_effort_screen(host, screen) == "medium"
    assert table.models_used(host)["frame"] == "gpt-5.6-terra"
    assert table.efforts_used(host)["frame"] == "medium"
    # the file is read as the file: no frontier row is invented
    assert "frontier" not in table.hosts[host] and table.tier_for("frame") == "frontier"


def test_stamp_puts_the_fallen_back_model_and_effort_on_a_frame_case():
    table = models_mod.parse(V14, source="v14")
    case = _frame_case("SOLUTION_MECHANISM")
    models_mod.stamp([case], table, "copilot")
    assert case.payload[models_mod.MODEL_KEY] == {"copilot": "gpt-5.6-terra"}
    assert case.payload[models_mod.EFFORT_KEY] == {"copilot": "medium"}
    models_mod.stamp([case], table, "claude")
    assert case.payload[models_mod.MODEL_KEY] == {"claude": "claude-opus-5-5"}
    assert case.payload[models_mod.EFFORT_KEY] == {"claude": "medium"}


def test_only_frontier_falls_and_only_one_rung():
    """keel-cloud `ModelRoutingTest.onlyFrontierFallsBackAndOnlyOneRung`: a standard class on a host with no standard
    row is no pin (a standard job is never sent to a light model), and a frontier class on a host with a light row
    only is no pin too."""
    document = json.loads(json.dumps(V14))
    document["hosts"]["codex"] = {"light": "gpt-5.6-luna"}
    document["efforts"]["codex"] = {}
    table = models_mod.parse(document, source="light-only")
    assert table.standing_tier("codex", "calibration") is None
    assert table.resolve("codex", "calibration") is None
    assert table.resolve("codex", "frame") is None
    assert table.resolve_effort("codex", "frame") is None
    assert table.resolve("codex", "reading") == "gpt-5.6-luna"


def test_the_effort_is_read_where_the_model_stands():
    """A host that pins a frontier MODEL with no frontier effort runs it at the CLI's default effort -- never the
    standard row's effort beside the frontier model (the effort falls only with the model)."""
    document = json.loads(json.dumps(V14))
    document["efforts"]["claude"] = {"standard": "medium"}
    table = models_mod.parse(document, source="no-frontier-effort")
    assert table.resolve("claude", "frame") == "claude-opus-5-5"
    assert table.resolve_effort("claude", "frame") is None


def test_a_host_with_no_row_at_all_is_still_no_pin():
    table = models_mod.parse(V14, source="v14")
    assert table.standing_tier("gemini", "frame") is None
    assert table.resolve("gemini", "frame") is None and table.resolve_effort("gemini", "frame") is None


def test_keel_clouds_live_table_resolves_the_frame_screens_per_host():
    from stack.config import load_config                                    # noqa: PLC0415
    path = load_config(validate=False).keel_cloud / models_mod.CLOUD_RESOURCE
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {path.parent}")
    table = models_mod.load(path)
    if table.tier_for("frame") != "frontier":
        pytest.skip(f"keel-cloud's routing v{table.version} predates spec 169 (frame is not on frontier)")
    assert table.resolve_screen("claude", "PROBLEM_INTERPRET") == "claude-opus-5-5"
    for host in ("codex", "copilot"):
        assert table.resolve_screen(host, "SOLUTION_MECHANISM") == table.hosts[host]["standard"]
        assert table.resolve_effort_screen(host, "SOLUTION_MECHANISM") == table.efforts[host]["standard"]


def test_s012s_per_job_check_reads_the_resolver_that_falls_back():
    source = (REPO / "evals" / "test_s012_journey_through_a_host.py").read_text(encoding="utf-8")
    assert "routing_table.resolve_screen(HOST, screen)" in source
    assert "standing_tier" in inspect.getsource(models_mod.ModelTable.resolve)
