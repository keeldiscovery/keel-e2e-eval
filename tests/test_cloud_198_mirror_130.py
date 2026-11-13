"""Spec 130, the mirrors owed by keel-cloud 198 (the strangers' options as a stranger would answer them; keel-cloud-docs
`cd0d736d`).

Ability to pay's five sources (`existing_line · charged_to_users · new_line_signed_off · outside_funding ·
taken_from_other_spend`, `no_budget` retired) and Buyer and payer's order, alone first, read off revision 22 through one
rule (`corpus.spec198_codes`, `spec198_pick`; no corpus revision -- spec 113 / 115's pattern); `charged_to_users` among
the budget supports; Adoption friction's `condition` (screen response contract 25, 155's `only_if` retired) and *Only if
{condition}*; *Or say: I can't say.*; Commitment's *Probably yes* and *Probably, after ... first*; Buyer and payer's
words; the value box's one escape and its unit-alone answer line.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from harness import interviewer_fake as fake
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import brief_facts as bf
from instructions import chain as chain_mod
from instructions import corpus as corpus_mod
from instructions import spoken as spoken_mod
from instructions.registry import ABILITY_KEY, BUYER_KEY
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"


def _cloud(path: str) -> str:
    full = KEEL_CLOUD / path
    if not full.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    return full.read_text(encoding="utf-8")


def _registry() -> dict:
    return json.loads(_cloud("src/main/resources/keel/dimension-registry.json"))


def _row(key: str) -> dict:
    return next(d for d in _registry()["dimensions"] if d["key"] == key)


def _after_198():
    if "charged_to_users" not in _cloud("src/main/resources/keel/dimension-registry.json"):
        pytest.skip("keel-cloud before 198: the registry names the four budget sources")


# ------------------------------------------------------------------------------------------- the codes (FR-4, FR-5)

def test_the_registrys_codes_are_198s():
    _after_198()
    assert tuple(a["code"] for a in _row(ABILITY_KEY)["respondent"]["fixed_answers"]) == corpus_mod.ABILITY_CODES_198
    assert tuple(a["code"] for a in _row(BUYER_KEY)["respondent"]["fixed_answers"]) == corpus_mod.BUYER_CODES_198
    assert tuple(a["code"] for a in _row(BUYER_KEY)["respondent"]["fixed_answers"]) == fake.BUYER_ANSWERS
    assert [a["label"] for a in _row(BUYER_KEY)["respondent"]["fixed_answers"]] == [
        "I decided on my own", "Someone else had to agree", "Several people had to agree", "It was someone else's call"]
    assert tuple(_row(BUYER_KEY)["respondent"]["supports"]) == fake.BUYER_SUPPORTS, "codes and supports unchanged"
    commitment = {a["code"]: a["label"] for a in _row("commercial.commitment")["respondent"]["fixed_answers"]}
    assert commitment["yes_after_trying"] == spoken_mod.PROBABLY_YES == "Probably yes"
    assert corpus_mod.B2B_BUDGET_CODES == corpus_mod.ABILITY_CODES_198


def test_revision_22s_codes_read_as_198_fixes_them_and_the_record_is_never_rewritten():
    old_ability, old_buyer = list(corpus_mod.ABILITY_CODES_197), list(corpus_mod.BUYER_CODES_197)
    assert corpus_mod.spec198_codes(ABILITY_KEY, old_ability) == list(corpus_mod.ABILITY_CODES_198)
    assert corpus_mod.spec198_codes(BUYER_KEY, old_buyer) == list(corpus_mod.BUYER_CODES_198)
    # gated on the registry handed: under a registry before 198 the record reads as recorded
    assert corpus_mod.spec198_codes(ABILITY_KEY, old_ability, old_ability) == old_ability
    assert corpus_mod.spec198_codes(BUYER_KEY, old_buyer, corpus_mod.BUYER_CODES_198) == list(corpus_mod.BUYER_CODES_198)
    assert corpus_mod.spec198_codes("commercial.commitment", ["yes_start"]) == ["yes_start"]
    assert old_ability == list(corpus_mod.ABILITY_CODES_197), "the recorded list is not touched"
    # one pick: no_budget is outside_funding (198's own fixture rule); case kept; other codes and keys as they are
    assert corpus_mod.spec198_pick(ABILITY_KEY, "no_budget") == "outside_funding"
    assert corpus_mod.spec198_pick(ABILITY_KEY, "NO_BUDGET") == "OUTSIDE_FUNDING"
    assert corpus_mod.spec198_pick(ABILITY_KEY, "no_budget", corpus_mod.ABILITY_CODES_197) == "no_budget"
    assert corpus_mod.spec198_pick(ABILITY_KEY, "existing_line") == "existing_line"
    assert corpus_mod.spec198_pick(BUYER_KEY, "no_budget") == "no_budget"
    # the value box's one escape since 198 FR-3
    assert corpus_mod.spec198_chip("commercial.existing_sacrifice", "rather_not_say") == "dont_know"
    assert corpus_mod.spec198_chip("problem.current_solution_satisfaction", "rather_not_say") == "rather_not_say"


def test_every_entry_loads_and_a_recorded_no_budget_is_answered_outside_funding():
    _after_198()
    corpus_mod.load(KEEL_CLOUD, backtest=True)                     # every back-test entry loads under 198
    corpus = corpus_mod.load(KEEL_CLOUD)                               # the golden seven: 05 and 06 record no_budget
    recorded = [(e, p) for e in corpus.entries for p in e.answers
                if (p.get("picks") or {}).get(ABILITY_KEY) == "no_budget"]
    assert recorded, "revision 22 records no_budget picks"
    entry, person = recorded[0]
    pick = vs._pick(entry, ABILITY_KEY, person["picks"][ABILITY_KEY])
    assert pick.codes == ["outside_funding"]


def test_the_budget_supports_hold_charged_to_users_and_not_outside_funding():
    _after_198()
    chain = _cloud(VECTORS + "CommercialChain.java")
    assert re.search(r'BUDGET_SUPPORTS = List\.of\(FROM_SPEND, "existing_line", "charged_to_users",\s*'
                     r'"taken_from_other_spend"\)', chain)
    assert chain_mod.BUDGET_SUPPORTS == vs_screens.BUDGET_SUPPORTS == (
        "from_spend", "existing_line", "charged_to_users", "taken_from_other_spend")
    assert "outside_funding" not in chain_mod.BUDGET_SUPPORTS


# ------------------------------------------------------------------------------------ the words (FR-1, FR-2, FR-4)

def test_buyer_and_payer_says_the_persons_own_answer_first_with_no_yes_or_no_in_front():
    _after_198()
    frames = _cloud(VECTORS + "ItemFrames.java")
    for said in ('"I could sign off myself"', '" would have to agree"', '"Several people would have to agree"',
                 '"It\'s someone else\'s call"', '" had to agree"'):
        assert said in frames, said
    labels = spoken_mod.buyer_answers("CFO")
    assert labels == ["I decided on my own", "The CFO had to agree", "Several people had to agree",
                      "It was someone else's call", "I could sign off myself", "The CFO would have to agree",
                      "Several people would have to agree", "It's someone else's call"]
    assert spoken_mod.buyer_answers("their partner")[1] == "My partner had to agree"
    assert spoken_mod.buyer_answers(None)[1] == "Someone else had to agree"
    assert spoken_mod.buyer_answers(None)[5] == "Someone else would have to agree"
    assert not [x for x in labels if x.startswith(("Yes", "No"))]


def test_commitments_soft_yes_is_on_every_list():
    _after_198()
    frames = _cloud(VECTORS + "ItemFrames.java")
    assert 'return "Probably, after " + step' in frames and 'PROBABLY_YES = "Probably yes"' in frames
    assert spoken_mod.second_yes("A free trial") == "Probably, after a free trial first"
    assert spoken_mod.second_yes("a look at it first") == "Probably, after a look at it first"
    assert spoken_mod.second_yes_118("A free trial") == "Yes, after a free trial first"
    facts = _cloud(APPLICATION + "BriefFacts.java")
    # spec 141 FR-4 (keel-cloud 221 FR-2): the smaller step as the soft yes says it (`ItemFrames.smallerSaid`)
    assert 'PROBABLY = "said probably"' in facts and '"probably, after "' in facts and 'smallerSaid(smaller) + " first"' \
        in facts
    assert bf.SAID_PROBABLY == "said probably"


def test_i_cant_say_is_said_as_itself():
    _after_198()
    spoken = _cloud(VECTORS + "SpokenForm.java")
    assert 'return "Or say: " + CANT_SAY + ".";' in spoken and 'CANT_SAY = "I can\'t say"' in spoken
    assert spoken_mod.escape_line("I can't say") == "Or say: I can't say."
    assert spoken_mod.escape_line("I can't recall") == "Or say you can't recall."
    assert spoken_mod.escape_line("I can't tell") == "Or say you can't tell."
    assert spoken_mod.escape_line(None) is None


def test_the_value_box_has_one_escape_and_says_its_unit_alone():
    _after_198()
    spoken = _cloud(VECTORS + "SpokenForm.java")
    assert 'VALUE_BOX_ANSWER_LINE = "A number, in the unit on the screen.";' in spoken
    assert vs.value_box_escapes(True) == vs.value_box_escapes(False) == ["DONT_KNOW"]
    assert vs.value_box_answer_line({"mode": "HOURS"}, "hours per site last month") == \
        "A number of hours per site last month."


# ------------------------------------------------------------------- Adoption friction's condition (FR-9, contract 25)

def test_screen_response_contract_25_names_condition_where_only_if_was():
    _after_198()
    contracts = _cloud(APPLICATION + "ScreenResponseContracts.java")
    assert re.search(r"public static final int CONTRACT_VERSION = (25|26);", contracts)   # 26 at keel-cloud 245 (spec 154)
    assert 'properties.put("condition", described(ONLY_IF_MAX, CONDITION_RULE));' in contracts
    assert 'properties.put("only_if", described(ONLY_IF_MAX, ONLY_IF_RULE));' not in contracts
    asked = _cloud(APPLICATION + "AskedRules.java")
    assert "static final int ONLY_IF_MAX_WORDS = 7;" in asked and '"K8: write this "' in asked


def test_the_scripted_asked_result_writes_condition_and_never_only_if():
    class Entry:
        id = "x"

        @staticmethod
        def founder_list(key):
            return {"items": [{"code": "a", "label": "Scan each delivery", "asked": "scan each delivery",
                               "only_if": "it works offline"},
                              {"code": "b", "label": "Keep a phone", "asked": "keep a phone near the door"}]}

    out = vs.asked_result(Entry(), "solution.adoption_friction")
    # spec 129 (keel-cloud 200 FR-1): a faced row also carries its hidden short name where the scripted writer names it
    assert out["items"][0] == {"index": 0, "asked": "scan each delivery", "condition": "it works offline",
                               "short_name": "scanning each delivery"}
    # spec 154 FR-0 (keel-cloud 245 FR-2, K8 strict on the first turn): every Adoption friction row carries a condition --
    # a row the entry records none for is handed the step's own (`adoption_condition`), never left without one
    assert out["items"][1] == {"index": 1, "asked": "keep a phone near the door", "short_name": "keeping a phone",
                               "condition": vs.adoption_condition({"label": "Keep a phone"})}
    assert out["items"][1]["condition"] == "keeping a phone never slowed my work"
    assert all("only_if" not in i for i in out["items"])
    assert "condition" not in vs.asked_result(Entry(), "solution.compatibility")["items"][0]


def test_the_conditional_yes_is_counted_in_the_strangers_own_words():
    assert bf.only_if_words({"label": "Scan each delivery", "condition": "it works offline"}) == \
        "only if it works offline"
    assert bf.only_if_words({"label": "Scan each delivery"}) == bf.ONLY_IF_WORDS == "if it was clearly worth it"
    assert fake.ONLY_IF == spoken_mod.ONLY_IF == "Only if "
