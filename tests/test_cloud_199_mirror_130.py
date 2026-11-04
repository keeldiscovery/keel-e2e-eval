"""Spec 130, the mirrors owed by keel-cloud 199 (the founder's beliefs keep the founder's words; keel-cloud-docs
`cd0d736d`). No contract moved.

The moved templates and the recorded sentences read through 199's rules (`corpus.spec199_reads`, keel-cloud's
`VectorCorpusFixture.spec199Reads`; no corpus revision -- spec 141's pattern): Buyer and payer *... must agree first.*
over every role, Relative advantage *For most, with it, their last {occasion} would have given them {value}.* over every
benefit, Commitment without *now*, Compatibility *Most {actor_plural} {value}.* (*For most ...* for a condition with its
own subject, `subjectless`), Importance *... hard when {circumstance}.*, Purchase friction's no-time sentence without
*quickly*, Existing sacrifice's payer and *per {unit}* dropped where the base names it (`chain.unit_beside`);
Compatibility's question; the rule names L25-L28 and W11 in the notes the back-test reports by name; the walker's
*not sure* on the time box where the entry's sources give no time.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from evals import backtest as bt
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import chain as chain_mod
from instructions import corpus as corpus_mod
from instructions import friction as friction_mod
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
FIXTURE = "src/test/java/com/keeldiscovery/cloud/corpus/VectorCorpusFixture.java"


def _cloud(path: str) -> str:
    full = KEEL_CLOUD / path
    if not full.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    return full.read_text(encoding="utf-8")


def _rows() -> dict:
    raw = json.loads(_cloud("src/main/resources/keel/dimension-registry.json"))
    if "must agree first" not in json.dumps(raw):
        pytest.skip("keel-cloud before 199")
    return {d["key"]: d for d in raw["dimensions"]}


def _golden(entry_id: str):
    return corpus_mod.load(KEEL_CLOUD).by_id(entry_id)


def _backtest(entry_id: str):
    corpus = corpus_mod.load(KEEL_CLOUD, backtest=True)
    return next(e for e in corpus.entries if e.id == entry_id)


# --------------------------------------------------------------------------------------------- the templates

def test_the_registrys_templates_are_199s():
    rows = _rows()
    founder = {k: r["founder"] for k, r in rows.items()}
    assert founder["commercial.buyer_payer_alignment"]["belief_template"] == corpus_mod.BUYER_BELIEF_TEMPLATE_199
    assert founder["solution.relative_advantage"]["belief_template"] == corpus_mod.ADVANTAGE_BELIEF_TEMPLATE_199
    assert founder["commercial.commitment"]["belief_template"] == corpus_mod.COMMITMENT_TEMPLATE_199
    assert founder["commercial.commitment"]["belief_template_decider"] == corpus_mod.COMMITMENT_DECIDER_TEMPLATE_199
    assert founder["solution.compatibility"]["belief_template"] == corpus_mod.COMPATIBILITY_BELIEF_TEMPLATE_199
    assert founder["problem.importance"]["belief_template"] == corpus_mod.IMPORTANCE_BELIEF_TEMPLATE_199
    assert rows["solution.compatibility"]["lullaby"]["founder_question"] == vs_screens.COMPATIBILITY_ANSWER_QUESTION
    beliefs = _cloud(VECTORS + "BeliefSentence.java")
    assert 'OWN_SUBJECT = "For most {actor_plural}, {value}.";' in beliefs
    assert corpus_mod.COMPATIBILITY_OWN_SUBJECT == "For most {actor_plural}, {value}."
    friction = _cloud(VECTORS + "PurchaseFriction.java")
    assert 'UNDATED_BELIEF = "Most {deciders} would get through {value}, or not need it.";' in friction
    assert friction_mod.UNDATED_BELIEF == corpus_mod.FRICTION_UNDATED_BELIEF_199
    assert friction_mod.belief("agencies", "the owner's approval", None) == \
        "Most agencies would get through the owner's approval, or not need it."
    prompts = _cloud(VECTORS + "AnswerPrompts.java")
    assert f'"{vs_screens.COMPATIBILITY_ANSWER_QUESTION}"' in prompts
    assert 'B2B_PAYER = "the buyer\'s organisation"' in _cloud(VECTORS + "CostEstimate.java")
    assert corpus_mod.B2B_PAYER == "the buyer's organisation"


def test_the_reader_is_the_clouds_spec199_reads():
    text = _cloud(FIXTURE)
    body = text[text.index("public static String spec199Reads("):]
    body = body[:body.index("\n    private static String joined(")]
    for said in ('" now."', '" quickly, or not need it."', '", or not need it."', '"The problem already costs "',
                 '"^(.*? decides, and )(.+) has to agree\\\\.$"', '" must agree first."',
                 '"^For most, their last (.+?) would have gone better with it: (.+)\\\\.$"',
                 '"For most, with it, their last "', '" would have given them "', 'subjectless(condition)'):
        assert said in body, said


# --------------------------------------------------------------------------------- the record, read by 199

@pytest.mark.parametrize("entry_id, key, read", [
    ("05-paidly", "commercial.commitment", "In most cases the agency would start a read-only trial."),
    ("03-lullaby", "commercial.commitment",
     "Most parents of babies under six months would allow it to use the microphone at night."),
    ("05-paidly", "commercial.purchase_friction",
     "Most agencies would get through the agency owner's approval, or not need it."),
    ("05-paidly", "commercial.existing_sacrifice",
     "The problem already costs the buyer's organisation about $100 to $300 a month."),
    ("02-compliancelog", "commercial.buyer_payer_alignment", "The HR manager decides, and the HR director must agree "
                                                             "first."),
    ("03-lullaby", "commercial.buyer_payer_alignment", "The parent decides, and nobody else must agree first."),
    ("03-lullaby", "solution.relative_advantage",
     "For most, with it, their last night would have given them fewer tries before the baby settles."),
    ("02-compliancelog", "solution.compatibility",
     "Most HR managers at firms of 200 to 500 people could connect a tool to the learning system."),
    ("07-mulchrun", "solution.compatibility",
     "Most landscaping crew leads in the Dallas suburbs knew the night before how much was needed."),
    ("03-lullaby", "solution.compatibility",
     "For most parents of babies under six months, their phone was within reach of the cot."),
])
def test_the_golden_record_reads_as_the_engine_writes_since_199(entry_id, key, read):
    entry = _golden(entry_id)
    before = entry.founder_calibration[key]["belief_sentence"]
    assert corpus_mod.spec199_reads(entry, key) == corpus_mod.engine_belief(entry, key) == read
    assert entry.founder_calibration[key]["belief_sentence"] == before, "never rewritten"


def test_every_role_and_every_benefit_is_joined_with_and():
    class Entry:
        context = {"actor_plural": "contractor operations leads"}
        persona = {"decision_maker": {"role": "CFO"}}
        founder_calibration = {
            "commercial.buyer_payer_alignment": {"belief_sentence": "The CFO decides, and the CFO has to agree."},
            "solution.relative_advantage": {"belief_sentence": "For most, their last job would have gone better with "
                                                                "it: Fewer missed items."}}
        lists = {"commercial.buyer_payer_alignment": [{"label": "CFO"}, {"label": "Project executive"},
                                                      {"label": "Nobody else"}],
                 "solution.relative_advantage": [{"label": "Fewer missed items."}, {"label": "A log done by noon"}]}

        def founder_list(self, key):
            return {"items": self.lists[key]}

        def tested(self, key):
            return self.lists[key][0]

    entry = Entry()
    assert corpus_mod.spec199_reads(entry, "commercial.buyer_payer_alignment") == \
        "The CFO decides, and the CFO and the project executive must agree first."
    assert corpus_mod.spec199_reads(entry, "solution.relative_advantage") == \
        "For most, with it, their last job would have given them fewer missed items and a log done by noon."
    assert corpus_mod.joined(["a", "b", "c"]) == "a, b and c"


@pytest.mark.parametrize("condition, bare", [
    ("They could talk over the noise on site", "could talk over the noise on site"),
    ("could connect a tool to the learning system", "could connect a tool to the learning system"),
    ("Their phone was within reach of the cot", None),
    ("The hotel's phones forward missed calls", None),
    ("Staff could scan each delivery", None),
    ("knew the night before how much was needed", "knew the night before how much was needed"),
    ("", None),
])
def test_compatibility_is_read_as_a_verb_phrase_with_no_subject(condition, bare):
    assert corpus_mod.subjectless(condition) == bare


# ---------------------------------------------------------------------------- Existing sacrifice (FR-10)

def test_the_base_is_said_once():
    _cloud(VECTORS + "CommercialChain.java")
    assert chain_mod.unit_beside("cluster", "the cluster's GPU hours", "month") is None
    assert chain_mod.unit_beside("agent", "the agent's runs in production", "month") is None
    assert chain_mod.unit_beside("site", "the daily log", "month") == "site"
    assert chain_mod.unit_beside("pole", "the poles inspected", "each") == "pole", "a cost each time keeps its unit"
    assert chain_mod.unit_beside("call minute", "staffed call minutes", "month") == "call minute"
    assert chain_mod.unit_beside(None, "x", "month") is None
    expanse = _backtest("17-expanse")
    cost = expanse.founder_calibration["commercial.existing_sacrifice"]
    assert cost["belief_phrase"] == "about 30% to 59% of the cluster's GPU hours a month"
    assert chain_mod.cost_said(cost["answer"], expanse.occasion(), None) == cost["belief_phrase"]
    text = _cloud(VECTORS + "CommercialChain.java")
    assert "static String unitBeside(String unit, String base, String period)" in text
    assert '(?:\'s|s|es)?\\\\b' in text


# ------------------------------------------------------------------------------ the rule names (FR-12)

def test_the_notes_name_l25_to_l28_and_w11():
    applier = _cloud(APPLICATION + "ScreenResultApplier.java")
    for rule in ("L25", "L26", "L27", "L28"):
        assert f'"{rule}: ' in applier or f'"{rule}: \'' in applier, rule
        assert rule in bt.LOCK_NOTES, rule
    assert '"W11: offer_name \'' in _cloud(VECTORS + "Wording.java") and "W11" in bt.LOCK_NOTES
    rows = [{"screen": "CALIBRATION_QUESTIONS", "detail": "breach result.questions[0].list.items: L25: the founder "
                                                          "named 'the project executive' as having to agree"},
            {"screen": "PROBLEM_INTERPRET", "turns": [{"content": "W11: offer_name 'someone to manage it' names a "
                                                                  "person"}]}]
    found = bt.lock_notes(None, rows)
    assert [n["rule"] for n in found] == ["L25", "W11"]
    assert found[0]["means"].startswith("a role the founder named")


# ----------------------------------------------------------------------- the time box, not sure (FR-4)

def test_the_walker_answers_not_sure_where_the_sources_give_no_time():
    # spec 132 FR-8 re-pin (keel-cloud 206 *Owed elsewhere*): the walker types the corpus entry's own time, never leaves
    # the box empty -- `time_sourced` still reads the sources, but no longer turns a recorded time into *not sure*
    fresco = _backtest("08-fresco")
    assert vs.founder_duration(fresco) == {"count": 2, "unit": "WEEKS"}
    assert not vs.time_sourced(fresco), "08-fresco's 2 weeks is an author's choice"
    assert vs.walker_duration(fresco) == {"count": 2, "unit": "WEEKS"}
    codyco = _backtest("21-codyco")
    assert not vs.time_sourced(codyco), "its bookings *in 4 weeks* is no purchase time"
    assert vs.walker_duration(codyco) == vs.founder_duration(codyco)
    # 2026-11-02 21:44 ET: S-016 and the sharing journeys stopped at Purchase friction's Choose by spec 119's name, so a
    # golden entry answers *not sure* with the walker's own default beside it for a page that draws no such control
    assert vs.walker_duration(_golden("05-paidly")) == {"unsure": True, "default": True, **vs.GOLDEN_DEFAULT_DURATION}


def test_the_fixed_three_where_the_time_was_not_sure_read_the_band_back():
    fresco = _backtest("08-fresco")
    person = next(p for p in vs.person_inputs(fresco)
                  if any(k.dimension == "commercial.purchase_friction" and k.codes for k in p.picks))
    fixed = {"commercial.purchase_friction": {"options": [{"optionId": c} for c in friction_mod.UNDATED_CODES]}}
    moved, notes = vs.served_friction_picks(fresco, person, fixed)
    pick = next(k for k in moved.picks if k.dimension == "commercial.purchase_friction")
    assert pick.codes[0] in friction_mod.UNDATED_CODES and notes
    banded = {"commercial.purchase_friction": {"options": [{"optionId": c} for c in friction_mod.codes(
        fresco.duration())]}}
    assert vs.served_friction_picks(fresco, person, banded) == (person, [])
    for code, want in (("days_7_to_14", "yes_quick"), ("days_14_to_30", "yes_long"), ("not_needed", "not_needed")):
        assert (friction_mod.NOT_NEEDED if code == "not_needed" else
                "yes_quick" if friction_mod.within(code, fresco.duration()) else "yes_long") == want, code


def test_the_choose_screen_ticks_not_sure_where_drawn():
    import inspect                                                      # noqa: PLC0415
    source = inspect.getsource(vs_screens)
    assert 'DURATION_UNSURE_TESTID = "duration-unsure"' in source
    assert '"duration_unsure": unsure' in source and 'unsure = "ticked" if box.count() else ("not drawn, default typed" if duration.get("default") else "not drawn")' in source
    # spec 129 (keel-web 164 W6): the control is drawn, a button with aria-pressed -- pressed and held
    assert "unsure = self._press_duration_unsure(box.first)" in source
    assert re.search(r"duration = vs\.walker_duration\(j\.entry\)", inspect.getsource(
        __import__("evals.corpus_scenario", fromlist=["x"])))
