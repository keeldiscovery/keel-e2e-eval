"""The `BRIEF` subject at `MARKS_VERSION` 9: its context, and its five marks (spec 029 FR-019,
marks-v9 §2.6, judgement call 35; T046).

Stackless and modelless. The context is three vectors with every dimension's standing under them,
one case a project (FR-019). **Each mark fails for its own reason and passes for its own reason**:
every one of the five has a companion case, because a mark that only ever showed its green half is
indistinguishable from a mark that is always green. The entry is the hand-sized
`tests/fixtures/corpus/09-fixture-r3.yaml`, whose standings a person can read off the file.
"""

from __future__ import annotations

import pytest

from instructions import brief as brief_mod
from instructions import context as context_mod
from instructions import marks as marks_mod
from instructions import prompts as prompts_mod
from instructions import score as score_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def entry():
    return fx.entry()


class _Case:
    """`prompts.Case`'s fields a mark reads, and nothing else."""

    def __init__(self, context, case_id="09-fixture/BRIEF/run1"):
        self.case_id = case_id
        self.run_index = 1
        self.payload = {"context": context}


@pytest.fixture()
def context(entry):
    return context_mod.build_brief(entry)


@pytest.fixture()
def case(context):
    return _Case(context)


# ------------------------------------------------------------------------------ the deciding line

def test_the_deciding_line_is_the_vectors_worst_deal_breaker_from_vector_verdicts(context):
    lines = {v["vector"]: brief_mod.deciding_line(v) for v in context["vectors"]}
    assert lines["PROBLEM"]["key"] == "problem.duration"
    assert lines["SOLUTION"]["key"] == "solution.effectiveness_threshold"
    assert lines["COMMERCIAL"]["key"] == "commercial.commitment"


def test_a_vector_naming_no_deciding_dimension_has_no_deciding_line():
    assert brief_mod.deciding_line({"vector": "PROBLEM", "dimensions": []}) is None


# ------------------------------------------------------------------------------------- the marks

_GOOD = ("Your problem is not holding up on how long it takes: you said 5 to 15 minutes, the "
         "middle answer was 8 minutes, and 5 of 7 came in under your range. On your solution "
         "the bar is set higher than yours, so it has to save more than you thought before it is "
         "worth the trouble. On price the people you asked are not ready: only 2 of 8 would go "
         "as far as you hoped.")


def _score(case, entry, paragraph, **kw):
    return brief_mod.score_brief(case, entry, {"whatThisSays": paragraph}, outcome="COMPLETED",
                                 **kw)


def test_a_good_paragraph_meets_all_five_marks(case, entry):
    score = _score(case, entry, _GOOD)
    assert score.marks == {"shape": True, "coverage": True, "register": True,
                           "source_material": True, "no_claim_words": True}, score.findings
    assert score.met is True


@pytest.mark.parametrize("paragraph,fragment", [
    (_GOOD + "\n\nAnd another thing.", "line break"),
    ("• " + _GOOD, "bullet glyph"),
    ("# Heading. " + _GOOD, "list or heading marker"),
    (_GOOD + " See https://keel.example for more.", "web address"),
    (_GOOD.replace("Your problem", "PROBLEM"), "vector label"),
    ("x" * 2001, "over the contract's 2000"),
    ("   ", "blank"),
])
def test_every_shape_rule_brief_md_states_is_a_miss(case, entry, paragraph, fragment):
    score = _score(case, entry, paragraph)
    assert score.marks["shape"] is False
    assert fragment in score.findings["shape"]


def test_the_designs_verdict_phrase_is_observed_and_never_marked(case, entry):
    score = _score(case, entry, _GOOD.replace("is not holding up", "falls apart"))
    assert score.marks["coverage"] is True
    problem = next(p for p in score.phrasing if p["vector"] == "PROBLEM")
    assert problem["verdict"] == "NOT_HOLDING_UP" and problem["present"] is False


def test_not_holding_up_is_never_observed_as_holding_up(case, entry):
    phrasing = brief_mod.verdict_phrasing("It is not holding up.",
                                          [{"vector": "SOLUTION", "verdict": "HOLDING_UP"}])
    assert phrasing[0]["present"] is False


def test_a_converted_median_misses_coverage(case, entry):
    score = _score(case, entry, _GOOD.replace("8 minutes", "eight minutes"))
    assert score.marks["coverage"] is False
    assert "8 minutes" in score.findings["coverage"]


def test_a_deciding_line_whose_founder_phrase_is_missing_misses_coverage(case, entry):
    score = _score(case, entry, _GOOD.replace("you said 5 to 15 minutes, ", ""))
    assert score.marks["coverage"] is False
    assert "5 to 15 minutes" in score.findings["coverage"]


def test_an_invented_count_misses_coverage(case, entry):
    score = _score(case, entry, _GOOD.replace("2 of 8", "2 of 9"))
    assert score.marks["coverage"] is False
    assert "2 of 9" in score.findings["coverage"]


def test_a_count_written_in_words_is_read_as_the_same_count(case, entry):
    assert _score(case, entry, _GOOD.replace("2 of 8", "two of eight")).marks["coverage"] is True


def test_a_split_may_be_counted_from_either_side(case, entry):
    assert _score(case, entry, _GOOD.replace("5 of 7 came in under",
                                             "2 of 7 came in inside")).marks["coverage"] is True


def test_an_option_count_row_is_a_count_the_standings_carry(case, entry):
    """marks §2.6: every `optionCounts` row of `n` -- a set dimension's standing *is* its counts."""
    score = _score(case, entry, _GOOD + " Cancelling worried 5 of 8 of you.")
    assert score.marks["coverage"] is True, score.findings["coverage"]


def test_a_paragraph_with_no_second_person_misses_register(case, entry):
    paragraph = ("The problem is not holding up: the founder said 5 to 15 minutes and the middle "
                 "answer was 8 minutes.")
    assert _score(case, entry, paragraph).marks["register"] is False


def test_money_the_context_never_carried_misses_register(case, entry):
    score = _score(case, entry, _GOOD + " They pay about $40 a month.")
    assert score.marks["register"] is False


def test_the_markets_own_money_is_fine(case, entry):
    """`£` is in this entry's own price belief sentence, so a paragraph may carry it."""
    score = _score(case, entry, _GOOD + " You hoped for about £3 a month.")
    assert score.marks["register"] is True, score.findings["register"]


@pytest.mark.parametrize("tail,fragment", [
    (" The problem.duration line is the one to watch.", "dimension key"),
    (" Its belief_sentence settles it.", "context field name"),
    (" That line is NOT_HOLDING_UP.", "enum name"),
    (" Duration is a DEAL_BREAKER.", "enum name"),
    (" It is a proxy for the real thing.", "the word 'proxy'"),
])
def test_reproducing_the_source_material_misses_that_mark(case, entry, tail, fragment):
    score = _score(case, entry, _GOOD + tail)
    assert score.marks["source_material"] is False
    assert fragment in score.findings["source_material"]


@pytest.mark.parametrize("word", ["inside", "outside", "guessed", "verdict", "drift", "holding"])
def test_the_ordinary_english_words_are_exempt(case, entry, word):
    score = _score(case, entry, _GOOD + f" The {word} of it is plain enough.")
    assert score.marks["source_material"] is True, score.findings["source_material"]


# ------------------------------------------------------------- call 35: the fifth per-case mark

@pytest.mark.parametrize("sentence", [
    "Your effectiveness threshold works.", "On price, £3 a month is proven.",
    "The effectiveness threshold will save you time.", "Price is confirmed by what they paid.",
])
def test_a_claim_word_beside_a_threshold_or_the_price_misses_no_claim_words(case, entry, sentence):
    score = _score(case, entry, _GOOD + " " + sentence)
    assert score.marks["no_claim_words"] is False
    assert score.findings["no_claim_words"].startswith("the sentence naming")


def test_the_same_word_beside_another_dimension_is_that_sentences_business(case, entry):
    score = _score(case, entry, _GOOD + " Your frequency works out much as you said.")
    assert score.marks["no_claim_words"] is True, score.findings["no_claim_words"]


def test_a_needs_input_is_a_failed_case_and_never_an_ask(case, entry):
    score = brief_mod.score_brief(case, entry, None, outcome="NEEDS_INPUT",
                                  needs_input_questions=[{"id": "q1", "question": "Which one?"}])
    assert score.needs_input is True and score.met is False
    assert set(score.marks) == set(brief_mod.MARK_NAMES)
    assert all(v is False for v in score.marks.values())


def test_a_result_carrying_no_paragraph_fails_rather_than_scoring_nothing(case, entry):
    score = brief_mod.score_brief(case, entry, {"somethingElse": "x"}, outcome="COMPLETED")
    assert score.met is False
    assert "no whatThisSays" in score.findings["shape"]


# ------------------------------------------------------------------------------------- the totals

def test_the_brief_number_has_not_moved():
    assert marks_mod.load()["brief_paragraphs"] == 1.00


def test_an_unmeasured_brief_mark_is_not_a_met_mark():
    totals = score_mod.totals(refusals_measured=True)
    judged = marks_mod.judge(totals, marks_mod.load())
    assert judged["brief_paragraphs"]["measured"] is False
    assert judged["brief_paragraphs"]["met"] is False and judged["passed"] is False


def test_the_brief_totals_are_all_five_marks_or_nothing(case, entry):
    good = _score(case, entry, _GOOD)
    claim = _score(case, entry, _GOOD + " Your effectiveness threshold works.")
    totals = score_mod.totals(brief_scores=[good, claim])
    assert totals["brief_cases"] == 2 and totals["brief_paragraphs"] == 0.5
    assert totals["brief_by_mark"]["shape"] == {"met": 2, "of": 2}
    assert totals["brief_by_mark"]["no_claim_words"] == {"met": 1, "of": 2}


def test_one_brief_case_an_entry_never_one_a_vector(tmp_path, entry):
    cases = prompts_mod.build_cases(entry, fx.exported(tmp_path), fx.instructions(),
                                    fx.FakeRuntime, n_runs=1)
    assert [c.case_id for c in cases if c.kind == "BRIEF"] == ["09-fixture/BRIEF/run1"]


# ------------------------------------------- call 42: a money set's observed figure, and its counts

class _Person:
    def __init__(self, picks):
        self.picks = picks


class _Entry:
    def __init__(self, costs, market="GB", answer=("staff_hours", "write_offs")):
        self.market = {"country": market}
        self.founder_calibration = {"commercial.existing_sacrifice": {"answer": list(answer)}}
        self._people = [_Person({"commercial.existing_sacrifice": {"bought": "staff_hours",
                                                                   "cost": c}}) for c in costs]

    def people(self):
        return self._people


_SET_STANDING = {"status": "NOT_HOLDING_UP", "n": 8, "median": 165,
                 "optionCounts": "staff_hours=4, write_offs=4, nothing=0"}


def test_a_money_sets_median_is_written_in_the_founders_unit():
    entry = _Entry([{"value": 150, "currency": "GBP", "per": "three_months"}] * 3)
    assert context_mod.observed_of(entry, "commercial.existing_sacrifice", _SET_STANDING) \
        == "£165 per three months"
    dollars = _Entry([{"value": 300, "currency": "USD", "per": "three_months"}], market="US")
    assert context_mod.observed_of(dollars, "commercial.existing_sacrifice",
                                   dict(_SET_STANDING, median=27.5)) == "$27.5 per three months"


def test_the_standings_own_currency_and_period_come_first_and_the_market_fills_a_gap():
    entry = _Entry([{"value": 150, "per": "three_months"}])
    assert context_mod.observed_of(entry, "commercial.existing_sacrifice", _SET_STANDING) \
        == "£165 per three months", "no currency on the answers: the market's"
    standing = dict(_SET_STANDING, currency="EUR", per="month")
    assert context_mod.observed_of(entry, "commercial.existing_sacrifice", standing) \
        == "€165 per month"


def test_a_set_whose_money_cannot_be_written_has_no_figure():
    mixed = _Entry([{"value": 1, "currency": "GBP", "per": "month"},
                    {"value": 2, "currency": "GBP", "per": "year"}])
    assert context_mod.observed_of(mixed, "commercial.existing_sacrifice", _SET_STANDING) is None


def _set_vector(observed, verdict="NOT_HOLDING_UP"):
    return [{"vector": "COMMERCIAL", "verdict": verdict, "deciding": "commercial.existing_sacrifice",
             "dimensions": [{"key": "commercial.existing_sacrifice", "name": "Existing sacrifice",
                             "founder_phrase": "staff hours and written-off stock",
                             "observed": observed, "inside": None, "outside": None,
                             "n_anchored": 8,
                             "option_counts": "staff_hours=4, write_offs=4, nothing=0"}]}]


def test_coverage_asks_a_money_set_for_its_figure_in_the_founders_unit():
    vectors = _set_vector("£165 per three months")
    said = ("You said staff hours and written-off stock; the middle of what they already give up "
            "is £165 per three months.")
    assert brief_mod._coverage(said, vectors)[0] is True
    met, finding = brief_mod._coverage(said.replace("£165 per three months", "165"), vectors)
    assert met is False and "£165 per three months" in finding


def test_coverage_asks_a_set_with_no_figure_for_one_of_its_option_counts():
    vectors = _set_vector(None, verdict="PEOPLE_DISAGREE")
    assert brief_mod._coverage("People disagree: 4 of 8 give up staff hours.", vectors)[0] is True
    met, finding = brief_mod._coverage("People disagree on what they give up.", vectors)
    assert met is False and "option counts" in finding


def test_the_founders_phrase_is_asked_for_only_on_a_bet_that_is_not_holding_up():
    """brief.md, "The four things", 2: `founder_phrase` against `observed` on a NOT_HOLDING_UP bet."""
    paragraph = "They already give up £165 per three months, split 4 of 8 and 4 of 8."
    assert brief_mod._coverage(paragraph, _set_vector("£165 per three months",
                                                      verdict="HOLDING_UP"))[0] is True
    met, finding = brief_mod._coverage(paragraph, _set_vector("£165 per three months"))
    assert met is False and "staff hours and written-off stock" in finding
