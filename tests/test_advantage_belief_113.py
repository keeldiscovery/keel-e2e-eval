"""Spec 113 -- the harness reads keel-cloud 173: Relative advantage's belief in one sentence, the occasion inside the
stranger's question.

FR-1 the belief is *For most, their last {occasion} would have gone better with it: {value}.* (the first benefit whole,
its leading capital dropped, a typed full stop dropped; *the last time* with no noun), and corpus revision 19's 152 words
are read through one rule (`corpus.spec173_reads`, keel-cloud's `VectorCorpusFixture.spec173Reads`), never rewritten.
FR-2 the question is *Would {idea} have made your last {occasion} go better for you, or not?*, past 20 words *Would it
have made your last {occasion} ...*; an item stored before 173 is read in 159's frame. FR-3 the spoken mirror quotes it.
FR-4 the registry slice, the drift clause *you said it would have gone better: {benefit} · ...* and the founder-lists
screen's 173 mark: one row per typed benefit, as typed, never split, none added.

Every sentence the cloud pins is pinned here as keel-cloud-docs `1acc3791`'s
`RelativeAdvantageBeliefInOneSentenceTest` writes it; a keel-cloud before 173 skips the reads of its sources by name.
"""
from __future__ import annotations

import inspect
import json
import re
import types
from pathlib import Path

import pytest
import yaml

from evals import corpus_scenario, interviewer_leg
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from instructions import run as run_mod
from instructions import screen_entries as screen_mod
from stack.config import load_config
from tests import v9_fixtures as fx

ADVANTAGE = "solution.relative_advantage"
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
REGISTRY_JSON = "src/main/resources/keel/dimension-registry.json"
GOLDEN = ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly", "06-repeatline", "07-mulchrun")
SLICE = Path(__file__).parent / "fixtures" / "registry" / "slice.yaml"
GALLERY = Path(__file__).parent / "fixtures" / "gallery" / "expected-interview-fresco.json"
PALUS = "Higher yield without hiring for treasury"


def _cloud(path: str, marker: str) -> str:
    text = (KEEL_CLOUD / path).read_text(encoding="utf-8") if (KEEL_CLOUD / path).is_file() else ""
    if marker not in text:
        pytest.skip(f"keel-cloud predates spec 173 (no {marker!r} in {path})")
    return text


def _java_string(text: str, name: str) -> str | None:
    m = re.search(rf"\b{name} = \"([^\"]*)\";", text)
    return m.group(1) if m else None


def _registry_row() -> dict:
    document = json.loads(_cloud(REGISTRY_JSON, "would have gone better with it"))
    return next(d for d in document["dimensions"] if d["key"] == ADVANTAGE)


def _entry(name: str):
    return corpus_mod.load_file(fx.canon_entry(f"{name}.yaml"), registry=fx.registry())


# ------------------------------------------------------------------------------------------- FR-1: the belief

def test_the_template_and_the_drift_template_are_the_registrys():
    """173 T001 / T004: the mirror's two templates are the exported registry row's, word for word."""
    row = _registry_row()
    assert row["founder"]["belief_template"] == corpus_mod.ADVANTAGE_BELIEF_TEMPLATE
    assert row["answers"]["drift_template"] == corpus_mod.ADVANTAGE_DRIFT_TEMPLATE


@pytest.mark.parametrize("benefit, occasion, sentence", [
    (PALUS, "cash decision",
     "For most, their last cash decision would have gone better with it: higher yield without hiring for treasury."),
    ("Missed calls turned into bookings", "booking call",
     "For most, their last booking call would have gone better with it: missed calls turned into bookings."),
    ("Following more of the conversation", "conversation",
     "For most, their last conversation would have gone better with it: following more of the conversation."),
    (PALUS, "time", "For most, the last time would have gone better with it: higher yield without hiring for treasury."),
    (PALUS, None, "For most, the last time would have gone better with it: higher yield without hiring for treasury."),
    ("IT tickets closed the same day", "week",
     "For most, their last week would have gone better with it: IT tickets closed the same day."),
    ("Higher yield without hiring for treasury.", "cash decision",
     "For most, their last cash decision would have gone better with it: higher yield without hiring for treasury."),
])
def test_the_belief_is_the_first_benefit_whole(benefit, occasion, sentence):
    """173 T002 / T003 (`BeliefSentence.benefit`, `OccasionNoun.fill`): the three entries' saved benefits, an unnamed
    occasion (*time*, none), an acronym kept, a typed full stop dropped."""
    assert corpus_mod.advantage_belief(benefit, occasion) == sentence


def test_the_drift_clause_quotes_the_benefit_bare():
    """173 T004: *you said it would have gone better: {founder} · {observed} of {n} said better, {a_lot} of them a lot*;
    `{founder}` is the sentence's `{value}`."""
    assert corpus_mod.advantage_drift_clause(PALUS, 5, 8, 3) == \
        "you said it would have gone better: higher yield without hiring for treasury · 5 of 8 said better, 3 of them a lot"


@pytest.mark.parametrize("recorded, read", [
    ("given them a shorter day", "a shorter day"),
    ("For most, it would have given them a shorter day on their last yard run.",
     "For most, their last yard run would have gone better with it: a shorter day."),
    ("For most, it would have given them a shorter day the last time.",
     "For most, the last time would have gone better with it: a shorter day."),
    ("For most, it would have made their last cash decision better.",
     "For most, it would have made their last cash decision better."),
    ("Most would move the long-term reserve out of the bank's treasury.",
     "Most would move the long-term reserve out of the bank's treasury."),
    (None, None),
])
def test_the_one_rule_reads_152s_words_as_173_writes_them(recorded, read):
    """`VectorCorpusFixture.spec173Reads`: the phrase, the named and the unnamed sentence; any other text (a back-test
    entry's pre-152 sentence, another dimension's) is returned as it is."""
    assert corpus_mod.spec173_reads(recorded) == read


def test_the_rule_is_keel_clouds():
    """The cloud's reader says the same two regexes and the same two sentences."""
    text = _cloud("src/test/java/com/keeldiscovery/cloud/corpus/VectorCorpusFixture.java", "spec173Reads")
    assert '"^For most, it would have given them (.+) on their last (.+)\\\\.$"' in text
    assert '"For most, their last " + named.group(2) + " would have gone better with it: " + named.group(1) + "."' in text
    assert '"For most, the last time would have gone better with it: " + unnamed.group(1) + "."' in text


@pytest.mark.parametrize("entry_id", GOLDEN)
def test_the_golden_record_stands_and_reads_as_the_engine_writes(entry_id):
    """FR-1: each golden entry's record keeps 152's words (never rewritten), and read through the one rule it is the
    sentence the mirror composes from the entry's first saved benefit and its occasion."""
    entry = _entry(entry_id)
    recorded = entry.founder_calibration[ADVANTAGE]
    assert recorded["belief_sentence"].startswith("For most, it would have given them ")
    assert recorded["belief_phrase"].startswith("given them ")
    first = vs.saved_list(entry, ADVANTAGE)["items"][0]["label"]
    want = corpus_mod.advantage_belief(first, vs.occasion(entry))
    assert corpus_mod.engine_belief(entry, ADVANTAGE) == want
    assert corpus_mod.spec173_reads(recorded["belief_phrase"]) == corpus_mod.advantage_benefit(first)
    other = "problem.importance"
    assert corpus_mod.engine_belief(entry, other) == entry.founder_calibration[other]["belief_sentence"]


def test_the_journey_holds_the_wire_to_the_record_read_through_the_rule():
    """FR-1 wired: the Keel-will-test box and the review rows compare the wire with `engine_belief`, not the raw
    record (else every strict journey would fail Relative advantage on 173's words)."""
    source = inspect.getsource(corpus_scenario)
    assert source.count("corpus_mod.engine_belief(j.entry, key)") == 2


# ------------------------------------------------------------------------------------------ FR-2: the question

def test_the_frames_are_scale_fours():
    text = _cloud(VECTORS + "ScaleFour.java", "FRAME_159")
    assert _java_string(text, "FRAME") == vs.BENEFIT_FRAME
    assert _java_string(text, "FRAME_159") == vs.BENEFIT_FRAME_159
    assert _java_string(text, "OLD_FRAME") == vs.BENEFIT_FRAME_085
    assert vs.BENEFIT_PLAIN_159 == "Would it have made it go better for you, or not?"


@pytest.mark.parametrize("occasion, name, question", [
    ("cash decision", "Palus", "Would Palus have made your last cash decision go better for you, or not?"),
    ("time", "Palus", "Would Palus have made the last time go better for you, or not?"),
    ("", "Palus", "Would Palus have made the last time go better for you, or not?"),
    ("booking call", "", "Would the idea have made your last booking call go better for you, or not?"),
    ("", "", "Would the idea have made the last time go better for you, or not?"),
])
def test_the_question_carries_the_occasion(occasion, name, question):
    """173 T005: the named frame, no noun (*the last time*), no name (*the idea*)."""
    assert vs.benefit_question(occasion, name) == question


def test_at_the_cap_the_name_is_kept_and_over_it_the_occasion_is():
    """173 T005: at 20 words the question names the idea; over, *Would it ...* with the occasion kept -- never 159's
    *Would {name} have made it go better ...* -- and the longest occasion (eight words) still fits."""
    at = vs.benefit_question("shift on the phones", "refill requests filed for you")
    assert len(at.split()) == vs.STEM_MAX_WORDS and at.startswith("Would refill requests filed for you ")
    over = vs.benefit_question("shift on the phones", "refill requests filed for you by text")
    assert over == "Would it have made your last shift on the phones go better for you, or not?"
    eight = "early morning delivery run across the north side"
    assert len(eight.split()) == 8
    longest = vs.benefit_question(eight, "a very long name for the idea itself")
    assert longest == vs.benefit_shortened(eight) and len(longest.split()) <= vs.STEM_MAX_WORDS
    assert eight in longest


@pytest.mark.parametrize("entry_id", GOLDEN)
def test_every_golden_question_keeps_its_occasion_within_the_cap(entry_id):
    entry = _entry(entry_id)
    asked = vs.benefit_question(vs.occasion(entry), vs.idea_name(entry))
    assert len(asked.split()) <= vs.STEM_MAX_WORDS
    assert f"your last {vs.occasion(entry)} go better for you, or not?" in asked
    assert vs.benefit_frame_of(asked) == "173"


def test_held_with_its_occasion_is_scale_fours():
    """173 T006 (`ScaleFour.heldWithItsOccasion`): a 173 stem says *it* and keeps the occasion; any other is None."""
    assert vs.benefit_held_with_its_occasion(
        "Would a filled-in daily log for the whole crew have made your last site walk go better for you, or not?") == \
        "Would it have made your last site walk go better for you, or not?"
    assert vs.benefit_held_with_its_occasion("Would Palus have made the last time go better for you, or not?") == \
        "Would it have made the last time go better for you, or not?"
    assert vs.benefit_held_with_its_occasion("On your last day, would Fresco have made it go better for you, or not?") \
        is None
    assert vs.benefit_held_with_its_occasion(None) is None


@pytest.mark.parametrize("stored, served", [
    # 173's within the cap, as stored; with a spec-120 anchor before it, the anchor kept
    ("Would Palus have made your last cash decision go better for you, or not?",
     "Would Palus have made your last cash decision go better for you, or not?"),
    ("Think of your last site walk. Would Fresco have made your last site walk go better for you, or not?",
     "Think of your last site walk. Would Fresco have made your last site walk go better for you, or not?"),
    # 173's past the cap: *it*, the occasion kept, never the plain frame
    ("Would a filled-in daily log for every one of the crew have made your last site walk go better for you, or not?",
     "Would it have made your last site walk go better for you, or not?"),
    # an item stored before 173: served in 159's words
    ("On your last cash decision, would Palus have made it go better for you, or not?",
     "On your last cash decision, would Palus have made it go better for you, or not?"),
    ("On your last day, would Fresco have made things better, or not?",
     "On your last day, would Fresco have made it go better for you, or not?"),
])
def test_a_stored_item_is_served_as_the_cloud_serves_it(stored, served):
    assert vs.served_benefit_question(stored) == served


def test_an_item_stored_before_173_past_the_cap_keeps_159s_plain_frame():
    """173 *not foreseen* 5: an old item past the cap falls to 159's plain frame -- named where the name fits."""
    stored = ("On your last shift on the phones, would refill requests filed for you have made it go better for you, "
              "or not?")
    assert vs.served_benefit_question(stored, "Issen") == "Would Issen have made it go better for you, or not?"
    assert vs.served_benefit_question(stored) == vs.BENEFIT_PLAIN_159


def test_the_gallery_keeps_its_recorded_run_read_in_159s_frame():
    """FR-2: the gallery's Fresco run (2026-10-22) recorded 085's words; the fixture is not touched, and the question
    is read in 159's frame (`ScaleFour.goBetter`), never rewritten into 173's."""
    written = json.loads(GALLERY.read_text(encoding="utf-8"))
    item = written["links"][0]["parts"][1]["items"][1]
    assert item["dimension"] == ADVANTAGE
    assert item["question"] == "On your last day, would Fresco have made things better, or not?"
    assert vs.benefit_frame_of(item["question"]) == "085"
    served = vs.served_benefit_question(item["question"])
    assert served == "On your last day, would Fresco have made it go better for you, or not?"
    assert vs.benefit_frame_of(served) == "159"
    assert served != vs.benefit_question("day", "Fresco")


def test_the_idea_name_hold_names_the_frame_it_was_served():
    """FR-2 wired: a strict journey wants 173's question; its fault says which composition the page served."""
    source = inspect.getsource(corpus_scenario._hold_the_idea_name)
    assert "vs.benefit_question(occasion, name)" in source and '"frame": vs.benefit_frame_of(served_q)' in source


# --------------------------------------------------------------------------------------- FR-3: the spoken mirror

def test_the_question_read_aloud_keeps_the_occasion():
    """FR-3: the recogniser's words of the question in 173's frame -- *or not* left off, the occasion inside."""
    said = interviewer_leg._question_words(vs.benefit_question("delivery", "an alert on mismatched deliveries"))
    assert said == "Would an alert on mismatched deliveries have made your last delivery go better for you"


# ------------------------------------------------------------------------------- FR-4: the slice and the marks

def test_the_slice_says_173s_words():
    """FR-4: the registry slice's belief template and its respondent guidance's quoted frame are the export's."""
    raw = yaml.safe_load(SLICE.read_text(encoding="utf-8"))
    row = next(d for d in raw["dimensions"] if d["key"] == ADVANTAGE)
    assert row["founder"]["belief_template"] == corpus_mod.ADVANTAGE_BELIEF_TEMPLATE
    guidance = row["respondent"]["guidance"]
    assert guidance.startswith("'Would' your idea, by its short name, 'have made your last {occasion} go better for "
                               "you, or not?'")
    assert "made it go better" not in guidance
    # the slice is hand-sized (spec 040 T002): its frame sentence is the export's, the rest its own shorter prose
    frame = guidance[:guidance.index("or not?'") + len("or not?'")]
    assert _registry_row()["respondent"]["guidance"].startswith(frame)
    assert row["founder"]["belief_template"].count("{value}") == 1
    assert fx.registry().by_key(ADVANTAGE) is not None


def test_the_benefit_limit_is_the_registrys():
    raw = yaml.safe_load(SLICE.read_text(encoding="utf-8"))
    row = next(d for d in raw["dimensions"] if d["key"] == ADVANTAGE)
    assert row["founder"]["saves"]["max_words"] == screen_mod.BENEFIT_MAX_WORDS


ROW = {"mark": "173", "dimension": ADVANTAGE, "typed": [PALUS]}


def _result(labels, **extra):
    return {"vector": "SOLUTION", "questions": [{"key": ADVANTAGE, "list": {"items": [
        {"label": label, **extra} for label in labels]}, "respondent_note": "x"}]}


def test_the_173_mark_holds_one_row_per_typed_benefit():
    """FR-4: 10-palus's Answer is one benefit with a *without* clause -- one row, as typed."""
    held = screen_mod.benefits_mark("10-palus", ROW, outcome="COMPLETED", result=_result([PALUS]))
    assert held["held"] and held["faults"] == [] and held["drafted"] == [PALUS] and held["row_words"] == [6]
    assert "173 held" in screen_mod.probe_line(held)
    # case and end punctuation aside, it is the typed benefit
    assert screen_mod.benefits_mark("10-palus", ROW, outcome="COMPLETED",
                                    result=_result(["higher yield without hiring for treasury."]))["held"]
    two = {**ROW, "typed": ["Fewer tries before the baby settles", "Sleep while keeping the light off"]}
    assert screen_mod.benefits_mark("03-lullaby", two, outcome="COMPLETED", result=_result(two["typed"]))["held"]


def test_a_benefit_past_the_limit_may_be_tidied_to_it_and_no_further():
    typed = "Hours back at the end of every single day on site for the crew"
    assert len(typed.split()) > screen_mod.BENEFIT_MAX_WORDS
    row = {**ROW, "typed": [typed]}
    assert screen_mod.benefits_mark("08-fresco", row, outcome="COMPLETED",
                                    result=_result(["Hours back at the end of every day"]))["held"]
    mark = screen_mod.benefits_mark("08-fresco", row, outcome="COMPLETED",
                                    result=_result(["Hours saved at the end of every day"]))
    assert any("is not the typed benefit" in f for f in mark["faults"]), mark["faults"]


@pytest.mark.parametrize("result, outcome, fault", [
    (_result(["Higher yield", "No hiring for treasury"]), "COMPLETED", "never split"),
    (_result([PALUS, "Less time on bank calls"]), "COMPLETED", "never split and none added"),
    (_result(["Higher yield on idle cash"]), "COMPLETED", "is not the typed benefit"),
    (_result([]), "COMPLETED", "missing or merged"),
    (_result([PALUS], suggested=True, suggested_why="x"), "COMPLETED", "Keel adds no benefit"),
    ({"vector": "SOLUTION", "questions": []}, "COMPLETED", "0 solution.relative_advantage questions"),
    (_result([PALUS]), "NEEDS_INPUT", "not COMPLETED"),
])
def test_the_173_mark_names_each_fault(result, outcome, fault):
    mark = screen_mod.benefits_mark("10-palus", ROW, outcome=outcome, result=result)
    assert not mark["held"] and any(fault in f for f in mark["faults"]), mark["faults"]


def test_two_typed_benefits_merged_into_one_row_is_a_fault():
    two = {**ROW, "typed": ["Fewer tries before the baby settles", "Sleep while keeping the light off"]}
    mark = screen_mod.benefits_mark("03-lullaby", two, outcome="COMPLETED",
                                    result=_result(["Fewer tries and sleep with the light off"]))
    assert any("missing or merged" in f for f in mark["faults"]), mark["faults"]


def _backtest_present(entry_id):
    if not (corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml").is_file():
        pytest.skip(f"keel-cloud has no back-test entry {entry_id}")


def test_the_screen_hands_10_palus_its_benefit_and_expects_one_row(tmp_path):
    """FR-4: `K=10-palus/CALIBRATION_SOLUTION/RELATIVE_ADVANTAGE` is the one redraft, handed the typed Answer *Higher
    yield without hiring for treasury*, and carries the 173 mark row; the Adoption friction redraft keeps 171's alone."""
    _backtest_present("10-palus")
    needle = "10-palus/CALIBRATION_SOLUTION/RELATIVE_ADVANTAGE"
    extras = screen_mod.load(KEEL_CLOUD, needle)
    cases = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime, needle=needle,
                                   n_runs=3)
    assert [c.case_id for c in cases] == [f"{needle}/run{n}" for n in (1, 2, 3)]
    case = cases[0]
    assert case.payload["context"]["answers"] == {ADVANTAGE: PALUS}
    assert [d["key"] for d in case.payload["context"]["dimensions"]] == [ADVANTAGE]
    assert case.meta["benefits"] == ROW and "steps" not in case.meta
    every = screen_mod.build_cases(screen_mod.load(KEEL_CLOUD, "10-palus/CALIBRATION_SOLUTION"), fx.exported(tmp_path),
                                   fx.instructions(), fx.FakeRuntime, needle="10-palus/CALIBRATION_SOLUTION", n_runs=1)
    for other in every:
        assert ("benefits" in other.meta) == (other.meta["dimension"] == ADVANTAGE)


def test_the_run_marks_the_10_palus_redraft_off_its_first_turn(tmp_path):
    """FR-4 wired: `_score_probe` writes the 173 mark into the case's diff; a split benefit fails the case."""
    _backtest_present("10-palus")
    needle = "10-palus/CALIBRATION_SOLUTION/RELATIVE_ADVANTAGE"
    extras = screen_mod.load(KEEL_CLOUD, needle)
    case = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime, needle=needle,
                                  n_runs=1)[0]
    state = run_mod._RunState()
    answer = types.SimpleNamespace(outcome="COMPLETED", result=_result([PALUS]), schema_valid=True, schema_error=None,
                                   error=None, questions=None)
    diff = run_mod._score(case, None, answer, None, state, judge=None)
    mark = run_mod._score_probe(case, answer, diff, state)
    assert mark["held"] and diff["probe"]["mark"] == "173" and diff["failed"] is None and "173 held" in diff["line"]
    split = types.SimpleNamespace(**{**vars(answer), "result": _result(["Higher yield", "No hiring for treasury"])})
    diff = run_mod._score(case, None, split, None, state, judge=None)
    run_mod._score_probe(case, split, diff, state)
    assert diff["failed"].startswith("probe: 2 rows for 1 typed benefits")
    assert [m["case_id"] for m in state.probes] == [f"{needle}/run1"] * 2
