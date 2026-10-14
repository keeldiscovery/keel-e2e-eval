"""Parity: `instructions.brief.reading_problems` against keel-cloud's own `screenContracts validate` (spec 040, call
82; keel-cloud 089 `BriefReading.check`, refusal `B7`).

The marks restate the aggregate's checks so a reading can be marked offline and re-scored; this is the proof they
are the same checks. The real validator is run **once** over the three scenario fixtures and every mutation below,
and for each case both sides must agree on accepted / refused, and on the fields (`path`) named by each problem. The
validator is handed no participant names, so the names mutation is the one the restatement alone checks.
"""

from __future__ import annotations

import copy
import re

import pytest

from instructions import brief as brief_mod
from instructions import validate as validate_mod
from stack.config import load_config
from tests.test_instruction_brief import SCENARIOS, load


def _stage_broke(fixture):
    """The first stage that broke, for the broke-not-cited mutation; every scenario has one."""
    return next(s for s in ("problem", "solution", "commercial") if fixture["facts"][s].get("broke"))


MUTATIONS = {
    "long-sentence": lambda r, f: r["headline"].update(text="x" * 401),
    "three-sentences": lambda r, f: r["problem"]["answer"].update(text="It holds. It is common. It is costly."),
    "forty-six-words": lambda r, f: r["headline"].update(text=" ".join(["word"] * 46) + "."),
    "fourth-test": lambda r, f: r["next"]["tests"].extend(
        {"key": f["facts"]["targets"][0]["key"], "text": "Ask more."} for _ in range(4)),
    "third-quote": lambda r, f: r.update(quotes=(r["quotes"] or []) * 3),
    "foreign-key": lambda r, f: r["headline"].update(cites=["problem.nonsense"]),
    "wrong-vector": lambda r, f: r["solution"]["answer"]["cites"].append("commercial.price"),
    "no-cite": lambda r, f: r["headline"].update(cites=[]),
    "broke-not-cited": lambda r, f: r[_stage_broke(f)]["answer"].update(
        cites=[k for k in f["facts"]["keys"] if k.startswith(_stage_broke(f) + ".")
               and k != f["facts"][_stage_broke(f)]["broke"]["key"]][:1]),
    "bad-target": lambda r, f: r["next"]["tests"][0].update(key="problem.nonsense"),
    "any-vector-headline": lambda r, f: r["headline"].update(
        cites=["solution.compatibility", "problem.prevalence"]),
    "invented-number": lambda r, f: r["headline"].update(text="Not yet: 77 of 12 had it."),
    "foreign-currency": lambda r, f: r["commercial"]["answer"].update(text="Start at ¥5 a month."),
    "digit-in-test": lambda r, f: r["next"]["tests"][0].update(text="Ask 5 more people."),
    "word-in-test": lambda r, f: r["next"]["tests"][0].update(text="Ask three more people."),
    "paraphrase": lambda r, f: r["quotes"][0].update(text="Something nobody said at all."),
    "stranger": lambda r, f: r["quotes"][0].update(invitationId="someone-else"),
    "will-pay": lambda r, f: r["solution"]["answer"].update(text="They will pay for it."),
    "proves": lambda r, f: r["solution"]["answer"].update(text="It proves the idea."),
    "it-works": lambda r, f: r["solution"]["answer"].update(text="It works."),
    "web": lambda r, f: r["solution"]["answer"].update(text="See keel.example.com."),
    "old-tiles": lambda r, f: (r.clear(), r.update(
        headline={"text": "Not yet.", "cites": ["problem.prevalence"]},
        tiles={"problem": {"text": "Holding up.", "cites": ["problem.prevalence"]}},
        problem={"conclusion": {"text": "It holds.", "cites": ["problem.prevalence"]}},
        next={"sentence": {"text": "Ask more.", "cites": ["problem.prevalence"]}, "tests": []}, quotes=[])),
    "old-paragraph": lambda r, f: (r.clear(), r.update(whatThisSays="A paragraph.")),
}

#: A limit keel-cloud holds in the response *schema* (`ScreenResponseContracts`), before `check` runs: the
#: validator accepts it, the restatement's `shape` mark refuses it (and says why).
SCHEMA_ONLY = {"long-sentence"}
#: Allowed on both sides: the headline cites any vector.
ALLOWED = {"any-vector-headline"}


def _paths(messages):
    return sorted(m.split(": ", 1)[0] for m in messages)


@pytest.fixture(scope="module")
def judged(tmp_path_factory):
    keel_cloud = load_config(validate=False).keel_cloud
    if not (keel_cloud / "gradlew").is_file():
        pytest.skip("no keel-cloud checkout to run `screenContracts validate` against")
    cases = []
    for name in SCENARIOS:
        fixture = load(name)
        cases.append((f"{name}", fixture))
        for label, edit in MUTATIONS.items():
            mutated = copy.deepcopy(fixture)
            edit(mutated["result"], fixture)
            cases.append((f"{name}/{label}", mutated))
    batch = {"cases": [{**{k: v for k, v in f.items() if not k.startswith("_")}, "case_id": cid}
                       for cid, f in cases]}
    directory = tmp_path_factory.mktemp("brief-parity")
    report = validate_mod.run(keel_cloud, batch, directory / "batch.json", directory / "report.json")
    return cases, {entry["case_id"]: entry for entry in report}


def test_the_restatement_and_the_validator_agree_on_every_case(judged):
    cases, report = judged
    refused = 0
    for cid, fixture in cases:
        mine = brief_mod.reading_problems(fixture["result"], fixture["facts"],
                                          {s["invitation_id"]: s["story"] for s in fixture["stories"]})
        entry = report[cid]
        if cid.split("/")[-1] in SCHEMA_ONLY:
            assert entry["accepted"] and [m for m, _ in mine] == ["shape"], (cid, mine)
            continue
        if entry["accepted"]:
            assert not mine, (cid, mine)
            continue
        refused += 1
        assert entry["refusal"]["rule"] == "B7", (cid, entry["refusal"])
        theirs = re.findall(r"(?:^|; )([A-Za-z0-9_.\[\]]+): ", entry["refusal"].get("message") or "")
        assert _paths([m for _, m in mine]) == sorted(theirs), (cid, mine, theirs)
    assert refused == (len(MUTATIONS) - len(SCHEMA_ONLY) - len(ALLOWED)) * len(SCENARIOS), \
        "every mutation is refused, bar the one that is allowed and the one the schema holds"


def test_the_three_good_scenarios_are_accepted_by_the_real_validator(judged):
    _cases, report = judged
    for name in SCENARIOS:
        assert report[name]["accepted"] is True, report[name]


def test_the_allowed_mutation_is_the_one_the_validator_allows(judged):
    _cases, report = judged
    assert all(report[f"{n}/any-vector-headline"]["accepted"] for n in SCENARIOS)
    accepted = [f"{n}/{m}" for n in SCENARIOS for m in MUTATIONS
                if m not in ALLOWED | SCHEMA_ONLY and report[f"{n}/{m}"]["accepted"]]
    assert not accepted


def test_the_new_clauses_are_named_as_the_validator_names_them(judged):
    """089's two new clauses -- the length and the broke cite -- come back from the validator with the path the
    restatement names."""
    _cases, report = judged
    for name in SCENARIOS:
        assert "text: 3 sentences; at most 2" in report[f"{name}/three-sentences"]["refusal"]["message"]
        assert "words; at most 45" in report[f"{name}/forty-six-words"]["refusal"]["message"]
        assert "broke on" in report[f"{name}/broke-not-cited"]["refusal"]["message"]


def test_names_are_the_one_check_only_the_restatement_makes():
    fixture = load("not-yet")
    result = copy.deepcopy(fixture["result"])
    result["solution"]["answer"]["text"] += " Ann said so."
    found = brief_mod.reading_problems(result, fixture["facts"], {}, names=["Ann"])
    assert any("names a person ('Ann')" in m for _, m in found)
