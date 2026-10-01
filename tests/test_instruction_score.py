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
    # Every anchor this file's reading fixtures write under. `A1` is a **merged occasion** --
    # `stages: [PROBLEM, SOLUTION]`, the shape every corpus entry's first anchor has carried since
    # the 2026-09-30 revision -- because the whole point of judgement call 24 is that one anchor
    # answering to two stages is one judgement and not two.
    anchors = [{"id": a, "stages": ["PROBLEM", "SOLUTION"] if a == "A1" else ["PROBLEM"]}
               for a in anchor_ids]
    return Entry(id="09-fixture", title="t", market={}, statements={}, roles=[],
                 beliefs=list(beliefs), questionnaire={"anchors": anchors}, answers=[],
                 expected={}, path=None, sha256="0" * 64)


def _case(kind, subject, run_index=1, earlier_lines=None):
    payload = {"context": {"earlier_lines": earlier_lines}} if earlier_lines else {}
    return Case(case_id=f"09-fixture/{subject}/run{run_index}", kind=kind, entry_id="09-fixture",
                screen="INTERPRET" if kind == "READING" else "PROBLEM_ASSUMPTIONS",
                subject=subject, run_index=run_index, payload=payload)


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


def test_an_anchoring_with_no_stage_scores_a_full_sheet_against_a_merged_anchor():
    """`MARKS_VERSION` 8, judgement call 24 (spec 025 SC-004): the match key is the bare `anchorId`.

    `AnchorRef` is a bare id since keel-cloud spec 049, so this is the shape the wire now carries,
    and `A1` here is a merged occasion serving PROBLEM and SOLUTION. Under v3's `(stage, anchorId)`
    this scored 0 of 1 with `A1` missing; it is one judgement and it agrees.
    """
    person = _person(A1="ANCHORED")
    result = {"anchorings": [{"anchorId": "A1", "anchoring": "ANCHORED"}]}   # no "stage", by design

    score = score_mod.score_reading(_case("READING", "Priya"), _entry(), person, result)

    assert score.answered == 1
    assert score.missing_ids == []
    assert score.extra_ids == []
    assert score.anchoring_accuracy == 1.0


def test_a_stage_a_model_wrote_anyway_is_neither_refused_nor_read_for():
    """The key is the id. A `stage` a model wrote is an extra field, not a wrong answer -- and
    naming the *other* stage the merged occasion serves is not a disagreement about anything, which
    is exactly why the pair stopped being the key."""
    person = _person(A1="ANCHORED")
    result = {"anchorings": [{"stage": "SOLUTION", "anchorId": "A1", "anchoring": "ANCHORED"}]}

    score = score_mod.score_reading(_case("READING", "Priya"), _entry(), person, result)

    assert score.answered == 1
    assert score.agreed == 1
    assert score.missing_ids == []
    assert score.extra_ids == []


def test_missing_and_extra_ids_are_bare_ids():
    """Spec 025 acceptance 3.3: the set arithmetic is over bare ids, both ways."""
    person = _person(A1="ANCHORED", A2="GUESSED")
    result = {"anchorings": [{"anchorId": "A1", "anchoring": "ANCHORED"},
                             {"anchorId": "A9", "anchoring": "GUESSED"}]}

    score = score_mod.score_reading(_case("READING", "Priya"), _entry(), person, result)

    assert score.missing_ids == ["A2"]
    assert score.extra_ids == ["A9"]


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
    # The rate and its denominator are v6's and have survived v7 and v8 untouched; the version
    # itself is `tests/test_instruction_marks.py`'s to pin.
    assert marks_mod.MARKS_VERSION >= 6
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


# ------------------------------- spec 025 FR-011: the reference is resolved before it is aligned

def test_score_assumptions_resolves_a_reference_before_it_aligns_and_reports_both_counts():
    """`MARKS_VERSION` 8, judgement call 27. The case's own `earlier_lines` -- the list this eval
    numbered and sent in that very prompt -- is what the ordinal is resolved against."""
    entry = _entry([_belief("P1", "yes")])
    lines = [{"stage": "PROBLEM", "line": 1, "heading": "h", "statement": "s", "measure": None,
              "band": {"options": ["yes", "no"], "expected": "yes"},
              "role": "Someone", "risk": "LOAD_BEARING"}]
    result = {"assumptions": [
        {"heading": "P1", "statement": "P1.", "risk": "LOAD_BEARING", "mark": "DIRECT",
         "reads": {"stage": "PROBLEM", "line": 1}}]}

    score = score_mod.score_assumptions(
        _case("ASSUMPTIONS", "PROBLEM", earlier_lines=lines), entry, result)

    assert score.matched == 1, "without resolve_reads this is 0 and recall falls by one line"
    assert score.golden_belief_recall == 1.0
    assert (score.resolved_reads, score.unresolved_reads) == (1, 0)


def test_an_unresolvable_reference_is_counted_and_left_to_fail_to_match():
    entry = _entry([_belief("P1", "yes")])
    result = {"assumptions": [
        {"heading": "P1", "statement": "P1.", "risk": "LOAD_BEARING", "mark": "DIRECT",
         "reads": {"stage": "PROBLEM", "line": 9}}]}

    score = score_mod.score_assumptions(_case("ASSUMPTIONS", "PROBLEM"), entry, result)

    assert score.matched == 0
    assert (score.resolved_reads, score.unresolved_reads) == (0, 1)
    totals = score_mod.totals([], [score])
    assert totals["unresolved_reads"] == 1
    assert totals["resolved_reads"] == 0
