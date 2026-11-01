"""Spec 121 (keel-cloud 190, routing v16, `InferenceCharge.VERSION` 15): the referee follows the light tier to Claude
Haiku 5.5.

FR-1: the `claude` host's `light` row is `claude-haiku-5-5` at effort `low` and the table has no `sampling` block, so
a claude light case (context, reading, asked, example_match) now carries the wire's seventh key, `effort: {claude:
low}`; Codex and Copilot light cases still carry none. The table is read as the file, never typed in the resolver.
Stackless and modelless: nothing here calls a model.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from instructions import models as models_mod
from instructions import prompts as prompts_mod

REPO = Path(__file__).resolve().parent.parent

#: keel-cloud 190's `src/main/resources/keel/model-routing.json` (branch `190-the-light-tier-on-haiku-5-5`,
#: `ddb691f0`), copied: v15 with `hosts.claude.light` claude-haiku-4-5-20251001 -> claude-haiku-5-5, `efforts.claude.light`
#: = low added, and the `sampling` block removed (190 T006 / T007).
V16 = {
    "version": 16,
    "hosts": {
        "codex": {"light": "gpt-5.6-luna", "standard": "gpt-5.6-terra"},
        "copilot": {"light": "gpt-5.6-luna", "standard": "gpt-5.6-terra"},
        "claude": {"light": "claude-haiku-5-5", "standard": "claude-sonnet-5-5", "frontier": "claude-opus-5-5"},
    },
    "efforts": {"codex": {"standard": "medium"}, "copilot": {"standard": "medium"},
                "claude": {"light": "low", "standard": "medium", "frontier": "medium"}},
    "_tiers": ["light", "standard", "frontier"],
    "classes": {"frame": "frontier", "reading": "light", "brief": "standard", "context": "light",
                "calibration": "standard", "respondent": "frontier", "asked": "light", "example_match": "light"},
}

LIGHT_CLASSES = ("context", "reading", "asked", "example_match")


def _case(kind, screen):
    return prompts_mod.Case(case_id=f"e/{screen}/run1", kind=kind, entry_id="e", screen=screen, subject="PROBLEM",
                            run_index=1,
                            payload=prompts_mod.payload_for("I", {"k": None}, {"allowed_outcomes": ["COMPLETED"]}))


# ------------------------------------------------------------------------------------- FR-1: routing v16

def test_v16_puts_every_claude_light_class_on_haiku_5_5_at_low():
    table = models_mod.parse(V16, source="v16")
    for job_class in LIGHT_CLASSES:
        assert table.resolve("claude", job_class) == "claude-haiku-5-5", job_class
        assert table.resolve_effort("claude", job_class) == "low", job_class
    assert table.resolve_screen("claude", "INTERPRET") == "claude-haiku-5-5"
    assert table.resolve_effort_screen("claude", "CONTEXT_INTERPRET") == "low"
    assert table.resolve_effort_screen("claude", "ASKED") == "low"


def test_v16_moves_nothing_but_the_claude_light_row():
    table = models_mod.parse(V16, source="v16")
    # the Sonnet and Opus classes keep their models and `medium`
    assert table.resolve("claude", "calibration") == "claude-sonnet-5-5"
    assert table.resolve_effort("claude", "calibration") == "medium"
    assert table.resolve("claude", "frame") == table.resolve("claude", "respondent") == "claude-opus-5-5"
    # Codex and Copilot light jobs: luna, and no effort (their rows name `standard` alone)
    for host in ("codex", "copilot"):
        for job_class in LIGHT_CLASSES:
            assert table.resolve(host, job_class) == "gpt-5.6-luna"
            assert table.resolve_effort(host, job_class) is None


def test_v16_efforts_used_records_low_on_the_light_classes():
    table = models_mod.parse(V16, source="v16")
    assert table.efforts_used("claude") == {"context": "low", "frame": "medium", "calibration": "medium",
                                            "respondent": "medium", "reading": "low", "asked": "low"}
    assert table.models_used("claude")["reading"] == "claude-haiku-5-5"


def test_stamp_writes_a_claude_reading_the_seventh_key_since_v16():
    table = models_mod.parse(V16, source="v16")
    reading, context = _case("READING", "INTERPRET"), _case("CONTEXT", "CONTEXT_INTERPRET")
    models_mod.stamp([reading, context], table, "claude")
    for case in (reading, context):
        assert case.payload[models_mod.MODEL_KEY] == {"claude": "claude-haiku-5-5"}
        assert case.payload[models_mod.EFFORT_KEY] == {"claude": "low"}
        assert case.effort == "low"
        assert list(case.payload)[-2:] == [models_mod.MODEL_KEY, models_mod.EFFORT_KEY]
    codex = _case("READING", "INTERPRET")
    models_mod.stamp([codex], table, "codex")
    assert codex.payload[models_mod.MODEL_KEY] == {"codex": "gpt-5.6-luna"}
    assert models_mod.EFFORT_KEY not in codex.payload


def test_v16_carries_no_sampling_and_a_v15_table_with_one_still_parses():
    """190 T007: the block is removed (no model the claude row names takes a non-default temperature or a seed, and no
    runtime reads it). The reader never read `sampling`, so a v15 table carrying it still parses, unchanged."""
    assert "sampling" not in V16
    v15 = dict(V16, version=15, sampling={c: {"temperature": 0, "seed": 122}
                                          for c in ("context", "calibration", "example_match")})
    v15["hosts"] = dict(V16["hosts"], claude=dict(V16["hosts"]["claude"], light="claude-haiku-4-5-20251001"))
    v15["efforts"] = dict(V16["efforts"], claude={"standard": "medium", "frontier": "medium"})
    table = models_mod.parse(v15, source="v15")
    assert table.resolve("claude", "reading") == "claude-haiku-4-5-20251001"
    assert table.resolve_effort("claude", "reading") is None


def test_keel_clouds_live_table_is_v16_as_mirrored():
    """The checkout's own table: from v16 on, the claude light row is the mirror's. Skipped by name on a checkout
    before keel-cloud 190 (its table still v15)."""
    from stack.config import load_config                                    # noqa: PLC0415
    path = load_config(validate=False).keel_cloud / models_mod.CLOUD_RESOURCE
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {path.parent}")
    document = json.loads(path.read_text(encoding="utf-8"))
    if int(document.get("version") or 0) < 16:
        pytest.skip(f"keel-cloud's routing v{document.get('version')} predates keel-cloud 190 (Haiku 5.5)")
    assert document["hosts"]["claude"]["light"] == V16["hosts"]["claude"]["light"]
    assert document["efforts"]["claude"]["light"] == V16["efforts"]["claude"]["light"]
    assert "sampling" not in document
    if document["version"] == 16:
        assert document == V16
    table = models_mod.parse(document, source=str(path))
    assert table.resolve_effort("claude", "reading") == "low"


def test_the_029_screen_pin_follows_the_light_row_and_is_still_refused_for_asked():
    path = REPO / "specs" / "029-marks-v9-vectors" / "contracts" / "models-screen.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["hosts"]["claude"]["light"] == "claude-haiku-5-5"
    assert document["efforts"]["claude"] == {"light": "low", "standard": "medium"}
    assert "spec 121" in document["_comment"]
    with pytest.raises(models_mod.ModelsUnavailable, match="says nothing about asked"):
        models_mod.load(path)

