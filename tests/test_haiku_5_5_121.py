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



# ------------------------------------------------------------------------ FR-2: the noise check's classifier

#: keel-cloud 190's classifier request as the SDK serialises it (`ApiRequestShapeTest.OnHaikuFiveFive`, written to its
#: `build/haiku-5-5-requests.txt`; the texts elided to their lengths there).
CLASSIFIER_REQUEST_190 = {"max_tokens": 1024, "messages": [{"content": "<40 bytes>", "role": "user"}],
                          "model": "claude-haiku-5-5", "output_config": {"effort": "low"},
                          "system": "<1853 bytes>", "thinking": {"type": "adaptive"}}

ITEM = {"kind": "single", "options": ["Daily", "Weekly", "Monthly"], "escape": "I can't say"}


def _shape(body: dict) -> dict:
    """The request with its texts elided, as keel-cloud's record writes it."""
    out = json.loads(json.dumps(body))
    out["system"] = f"<{len(body['system'].encode())} bytes>"
    for message in out["messages"]:
        message["content"] = f"<{len(message['content'].encode())} bytes>"
    return out


def test_the_noise_checks_request_is_the_products_on_haiku_5_5():
    from evals.noise import pipeline as pl                                   # noqa: PLC0415
    body = pl.request_body(ITEM, "weekly", "S" * 1853)
    assert set(body) == set(CLASSIFIER_REQUEST_190)
    for key in ("max_tokens", "model", "output_config", "thinking"):
        assert body[key] == CLASSIFIER_REQUEST_190[key], key
    assert [m["role"] for m in body["messages"]] == ["user"] and isinstance(body["messages"][0]["content"], str)
    for absent in ("temperature", "top_p", "top_k", "budget_tokens"):
        assert absent not in json.dumps(body), absent
    assert pl.HAIKU_USD_IN == 0.10 and pl.HAIKU_USD_OUT == 0.50       # Haiku 5.5's first card ($0.10 / $0.50 a MTok)


def test_the_request_matches_keel_clouds_own_record_where_the_checkout_has_it():
    from stack.config import load_config                                    # noqa: PLC0415
    from evals.noise import pipeline as pl                                   # noqa: PLC0415
    record = load_config(validate=False).keel_cloud / "build" / "haiku-5-5-requests.txt"
    if not record.is_file():
        pytest.skip(f"keel-cloud's checkout has no {record.name} (before keel-cloud 190, or not built)")
    text = record.read_text(encoding="utf-8")
    served = json.loads(text.split("## the classifier (classify-answer.md)", 1)[1].strip())
    assert served == CLASSIFIER_REQUEST_190
    ours = _shape(pl.request_body(ITEM, "weekly", "S" * 1853))
    assert {k: v for k, v in ours.items() if k != "messages"} == {k: v for k, v in served.items() if k != "messages"}


def test_the_answer_is_read_by_type_past_a_thinking_block():
    from evals.noise import pipeline as pl                                   # noqa: PLC0415
    reply = {"content": [{"type": "thinking", "thinking": "they said weekly", "signature": "x"},
                         {"type": "text", "text": '{"picks": [2], '}, {"type": "text", "text": '"confidence": 0.9}'}]}
    assert pl.answer_text(reply) == '{"picks": [2], "confidence": 0.9}'
    assert pl.answer_text({"content": [], "stop_reason": "refusal"}) == ""        # no text: unparsed, then unclear


def test_classify_sends_the_body_and_parses_past_thinking(monkeypatch):
    """One mocked Messages call, no network and no key: the body sent is `request_body`'s and the parsed answer is the
    text block's, the thinking block skipped."""
    import requests                                                          # noqa: PLC0415
    from evals.noise import pipeline as pl                                   # noqa: PLC0415
    sent = []

    class Reply:
        status_code = 200

        @staticmethod
        def json():
            return {"content": [{"type": "thinking", "thinking": "{not this}"},
                                {"type": "text", "text": '{"picks": [2], "confidence": 0.9}'}],
                    "usage": {"input_tokens": 600, "output_tokens": 90}, "stop_reason": "end_turn"}

    monkeypatch.setattr(requests, "post", lambda url, **kw: sent.append(kw) or Reply())
    out, _ms, usage, text, stop = pl.classify(ITEM, "weekly", "k", "S")
    assert out == {"picks": [2], "confidence": 0.9} and usage == (600, 90) and stop == "end_turn"
    assert len(sent) == 1 and sent[0]["json"] == pl.request_body(ITEM, "weekly", "S")
    assert "temperature" not in sent[0]["json"]


def test_the_makefile_says_the_classifier_as_it_is_called():
    make = (REPO / "Makefile").read_text(encoding="utf-8")
    comment = make[make.index("# make noise-check (spec 074 FR-3)"):make.index("\nnoise-check:")]
    assert "claude-haiku-5-5 with no temperature, max_tokens 1,024 and adaptive thinking at effort low" in comment


def test_no_test_or_fixture_names_the_old_light_id_but_the_v15_shape_above():
    """Every fixture's light id moved (FR-1); the one place it stays is this file's v15 table, which is what it is."""
    hits = []
    for path in sorted((REPO / "tests").rglob("*")):
        if path.is_file() and path.suffix in (".py", ".json", ".yaml", ".toml") and path.name != Path(__file__).name:
            if "claude-haiku-4-5" in path.read_text(encoding="utf-8", errors="ignore"):
                hits.append(str(path.relative_to(REPO)))
    assert hits == []
