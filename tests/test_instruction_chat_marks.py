"""The calibration chat's six marks (spec 035 US1, US2; `MARKS_VERSION` 17, calls 76-79): every mark has a fixture
that passes and one that fails each of its clauses (SC-001). The answers are hand-written in
`tests/fixtures/chat/results.yaml`; the three acceptance scenarios of the spec are the first three tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from instructions import chat as chat_mod
from instructions.corpus import ChatCase

FIX = Path(__file__).parent / "fixtures" / "chat"
RESULTS = yaml.safe_load((FIX / "results.yaml").read_text(encoding="utf-8"))
BLOCKS = yaml.safe_load((FIX / "blocks.yaml").read_text(encoding="utf-8"))
PAYROLL_WORDS = ["payroll error checker", "error checker", "register checker"]


def case(dimension, founder, *, follow_up=False, measure, family=None, respondent, idea="payroll"):
    return ChatCase(idea=idea, dimension=dimension, founder=founder, follow_up=follow_up, measure=measure,
                    family=family, respondent=respondent)


CURRENT = case("problem.current_solution_satisfaction",
               "They check every line by hand against last month. It takes hours and they still miss some.",
               follow_up=True, measure="TIME", respondent="band_ladder")
RELATIVE = case("solution.relative_advantage", "It would cut the checking time by about half.",
                measure="PERCENT", respondent="word_bands")
ADOPTION = case("solution.adoption_friction",
                "Downloading the register and uploading it every run, loading past registers once.",
                follow_up=True, measure="EFFORT", family="EACH_TIME", respondent="effort_yes_no")
CHOC_ADOPTION = case("solution.adoption_friction", "Nothing, really; you pick it off the shelf.",
                     measure="EFFORT", respondent="leave_out", idea="dark-chocolate")
VOICE_HABIT = case("solution.adoption_friction", "They would record one most days.", follow_up=True,
                   measure="EFFORT", family="HABIT", respondent="how_often", idea="voice-notes")
IMPORTANCE = case("problem.importance",
                  "Collecting hours on time, tax rules, finance approval, reconciling with the books.",
                  measure="LIST", respondent="top_three")
COMMITMENT = case("commercial.commitment", "A read-only trial on last month's register.",
                  measure="LADDER", respondent="furthest_rung")
PRICE = case("commercial.price", "Per company, a lot a quarter.", measure="MONEY", respondent="price_ladder")


def result(name):
    return RESULTS[name]


def block(c):
    return BLOCKS[c.dimension]


def one(c, name):
    return chat_mod.one_measurable(c, block(c), result(name))


# ------------------------------------------------------------------------- the spec's acceptance scenarios

def test_acceptance_1_payroll_current_solution_wants_one_follow_up_and_one_measure():
    """Hours and still miss some: one follow-up passes; zero fail the budget; a proposal of both kinds fails."""
    assert chat_mod.follow_up_budget(CURRENT, [("NEEDS_INPUT", 1), "COMPLETED"]) == (True, [])
    passed, why = chat_mod.follow_up_budget(CURRENT, ["COMPLETED"])
    assert not passed and "expected" in why[0]
    passed, why = one(CURRENT, "payroll_current_two_kinds")
    assert not passed and why[0].startswith("CC1")
    assert one(CURRENT, "payroll_current_ok") == (True, [])


def test_acceptance_2_a_respondent_slot_with_the_founders_half_or_fifty_percent_leaks():
    assert chat_mod.no_founder_leak(RELATIVE, PAYROLL_WORDS, result("payroll_ra_ok")) == (True, [])
    for name, said in (("payroll_ra_half", "half"), ("payroll_ra_fifty", "50")):
        passed, why = chat_mod.no_founder_leak(RELATIVE, PAYROLL_WORDS, result(name))
        assert not passed and any(said in w and w.startswith("SHOWS_NUMBER") for w in why), (name, why)


def test_acceptance_3_leave_out_passes_and_inventing_paying_more_fails():
    assert one(CHOC_ADOPTION, "chocolate_adoption_left_out") == (True, [])
    passed, why = one(CHOC_ADOPTION, "chocolate_adoption_invented")
    assert not passed and "leave_out" in why[0]


# --------------------------------------------------------------------------------------- one_measurable

@pytest.mark.parametrize("c, name, starts", [
    (CURRENT, "payroll_current_two_kinds", "CC1"),
    (CURRENT, "payroll_current_proposals", "CC1"),
    (CURRENT, "payroll_current_errors", "CC2"),             # ERRORS is not a measure of Current solution
    (CURRENT, "payroll_current_money", "the corpus expects TIME"),
    (ADOPTION, "payroll_adoption_money", "CC5"),
    (VOICE_HABIT, "voice_habit_no_frequency", "CC8"),
    (COMMITMENT, "payroll_commitment_money_early", "CC6"),
    (COMMITMENT, "payroll_commitment_no_money", "CC6"),
    (PRICE, "payroll_price_no_unit", "CC7"),
    (PRICE, "payroll_price_per_item_no_count", "CC7"),
])
def test_one_measurable_fails_each_clause_by_name(c, name, starts):
    passed, why = one(c, name)
    assert not passed and any(w.startswith(starts) for w in why), why


def test_one_measurable_passes_each_clean_proposal():
    for c, name in ((CURRENT, "payroll_current_ok"), (RELATIVE, "payroll_ra_ok"),
                    (ADOPTION, "payroll_adoption_ok"), (VOICE_HABIT, "voice_habit_ok"),
                    (COMMITMENT, "payroll_commitment_ok"), (PRICE, "payroll_price_ok")):
        assert one(c, name) == (True, []), (name, one(c, name))


def test_one_measurable_wants_the_corpus_family():
    wrong_family = case("solution.adoption_friction", "x", measure="EFFORT", family="ONCE",
                        respondent="effort_yes_no")
    passed, why = one(wrong_family, "payroll_adoption_ok")
    assert not passed and "family ONCE" in why[0]


def test_one_measurable_refuses_a_leave_out_where_the_corpus_measures_and_no_answer_at_all():
    passed, why = one(CURRENT, "chocolate_adoption_left_out")
    assert not passed and "left out where the corpus measures it as TIME" in why[0]
    assert chat_mod.one_measurable(CURRENT, block(CURRENT), None)[0] is False


# ------------------------------------------------------------------------------------- follow_up_budget

def test_the_follow_up_budget_is_one_and_only_where_expected():
    ask = ("NEEDS_INPUT", 1)
    assert chat_mod.follow_up_budget(CURRENT, [ask, "COMPLETED"])[0]
    assert chat_mod.follow_up_budget(IMPORTANCE, ["COMPLETED"])[0]
    assert chat_mod.follow_up_budget(CURRENT, [ask])[0], "one call: the follow-up asked, the reply unscripted"
    twice = chat_mod.follow_up_budget(CURRENT, [ask, ask, "COMPLETED"])
    assert not twice[0] and twice[1][0].startswith("C9")
    needless = chat_mod.follow_up_budget(IMPORTANCE, [ask, "COMPLETED"])
    assert not needless[0] and "needless" in needless[1][0]
    missed = chat_mod.follow_up_budget(CURRENT, ["COMPLETED"])
    assert not missed[0] and "expected" in missed[1][0]
    three_questions = chat_mod.follow_up_budget(CURRENT, [("NEEDS_INPUT", 3), "COMPLETED"])
    assert not three_questions[0] and "one question" in three_questions[1][0]


# ----------------------------------------------------------------------------------------- preview_rules

def preview(c, name):
    return chat_mod.preview_rules(c, block(c), result(name))


def test_preview_rules_pass_a_clean_proposal_and_a_balanced_yes_no():
    assert preview(RELATIVE, "payroll_ra_ok") == (True, [])
    assert preview(ADOPTION, "payroll_adoption_ok") == (True, [])
    assert preview(IMPORTANCE, "payroll_importance_ok") == (True, [])
    assert preview(CHOC_ADOPTION, "chocolate_adoption_left_out") == (True, [])


def test_preview_rules_fail_each_clause():
    passed, why = preview(ADOPTION, "payroll_adoption_unbalanced")
    assert not passed and why[0].startswith("LEADING_OPTION")            # a yes/no ends ", or not?"
    passed, why = preview(RELATIVE, "payroll_ra_choices_on_a_code_frame")
    assert not passed and why[0].startswith("CHANGES_FRAME") and "word_bands" in why[0]
    wrong_frame = case("solution.relative_advantage", "x", measure="PERCENT", respondent="band_ladder")
    passed, why = preview(wrong_frame, "payroll_ra_ok")                  # the corpus expects another frame
    assert not passed and "band_ladder" in why[0]
    passed, why = preview(CHOC_ADOPTION, "chocolate_adoption_invented")  # a left-out dimension shows nothing
    assert not passed
    labelled = {"proposal": {**result("payroll_current_ok")["proposal"], "none_label": "Fewer than 3 hours"}}
    passed, why = chat_mod.preview_rules(CURRENT, block(CURRENT), labelled)
    assert not passed and "carries a number" in why[0]


def test_a_habit_is_framed_by_how_often_not_by_yes_no():
    assert preview(VOICE_HABIT, "voice_habit_ok") == (True, [])


# ------------------------------------------------------------------------------------- no_founder_leak

def leak(c, name):
    return chat_mod.no_founder_leak(c, PAYROLL_WORDS, result(name))


def test_no_founder_leak_passes_a_clean_answer_and_a_list_of_the_founders_own_parts():
    assert leak(CURRENT, "payroll_current_ok") == (True, [])
    assert leak(IMPORTANCE, "payroll_importance_ok") == (True, []), "the founder's list is the list"


def test_no_founder_leak_fails_a_number_word_a_percentage_and_a_run_of_the_founders_words():
    assert not leak(RELATIVE, "payroll_ra_half")[0]
    assert not leak(RELATIVE, "payroll_ra_fifty")[0]
    passed, why = leak(RELATIVE, "payroll_ra_run_of_words")
    assert not passed and why[0].startswith("SHOWS_BELIEF")
    hours = case("problem.current_solution_satisfaction", "It takes about 3 hours.", measure="TIME",
                 respondent="band_ladder")
    passed, why = chat_mod.no_founder_leak(hours, PAYROLL_WORDS, {"proposal": {
        "kind": "TIME", "question": "Did checking take 3 hours on your last run?"}})
    assert not passed and "'3'" in why[0]
    spelled = case("problem.current_solution_satisfaction", "It takes about three hours.", measure="TIME",
                   respondent="band_ladder")
    assert not chat_mod.no_founder_leak(spelled, PAYROLL_WORDS, {"proposal": {
        "kind": "TIME", "question": "Did checking take three hours on your last run?"}})[0]


def test_no_founder_leak_keeps_the_idea_out_of_a_problem_slot_only():
    named = {"proposal": {"kind": "TIME", "question": "How long did the payroll error checker take to run?"}}
    passed, why = chat_mod.no_founder_leak(CURRENT, PAYROLL_WORDS, named)
    assert not passed and "names the idea" in why[0]
    solution = case("solution.adoption_friction", "x", measure="EFFORT", respondent="effort_yes_no")
    assert chat_mod.no_founder_leak(solution, PAYROLL_WORDS, named)[0], "after the reveal the idea may be named"


def test_founder_numbers_reads_digits_words_and_fractions():
    said = chat_mod.founder_numbers("about half, $2,400 and two or three times")
    assert {"half", "50", "2400", "two", "three"} <= set(said)


# ------------------------------------------------------------------------------------- importance_list

def test_the_importance_list_is_the_problem_plus_six_others():
    assert chat_mod.importance_list(IMPORTANCE, PAYROLL_WORDS, result("payroll_importance_ok")) == (True, [])
    for name, starts in (("payroll_importance_five", "CC3"), ("payroll_importance_names_the_idea", "CC4"),
                         ("payroll_importance_the_problem_again", "CC4"),
                         ("payroll_importance_near_neighbours", "near-neighbours")):
        passed, why = chat_mod.importance_list(IMPORTANCE, PAYROLL_WORDS, result(name))
        assert not passed and any(w.startswith(starts) for w in why), (name, why)


# -------------------------------------------------------------------------------------- feedback_obeys

CASES = {c["id"]: c for c in chat_mod.feedback_cases()}
ITEM = CASES["payroll-current/chatpreview-example"]["item"]
RIGHT = {
    "payroll-current/chatpreview-example": {
        "change": {"question": "On your last payroll run, about how long did checking it take?",
                   "add_option": {"label": "Someone else checks it", "kind": "SOMEONE_ELSE"}},
        "said": "I've asked about the last run and added an answer for when someone else checks it. The ranges "
                "stay: they're built around your number."},
    "payroll-current/reword": {"change": {"question": "On your last payroll run, about how long did checking it take?"},
                               "said": "Reworded."},
    "payroll-current/relabel-none": {"change": {"labels": [{"code": "none", "label": "Nobody checks it"}]},
                                     "said": "Relabelled."},
    "payroll-current/shows-number": {"refused": {"rule": "SHOWS_NUMBER"}, "said": "That is your own number."},
    "payroll-current/shows-belief": {"refused": {"rule": "SHOWS_BELIEF"}, "said": "That is what you believe."},
    "payroll-current/drops-escape": {"refused": {"rule": "DROPS_ESCAPE"}, "said": "That answer stays."},
    "payroll-current/changes-frame": {"refused": {"rule": "CHANGES_FRAME"}, "said": "The ranges are code's."},
    "payroll-adoption/leading-option": {"refused": {"rule": "LEADING_OPTION"}, "said": "That leans your way."},
    "payroll-adoption/reword-keeps-balance": {
        "change": {"question": "Before each payroll goes out, you'd download the register and upload it to the "
                               "checker, about a minute or so. Would you do that every run, or not?"},
        "said": "Reworded, still balanced."},
    "payroll-importance/remove-item": {"change": {"remove_option": "other_3"}, "said": "Dropped it."},
}


def test_every_feedback_case_has_a_right_answer_and_it_scores():
    assert set(RIGHT) == set(CASES), "one right answer a case"
    for case_id, answer in RIGHT.items():
        assert chat_mod.feedback_obeys(CASES[case_id], answer) == (True, []), \
            (case_id, chat_mod.feedback_obeys(CASES[case_id], answer))


def test_there_is_a_feedback_case_for_each_rule_and_each_allowed_change():
    refused = {c["expect"]["rule"] for c in CASES.values() if c["expect"]["outcome"] == "refuse"}
    assert refused == set(chat_mod.RULES)
    changes = {k for c in CASES.values() if c["expect"]["outcome"] == "change" for k in c["expect"]["change"]}
    assert changes == {"reword", "add_kind", "relabel", "remove"}


def test_chatpreviews_example_scores_one():
    answer = RIGHT["payroll-current/chatpreview-example"]
    score = chat_mod.score_feedback(CASES["payroll-current/chatpreview-example"], "COMPLETED", answer)
    assert score.marks == {"feedback_obeys": True} and score.faults == []


@pytest.mark.parametrize("case_id, answer, why", [
    # a forbidden request refused with the wrong rule, and not refused at all
    ("payroll-current/shows-number", {"refused": {"rule": "SHOWS_BELIEF"}, "said": "x"}, "the right rule"),
    ("payroll-current/drops-escape", {"change": {"remove_option": "none"}, "said": "Done."}, "refused nothing"),
    # an invented rule
    ("payroll-current/drops-escape", {"refused": {"rule": "TOO_LONG"}, "said": "x"}, "F2"),
    # no `said`
    ("payroll-current/reword", {"change": {"question": "On your last payroll run, how long?"}}, "F1"),
    # an allowed change refused: nothing applied
    ("payroll-current/reword", {"refused": {"rule": "CHANGES_FRAME"}, "said": "No."}, "nothing was applied"),
    # an allowed change not made
    ("payroll-current/reword", {"said": "Fine as it is."}, "none was made"),
    # the change applied beside things it was not asked to change
    ("payroll-current/reword", {"change": {"question": "On your last payroll run, how long?",
                                           "add_option": {"label": "Someone else checks it",
                                                          "kind": "SOMEONE_ELSE"}}, "said": "x"}, "added"),
    ("payroll-current/chatpreview-example",
     {"change": {"add_option": {"label": "Someone else checks it", "kind": "SOMEONE_ELSE"}}, "said": "x"},
     "to be reworded"),
    # an allowed-looking change that ItemRules refuses: the model should have said so
    ("payroll-current/reword", {"change": {"question": "How long did two to three hours of checking take?"},
                                "said": "x"}, "SHOWS_NUMBER"),
    ("payroll-current/relabel-none", {"change": {"labels": [{"code": "under_1", "label": "Under an hour"}]},
                                      "said": "x"}, "CHANGES_FRAME"),
])
def test_feedback_obeys_fails_each_clause(case_id, answer, why):
    passed, faults = chat_mod.feedback_obeys(CASES[case_id], answer)
    assert not passed and any(why in f for f in faults), faults


def test_a_feedback_case_that_never_answered_is_a_miss_not_a_skip():
    score = chat_mod.score_feedback(CASES["payroll-current/reword"], None, None, failed="timed out")
    assert score.marks == {"feedback_obeys": False}


# ---------------------------------------------------------------------------------- scoring and totals

def test_score_chat_measures_what_one_call_can_and_leaves_the_rest_unmeasured():
    ask = chat_mod.score_chat(CURRENT, block(CURRENT), PAYROLL_WORDS, "NEEDS_INPUT", None, questions=1)
    assert ask.marks == {"follow_up_budget": True}, "a follow-up asked has no proposal to read yet"
    done = chat_mod.score_chat(IMPORTANCE, block(IMPORTANCE), PAYROLL_WORDS, "COMPLETED",
                               result("payroll_importance_ok"))
    assert done.marks == {"follow_up_budget": True, "one_measurable": True, "preview_rules": True,
                          "no_founder_leak": True, "importance_list": True}
    broken = chat_mod.score_chat(IMPORTANCE, block(IMPORTANCE), PAYROLL_WORDS, "COMPLETED",
                                 result("payroll_importance_five"))
    assert broken.marks["importance_list"] is False and broken.faults


def test_a_case_with_no_answer_misses_every_mark_it_applies_to():
    miss = chat_mod.score_chat(IMPORTANCE, block(IMPORTANCE), PAYROLL_WORDS, None, None, failed="never fit its shape")
    assert miss.marks == {"one_measurable": False, "follow_up_budget": False, "preview_rules": False,
                          "no_founder_leak": False, "importance_list": False}


def test_totals_sum_each_mark_over_the_cases_it_reached_and_leave_unreached_marks_none():
    scores = [chat_mod.ChatScore("a", "CHAT", {"one_measurable": True, "follow_up_budget": True}),
              chat_mod.ChatScore("b", "CHAT", {"one_measurable": False, "follow_up_budget": None}),
              chat_mod.ChatScore("c", "FEEDBACK", {"feedback_obeys": True})]
    t = chat_mod.totals(scores)
    assert t["one_measurable"] == 0.5 and t["one_measurable_of"] == 2 and t["one_measurable_hit"] == 1
    assert t["follow_up_budget"] == 1.0 and t["follow_up_budget_of"] == 1
    assert t["feedback_obeys"] == 1.0 and t["chat_cases"] == 2 and t["feedback_cases"] == 1
    assert t["importance_list"] is None and t["importance_list_of"] == 0
    assert chat_mod.totals([])["one_measurable"] is None
