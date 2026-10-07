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


# ------------------------------------------------------------ produced answers a scorer reads

class FakeJudge:
    """`judge.Judge`'s one question, answered from a table and recorded -- never a model."""

    def __init__(self, answer=False):
        self.answer = answer
        self.calls = []
        self._cache = {}

    @property
    def call_count(self):
        return len(self.calls)

    def reveals_solution(self, question_text, mechanism_one_liner, *, context=""):
        key = question_text
        if key not in self._cache:
            self.calls.append({"question": question_text, "mechanism": mechanism_one_liner})
            self._cache[key] = self.answer
        return self._cache[key]


def calibration_question(dimension, *, b2b=False) -> dict:
    """A question that meets every §2.2 rule for `dimension` -- the green half every red half of
    `tests/test_instruction_score.py` mutates by one thing."""
    from instructions import score as score_mod                       # noqa: PLC0415
    text = f"About {dimension.name.lower()}: what do you believe, for the people you mean?"
    if dimension.key == "problem.prevalence":
        text = "Out of 10, how many had this at least once in the last 7 nights?"
    if dimension.founder_numeric:
        return {"key": dimension.key, "question": text, "options": None,
                "respondent_note": "asked as a number"}
    codes = dimension.fixed_codes
    if codes is None:
        codes = score_mod._ladder_codes(dimension, b2b) or ["first_kind", "second_kind",
                                                            "third_kind", "fourth_kind"]
        if dimension.key == "commercial.existing_sacrifice":
            codes = ["spares", "locksmiths", "taxis", "none"]
    options = [{"label": f"Option {i} for this", "normalized": code,
                "belief_phrase": f"the {code.replace('_', ' ')} answer"}
               for i, code in enumerate(codes, start=1)]
    return {"key": dimension.key, "question": text, "options": options,
            "respondent_note": "asked of the stranger in their own words"}


def calibration_result(registry, vector) -> dict:
    return {"vector": vector, "questions": [calibration_question(d) for d in registry.slice(vector)]}


def calibration_case(entry, vector, run_index=1):
    from instructions import prompts as prompts_mod                   # noqa: PLC0415
    return prompts_mod.Case(case_id=f"{entry.id}/CALIBRATION_{vector}/run{run_index}",
                            kind="CALIBRATION", entry_id=entry.id,
                            screen="CALIBRATION_QUESTIONS", subject=vector,
                            run_index=run_index, payload={}, meta={"vector": vector})


def respondent_item(entry, key, *, label_only=False) -> dict:
    """An item meeting every §2.2 respondent rule, written from the golden plan row."""
    row = entry.respondent_questions[key]
    item = {"key": key, "question": f"Thinking about that time: {key.split('.')[1].replace('_', ' ')}?"}
    if row["control"] in ("segmented_0_to_7", "number_with_unit", "two_numbers_optional",
                          "gate_yes_no"):
        item["options"] = None
        return item
    options = []
    for i, code in enumerate(row.get("codes") or [], start=1):
        label = "Something else" if code == "something_else" else f"Choice {i}"
        options.append(label if label_only else {"label": label, "code": code})
    item["options"] = options
    return item


def respondent_result(entry, part, *, link="PRIMARY", label_only=False) -> dict:
    keys = entry.plan()[part]
    result = {"part": part, "link": link,
              "items": [respondent_item(entry, k, label_only=label_only) for k in keys]}
    if part == 2:
        result["reveal"] = {"title": "What we are testing", "body": "A small thing you could try."}
    return result


def respondent_case(entry, part, *, link="PRIMARY", run_index=1):
    from instructions import prompts as prompts_mod                   # noqa: PLC0415
    label = "B2B" if link == "COMMERCIAL_B2B" else f"PART{part}"
    plan = entry.plan()
    return prompts_mod.Case(case_id=f"{entry.id}/RESPONDENT_{label}/run{run_index}",
                            kind="RESPONDENT", entry_id=entry.id,
                            screen="RESPONDENT_QUESTIONS", subject=label, run_index=run_index,
                            payload={}, meta={"part": part, "link": link,
                                              "plan": list(plan[part])})


def interpret_case(entry, person, run_index=1):
    from instructions import prompts as prompts_mod                   # noqa: PLC0415
    return prompts_mod.Case(case_id=f"{entry.id}/INTERPRET/{person}/run{run_index}",
                            kind="READING", entry_id=entry.id, screen="INTERPRET",
                            subject=person, run_index=run_index, payload={},
                            meta={"person": person})
