"""Spec 132 -- the harness mirrors keel-cloud 205, 206, 207, 208 and keel-web 166, 168, 169 (their tasks.md, *Owed
elsewhere*: keel-e2e-eval). No stack, no model, no paid call; the cloud's and the web's sources are read from the
checkouts `stack.toml` names (keel-cloud-docs master `7c96988d`, keel-web master `a1848dc3`), skipped without them.

- FR-1 `L32` by name: `instructions.friction.founders_offer` restates `PurchaseFriction.foundersOffer`'s closed
  vocabulary; `instructions/score.py` names it on a Purchase friction draft; `backtest.LOCK_NOTES` reports it.
- FR-2 the scripted writer and the walker's rows: a typed Purchase friction row naming the founder's own offer is left
  out (`vectors_script.offer_rows`, `kept_items`), its pick moving to the first row kept.
- FR-3 / FR-10 Buyer and payer: the walker picks 1 (every role) wherever the Answer names one, 0 only where it names
  nobody, never by label; the founder's side reads that pick.
- FR-4 / FR-5 the cards (`tests/test_dimension_cards_131.py`) and the pins (the two moved Answer questions).
- FR-6 / FR-12 `E9`, `K10`, `K8`, `W12`, `M7`, `M8`, `P6` by name.
- FR-7 the scripted Adoption friction rows carry their `only_if`.
- FR-8 the walker types the corpus time, *not sure* only where none is recorded.
- FR-9 206's Existing sacrifice stems (never *miss*), Commitment's *Yes, I would*, keel-web 166's window clause.
- FR-11 corpus revision 23's change set (`idea_what` on five, the revision line elsewhere).
- FR-13 the idea screen's boxes in the founder-reader's capture (Codyco's served card).
- FR-14 the context intro's count.
- FR-15 208's follow-up texts (most re-pinned in place: `test_follow_up_ladder`, `test_after_131`,
  `test_cloud_200_mirror_129`, `test_after_130`, `test_money_cards_redrawn_118`).
"""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import interviewer_fake as fake
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from instructions import friction as friction_mod
from instructions import score as score_mod
from quality import readers
from stack.config import load_config

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
KEEL_WEB = Path(CONFIG.keel_web)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
PF = "commercial.purchase_friction"
BP = "commercial.buyer_payer_alignment"
ADOPTION = "solution.adoption_friction"
IMPORTANCE = "problem.importance"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_CLOUD}")
    return path.read_text(encoding="utf-8")


def _web(rel: str) -> str:
    path = KEEL_WEB / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_WEB}")
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def golden() -> dict:
    if not corpus_mod.corpus_dir(KEEL_CLOUD).is_dir():
        pytest.skip(f"no corpus at {KEEL_CLOUD}")
    return {e.id: e for e in vs.load(KEEL_CLOUD).entries}


@pytest.fixture(scope="module")
def backtest() -> dict:
    if not corpus_mod.backtest_dir(KEEL_CLOUD).is_dir():
        pytest.skip(f"no back-test corpus at {KEEL_CLOUD}")
    return {e.id: e for e in vs.load(KEEL_CLOUD, backtest=True).entries}


# ------------------------------------------------------------------------------------ FR-1: L32 by name

def test_the_offer_vocabulary_is_purchase_frictions_word_for_word():
    java = _cloud(VECTORS + "PurchaseFriction.java")
    block = java.split("Pattern OFFER = java.util.regex.Pattern.compile(", 1)[1].split(");", 1)[0]
    words = re.search(r"\(trials\?\|pilots\?\|guarantees\?\|onboarding\|money\[- \]back\)", block.replace("\\\\", "\\"))
    assert words, block
    assert "(trials?|pilots?|guarantees?|onboarding|money[- ]back)" in friction_mod.OFFER.pattern
    assert "(?<![\\\\p{L}-])" in block and "(?![\\\\p{L}-])" in block, "whole words, no letter or hyphen beside"
    reason = _cloud(APPLICATION + "FounderReason.java")
    said = reason.split('case "L32" -> ', 1)[1].split(";", 1)[0]
    assert "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', said)) == friction_mod.OFFER_NOTE


@pytest.mark.parametrize("step, word", [
    ("A trial on one live job", "trial"), ("A budget line for the department's pilot", "pilot"),
    ("A trial at one hotel first", "trial"), ("Onboarding the finance team", "Onboarding"),
    ("A money-back test", "money-back"), ("A money back offer", "money back"), ("Two guarantees", "guarantees"),
    ("Diligence on a new provider", None), ("Board approval of the cash policy", None),
    ("A tax adviser's sign-off", None), ("A security review of the product", None), ("Trialling it", None),
    ("A pre-trial review", None), ("Autopilots", None)])
def test_founders_offer_reads_the_closed_vocabulary_alone(step, word):
    """keel-cloud 205's own cases: Expanse's pilot budget and Codyco's trial are offers, Palus's three steps and the
    card's good example are not; a longer word or a hyphened one is no offer word."""
    assert friction_mod.founders_offer(step) == word


def _dimension(key: str):
    return SimpleNamespace(key=key, founder_control="item_list", part=3,
                           saves={"min_items": 1, "max_items": 4, "max_words": 9, "picked": True})


def test_score_names_l32_on_a_drafted_offer_and_on_purchase_friction_alone():
    draft = {"list": {"items": [{"label": "A trial on one live job"}, {"label": "A security review"}]}}
    faults = score_mod.list_faults(draft, _dimension(PF))
    l32 = [f for f in faults if f.startswith("L32:")]
    assert len(l32) == 1 and "'A trial on one live job'" in l32[0] and "('trial')" in l32[0]
    assert not [f for f in score_mod.list_faults(draft, _dimension(ADOPTION)) if f.startswith("L32:")]
    clean = {"list": {"items": [{"label": "A security review"}]}}
    assert not [f for f in score_mod.list_faults(clean, _dimension(PF)) if f.startswith("L32:")]


#: keel-cloud 205-207's rules as the cloud words their notes and repair turns (`ScreenResultApplier`, `AskedRules`,
#: `IdeaLines`, `RespondentQuestionsRules`): each by name where refusals are reported.
NOTES = [
    ("CALIBRATION_QUESTIONS", "detail", "L32: the founder typed 'A trial on one live job', their own offer -- left out: "
                                        "a step here is one the buyer's side must clear before paying"),
    ("RESPONDENT_QUESTIONS", "detail", "E9: 'could have caught the error sooner' says 'could have', what might have "
                                       "been; nearly anyone could say yes to it"),
    ("ASKED", "turn", "K10: 'could talk to the site' opens 'could talk', with no subject of its own; open on its "
                      "subject and verb said to them"),
    ("CALIBRATION_QUESTIONS", "detail", "K8: write this item's condition -- the one thing that would most have to be "
                                        "true for one of them to take this step"),
    ("SOLUTION_MECHANISM", "detail", "W12: idea_what, 'Codyco', is the idea's name; say what it is"),
    ("SOLUTION_MECHANISM", "detail", "M7: the how line runs 6 sentences; heard once, it is at most five"),
    ("SOLUTION_MECHANISM", "detail", "M8: the belief names PMS, OPERA Cloud again"),
    ("PROBLEM_INTERPRET", "detail", "P6: 'thee' in 'two to thee times' is the number word 'three' misspelt"),
]


def test_the_new_rules_are_named_where_refusals_are_reported():
    """FR-1, FR-6, FR-12: L32, E9, K10, K8, W12, M7, M8 and P6 in the lock notes the back-test reports by name, read off
    an interaction's `detail` and its repair turns."""
    for rule in ("L32", "E9", "K10", "K8", "W12", "M7", "M8", "P6"):
        assert rule in bt.LOCK_NOTES and bt.LOCK_NOTES[rule].endswith(")"), rule
    rows = [{"screen": screen, "detail": text} if where == "detail" else
            {"screen": screen, "turns": [{"content": text}]} for screen, where, text in NOTES]
    found = bt.lock_notes(None, rows)
    assert [n["rule"] for n in found] == ["L32", "E9", "K10", "K8", "W12", "M7", "M8", "P6"]
    assert all(n["means"] == bt.LOCK_NOTES[n["rule"]] for n in found)
    assert "keel-cloud 205" in found[0]["means"] and "keel-cloud 206" in found[1]["means"]
    assert "keel-cloud 207" in found[4]["means"] and "keel-cloud 207" in found[7]["means"]


def test_the_cloud_words_each_rule_as_the_notes_read_it():
    applier = _cloud(APPLICATION + "ScreenResultApplier.java")
    for prefix in ('"L32: the founder typed \'', '"L32: \'', '"E9: \'', '"K8: write this item\'s condition', '"M7: ',
                   '"M8: ', '"P6: \''):
        assert prefix in applier or prefix in _cloud(APPLICATION + "RespondentQuestionsRules.java"), prefix
    assert '"K10: \'' in _cloud(APPLICATION + "AskedRules.java")
    assert '"W12: idea_what, \'' in _cloud("src/main/java/com/keeldiscovery/cloud/domain/project/IdeaLines.java")


# ------------------------------------------------------------------- FR-2: the founder's own offer, left out

def test_five_back_test_entries_type_an_offer_and_no_gallery_or_golden_entry_does(golden, backtest):
    # spec 135 FR-2 re-pin (corpus revision 24, keel-cloud 215): the card review dropped 08-fresco's and 21-codyco's own
    # trials and reworded 14-code-four's and 17-expanse's into the buyer's own step, so no gallery entry types the
    # founder's own offer; the five outside the gallery (revision 23) still do
    assert all(vs.offer_rows(e) == [] for e in golden.values())
    typed = {k: vs.offer_rows(e) for k, e in backtest.items() if vs.offer_rows(e)}
    assert not set(typed) & set(corpus_mod.GALLERY)
    assert all(vs.offer_expectation(backtest[k]) == vs.NO_OFFER_TYPED for k in corpus_mod.GALLERY if k in backtest)
    assert typed["25-bidflow"] == ["A trial on one live bid"]
    assert vs.offer_expectation(backtest["25-bidflow"]) == "L32 owed on: A trial on one live bid"
    assert sorted(typed) == ["22-andy-ai", "25-bidflow", "26-cubic", "27-blacksmith", "28-relvy-ai"]


def test_the_scripted_writer_leaves_the_offer_out_and_the_pick_moves_to_the_first_row_kept(backtest):
    # spec 135 FR-2 re-pin: Fresco's list is the two it keeps at revision 24 (its trial dropped, the pick on
    # `procore_check` at index 0 with the founder's 2 weeks), so nothing is left out; 25-bidflow types its trial between
    # two rows and the cloud leaves it out, the pick (0) unmoved
    fresco = backtest["08-fresco"]
    drafted = [i["label"] for i in vs.drafted_list(fresco, PF)["items"]]
    assert drafted == ["A check that it works with Procore", "A security review of the site videos"]
    assert [i["label"] for i in fresco.founder_list(PF)["items"]] == drafted and fresco.founder_list(PF)["picked"] == 0
    assert vs.founder_duration(fresco) == {"count": 2, "unit": "WEEKS"}
    assert not [f for f in score_mod.list_faults({"list": vs.drafted_list(fresco, PF)}, _dimension(PF))
                if f.startswith("L32:")], "the scripted draft spends no repair turn"
    saved = vs.saved_list(fresco, PF)
    assert [i["label"] for i in saved["items"]] == drafted and saved["pickedIndex"] == 0
    assert [i["code"] for i in saved["items"]] == ["item_1", "item_2"], "code's positional codes on the kept rows"
    expanse = backtest["17-expanse"]
    saved = vs.saved_list(expanse, PF)
    assert len(saved["items"]) == 2 and saved["pickedIndex"] == 0
    assert saved["items"][0]["label"] == "A security review of an agent on every node"
    assert saved["items"][1]["label"] == "A budget line in the department's plan"
    answer = next(a for a in vs.calibration_answers(fresco, "COMMERCIAL") if a.dimension == PF)
    assert [i["label"] for i in answer.listed["items"]] == drafted
    assert "trial" not in answer.text, "no own-offer row typed (spec 135 FR-2)"
    bidflow = backtest["25-bidflow"]
    kept = [i["label"] for i in vs.saved_list(bidflow, PF)["items"]]
    assert kept == ["A check against a past takeoff", "Getting counts into our estimating software"]
    assert vs.saved_list(bidflow, PF)["pickedIndex"] == 0
    # the walker's typed rows are the kept ones (`calibration_answers`), so the trial is no *Keel left out* finding
    answer = next(a for a in vs.calibration_answers(bidflow, "COMMERCIAL") if a.dimension == PF)
    assert [i["label"] for i in answer.listed["items"]] == kept
    assert "A trial on one live bid" in answer.text, "the founder still types it; the cloud leaves it out with a note"


# ------------------------------------------------------------------------- FR-3 / FR-10: Buyer and payer

def test_the_walker_picks_every_role_wherever_the_answer_names_one(golden, backtest):
    palus = backtest["10-palus"]
    assert palus.founder_list(BP)["picked"] == 0, "the corpus picks Nobody else beside the board"
    assert vs.buyer_payer_roles(palus) == ["The board"] and vs.buyer_payer_pick(palus) == 1
    assert vs.saved_list(palus, BP)["pickedIndex"] == 1
    assert vs.founder_side(palus).buyer_supports == fake.BUYER_SUPPORTS
    assert vs.buyer_payer_pick(backtest["15-voltair"]) == 1, "a role's own index (2) is never sent"
    assert vs.buyer_payer_pick(golden["01-countly"]) == 0 and vs.buyer_payer_roles(golden["01-countly"]) == []
    assert vs.founder_side(golden["01-countly"]).buyer_supports == (fake.BUYER_ALONE,)
    assert vs.buyer_payer_pick(golden["02-compliancelog"]) == 1
    for entry in [*golden.values(), *backtest.values()]:
        if entry.founder_list(BP):
            assert vs.buyer_payer_pick(entry) == (1 if vs.buyer_payer_roles(entry) else 0), entry.id


def test_the_leg_picks_buyer_and_payer_by_index_never_by_label():
    source = inspect.getsource(cs.leg_calibrate)
    assert "pick = vs.buyer_payer_pick(j.entry)" in source
    assert "j.corridor.list_choose(question, None, index=pick)" in source
    assert vs_screens.roles_joined(["The CFO", "The project executive"]) == "The CFO and the project executive"
    assert vs_screens.roles_joined(["The board"]) == "The board"
    assert vs_screens.roles_joined(["Finance", "The CTO", "Their partner"]) == "Finance, the CTO and their partner", \
        "a one-word capitalised role is kept as a name, as keel-web's `theRole`"


def test_the_confirm_statement_is_keel_webs():
    text = _web("src/lib/translate.ts")
    said = re.search(r"export const BUYER_PAYER_CONFIRM_ONLY =\s*\"([^\"]*)\";", text)
    assert said and said.group(1) == vs_screens.BUYER_PAYER_CONFIRM_ONLY
    page = _web("src/components/calibration/ListQuestion.tsx")
    for testid in (vs_screens.CHOOSE_CONFIRM_TESTID, vs_screens.CHOOSE_STATEMENT_TESTID, "role-agree"):
        assert f'data-testid="{testid}"' in page, testid


def test_a_percent_of_what_it_gets_back_is_absent_on_a_fresh_study():
    assert vs_screens.CHAIN_PRICE_CHOICE[("SHARE", "RECOVERED")] == vs_screens.CHAIN_RECOVERED_TESTID
    assert vs_screens.recovered_drawn_faults({"recovered_drawn": True}) == [
        "chain-share-RECOVERED is drawn on a fresh study (keel-web 168 FR-5)"]
    assert vs_screens.recovered_drawn_faults({"recovered_drawn": False}) == []
    assert vs_screens.recovered_drawn_faults({"recovered_drawn": True}, fresh=False) == []
    assert "RECOVERED_NOT_DRAWN" in inspect.getsource(vs_screens.Corridor._chain_price)


@pytest.mark.parametrize("name", ["CURRENT_SOLUTION_HOW_HINT", "PURCHASE_FRICTION_BAR_UNDATED"])
def test_the_moved_founder_words_are_keel_webs(name):
    text = _web("src/lib/translate.ts")
    said = re.search(rf'export const {name} = "([^"]*)";', text).group(1)
    ours = {"PURCHASE_FRICTION_BAR_UNDATED": vs_screens.PURCHASE_FRICTION_CHOOSE_BAR_UNDATED}.get(
        name, getattr(vs_screens, name, None))
    assert said == ours


def test_the_answer_hints_are_168s():
    text = _web("src/lib/translate.ts")
    assert "each up to ${c.words} words.`" in text and "Up to 25 words" not in text.split("ANSWER_HINT_OF", 1)[1].split(
        "export const compatibilityHint", 1)[0]
    assert vs_screens.IMPORTANCE_ANSWER_HINT == "Name up to four other difficulties they meet around this, each up to 9 " \
                                               "words."
    hint = vs_screens.COMPATIBILITY_ANSWER_HINT_WANT.format(people="construction superintendents")
    assert vs_screens.COMPATIBILITY_ANSWER_HINT.match(hint)["people"] == "construction superintendents"
    assert vs_screens.chain_base_help("the balance") == "The part of the balance they lose."
    assert vs_screens.chain_base_help("") == "The part they lose."


# ---------------------------------------------------------------------------- FR-5: the moved Answer questions

def test_the_two_moved_answer_questions_are_the_clouds():
    prompts = _cloud(VECTORS + "AnswerPrompts.java")
    assert f'COMMERCIAL_PURCHASE_FRICTION -> "{vs_screens.PURCHASE_FRICTION_ANSWER_QUESTION}"' in prompts
    joined = re.sub(r'"\s*\+\s*"', "", prompts)
    assert f'COMMERCIAL_COMMITMENT -> "{vs_screens.COMMITMENT_ANSWER_QUESTION}"' in joined
    # spec 133 FR-3 (keel-cloud 211 FR-7): Commitment's moved again -- 205's *where would any money go?* is gone
    for old in (vs_screens.PURCHASE_FRICTION_ANSWER_QUESTION_204, vs_screens.COMMITMENT_ANSWER_QUESTION_204,
                vs_screens.COMMITMENT_ANSWER_QUESTION_205):
        assert f'-> "{old}"' not in joined, old


# ------------------------------------------------------------------- FR-7: the scripted Adoption friction rows

def test_every_scripted_adoption_row_carries_a_condition_the_cloud_takes(golden, backtest):
    rules = _cloud(APPLICATION + "AskedRules.java")
    assert f"ONLY_IF_MAX_WORDS = {vs.ONLY_IF_MAX_WORDS};" in rules
    for entry in [*golden.values(), *backtest.values()]:
        if not entry.founder_list(ADOPTION) or entry.unsure(ADOPTION):
            continue
        for item in vs.drafted_list(entry, ADOPTION)["items"]:
            condition = item.get("only_if")
            assert condition and 1 <= len(condition.split()) <= vs.ONLY_IF_MAX_WORDS, (entry.id, item)
            assert not vs._EVERY_STEP.search(condition) and "?" not in condition, (entry.id, condition)
            assert not re.search(r"\d", condition) or re.search(r"\d", item["label"]), (entry.id, condition)
    countly = vs.drafted_list(golden["01-countly"], ADOPTION)["items"]
    assert [i["only_if"] for i in countly] == ["scanning never slowed my work", "confirming never slowed my work"]
    assert vs.adoption_condition({"label": "Check and fix the notes", "condition": "I could try it on one site"}) == \
        "I could try it on one site", "the entry's own condition where it records one"


# --------------------------------------------------------------------------------- FR-8: the walker's time

def test_the_walker_types_the_corpus_time_and_never_leaves_the_box_empty(golden, backtest):
    assert vs.walker_duration(backtest["10-palus"]) == {"count": 4, "unit": "WEEKS"}
    assert vs.walker_duration(backtest["17-expanse"]) == {"count": 6, "unit": "WEEKS"}
    for entry in backtest.values():
        if entry.founder_list(PF) and not entry.unsure(PF):
            owed = vs.walker_duration(entry)
            assert owed == vs.founder_duration(entry) and not owed.get("unsure"), entry.id
    assert vs.walker_duration(golden["03-lullaby"]) == {"unsure": True, "default": True,
                                                         **vs.GOLDEN_DEFAULT_DURATION}


# --------------------------------------------------------- FR-9: 206's stems, Yes I would, 166's window clause

def test_no_existing_sacrifice_stem_says_miss_or_lose_and_a_percent_box_asks_what_percent(golden, backtest):
    asked = 0
    for entry in [*golden.values(), *backtest.values()]:
        item = vs.cost_item(entry)
        if item is None:
            continue
        asked += 1
        question = item["question"]
        assert vs.loss_word(question) is None, (entry.id, question)
        cost = entry.cost()
        if cost.get("mode") == "RATE" and vs.cost_measure(cost) in (None, "%"):
            assert "what percent" in question and "how much" not in question, (entry.id, question)
    assert asked >= 20
    assert vs.one_verb("reserve and never use") == "never use" and vs.one_verb("fail in front") == "fail in front"
    assert vs.without_the_measure("the thread of the conversation", "conversations") == "the thread"
    assert vs.loss_word("about how many calls did you miss?") == "miss" and vs.loss_word("the dismissed") is None


def test_commitments_fallback_first_label_is_yes_i_would():
    rows = {d["key"]: d for d in json.loads(_cloud("src/main/resources/keel/dimension-registry.json"))["dimensions"]}
    labels = [a["label"] for a in rows["commercial.commitment"]["respondent"]["fixed_answers"]]
    assert labels[0] == "Yes, I would" and "Yes, I'd start one" not in labels


@pytest.mark.parametrize("understands, clause", [
    ("Construction superintendents at US general contractors. When they put the day's photos and notes into the daily "
     "log, they want to keep a record. We'll ask about the last 5 working days.",
     "the last time they put the day's photos and notes into the daily log"),
    ("Startup founders. When their raise cash sits in your account, they want to earn on it.",
     "the last time their raise cash sits in their account"),
    ("Startup founders. When you decide where your raise cash sits, they want to earn on it.", None),
    ("Parents. When the baby cries in the night, parents are trying to settle them.", None),
    ("Parents of babies under six months.", None),
    ("Agents. When a guest calls you back, they want to book.", None)])
def test_the_window_clause_names_the_moment(understands, clause):
    """FR-9 (keel-web 166 FR-1, `circumstanceClauseOf`): the clause after *When*, said of the people -- none where the
    sentence has no *When ..., they* (a read before keel-cloud 122) or a *you* grammar cannot place."""
    assert vs_screens.circumstance_clause_of(understands) == clause
    if clause:
        label = vs_screens.recall_window_label("construction superintendents", clause)
        assert vs_screens.RECALL_WINDOW_QUESTION.match(label)["clause"] == clause


def test_the_held_choose_is_keel_webs():
    text = _web("src/lib/translate.ts")
    assert f'export const PURCHASE_FRICTION_TIME_OWED = "{vs_screens.PURCHASE_FRICTION_TIME_OWED}";' in text
    assert f'export const KEEL_TEST_PENDING = "{vs_screens.KEEL_TEST_PENDING}";' in text
    assert f'data-testid="{vs_screens.KEEL_TEST_WAITING_TESTID}"' in _web("src/components/calibration/KeelTest.tsx")


# ------------------------------------------------------------------------------ FR-11: corpus revision 23

def test_revision_23_moves_exactly_207s_edits():
    """The revision-22 records beside canon: the revision line (22 -> 23) on every entry, `idea_what` added on the five
    cycle-9 entries, nothing else. Spec 135 re-pin (keel-cloud 215, corpus revision 24): canon's fourteen gallery
    entries moved on to 24, so 22 -> 23 is read between keel-cloud's revision-22 and revision-23 records
    (`corpus-r23/`, `backtest-r23/`, kept by 215); 23 -> 24 is `test_harness_reads_r24_135.py`'s."""
    mirror = KEEL_CLOUD / "src" / "test" / "resources" / "keel"
    if not all((mirror / f"{kind}-r{n}").is_dir() for kind in ("corpus", "backtest") for n in (22, 23)):
        pytest.skip("no revision-22 and revision-23 records")
    whats = {}
    for kind in ("corpus", "backtest"):
        for path in sorted((mirror / f"{kind}-r23").glob("*.yaml")):
            before = yaml.safe_load((mirror / f"{kind}-r22" / path.name).read_text(encoding="utf-8"))
            after = yaml.safe_load(path.read_text(encoding="utf-8"))
            assert (before["revision"], after["revision"]) == (22, 23), path.name
            what = (after.get("solution_mechanism") or {}).pop("idea_what", None)
            if what:
                whats[after["id"]] = what
            before.pop("revision"), after.pop("revision")
            assert before == after, path.name
    assert whats == {"08-fresco": "an AI scribe that writes up site walk videos as notes",
                     "10-palus": "a treasury account that holds a startup's reserve in bonds",
                     "13-aircaps": "glasses paired to a phone app that captions speech in the lens",
                     "17-expanse": "a cluster tool that predicts what each job needs at submit",
                     "21-codyco": "an AI reservation agent for missed hotel calls"}
    assert all(len(w.split()) <= 12 for w in whats.values())


def test_the_scripted_writer_sends_idea_what_where_the_entry_records_one(golden, backtest):
    assert vs.mechanism_result(backtest["21-codyco"])["idea_what"] == "an AI reservation agent for missed hotel calls"
    assert backtest["21-codyco"].idea_what() == "an AI reservation agent for missed hotel calls"
    assert "idea_what" not in vs.mechanism_result(golden["03-lullaby"]) and golden["03-lullaby"].idea_what() is None


# ------------------------------------------------------------------- FR-13: the idea screen's boxes, captured

#: Cycle 9's served card for 21-codyco (the walk's transcript): the name the founder typed, Keel's what-it-is words in
#: the box beside it, the how and the belief.
CODYCO_IDEA = {"name": "Codyco", "whatItIs": "an AI agent that answers unanswered booking calls",
               "how": "Hotels forward the calls nobody picks up to Codyco. Its AI answers in the hotel's voice.",
               "belief": "Codyco would turn missed booking calls into bookings."}


def test_the_idea_screens_boxes_reach_the_founder_reader():
    assert "idea_boxes: idea" in bt.READ_JS and "[data-testid=idea-what-it-is]" in bt.READ_JS
    shot = {"n": 7, "slug": "idea", "kicker": "STEP 3 OF 4 · THE SOLUTION", "question": "Check what strangers will read",
            "idea_boxes": CODYCO_IDEA}
    cam = SimpleNamespace(founder_shots=[shot])
    wire = {"idea": {"what": "Codyco", "name": "Codyco", "whatItIs": CODYCO_IDEA["whatItIs"],
                     "line": "Imagine Codyco, an AI agent that answers unanswered booking calls.",
                     "how": CODYCO_IDEA["how"], "belief": CODYCO_IDEA["belief"]}}
    j = SimpleNamespace(founder=SimpleNamespace(calibration={}, project_name="Codyco"))
    screens = bt.founder_screens(j, cam, wire)
    assert screens[0]["idea_boxes"] == CODYCO_IDEA
    assert screens[0]["keel read back"]["whatItIs"] == CODYCO_IDEA["whatItIs"]
    assert screens[0]["keel read back"]["line"].startswith("Imagine Codyco, an AI agent")
    full = readers.founder_screens({"founder_screens": screens})[0].full
    assert "The idea's boxes, as drawn:" in full
    assert "- What it is (the box beside the name): an AI agent that answers unanswered booking calls" in full
    assert "- Its name: Codyco" in full
    assert readers._idea_boxes({"idea_boxes": {"name": "Codyco", "whatItIs": ""}}) == [
        "The idea's boxes, as drawn:", "- Its name: Codyco", "- What it is (the box beside the name): (empty as drawn)"]
    assert readers._idea_boxes({}) == []


def test_the_walk_captures_the_boxes_beside_the_page_text():
    assert vs_screens.idea_boxes_text({"what": "Codyco", "whatItIs": CODYCO_IDEA["whatItIs"], "how": "h",
                                       "belief": "b"}) == (
        "Name: Codyco\nWhat it is: an AI agent that answers unanswered booking calls\nHow: h\nBelief: b")
    assert vs_screens.idea_boxes_text({"what": "Codyco", "whatItIs": None, "how": "h", "belief": "b"}) == \
        "Name: Codyco\nHow: h\nBelief: b", "a page before keel-web 156 draws no what-it-is box"
    assert 'h.capture_text("stage_screen", idea_boxes_text(lines))' in inspect.getsource(vs_screens.Corridor.idea_check)


# ------------------------------------------------------------------------------- FR-14: the context intro

def test_the_context_intro_counts_its_answers():
    text = _web("src/lib/translate.ts")
    assert 'export const CONTEXT_INTRO = `Four short answers, a phrase each. ${CONTEXT_INTRO_BOUNDARY}`;' in text
    assert 'export const CONTEXT_INTRO_WITH_WINDOW = `Five short answers, a phrase each. ${CONTEXT_INTRO_BOUNDARY}`;' \
        in text
    assert f'const CONTEXT_INTRO_BOUNDARY = "{vs_screens.CONTEXT_INTRO_BOUNDARY}";' in text
    for scope in ("ALL", "PROBLEM", "SOLUTION", "SOLUTION_COMMERCIAL"):
        assert vs_screens.context_intro(scope).startswith("Four short answers, a phrase each."), scope  # keel-web 171
    assert vs_screens.context_intro("COMMERCIAL").startswith("Four short answers, a phrase each.")
    fixture = json.loads((Path(__file__).parent / "fixtures" / "typist" / "backtest-21-codyco-PROBLEM.json")
                         .read_text(encoding="utf-8"))
    context = next(s for s in fixture["founder_screens"] if s["screen"] == "context")
    assert context["intro"] == vs_screens.context_intro("PROBLEM")


# ------------------------------------------------------------------------------- FR-15: the follow-up texts

def _interview(rung: str, labels: dict, question: str = "q", token: str = "tok", part: int = 2) -> dict:
    item = {"dimension": rung, "question": question,
            "options": [{"optionId": vs.option_id(token, rung, code), "label": label} for code, label in labels.items()]}
    return {"occasion": "night", "parts": [{"part": part, "items": [item]}]}


@pytest.mark.parametrize("row, said", [
    ("Keeping idle cash in the bank's treasury money market fund", "keeping idle cash"),
    ("Working out what the baby needed", "working out what the baby needed"),
    ("Getting cash back fast when needed", "getting cash back fast when needed"),
    ("A bank account or wallet for the business and the team", "a bank account or wallet"),
    ("Checking each shipment's weight and size and stacking and labelling it", "checking each shipment's weight and size"),
    ("Keeping cash safe above the insured limit always", "keeping cash safe above the insured limit always"),
    (None, None)])
def test_a_row_with_no_short_name_is_said_back_cut(row, said):
    """keel-cloud 208 (`saidShort`): six words by its trailing phrases, then a trailing alternative; a row with no clean
    cut as written."""
    assert fake.said_short(row) == said


def test_importance_says_the_picks_back_in_the_persons_words(golden):
    lullaby = golden["03-lullaby"]
    codes = [vs.wire_code(IMPORTANCE, i) for i in range(5)]
    labels = {codes[0]: "Working out what the cry means", codes[1]: "Getting the baby back down after a feed",
              codes[2]: "Getting back to sleep yourself", codes[3]: "Keeping track of the night's feeds and nappies "
              "across a long and broken night", codes[4]: "Remembering which side you fed from at the last feed "
              "of the night"}
    interview = _interview(IMPORTANCE, labels, part=1)
    one = vs.follow_up_question(lullaby, [vs.Pick(dimension=IMPORTANCE, codes=[codes[1]])], vs.LINK_PRIMARY,
                                interview, "tok", stem=(IMPORTANCE, False))
    short = vs.tested_short_name(lullaby, IMPORTANCE) or fake.said_short(labels[codes[0]])
    first = vs.pick_said(lullaby, IMPORTANCE, labels[codes[1]])
    assert one["text"] == f"You picked {first} over {short}. Why did that matter more to you?"
    assert one["spoken"] == f"What mattered more to you than {short}?"
    two = vs.follow_up_question(lullaby, [vs.Pick(dimension=IMPORTANCE, codes=codes[1:3])], vs.LINK_PRIMARY,
                                interview, "tok", stem=(IMPORTANCE, False))
    second = vs.pick_said(lullaby, IMPORTANCE, labels[codes[2]])
    assert two["text"] == f"You picked {first} and {second} over {short}. Why did those matter more to you?"
    assert not fake.over_cap(two["text"])
    long = vs.follow_up_question(lullaby, [vs.Pick(dimension=IMPORTANCE, codes=codes[3:5])], vs.LINK_PRIMARY,
                                 interview, "tok", stem=(IMPORTANCE, False))
    third, fourth = (vs.pick_said(lullaby, IMPORTANCE, labels[c]) for c in codes[3:5])
    assert fake.over_cap(f"You picked {third} and {fourth} over {short}. Why did those matter more to you?")
    assert long["text"] == f"You picked {third} over {short}. Why did that matter more to you?", \
        "two picks past the cap say the first alone, *that* agreeing"
    none = vs.follow_up_question(lullaby, [vs.Pick(dimension=IMPORTANCE, chip="NONE_OF_THESE")], vs.LINK_PRIMARY,
                                 interview, "tok", stem=(IMPORTANCE, False))
    assert none["text"] == "You said none of these. What would you most like made easier instead?"


def test_over_cap_reads_each_sentence():
    assert not fake.over_cap("You picked a over b. Why did that matter more to you?")
    assert fake.over_cap("You picked " + " ".join(["word"] * 18) + " over b. Why?")


def test_the_bands_are_said_as_a_person_says_a_range():
    """keel-cloud 208 FR-1's own cases (`TheFollowUpSaysThePickBackTest`): Fresco's price, Palus's percent (and in words
    on the spoken line), AirCaps' up front, the round figures, an old label's own unit and period."""
    fresco = "What would Fresco be worth to you a month, per site?"
    assert fake.price_said_back(fresco, "$500 to under $800", "Fresco") == \
        "You said about $500 to $800 a site a month for Fresco. What would make it worth more to you?"
    palus = fake.price_said_back("What fee a year would feel fair to you?", "0.1% to under 0.25%", "Palus")
    assert palus == "You said about 0.1% to 0.25% a year for Palus. What would make it worth more to you?"
    assert fake.percent_said(palus) == ("You said about a tenth to a quarter of a percent a year for Palus. What would "
                                        "make it worth more to you?")
    assert fake.percent_said("You said under 0.1% a year.") == "You said under a tenth of a percent a year."
    assert fake.band_written("$250 to under $599", "up front") == "about $250 to $600 up front"
    from decimal import Decimal                                         # noqa: PLC0415
    assert [fake.band_round(Decimal(v)) for v in ("599", "990", "1234", "12.5", "49.99", "0.249", "750")] == \
        [Decimal(v) for v in ("600", "1000", "1234", "12.5", "50", "0.25", "750")]
    assert fake.band_written("$990 to $1,234", None) == "about $1,000 to $1,234"
    assert fake.band_written("Over $5,000", "a year") == "$5,000 or more a year"
    assert fake.band_written("I wouldn't pay for this", "a year") is None
    assert fake.unit_of("What fee a year, per office, would feel fair to you?") == "an office a year"
    assert fake.unit_of("Would you pay for it?") is None
    assert fake.duration_said("1 to under 3 months") == "1 to 3 months"
    assert fake.duration_said("Over 6 months") == "over 6 months"
    band = _cloud(VECTORS + "BandSaid.java")
    assert f'ROUND_WITHIN = new BigDecimal("{fake.ROUND_WITHIN}")' in band


def test_purchase_friction_says_the_band_back_first(backtest):
    expanse = backtest["17-expanse"]
    labels = {"days_under_14": "Under 2 weeks", "days_14_to_42": "2 to under 6 weeks",
              "days_42_to_90": "6 weeks to 3 months", "not_needed": "It wouldn't be needed"}
    interview = _interview(PF, labels, question="If your lab bought it, how long would it take?", part=3)
    owed = vs.follow_up_question(expanse, [vs.Pick(dimension=PF, codes=["days_42_to_90"])], vs.LINK_B2B, interview,
                                 "tok", stem=(PF, False))
    name = vs.served_idea_name(interview) or vs._typed_idea_name(expanse)
    assert owed["text"] == owed["spoken"] == \
        f"You said 6 weeks to 3 months. What would take the time in buying {fake.named(name)}?"


def test_compatibilitys_second_stem_says_the_pick_back():
    assert fake.ALSO["solution.compatibility"][1:] == (
        "You said yes, with some steps. What did you have to do?",
        "You said yes, with some steps. What did you have to do?", "What steps did it take?")
    assert fake.fill_wording(fake.ALSO_NAMED["solution.compatibility"]["text"],
                             {"{short_name}": "getting your phone online", "{occasion}": "night"}) == \
        "You said yes, with some steps. What went into getting your phone online for that night?"
    composer = _cloud(APPLICATION + "FollowUpComposer.java")
    assert 'Map.entry("{their_pick}", "the one you picked"), Map.entry("{their_next}", "the other one")' in composer
    assert fake.FILL_DEFAULTS["{their_pick}"] == "the one you picked"
    assert fake.FILL_DEFAULTS["{their_next}"] == "the other one"
    assert "SAID_MAX_WORDS = com.keeldiscovery.cloud.domain.vectors.ShortName.MAX_WORDS + 1;" in composer
    assert fake.SAID_MAX_WORDS == 6
