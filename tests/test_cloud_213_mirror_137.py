"""Spec 137 -- the harness mirrors keel-cloud 213 (the money beliefs keep every term; a draft row is never cut;
keel-cloud-docs `219464f9`, contract 59) and walks keel-web 173 (contract 59 on the money and Check screens).

FR-1 the cards, byte for byte the vendored copy at 213's `CARDS_SHA256`. FR-2 the instruction and rule mirrors
(`chain`: the price whole, the optional plan, one measure on a percent of a named base; `corpus`: the cost's payer the
decider's plural, Current solution's act bare, Compatibility's owned subject, read through `spec213_reads` /
`spec213_chain` until a corpus revision records 213's words; `step_cost`: moved money; `spoken`: Relative advantage's
*{Name}, {what it is}*, Buyer and payer's share stem, Commitment's four answers and note). FR-3 the walk on contract 59
(the price's two plan boxes and *Optional plan*, the PUT, Commitment's Check block, the role rows' tags, the strings).
FR-4 the entries' prices (Codyco's range, AirCaps' optional plan read off its sources file).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.steps import Recorder
from instructions import chain as chain_mod
from instructions import corpus as corpus_mod
from instructions import spoken as spoken_mod
from instructions import step_cost as step_cost_mod
from quality import cards
from stack.config import load_config
from tests import v9_fixtures as fx

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
KEEL_WEB = Path(CONFIG.keel_web)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
CARDS_SHA256_213 = "e3cdea00e2267ec0fcb6dc447d1a43497f85925060bd4996ba3c176e8566f594"
CARDS_SHA256_214 = "0ab29614dee596b55da9e1e9b1033d81a2328c08fa2cea0571c0160536c6f172"
#: Spec 139 FR-1 (keel-cloud 216 FR-6): the No-sayer, the own row the hurt, the frequency frame, the paying unit, the
#: assurance -- the cards' digest since 216.
CARDS_SHA256_216 = "2f1a63ccc481175ff45a540a199c0930c77f4640a64ea0c798f5c2a3c0fdd2c4"
BASE = "http://keel.test"
PALUS_STEP = "move a small part of the reserve"


def _cloud(path: str) -> str:
    target = KEEL_CLOUD / path
    if not target.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    return target.read_text(encoding="utf-8")


def _web(path: str) -> str:
    target = KEEL_WEB / path
    if not target.is_file():
        pytest.skip(f"no {path} at {KEEL_WEB}")
    return target.read_text(encoding="utf-8")


def _gallery(entry_id: str):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no {entry_id} at {path.parent}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


def _golden(entry_id: str):
    return corpus_mod.load_file(fx.canon_entry(f"{entry_id}.yaml"), registry=fx.registry())


# ------------------------------------------------------------------------------------------------ FR-1 the cards

def test_the_cards_are_the_vendored_copy_at_the_clouds_digest():
    """FR-1 (keel-cloud 213 FR-11b, then 214 FR-2): the cloud's copy carries the corpus writer's law at its head, 212's
    cap as its code holds it and (214) Relative advantage's hard case, so the eval's cards are byte for byte the
    vendored file -- `e3cdea00...` at 213, `0ab29614...` at 214."""
    ours = cards.CARDS_PATH.read_bytes()
    review = _cloud("src/main/java/com/keeldiscovery/cloud/application/RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    assert hashlib.sha256(ours).hexdigest() == sha
    assert sha in (CARDS_SHA256_213, CARDS_SHA256_214, CARDS_SHA256_216)     # spec 139 FR-1: 216's digest
    assert (KEEL_CLOUD / "src/main/resources/keel/dimension-cards.md").read_bytes() == ours
    text = " ".join(ours.decode("utf-8").split())
    assert text.count("at most 9 words, 8 on a working-days window: 20 spoken words minus the strangers' frame") == 2
    assert "at most 8 words" not in text
    if sha in (CARDS_SHA256_214, CARDS_SHA256_216):
        assert "*Think of the last {occasion} when {circumstance}. Would {Name}, {what it is}, have done that better " \
               "for you, or not?* -- the hard case the advantage is for" in text


# ------------------------------------------------------------------------------------ FR-2 the price, whole

def _price(**kw) -> dict:
    return {"shape": "UPFRONT_THEN", "upfrontLow": 599, "upfrontHigh": 599, "low": 20, "high": 20, "currency": "USD",
            **kw}


def test_the_up_front_then_price_says_the_plans_range_and_an_optional_plan():
    """keel-cloud 213 FR-1a / FR-1c (`CommercialChain.priceSaid`)."""
    hotel = {"mode": "RATE", "low": 1, "high": 2, "period": "month", "unit": "hotel", "measure": "%"}
    codyco = _price(upfrontLow=3000, upfrontHigh=3000, low=1000, high=1500, currency="EUR")
    assert chain_mod.price_said(codyco, hotel, None, None) == "€3,000 up front, then €1,000 to €1,500 per hotel a month"
    month = {"mode": "MONEY", "low": 4, "high": 8, "period": "month", "currency": "USD"}
    assert chain_mod.price_said(_price(optional=True), month, None, None) == \
        "$599 up front, then an optional $20 a month plan"
    assert chain_mod.price_said(_price(optional=False), month, None, None) == "$599 up front, then $20 a month"
    assert chain_mod.price_said(_price(thenNothing=True, optional=True), month, None, None) == \
        "$599 up front, then nothing"
    assert chain_mod.optional_plan(_price(optional=True)) and not chain_mod.optional_plan(_price())
    chain = _cloud(VECTORS + "CommercialChain.java")
    assert 'upfront + ", then an optional " + plan + " plan"' in chain


def test_a_percent_of_a_named_base_says_one_measure():
    """keel-cloud 213 FR-2b (`percentOfBase`): no *per {unit}* beside a percent of a named base -- the cost's phrase and
    belief, and a share of that base; a share of what it gets back keeps its unit, and a count keeps its noun."""
    palus = {"mode": "RATE", "low": 2, "high": 2, "period": "year", "unit": "company", "measure": "%",
             "base": "the balance"}
    assert chain_mod.percent_of_base(palus, "the balance")
    assert chain_mod.cost_said(palus, None, None) == "about 2% of the balance a year"
    share = {"shape": "SHARE", "low": 0.25, "high": 0.25, "shareBase": "COST_BASE", "currency": "USD"}
    assert chain_mod.price_said(share, palus, None, None) == "0.25% of the balance a year"
    assert chain_mod.price_belief(share, palus, "startup founders", None, None, "founder", "Startup founders", "Palus") \
        == "Startup founders would think a fee of 0.25% of the balance a year fair for Palus."
    back = {**share, "shareBase": "RECOVERED"}
    assert chain_mod.price_said(back, palus, None, None) == \
        "0.25% of what it gets back, only when it does, per company a year"
    count = {**palus, "measure": "conversations", "unit": "person"}
    assert not chain_mod.percent_of_base(count, "the balance")
    assert chain_mod.cost_said(count, None, None) == "about 2 conversations of the balance per person a year"


def test_the_recorded_chain_words_read_by_213s_one_measure_rule():
    """`VectorCorpusFixture.spec213Chain`: revision 24's *of {base} per {unit}* reads *of {base}* on a percent or a
    share of that base, *, each* kept; any other words as recorded."""
    cost = {"mode": "RATE", "measure": "%", "base": "the balance", "unit": "company", "low": 2, "high": 2,
            "period": "year"}
    assert corpus_mod.spec213_chain("about 2% of the balance per company a year", cost, None) == \
        "about 2% of the balance a year"
    assert corpus_mod.spec213_chain("2% of the balance per company, each", cost, None) == "2% of the balance each"
    money = {"mode": "MONEY", "base": "the balance", "unit": "company", "low": 2, "high": 2, "period": "year"}
    assert corpus_mod.spec213_chain("about $2 of the balance per company a year", money, None) == \
        "about $2 of the balance per company a year"
    fixture = _cloud("src/test/java/com/keeldiscovery/cloud/corpus/VectorCorpusFixture.java")
    assert 'recorded.replace(of + per + ", each", of + " each").replace(of + per, of)' in fixture


def test_every_gallery_entry_loads_by_213s_chain_rules():
    """The loader holds every recorded chain sentence to the engine's words read through `spec213_chain`, as
    `BacktestCorpusTest.theChainsWordsAreTheEngines` does."""
    if not corpus_mod.backtest_dir(KEEL_CLOUD).is_dir():
        pytest.skip("no gallery")
    loaded = [corpus_mod.load_file(p, registry=fx.registry(), backtest=True)
              for p in sorted(corpus_mod.backtest_dir(KEEL_CLOUD).glob("*.yaml"))]
    assert len(loaded) >= 14


def test_an_optional_plan_is_refused_off_the_up_front_then_plan(tmp_path):
    """keel-cloud 213 FR-1c (`checkChainPrice`): only a plan after a one-off is optional."""
    import yaml
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "32-frizzle.yaml"
    if not path.is_file():
        pytest.skip("no 32-frizzle")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    raw["founder_calibration"]["commercial.price"]["answer"]["optional"] = True
    with pytest.raises(corpus_mod.CorpusError, match="optional only on UPFRONT_THEN"):
        corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="32-frizzle.yaml"), registry=fx.registry(),
                             backtest=True)


# ----------------------------------------------------------- FR-2 who pays, the act bare, the owned subject

def test_the_b2b_payer_is_the_deciders_word_never_the_buyers_organisation():
    """keel-cloud 213 FR-2a: `CostEstimate.B2B_PAYER` deleted; 199's read of the record retired."""
    estimate = _cloud(VECTORS + "CostEstimate.java")
    assert "the buyer's organisation" not in estimate.split("public static String payer(boolean b2b, String deciders",
                                                            1)[1]
    assert not hasattr(corpus_mod, "B2B_PAYER")
    paidly = _golden("05-paidly")
    key = "commercial.existing_sacrifice"
    assert corpus_mod.engine_belief(paidly, key) == paidly.founder_calibration[key]["belief_sentence"]


def test_current_solutions_belief_reads_the_act_bare():
    """keel-cloud 213 FR-3b (`BeliefSentence.bareAct`, `spec213Reads`)."""
    assert corpus_mod.bare_act("Your way of working out what the baby needed") == "working out what the baby needed"
    assert corpus_mod.bare_act("your notes app") == "their notes app"
    lullaby = _golden("03-lullaby")
    assert corpus_mod.engine_belief(lullaby, corpus_mod.CURRENT_SOLUTION_KEY) == \
        "For most parents of babies under six months, working out what the baby needed still falls short."
    registry = json.loads(_cloud("src/main/resources/keel/dimension-registry.json"))
    assert "For most parents of babies under six months, working out what the baby needed still falls short." in \
        json.dumps(registry)


@pytest.mark.parametrize("condition, people, owned", [
    ("Their bank could link through Plaid.", "finance leads", "finance leads' banks could link through Plaid"),
    ("Your phone was with you and online", "deaf or hard-of-hearing adults",
     "deaf or hard-of-hearing adults' phones were with them and online"),
    ("Their company could wait two days for its cash", "finance leads",
     "finance leads' companies could wait two days for their cash"),
    ("Their phone was with them", "parents of babies under six months", None),
    ("They could link through Plaid", "finance leads", None),
    ("Their manager, the CFO, could sign", "finance leads", None),
])
def test_compatibilitys_owned_subject_is_the_clouds(condition, people, owned):
    """keel-cloud 213 FR-10c (`BeliefSentence.ownedSubject`): the people's own thing read as theirs after *Most*."""
    assert corpus_mod.owned_subject(condition, people) == owned


def test_the_owned_subject_vocabularies_are_the_clouds():
    beliefs = _cloud(VECTORS + "BeliefSentence.java")
    assert 'OWNED_SUBJECT = "Most {value}.";' in beliefs and corpus_mod.COMPATIBILITY_OWNED_SUBJECT == "Most {value}."
    verbs = re.search(r"PLURAL_VERBS = java\.util\.Map\.of\((.*?)\);", beliefs, re.S).group(1)
    pairs = re.findall(r'"([^"]+)"', verbs)
    assert dict(zip(pairs[::2], pairs[1::2])) == corpus_mod.PLURAL_VERBS
    qualifiers = re.search(r'Set<String> qualifiers = java\.util\.Set\.of\((.*?)\);', beliefs, re.S).group(1)
    assert set(re.findall(r'"([^"]+)"', qualifiers)) == set(corpus_mod._OWNED_QUALIFIERS)


# ------------------------------------------------------------------------------------- FR-2 moved money, L34

def test_moved_money_is_the_clouds_vocabulary():
    """keel-cloud 213 FR-8 (`StepCost.MOVE_WORDS`, `DESTINATION`, `CommercialChain.MONEY_NOUNS`), word for word."""
    step = _cloud(VECTORS + "StepCost.java")
    move = re.search(r'MOVE_WORDS = Pattern\.compile\((.*?)\);', step, re.S).group(1)
    java = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', move)).replace("\\\\", "\\")
    assert java == step_cost_mod.MOVE_WORDS.pattern
    destination = re.search(r'DESTINATION = Pattern\.compile\((.*?)\);', step, re.S).group(1)
    assert "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', destination)).replace("\\\\", "\\") == \
        step_cost_mod.DESTINATION.pattern
    chain = _cloud(VECTORS + "CommercialChain.java")
    nouns = re.search(r"MONEY_NOUNS = java\.util\.Set\.of\((.*?)\);", chain, re.S).group(1)
    assert set(re.findall(r'"([^"]+)"', nouns)) == step_cost_mod.MONEY_NOUNS


def test_palus_step_moves_money_owes_the_free_smaller_step_and_the_note():
    """keel-cloud 213 FR-8: *move a small part of the reserve* costs money (L34 owes a free smaller step) and names no
    place, so the Check row's note asks where (*into Palus*); a destination named, no note."""
    assert step_cost_mod.of(PALUS_STEP) == step_cost_mod.Cost(step_cost_mod.MONEY, "move")
    assert step_cost_mod.l34([PALUS_STEP]).startswith("L34: ")
    assert step_cost_mod.l34([PALUS_STEP, "a look at how it works"]) is None
    assert step_cost_mod.moves_money_nowhere(PALUS_STEP)
    assert not step_cost_mod.moves_money_nowhere(PALUS_STEP + " into Palus")
    assert not step_cost_mod.moves_money_nowhere("move the meeting to Friday")
    assert spoken_mod.commitment_note(PALUS_STEP, "Palus") == "Say where the money goes (into Palus)."
    assert spoken_mod.commitment_note("start a paid pilot", "Palus") is None
    controller = _cloud("src/main/java/com/keeldiscovery/cloud/protocol/founder/VectorsController.java")
    assert f'COMMITMENT_NOTE = "{spoken_mod.COMMITMENT_NOTE}";' in controller
    palus = _gallery("10-palus")
    labels = [i["label"] for i in vs.drafted_list(palus, "commercial.commitment")["items"]]
    assert labels[1] == vs.KEELS_SMALLER_STEP and step_cost_mod.l34(labels) is None


def test_the_four_commitment_answers_are_the_items():
    """keel-cloud 213 FR-8 (`commitmentAnswers` over `RespondentItems.commitmentOptions`)."""
    assert spoken_mod.commitment_answers([PALUS_STEP, "a look at how it works"]) == [
        "Yes, I'd move a small part of the reserve", "Probably, after a look at how it works first", "Probably not",
        "No"]
    assert spoken_mod.commitment_answers(["book a demo"]) == ["Yes, I'd book a demo", "Probably yes", "Probably not",
                                                              "No"]
    assert spoken_mod.commitment_answers([]) == []


# ------------------------------------------------------------------- FR-2 the stranger's stems, code's words

def test_relative_advantages_stem_names_the_idea_with_what_it_is():
    """keel-cloud 213 FR-6 (`ScaleFour.question`): *{Name}, {what it is},* -- whole, else cut, else its head."""
    assert spoken_mod.advantage_stem("night", "Lullaby", "a phone app that listens to crying",
                                     "work out what the baby needs") == (
        "Think of the last night when you had to work out what the baby needs. Would Lullaby, a phone app that "
        "listens to crying, have done that better for you, or not?")
    assert spoken_mod.advantage_stem(None, "Codyco", "an AI reservation agent that answers the calls nobody picks up "
                                                     "at the front desk", "answer a booking call").endswith(
        "Would Codyco, an AI reservation agent, have done that better for you, or not?")
    assert spoken_mod.what_head("an AI reservation agent that answers the calls") == "an AI reservation agent"
    assert spoken_mod.what_head("that answers the calls") is None
    assert spoken_mod.advantage_stem("night", "Lullaby", None, "work out what the baby needs").endswith(
        "Would Lullaby have done that better for you, or not?")
    assert spoken_mod.advantage_stem("night", "Lullaby", "a phone app", None) is None
    scale = _cloud(VECTORS + "ScaleFour.java")
    assert f'DONE_BETTER = "{spoken_mod.DONE_BETTER}";' in scale and "ideas.add(named + \", \" + one" in scale.replace(
        "named != null ? named + \", \" + one + \",\" : one", "ideas.add(named + \", \" + one")


def test_buyer_and_payers_share_stem_names_the_price():
    """keel-cloud 213 FR-10a (`ItemFrames.buyerPayerAtPrice`): *a fee of* where it fits, else the share as asked."""
    palus = spoken_mod.buyer_payer_at_price("board", "Palus", "about 0.25% of the balance a year")
    assert palus == "Could you sign off on about 0.25% of the balance a year yourself, or would the board have to agree?"
    assert len(palus.split()) == 20
    assert spoken_mod.buyer_payer_at_price("CFO", "Palus", "1% a year") == \
        "Could you sign off on a fee of 1% a year yourself, or would the CFO have to agree?"
    assert spoken_mod.buyer_payer_at_price(None, "Codyco", "about €3,000 per hotel, once") == \
        "Could you sign off on about €3,000 per hotel yourself, or would someone else have to agree?"
    frames = _cloud(VECTORS + "ItemFrames.java")
    assert '"a fee of " + said.replaceFirst("^about\\\\s+", "")' in frames


# ------------------------------------------------------------------------------------- FR-4 the entries' prices

def test_codycos_range_and_aircaps_optional_plan_are_what_the_walk_types():
    """FR-4: Codyco's recorded *€1,000 to €1,500* (`low` 1000, `high` 1500); AirCaps' *optional $20 a month plan* read
    off its sources file (*free plan ...; "Pro plan: $20/month"*) until a corpus revision records `optional`."""
    codyco, aircaps = _gallery("21-codyco"), _gallery("13-aircaps")
    assert vs.founder_price(codyco)["low"] == 1000 and vs.founder_price(codyco)["high"] == 1500
    assert not vs.plan_optional_sourced(codyco) and "optional" not in vs.founder_price(codyco)
    recorded = (aircaps.founder_calibration["commercial.price"] or {})["answer"]
    assert "optional" not in recorded, "a corpus revision records it now: read the yaml's field (plan.md, call 4)"
    assert vs.plan_optional_sourced(aircaps) and vs.founder_price(aircaps)["optional"] is True
    assert vs.price_belief_owed(aircaps) == \
        "Deaf and hard-of-hearing adults would think AirCaps worth $599 up front, then an optional $20 a month plan."
    assert vs.price_belief_owed(codyco) == ("Hotel group revenue directors would think Codyco worth €3,000 up front, "
                                            "then €1,000 to €1,500 per hotel a month.")
    body = next(a for a in vs.calibration_answers(aircaps, "COMMERCIAL") if a.dimension == "commercial.price")
    assert body.as_wire()["price"]["optional"] is True
    frizzle = _gallery("32-frizzle")
    assert not vs.plan_optional_sourced(frizzle), "a free plan beside a fee that is no up-front-then plan"


# ------------------------------------------------------------------------------------- FR-3 the walk, contract 59

def test_keel_web_173_draws_what_the_walk_reads():
    """keel-web 173 (merged): the test ids and the words the walk and the holds read."""
    control = _web("src/components/calibration/FounderControl.tsx")
    for testid in (vs_screens.CHAIN_PLAN_HIGH_TESTID, vs_screens.CHAIN_PLAN_OPTIONAL_TESTID):
        assert f'"{testid}"' in control, testid
    lists = _web("src/components/calibration/ListQuestion.tsx")
    for testid in (vs_screens.COMMITMENT_ANSWERS_TESTID, vs_screens.COMMITMENT_ANSWER_TESTID,
                   vs_screens.COMMITMENT_NOTE_TESTID):
        assert f'data-testid="{testid}"' in lists, testid
    assert '"data-tag": role' in lists
    words = _web("src/lib/translate.ts")
    for said in (f'CHAIN_PLAN_OPTIONAL = "{vs_screens.CHAIN_PLAN_OPTIONAL}"',
                 f'COMMITMENT_ANSWERS_TITLE = "{vs_screens.COMMITMENT_ANSWERS_TITLE}"',
                 f'BUYER_PAYER_PURCHASE = "{vs_screens.BUYER_PAYER_PURCHASE}"',
                 f'BUYER_PAYER_ALONE_COUNTS = "{vs_screens.BUYER_PAYER_ALONE_COUNTS}"',
                 f'"{vs_screens.PURCHASE_FRICTION_CHOOSE_INTRO}"',
                 'the difficulties at that moment, not the job as a whole.`',
                 'LIST_ROLE_AGREES = "· has to agree"'):
        assert said in words, said
    assert "before it went through. Pick the one step." not in words


def test_the_chain_words_owed_move_with_173():
    """FR-3: the equation's `chain-per` and the price's locked words -- one measure, no unit where the user pays."""
    palus = {"mode": "RATE", "low": 2, "high": 2, "period": "year", "unit": "company", "measure": "%",
             "base": "the balance"}
    share = {"shape": "SHARE", "low": 0.25, "high": 0.25, "shareBase": "COST_BASE"}
    assert cs.chain_words_owed("commercial.existing_sacrifice", palus, share, True) == (["a year"], ["per company"])
    assert cs.chain_words_owed("commercial.price", palus, share, True) == (["a year"], ["per company"])
    site = {"mode": "MONEY", "low": 800, "high": 900, "period": "month", "unit": "site"}
    assert cs.chain_words_owed("commercial.existing_sacrifice", site, None, True) == (["per site", "a month"], [])
    assert cs.chain_words_owed("commercial.price", site, _price(), True) == (["per site", "a month"], [])
    assert cs.chain_words_owed("commercial.price", {**site, "unit": "person"}, _price(), False) == \
        (["a month"], ["per person"])
    assert chain_mod.locked_drawn(chain_mod.locked_words(site, None, None, b2b=False), False) == "a month"
    assert chain_mod.locked_drawn({"base": "the balance", "unit": "company", "period": "year"}, True) == \
        "of the balance · a year"
    assert chain_mod.equation_per_drawn(palus) == "· a year"
    assert chain_mod.equation_per_drawn(site) == "· per site · a month"


def test_the_price_put_is_held_to_the_entrys():
    """FR-3: the PUT carries the plan's `low`, `high` and `optional` as the entry states them."""
    codyco = _price(upfrontLow=3000, upfrontHigh=3000, low=1000, high=1500, currency="EUR")
    assert vs_screens.price_sent_faults(codyco, {**codyco}) == []
    assert [f["what"] for f in vs_screens.price_sent_faults(codyco, {**codyco, "high": 1000})] == ["the plan's high"]
    aircaps = _price(optional=True)
    assert [f["what"] for f in vs_screens.price_sent_faults(aircaps, _price())] == ["the optional plan"]
    assert vs_screens.price_sent_faults(aircaps, _price(optional=True)) == []
    assert [f["what"] for f in vs_screens.price_sent_faults(aircaps, None)] == ["no price was PUT"]
    share = {"shape": "SHARE", "low": 1, "high": 1}
    assert vs_screens.price_sent_faults(share, {**share, "optional": True})[0]["what"] == \
        "optional sent off the up-front-then plan"
    writes = [{"body": {"answers": [{"dimension": "commercial.price", "price": codyco}]}}]
    assert vs_screens.sent_price("commercial.price", writes) == codyco
    assert vs_screens.sent_price("commercial.commitment", writes) is None


def test_the_commitment_check_faults():
    """FR-3: the drawn four and note are the served ones, and the served ones code's."""
    question = {"answers": spoken_mod.commitment_answers([PALUS_STEP, "a look at how it works"]),
                "note": "Say where the money goes (into Palus)."}
    seen = {"rows": [{"text": PALUS_STEP, "locked": False}], "field": None,
            "commitment": {"answers": list(question["answers"]), "note": question["note"]}}
    assert cs.commitment_check_faults(seen, question, "Palus") == []
    off = {**seen, "commitment": {"answers": question["answers"][:3], "note": None}}
    assert [f["what"] for f in cs.commitment_check_faults(off, question, "Palus")] == [
        "the four answers drawn are the served ones", "the note drawn is the served one"]
    no_note = {**question, "note": None}
    assert [f["what"] for f in cs.commitment_check_faults({**seen, "commitment": {"answers": question["answers"]}},
                                                          no_note, "Palus")] == \
        ["the note is owed exactly where the step moves money nowhere"]
    older = {"rows": seen["rows"], "field": None}
    assert cs.commitment_check_faults(older, {"answers": None, "note": None}, "Palus") == []


def test_a_row_is_said_with_its_tag():
    assert vs_screens.row_said("The CFO", "· has to agree") == "The CFO · has to agree"
    assert vs_screens.row_said("The CFO", "has to agree") == "The CFO · has to agree"
    assert vs_screens.row_said("The CFO", None) == "The CFO"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


_PRICE_PAGE = """<!doctype html><html><body><main><div data-testid="chain-price">
<button data-testid="chain-shape-UPFRONT_THEN">Up front, then a plan</button>
<input data-testid="chain-upfront"><input data-testid="chain-plan"><span>to</span><input data-testid="chain-plan-high">
<span data-testid="chain-locked">per hotel · a month</span>
<label data-testid="chain-plan-optional"><input type="checkbox"><span>Optional plan</span></label>
</div></main></body></html>"""

_CHECK_PAGE = """<!doctype html><html><body><main><div class="listcheck"><p class="listcheck__title">Check</p>
<ul class="listrows">
<li class="listrow" data-tag="· has to agree"><textarea class="listrow__ed">The CFO</textarea>
<span class="listrow__tag" data-testid="role-agree">· has to agree</span></li>
<li class="listrow"><textarea class="listrow__ed">move a small part of the reserve</textarea>
<p class="listrow__warn" data-testid="commitment-note">Say where the money goes (into Palus).</p></li>
</ul>
<div class="listcheck__field listcheck__answers" data-testid="commitment-answers"><p class="listcheck__k">What strangers
can answer</p><ul><li data-testid="commitment-answer">Yes, I'd move a small part of the reserve</li>
<li data-testid="commitment-answer">Probably, after a look at how it works first</li>
<li data-testid="commitment-answer">Probably not</li><li data-testid="commitment-answer">No</li></ul></div>
</div></main></body></html>"""


def _corridor(browser, tmp_path, html: str):
    page = browser.new_page()
    page.set_content(html)
    return page, vs_screens.Corridor(page, Recorder(tmp_path), BASE)


@pytest.mark.parametrize("price, boxes", [
    (_price(upfrontLow=3000, upfrontHigh=3000, low=1000, high=1500, currency="EUR"),
     {"low": "1000", "high": "1500", "optional_drawn": True, "optional": False}),
    (_price(optional=True), {"low": "20", "high": "20", "optional_drawn": True, "optional": True}),
])
def test_the_walk_types_the_plans_two_boxes_and_ticks_the_optional_plan(browser, tmp_path, price, boxes):
    """FR-3 (keel-web 173 FR-2): `chain-plan` the low, `chain-plan-high` the high, *Optional plan* ticked where the
    entry's plan is optional."""
    page, corridor = _corridor(browser, tmp_path, _PRICE_PAGE)
    try:
        seen = corridor._chain_price(price)
        assert seen["plan_boxes"] == boxes
        assert page.get_by_test_id("chain-upfront").input_value() == str(price["upfrontLow"])
    finally:
        page.close()


def test_the_check_read_carries_the_tag_the_four_answers_and_the_note(browser, tmp_path):
    """FR-3 (keel-web 173 FR-1, FR-5a): a role row read with its tag; Commitment's block read in served order."""
    page, corridor = _corridor(browser, tmp_path, _CHECK_PAGE)
    try:
        drawn = corridor._list_rows()
        assert drawn["rows"][0]["said"] == "The CFO · has to agree"
        assert "said" not in drawn["rows"][1]
        assert drawn["commitment"] == {"answers": ["Yes, I'd move a small part of the reserve",
                                                   "Probably, after a look at how it works first", "Probably not",
                                                   "No"],
                                       "title": "What strangers can answer",
                                       "note": "Say where the money goes (into Palus)."}
    finally:
        page.close()


def test_the_readers_screen_read_says_the_role_rows_tag(browser, tmp_path):
    """FR-3 (keel-web 173 judgement call 6): the reader's own read (`evals/backtest.READ_JS`) takes the row's tag with
    its value, so cycle 12's readers see *The CFO · has to agree*; and Commitment's four and the note."""
    from evals import backtest as bt
    page = browser.new_page()
    try:
        page.set_content(_CHECK_PAGE)
        read = page.evaluate(bt.READ_JS)
        assert read["rows"][0] == "The CFO · has to agree"
        assert read["rows"][1].startswith("move a small part of the reserve")
        assert read["commitment"]["answers"][0] == "Yes, I'd move a small part of the reserve"
        assert read["commitment"]["note"] == "Say where the money goes (into Palus)."
    finally:
        page.close()
