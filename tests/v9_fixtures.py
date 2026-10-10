"""Shared, hand-checkable fixtures for the `MARKS_VERSION` 9 tests (spec 029 T004-T006), at 10 since
spec 030 (the registry of twelve, corpus revision 4).

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
ENTRY = FIXTURES / "corpus" / "09-fixture-r6.yaml"
ENTRY_B2B = FIXTURES / "corpus" / "10-fixture-r6-b2b.yaml"
COMPARE = FIXTURES / "compare"
V8_BUNDLE = FIXTURES / "runs" / "v8-bundle"

#: Why a test reading keel-cloud's canon corpus skips: the canon is not at revision 5 yet (calls 49, 51, 60 --
#: there is no fixture fallback any more; keel-cloud 074 carries revision 6).
CANON_NOT_R6 = ("keel-cloud's canon corpus is not at revision 6 (keel-cloud 074) -- spec 031 reads "
                "the corpus from keel-cloud's canon and nowhere else (judgement call 49)")


def canon_dir() -> Path:
    """keel-cloud's corpus directory, as `stack.toml` names the checkout."""
    from stack.config import load_config                              # noqa: PLC0415
    return corpus_mod.corpus_dir(load_config(validate=False).keel_cloud)


def canon_entry(name: str) -> Path:
    """One of keel-cloud's revision-6 entries (`03-lullaby.yaml`...), or a skip naming why."""
    import pytest                                                     # noqa: PLC0415
    path = canon_dir() / name
    try:
        revision = yaml.safe_load(path.read_text(encoding="utf-8")).get("revision")
    except (OSError, AttributeError, yaml.YAMLError):
        revision = None
    if revision != corpus_mod.REVISION:
        pytest.skip(CANON_NOT_R6)
    return path



def registry():
    return registry_mod.load(SLICE)


def registry_document() -> dict:
    return yaml.safe_load(SLICE.read_text(encoding="utf-8"))


def entry(path=ENTRY):
    return corpus_mod.load_file(path, registry=registry())


def raw_entry(path=ENTRY) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def write_entry(tmp_path, raw: dict, name="09-fixture-r6.yaml") -> Path:
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
    text = f"About {dimension.name.lower()}: what is true for the people meant?"
    if dimension.founder_price:                         # call 53: the key and the note, no more
        return {"key": dimension.key, "respondent_note": "asked of whoever pays"}
    if dimension.founder_numeric:                       # call 52: framed on 7 nights, no text
        return {"key": dimension.key, "options": None, "respondent_note": "asked as a number"}
    if dimension.founder_cost:                          # call 61: the kinds and their units, no question, no phrase
        kinds = [{"label": label, "normalized": code, "unit": unit}
                 for label, code, unit in (("Spare keys", "spares", "money"),
                                           ("Locksmith call-outs", "locksmiths", "money"),
                                           ("Time spent searching", "searching", "hours"),
                                           ("None of these; they cope", "none", None))]
        kinds = [{k: v for k, v in kind.items() if v is not None} for kind in kinds]
        return {"key": dimension.key, "options": kinds, "respondent_note": "asked of the stranger"}
    head = {"key": dimension.key, "question": text}
    if dimension.key == "problem.prevalence":           # call 52: the event clause, no question
        head = {"key": dimension.key, "event": "could not find their keys on the way out"}
    codes = dimension.fixed_codes
    if codes is None:
        codes = score_mod._ladder_codes(dimension, b2b) or ["first_kind", "second_kind",
                                                            "third_kind", "fourth_kind"]
        if dimension.key == "commercial.existing_sacrifice":
            codes = ["spares", "locksmiths", "taxis", "none"]
    options = [{"label": f"Option {i} for this", "normalized": code,
                "belief_phrase": f"the {code.replace('_', ' ')} answer"}
               for i, code in enumerate(codes, start=1)]
    if dimension.key == "commercial.existing_sacrifice":              # call 54: U1
        for option in options:
            if option["normalized"] != "none":
                option["unit"] = "money"
    return {**head, "options": options, "respondent_note": "asked of the stranger in their own words"}


def calibration_result(registry, vector, *, b2b=False) -> dict:
    """A good answer for the vector's answered slice (calls 47, 61: Purchase friction on B2B only, never the
    derived Ability to pay)."""
    return {"vector": vector, "questions": [calibration_question(d, b2b=b2b)
                                            for d in registry.answered_slice(vector, b2b)]}


def calibration_case(entry, vector, run_index=1):
    from instructions import prompts as prompts_mod                   # noqa: PLC0415
    return prompts_mod.Case(case_id=f"{entry.id}/CALIBRATION_{vector}/run{run_index}",
                            kind="CALIBRATION", entry_id=entry.id,
                            screen="CALIBRATION_QUESTIONS", subject=vector,
                            run_index=run_index, payload={}, meta={"vector": vector})


def respondent_item(entry, key, *, label_only=False) -> dict:
    """An item meeting every §2.2 respondent rule (call 38), written from the golden plan row: the
    code-appended codes (`RESPONDENT_ESCAPES`, *Something else*) left to code; a set carries the
    founder's labels (the fixture records none, so its codes stand in) plus two distractors (a
    categorical pick none); a band, numeric or gate
    control carries `options: None`."""
    from instructions.registry import RESPONDENT_ESCAPES             # noqa: PLC0415
    row = entry.respondent_questions[key]
    item = {"key": key, "question": f"Thinking about that time: {key.split('.')[1].replace('_', ' ')}?"}
    from instructions.registry import GATE_CONTROL, NUMERIC_RESPONDENT_CONTROLS  # noqa: PLC0415
    if row["control"] == "price_ladder":                # call 53: code's whole item
        return {"key": key}
    if row["control"] == GATE_CONTROL:                  # call 52: the event clause
        return {"key": key, "event": "lose your keys on the way out", "options": None}
    if row["control"] in NUMERIC_RESPONDENT_CONTROLS:   # call 52: framed on 7 nights, no text
        return {"key": key, "options": None}
    dimension = entry.registry.by_key(key)
    is_set = (dimension.fixed_codes is None and not dimension.founder_numeric
              and not dimension.derived and row["control"] != "multi_choice_ladder")
    options = []
    for i, code in enumerate(c for c in row.get("codes") or [] if c not in RESPONDENT_ESCAPES):
        label = code if is_set else f"Choice {i + 1}"
        options.append(label if label_only else {"label": label, "code": code})
    if is_set and dimension.normalized.get("kind") != "categorical":
        for n in ("one", "two"):
            label = f"A distractor {n}"
            options.append(label if label_only else {"label": label, "code": f"distractor_{n}"})
    item["options"] = options
    if key == "commercial.existing_sacrifice":          # call 62: W10, the founder's recall words
        item["question"] = f"Thinking about {context_mod.cost_recall_of(entry)}: what did this cost you?"
    if key == "commercial.existing_sacrifice":          # call 54: U1, one unit per option
        item["units"] = ["money"] * len(options)
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
