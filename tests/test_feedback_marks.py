"""Spec 046: the founder's feedback marks (`evals/feedback_marks.py`) over a record shaped like the journey's -- each met
on a good record and each failed by a fault seeded into it, so no mark is a pass that cannot fail; an absent subject
is unmeasured, never passed; the role-word rule restated against keel-cloud 097's own `RoleWords` cases and its
registry export where the checkout carries them."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from evals import corpus_scenario
from evals import feedback_marks as marks
from harness import vectors_script as vs
from stack.config import load_config

ROLE_WORDS = ["director", "manager", "CFO", "CTO", "CEO", "head", "officer", "VP", "partner", "spouse", "owner",
              "founder", "accountant", "lawyer", "HR", "finance", "legal", "procurement", "IT", "security team"]


def good() -> dict:
    """A record as S-006's journey writes one (05-paidly's words)."""
    return {
        "role_words": list(ROLE_WORDS),
        "founder_text": {"context": {"actor": "freelance translator", "job": "get paid for finished work",
                                     "circumstance": "an agency has approved the invoice",
                                     "segment": "freelance translators in the UK"},
                         "problem_seed": "Freelance translators wait about forty-five days to be paid by agencies.",
                         "solution_seed": "A platform that pays the translator within seven days.",
                         "persona_roles": ["freelance translator", "agency"]},
        "lists": [
            {"dimension": "problem.importance", "draft": "first", "items": [{"label": "Getting paid on time"}],
             "phrase": None, "answer": None},
            {"dimension": "commercial.purchase_friction", "draft": "answer",
             "items": [{"label": "The agency owner's approval"}, {"label": "Setting it up with finance"}],
             "phrase": None, "answer": "The agency owner's approval; Setting it up with finance"},
            {"dimension": "commercial.buyer_payer_alignment", "draft": "answer",
             "items": [{"label": "Nobody else", "fixed": True}, {"label": "The agency"}], "phrase": None,
             "answer": "The agency"},
        ],
        "importance": {"own": "Getting paid on time",
                       "named": ["Finding enough steady work", "Getting fair rates for work"],
                       "first_draft": ["Getting paid on time"],
                       "redraft": ["Getting paid on time", "Finding enough steady work", "Getting fair rates for work"],
                       "saved": ["Getting paid on time", "Finding enough steady work", "Getting fair rates for work"]},
        "base_query": {"PRIMARY": {"titles": ["translator"], "levels": [], "categories": [], "companySizes": []},
                       "COMMERCIAL_B2B": {"titles": ["project manager"], "levels": ["MANAGER", "DIRECTOR"],
                                          "companySizes": ["11-50"]}},
        "idea": {"seed_name": None, "served": None, "typed": "Invoice payout service",
                 "typed_name": "invoice payout service", "stored": "invoice payout service", "approved": True,
                 "refusals": {"approve": {"status": 422, "code": "IDEA_NAME_REQUIRED"},
                              "empty": {"status": 422, "code": "IDEA_NAME_REQUIRED"}},
                 "screen": {"value": "", "placeholder": marks.NAME_PLACEHOLDER, "save_enabled": False},
                 "named_on": "screen"},
        "ai_flow": {"next_presses": 0, "events": [
            {"t": 0, "kind": "phase", "value": "speaking"}, {"t": 10, "kind": "play", "clip": "a"},
            {"t": 900, "kind": "phase", "value": "listening"}, {"t": 1500, "kind": "phase", "value": "thinking"},
            {"t": 2000, "kind": "phase", "value": "speaking"}, {"t": 2100, "kind": "play", "clip": "b"}]},
        "typed_fields": [{"itemId": "abc", "typed": "200", "how": "TYPED", "heard": "200"}],
    }


def _by_mark(record: dict) -> dict:
    return {c.mark: c for c in marks.score(record)}


def test_every_mark_is_met_on_a_good_record():
    card = marks.scorecard(good())
    assert card["version"] == marks.FEEDBACK_MARKS_VERSION == 1
    assert card["measured"] == card["met"] == len(marks.MARKS) == 6, card
    assert card["unmeasured"] == []
    assert marks.owed(good()) == ["FM1", "FM2", "FM3", "FM4", "FM5", "FM6"]


@pytest.mark.parametrize("mark,key", [(m, k) for m, k, _ in marks.MARKS])
def test_an_absent_subject_is_unmeasured_and_never_passed(mark, key):
    record = good()
    del record[key]
    check = _by_mark(record)[mark]
    assert not check.measured and not check.ok
    assert mark not in marks.owed(record)


def test_fm1_fails_on_a_role_the_founder_never_named():
    record = good()
    record["lists"][1]["items"].append({"label": "The finance director's sign-off"})
    check = _by_mark(record)["FM1"]
    assert check.measured and not check.ok
    assert check.detail["unnamed"] == [{"dimension": "commercial.purchase_friction", "draft": "answer",
                                        "where": "items[2].label", "text": "The finance director's sign-off",
                                        "word": "director"}]


def test_fm1_reads_an_asked_clause_and_a_phrase_too():
    record = good()
    record["lists"].append({"dimension": "solution.compatibility", "draft": "first", "answer": None, "phrase": None,
                            "items": [{"label": "Approve it online", "asked": "could your manager approve it online"}]})
    assert _by_mark(record)["FM1"].detail["unnamed"][0]["word"] == "manager"
    record = good()
    record["lists"].append({"dimension": "problem.current_solution_satisfaction", "draft": "answer", "answer": "x",
                            "phrase": "your accountant's way of chasing", "items": []})
    assert _by_mark(record)["FM1"].detail["unnamed"][0]["where"] == "phrase"


def test_fm1_takes_the_role_from_the_founders_own_words():
    """A role in the Answer, a seed, the context or the persona is the founder's: the list may name it."""
    record = good()
    record["lists"][1]["answer"] += "; the finance director's sign-off"
    record["lists"][1]["items"].append({"label": "The finance director's sign-off"})
    assert _by_mark(record)["FM1"].ok
    record = good()
    record["founder_text"]["persona_roles"].append("HR director")
    record["lists"][1]["items"].append({"label": "The HR director's approval"})
    assert _by_mark(record)["FM1"].ok
    record = good()
    record["lists"][2]["items"][0] = {"label": "The partner", "fixed": True}
    assert _by_mark(record)["FM1"].ok, "the fixed first item is code's and is not read"


def test_role_words_match_as_keel_cloud_097_matches_them():
    """keel-cloud 097 `RoleWordsTest`'s cases, then more: whole words, plural and possessive, capitals only for acronyms,
    a two-word role across spaces; never inside another word."""
    assert marks.first_unnamed("The finance director's sign-off", ROLE_WORDS, "payroll errors at month end") == "director"
    assert marks.first_unnamed("Two directors agree", ROLE_WORDS, "the finance director signs") is None
    assert not marks.carries("Get ahead of the run", "head")
    assert not marks.carries("Ownership of the account", "owner")
    assert not marks.carries("Let it listen at night", "IT") and marks.carries("Ask IT for access", "IT")
    assert marks.carries("A partner's agreement", "partner")
    assert marks.carries("The Security  Team's review", "security team")
    assert marks.first_unnamed(None, ROLE_WORDS, "") is None and marks.first_unnamed("  ", ROLE_WORDS, "") is None
    assert marks.carries("The finance directors", "director")
    assert marks.carries("the partner's view", "partner") and marks.carries("the owners' sign-off", "owner")
    assert marks.carries("the bosses", "boss") and not marks.carries("ahead of time", "head")
    assert not marks.carries("put it in the bin", "IT") and marks.carries("the IT supplier", "IT")
    assert marks.carries("our HR team", "HR") and not marks.carries("three hrs", "HR")
    assert marks.carries("the security   team signs", "security team")
    assert not marks.carries("a security review", "security team")
    assert marks.carries("The CFO's sign-off", "CFO") and not marks.carries("the cfo", "CFO")
    assert marks.first_unnamed("The manager signs", ROLE_WORDS, "managers in kitchens") is None
    assert marks.first_unnamed("The manager and the owner", ROLE_WORDS, "the manager") == "owner"
    assert marks.first_unnamed("", ROLE_WORDS, "") is None


def test_role_words_are_keel_clouds_own_list():
    """`common.role_words` in keel-cloud's registry export is the list this file's record carries (097 call 9)."""
    keel_cloud = Path(load_config(validate=False).keel_cloud)
    path = keel_cloud / "src" / "main" / "resources" / "keel" / "dimension-registry.json"
    if not path.is_file():
        pytest.skip(f"no registry export at {path}")
    common = json.loads(path.read_text(encoding="utf-8")).get("common") or {}
    if "role_words" not in common:
        pytest.skip("this keel-cloud checkout predates 097")
    assert common["role_words"] == ROLE_WORDS == list(vs.ROLE_WORDS)


@pytest.mark.parametrize("fault,why", [
    (lambda x: x.update(first_draft=x["redraft"]), "Keel's first draft padded beyond the own item"),
    (lambda x: x["redraft"].append("Keeping up with tax admin"), "a difficulty the Answer never named"),
    (lambda x: x["redraft"].pop(), "a difficulty the Answer named, dropped"),
    (lambda x: x.update(saved=x["redraft"][:2], redraft=x["redraft"][:2], named=x["named"][:1]),
     "own + 1 saved: people pick two of three at least"),
    (lambda x: x.update(saved=list(reversed(x["saved"]))), "the saved list is not the redraft"),
    (lambda x: x.update(redraft=list(reversed(x["redraft"]))), "the own item not first"),
    (lambda x: x.update(typed=["Working to tight deadlines"]), "typed on Check, and not saved"),
])
def test_fm2_fails_on_an_invented_or_missing_difficulty(fault, why):
    record = good()
    fault(record["importance"])
    assert not _by_mark(record)["FM2"].ok, why


def test_fm2_counts_what_the_founder_typed_on_the_check_screen():
    """keel-web 070 F9: Keel's redraft is own + what the Answer named; the founder may type more on Check, and the list
    saved is both -- nothing of it Keel's own invention."""
    record = good()
    x = record["importance"]
    x.update(named=x["named"][:1], redraft=x["redraft"][:2], typed=["Getting fair rates for work"])
    assert _by_mark(record)["FM2"].ok, _by_mark(record)["FM2"].detail


def test_fm3_fails_on_an_industry_in_any_base_query():
    record = good()
    record["base_query"]["COMMERCIAL_B2B"]["categories"] = ["political organizations"]
    check = _by_mark(record)["FM3"]
    assert not check.ok and check.detail["categories"] == {"COMMERCIAL_B2B": ["political organizations"]}
    record = good()
    record["base_query"] = {}
    assert not _by_mark(record)["FM3"].ok, "no base query read is not a pass"
    record = good()
    record["base_query"]["PRIMARY"] = None
    assert not _by_mark(record)["FM3"].ok


@pytest.mark.parametrize("fault,why", [
    (lambda x: x.update(served="payment within seven days"), "Keel drafted a name"),
    (lambda x: x["refusals"].update(approve={"status": 200, "code": None}), "an unnamed idea approved"),
    (lambda x: x["refusals"].pop("empty"), "the empty name never tried"),
    (lambda x: x["screen"].update(save_enabled=True), "the screen did not demand a name"),
    (lambda x: x["screen"].update(value="payment within seven days"), "the field was not empty"),
    (lambda x: x["screen"].update(placeholder=""), "no placeholder"),
    (lambda x: x.update(typed="one two three four five six"), "over five words"),
    (lambda x: x.update(stored="payment within seven days"), "the stored name is not the typed one"),
    (lambda x: x.update(approved=False), "never approved"),
])
def test_fm4_fails_where_keel_named_the_idea_or_the_founder_did_not(fault, why):
    record = good()
    fault(record["idea"])
    assert not _by_mark(record)["FM4"].ok, why


def test_fm4_holds_a_seeds_own_name_and_needs_no_screen_on_the_wire():
    record = good()
    record["idea"] = {"seed_name": "Payroll Guard", "served": "Payroll Guard", "stored": "Payroll Guard"}
    assert _by_mark(record)["FM4"].ok
    record["idea"]["served"] = None
    assert not _by_mark(record)["FM4"].ok, "a seed with a name, served none"
    record = good()
    del record["idea"]["screen"]
    record["idea"]["named_on"] = "wire"
    assert _by_mark(record)["FM4"].ok, "the wire's refusals are the demand while S2 is not walked unnamed"


def test_fm5_fails_on_a_next_press_or_a_long_think():
    record = good()
    record["ai_flow"]["next_presses"] = 1
    assert not _by_mark(record)["FM5"].ok
    record = good()
    record["ai_flow"]["events"][-2]["t"] = 3000
    record["ai_flow"]["events"][-1]["t"] = 3100
    check = _by_mark(record)["FM5"]
    assert not check.ok and check.detail["long"] == [1600]
    record = good()
    record["ai_flow"]["events"] = record["ai_flow"]["events"][:2]
    assert not _by_mark(record)["FM5"].ok, "one clip played is no advance measured"


def test_fm5_does_not_time_the_pilot_asks_finish():
    """The pilot ask keeps *Finish* (keel-web 070 F1): the wait before it is the stranger's, not a stop of the flow."""
    record = good()
    record["ai_flow"]["events"] += [{"t": 2600, "kind": "phase", "value": "listening"},
                                    {"t": 2700, "kind": "phase", "value": "thinking"},
                                    {"t": 6000, "kind": "next", "value": "Finish"},
                                    {"t": 6050, "kind": "phase", "value": "speaking"},
                                    {"t": 6100, "kind": "play", "clip": "thanks"}]
    check = _by_mark(record)["FM5"]
    assert check.ok and check.detail["thinking spans (ms)"] == [600], check.detail


def test_fm6_fails_on_a_typed_value_without_heard():
    record = good()
    record["typed_fields"][0]["heard"] = None
    assert not _by_mark(record)["FM6"].ok
    record = good()
    record["typed_fields"][0]["how"] = "SPOKEN"
    assert not _by_mark(record)["FM6"].ok
    record = good()
    record["typed_fields"][0].update(typed="30", heard="30.0")
    assert _by_mark(record)["FM6"].ok, "the same number, written as a decimal"
    record = good()
    record["typed_fields"] = []
    assert not _by_mark(record)["FM6"].ok


def test_a_record_that_cannot_be_read_fails_measured():
    record = good()
    record["importance"] = None
    check = _by_mark(record)["FM2"]
    assert check.measured and not check.ok


def test_the_journey_builds_the_record_and_scores_it_last():
    """The journey's seam: `run` scores the feedback marks after the scenario's own extra, and the idea step names the
    idea on the wire only while `NAME_ON_THE_WIRE` stands in for keel-web 070's S2."""
    import inspect
    source = inspect.getsource(corpus_scenario.run)
    assert source.index("extra(journey)") < source.index("score_feedback(journey)")
    assert isinstance(corpus_scenario.NAME_ON_THE_WIRE, bool)
    record = copy.deepcopy(good())
    assert marks.scorecard(record)["met"] == 6
