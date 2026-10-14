"""The `BRIEF` subject at `MARKS_VERSION` 18 (spec 040; keel-cloud 089, contract 13): its context and its seven
reading marks (judgement call 82).

Stackless and modelless. **Each mark fails for its own reason and passes for its own reason**: every one of the seven
has a mutation of a good reading that misses it and only it, because a mark that only ever showed its green half is
indistinguishable from a mark that is always green. The three good readings are the fixtures under
`tests/fixtures/brief/` -- a NOT_YET and a BUILD_BUT_CHANGE over keel-cloud's own facts for corpus r10 01-countly and
02-compliancelog, and keel-cloud's payroll worked example (B2B, USD).
"""

from __future__ import annotations

import copy
import json
import types
from pathlib import Path

import pytest

from instructions import brief as brief_mod
from instructions import context as context_mod
from tests import v9_fixtures as fx

FIXTURES = Path(__file__).parent / "fixtures" / "brief"
SCENARIOS = ("not-yet", "build-but-change", "build-but-change-b2b")


def load(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


class _Case:
    def __init__(self, fixture):
        self.case_id = fixture["case_id"]
        self.run_index = 1
        self.payload = {"context": {"facts": fixture["facts"], "stories": fixture["stories"]}}


_ENTRY = types.SimpleNamespace(id="fixture", people=lambda: [
    types.SimpleNamespace(person="Ann Abbott"), types.SimpleNamespace(person="Bo Brand")])


def score(fixture, result=None):
    return brief_mod.score_brief(_Case(fixture), _ENTRY, result or fixture["result"], outcome="COMPLETED")


# ------------------------------------------------------------------------------ the good readings

@pytest.mark.parametrize("name", SCENARIOS)
def test_each_scenario_meets_all_seven_marks(name):
    got = score(load(name))
    assert got.marks == {m: True for m in brief_mod.MARK_NAMES}, got.findings
    assert got.met is True and got.paragraph.startswith("headline: ")


def test_the_scenarios_are_two_decisions_and_the_b2b_one_is_keel_clouds_worked_example():
    labels = {n: load(n)["facts"]["decision"]["label"] for n in SCENARIOS}
    assert labels == {"not-yet": "NOT_YET", "build-but-change": "BUILD_BUT_CHANGE",
                      "build-but-change-b2b": "BUILD_BUT_CHANGE"}
    assert "decision-makers" in load("build-but-change-b2b")["facts"]["decision"]["reason"]
    assert load("build-but-change-b2b")["case_id"] == "payroll/BRIEF/worked-example"


def test_the_readings_answer_where_each_stage_broke():
    for name in SCENARIOS:
        fixture = load(name)
        for stage in ("problem", "solution", "commercial"):
            broke = (fixture["facts"][stage].get("broke") or {}).get("key")
            if broke:
                assert broke in fixture["result"][stage]["answer"]["cites"], (name, stage)


# ------------------------------------------------------------------- every mark's own mutation

def mutate(name, edit):
    fixture = load(name)
    result = copy.deepcopy(fixture["result"])
    edit(result)
    return score(fixture, result)


def only(got, mark):
    assert got.marks[mark] is False, got.findings
    assert [m for m in brief_mod.MARK_NAMES if got.marks[m] is False] == [mark], got.marks
    return got.findings[mark]


def test_shape_misses_a_long_sentence_and_a_fourth_test_and_a_third_quote():
    only(mutate("not-yet", lambda r: r["headline"].update(text="x" * 401)), "shape")
    only(mutate("not-yet", lambda r: r["next"]["tests"].extend(
        {"key": "problem.frequency", "text": "Ask more."} for _ in range(2))), "shape")
    only(mutate("not-yet", lambda r: r.update(quotes=r["quotes"] * 3)), "shape")


def test_shape_misses_a_missing_answer_and_the_old_tiles_result():
    found = only(mutate("not-yet", lambda r: r["solution"].pop("answer")), "shape")
    assert "solution.answer" in found
    old = {"headline": load("not-yet")["result"]["headline"],
           "tiles": {"problem": {"text": "Holding up.", "cites": ["problem.prevalence"]}},
           "problem": {"conclusion": {"text": "It holds.", "cites": ["problem.prevalence"]}},
           "next": {"sentence": {"text": "Ask more.", "cites": ["problem.prevalence"]}, "tests": []},
           "quotes": []}
    got = score(load("not-yet"), old)
    assert got.marks["shape"] is False and got.met is False
    got = brief_mod.score_brief(_Case(load("not-yet")), _ENTRY, {"whatThisSays": "A paragraph."},
                                outcome="COMPLETED")
    assert got.marks["shape"] is False and got.met is False


def test_length_misses_three_sentences_and_forty_six_words():
    """089 FR-007: the headline and each answer at most two sentences and 45 words."""
    found = only(mutate("not-yet", lambda r: r["solution"]["answer"].update(
        text="It fits. 7 of 8 said yes. Staff could scan the delivery as it arrived.")), "length")
    assert "3 sentences; at most 2" in found
    found = only(mutate("not-yet", lambda r: r["headline"].update(
        text="Not yet " + "and people disagree " * 15 + "today.")), "length")
    assert "words; at most 45" in found


def test_a_decimal_or_a_price_does_not_split_a_sentence():
    assert brief_mod.sentences("Start at $1,000.50 a quarter. Then test more.") == 2
    assert brief_mod.sentences("One line without a stop") == 1
    assert brief_mod.sentences("Two. Lines!") == 2


def test_cites_misses_a_foreign_key_a_wrong_vector_and_no_cite():
    assert "not a dimension on this project" in only(mutate(
        "not-yet", lambda r: r["headline"].update(cites=["problem.nonsense"])), "cites")
    assert "is not a solution dimension" in only(mutate(
        "not-yet", lambda r: r["solution"]["answer"]["cites"].append("commercial.price")), "cites")
    only(mutate("not-yet", lambda r: r["headline"].update(cites=[])), "cites")


def test_cites_misses_a_test_aimed_at_no_target():
    found = only(mutate("not-yet", lambda r: r["next"]["tests"][0].update(key="problem.importance")),
                 "cites")
    assert "not a next-test target" in found


def test_the_headline_may_cite_any_vector():
    got = mutate("not-yet", lambda r: r["headline"].update(
        cites=["solution.compatibility", "problem.current_solution_satisfaction", "commercial.price"]))
    assert got.met, got.findings


def test_broke_misses_an_answer_that_does_not_cite_what_broke():
    """089 FR-007, call 15: where a stage broke, its answer cites the dimension that broke."""
    found = only(mutate("not-yet", lambda r: r["problem"]["answer"].update(cites=["problem.prevalence"])),
                 "broke")
    assert "the problem broke on 'problem.current_solution_satisfaction'" in found
    found = only(mutate("build-but-change", lambda r: r["commercial"]["answer"].update(
        cites=["commercial.ability_to_pay"])), "broke")
    assert "commercial.price" in found


def test_broke_asks_nothing_of_a_stage_that_held():
    got = mutate("not-yet", lambda r: r["solution"]["answer"].update(cites=["solution.relative_advantage"]))
    assert got.marks["broke"] is True and got.met, got.findings


def test_numbers_misses_an_invented_number_and_a_foreign_currency():
    assert "the number 77 is not in the facts" in only(mutate(
        "not-yet", lambda r: r["solution"]["answer"].update(text="It fits: 77 of 8 said yes.")), "numbers")
    assert "the currency $" in only(mutate(
        "not-yet", lambda r: r["commercial"]["answer"].update(text="Start at $35 a month.")), "numbers")


def test_numbers_misses_a_digit_or_a_number_word_in_a_test():
    assert "a test carries no number" in only(mutate(
        "not-yet", lambda r: r["next"]["tests"][0].update(text="Ask 5 more people.")), "numbers")
    only(mutate("not-yet", lambda r: r["next"]["tests"][0].update(text="Ask three more people.")), "numbers")


def test_a_b2b_reading_is_held_to_its_own_markets_symbol():
    got = mutate("build-but-change-b2b", lambda r: r["commercial"]["answer"].update(
        text="Start at £1,000 a quarter."))
    assert "the currency £ is not the market's" in only(got, "numbers")


def test_quotes_miss_a_paraphrase_and_a_stranger():
    assert "not a verbatim piece" in only(mutate(
        "not-yet", lambda r: r["quotes"][0].update(text="A keg went missing.")), "quotes")
    assert "has no story" in only(mutate(
        "not-yet", lambda r: r["quotes"][0].update(invitationId="someone-else")), "quotes")


@pytest.mark.parametrize("claim", ["They will pay for it.", "It proves the idea.",
                                   "The idea is validated.", "It works.", "See keel.example.com.",
                                   "Ann Abbott said so."])
def test_bans_miss_each_claim_the_brief_forbids(claim):
    got = mutate("not-yet", lambda r: r["solution"]["answer"].update(
        text="It fits, staff could scan the delivery as it arrived. " + claim))
    assert only(got, "bans")


def test_an_ordinary_sentence_is_not_a_ban():
    got = mutate("not-yet", lambda r: r["solution"]["answer"].update(
        text="They would scan each delivery on arrival, as you said."))
    assert got.met, got.findings


def test_names_are_held_whole_and_by_first_name():
    got = mutate("not-yet", lambda r: r["solution"]["answer"].update(text="Ann said it would fit."))
    assert "names a person ('Ann')" in only(got, "bans")


# ----------------------------------------------------------------------- failure and the totals

def test_a_needs_input_is_every_mark_missed_on_a_screen_with_nobody_to_ask():
    got = brief_mod.score_brief(_Case(load("not-yet")), _ENTRY, None, outcome="NEEDS_INPUT",
                                needs_input_questions=["which?"])
    assert got.needs_input and got.met is False
    assert set(got.marks.values()) == {False}


def test_a_failed_case_or_no_object_misses_every_mark():
    got = brief_mod.score_brief(_Case(load("not-yet")), _ENTRY, None, outcome="COMPLETED",
                                failed="refused twice")
    assert got.met is False and got.findings["shape"] == "refused twice"


def test_the_marks_are_seven_and_the_paragraph_and_tile_sentences_are_gone():
    assert brief_mod.MARK_NAMES == ("shape", "length", "cites", "broke", "numbers", "quotes", "bans")
    assert [s[:2] for s in brief_mod.SENTENCES] == [("headline", None), ("problem", "answer"),
                                                     ("solution", "answer"), ("commercial", "answer")]
    for retired in ("coverage", "register", "source_material"):
        assert retired not in brief_mod.MARK_NAMES
    assert (brief_mod.ANSWER_SENTENCES, brief_mod.ANSWER_WORDS) == (2, 45)


def test_the_brief_totals_are_all_seven_marks_or_nothing():
    good, bad = score(load("not-yet")), mutate("not-yet", lambda r: r["headline"].update(cites=[]))
    totals = brief_mod.totals([good, bad])
    assert totals["brief_answers"] == 0.5 and totals["brief_cases"] == 2
    assert "brief_paragraphs" not in totals
    assert totals["brief_by_mark"]["cites"] == {"met": 1, "of": 2}
    assert totals["brief_by_mark"]["length"] == {"met": 2, "of": 2}
    assert brief_mod.totals([])["brief_answers"] is None, "None, never 0"


# ----------------------------------------------------------------- the context built from a corpus

def test_a_context_built_from_the_corpus_scores_a_reading_over_its_own_facts():
    """The eval's reading of the fixture entry (`brief_facts.facts_for`, call 84) is what `check` reads: a
    reading citing and counting only what it carries -- and answering where the commercial stage broke -- meets
    every mark."""
    entry = fx.entry()
    context = context_mod.build_brief(entry)
    facts = context["facts"]
    assert facts["commercial"]["broke"]["key"] == "commercial.existing_sacrifice"
    person = context["stories"][0]
    result = {
        "headline": {"text": "Build, but change it: the problem holds, but they lose less than you said.",
                     "cites": ["problem.prevalence", "commercial.existing_sacrifice"]},
        "problem": {"answer": {"text": "Yes: 10 of 12 had it in the last 7 nights.",
                               "cites": ["problem.prevalence"]}},
        "solution": {"answer": {"text": "It fits: 5 of 7 said yes.", "cites": ["solution.compatibility"]}},
        "commercial": {"answer": {"text": "They lose about £10 a month, less than you said, so test a lower price.",
                                  "cites": ["commercial.existing_sacrifice", "commercial.price"]}},
        "next": {"tests": [{"key": facts["targets"][0]["key"], "text": "Ask what last month's lost mornings cost."}]},
        "quotes": [{"invitationId": person["invitation_id"], "text": person["story"][:40]}],
    }
    case = types.SimpleNamespace(case_id="09-fixture/BRIEF/run1", run_index=1, payload={"context": context})
    got = brief_mod.score_brief(case, entry, result, outcome="COMPLETED")
    assert got.met, got.findings


def test_a_context_handed_keel_clouds_facts_carries_them_whole():
    entry = fx.entry()
    facts = {"keys": ["problem.prevalence"], "decision": {"label": "BUILD"}}
    context = context_mod.build_brief(entry, facts=facts)
    assert context["facts"] is facts
    assert all("weight" not in b for b in context["beliefs"])
