"""Spec 123 -- the referee follows keel-cloud 193 (keel-cloud-docs `2d848360`).

FR-1 the cost sentence names who really spends (`chain.cost_belief`, `CommercialChain.costBelief`); FR-2 E4 measures
the Frequency question served (`wording.framed_fault`, `vectors_script.e4_fault`), the writer shortens, never cut;
FR-3 the problem statement's numbers are the cloud's validator's (no copy here); FR-4 no fallback condition on the
decision-maker's link. Beside them, keel-cloud 192 FR-1 (the stage reads as its cards read), which the brief-facts
compare needed at `2d848360` (tasks.md, *Not foreseen*).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from harness import vectors_script as vs
from instructions import brief_facts as bf
from instructions import chain as chain_mod
from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from instructions import validate as validate_mod
from instructions import wording as wording_mod
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
SACRIFICE = "commercial.existing_sacrifice"
CHAIN = "src/main/java/com/keeldiscovery/cloud/domain/vectors/CommercialChain.java"


def _cloud(path: str) -> str:
    full = KEEL_CLOUD / path
    if not full.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    return full.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def registry():
    try:
        return cloud_mod.registry_of_record(KEEL_CLOUD)
    except Exception as missing:                                        # noqa: BLE001
        pytest.skip(f"no keel-cloud registry of record: {missing}")


def _backtest(entry_id: str, registry):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {entry_id}")
    return corpus_mod.load_file(path, registry=registry, backtest=True)


def _hours(low, high, base, unit, period="month"):
    return {"mode": "HOURS", "low": low, "high": high, "period": period, "base": base, "unit": unit}


def _rate(low, base, unit, loss):
    return {"mode": "RATE", "low": low, "high": low, "period": "month", "currency": "USD", "measure": "%",
            "base": base, "unit": unit, "lossPhrase": loss}


CODE_FOUR = dict(actor="patrol officer", actor_plural="patrol officers at small and mid-sized police departments")
ISSEN = dict(actor="language learner", actor_plural="intermediate and advanced learners of a foreign language")
TRANSLOAD = dict(actor="dock supervisor", actor_plural="dock supervisors at freight terminals")
SUPERS = dict(actor="site superintendent", actor_plural="site superintendents")


# --------------------------------------------------------------------------------- FR-1: the cost sentence

def test_the_three_entries_sentences_are_193s_table():
    """keel-cloud `TheCostSentenceNamesWhoReallySpendsTest.theThreeEntriesSentences`, word for word."""
    assert chain_mod.cost_belief(_hours(40, 60, "the incident reports", "officer"), "incident report", "chief",
                                 "Police chiefs", True, **CODE_FOUR) == (
        "Patrol officers at small and mid-sized police departments already spend 40 to 60 hours a month on the "
        "incident reports.")
    assert chain_mod.cost_belief(_hours(8, 16, "the speaking practice they go without", "person"), "practice session",
                                 None, "intermediate and advanced learners of a foreign language", False, **ISSEN) == (
        "Intermediate and advanced learners of a foreign language already spend 8 to 16 hours a month.")
    assert chain_mod.cost_belief(
        _rate(10, "the shipments", "terminal", "Charges on freight that is bigger or heavier than the bill says"),
        "inbound shipment", "terminal manager", "Terminal managers", True, **TRANSLOAD) == (
        # spec 137 (keel-cloud 213 FR-2b, `TheCostSentenceNamesWhoReallySpendsTest` re-pinned likewise): one measure --
        # no *per terminal* beside a percent of the shipments
        "About 10% of the shipments a month: charges on freight that is bigger or heavier than the bill says.")


def test_a_rates_loss_is_its_predicate_when_it_opens_on_a_verb():
    args = ("inbound shipment", "terminal manager", "Terminal managers", True)
    assert chain_mod.cost_belief(_rate(10, "the shipments", "terminal", "carry a dimension error"), *args,
                                 **TRANSLOAD) == "About 10% of the shipments a month carry a dimension error."
    assert chain_mod.cost_belief(_rate(10, "the shipments", "terminal", "billed as declared"), *args,
                                 **TRANSLOAD) == "About 10% of the shipments a month: billed as declared."
    assert chain_mod.cost_belief(_rate(10, "the shipments", "terminal", None), *args, **TRANSLOAD) == (
        "Dock supervisors at freight terminals already lose about 10% of the shipments a month.")
    assert chain_mod.loss_predicate("never come back") and not chain_mod.loss_predicate("runs late")


def test_money_keeps_the_deciders_and_a_site_unit_its_shape():
    money = {"mode": "MONEY", "low": 0.90, "high": 0.90, "period": "each", "currency": "USD",
             "base": "staffed call time", "unit": "call minute"}
    assert chain_mod.cost_belief(money, None, "support desk lead", "Support desk leads", True,
                                 actor="support agent", actor_plural="support agents on the phones") == (
        "Support desk leads already spend about $0.90 on staffed call time per call minute, each.")
    assert chain_mod.cost_belief(_hours(30, 60, "the daily log", "site"), None, "general contractor",
                                 "General contractors", True, **SUPERS) == (
        "Site superintendents already spend 30 to 60 hours per site a month on the daily log.")
    assert chain_mod.cost_belief(_hours(2, 3, "the shifts they miss", "site"), None, "general contractor",
                                 "General contractors", True, **SUPERS) == (
        "Site superintendents already spend 2 to 3 hours per site a month.")
    assert chain_mod.own_noun("officers", **{"actor": "patrol officer", "actor_plural": CODE_FOUR["actor_plural"]})
    assert not chain_mod.own_noun("site", **SUPERS)


def test_the_mirror_reads_the_engines_lists(registry):
    """`LACK`, `LOSS_VERBS` and `BASE_ENDS` are `CommercialChain`'s own."""
    import re                                                           # noqa: PLC0415
    text = _cloud(CHAIN)
    verbs = re.search(r"LOSS_VERBS = java\.util\.Set\.of\(([^;]*)\);", text, re.S)
    assert verbs and set(re.findall(r'"([^"]+)"', verbs.group(1))) == chain_mod.LOSS_VERBS
    ends = re.search(r"BASE_ENDS = java\.util\.Set\.of\(([^;]*)\);", text, re.S)
    assert ends and set(re.findall(r'"([^"]+)"', ends.group(1))) == chain_mod.BASE_ENDS
    assert '"(?i)\\\\b(?:go|goes|went|going) without\\\\b|\\\\black(?:s|ing)?\\\\b|\\\\bmiss(?:es|ed|ing)?\\\\b"' in text


@pytest.mark.parametrize("entry_id, sentence", [
    ("18-careforce", "About 30% to 33% of the patients due for a visit or screening per health center a month: visits "
                     "and screenings never booked because nobody reached the patient."),
    ("08-fresco", "Construction superintendents on commercial jobs already spend 30 to 60 hours per site a month on "
                  "the daily log."),
    ("14-code-four", "Patrol officers at small and mid-sized police departments already spend 40 to 60 hours a month "
                     "on the incident reports."),
])
def test_revision_22_amended_in_place_reads_as_the_engine_writes(registry, entry_id, sentence):
    """FR-1 (keel-cloud 193 *Not foreseen*): revision 22 stands, its 17 sentences moved in place; the load holds each to
    `cost_belief` (rule C), and three are pinned here as the yaml says them."""
    entry = _backtest(entry_id, registry)
    assert entry.founder_calibration[SACRIFICE]["belief_sentence"] == sentence


def test_every_back_test_entry_loads_and_seventeen_are_amended(registry):
    directory = corpus_mod.backtest_dir(KEEL_CLOUD)
    corpus = corpus_mod.load(KEEL_CLOUD, registry=registry, backtest=True)
    assert corpus.entries
    # spec 130 re-pin (keel-cloud 199 FR-10): three of the seventeen carry 199's note above 193's, so the note is read
    # in the header, not only at its head
    amended = [p.name for p in sorted(directory.glob("*.yaml"))
               if "# AMENDED IN PLACE (keel-cloud spec 193 FR-1" in p.read_text(encoding="utf-8").split("\nid:", 1)[0]]
    assert len(amended) == 17, amended


# -------------------------------------------------------------------------------- FR-2: E4 in the served frame

def test_e4_measures_the_question_served_and_asks_the_writer():
    w = vs.Window(count=5, unit="WORKING_DAYS")
    careforce = "get every patient who is due for a screening or visit called and booked"
    fault = vs.e4_fault(w, careforce)
    assert fault and fault.startswith("E4: framed, the clause makes the Frequency question served"), fault
    assert "In the last 5 working days, on how many days did you get every patient" in fault
    assert fault.endswith("so shorten the clause, keeping its verb and its object"), fault
    assert vs.e4_fault(w, "call the patients due for a visit") is None
    # the instruction eval's E4 says the same
    window = type("W", (), {"words": lambda self: "the last 5 working days", "plural": "working days",
                            "count": 5})()
    assert (wording_mod.framed_fault(careforce, window) or "").startswith(
        "E4: framed, the clause makes the Frequency question served")


def test_the_scripted_gate_clauses_fit_the_served_frame_and_none_is_cut():
    """The golden entries' scripted writer clauses fit E4 as served (five shortened, verb and object kept); the founder's
    past-tense clause is unchanged by 193 (cut to its window's cap by spec 136); `frequency_held` serves each
    whole."""
    corpus = corpus_mod.load(KEEL_CLOUD)
    for entry in corpus.entries:
        event = vs.event_base(entry)
        window = vs.window_of(entry)
        assert vs.e4_fault(window, event) is None, entry.id
        assert vs.frequency_held(window, event) == vs.frequency_served(window, event), entry.id
    # spec 136 re-pin (keel-cloud 212 FR-1, FR-3): the founder's clause within its window's cap (*to be paid* off), and
    # the strangers' its second person, by code
    assert vs.PROBLEM_CLAUSES["05-paidly"] == ("waited beyond agreed terms for an approved invoice",
                                               "wait beyond agreed terms for an approved invoice")


def test_an_overrunning_scripted_clause_is_reported_never_cut():
    entry = type("E", (), {"id": "x-over", "context": {"recall_window": {"count": 4, "unit": "WEEKS"},
                                                       "circumstance": "the long and winding day of a very busy "
                                                                       "shift is finally over at last"}})()
    with pytest.raises(vs.VectorsScriptError, match="E4: framed, .* keeping its verb and its object"):
        vs.event_base(entry)


# ------------------------------------------------------------------- FR-3: the numbers are the cloud validator's

def test_the_statements_numbers_are_judged_by_the_clouds_own_validator():
    """keel-cloud 193 FR-3 (`ScreenResultApplier.statementNumberFault`): P2 lives in keel-cloud, and the instruction eval
    hands PROBLEM_INTERPRET to the aggregate (`instructions/validate.py`) rather than keep a copy -- so a world's number
    the founder typed passes here exactly when it passes there. No mark number moves."""
    assert validate_mod._SHAPE_MARKERS["PROBLEM_INTERPRET"] == "InferenceScreen.PROBLEM_INTERPRET"
    text = _cloud("src/main/java/com/keeldiscovery/cloud/application/ScreenResultApplier.java")
    assert "statementNumberFault(" in text and "BELIEF_WORDS" in text


# ----------------------------------------------------------------- FR-4: no fallback condition for the decider

def test_no_written_decider_condition_serves_none(registry, monkeypatch):
    corpus = corpus_mod.load(KEEL_CLOUD, registry=registry)
    for entry in corpus.entries:
        assert vs.decider_condition(entry) is None, entry.id
    served = 0
    for entry_id in ("08-fresco", "10-palus", "17-expanse"):
        entry = _backtest(entry_id, registry)
        written = vs.decider_screener(entry)
        assert written, entry_id
        if vs.segment_of(entry)["condition"]:
            # `RespondentQuestionsRules.deciderCondition`: the writer's clause, served where the study has a condition
            assert vs.decider_condition(entry) == {"question": written["question"], "inCodes": [written["inside"]]}
            served += 1
        else:
            assert vs.decider_condition(entry) is None, entry_id
    # a written clause on a study with a condition is served (none of the three records a segment condition today)
    fresco = _backtest("08-fresco", registry)
    real = vs.segment_of
    monkeypatch.setattr(vs, "segment_of", lambda e: {**real(e), "condition": "run jobs on Procore"})
    written = vs.decider_screener(fresco)
    assert vs.decider_condition(fresco) == {"question": written["question"], "inCodes": [written["inside"]]}
    from dataclasses import replace                                    # noqa: PLC0415
    assert vs.decider_condition(replace(fresco, screeners={})) is None, "no written clause: no condition, even with the segment's"
    # keel-cloud 193 FR-4a: the decision-maker's part 3 with none written is noted *none is asked*
    source = _cloud("src/main/java/com/keeldiscovery/cloud/application/RespondentQuestionsRules.java")
    assert "written; none is asked" in source


# ---------------------------------------------------------- keel-cloud 192 FR-1: the stage reads as its cards

def test_a_bar_line_past_its_bar_raises_the_stage_never_lowers_it():
    cards = [{"key": "solution.compatibility", "status": "HOLDING_UP", "statusWords": "Holding up"},
             {"key": "solution.adoption_friction", "status": "PEOPLE_DISAGREE", "statusWords": "Did not hold · x"}]
    assert bf.stage_verdict(cards, {"verdict": "PEOPLE_DISAGREE", "deciding": "solution.adoption_friction"}) == \
        "NOT_HOLDING_UP"
    assert bf.stage_verdict(cards[:1], {"verdict": "PEOPLE_DISAGREE"}) == "PEOPLE_DISAGREE", "never lowered"
    assert bf.stage_verdict([], {"verdict": "NOT_TESTED"}) == "NOT_TESTED"
    left = [{"key": "solution.compatibility", "status": "LEFT_OUT", "statusWords": "Left out"}]
    assert bf.card_status(left[0]) is None and bf.stage_verdict(left, {"verdict": "HOLDING_UP"}) == "HOLDING_UP"
