"""Shared, hand-checkable fixtures for the `MARKS_VERSION` 9 tests (spec 029 T004-T006).

Nothing here is a corpus entry or a copy of the cloud: the registry is a hand-sized slice of the
design-time draft, the two entries are invented and small, and the export is written by the test
into a temporary directory in the shape keel-cloud 058's exporter is asked for
(`contracts/screen-shapes.md` §2).
"""

from __future__ import annotations

import json
import types
from pathlib import Path

import yaml

from instructions import context as context_mod
from instructions import contract as contract_mod
from instructions import corpus as corpus_mod
from instructions import registry as registry_mod

FIXTURES = Path(__file__).parent / "fixtures"
SLICE = FIXTURES / "registry" / "slice.yaml"
BROKEN = FIXTURES / "registry" / "broken"
ENTRY = FIXTURES / "corpus" / "09-fixture-r3.yaml"
ENTRY_B2B = FIXTURES / "corpus" / "10-fixture-r3-b2b.yaml"
COMPARE = FIXTURES / "compare"
V8_BUNDLE = FIXTURES / "runs" / "v8-bundle"
CORPUS_R3 = FIXTURES / "corpus-r3"


def registry():
    return registry_mod.load(SLICE)


def registry_document() -> dict:
    return yaml.safe_load(SLICE.read_text(encoding="utf-8"))


def entry(path=ENTRY):
    return corpus_mod.load_file(path, registry=registry())


def raw_entry(path=ENTRY) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def write_entry(tmp_path, raw: dict, name="09-fixture-r3.yaml") -> Path:
    path = Path(tmp_path) / name
    path.write_text(yaml.safe_dump(raw, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def write_export(directory, *, with_registry=True, routing=None, keys=None) -> Path:
    """An exported contract in 058's requested shape: the seven model screens, each with the
    context keys of screen-shapes §2 and a permissive contract, plus `dimension-registry.json`."""
    directory = Path(directory)
    (directory / "contracts").mkdir(parents=True, exist_ok=True)
    screens = list(contract_mod.MODEL_SCREENS)
    (directory / "manifest.json").write_text(json.dumps(
        {"screens": screens, "keel_cloud_commit": "abc1234", "keel_cloud_dirty": False,
         "generated_at": "2026-10-07T00:00:00Z"}), encoding="utf-8")
    (directory / "context-keys.json").write_text(json.dumps(
        keys or {s: context_mod.DEFAULT_KEYS[s] for s in screens}), encoding="utf-8")
    for screen in screens:
        (directory / "contracts" / f"{screen}.json").write_text(json.dumps(
            {"allowed_outcomes": ["COMPLETED", "NEEDS_INPUT"], "completed_result_schema": {}}),
            encoding="utf-8")
    if with_registry:
        (directory / contract_mod.REGISTRY_NAME).write_text(
            json.dumps(registry_document()), encoding="utf-8")
    if routing is not None:
        (directory / "model-routing.json").write_text(json.dumps(routing), encoding="utf-8")
    return directory


def exported(tmp_path, **kw):
    return contract_mod.read(write_export(Path(tmp_path) / "export", **kw))


class FakeRuntime:
    """Enough of `keel_runtime.executor` to render through: the prompt is the screen and the
    context, so a test can read what a case would have been sent."""

    @staticmethod
    def InferenceRequest(**kw):                       # noqa: N802 - mirrors the real dataclass
        return types.SimpleNamespace(**kw)

    @staticmethod
    def build_prompt(request):
        payload = request.request_payload
        return (payload.get("instruction") or "") + "\n" + json.dumps(payload.get("context"))


def instructions() -> dict:
    return {screen: f"INSTRUCTION FOR {screen}" for screen in contract_mod.MODEL_SCREENS}
