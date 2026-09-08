"""The `BRIEF` subject: its context, and its four marks (spec 009 follow-on, MARKS_VERSION 4).

Stackless and modelless, like every other `instructions/` test. Two things are guarded here.

**The context is the context production builds** -- `ScreenContextBuilder`'s BRIEF case writes
`project_name`, `market` and `claims`, and the claim/belief field lists are keel-cloud's own order
and keel-cloud's own null rules (an unapproved stage carries no beliefs and a null verdict). Three
fields the corpus cannot evidence are written and left `null` on purpose, and that is asserted
rather than left to be noticed later: `claims[].drift`, `below` and `above`. `median_reads` is the
named deviation -- keel-cloud renders it with `Measure.say`, this repo does not own that
arithmetic, and the number goes over in the corpus's own unit.

**Each mark fails for its own reason and passes for its own reason.** Every one of the four has a
companion case, because a mark that only ever showed its green half is indistinguishable from a
mark that is always green.
"""

from __future__ import annotations

import pytest

from instructions import brief as brief_mod
from instructions import context as context_mod
from instructions import marks as marks_mod
from instructions import score as score_mod
from instructions.corpus import Entry, GoldenBelief

BRIEF_KEYS = ["project_name", "market", "claims"]


def _belief(bid, stage, *, risk="LOAD_BEARING", phrase=None, interval=False, unit="hours"):
    expectation = ({"type": "INTERVAL", "measure": {"kind": "DURATION", "unit": unit,
                                                    "per": "incident"},
                    "lower": {"value": 1}, "upper": {"value": 2}}
                   if interval else
                   {"type": "CHOICE", "options": ["yes", "no"], "expected": "yes"})
    return GoldenBelief(id=bid, stage=stage, heading=f"{bid} heading", statement=f"{bid} says so",
                        founder_phrase=phrase, risk=risk, asked_of="manager", mark="DIRECT",
                        expectation=expectation, selection="S1", group=None)


@pytest.fixture()
def entry():
    return Entry(
        id="09-fixture", title="A fixture",
        market={"country": "GB", "region": None, "language": "en-GB"},
        statements={"problem": "The problem.", "solution": "The solution.",
                    "commercial": "They will pay £40 a month."},
        roles=[], beliefs=[
            _belief("P1", "PROBLEM", risk="SUPPORTING"),
            _belief("P2", "PROBLEM", phrase="one to two hours", interval=True),
            _belief("S1", "SOLUTION"),
            _belief("C1", "COMMERCIAL"),
        ],
        questionnaire={}, answers=[],
        expected={
            "stages": {"PROBLEM": "CONTRADICTED", "SOLUTION": "SUPPORTED",
                       "COMMERCIAL": "MIXED"},
            "standings": {
                "P1": {"verdict": "SUPPORTED", "drift": "none", "inside": 9, "outside": 0,
                       "guessed": 3},
                "P2": {"verdict": "CONTRADICTED", "drift": "below", "inside": 2, "outside": 7,
                       "guessed": 3, "median": 0.75},
                "S1": {"verdict": "SUPPORTED", "drift": "none", "inside": 8, "outside": 1,
                       "guessed": 0},
                "C1": {"verdict": "MIXED", "drift": "none", "inside": 5, "outside": 4,
                       "guessed": 1},
            },
        },
        path=None, sha256="0" * 64)


class _Case:
    """`prompts.Case`'s two fields a mark reads, and nothing else."""

    def __init__(self, entry, context, case_id="09-fixture/BRIEF/run1"):
        self.case_id = case_id
        self.run_index = 1
        self.payload = {"context": context}


@pytest.fixture()
def context(entry):
    return context_mod.build_brief(entry, BRIEF_KEYS)


@pytest.fixture()
def case(entry, context):
    return _Case(entry, context)


# ------------------------------------------------------------------------------------ the context

def test_the_three_keys_arrive_in_the_builders_own_order(context):
    assert list(context) == BRIEF_KEYS
    assert context["project_name"] == "A fixture"
    assert context["market"] == {"country": "GB", "region": None, "language": "en-GB"}


def test_all_three_claims_are_present_in_the_founders_own_order(context):
    assert [c["stage"] for c in context["claims"]] == ["PROBLEM", "SOLUTION", "COMMERCIAL"]
    assert [c["verdict"] for c in context["claims"]] == ["CONTRADICTED", "SUPPORTED", "MIXED"]
    assert all(c["approved"] for c in context["claims"])


def test_a_claims_belief_carries_the_builders_fourteen_fields(context):
    belief = context["claims"][0]["beliefs"][0]
    assert list(belief) == ["heading", "statement", "risk", "mark", "founder_phrase", "verdict",
                            "drift", "median_reads", "inside", "outside", "below", "above",
                            "guessed", "escaped"]
    assert belief["verdict"] == "SUPPORTED" and belief["drift"] == "NONE"
    assert belief["inside"] == 9 and belief["outside"] == 0 and belief["guessed"] == 3


def test_the_three_fields_the_corpus_cannot_evidence_are_written_and_null(context):
    """Written, never omitted -- `build_assumptions`'s own rule, one layer down. Asserted so the
    limit is a fact of the suite rather than a paragraph nobody re-reads."""
    for claim in context["claims"]:
        assert claim["drift"] is None, "Project.driftOfStage is keel-cloud's, not this repo's"
        for belief in claim["beliefs"]:
            assert belief["below"] is None and belief["above"] is None


def test_the_median_goes_over_in_the_corpuss_own_unit_and_not_keel_clouds_phrase(context):
    """The named deviation: keel-cloud's `Measure.say` would round 0.75 hours to *45 minutes*.
    This repo does not own that arithmetic and hands the number as the corpus writes it."""
    beliefs = {b["heading"]: b for b in context["claims"][0]["beliefs"]}
    assert beliefs["P2 heading"]["median_reads"] == "0.75 hours"
    assert beliefs["P1 heading"]["median_reads"] is None, "a CHOICE has no middle to have"


def test_an_unapproved_stage_carries_its_statement_and_no_status(entry):
    entry.expected["stages"].pop("SOLUTION")
    claims = context_mod.build_brief(entry, BRIEF_KEYS)["claims"]
    solution = next(c for c in claims if c["stage"] == "SOLUTION")
    assert solution["approved"] is False
    assert solution["verdict"] is None and solution["drift"] is None
    assert solution["beliefs"] == []
    assert solution["statement"] == "The solution."


# ------------------------------------------------------------------------------ the deciding line

def test_the_deciding_line_is_the_first_load_bearing_line_at_the_stages_own_verdict(context):
    problem = context["claims"][0]
    line = brief_mod.deciding_line(problem)
    assert line["heading"] == "P2 heading", "P1 is SUPPORTING and does not decide anything"


def test_an_unapproved_stage_has_no_deciding_line():
    assert brief_mod.deciding_line({"stage": "SOLUTION", "approved": False}) is None


# ------------------------------------------------------------------------------------- the marks

_GOOD = ("Your problem claim is not holding up: on the line about how long it takes, the middle "
         "answer is 0.75 hours, not the one to two hours you said, and 2 of 9 landed in your "
         "band. Your solution is holding up — 8 of 9 described exactly that. On price the people "
         "you asked disagree, 5 of 9 inside what you expected, so treat that number as untested "
         "until you ask again.")


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
    (_GOOD.replace("Your problem claim", "PROBLEM"), "stage label"),
    ("x" * 1201, "over the contract's 1200"),
    ("   ", "blank"),
])
def test_every_shape_rule_brief_md_states_is_a_miss(case, entry, paragraph, fragment):
    score = _score(case, entry, paragraph)
    assert score.marks["shape"] is False
    assert fragment in score.findings["shape"]


def test_the_design_s_verdict_phrase_is_observed_and_never_marked(case, entry):
    """MARKS_VERSION 5, judgement call 20. The first BRIEF run came back 0 of 7 on a mark that
    required the literal words, against seven paragraphs that were plainly right -- because
    `brief.md`'s own next sentence licenses the paraphrase (*"the problem is real"*). So the
    phrase is recorded per stage and rendered on the register page, and `coverage` does not turn
    on it."""
    paragraph = _GOOD.replace("Your solution is holding up", "Your solution is fine")
    score = _score(case, entry, paragraph)
    assert score.marks["coverage"] is True, score.findings["coverage"]
    observed = {row["stage"]: row for row in score.phrasing}
    assert observed["SOLUTION"]["present"] is False
    assert observed["SOLUTION"]["phrase"] == "holding up"
    assert observed["PROBLEM"]["present"] is True


def test_not_holding_up_is_never_observed_as_holding_up(case, entry):
    """The one ordering that would call every contradicted claim supported: `CONTRADICTED`'s own
    phrase contains `SUPPORTED`'s, so the negative comes out of the paragraph first."""
    paragraph = ("Your problem claim is not holding up: the middle answer is 0.75 hours, not the "
                 "one to two hours you said. Your solution is fine and on price people disagree, "
                 "5 of 9 inside what you expected.")
    observed = {row["stage"]: row for row in
                brief_mod.verdict_phrasing(paragraph, case.payload["context"]["claims"])}
    assert observed["PROBLEM"]["present"] is True
    assert observed["SOLUTION"]["present"] is False, "not holding up is not holding up"
    assert observed["COMMERCIAL"]["present"] is True


def test_an_unapproved_stage_is_observed_as_having_no_status_to_name(entry, context):
    entry.expected["stages"].pop("SOLUTION")
    claims = context_mod.build_brief(entry, BRIEF_KEYS)["claims"]
    observed = {row["stage"]: row for row in brief_mod.verdict_phrasing(_GOOD, claims)}
    assert observed["SOLUTION"] == {"stage": "SOLUTION", "verdict": None, "phrase": None,
                                     "present": None}


def test_a_converted_median_misses_coverage(case, entry):
    """brief.md: *not forty-five minutes, not 0.75 hours, not about three quarters of an hour* --
    the paragraph quotes what it was handed, and a model that converts has broken the rule this
    subject can check hardest."""
    score = _score(case, entry, _GOOD.replace("0.75 hours", "45 minutes"))
    assert score.marks["coverage"] is False
    assert "does not quote it" in score.findings["coverage"]


def test_a_deciding_line_whose_founder_phrase_is_missing_misses_coverage(case, entry):
    score = _score(case, entry, _GOOD.replace(", not the one to two hours you said", ""))
    assert score.marks["coverage"] is False
    assert "does not carry it" in score.findings["coverage"]


def test_an_invented_count_misses_coverage(case, entry):
    """*No number you were not given*: every `N of M` must be some line's inside of
    inside + outside."""
    score = _score(case, entry, _GOOD.replace("8 of 9", "3 of 9"))
    assert score.marks["coverage"] is False
    assert "is no line's inside" in score.findings["coverage"]


def test_a_count_written_in_words_is_read_as_the_same_count(case, entry):
    score = _score(case, entry, _GOOD.replace("8 of 9", "eight of the nine"))
    assert score.marks["coverage"] is True, score.findings["coverage"]


def test_a_split_may_be_counted_from_either_side(case, entry):
    """MARKS_VERSION 5, judgement call 21. `brief.md`'s third thing a paragraph says is *who the
    split is between*, named by the answers people gave -- so `outside` of `inside + outside` is
    a count the standings contain as much as `inside` is. `02-compliancelog` was marked down for
    exactly this on the first run."""
    score = _score(case, entry, _GOOD.replace("5 of 9 inside what you expected",
                                              "4 of 9 said the other thing"))
    assert score.marks["coverage"] is True, score.findings["coverage"]


def test_a_paragraph_with_no_second_person_misses_register(case, entry):
    paragraph = _GOOD.replace("Your", "The").replace("you said", "was claimed") \
                     .replace("you asked", "they asked").replace("you expected", "was expected") \
                     .replace("your band", "the band").replace("you ask", "they ask")
    score = _score(case, entry, paragraph)
    assert score.marks["register"] is False
    assert "no second person" in score.findings["register"]


def test_money_the_context_never_carried_misses_register(case, entry):
    score = _score(case, entry, _GOOD + " They pay about $40 a month.")
    assert score.marks["register"] is False
    assert "$" in score.findings["register"]


def test_the_markets_own_money_is_fine(case, entry):
    """`£` is in this entry's own commercial statement, so a paragraph may carry it."""
    score = _score(case, entry, _GOOD + " They pay about £40 a month.")
    assert score.marks["register"] is True, score.findings["register"]


@pytest.mark.parametrize("tail,fragment", [
    (" Line P2 is the one to watch.", "belief id"),
    (" The median_reads value settles it.", "context field name"),
    (" Their founderPhrase settles it.", "context field name"),
    (" That line is CONTRADICTED.", "enum name"),
    (" It is a proxy for the real thing.", "the word 'proxy'"),
])
def test_reproducing_the_source_material_misses_that_mark(case, entry, tail, fragment):
    score = _score(case, entry, _GOOD + tail)
    assert score.marks["source_material"] is False
    assert fragment in score.findings["source_material"]


@pytest.mark.parametrize("word", ["inside", "outside", "guessed", "escaped", "claims", "beliefs",
                                   "statement", "heading", "risk", "verdict", "drift"])
def test_the_ordinary_english_field_names_are_exempt(case, entry, word):
    """`evals/policy.py`'s judgement calls 1, 5 and 10, one eval over: `brief.md` itself says
    *how many people landed **inside** the founder's own band*, so sweeping these would flag the
    paragraph the instruction asks for rather than a leak."""
    score = _score(case, entry, _GOOD + f" The {word} of it is plain enough.")
    assert score.marks["source_material"] is True, score.findings["source_material"]


def test_a_needs_input_is_a_failed_case_and_never_an_ask(case, entry):
    """brief.md: *there is nobody to ask, so there is no NEEDS_INPUT on this screen*. It is the
    order-following rule's other half and it fails every mark, not just its own."""
    score = brief_mod.score_brief(case, entry, None, outcome="NEEDS_INPUT",
                                  needs_input_questions=[{"id": "q1", "question": "Which one?"}])
    assert score.needs_input is True
    assert score.met is False
    assert all(v is False for v in score.marks.values())
    assert "COMPLETED" in score.findings["source_material"]


def test_a_result_carrying_no_paragraph_fails_rather_than_scoring_nothing(case, entry):
    score = brief_mod.score_brief(case, entry, {"somethingElse": "x"}, outcome="COMPLETED")
    assert score.met is False
    assert "no whatThisSays" in score.findings["shape"]


# ------------------------------------------------------------------------------------- the totals

def test_the_marks_version_is_five_and_the_marks_file_carries_the_new_number():
    assert marks_mod.MARKS_VERSION == 5
    assert marks_mod.load()["brief_paragraphs"] == 1.00


def test_an_unmeasured_brief_mark_is_not_a_met_mark():
    """Judgement call 13, applied to the fourth mark: a run filtered to one subject reports the
    others as unmeasured and fails, which is why a filtered run's verdict is never a pass."""
    totals = score_mod.totals([], [], refusals_measured=True)
    judged = marks_mod.judge(totals, marks_mod.load())
    assert judged["brief_paragraphs"]["measured"] is False
    assert judged["brief_paragraphs"]["met"] is False
    assert judged["passed"] is False


def test_the_brief_totals_are_all_four_marks_or_nothing(case, entry):
    """Judgement call 16: a paragraph that is the right shape and names no verdict has not
    half-worked, so the fraction counts whole paragraphs and never averages the four marks."""
    good = _score(case, entry, _GOOD)
    half = _score(case, entry, _GOOD.replace("8 of 9", "3 of 9"))
    totals = score_mod.totals([], [], brief_scores=[good, half])
    assert totals["brief_cases"] == 2
    assert totals["brief_paragraphs"] == 0.5
    assert totals["brief_by_mark"]["shape"] == {"met": 2, "of": 2}
    assert totals["brief_by_mark"]["coverage"] == {"met": 1, "of": 2}
    assert totals["brief_measured"] is True
