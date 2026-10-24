"""Spec 069 (keel-cloud 130, contract 37): the harness half after 130, stackless -- the follow-up mirror and the words it
reads beside the wire (FR-1), contract 37's replaced rows (FR-2), the lock-time notes as findings (FR-3). Every served
sentence quoted here is 130's own (its tasks.md, `AfterTheRerunsOn129Test`)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from harness import interviewer_fake as fake
from harness import vectors_script as vs
from instructions import brief_facts as bf
from instructions import corpus as corpus_mod
from instructions.registry import RecallWindow
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)


def _golden(entry_id: str):
    return corpus_mod.load_file(corpus_mod.corpus_dir(KEEL_CLOUD) / f"{entry_id}.yaml", registry=fx.registry())


def _backtest(entry_id: str):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no {entry_id} at {path.parent}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


# ------------------------------------------------------------------------------- FR-1: Price's follow-up, whole

def test_the_price_follow_up_says_back_the_price_shown_the_band_or_low():
    """130 FR-7 (`FollowUpComposer.priceSaidBack`): the four cases, never *less than we asked*."""
    assert fake.price_said_back("Could you sign off on about €3,000 per hotel yourself?", "under €1,000") == \
        "You put it below €3,000. What would make it worth more?"
    assert fake.price_said_back("What would it be worth to you a month?", "under $10 a month") == \
        "You put it at under $10 a month. What would make it worth more?"
    assert fake.price_said_back("What would it be worth to you a month?", None) == \
        "You put it low. What would make it worth more?"
    assert fake.price_said_back(None, fake.WOULD_NOT_PAY_BAND) == "You put it low. What would make it worth more?"
    # the registry's words are unchanged (130 judgement call 6): the pre-rendered FOLLOW_UP clip keeps them
    assert fake.rung("commercial.price")[3] == "You put it below what we asked. What would make it worth more?"


def _price_interview(question: str, token: str = "tok") -> dict:
    options = [{"optionId": vs.option_id(token, "commercial.price", code), "label": label}
               for code, label in (("under_2", "Under $2"), ("would_not_pay", "I wouldn't pay for this"))]
    item = {"dimension": "commercial.price", "question": question, "options": options}
    return {"occasion": "night", "parts": [{"part": 3, "items": [item]}]}


def test_the_owed_price_follow_up_is_composed_whole_text_and_spoken_alike():
    """130 FR-7 on the golden walk: Lullaby's stem shows no price, so the text stays *You put it at under $2. ...* and the
    spoken line is the text (it was the registry's *below what we asked*); a stem with a price says it back; the
    would-not-pay sentence still comes first."""
    lullaby = _golden("03-lullaby")
    pick = lambda *codes: [vs.Pick(dimension="commercial.price", codes=list(codes))]  # noqa: E731
    stem = "What would something that helps at night be worth to you a month?"
    owed = vs.follow_up_question(lullaby, pick("under_2"), vs.LINK_PRIMARY, _price_interview(stem), "tok")
    assert owed["dimension"] == "commercial.price"
    assert owed["text"] == owed["spoken"] == "You put it at under $2. What would make it worth more?"
    shown = vs.follow_up_question(lullaby, pick("under_2"), vs.LINK_PRIMARY,
                                  _price_interview("Would you pay $5 a month for it?"), "tok")
    assert shown["text"] == shown["spoken"] == "You put it below $5. What would make it worth more?"
    closed = vs.follow_up_question(lullaby, pick("would_not_pay"), vs.LINK_PRIMARY, _price_interview(stem), "tok")
    assert closed["text"] == closed["spoken"] == "You said you wouldn't pay for this. What would change that?"


# ------------------------------------------------------------------------------- FR-1: the named statement, the step

def test_the_adoption_statement_names_the_idea_where_the_name_is_known():
    """130 FR-11 (T017): *{Name} means {step}. Would you do that, or not?*; no name, no named frame."""
    assert vs.adoption_statement("Pay a verified seller they have never met", "Karsa") == \
        "Karsa means paying a verified seller you have never met. Would you do that, or not?"
    assert vs.adoption_statement("you'd talk out loud to an AI tutor", "Issen") == \
        "Issen means talking out loud to an AI tutor. Would you do that, or not?"
    assert vs.gerund("you'd upload your ID card") == "uploading your ID card"
    assert vs.gerund("scan each delivery") == "scanning each delivery"
    assert vs.adoption_statement("Pay a verified seller they have never met", None) is None
    long = "you'd read and correct every single line of every drafted report before you sign it off at the end"
    assert vs.adoption_statement(long, "Code Four") is None             # past 20 words: the statement as before


def test_the_commitment_stem_introduces_a_step_the_card_never_named():
    """130 FR-10 (T018, T019): Issen's trial introduced (16 words, the opener dropped); a card that names it, no card,
    and Codyco's *a money-back pilot* (its own introduction) ask as before."""
    card = "Imagine Issen. You talk out loud to an AI tutor on your phone. It would help you speak."
    assert vs.commitment_stem("pay for one month after the trial", "Issen", card) == \
        "Issen starts with a trial. Would you pay for one month after the trial, or not?"
    assert vs.commitment_stem("pay for one month after the trial", "Issen", card + " Start with a free trial.") == \
        "If it were ready today, would you pay for one month after the trial, or not?"
    assert vs.commitment_stem("pay for one month after the trial", "Issen", None) == \
        "If it were ready today, would you pay for one month after the trial, or not?"
    assert vs.commitment_stem("pay €3,000 for a money-back pilot at one hotel", "Codyco", "Imagine Codyco.") == \
        "If it were ready today, would you pay €3,000 for a money-back pilot at one hotel, or not?"
    assert vs.commitment_stem("book the demo", "Lemma", "Imagine Lemma.") == \
        "Lemma starts with a demo. If it were ready today, would you book the demo, or not?"
    assert vs.with_article("onboarding call") == "an onboarding call"


def test_the_spoken_guard_reads_an_introduced_step_said_twice():
    """S10 reads *Would you* as it reads *would you*: an introduced step past 20 words opens its question so."""
    from instructions import spoken as sp                               # noqa: PLC0415
    from instructions.cloud_corpus import ComposedItem                  # noqa: PLC0415
    stem = "Issen starts with a trial. Would you introduce you to the tutor after the trial, or not?"
    item = ComposedItem(entry="11-issen", key="commercial.commitment", part=3, question=stem,
                        options=("Yes, I'd introduce you to the tutor", "Probably not", "No"), escape=None,
                        anchor=None, stem=stem, count_line="I'll read three options.",
                        options_line="Yes, you'd introduce you to the tutor; probably not; or no.", escape_line=None,
                        transform="none")
    assert any(f.startswith("S10") for f in sp.item_faults(item, fx.registry(), None))


# ------------------------------------------------------------------------------- FR-1: the gate's event, the lines

def test_the_gate_takes_the_occasions_event_before_the_job():
    """130 FR-6 (T001, T004): Codyco's occasion clause with its own subject, the person's own time kept; the
    circumstance cut before its negative; the job-gate is the fault, read on the wire."""
    assert vs.own_subject_event("did a booking call come in on your shift") == "a booking call come in on your shift"
    assert vs.own_subject_event("did you try to practise speaking") is None
    circumstance = ("booking calls come in on every shift, after hours, at peak and on holidays, and not every one "
                    "gets answered")
    assert vs.without_negative_clause(circumstance) == \
        "booking calls come in on every shift, after hours, at peak and on holidays"
    assert vs.without_negative_clause("they want to practise speaking the language") is None
    codyco = _backtest("21-codyco")
    assert vs.gate_asks_the_job(codyco, "In the last 7 days, did you turn every guest who calls into a booking?")
    assert not vs.gate_asks_the_job(codyco, "In the last 7 days, did a booking call come in on your shift?")


def test_the_brief_says_the_served_gate_of_them_in_the_windows_unit():
    """130 FR-6 (T003): a gate with a subject of its own reads *had {clause}* on the brief; FR-2 (T025): Frequency's
    line in the window's unit -- *months* on a 3-month window, *days* on a 7-day one, none with no gate."""
    week = RecallWindow(7, "DAYS")
    clause = bf.gate_clause_of_them("In the last 7 days, did a booking call come in on your shift?", week)
    assert clause == "had a booking call come in on their shift"
    assert bf.prevalence_line(clause, week.words()) == "had a booking call come in on their shift in the last 7 days"
    assert bf.frequency_line(clause, week) == "the middle answer · days they had a booking call come in on their shift"
    assert bf.gate_clause_of_them("In the last 7 days, did you want to practise speaking the language?", week) is None
    assert bf.gate_clause_of_them("In the last 3 months, did a call come in?", week) is None   # not this window's frame
    months = RecallWindow(3, "MONTHS")
    assert bf.frequency_line("had rupees left over", months) == "the middle answer · months they had rupees left over"
    assert bf.frequency_line(None, months) == "the middle answer"


# ------------------------------------------------------------------------------- FR-1: X12's drawn condition

def test_x12_draws_the_condition_from_the_founders_qualifier():
    """130 FR-8 (T009, T010): Issen's negative qualifier, Code Four's size, a level; a people with no qualifier none."""
    issen = "adults in the US learning a foreign language at intermediate level or above, not starting from zero"
    assert vs.drawn_condition(issen) == "are past the beginner stage"
    assert vs.condition_from("not starting from zero") == "are past the beginner stage"
    assert vs.condition_from("at intermediate level or above") == "are at intermediate level or above"
    assert vs.drawn_condition("patrol officers at US police, sheriff, transit and university departments of 10 to 200 "
                              "officers") == "work at a department with 10 to 200 officers"
    assert vs.condition_from("that bank with Mercury or Brex") == "bank with Mercury or Brex"
    assert vs.condition_from("with no foreign currency account") == "have no foreign currency account"
    assert vs.drawn_condition("reservation agents at hotel groups in Germany") is None


# ------------------------------------------------------------------------------- FR-1 / FR-2: the back-test's reading

def test_the_back_test_reads_130s_words_beside_the_mirror_as_findings():
    """Spec 069 FR-1: a served Adoption statement that does not name the idea, a gate that asks the job, a Frequency
    line in *days* on a gate with its own subject -- each a finding; the words that match are none; FR-2's replaced
    rows ride along."""
    from evals import backtest as bt                                    # noqa: PLC0415
    codyco = _backtest("21-codyco")
    lists = {"solution.adoption_friction": {"pickedIndex": 0, "items": [
                 {"label": "Let an AI answer guests in the hotel's voice",
                  "asked": "you'd let an AI agent answer guests who call"}]},
             "commercial.commitment": {"items": [{"label": "pay €3,000 for a money-back pilot at one hotel"}]}}
    gate = {"question": "In the last 7 days, did you turn every guest who calls into a booking?"}
    old = {"dimension": "solution.adoption_friction",
           "question": "You'd let an AI agent answer guests who call. Would you do that, or not?"}
    plain = {"dimension": "commercial.commitment",
             "question": "If it were ready today, would you pay €3,000 for a money-back pilot at one hotel, or not?"}
    interview = {"kind": "FULL", "reveal": {"what": "Imagine Codyco."}, "gate": gate,
                 "parts": [{"part": 2, "items": [old]}, {"part": 3, "items": [plain]}]}
    standings = {"facts": {"cards": [
        {"key": "problem.frequency", "line": "the middle answer · weeks they turned every guest into a booking"}]}}
    j = SimpleNamespace(entry=codyco, interviews={"Andreas": interview, "Bea": interview}, findings=[],
                        project=lambda path: f"/v2/projects/p{path}", get=lambda path: {"lists": lists},
                        changed={"replaced": [{"dimension": "solution.compatibility", "label": "Keel's",
                                               "replaces": "theirs"}]})
    got = bt.cloud_130(j, standings)
    assert [r["dimension"] for r in got["stems"]] == ["solution.adoption_friction"]
    assert got["stems"][0]["mirror"] == \
        "Codyco means letting an AI agent answer guests who call. Would you do that, or not?"
    assert [r["gate"] for r in got["gate_asks_the_job"]] == [gate["question"]]
    assert [(r["key"], r["rule"]) for r in got["brief_lines"]] == [("problem.frequency", "130 FR-2")]
    assert got["replaced"][0]["replaces"] == "theirs"
    assert len(j.findings) == 3
    md = bt.markdown({"changed_screens": {"cloud_130": got}, "respondents": {}, "founder_screens": []})
    assert "keel-cloud 130's words" in md and "in place of the founder's *theirs*" in md
    # 130's own words read clean: nothing to say
    named = dict(old, question=got["stems"][0]["mirror"])
    good = dict(interview, gate={"question": "In the last 7 days, did a booking call come in on your shift?"},
                parts=[{"part": 2, "items": [named]}, {"part": 3, "items": [plain]}])
    lines = {"facts": {"cards": [
        {"key": "problem.prevalence", "line": "had a booking call come in on their shift in the last 7 days"},
        {"key": "problem.frequency", "line": "the middle answer · days they had a booking call come in on their shift"}]}}
    clean = SimpleNamespace(entry=codyco, interviews={"Andreas": good}, findings=[], changed={},
                            project=lambda path: path, get=lambda path: {"lists": lists})
    assert bt.cloud_130(clean, lines) == {} and clean.findings == []
    # a stub with no wire (the 067 test's) reads nothing and raises nothing
    assert bt.cloud_130(SimpleNamespace(entry=codyco, interviews={}), None) == {}
