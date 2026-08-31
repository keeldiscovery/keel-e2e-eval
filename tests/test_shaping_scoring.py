"""Stackless tests for the shaping gauntlet's scoring (harness/shaping_scoring.py): SHP-6's own
token-overlap math, and a seeded-failure-plus-clean-control pass over SHP-1..SHP-7 (the same
construction `tests/test_policy_v4.py` already uses for its own checks). Runs under `make unit`
-- no stack, no `claude` CLI required.
"""

from __future__ import annotations

from harness.founder_sim import FounderSimulator
from harness.shaping_scoring import (BeliefSnapshot, ShpCheck, StageSnapshot, extract_numbers,
                                      has_unknown_marker, jaccard_overlap, near_duplicate_pairs,
                                      round_half, shaping_score, vague_word_hits,
                                      compute_shp_checks)


def _check(checks: list[ShpCheck], check_id: str) -> ShpCheck:
    return next(c for c in checks if c.check_id == check_id)


# ------------------------------------------------------------------------------- pure-text helpers

def test_extract_numbers_finds_dollar_percent_and_plain_forms():
    assert extract_numbers("about $99 a month, or 90 minutes, or 12.5%") == {"$99", "90", "12.5%"}


def test_extract_numbers_is_empty_for_no_digits():
    assert extract_numbers("no numbers here at all") == set()


def test_jaccard_overlap_is_one_for_identical_text_after_normalization():
    assert jaccard_overlap("They reconcile inventory by hand.", "THEY RECONCILE INVENTORY BY HAND!!") == 1.0


def test_jaccard_overlap_is_zero_for_disjoint_text():
    assert jaccard_overlap("restaurant managers reconcile inventory", "software pricing budget owner") == 0.0


def test_jaccard_overlap_is_zero_when_one_side_has_no_meaningful_tokens():
    assert jaccard_overlap("", "the a an") == 0.0  # nothing but stopwords on one side


def test_near_duplicate_pairs_flags_only_pairs_at_or_above_threshold():
    statements = [
        "They reconcile inventory by hand every month-end close.",
        "They reconcile the inventory by hand every month-end close period.",  # near-identical
        "Independent restaurant managers would pay a monthly fee.",  # unrelated
    ]
    pairs = near_duplicate_pairs(statements)
    assert [(i, j) for i, j, _overlap in pairs] == [(0, 1)]
    assert pairs[0][2] >= 0.6


def test_vague_word_hits_matches_whole_words_only():
    assert vague_word_hits("This is a useful, easy tool.") == ["easy", "useful"]
    # "badge"/"usefulness"/"easygoing" each contain a banned word as a substring but not as a
    # whole word (no boundary right after "bad"/"useful"/"easy") -- none should match.
    assert vague_word_hits("The badge, usefulness, and easygoing cat") == []


def test_has_unknown_marker_matches_common_phrasings():
    assert has_unknown_marker("the price is unknown for now")
    assert has_unknown_marker("honestly, not sure")
    assert not has_unknown_marker("the price is $99 a month")


# ------------------------------------------------------------------------------------- round_half

def test_round_half_rounds_to_the_nearest_half_point():
    assert round_half(4.24) == 4.0
    assert round_half(4.26) == 4.5
    assert round_half(4.75) == 5.0


def test_shaping_score_is_5x_weighted_pass_fraction():
    checks = [ShpCheck("A", "a", True, "d"), ShpCheck("B", "b", False, "d"),
              ShpCheck("C", "c", True, "d"), ShpCheck("D", "d", True, "d")]
    # 3/4 passed -> 5 * 0.75 = 3.75 -> rounds to 4.0 (nearest half)
    assert shaping_score(checks) == 4.0


def test_shaping_score_is_zero_for_no_checks():
    assert shaping_score([]) == 0.0


# --------------------------------------------------------------------------- compute_shp_checks

def _good_run() -> tuple[StageSnapshot, StageSnapshot, StageSnapshot, FounderSimulator]:
    """A fully-shaped run: every fact earned, every claim grounded in what was actually earned,
    two clearly-distinct PROBLEM beliefs, no vague words, no invented numbers. All seven SHP
    checks pass -- the clean control every seeded-failure test below perturbs exactly one thing
    away from."""
    sim = FounderSimulator()
    sim.earned = {"who": 1, "frequency": 2, "cost": 3, "mechanism": 4, "price": 5}
    problem = StageSnapshot(
        stage="PROBLEM",
        claim="Independent restaurant managers lose about 90 minutes each time, every "
              "month-end close, reconciling inventory.",
        previous_claim=None,
        beliefs=[
            BeliefSnapshot(heading="Handles it themselves",
                            statement="They reconcile inventory by hand every month-end close.",
                            verdict=None, applying=True),
            BeliefSnapshot(heading="Costs real time",
                            statement="Sorting out the mismatches takes real concentration and focus.",
                            verdict=None, applying=True),
        ],
    )
    solution = StageSnapshot(
        stage="SOLUTION",
        claim="It scans the shelf counts and compares them against what the POS system already "
              "recorded, and flags whatever doesn't match.",
        previous_claim=None, beliefs=[],
    )
    commercial = StageSnapshot(
        stage="COMMERCIAL",
        claim="Independent restaurant managers would pay maybe $99 a month, honestly not sure, "
              "once it reliably flags mismatches.",
        previous_claim=None, beliefs=[],
    )
    return problem, solution, commercial, sim


def test_the_good_run_passes_every_shp_check():
    problem, solution, commercial, sim = _good_run()
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert {c.check_id for c in checks} == {f"SHP-{n}" for n in range(1, 8)}
    failed = [c.check_id for c in checks if not c.passed]
    assert failed == [], [(_check(checks, cid).detail) for cid in failed]
    assert shaping_score(checks) == 5.0


def test_shp1_fails_when_a_quantifying_fact_was_never_earned():
    problem, solution, commercial, sim = _good_run()
    del sim.earned["frequency"]
    problem.claim = ("Independent restaurant managers lose about 90 minutes each time "
                      "reconciling inventory.")
    # Beliefs cleared too -- the good-run fixture's own belief text happens to repeat "month-end
    # close" (grounding the frequency fact when it IS earned), which would otherwise leak into
    # SHP-7's own "is this dimension mentioned anywhere on its home stage" check and break this
    # test's isolation claim. SHP-1 itself never reads beliefs at all, so this changes nothing it
    # actually measures.
    problem.beliefs = []
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert not _check(checks, "SHP-1").passed
    assert "frequency" in _check(checks, "SHP-1").detail
    # isolated: every other check still passes
    assert all(c.passed for c in checks if c.check_id != "SHP-1")


def test_shp2_fails_on_an_invented_number_never_released():
    problem, solution, commercial, sim = _good_run()
    problem.beliefs[1].statement = "Sorting out the mismatches takes about 3 hours of focus."
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert not _check(checks, "SHP-2").passed
    assert "3" in _check(checks, "SHP-2").detail
    assert all(c.passed for c in checks if c.check_id != "SHP-2")


def test_shp3_fails_when_the_solution_claim_is_a_bare_label():
    problem, solution, commercial, sim = _good_run()
    del sim.earned["mechanism"]
    solution.claim = "An inventory management app."
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert not _check(checks, "SHP-3").passed
    assert all(c.passed for c in checks if c.check_id != "SHP-3")


def test_shp4_fails_when_the_commercial_claim_never_names_a_buyer():
    problem, solution, commercial, sim = _good_run()
    commercial.claim = "Restaurant managers would find this valuable."
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert not _check(checks, "SHP-4").passed
    assert all(c.passed for c in checks if c.check_id != "SHP-4")


def test_shp5_fails_on_a_banned_vague_word():
    problem, solution, commercial, sim = _good_run()
    problem.beliefs[1].statement = "It's useful because it takes real focus to sort out."
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert not _check(checks, "SHP-5").passed
    assert "useful" in _check(checks, "SHP-5").detail
    assert all(c.passed for c in checks if c.check_id != "SHP-5")


def test_shp6_fails_on_near_duplicate_problem_beliefs():
    problem, solution, commercial, sim = _good_run()
    problem.beliefs[1] = BeliefSnapshot(
        heading="Handles it themselves (again)",
        statement="They reconcile the inventory by hand every month-end close period.",
        verdict=None, applying=True)
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert not _check(checks, "SHP-6").passed
    assert all(c.passed for c in checks if c.check_id != "SHP-6")


def test_shp7_fails_when_a_never_earned_dimension_is_mentioned_without_being_named_unknown():
    problem, solution, commercial, sim = _good_run()
    del sim.earned["frequency"]
    # Mentions the topic (a month-ish cadence) without ever earning the fact and without any
    # "unknown"/"not sure" marker anywhere on the stack -- a silent guess, not a surfaced gap.
    problem.beliefs.append(BeliefSnapshot(
        heading="Happens monthly", statement="This comes up about once a month or so.",
        verdict=None, applying=True))
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert not _check(checks, "SHP-7").passed
    assert "frequency" in _check(checks, "SHP-7").detail
    # Note: this dimension also feeds SHP-1 (frequency is one of the quantifying facts), so SHP-1
    # legitimately fails here too -- not a test bug, the two checks share the same underlying gap.


def test_shp7_passes_when_a_never_earned_dimension_is_named_as_a_genuine_unknown():
    problem, solution, commercial, sim = _good_run()
    del sim.earned["frequency"]
    problem.claim = ("Independent restaurant managers lose about 90 minutes reconciling "
                      "inventory; how often this happens is still unknown.")
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert _check(checks, "SHP-7").passed


def test_the_empty_stack_fails_the_presence_checks_honestly_rather_than_crashing():
    """No project was ever created (harness/shaping_scoring.py's `empty_stage` -- the honest
    fallback `evals/test_shaping_gauntlet.py` uses when the conversation never produced one):
    every check still runs, none crashes on the missing claim/belief text. SHP-1/3/4 (which all
    require a *grounded, present* claim) fail correctly; SHP-2/5/6/7 (which look for something
    gone *wrong*, not for presence) pass vacuously -- silence is not the same failure mode as
    fakery, vagueness, duplication, or an unsurfaced unknown, and this test pins that distinction
    rather than assuming a blanket all-fail."""
    from harness.shaping_scoring import empty_stage
    sim = FounderSimulator()
    problem, solution, commercial = (empty_stage("PROBLEM"), empty_stage("SOLUTION"),
                                      empty_stage("COMMERCIAL"))
    checks = compute_shp_checks(problem, solution, commercial, sim)
    assert len(checks) == 7
    failed = {c.check_id for c in checks if not c.passed}
    assert failed == {"SHP-1", "SHP-3", "SHP-4"}
    assert shaping_score(checks) == 3.0
