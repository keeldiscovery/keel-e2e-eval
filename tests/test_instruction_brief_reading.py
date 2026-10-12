"""Parity: `instructions.brief.reading_problems` against keel-cloud's own `screenContracts validate`
(spec 034 FR-004; keel-cloud 079 `BriefReading.check`, refusal `B7`).

The marks restate the aggregate's checks so a reading can be marked offline and re-scored; this is the
proof they are the same checks. The real validator is run **once** over the three scenario fixtures and
every mutation below, and for each case both sides must agree on accepted / refused, and on the
fields (`path`) named by each problem. The validator is handed no participant names, so the names
mutation is the one the restatement alone checks.
"""

from __future__ import annotations

import copy
import re
import json

import pytest

from instructions import brief as brief_mod
from instructions import validate as validate_mod
from stack.config import load_config
from tests.test_instruction_brief import SCENARIOS, load

MUTATIONS = {
    "long-sentence": lambda r: r["headline"].update(text="x " * 201),
    "third-test": lambda r: r["next"]["tests"].extend(
        {"key": "problem.importance", "text": "Ask more."} for _ in range(3)),
    "third-quote": lambda r: r.update(quotes=r["quotes"] * 3),
    "no-tile": lambda r: r["tiles"].pop("solution"),
    "foreign-key": lambda r: r["headline"].update(cites=["problem.nonsense"]),
    "wrong-vector": lambda r: r["tiles"]["problem"].update(cites=["commercial.price"]),
    "no-cite": lambda r: r["tiles"]["problem"].update(cites=[]),
    "thin-infer": lambda r: r["problem"]["infer"].update(cites=["problem.prevalence"] * 2),
    "bad-target": lambda r: r["next"]["tests"][0].update(key="problem.frequency"),
    "any-vector-headline": lambda r: r["next"]["sentence"].update(
        cites=["solution.compatibility", "problem.prevalence"]),
    "invented-number": lambda r: r["tiles"]["problem"].update(text="77 of 12 had one."),
    "dollar": lambda r: r["commercial"]["conclusion"].update(text="Start at $5 a month."),
    "digit-in-test": lambda r: r["next"]["tests"][0].update(text="Ask 5 more people."),
    "word-in-test": lambda r: r["next"]["tests"][0].update(text="Ask three more people."),
    "paraphrase": lambda r: r["quotes"][0].update(text="She cried and I guessed."),
    "stranger": lambda r: r["quotes"][0].update(invitationId="someone-else"),
    "will-pay": lambda r: r["solution"]["conclusion"].update(text="They will pay for it."),
    "proves": lambda r: r["solution"]["conclusion"].update(text="It proves the idea."),
    "it-works": lambda r: r["solution"]["conclusion"].update(text="It works."),
    "web": lambda r: r["solution"]["conclusion"].update(text="See keel.example.com."),
    "sharpest-without-split": lambda r: r.update(
        sharpest={"text": "All of them.", "cites": ["problem.importance"]}),
    "old-paragraph": lambda r: (r.clear(), r.update(whatThisSays="A paragraph.")),
}


#: A limit keel-cloud holds in the response *schema* (`ScreenResponseContracts`), before `check` runs:
#: the validator accepts it, the restatement's `shape` mark refuses it (and says why).
SCHEMA_ONLY = {"long-sentence"}


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
            edit(mutated["result"])
            cases.append((f"{name}/{label}", mutated))
    batch = {"cases": [{**f, "case_id": cid} for cid, f in cases]}
    directory = tmp_path_factory.mktemp("brief-parity")
    report = validate_mod.run(keel_cloud, batch, directory / "batch.json", directory / "report.json")
    return cases, {entry["case_id"]: entry for entry in report}


def test_the_restatement_and_the_validator_agree_on_every_case(judged):
    cases, report = judged
    refused = 0
    for cid, fixture in cases:
        mine = brief_mod.reading_problems(fixture["result"], fixture["facts"],
                                          {s["invitation_id"]: s["story"]
                                           for s in fixture["stories"]})
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
    assert refused == (len(MUTATIONS) - 2) * len(SCENARIOS), \
        "every mutation is refused, bar the one that is allowed and the one the schema holds"


def test_the_three_good_scenarios_are_accepted_by_the_real_validator(judged):
    _cases, report = judged
    for name in SCENARIOS:
        assert report[name]["accepted"] is True, report[name]


def test_the_allowed_mutation_is_the_one_the_validator_allows(judged):
    _cases, report = judged
    assert all(report[f"{n}/any-vector-headline"]["accepted"] for n in SCENARIOS)
    accepted = [f"{n}/{m}" for n in SCENARIOS for m in MUTATIONS
                if m not in ("any-vector-headline", *SCHEMA_ONLY) and report[f"{n}/{m}"]["accepted"]]
    assert not accepted


def test_names_are_the_one_check_only_the_restatement_makes():
    fixture = load("build")
    result = copy.deepcopy(fixture["result"])
    result["solution"]["conclusion"]["text"] += " Ann said so."
    found = brief_mod.reading_problems(result, fixture["facts"], {}, names=["Ann"])
    assert any("names a person ('Ann')" in m for _, m in found)


# ---------------------------------------------- spec 036: keel-cloud 082's split / notTested facts

def _vectors(problem, solution="HOLDING_UP", commercial="HOLDING_UP"):
    dim = {"weight": "DEAL_BREAKER", "status": "HOLDING_UP", "n_anchored": 12}
    return [{"vector": v, "verdict": verdict, "dimensions": [dict(dim, status=verdict)]}
            for v, verdict in (("PROBLEM", problem), ("SOLUTION", solution),
                               ("COMMERCIAL", commercial))]


@pytest.mark.parametrize("vectors, label, split, not_tested", [
    (_vectors("HOLDING_UP"), "BUILD", False, []),
    (_vectors("PEOPLE_DISAGREE"), "NOT_YET", True, []),
    (_vectors("NOT_HOLDING_UP"), "NOT_YET", False, []),
    (_vectors("NOT_TESTED"), "KEEP_INTERVIEWING", False, ["PROBLEM"]),
    (_vectors("HOLDING_UP", commercial="NOT_TESTED"), "KEEP_INTERVIEWING", False, ["COMMERCIAL"]),
    (_vectors("HOLDING_UP", solution="NOT_HOLDING_UP"), "BUILD_BUT_CHANGE", False, []),
])
def test_the_decision_carries_split_and_not_tested(vectors, label, split, not_tested):
    from instructions import brief_facts                                    # noqa: PLC0415
    decision = brief_facts.decision(vectors, b2b=False)
    assert (decision["label"], decision["split"], decision["notTested"]) == (label, split, not_tested)
