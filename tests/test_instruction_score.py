"""`instructions/score.py`: the arithmetic, on fixtures a person can check by hand (FR-018).

The test that matters most here is the one about a reader that answers `ANCHORED` to everything.
In this corpus most anchors are anchored, so such a reader scores high on accuracy and has recall
zero on the one judgement the instrument exists to make — which is the whole reason precision and
recall are mandatory beside accuracy rather than optional (judgement call 5).
"""

from __future__ import annotations

from instructions import score as score_mod
from instructions.corpus import Entry, GoldenBelief, Person
from instructions.prompts import Case


READING_ANCHOR_IDS = ("A1", "A2", "A3", "A4", "A9")


def _entry(beliefs=(), *, anchor_ids=READING_ANCHOR_IDS):
    # Every anchor this file's reading fixtures write under, stage-tagged PROBLEM so
    # `score_reading`'s own `entry.anchor(anchor_id)` lookup (measured-beliefs decision 18, DRIFT
    # #37) resolves the same stage the wire's own `result["anchorings"]` entries below carry.
    anchors = [{"id": a, "stage": "PROBLEM"} for a in anchor_ids]
    return Entry(id="09-fixture", title="t", market={}, statements={}, roles=[],
                 beliefs=list(beliefs), questionnaire={"anchors": anchors}, answers=[],
                 expected={}, path=None, sha256="0" * 64)


def _case(kind, subject, run_index=1):
    return Case(case_id=f"09-fixture/{subject}/run{run_index}", kind=kind, entry_id="09-fixture",
                screen="INTERPRET" if kind == "READING" else "PROBLEM_ASSUMPTIONS",
                subject=subject, run_index=run_index, payload={})


def _person(**anchors):
    return Person(person="Priya", picks={},
                  anchors={k: {"text": "something", "anchoring": v} for k, v in anchors.items()})


def _belief(bid, expected="yes"):
    return GoldenBelief(id=bid, stage="PROBLEM", heading=bid, statement=f"{bid}.",
                        founder_phrase=None, risk="LOAD_BEARING", asked_of="manager",
                        mark="DIRECT",
                        expectation={"type": "CHOICE", "options": ["yes", "no"],
                                     "expected": expected},
                        selection=f"S-{bid}", group=None)


# --------------------------------------------------------------------------------------- reading

def test_a_reader_that_says_anchored_to_everything_scores_high_and_recalls_nothing():
    person = _person(A1="ANCHORED", A2="ANCHORED", A3="ANCHORED", A4="GUESSED")
    result = {"anchorings": [{"stage": "PROBLEM", "anchorId": a, "anchoring": "ANCHORED"}
                             for a in ("A1", "A2", "A3", "A4")]}

    score = score_mod.score_reading(_case("READING", "Priya"), _entry(), person, result)
    totals = score_mod.totals([score], [])

    assert score.anchoring_accuracy == 0.75, "three of four right looks respectable"
    assert totals["guessed_recall"] == 0.0, "and it never once spotted a guess"
    assert totals["guessed_precision"] is None, "it called nothing GUESSED, so precision has no "\
        "denominator -- reported as absent, never as 1.0"
    assert totals["confusion"] == {"aa": 3, "ag": 0, "ga": 1, "gg": 0}


def test_a_reader_that_spots_the_guess_has_precision_and_recall_of_one():
    person = _person(A1="ANCHORED", A2="GUESSED")
    result = {"anchorings": [{"stage": "PROBLEM", "anchorId": "A1", "anchoring": "ANCHORED"},
                             {"stage": "PROBLEM", "anchorId": "A2", "anchoring": "GUESSED"}]}

    totals = score_mod.totals(
        [score_mod.score_reading(_case("READING", "Priya"), _entry(), person, result)], [])

    assert totals["anchoring_accuracy"] == 1.0
    assert totals["guessed_precision"] == 1.0
    assert totals["guessed_recall"] == 1.0


def test_an_omitted_anchor_is_recorded_and_never_quietly_matched_by_position():
    person = _person(A1="ANCHORED", A2="GUESSED")
    result = {"anchorings": [{"stage": "PROBLEM", "anchorId": "A9", "anchoring": "ANCHORED"}]}

    score = score_mod.score_reading(_case("READING", "Priya"), _entry(), person, result)

    assert score.given == 2
    assert score.answered == 0, "neither anchor it was given came back"
    assert score.missing_ids == ["A1", "A2"]
    assert score.extra_ids == ["A9"], "an invented id is a finding of its own"
    assert score.anchoring_accuracy is None


def test_a_failed_reading_case_answers_no_anchor_at_all():
    person = _person(A1="ANCHORED")

    score = score_mod.score_reading(_case("READING", "Priya"), _entry(), person, None,
                                    failed="outcome 'X' is not in allowed_outcomes")

    assert score.answered == 0 and score.missing_ids == ["A1"]
    assert score.failed.startswith("outcome")


def test_an_anchoring_with_no_stage_is_refused_the_same_as_an_omitted_one():
    """Measured-beliefs decision 18 / DRIFT #37: `stage` is required on the wire now (the same
    pair the context handed the model), so an anchoring missing it is not a match -- it is treated
    exactly like an omitted anchor, never resolved by the bare id alone."""
    person = _person(A1="ANCHORED")
    result = {"anchorings": [{"anchorId": "A1", "anchoring": "ANCHORED"}]}   # no "stage"

    score = score_mod.score_reading(_case("READING", "Priya"), _entry(), person, result)

    assert score.answered == 0
    assert score.missing_ids == ["A1"]
    assert score.anchoring_accuracy is None


def test_a_stage_that_does_not_match_the_goldens_own_is_not_a_match():
    """Two occasions can share the bare id `A1` on two different stages (a link spanning both) --
    the wrong stage is a wrong answer, not a coincidence to accept."""
    person = _person(A1="ANCHORED")
    result = {"anchorings": [{"stage": "SOLUTION", "anchorId": "A1", "anchoring": "ANCHORED"}]}

    score = score_mod.score_reading(_case("READING", "Priya"), _entry(), person, result)

    assert score.answered == 0
    assert score.missing_ids == ["A1"]
    assert score.extra_ids == ["A1"], "the same id, wrong stage, is an extra -- not a match"


# ----------------------------------------------------------------------------------- assumptions

def test_recall_is_matched_over_the_stages_goldens_and_extras_are_counted_not_marked():
    entry = _entry([_belief("P1", "yes"), _belief("P2", "no")])
    result = {"assumptions": [
        {"heading": "P1", "statement": "P1.", "risk": "LOAD_BEARING", "mark": "DIRECT",
         "expectation": {"type": "CHOICE", "options": ["yes", "no"], "expected": "yes"}},
        {"heading": "invented", "statement": "Something else.", "risk": "SUPPORTING",
         "mark": "DIRECT",
         "expectation": {"type": "INTERVAL", "measure": {"kind": "COUNT", "unit": "things"},
                         "lower": {"value": 1}}}]}

    score = score_mod.score_assumptions(_case("ASSUMPTIONS", "PROBLEM"), entry, result)

    assert score.matched == 1 and score.golden_total == 2
    assert score.golden_belief_recall == 0.5
    assert score.extra_beliefs == 1, "an extra is a count, never a mark"


def test_needs_input_is_a_failed_case_counted_in_the_recall_denominator():
    # Design decision 14: an assumption screen's only legitimate ask is a missing statement, and
    # this harness always supplies one. So an ask is a failure, not an excusable abstention.
    entry = _entry([_belief("P1"), _belief("P2")])

    score = score_mod.score_assumptions(
        _case("ASSUMPTIONS", "PROBLEM"), entry, None,
        needs_input_questions=[{"id": "q1", "question": "What is the statement?"}])

    assert score.needs_input is True
    assert score.matched == 0
    assert score.golden_total == 2, "still in the denominator"
    assert score.golden_belief_recall == 0.0
    totals = score_mod.totals([], [score])
    assert totals["needs_input_cases"] == 1
    assert totals["golden_belief_recall"] == 0.0


def test_exact_match_is_over_matched_pairs_only_and_per_field():
    # Judgement call 1: an unmatched golden is already counted by recall, and counting it here too
    # would double-penalise the same failure.
    entry = _entry([_belief("P1", "yes"), _belief("P2", "no")])
    result = {"assumptions": [
        {"heading": "P1", "statement": "P1.", "risk": "SUPPORTING", "mark": "DIRECT",
         "expectation": {"type": "CHOICE", "options": ["yes", "no"], "expected": "yes"}}]}

    score = score_mod.score_assumptions(_case("ASSUMPTIONS", "PROBLEM"), entry, result)
    rates = score.exact_match()

    assert rates["risk"] == 0.0, "the one matched pair got risk wrong"
    assert rates["mark"] == 1.0
    assert rates["kind"] is None and rates["unit"] is None, "a Choice pair is n/a, not agreeing"
    assert score.golden_belief_recall == 0.5


def test_the_phrase_and_the_band_are_read_together_in_four_combinations():
    golden = GoldenBelief(id="P1", stage="PROBLEM", heading="How long", statement="It took a week.",
                          founder_phrase="about a week", risk="LOAD_BEARING", asked_of="m",
                          mark="DIRECT",
                          expectation={"type": "INTERVAL",
                                       "measure": {"kind": "DURATION", "unit": "days"},
                                       "lower": {"value": 5}, "upper": {"value": 9}},
                          selection="S1", group=None)
    entry = _entry([golden])
    right_band_wrong_phrase = {
        "heading": "How long", "statement": "It took a week.", "risk": "LOAD_BEARING",
        "mark": "DIRECT", "founderPhrase": "five to nine days",
        "expectation": {"type": "INTERVAL", "measure": {"kind": "DURATION", "unit": "days"},
                        "lower": {"value": 5}, "upper": {"value": 9}}}

    score = score_mod.score_assumptions(_case("ASSUMPTIONS", "PROBLEM"), entry,
                                        {"assumptions": [right_band_wrong_phrase]})

    assert score.phrase_band["band_only"] == 1, \
        "a right band from a phrase the founder never used is right for the wrong reason"
    assert score.phrase_band["phrase_band"] == 0


def test_the_spread_reports_every_run_and_averages_nothing():
    entry = _entry([_belief("P1")])
    hit = {"assumptions": [{"heading": "P1", "statement": "P1.", "risk": "LOAD_BEARING",
                            "mark": "DIRECT",
                            "expectation": {"type": "CHOICE", "options": ["yes", "no"],
                                            "expected": "yes"}}]}
    scores = [score_mod.score_assumptions(_case("ASSUMPTIONS", "PROBLEM", 1), entry, hit),
              score_mod.score_assumptions(_case("ASSUMPTIONS", "PROBLEM", 2), entry, hit),
              score_mod.score_assumptions(_case("ASSUMPTIONS", "PROBLEM", 3), entry,
                                          {"assumptions": []})]

    spread = score_mod.spread(scores, lambda s: s.golden_belief_recall)

    assert spread["09-fixture/PROBLEM"]["runs"] == [1.0, 1.0, 0.0]
    assert spread["09-fixture/PROBLEM"]["min"] == 0.0
    assert spread["09-fixture/PROBLEM"]["max"] == 1.0


def test_three_ways_of_being_wrong_stay_three_numbers():
    totals = score_mod.totals([], [], refusals_by_rule={"E4": 2, "Q5": 1}, shape_refusals=3,
                              schema_invalid=7, errored=1, refusals_measured=True)

    assert totals["refusals_by_rule"] == {"E4": 2, "Q5": 1}
    assert totals["shape_refusals"] == 3
    assert totals["schema_invalid"] == 7
    assert totals["errored"] == 1


def test_an_unmeasured_refusal_count_fails_its_mark_rather_than_meeting_it():
    """Judgement call 13, and the reason for it: the baseline of 2026-09-06 reported
    `refusals: 0, met: true` while nothing had ever been shown to the aggregate."""
    from instructions import marks as marks_mod
    marks = marks_mod.load()

    unmeasured = score_mod.totals([], [], refusals_measured=False)
    unmeasured["anchoring_accuracy"] = 0.99
    unmeasured["golden_belief_recall"] = 0.99
    judged = marks_mod.judge(unmeasured, marks)

    assert judged["refusals"]["measured"] is False
    assert judged["refusals"]["value"] is None
    assert judged["refusals"]["met"] is False
    assert judged["passed"] is False, "two green marks and one unasked question is not a pass"

    measured = score_mod.totals([], [], refusals_measured=True, refusals_shown=63)
    measured["anchoring_accuracy"] = 0.99
    measured["golden_belief_recall"] = 0.99
    # MARKS_VERSION 4 added a fourth subject, and its mark answers to the same rule: an unmeasured
    # BRIEF is not a met BRIEF, so this run is a pass only once all four have been asked.
    assert marks_mod.judge(measured, marks)["passed"] is False
    measured["brief_paragraphs"], measured["brief_measured"] = 1.0, True
    assert marks_mod.judge(measured, marks)["passed"] is True



def test_v6_the_rule_refusal_mark_is_a_rate_over_the_answers_the_aggregate_judged():
    """Judgement call 22 (the founder, 2026-09-12): one invented unit in a full run is one
    correction, not a failed host. The denominator is what the aggregate judged, never the
    case-runs it never saw; shape refusals keep their absolute zero."""
    from instructions import marks as marks_mod
    marks = marks_mod.load()
    assert marks_mod.MARKS_VERSION == 6
    green = {"anchoring_accuracy": 0.99, "golden_belief_recall": 0.99,
             "brief_paragraphs": 1.0, "brief_measured": True}

    one_in_63 = score_mod.totals([], [], refusals_by_rule={"measure": 1}, refusals_measured=True,
                                 refusals_shown=63)
    one_in_63.update(green)
    judged = marks_mod.judge(one_in_63, marks)
    assert judged["refusals"]["value"] == 1
    assert abs(judged["refusals"]["rate"] - 1 / 63) < 1e-9
    assert judged["refusals"]["met"] is True and judged["passed"] is True

    two_in_63 = score_mod.totals([], [], refusals_by_rule={"measure": 2}, refusals_measured=True,
                                 refusals_shown=63)
    two_in_63.update(green)
    assert marks_mod.judge(two_in_63, marks)["refusals"]["met"] is False

    shape = score_mod.totals([], [], shape_refusals=1, refusals_measured=True, refusals_shown=63)
    shape.update(green)
    judged = marks_mod.judge(shape, marks)
    assert judged["shape_refusals"]["met"] is False and judged["passed"] is False

    nothing_shown = score_mod.totals([], [], refusals_measured=True, refusals_shown=0)
    nothing_shown.update(green)
    assert marks_mod.judge(nothing_shown, marks)["refusals"]["met"] is False, \
        "a run that showed the aggregate nothing has no rate"
