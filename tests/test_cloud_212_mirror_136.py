"""Spec 136 -- the harness mirrors keel-cloud 212 (one event, the act that hurts; keel-cloud-docs `55bf014d`).

FR-1 the cards' one-clause lines; FR-2 the mirrors of founder-lists.md and respondent-questions.md (`wording`:
`event_max_words`, `packed_fault` E8, `routine_fault` E7; `score`: the two fields, L35, E10); FR-3 the scripted results
(`vectors_script`: `routine`, `went_wrong`, the event within the window's cap, `settled_by`, no gate `event` where the
founder's clause is held); FR-4 every golden and gallery entry's founder clause read against its window's cap -- an
entry over it a finding for the next corpus revision, named with its count, never a failure. The five entries' clauses
are cycle 11's, as keel-cloud 212's plan quotes them (`OneEventTheActThatHurtsTest`'s fixtures).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from harness import vectors_script as vs
from instructions import context as context_mod
from instructions import corpus as corpus_mod
from instructions import score as score_mod
from instructions import wording as wording_mod
from instructions.registry import RecallWindow
from quality import cards
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
GATE = "problem.prevalence"
COMPATIBILITY = "solution.compatibility"
SEVEN_DAYS = RecallWindow(7, "DAYS")
FIVE_WORKING = RecallWindow(5, "WORKING_DAYS")
GOLDEN = ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly", "06-repeatline", "07-mulchrun")


def _cloud(path: str) -> str:
    target = KEEL_CLOUD / path
    if not target.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    return target.read_text(encoding="utf-8")


def _golden(entry_id: str):
    return corpus_mod.load_file(fx.canon_entry(f"{entry_id}.yaml"), registry=fx.registry())


def _gallery(entry_id: str):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no {entry_id} at {path.parent}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


# ------------------------------------------------------------------------------------------------ FR-1 the cards

def test_the_cards_carry_the_one_clause_lines_under_prevalence_and_frequency():
    """FR-1 (keel-cloud 212 FR-5): the eval's cards, the source, say what the vendored copy says under both shapes."""
    ours = cards.CARDS_PATH.read_text(encoding="utf-8")
    prevalence, frequency = cards.card(GATE, ours), cards.card("problem.frequency", ours)
    assert "- **One clause (keel-cloud 212).** The strangers' event is the founder's clause, by code: the gate" in prevalence
    assert "`went_wrong`" in prevalence and "`routine`" in prevalence
    assert "- **One clause (keel-cloud 212).** The strangers' event is the founder's clause, by code: the founder's " \
           "Frequency" in re.sub(r"\s+", " ", frequency)
    vendored = _cloud("src/main/resources/keel/dimension-cards.md")
    for key in (GATE, "problem.frequency"):
        assert cards.card(key, vendored) == cards.card(key, ours), key


def test_the_registrys_frequency_guidance_is_212s():
    """FR-1: the registry of record's Frequency founder guidance is 212's (the 115 slice pin moved to it), and the
    gate's respondent guidance says the clause is the founder's, by code."""
    from tests.test_seven_templates_115 import (FREQUENCY_GUIDANCE_205, FREQUENCY_GUIDANCE_212,  # noqa: PLC0415
                                                FREQUENCY_GUIDANCE_216)
    rows = {d["key"]: d for d in json.loads(_cloud("src/main/resources/keel/dimension-registry.json"))["dimensions"]}
    # spec 139 FR-2 re-pin (keel-cloud 216 FR-3): 216's frame and the row's cut (216 judgement call 9)
    assert rows["problem.frequency"]["founder"]["guidance"] == FREQUENCY_GUIDANCE_216 != FREQUENCY_GUIDANCE_212 \
        != FREQUENCY_GUIDANCE_205
    assert "'On how many of {window} did you ...?': its unit said once" in rows["problem.frequency"]["respondent"][
        "guidance"]
    assert "the founder's own clause, by code (spec 212)" in rows[GATE]["respondent"]["guidance"]
    assert rows[GATE]["founder"]["guidance"].startswith("Out of 10 in the segment")
    assert "written from went_wrong" in rows[GATE]["founder"]["guidance"]


# --------------------------------------------------------------------------------------------- FR-2 the mirrors

def test_the_instructions_say_what_the_mirrors_hold():
    """FR-2: founder-lists.md's Sizes line carries the window's cap and the two fields; respondent-questions.md's gate
    is code's whole, the writer's clause only where `problem` is null."""
    lists = _cloud("src/main/resources/keel/inference-instructions/founder-lists.md")
    assert "Prevalence's `event` at most 9 words (8 on working days)" in lists
    assert "**`routine`**" in lists and "**`went_wrong`**" in lists and "**`event` from `went_wrong`**" in lists
    # spec 142 FR-3 (keel-cloud 230 FR-4): the instruction's restatement of settled_by's three values is cut (the schema's
    # enum); the values are read off `SavedList.SETTLED_BY`, the line itself stays
    assert "**`settled_by`** (Compatibility)" in lists and "one at least `nobody`" in lists
    saved = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/SavedList.java")
    values = saved.split("SETTLED_BY = java.util.List.of(", 1)[1].split(");", 1)[0]
    assert tuple(re.findall(r'"([^"]+)"', values)) == tuple(wording_mod.SETTLED_BY) == (
        "nobody", "the segment", "the usual way")
    asked = _cloud("src/main/resources/keel/inference-instructions/respondent-questions.md")
    assert "**is code's whole**" in asked and "**only where `problem` is `null`**" in asked
    assert '{"key": "problem.prevalence"}, {"key": "problem.frequency"}' in asked


@pytest.mark.parametrize("window, cap", [(RecallWindow(7, "NIGHTS"), 9), (SEVEN_DAYS, 9), (RecallWindow(4, "WEEKS"), 9),
                                         (RecallWindow(3, "MONTHS"), 9), (FIVE_WORKING, 8)])
def test_the_cap_is_the_windows_own(window, cap):
    """FR-2 (keel-cloud 212 FR-3 amended, `WindowFrame.eventMaxWords`): 9 on nights, days, weeks and months, 8 on
    working days -- the strangers' Frequency item a clause at the cap fills is 20 words exactly. Spec 139 FR-2 re-pin
    (keel-cloud 216 FR-3, the coordinator's correction): the cap is unchanged, measured on 174's frame (20 words there);
    216's frame served is a word shorter, so the question at the cap is 19."""
    assert wording_mod.event_max_words(window) == cap
    at_cap = " ".join(["act"] * cap)
    assert len(wording_mod.frequency_respondent_before216(window, at_cap).split()) == 20
    assert len(wording_mod.frequency_respondent(window, at_cap).split()) == 19


@pytest.mark.parametrize("event, went_wrong, routine, window", [
    # Fresco (cycle 12): the act that hurts (its 16 words are E2's, past 5 working days' 8 -- not E7's or E8's)
    ("had to put the day's site photos and notes into the daily log after the site walks",
     "still had the day's photos and notes to put into the log after the walks", "write the daily log", FIVE_WORKING),
    # Codyco (cycle 11): *without* is 128's negative, and the founder's clause of what went wrong stands (212 call 5)
    ("had a booking call ring out without being answered", "a booking call rang out unanswered",
     "a booking call comes in on a shift", SEVEN_DAYS),
])
def test_fresco_and_codyco_pass_e7_and_e8(event, went_wrong, routine, window):
    """FR-2 (212 FR-6): the two clauses of what went wrong are neither the routine nor packed."""
    assert wording_mod.packed_fault(event, went_wrong) is None
    assert wording_mod.routine_fault(event, routine, went_wrong, "construction superintendents") is None


@pytest.mark.parametrize("event, words", [
    ("found a conversation with hearing people too fast or too noisy to follow", "is a judgement on the act"),
    ("left cash from a raise sitting in a treasury product that paid little after fees", "says 'sitting'"),
    ("had a job fail mid-run after guessing its memory, GPUs and run time", "('after guessing')"),
    ("still had the photos to file", "says 'still had'"),
])
def test_aircaps_palus_and_expanse_are_refused_by_e8(event, words):
    """FR-2 (212 FR-6, `WindowFrame.packedFault`): a judgement, a lasting state, a cause packed in -- E8, the field
    named; *still have* only where `went_wrong` says it."""
    fault = wording_mod.packed_fault(event, "lost the thread")
    assert fault and fault.startswith(f"E8: event '{event}'") and words in fault and "went_wrong" in fault, fault
    assert wording_mod.packed_fault("still had the photos to file", "still had the photos to file after the walk") \
        is None


def test_e7_is_the_routine_and_names_both_fields():
    """FR-2 (212 FR-2, `WindowFrame.routineFault`, plan call 9): every content word of the event the routine's, in its
    base (*wrote* *write*) -- refused naming both fields; a shared noun never makes the act that hurts the routine."""
    routine, went_wrong = "write the daily log", "still had the day's photos and notes to put into the log after the walks"
    fault = wording_mod.routine_fault("wrote the daily log", routine, went_wrong, "construction superintendents")
    assert fault.startswith("E7: event 'wrote the daily log' is the routine ('write the daily log')"), fault
    assert f"('{went_wrong}'), the act that hurts" in fault
    assert wording_mod.routine_fault("had the photos left to put into the log", routine, went_wrong, None) is None
    assert wording_mod.routine_fault("wrote the daily log", routine, "", None) is None, "a blank field: E7's missing"


def test_score_holds_the_two_fields_e7_e8_and_the_cap_on_prevalence():
    """FR-2: `calibration_checks` on Prevalence -- the missing fields named, E7, E8, E2 at the window's cap."""
    gate = fx.registry().by_key(GATE)
    good = fx.calibration_question(gate)
    assert score_mod.calibration_checks(good, gate, window=SEVEN_DAYS) == []
    bare = {k: v for k, v in good.items() if k not in ("routine", "went_wrong")}
    # spec 139 FR-2 (keel-cloud 216 FR-1): with no went_wrong E9 reads only the no-sayer's own presence
    assert [f[:24] for f in score_mod.calibration_checks(bare, gate, window=SEVEN_DAYS)] == ["E7: write routine and we"]
    no_sayer = {k: v for k, v in good.items() if k != "no_sayer"}
    assert [f[:30] for f in score_mod.calibration_checks(no_sayer, gate, window=SEVEN_DAYS)] == \
        ["E9: write no_sayer beside even"]
    routine = dict(good, event="went out of the house in the morning")
    assert [f[:3] for f in score_mod.calibration_checks(routine, gate, window=SEVEN_DAYS)] == ["E7:"]
    packed = dict(good, event="lost their keys because the hook was empty")
    assert [f[:3] for f in score_mod.calibration_checks(packed, gate, window=SEVEN_DAYS)] == ["E8:"]
    long = dict(good, event="could not find their keys on the way out of the flat")
    assert score_mod.calibration_checks(long, gate, window=SEVEN_DAYS)[0].startswith("E2: the clause is 12 words; at "
                                                                                    "most 9 in the last 7 days")


def test_l35_settled_by_on_compatibility():
    """FR-2 (keel-cloud 212 FR-4, `settledRows`): every row shows its test; the suggested row is settled by nobody; a
    list settled entirely elsewhere tests nothing."""
    compat = fx.registry().by_key(COMPATIBILITY)
    rows = fx.GOOD_LISTS[COMPATIBILITY]["items"]
    assert not [f for f in score_mod.list_faults({"list": {"items": rows}}, compat) if f.startswith("L35")]
    unsaid = [{k: v for k, v in r.items() if k != "settled_by"} for r in rows]
    assert [f[:24] for f in score_mod.list_faults({"list": {"items": unsaid}}, compat) if f.startswith("L35")] == \
        ["L35: write settled_by on"] * 2
    suggested = [dict(rows[0], settled_by="the segment", suggested=True), rows[1]]
    assert [f for f in score_mod.list_faults({"list": {"items": suggested}}, compat) if f.startswith("L35")] == [
        "L35: 'They had a phone to hand' is settled by the segment, so it tests nothing; the suggested condition is one "
        "settled by nobody"]
    elsewhere = [dict(r, settled_by="the usual way") for r in rows]
    assert [f[:41] for f in score_mod.list_faults({"list": {"items": elsewhere}}, compat) if f.startswith("L35")] == \
        ["L35: every condition is settled by the se"]


# ------------------------------------------------------------------------------------ FR-3 the scripted results

@pytest.mark.parametrize("entry_id", GOLDEN)
def test_every_scripted_prevalence_is_the_act_that_hurts_within_the_cap(entry_id):
    """FR-3: the scripted CALIBRATION_QUESTIONS Prevalence carries `routine`, `went_wrong` and an `event` within the
    window's cap that passes E1-E3, E7 and E8; the strangers' clause is the founder's in the second person."""
    entry = _golden(entry_id)
    q = next(q for q in vs.calibration_result(entry, "PROBLEM")["questions"] if q["key"] == GATE)
    assert all(isinstance(q.get(f), str) and q[f].strip() for f in ("routine", "went_wrong", "event")), q
    window = context_mod.window_of(entry)
    assert len(wording_mod.clause(q["event"]).split()) <= wording_mod.event_max_words(window)
    assert wording_mod.event_fault(q["event"], window) is None
    assert wording_mod.packed_fault(q["event"], q["went_wrong"]) is None
    assert wording_mod.routine_fault(q["event"], q["routine"], q["went_wrong"],
                                     context_mod.context_of(entry).get("actor_plural")) is None
    assert score_mod.act_that_hurts(q, actor_plural=context_mod.context_of(entry).get("actor_plural")) == []
    assert len(vs.frequency_served(vs.window_of(entry), vs.event_base(entry)).split()) <= vs.STEM_MAX_WORDS
    past, base = vs.PROBLEM_CLAUSES[entry_id]
    assert q["event"] == past and base.split()[1:] == [w.replace("their", "your") for w in past.split()[1:]]


@pytest.mark.parametrize("entry_id", ("01-countly", "03-lullaby", "05-paidly"))
def test_every_scripted_compatibility_row_is_settled_by_nobody(entry_id):
    """FR-3 (keel-cloud 212 FR-4, L35): the scripted draft's conditions each carry `settled_by: nobody`."""
    entry = _golden(entry_id)
    rows = vs.drafted_list(entry, COMPATIBILITY)["items"]
    assert rows and {r["settled_by"] for r in rows} == {"nobody"}
    assert not [f for f in score_mod.list_faults({"list": {"items": rows}}, fx.registry().by_key(COMPATIBILITY))
                if f.startswith("L35")]


def test_the_scripted_gate_carries_no_event_where_the_founders_clause_is_held():
    """FR-3 (keel-cloud 212 FR-1): with the problem in scope the scripted RESPONDENT_QUESTIONS gate is its key alone;
    in a solution study (the gate the uncounted anchor, `problem` null) the writer's clause stands."""
    import dataclasses                                                  # noqa: PLC0415
    countly = _golden("01-countly")
    assert vs.respondent_result(countly, 1, vs.LINK_PRIMARY)["items"][0] == {"key": GATE}
    solution = dataclasses.replace(countly, scope="SOLUTION")
    assert not vs.gate_counts(solution) and vs.serves_gate(solution)
    assert vs.respondent_result(solution, 1, vs.LINK_PRIMARY)["items"][0] == {"key": GATE,
                                                                              "event": vs.event_base(countly)}


# --------------------------------------------------------------------------------- FR-4 the fourteen's clauses

#: FR-4's findings for the next corpus revision (keel-cloud-docs `55bf014d`, revision 24): the gallery entry's founder
#: clause -- `event_past`, *had a time when {circumstance}*, what `context.problem_of` hands the respondent job, since a
#: back-test entry records no founder clause of its own -- and its words against its window's cap. Every one of the
#: fourteen is over it: revision 24 records no `routine`, `went_wrong` or `event`, so none fits until one is written.
OVER_THE_CAP = {
    "08-fresco": (23, 8), "09-karsa": (16, 9), "10-palus": (17, 9), "11-issen": (11, 9), "12-transload": (14, 8),
    "13-aircaps": (17, 9), "14-code-four": (21, 9), "15-voltair": (24, 9), "16-pairio": (18, 8), "17-expanse": (22, 8),
    "18-careforce": (20, 8), "19-veles": (21, 9), "20-lemma": (19, 8), "21-codyco": (24, 9),
}


def _over_the_cap(entry) -> tuple[int, int] | None:
    window = context_mod.window_of(entry)
    words, cap = len(wording_mod.clause(vs.event_past(entry)).split()), wording_mod.event_max_words(window)
    return (words, cap) if words > cap else None


def test_the_golden_sevens_clauses_fit_their_windows_cap():
    """FR-4: the golden seven's clauses are the eval's own (`PROBLEM_CLAUSES`), within the cap since FR-3."""
    assert {e: _over_the_cap(_golden(e)) for e in GOLDEN} == {e: None for e in GOLDEN}


def test_the_gallerys_clauses_over_the_cap_are_findings_named_with_their_count():
    """FR-4: each gallery entry's clause read against its window's cap; an entry over it is a finding for the next
    corpus revision -- named with its count here (`OVER_THE_CAP`), never a failure of the entry, until the founder's
    word. A clause that comes to fit, or a new one over, moves this pin, so the finding is seen."""
    assert tuple(OVER_THE_CAP) == corpus_mod.GALLERY
    found = {e: _over_the_cap(_gallery(e)) for e in corpus_mod.GALLERY}
    assert {e: f for e, f in found.items() if f} == OVER_THE_CAP
