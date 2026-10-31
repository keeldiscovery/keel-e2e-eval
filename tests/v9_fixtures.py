"""Shared, hand-checkable fixtures for the instruction-eval tests (spec 029 T004-T006; at `MARKS_VERSION` 18 since
spec 040: registry 4, corpus revision 10, contract 13).

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
ENTRY = FIXTURES / "corpus" / "09-fixture.yaml"
ENTRY_B2B = FIXTURES / "corpus" / "10-fixture-b2b.yaml"
COMPARE = FIXTURES / "compare"
V8_BUNDLE = FIXTURES / "runs" / "v8-bundle"

#: Why a test reading keel-cloud's canon corpus skips: the canon is not at the reader's revision (calls 49, 78, 110 --
#: there is no fixture fallback; keel-cloud 124 carries revision 13, spec 064).
CANON_NOT_R13 = ("keel-cloud's canon corpus is not at revision 13 (keel-cloud 124) -- spec 064 reads "
                 "the corpus from keel-cloud's canon and nowhere else (judgement calls 49, 78, 110)")


def canon_dir() -> Path:
    """keel-cloud's corpus directory, as `stack.toml` names the checkout."""
    from stack.config import load_config                              # noqa: PLC0415
    return corpus_mod.corpus_dir(load_config(validate=False).keel_cloud)


def canon_entry(name: str) -> Path:
    """One of keel-cloud's revision-13 entries (`03-lullaby.yaml`...), or a skip naming why."""
    import pytest                                                     # noqa: PLC0415
    path = canon_dir() / name
    try:
        revision = yaml.safe_load(path.read_text(encoding="utf-8")).get("revision")
    except (OSError, AttributeError, yaml.YAMLError):
        revision = None
    if revision != corpus_mod.REVISION:
        pytest.skip(CANON_NOT_R13)
    return path



def registry():
    return registry_mod.load(SLICE)


def registry_document() -> dict:
    return yaml.safe_load(SLICE.read_text(encoding="utf-8"))


def entry(path=ENTRY):
    return corpus_mod.load_file(path, registry=registry())


def raw_entry(path=ENTRY) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def write_entry(tmp_path, raw: dict, name="09-fixture.yaml") -> Path:
    path = Path(tmp_path) / name
    path.write_text(yaml.safe_dump(raw, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def write_export(directory, *, with_registry=True, routing=None, keys=None) -> Path:
    """An exported contract in 058's requested shape: the eight model screens (contract 13), each with the
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


#: A list draft that meets every L rule (and, with a face, the K rules) -- the green half the scorer's red halves
#: mutate by one thing.
GOOD_LISTS = {
    # spec 091 FR-1 (founder-lists.md's `rival_list`): the seed-time job's `answers` is `{}`, so a draft that meets
    # every L rule is the problem itself alone; the four rivals were the save's count (`saves`), never the draft's
    "problem.importance": {"items": [{"label": "Finding the keys on the way out"}]},
    # spec 093 FR-3 (keel-cloud 161 L1): a draft that meets every L rule writes the act bare
    "problem.current_solution_satisfaction": {"phrase": "finding them",
                                              "items": [{"label": "Found them straight away"},
                                                        {"label": "Found them after a quick look"},
                                                        {"label": "It took a full search"},
                                                        {"label": "Found them only after being late"},
                                                        {"label": "Never found them that morning"}]},
    "solution.compatibility": {"items": [{"label": "They had a phone to hand",
                                          "asked": "did you have your phone to hand"},
                                         {"label": "Their keys were on one ring",
                                          "asked": "were your keys all on one ring"}]},
    "solution.relative_advantage": {"items": [{"label": "A shorter search"}]},
    "solution.adoption_friction": {"items": [{"label": "Clip a tag to the key ring",
                                              "asked": "you'd clip a tag to your key ring, once"}]},
    "commercial.buyer_payer_alignment": {"items": [{"label": "The office manager"}]},
    "commercial.purchase_friction": {"items": [{"label": "The office manager's sign-off"},
                                               {"label": "A security check", "suggested": True}]},
    "commercial.commitment": {"items": [{"label": "install the app"}]},
}

#: The five fifths Prevalence is written as (C2-C4).
FIFTHS = [("Fewer than 2 in 10", "Only a few"), ("2 to 4 in 10", "A minority"), ("4 to 6 in 10", "Around half"),
          ("6 to 8 in 10", "Most"), ("8 to 10 in 10", "Nearly all")]


def calibration_question(dimension, *, b2b=False) -> dict:
    """An entry that meets every rule the founder-lists job is held to for `dimension` (calls 83, 85)."""
    import copy                                                       # noqa: PLC0415
    note = "asked of the stranger in their own words"
    if dimension.key == "problem.prevalence":
        return {"key": dimension.key, "event": "could not find their keys on the way out",
                "options": [{"label": label, "belief_phrase": phrase} for label, phrase in FIFTHS],
                "respondent_note": note}
    if dimension.founder_list:
        return {"key": dimension.key, "list": copy.deepcopy(GOOD_LISTS[dimension.key]), "respondent_note": note}
    return {"key": dimension.key, "respondent_note": note}


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


def respondent_item(entry, key) -> dict:
    """An item meeting keel-cloud 088's respondent rule: the key alone, and on the gate its `event` clause."""
    if key == "problem.prevalence":
        return {"key": key, "event": "lose your keys on the way out"}
    return {"key": key}


def respondent_result(entry, part, *, link="PRIMARY") -> dict:
    keys = entry.plan()[part]
    return {"part": part, "link": link, "items": [respondent_item(entry, k) for k in keys]}


def asked_case(entry, key="solution.compatibility", run_index=1):
    """An `ASKED` case on the entry's own list (spec 040), its items by index."""
    from instructions import context as context_mod                   # noqa: PLC0415
    from instructions import prompts as prompts_mod                   # noqa: PLC0415
    context = context_mod.build_asked(entry, key)
    subject = prompts_mod.ASKED_SUBJECTS[key]
    return prompts_mod.Case(case_id=f"{entry.id}/ASKED_{subject}/run{run_index}", kind="ASKED",
                            entry_id=entry.id, screen="ASKED", subject=subject, run_index=run_index,
                            payload={"context": context},
                            meta={"dimension": key, "items": list(context["items"])})


def asked_result(entry, key="solution.compatibility") -> dict:
    """The corpus's own faces, as the model would return them."""
    saved = entry.founder_list(key) or {}
    return {"items": [{"index": i, "asked": item.get("asked")} for i, item in enumerate(saved.get("items") or [])]}


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


def skip_a_spoken_record_before_159(keel_cloud) -> None:
    """Spec 089: keel-cloud's `build/spoken-corpus.txt` is a Gradle run's output, not the checkout's -- one written before
    keel-cloud 158 / 159 says Importance's *; pick two* and Relative advantage's `yes_no_per_benefit`, which the spoken
    rules now refuse. Such a record is skipped by name (rerun its SpokenGuidelinesCorpusTest to compare)."""
    import pytest                                                     # noqa: PLC0415
    from instructions import cloud_corpus as cloud_mod                # noqa: PLC0415
    path = Path(keel_cloud) / cloud_mod.SPOKEN_FILE
    record = path.read_text(encoding="utf-8") if path.is_file() else ""
    if "; pick two." in record or "yes_no_per_benefit" in record:
        pytest.skip("keel-cloud's build/spoken-corpus.txt predates keel-cloud 158 / 159 (a count line says '; pick two', "
                    "an item transforms 'yes_no_per_benefit') -- rerun `./gradlew test --tests "
                    "'*SpokenGuidelinesCorpusTest'` in the keel-cloud checkout to compare")


#: keel-cloud 170 FR-5 (spec 110 FR-2): Existing sacrifice's registry escape, *I don't know* before 170.
SACRIFICE_ESCAPE_BEFORE_170 = "I don't know"


def skip_a_spoken_record_before_170(keel_cloud, registry) -> None:
    """Spec 110 FR-2: keel-cloud 170 moved Existing sacrifice's registry escape to *I can't recall* (the code
    `dont_know` unmoved). `build/spoken-corpus.txt` writes the escape the registry named when its Gradle run ran, so a
    record written before 170 against the registry of record after it reads *I don't know* where the registry says *I
    can't recall* -- the record's age, not a fault of the record or of S6. Such a record is skipped by name (rerun its
    SpokenGuidelinesCorpusTest to compare)."""
    import pytest                                                     # noqa: PLC0415
    from instructions import cloud_corpus as cloud_mod                # noqa: PLC0415
    from instructions import spoken as spoken_mod                     # noqa: PLC0415
    from instructions.registry import SACRIFICE_KEY                   # noqa: PLC0415
    path = Path(keel_cloud) / cloud_mod.SPOKEN_FILE
    record = path.read_text(encoding="utf-8") if path.is_file() else ""
    stale = f"{SACRIFICE_KEY} [part 3]\n  Q: " in record and any(
        block.split("\n  escape: ", 1)[-1].split("\n", 1)[0] == SACRIFICE_ESCAPE_BEFORE_170
        for block in record.split(f"{SACRIFICE_KEY} [part 3]\n")[1:])
    if stale and registry is not None and registry.has(SACRIFICE_KEY) \
            and spoken_mod.registry_escape(registry, SACRIFICE_KEY) != SACRIFICE_ESCAPE_BEFORE_170:
        pytest.skip("keel-cloud's build/spoken-corpus.txt predates keel-cloud 170 (Existing sacrifice's escape reads "
                    f"{SACRIFICE_ESCAPE_BEFORE_170!r}; the registry of record names "
                    f"{spoken_mod.registry_escape(registry, SACRIFICE_KEY)!r}) -- rerun `./gradlew test --tests "
                    "'*SpokenGuidelinesCorpusTest'` in the keel-cloud checkout to compare")
