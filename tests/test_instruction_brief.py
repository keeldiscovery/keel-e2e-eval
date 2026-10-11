"""The `BRIEF` subject at `MARKS_VERSION` 14 (spec 034; keel-cloud 079, contract 9): its context and its
five reading marks.

Stackless and modelless. **Each mark fails for its own reason and passes for its own reason**: every
one of the five has a mutation of a good reading that misses it and only it, because a mark that only
ever showed its green half is indistinguishable from a mark that is always green. The three good
readings are the fixtures under `tests/fixtures/brief/` -- a BUILD, a NOT_YET and a BUILD_BUT_CHANGE
B2B -- each built from keel-cloud's golden `validate-golden/BRIEF.json` shape.
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
SCENARIOS = ("build", "not-yet", "build-but-change-b2b")


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
    return brief_mod.score_brief(_Case(fixture), _ENTRY, result or fixture["result"],
                                 outcome="COMPLETED")


# ------------------------------------------------------------------------------ the good readings

@pytest.mark.parametrize("name", SCENARIOS)
def test_each_scenario_meets_all_five_marks(name):
    got = score(load(name))
    assert got.marks == {m: True for m in brief_mod.MARK_NAMES}, got.findings
    assert got.met is True and got.paragraph.startswith("headline: ")


def test_the_three_scenarios_are_the_three_decisions():
    labels = {n: load(n)["facts"]["decision"]["label"] for n in SCENARIOS}
    assert labels == {"build": "BUILD", "not-yet": "NOT_YET",
                      "build-but-change-b2b": "BUILD_BUT_CHANGE"}
    assert "decision-makers" in load("build-but-change-b2b")["facts"]["decision"]["reason"]


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


def test_shape_misses_a_long_sentence_and_a_third_test_and_a_third_quote():
    only(mutate("build", lambda r: r["headline"].update(text="x " * 201)), "shape")
    only(mutate("build", lambda r: r["next"]["tests"].extend(
        {"key": "problem.importance", "text": "Ask more."} for _ in range(2))), "shape")
    only(mutate("build", lambda r: r.update(quotes=r["quotes"] * 3)), "shape")


def test_shape_misses_a_missing_sentence_and_the_old_paragraph_result():
    found = only(mutate("build", lambda r: r["tiles"].pop("solution")), "shape")
    assert "tiles.solution" in found
    got = brief_mod.score_brief(_Case(load("build")), _ENTRY, {"whatThisSays": "A paragraph."},
                                outcome="COMPLETED")
    assert got.marks["shape"] is False and got.met is False


def test_a_sharpest_without_a_split_in_the_facts_is_a_shape_miss():
    found = only(mutate("build", lambda r: r.update(
        sharpest={"text": "All of them.", "cites": ["problem.importance"]})), "shape")
    assert "no sharpest sentence" in found


def test_cites_misses_a_foreign_key_a_wrong_vector_no_cite_and_a_thin_infer():
    assert "not a dimension on this project" in only(mutate(
        "build", lambda r: r["headline"].update(cites=["problem.nonsense"])), "cites")
    assert "is not a problem dimension" in only(mutate(
        "build", lambda r: r["tiles"]["problem"].update(cites=["commercial.price"])), "cites")
    only(mutate("build", lambda r: r["tiles"]["problem"].update(cites=[])), "cites")
    assert "at least two problem dimensions" in only(mutate(
        "build", lambda r: r["problem"]["infer"].update(cites=["problem.prevalence"] * 2)), "cites")


def test_cites_misses_a_test_aimed_at_no_target():
    found = only(mutate("build", lambda r: r["next"]["tests"][0].update(
        key="problem.frequency")), "cites")
    assert "not a next-test target" in found


def test_the_headline_and_the_next_sentence_may_cite_any_vector():
    got = mutate("build", lambda r: r["next"]["sentence"].update(
        cites=["solution.compatibility", "problem.prevalence"]))
    assert got.met, got.findings


def test_numbers_misses_an_invented_number_and_a_foreign_currency():
    assert "the number 77 is not in the facts" in only(mutate(
        "build", lambda r: r["tiles"]["problem"].update(text="77 of 12 had a night like it.")),
        "numbers")
    assert "the currency $" in only(mutate(
        "build", lambda r: r["commercial"]["conclusion"].update(text="Start at $5 a month.")),
        "numbers")


def test_numbers_misses_a_digit_or_a_number_word_in_a_test():
    assert "a test carries no number" in only(mutate(
        "build", lambda r: r["next"]["tests"][0].update(text="Ask 5 more people.")), "numbers")
    only(mutate("build", lambda r: r["next"]["tests"][0].update(text="Ask three more people.")),
         "numbers")


def test_a_b2b_reading_is_held_to_its_own_markets_symbol():
    got = mutate("build-but-change-b2b", lambda r: r["commercial"]["conclusion"].update(
        text="Start at £50 a month."))
    assert "the currency £ is not the market's" in only(got, "numbers")


def test_quotes_miss_a_paraphrase_and_a_stranger():
    assert "not a verbatim piece" in only(mutate(
        "build", lambda r: r["quotes"][0].update(text="She cried and I guessed.")), "quotes")
    assert "has no story" in only(mutate(
        "build", lambda r: r["quotes"][0].update(invitationId="someone-else")), "quotes")


@pytest.mark.parametrize("claim", ["They will pay for it.", "It proves the idea.",
                                   "The idea is validated.", "It works.", "See keel.example.com.",
                                   "Ann Abbott said so."])
def test_bans_miss_each_claim_the_brief_forbids(claim):
    got = mutate("build", lambda r: r["solution"]["conclusion"].update(
        text=r["solution"]["conclusion"]["text"] + " " + claim))
    assert only(got, "bans")


def test_an_ordinary_sentence_is_not_a_ban():
    got = mutate("build", lambda r: r["solution"]["conclusion"].update(
        text="They would turn to it first, and it fits where you said."))
    assert got.met, got.findings


# ----------------------------------------------------------------------- failure and the totals

def test_a_needs_input_is_every_mark_missed_on_a_screen_with_nobody_to_ask():
    got = brief_mod.score_brief(_Case(load("build")), _ENTRY, None, outcome="NEEDS_INPUT",
                                needs_input_questions=["which?"])
    assert got.needs_input and got.met is False
    assert set(got.marks.values()) == {False}


def test_a_failed_case_or_no_object_misses_every_mark():
    got = brief_mod.score_brief(_Case(load("build")), _ENTRY, None, outcome="COMPLETED",
                                failed="refused twice")
    assert got.met is False and got.findings["shape"] == "refused twice"


def test_the_marks_are_five_and_the_paragraph_marks_are_gone():
    assert brief_mod.MARK_NAMES == ("shape", "cites", "numbers", "quotes", "bans")
    for retired in ("coverage", "register", "source_material"):
        assert retired not in brief_mod.MARK_NAMES
    assert not hasattr(brief_mod, "verdict_phrasing") and not hasattr(brief_mod, "deciding_line")


def test_the_brief_totals_are_all_five_marks_or_nothing():
    good, bad = score(load("build")), mutate("build", lambda r: r["headline"].update(cites=[]))
    totals = brief_mod.totals([good, bad])
    assert totals["brief_paragraphs"] == 0.5 and totals["brief_cases"] == 2
    assert totals["brief_by_mark"]["cites"] == {"met": 1, "of": 2}
    assert totals["brief_by_mark"]["shape"] == {"met": 2, "of": 2}
    assert brief_mod.totals([])["brief_paragraphs"] is None, "None, never 0"


# ----------------------------------------------------------------- the context built from a corpus

def test_a_context_built_from_the_corpus_scores_a_reading_over_its_own_facts():
    """The corpus-built `facts` are what `check` reads: a reading citing and counting only what
    they carry meets every mark, with no fixture in the way."""
    entry = fx.entry()
    context = context_mod.build_brief(entry)
    facts = context["facts"]
    person = context["stories"][0]
    story = person["story"]
    result = {
        "headline": {"text": "Not yet: the problem is not holding up.",
                     "cites": ["problem.prevalence", "problem.importance"]},
        "tiles": {"problem": {"text": "10 of 12 had a night like it.", "cites": ["problem.prevalence"]},
                  "solution": {"text": "Holding up.", "cites": ["solution.compatibility"]},
                  "commercial": {"text": "Not holding up.", "cites": ["commercial.price"]}},
        "problem": {"conclusion": {"text": "Few would fix it first.", "cites": ["problem.importance"]},
                    "infer": {"text": "10 of 12 had it and 2 of 8 would fix it first.",
                              "cites": ["problem.prevalence", "problem.importance"]}},
        "solution": {"conclusion": {"text": "It fits.", "cites": ["solution.compatibility"]}},
        "commercial": {"conclusion": {"text": "Price is not holding up.",
                                      "cites": ["commercial.price"]}},
        "next": {"sentence": {"text": "Test what matters most.", "cites": ["problem.importance"]},
                 "tests": [{"key": facts["targets"][0]["key"], "text": "Ask what they would fix first."}]},
        "quotes": [{"invitationId": person["invitation_id"], "text": story[:40]}],
    }
    case = types.SimpleNamespace(case_id="09-fixture/BRIEF/run1", run_index=1,
                                 payload={"context": context})
    got = brief_mod.score_brief(case, entry, result, outcome="COMPLETED")
    assert got.met, got.findings
