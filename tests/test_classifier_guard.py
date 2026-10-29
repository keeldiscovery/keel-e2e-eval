"""Spec 048 FR-3: the classifier guard's machinery, stackless -- the cases copied whole from keel-cloud's canon, the
judge (keel-cloud `FakeClassifierCasesTest.matches` ported), the served items read as keel-cloud `SpokenItem.of` reads
them, and the transposition onto a link's own items, which must never change what a case means. The guard's run
against the stack's `classify` route is the AI-link leg's (`evals/interviewer_leg.py::_classifier_guard`)."""

from __future__ import annotations

import pytest

from harness import classifier_cases as cases
from harness import classifier_guard as guard
from stack.config import load_config


def test_the_cases_are_the_checks_170():
    """099's 152 and keel-cloud 100's 18 `readaloud` cases (spec 049 FR-1 / FR-8)."""
    assert (len(cases.CASES), len(cases.CONFIRM), len(guard.all_cases())) == (155, 15, 170)
    readaloud = [c for c in guard.all_cases() if c.group == "readaloud"]
    assert len(readaloud) == 18
    assert {c.item for c in readaloud} == {"gate", "better", "approval", "effort", "importance", "benefits", "cost",
                                           "days", "budget"}
    assert sum(1 for c in readaloud if c.expected == {"unclear": True}) >= 2
    assert set(cases.ITEMS) == {c.item for c in guard.all_cases()}
    for said in guard.CORRECTIONS:
        assert said in {c.said for c in guard.all_cases()}, said


def test_the_copy_is_the_canons_word_for_word_below_its_header():
    canon = load_config(validate=False).keel_cloud / "canon/designs/spoken-classifier-check-2026-10-16/cases.py"
    if not canon.is_file():
        pytest.skip("keel-cloud's canon has no spoken-classifier check (before 099)")
    ours = (guard.cases.__file__ and open(guard.cases.__file__, encoding="utf-8").read())
    assert ours.endswith(canon.read_text(encoding="utf-8")), "harness/classifier_cases.py drifted from the canon"


def _identity(case: guard.Case) -> guard.Asked:
    asked = guard.transpose(case, guard.case_item(case.item))
    assert isinstance(asked, guard.Asked), (case.name, getattr(asked, "reason", None))
    return asked


@pytest.mark.parametrize("case", guard.all_cases(), ids=lambda c: c.name[:60])
def test_a_case_asked_of_its_own_item_is_said_as_written(case):
    asked = _identity(case)
    assert asked.said == case.said.lower().replace("’", "'").strip()
    assert asked.expected == case.expected


def test_the_punctuation_the_classifier_reads_is_kept():
    for said in ("no, the second", "not the second, the fourth", "the tax one... no sorry the timesheets"):
        case = next(c for c in guard.all_cases() if c.said == said)
        assert _identity(case).said == said


PAYROLL = ["Catching errors before the payroll is approved", "Chasing missing timesheets", "Explaining payslips to staff",
           "Keeping up with tax changes", "Reconciling payroll with the ledger"]
INVOICES = ["Chasing the agency after the invoice is overdue", "Waiting weeks for remittance slips",
            "Explaining fees to clients", "Keeping track of currency changes", "Matching invoices with the agency"]


def _served(options, *, kind="multi", pick=2, escape="None of these") -> guard.Served:
    return guard.Served("item-1", "problem.importance", kind, tuple(options), escape, pick)


def test_a_case_is_carried_onto_served_labels_word_for_place():
    case = next(c for c in guard.all_cases() if c.said == "the timesheets one and the tax changes")
    asked = guard.transpose(case, _served(INVOICES))
    assert isinstance(asked, guard.Asked), asked
    words = asked.said.split()
    # "timesheets" (only label 2's) -> a word only served label 2 has; "tax", "changes" (label 4's) -> label 4's
    assert any(w in guard._sig(INVOICES[1]) for w in words) and any(w in guard._sig(INVOICES[3]) for w in words)
    assert "timesheets" not in words and "tax" not in words
    assert asked.expected == {"picks": [2, 4]}


def test_a_word_two_labels_share_needs_one_two_served_labels_share():
    case = next(c for c in guard.all_cases() if c.item == "importance" and c.said == "payroll")
    asked = guard.transpose(case, _served(INVOICES))
    # "payroll" sits in labels 1 and 5; "agency" and "invoice" sit in served 1 and 5
    assert isinstance(asked, guard.Asked) and asked.said in ("agency", "invoice"), asked
    lonely = ["Chasing the firm after the bill is overdue"] + INVOICES[1:]
    assert isinstance(guard.transpose(case, _served(lonely)), guard.NotAsked)


def test_a_served_label_said_whole_by_accident_is_not_asked():
    approval = ["Yes, with some steps", "Yes, quickly", "No", "Only with help or approval"]
    case = next(c for c in guard.all_cases() if c.item == "approval" and c.said == "no")
    got = guard.transpose(case, guard.Served("i", "solution.compatibility", "single", tuple(approval), "I can't recall"))
    assert isinstance(got, guard.NotAsked) and "whole" in got.reason


def test_a_turn_word_is_never_carried_onto_an_option():
    case = next(c for c in guard.all_cases() if c.said == "that's right")
    approval = ["Yes, with some steps", "Yes, quickly", "Mostly on my own", "Only with help or approval"]
    got = guard.transpose(case, guard.Served("i", "x", "single", tuple(approval), "I can't recall"))
    assert isinstance(got, guard.Asked) and got.said == "that's right" and got.previous == [approval[2]]


def test_shapes_must_agree():
    case = next(c for c in guard.all_cases() if c.item == "better")
    assert isinstance(guard.transpose(case, _served(PAYROLL)), guard.NotAsked)                  # multi for a single
    two = next(c for c in guard.all_cases() if c.item == "importance")
    assert isinstance(guard.transpose(two, _served(PAYROLL[:4])), guard.NotAsked)               # four, not five
    assert isinstance(guard.transpose(two, _served(PAYROLL, pick=0)), guard.NotAsked)          # pick-any


def test_a_number_on_another_range_is_asked_only_where_it_means_the_same():
    served = guard.Served("n", "problem.frequency", "number", (), None, 0, 0, 7, "times out of 7")
    by = {c.said: c for c in guard.all_cases() if c.item == "days"}
    assert isinstance(guard.transpose(by["about three, maybe four"], served), guard.Asked)
    assert isinstance(guard.transpose(by["12"], served), guard.NotAsked)                      # out of 0..7
    assert isinstance(guard.transpose(by["31"], served), guard.NotAsked)                      # unclear only over 30
    assert isinstance(guard.transpose(by["yesterday"], served), guard.NotAsked)               # a day, not a count
    assert isinstance(guard.transpose(by["three days, no wait, five"], served), guard.NotAsked)
    days = guard.Served("n", "problem.recency", "number", (), "I can't recall", 0, 0, 30, "days ago")
    assert isinstance(guard.transpose(by["three days, no wait, five"], days), guard.Asked)


def test_an_amount_said_with_no_currency_is_the_markets():
    served = guard.Served("c", "commercial.existing_sacrifice", "amount_or_hours", (), "I can't recall", currency="GBP")
    case = next(c for c in guard.all_cases() if c.said == "it cost us about five hundred")
    asked = guard.transpose(case, served)
    assert asked.expected == {"any": [{"value": 500, "unit": "AMOUNT", "currency": "GBP"}, {"unclear": True}]}
    said = next(c for c in guard.all_cases() if c.said == "two hundred dollars")
    assert guard.transpose(said, served).expected["currency"] == "USD"


def test_served_items_read_as_spoken_item_of():
    interview = {"gate": {"itemId": "g", "dimension": "problem.recency", "question": "Did it happen?"},
                 "parts": [{"part": 1, "items": [
                     {"itemId": "a", "dimension": "problem.importance", "control": "pick_two",
                      "options": [{"optionId": "o1", "label": "One"}, {"optionId": "o2", "label": "Two"}],
                      "escape": {"code": "NONE_OF_THESE", "label": "None of these"}},
                     {"itemId": "b", "dimension": "problem.frequency", "control": "segmented_0_to_7",
                      "scale": {"min": 0, "max": 7}, "escape": None},
                     {"itemId": "c", "dimension": "problem.frequency", "control": "number_with_unit",
                      "numeric": {"defaultUnit": "months out of 3"}, "escape": None},
                     # spec 089 FR-4 (keel-cloud 159): the scale is one single ask -- no advantages ask after it
                     {"itemId": "d", "dimension": "solution.relative_advantage", "control": "scale_four",
                      "options": [{"optionId": "x", "label": "A lot better"}, {"optionId": "y", "label": "Worse"}],
                      "escape": {"label": "I can't tell"}},
                     {"itemId": "e", "dimension": "commercial.existing_sacrifice", "control": "cost_total",
                      "costTotal": {"currency": "GBP"}, "escape": {"label": "I can't recall"}}]}]}
    got = guard.served_items(interview)
    assert [(s.item_id, s.kind, s.pick, s.ask) for s in got] == [
        ("g", "gate", 0, None), ("a", "multi", 2, None), ("b", "number", 0, None), ("c", "number", 0, None),
        ("d", "single", 0, None), ("e", "amount_or_hours", 0, None)]
    assert (got[2].low, got[2].high, got[3].low, got[3].high) == (0, 7, 0, 3)
    assert got[5].currency == "GBP" and got[1].escape == "None of these" and got[0].options == ("Yes", "No")


def _got(**kw) -> dict:
    base = {"picks": [], "escape": False, "value": None, "unit": None, "currency": None, "confidence": "high",
            "runnerUp": None, "agree": False, "unclear": False, "reason": ""}
    return {**base, **kw}


def test_the_judge_reads_right_safe_and_wrong():
    item = guard.case_item("importance")
    asked = guard.Asked(guard.all_cases()[0], item, "x", None, {"picks": [2, 4]})
    assert guard.verdict(asked, _got(picks=[item.options[3], item.options[1]])) == "right"
    assert guard.verdict(asked, _got(picks=[item.options[1]], confidence="medium")) == "safe"
    assert guard.verdict(asked, _got(unclear=True, confidence="low")) == "safe"
    assert guard.verdict(asked, _got(picks=[item.options[0], item.options[1]])) == "wrong"
    unclear = guard.Asked(guard.all_cases()[0], item, "payroll", None, {"unclear": True})
    assert guard.verdict(unclear, _got(picks=[item.options[0]], confidence="medium")) == "safe"
    assert guard.verdict(unclear, _got(picks=[item.options[0]])) == "wrong"
    agree = guard.Asked(guard.all_cases()[0], item, "yes", [item.options[3]], {"agree": True})
    assert guard.verdict(agree, _got(agree=True)) == "right"
    cost = guard.Asked(guard.all_cases()[0], guard.case_item("cost"), "x", None,
                       {"value": 200, "unit": "AMOUNT", "currency": "USD"})
    assert guard.verdict(cost, _got(value=200, unit="AMOUNT", currency="USD")) == "right"
    assert guard.verdict(cost, _got(value=200, unit="AMOUNT", currency="GBP")) == "wrong"


def test_run_sends_each_case_once_and_counts():
    served = [guard.case_item(k) for k in cases.ITEMS]
    sent: list[dict] = []

    def post(body: dict) -> tuple[int, dict]:
        sent.append(body)
        return 200, _got(unclear=True, confidence="low")

    report = guard.run(post, served)
    unclear = [c for c in guard.all_cases() if guard.matches(guard.case_item(c.item), c.expected, _got(unclear=True))]
    assert len(sent) == 170 and not report.wrong and not report.skipped
    assert (report.count("right"), report.count("safe")) == (len(unclear), 170 - len(unclear))
    groups = report.groups()
    assert groups["readaloud"]["asked"] == 18 and groups["confirm"]["asked"] == 15
    assert sum(g["asked"] for g in groups.values()) == 170 and not any(g["wrong"] for g in groups.values())
    assert all(set(b) <= {"itemId", "heard", "language", "previous", "ask"} for b in sent)
    assert sum(1 for b in sent if b.get("previous")) == 14            # the confirmation turn on days holds no option
    with pytest.raises(ValueError, match="over the"):
        guard.run(post, served, limit=100)


def test_the_live_budget_holds_what_a_link_can_ask():
    """Spec 049 judgement call: the ceiling stays $0.10 (spec 048 FR-2). 170 cases at $0.0006 would be $0.102, but the
    live check asks only the cases its link's items can carry (048 measured 83 and 119 on the corpus links) and is
    refused by name before the first call when the plan would pass the ceiling (`run(limit=...)`), never overspent."""
    calls = int(guard.LIVE_BUDGET_USD / guard.COST_PER_CALL_USD)
    assert calls == 166 and len(guard.all_cases()) - calls == 4
    assert len([c for c in guard.all_cases() if c.group != "readaloud"]) * guard.COST_PER_CALL_USD < guard.LIVE_BUDGET_USD


def test_the_fakes_reasons_are_its_own():
    """`FAKE_REASONS` against keel-cloud's FakeClassifier and validators, where the checkout carries them: every reason
    literal they write is known, so a live run answered by the fake is told apart from one the model answered."""
    import re                                                             # noqa: PLC0415
    root = load_config(validate=False).keel_cloud / "src/main/java/com/keeldiscovery/cloud"
    files = [root / "infrastructure/interviewer/FakeClassifier.java", root / "application/interviewer/Classification.java"]
    if not all(f.is_file() for f in files):
        pytest.skip("keel-cloud has no FakeClassifier (before 099)")
    calls = re.compile(r"\b(?:valued|picked|unclear|escaped|agreed|hours|settle|withOrdinals)\(|new Read\(|\.at\(")
    written: set[str] = set()
    for f in files:
        source = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", f.read_text(encoding="utf-8"), flags=re.S))
        for statement in source.split(";"):
            if "return" in statement and calls.search(statement):
                written |= set(re.findall(r'"([^"]*)"', statement))
    # the words the same statements match on, never a reason
    words = {"a", "all", "an", "and", "day", "each", "every", "full", "half", "hour", "not all", "one", "whole"}
    unknown = sorted(r for r in written - words if not guard.fake_reason(r) and not re.search(r"[?|]", r))
    assert not unknown, unknown
    assert "yes or no" in written and "two labels fit" in written, sorted(written)
    if "read aloud first" in " ".join(written):                         # keel-cloud 100's rules are in the checkout
        assert {"yes and no heard", "read the options aloud, settled on none", "read aloud first"} <= written
    report = guard.Report(outcomes=[guard.Outcome(None, 200, {"reason": "two labels fit"}, "safe")])
    assert report.answered_by_fake
    report.outcomes.append(guard.Outcome(None, 200, {"reason": "correction: timesheets replaces tax"}, "right"))
    assert not report.answered_by_fake


def test_a_run_the_model_never_answered_is_told_apart():
    failed = guard.Report(outcomes=[guard.Outcome(None, 200, {"reason": r, "unclear": True}, "safe")
                                    for r in ("timeout", "vendor")])
    assert failed.model_never_answered and not failed.answered_by_fake
    failed.outcomes.append(guard.Outcome(None, 200, {"reason": "two labels fit"}, "safe"))
    assert not failed.model_never_answered
