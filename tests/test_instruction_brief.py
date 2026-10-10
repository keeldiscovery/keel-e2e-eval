"""The `BRIEF` subject at `MARKS_VERSION` 12: its context, and its four marks (spec 029 FR-019,
marks-v9 §2.6; T046; spec 030 T010 -- `no_claim_words` retired, judgement call 48; spec 031 T010 --
the two commercial figures keel-cloud's own, judgement call 57; spec 032 T008 -- per the founder's period,
the time-only apart and Ability to pay's figure, judgement call 64).

Stackless and modelless. The context is three vectors with every dimension's standing under them,
one case a project (FR-019). **Each mark fails for its own reason and passes for its own reason**:
every one of the four has a companion case, because a mark that only ever showed its green half is
indistinguishable from a mark that is always green. The entry is the hand-sized
`tests/fixtures/corpus/09-fixture-r6.yaml`, whose standings a person can read off the file.
"""

from __future__ import annotations

import pytest

from instructions import brief as brief_mod
from instructions import context as context_mod
from instructions import corpus as corpus_mod
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
    assert lines["PROBLEM"]["key"] == "problem.importance"
    assert lines["SOLUTION"]["key"] == "solution.compatibility"
    assert lines["COMMERCIAL"]["key"] == "commercial.existing_sacrifice"
    assert lines["COMMERCIAL"]["observed"] == "a median £12 a month"     # calls 57, 64


def test_a_vector_naming_no_deciding_dimension_has_no_deciding_line():
    assert brief_mod.deciding_line({"vector": "PROBLEM", "dimensions": []}) is None


# ------------------------------------------------------------------------------------- the marks

_GOOD = ("Your problem is not holding up on how much it matters: 6 of 8 put it lower than you "
         "did. On your solution, 6 of 8 would reach for it once the first look has failed, as you "
         "said. On price the people you asked are not giving up what you hoped: you said about "
         "£20 to £60 a month, and they already spend a median £12 a month, with only 2 "
         "of 8 buying spare keys.")


def _score(case, entry, paragraph, **kw):
    return brief_mod.score_brief(case, entry, {"whatThisSays": paragraph}, outcome="COMPLETED",
                                 **kw)


def test_a_good_paragraph_meets_all_four_marks(case, entry):
    score = _score(case, entry, _GOOD)
    assert score.marks == {"shape": True, "coverage": True, "register": True,
                           "source_material": True}, score.findings
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
    score = _score(case, entry, _GOOD.replace("a median £12 a month",
                                              "twelve pounds a quarter"))
    assert score.marks["coverage"] is False
    assert "a median £12 a month" in score.findings["coverage"]


def test_a_deciding_line_whose_founder_phrase_is_missing_misses_coverage(case, entry):
    score = _score(case, entry, _GOOD.replace("you said about £20 to £60 a month, and ", ""))
    assert score.marks["coverage"] is False
    assert "about £20 to £60 a month" in score.findings["coverage"]


def test_an_invented_count_misses_coverage(case, entry):
    score = _score(case, entry, _GOOD.replace("2 of 8", "2 of 9"))
    assert score.marks["coverage"] is False
    assert "2 of 9" in score.findings["coverage"]


def test_a_count_written_in_words_is_read_as_the_same_count(case, entry):
    assert _score(case, entry, _GOOD.replace("2 of 8", "two of eight")).marks["coverage"] is True


def test_a_split_may_be_counted_from_either_side(case, entry):
    assert _score(case, entry, _GOOD.replace("6 of 8 put it lower than you did",
                                             "2 of 8 put it where you did")).marks["coverage"] is True


def test_an_option_count_row_is_a_count_the_standings_carry(case, entry):
    """marks §2.6: every `optionCounts` row of `n` -- a set dimension's standing *is* its counts."""
    score = _score(case, entry, _GOOD + " And 5 of 8 of you gave up none of these.")
    assert score.marks["coverage"] is True, score.findings["coverage"]


def test_a_paragraph_with_no_second_person_misses_register(case, entry):
    paragraph = ("The problem is not holding up: the founder said about £20 to £60 a month and the "
                 "median was a median £12 a month.")
    assert _score(case, entry, paragraph).marks["register"] is False


def test_money_the_context_never_carried_misses_register(case, entry):
    score = _score(case, entry, _GOOD + " They pay about $40 a month.")
    assert score.marks["register"] is False


def test_the_markets_own_money_is_fine(case, entry):
    """`£` is in this entry's own price belief sentence, so a paragraph may carry it."""
    score = _score(case, entry, _GOOD + " You hoped for about £3 a month.")
    assert score.marks["register"] is True, score.findings["register"]


@pytest.mark.parametrize("tail,fragment", [
    (" The problem.frequency line is the one to watch.", "dimension key"),
    (" Its belief_sentence settles it.", "context field name"),
    (" That line is NOT_HOLDING_UP.", "enum name"),
    (" Importance is a DEAL_BREAKER.", "enum name"),
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


# ------------------------------------------------------- call 48: no_claim_words retired at v10

def test_the_marks_are_four_and_no_claim_words_is_gone_with_its_two_statuses():
    """Call 48: BAR_SET and NOT_TESTED_BY_DESIGN left the registry (keel-cloud 071), and the mark
    that scored the sentences naming them went with them."""
    assert brief_mod.MARK_NAMES == ("shape", "coverage", "register", "source_material")
    for retired in ("no_claim_words", "claim_scoped_names", "CLAIM_SCOPED_STATUSES"):
        assert not hasattr(brief_mod, retired), retired
    assert not {"BAR_SET", "NOT_TESTED_BY_DESIGN"} & set(brief_mod.ENUM_NAMES)
    assert not {"BAR_SET", "NOT_TESTED_BY_DESIGN"} & set(brief_mod.VERDICT_MARKERS)
    assert set(brief_mod.VERDICT_MARKERS) == set(corpus_mod.STATUSES)


def test_a_claim_word_is_no_mark_of_its_own_any_more(case, entry):
    score = _score(case, entry, _GOOD + " Your solution works.")
    assert set(score.marks) == set(brief_mod.MARK_NAMES) and score.met is True, score.findings


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


def test_the_brief_totals_are_all_four_marks_or_nothing(case, entry):
    good = _score(case, entry, _GOOD)
    keyed = _score(case, entry, _GOOD + " The problem.importance line decides it.")
    totals = score_mod.totals(brief_scores=[good, keyed])
    assert totals["brief_cases"] == 2 and totals["brief_paragraphs"] == 0.5
    assert totals["brief_by_mark"]["shape"] == {"met": 2, "of": 2}
    assert totals["brief_by_mark"]["source_material"] == {"met": 1, "of": 2}
    assert set(totals["brief_by_mark"]) == set(brief_mod.MARK_NAMES)


def test_one_brief_case_an_entry_never_one_a_vector(tmp_path, entry):
    cases = prompts_mod.build_cases(entry, fx.exported(tmp_path), fx.instructions(),
                                    fx.FakeRuntime, n_runs=1)
    assert [c.case_id for c in cases if c.kind == "BRIEF"] == ["09-fixture/BRIEF/run1"]


# ---------------------------- call 57 (call 42 superseded): the two commercial figures, keel-cloud's

class _Entry:
    """What `cost_figure` / `price_figure` / `ability_figure` read: the market, the founder's cost and price,
    and the people (none here unless given)."""

    def __init__(self, market="GB", price=None, cost=None, people=(), b2b=False):
        self.market = {"country": market}
        self.founder_calibration = {}
        if price:
            self.founder_calibration["commercial.price"] = {"answer": price}
        self._cost = cost
        self._people = list(people)
        self._b2b = b2b

    def cost(self):
        return self._cost

    def b2b(self):
        return self._b2b

    def gate_yes(self):
        return self._people


_SET_STANDING = {"status": "NOT_HOLDING_UP", "n": 8, "median": 165,
                 "optionCounts": "staff_hours=4, write_offs=4, nothing=0"}
_MONTH = {"mode": "AMOUNT", "low": 10, "high": 30, "period": "month", "currency": "GBP"}


def _person(price, hours=None, money=None, period="quarter", anchoring="ANCHORED"):
    amounts = ([{"kind": "time", "value": hours, "unit": "hours"}] if hours is not None else []) + \
        ([{"kind": "spend", "value": money, "unit": "money"}] if money is not None else [])
    return corpus_mod.Person(person="p", recency="yes", story="s", chip=None, anchoring=anchoring,
                             picks={"commercial.existing_sacrifice": {"currency": "GBP",
                                                                      "period": period,
                                                                      "amounts": amounts},
                                    "commercial.price": price})


def test_existing_sacrifices_figure_is_figures_cost_per_the_founders_period():
    """`Figures.cost` (keel-cloud 074): a median in the market's currency, rounded half up, over the
    founder's period; over three months where the cost was left out."""
    key = "commercial.existing_sacrifice"
    assert context_mod.observed_of(_Entry(cost=_MONTH), key, _SET_STANDING) == "a median £165 a month"
    assert context_mod.observed_of(_Entry(), key, _SET_STANDING) == "a median £165 over three months"
    assert context_mod.observed_of(_Entry("US", cost=dict(_MONTH, period="year", currency="USD")), key,
                                   dict(_SET_STANDING, median=27.5)) == "a median $27.50 a year"
    assert context_mod.observed_of(_Entry(), key, dict(_SET_STANDING, median=None)) is None


def test_the_people_who_gave_only_time_are_reported_apart_with_what_an_hour_is_worth():
    """Founder decision 1 (keel-cloud 074 D-12), `Figures.timeOnly`: three managers who lose 30, 45 and 60 hours
    a quarter (10, 15, 20 a month: median 15), bands £20 to £50 / £20 to £50 / £50 to £100 -- the lower
    middle, £20 to £50 over 15 hours is £1.33 to £3.33 an hour."""
    people = [_person("band_20_50", hours=30), _person("band_20_50", hours=45),
              _person("band_50_100", hours=60)]
    figure = context_mod.observed_of(_Entry(cost=_MONTH, people=people),
                                     "commercial.existing_sacrifice", _SET_STANDING)
    assert figure == ("a median £165 a month; 3 lose only time: median 15 hours a month, valued getting "
                      "them back at £20 to £50 a month, about £1.33 to £3.33 an hour")
    one = context_mod.observed_of(_Entry(cost=_MONTH, people=[_person("would_not_pay", hours=30)]),
                                  "commercial.existing_sacrifice", dict(_SET_STANDING, median=None))
    assert one == "1 loses only time: median 10 hours a month, and would not pay to get them back"
    guessed = _Entry(cost=_MONTH, people=[_person("band_20_50", hours=30, anchoring="GUESSED")])
    assert context_mod.observed_of(guessed, "commercial.existing_sacrifice", _SET_STANDING) == \
        "a median £165 a month", "an unanchored person is never counted apart"
    spender = _Entry(cost=_MONTH, people=[_person("band_20_50", hours=30, money=40)])
    assert context_mod.observed_of(spender, "commercial.existing_sacrifice", _SET_STANDING) == \
        "a median £165 a month", "someone who gave money and time is counted on the money"
    b2b = _Entry(cost=_MONTH, people=people, b2b=True)
    assert context_mod.observed_of(b2b, "commercial.existing_sacrifice", _SET_STANDING) == \
        "a median £165 a month", "B2B prices hours at the rate: nobody is apart"


def test_a_sacrifice_with_no_median_and_nobody_apart_has_no_figure():
    assert context_mod.observed_of(_Entry(), "commercial.existing_sacrifice",
                                   dict(_SET_STANDING, median=None)) is None


def test_prices_figure_is_figures_price_at_the_founders_floor():
    """`Figures.price`: inside of n, the founder's band's floor (the ladder point at or below the
    low), the period in words; none where Price was left out or nobody counted."""
    standing = {"status": "PEOPLE_DISAGREE", "n": 8, "inside": 5, "outside": 3}
    lullaby = _Entry(price={"low": 5, "high": 12, "period": "month", "currency": "GBP"})
    assert context_mod.observed_of(lullaby, "commercial.price", standing) == \
        "5 of 8 said it would be worth £5 a month or more"
    linerly = _Entry(price={"low": 30, "high": 45, "period": "year", "currency": "GBP"})
    assert context_mod.observed_of(linerly, "commercial.price", standing) == \
        "5 of 8 said it would be worth £20 a year or more"
    assert context_mod.observed_of(_Entry(), "commercial.price", standing) is None


def test_ability_to_pays_figure_is_figures_ability_at_the_founders_price_low():
    """`Figures.ability` (keel-cloud 074): *{inside} of {n} already spend {price low} {period} or more*."""
    standing = {"status": "HOLDING_UP", "n": 8, "inside": 7, "outside": 1}
    entry = _Entry(price={"low": 5, "high": 12, "period": "month", "currency": "GBP"})
    assert context_mod.observed_of(entry, "commercial.ability_to_pay", standing) == \
        "7 of 8 already spend £5 a month or more"
    assert context_mod.observed_of(_Entry(), "commercial.ability_to_pay", standing) is None
    assert context_mod.observed_of(entry, "commercial.ability_to_pay",
                                   {"status": "LEFT_OUT"}) is None


def _set_vector(observed, verdict="NOT_HOLDING_UP"):
    return [{"vector": "COMMERCIAL", "verdict": verdict, "deciding": "commercial.existing_sacrifice",
             "dimensions": [{"key": "commercial.existing_sacrifice", "name": "Existing sacrifice",
                             "founder_phrase": "staff hours and written-off stock",
                             "observed": observed, "inside": None, "outside": None,
                             "n_anchored": 8,
                             "option_counts": "staff_hours=4, write_offs=4, nothing=0"}]}]


def test_coverage_asks_a_money_set_for_its_figure_in_the_founders_unit():
    vectors = _set_vector("a median £165 over three months")
    said = ("You said staff hours and written-off stock; the middle of what they already give up "
            "is a median £165 over three months.")
    assert brief_mod._coverage(said, vectors)[0] is True
    met, finding = brief_mod._coverage(said.replace("a median £165 over three months", "165"), vectors)
    assert met is False and "a median £165 over three months" in finding


def test_coverage_asks_a_set_with_no_figure_for_one_of_its_option_counts():
    vectors = _set_vector(None, verdict="PEOPLE_DISAGREE")
    assert brief_mod._coverage("People disagree: 4 of 8 give up staff hours.", vectors)[0] is True
    met, finding = brief_mod._coverage("People disagree on what they give up.", vectors)
    assert met is False and "option counts" in finding


def test_the_founders_phrase_is_asked_for_only_on_a_bet_that_is_not_holding_up():
    """brief.md, "The four things", 2: `founder_phrase` against `observed` on a NOT_HOLDING_UP bet."""
    paragraph = "They already give up a median £165 over three months, split 4 of 8 and 4 of 8."
    assert brief_mod._coverage(paragraph, _set_vector("a median £165 over three months",
                                                      verdict="HOLDING_UP"))[0] is True
    met, finding = brief_mod._coverage(paragraph, _set_vector("a median £165 over three months"))
    assert met is False and "staff hours and written-off stock" in finding
