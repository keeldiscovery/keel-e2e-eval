"""The chat rules against keel-cloud's own tests (spec 035 FR-004, T008; `MARKS_VERSION` 17, call 78).

**Parity, as far as it can go.** The spec asked for these to be proved equal to the real `screenContracts validate`.
At keel-cloud 083 the validator takes neither chat screen (CC1-CC8, C9, F1, F2 and `ItemRules` run in the
orchestrator), so there is no verdict to compare with. What there is: keel-cloud's `ItemRulesTest` and
`CalibrationChatContractTest`, whose cases are transcribed below clause for clause -- each expected rule is the one the
Java test asserts. `validate._SHAPE_MARKERS` lists the two screens, so the day the validator names them they are
batched and this file is where a parity run against it goes.
"""

from __future__ import annotations

import pytest

from instructions import chat as chat_mod
from instructions import validate as validate_mod
from instructions.corpus import ChatCase

# ------------------------------------------------------------------------------- ItemRulesTest (T006)

PAYROLL_NUMBERS = [2, 3]


def band(code, label):
    return {"code": code, "label": label, "kind": "BAND"}


def payroll():
    return {"frame": "band_ladder",
            "question": "On your last payroll that's been paid and settled, about how long did checking it take?",
            "options": [band("under_1", "Under 1 hour"), band("band_1_2", "1 to 2 hours"),
                        band("band_2_5", "2 to 5 hours"), band("band_5_10", "5 to 10 hours"),
                        band("over_10", "More than 10 hours"),
                        {"code": "none", "label": "We don't check it", "kind": "NONE"}]}


def friction():
    return {"frame": "effort_yes_no",
            "question": "Before approving each payroll, you'd download the register and upload it to the checker, "
                        "about 2 minutes. Would you do that every payroll run, or not?",
            "options": [{"code": "yes", "label": "Yes, every run", "kind": "YES"},
                        {"code": "conditional", "label": "Only if it clearly saved me time", "kind": "YES_CONDITIONAL"},
                        {"code": "probably_not", "label": "Probably not", "kind": "PROBABLY_NOT"},
                        {"code": "no", "label": "No", "kind": "NO"}]}


def check(reference, candidate, numbers=(), claim=None, addable=("NONE", "SOMEONE_ELSE")):
    found = chat_mod.item_check(reference, candidate, numbers=numbers, claim=claim, addable=addable)
    return found[0] if found else None


def with_(item, question=None, options=None):
    return {**item, "question": question or item["question"], "options": options or item["options"]}


def test_the_item_as_built_passes():
    assert check(payroll(), payroll(), PAYROLL_NUMBERS) is None
    assert check(friction(), friction(), claim="would upload every run", addable=("YES_CONDITIONAL",)) is None


def test_rewording_the_occasion_and_adding_someone_else_is_allowed():
    item = payroll()
    changed = with_(item, "On your last payroll run, about how long did checking it take?",
                    item["options"] + [{"code": "someone_else", "label": "Someone else checks it",
                                        "kind": "SOMEONE_ELSE"}])
    assert check(item, changed, PAYROLL_NUMBERS) is None


def test_the_founders_number_as_digits_or_a_word_is_shows_number():
    for question in ("Did checking take about 2 hours on your last run?",
                     "Did checking take three hours or so on your last run?"):
        assert check(payroll(), with_(payroll(), question), PAYROLL_NUMBERS) == "SHOWS_NUMBER"


def test_the_beliefs_own_words_are_shows_belief():
    item = friction()
    leaking = with_(item, "Most people say they would feel closer to their friends. "
                          "Would you do that every payroll run, or not?")
    assert check(item, leaking, claim="they would feel closer to their friends",
                 addable=("YES_CONDITIONAL",)) == "SHOWS_BELIEF"


def test_an_added_supporting_option_or_an_unbalanced_yes_no_is_leading():
    item = friction()
    added = [{"code": "definitely", "label": "Yes, definitely, it's a great idea", "kind": "YES"}] + item["options"]
    assert check(item, with_(item, options=added), PAYROLL_NUMBERS) == "LEADING_OPTION"
    assert check(item, with_(item, "Would you do that every payroll run?"), PAYROLL_NUMBERS) == "LEADING_OPTION"


def test_dropping_none_is_drops_escape():
    item = payroll()
    dropped = [o for o in item["options"] if o["kind"] != "NONE"]
    assert check(item, with_(item, options=dropped), PAYROLL_NUMBERS) == "DROPS_ESCAPE"


def test_a_band_relabelled_or_removed_is_changes_frame():
    item = payroll()
    relabelled = [dict(o) for o in item["options"]]
    relabelled[2]["label"] = "2 to 3 hours"
    assert check(item, with_(item, options=relabelled), PAYROLL_NUMBERS) == "CHANGES_FRAME"
    fewer = [o for i, o in enumerate(item["options"]) if i != 4]
    assert check(item, with_(item, options=fewer), PAYROLL_NUMBERS) == "CHANGES_FRAME"


def test_an_added_option_of_a_kind_the_frame_does_not_take_is_changes_frame():
    item = payroll()
    added = item["options"] + [{"code": "cant_tell", "label": "I can't tell", "kind": "CANT_TELL"}]
    found = chat_mod.item_check(item, with_(item, options=added), numbers=PAYROLL_NUMBERS,
                                addable=("NONE", "SOMEONE_ELSE"))
    assert found[0] == "CHANGES_FRAME"


# ------------------------------------------------------------------- CalibrationChatContractTest (T008)

BLOCKS = {
    "problem.current_solution_satisfaction": {"measures": ["TIME", "MONEY", "EFFORT"],
                                              "respondent": {"frames": {"TIME": "band_ladder"}}},
    "problem.importance": {"measures": ["LIST"], "respondent": {"frames": {"LIST": "top_three"}}},
    "solution.adoption_friction": {"measures": ["EFFORT"], "respondent": {"frames": {"EFFORT": "effort_yes_no"}}},
    "commercial.commitment": {"measures": ["LADDER"], "respondent": {"frames": {"LADDER": "furthest_rung"}}},
    "commercial.price": {"measures": ["MONEY"], "respondent": {"frames": {"MONEY": "price_ladder"}}},
}


def cc(dimension, proposal, measure, family=None, respondent="band_ladder"):
    case = ChatCase("lullaby", dimension, "x", False, measure, family, respondent)
    return chat_mod.one_measurable(case, BLOCKS[dimension], {"proposal": proposal, "belief_draft": "a belief",
                                                              "kept_verbatim": []})


@pytest.mark.parametrize("dimension, proposal, measure, family, rule", [
    ("problem.current_solution_satisfaction", {"kind": ["TIME", "MONEY"], "question": "q"}, "TIME", None, "CC1"),
    ("problem.current_solution_satisfaction", {"kind": "PERCENT", "question": "q"}, "TIME", None, "CC2"),
    ("problem.importance", {"kind": "LIST", "question": "q", "own_item": "Not knowing why",
                            "choices": ["a", "b", "c", "d", "e"]}, "LIST", None, "CC3"),
    ("problem.importance", {"kind": "LIST", "question": "q", "own_item": "Not knowing why the baby cries",
                            "choices": ["Night feeds", "Naps", "Sharing nights", "Nappies",
                                        "Getting a suggested reason for crying from an app",
                                        "Room temperature"]}, "LIST", None, "CC4"),
    ("problem.importance", {"kind": "LIST", "question": "q", "own_item": "Not knowing why the baby cries",
                            "choices": ["Night feeds", "Naps", "Sharing nights", "Nappies",
                                        "Why the baby cries, not knowing it", "Room temperature"]}, "LIST", None,
     "CC4"),
    ("solution.adoption_friction", {"kind": "EFFORT", "family": "EACH_TIME",
                                    "question": "Would you pay £5 every month for it, or not?",
                                    "condition_label": "Only if it helped"}, "EFFORT", "EACH_TIME", "CC5"),
    ("solution.adoption_friction", {"kind": "EFFORT", "family": "HABIT",
                                    "question": "How often would you record a note?"}, "EFFORT", "HABIT", "CC8"),
    ("commercial.commitment", {"kind": "LADDER", "question": "q", "product_type": "APP",
                               "choices": ["Join the waitlist", "Install it", "Allow the microphone",
                                           "Use it again"]}, "LADDER", None, "CC6"),
    ("commercial.commitment", {"kind": "LADDER", "question": "q", "product_type": "APP",
                               "choices": ["Pay up front", "Install it", "Allow the microphone",
                                           "Pay for a month"]}, "LADDER", None, "CC6"),
    ("commercial.price", {"kind": "MONEY", "question": "q", "price_unit": "PER_ITEM"}, "MONEY", None, "CC7"),
    ("commercial.price", {"kind": "MONEY", "question": "q"}, "MONEY", None, "CC7"),
])
def test_keel_clouds_own_refusals_are_this_marks_faults(dimension, proposal, measure, family, rule):
    case = ChatCase("lullaby", dimension, "x", False, measure, family, "x")
    passed, why = chat_mod.one_measurable(case, BLOCKS[dimension], {"proposal": proposal})
    if dimension == "problem.importance":
        passed, why = chat_mod.importance_list(case, ["a suggested reason for crying", "listen"],
                                               {"proposal": proposal})
    assert not passed and any(w.startswith(rule) for w in why), (rule, why)


def test_money_is_money_and_payroll_is_not():
    """keel-cloud's `MONEY` has no closing word boundary, so *payroll* trips CC5 there; here it does not."""
    ok = {"kind": "EFFORT", "family": "EACH_TIME", "condition_label": "Only if it helped",
          "question": "Would you upload the payroll register every payroll run, or not?"}
    assert cc("solution.adoption_friction", ok, "EFFORT", "EACH_TIME", "effort_yes_no")[0]
    assert not chat_mod.MONEY.search("Would you keep ordering planning notes for the payroll?")
    assert chat_mod.MONEY.search("Would you pay £5 every month for it?")


def test_a_second_follow_up_is_c9_and_the_validator_does_not_yet_take_either_screen(tmp_path):
    case = ChatCase("lullaby", "problem.current_solution_satisfaction", "x", True, "TIME", None, "band_ladder")
    assert chat_mod.follow_up_budget(case, [("NEEDS_INPUT", 1), ("NEEDS_INPUT", 1)])[1][0].startswith("C9")
    tool = tmp_path / validate_mod._TOOL
    tool.parent.mkdir(parents=True)
    tool.write_text("case CALIBRATION_QUESTIONS, RESPONDENT_QUESTIONS -> b();")
    taken = validate_mod.shapes_taken(tmp_path)
    assert not taken["CALIBRATION_CHAT"] and not taken["ITEM_FEEDBACK"]
    batch = {"cases": [{"screen": "CALIBRATION_CHAT"}, {"screen": "ITEM_FEEDBACK"}, {"screen": "BRIEF"}]}
    assert "CALIBRATION_CHAT" not in validate_mod.unmet_by_screen(tmp_path, batch), \
        "their rules are restated here, so the validator's rate is not held up by them"
    assert validate_mod.own_rules_untaken(tmp_path, batch) == ["CALIBRATION_CHAT", "ITEM_FEEDBACK"]
    kept = validate_mod.without_screens(batch, validate_mod.own_rules_untaken(tmp_path, batch))
    assert [c["screen"] for c in kept["cases"]] == ["BRIEF"]
    tool.write_text("case CALIBRATION_CHAT, ITEM_FEEDBACK -> b();")
    assert validate_mod.own_rules_untaken(tmp_path, batch) == [], "the day it takes them, they are batched"
