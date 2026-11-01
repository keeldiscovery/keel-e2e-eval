"""Spec 124 -- the referee follows keel-cloud 194 (the condition's clip, contract 57; keel-cloud-docs `2d848360`).

FR-1 `ClipKind.CONDITION` and its words (*{question} Yes or no.*); FR-2 the recording's spoken order and framing
expect it where the link asks a condition, and a lock from before 194 is not refused; FR-3 the problem passage's
checks sentence and the opening's checked route, as `PassageComposer` serves them; FR-4 contract 57.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from evals import interviewer_leg as il
from evals import interviewer_marks as im
from harness import interviewer_fake as fake
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
COMPOSER = "src/main/java/com/keeldiscovery/cloud/application/interviewer/PassageComposer.java"


def _cloud(path: str) -> str:
    full = KEEL_CLOUD / path
    if not full.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    return full.read_text(encoding="utf-8")


def _constant(text: str, name: str) -> str | None:
    """A `static final String NAME = "..." + "...";` constant, its pieces joined."""
    m = re.search(rf"\b{name} =\s*((?:\"[^\"]*\"\s*\+?\s*)+);", text)
    return "".join(re.findall(r'"([^"]*)"', m.group(1))) if m else None


# --------------------------------------------------------------------------------------------- FR-1 / FR-3

@pytest.mark.parametrize("name", ["CHECKED_COMMERCIAL_ROUTE", "CHECKS", "YES_OR_NO", "COMMERCIAL_ROUTE", "FULL_ROUTE"])
def test_194s_lines_are_the_composers_own(name):
    text = _cloud(COMPOSER)
    if "CHECKED_COMMERCIAL_ROUTE" not in text:
        pytest.skip("keel-cloud predates spec 194")
    assert _constant(text, name) == getattr(fake, name), name


def test_the_condition_clip_and_the_counts_say_194s_words():
    """194's tasks.md, *As composed*: the payroll practitioner's passage and condition, the decision-maker's opening."""
    assert fake.condition_clip("Do you run payroll for at least 50 employees?") == \
        "Do you run payroll for at least 50 employees? Yes or no."
    assert fake.condition_clip("  ") is None and fake.condition_clip(None) is None
    assert fake.problem_passage("", 3, gated=True) == (
        "That's the problem. Take a moment with it. First a quick check or two that this is for you. Then I'll ask you "
        "three questions about it.")
    assert fake.checks(0, "about it") == fake.CHECKS, "the anchor alone: the first sentence alone"
    assert fake.checks(1, "about it").endswith("Then I'll ask you one question about it.")
    assert fake.problem_passage("", 4) == ("That's the problem. Take a moment with it. Then I'll ask you four questions "
                                           "about it."), "an ungated part 1 keeps today's sentence"
    assert fake.opening("Athul", True, checked=True) == (
        "I'm Keel's interviewer. I'm an AI, not a person. Athul has an idea for a problem you may know. First a quick "
        "check that this is for you. Then the idea, and a few questions on the money side. Say the answer that fits, or "
        "tap it.")
    assert fake.opening("Athul", True) == fake.opening("Athul", True, checked=False) != fake.opening("Athul", True,
                                                                                                     checked=True)
    # money alone's person link (no gate) asks its condition before the idea too
    assert fake.opening(None, False, checked=True).count(fake.CHECKED_COMMERCIAL_ROUTE) == 1


def test_the_condition_a_link_asks():
    gated = {"kind": "FULL", "gate": {"condition": {"question": "Do you run payroll?", "inCodes": ["YES"]}}}
    assert fake.condition_of(gated)["question"] == "Do you run payroll?"
    assert fake.condition_of({"kind": "COMMERCIAL_LINK", "condition": {"question": "Does your team call?"}})
    assert fake.condition_of({"kind": "COMMERCIAL_LINK"}) is None
    assert fake.condition_of({"kind": "FULL", "gate": {"condition": {"question": " "}}}) is None
    assert il._condition_place(gated) == {"where": "gate", "script": "Do you run payroll? Yes or no."}
    assert il._condition_place({"kind": "COMMERCIAL_LINK", "condition": {"question": "Q?"}})["where"] == "idea"


def test_the_kinds_carry_condition_last_and_in_the_spoken_order():
    assert fake.KINDS[-1] == "CONDITION" and "CONDITION" not in fake.UNSPOKEN
    text = _cloud("src/main/java/com/keeldiscovery/cloud/domain/interviewer/ClipKind.java")
    assert re.search(r"^\s+CONDITION;", text, re.M)


# ------------------------------------------------------------------------------------------------- FR-2

def _role(kind, parts, condition=None):
    return {"kind": kind, "parts": parts, "condition": condition}


def test_im3_expects_the_condition_where_the_link_asks_one():
    gate_dim = "problem.prevalence"
    full = _role("FULL", [{"part": 1, "items": [gate_dim, "problem.frequency"]}, {"part": 2, "items": ["s.a"]}],
                 {"where": "gate", "script": "Q? Yes or no."})
    assert im._expected_kinds(full) == [
        ("OPENING", None), ("PROBLEM", None), ("CONDITION", None), ("ITEM", gate_dim), ("ITEM", "problem.frequency"),
        ("SOLUTION", None), ("ITEM", "s.a"), ("PILOT", None), ("THANKS", None)]
    decider = _role("COMMERCIAL_LINK", [{"part": 3, "items": ["commercial.price"]}], {"where": "idea", "script": "x"})
    assert im._expected_kinds(decider)[:3] == [("OPENING", None), ("CONDITION", None), ("SOLUTION", None)]
    # a lock from before 194 (no CONDITION clip) is read as before -- not refused
    assert ("CONDITION", None) not in im._expected_kinds(full, with_condition=False)
    assert ("CONDITION", None) not in im._expected_kinds(_role("FULL", full["parts"]))


def _recording(role, kinds):
    return {"recording": {"clips": [{"role": role, "kind": k, "itemId": i} for k, i in kinds]
                          + [{"role": role, "kind": "DIDNT_CATCH"}, {"role": role, "kind": "IS_THAT_RIGHT"}]}}


def test_spoken_order_holds_a_set_with_the_clip_and_a_set_from_before_194():
    parts = [{"part": 1, "items": ["problem.prevalence", "problem.frequency"]}]
    role = _role("FULL", parts, {"where": "gate", "script": "Q? Yes or no."})
    since = [("OPENING", None), ("PROBLEM", None), ("CONDITION", None), ("ITEM", "problem.prevalence"),
             ("ITEM", "problem.frequency"), ("PILOT", None), ("THANKS", None)]
    before = [k for k in since if k[0] != "CONDITION"]
    for kinds in (since, before):
        r = {**_recording("PRIMARY", kinds), "roles": {"PRIMARY": role}}
        ok, out = im.spoken_order(r)
        assert ok, out
    misplaced = [since[0], since[2], since[1]] + since[3:]
    assert not im.spoken_order({**_recording("PRIMARY", misplaced), "roles": {"PRIMARY": role}})[0]


def test_the_framing_words_on_a_gated_link_and_the_deciders():
    served = {"kind": "FULL", "founderFirstName": "Athul", "topic": "Payroll runs late.",
              "gate": {"dimension": "problem.prevalence", "condition": {"question": "Do you run payroll?"}}}
    role = {"parts": [{"part": 1, "items": ["problem.prevalence", "a", "b", "c"]}]}
    words = il._framing_words(served, role)
    assert words["PROBLEM"]["whole"].endswith("First a quick check or two that this is for you. Then I'll ask you "
                                              "three questions about it."), "the gate is not counted"
    assert words["CONDITION"] == {"whole": "Do you run payroll? Yes or no."}
    assert fake.FULL_ROUTE in words["OPENING"]["whole"]
    old = il._framing_words(served, role, with_condition=False)
    assert "CONDITION" not in old and old["PROBLEM"]["whole"].endswith("Then I'll ask you four questions about it.")
    decider = {"kind": "COMMERCIAL_LINK", "condition": {"question": "Does your team call patients?"},
               "idea": {"problem": None}}
    dwords = il._framing_words(decider, {"parts": [{"part": 3, "items": ["x", "y"]}]})
    assert fake.CHECKED_COMMERCIAL_ROUTE in dwords["OPENING"]["whole"]
    assert dwords["SOLUTION"]["ends"].endswith("Then I'll ask you two questions on whether it would help you.")


def test_the_words_before_101_read_past_the_checks():
    problem = fake.problem_passage("Payroll runs late.", 3, gated=True)
    assert fake.before_101("PROBLEM", problem) == "Payroll runs late. I'll ask you three questions about that."


# ------------------------------------------------------------------------------------------------- FR-4

def test_contract_57_serves_the_condition_clip():
    """Contract 57 (keel-cloud 194 FR-1): `InterviewerPlayer.clips.condition`, optional (a lock from before 194 has
    none); nothing else the harness reads moved."""
    spec = _cloud("canon/openapi-v2.yaml")
    assert int(re.search(r"x-keel-contract: (\d+)", spec).group(1)) >= 57
    import yaml                                                         # noqa: PLC0415
    schemas = (yaml.safe_load(spec).get("components") or {}).get("schemas") or {}
    clips = ((schemas["InterviewerPlayer"].get("properties") or {}).get("clips") or {})
    props = clips.get("properties") or {}
    assert "condition" in props, sorted(props)
    assert "condition" not in (clips.get("required") or []), "optional: a lock from before 194 has none"
    assert {"opening", "problem", "solution"} <= set(props), sorted(props)
