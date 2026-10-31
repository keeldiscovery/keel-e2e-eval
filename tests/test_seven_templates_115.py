"""Spec 115 -- the harness reads keel-cloud 174: the seven template and frame rules.

FR-0 revision 19's Purchase friction `cant_recall` is read as 174's `cant_tell` through one rule
(`corpus.spec174_escape`), never rewritten; the walk sends the code served. FR-1 the registry slice, the belief mirrors
(`corpus.spec174_reads`, keel-cloud's `VectorCorpusFixture.spec174Reads`), the fact four and the fact said back. FR-2
Frequency's frames -- the unit kept and counted as it is, a two-word unit said once more short, *Say a number from 1 to
N.* past five steps. FR-3 the *Only if* follow-up, mirrored beside the ladder. FR-4 the gallery fixtures stay in their
recorded frame.

Every sentence the cloud pins is pinned here as keel-cloud-docs `e68c0de4` writes it (`FrequencyKeepsItsUnitTest`,
`CommitmentNamesTheDeciderTest`, `OnlyIfAsksForTheEventTest`, ...); a keel-cloud before 174 skips the reads of its
sources by name.
"""
from __future__ import annotations

import dataclasses
import inspect
import json
import re
import types
from pathlib import Path

import pytest
import yaml

from evals import corpus_scenario, scope_journey
from harness import interviewer_fake as fake
from harness import vectors_script as vs
from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from instructions import registry as registry_mod
from instructions import spoken as spoken_mod
from instructions import wording as wording_mod
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
FIXTURE = "src/test/java/com/keeldiscovery/cloud/corpus/VectorCorpusFixture.java"
COMPOSER = "src/main/java/com/keeldiscovery/cloud/application/FollowUpComposer.java"
REGISTRY_JSON = "src/main/resources/keel/dimension-registry.json"
SLICE = Path(__file__).parent / "fixtures" / "registry" / "slice.yaml"
FRESCO_RUN = Path(__file__).parent / "fixtures" / "gallery" / "20261022T164045Z-backtest-08-fresco" / "export"
FRICTION = "commercial.purchase_friction"
COMMITMENT = "commercial.commitment"
COMPATIBILITY = "solution.compatibility"
IMPORTANCE = "problem.importance"
ADOPTION = "solution.adoption_friction"
#: 174's four entries the reader refused on master (`instructions.corpus` under the exported registry).
REFUSED = ("05-paidly", "10-palus", "17-expanse", "21-codyco")


def _cloud(path: str, marker: str) -> str:
    text = (KEEL_CLOUD / path).read_text(encoding="utf-8") if (KEEL_CLOUD / path).is_file() else ""
    if marker not in text:
        pytest.skip(f"keel-cloud predates spec 174 (no {marker!r} in {path})")
    return text


def _exported():
    _cloud(REGISTRY_JSON, "can slow or stop the purchase")
    return cloud_mod.registry_of_record(KEEL_CLOUD)


def _rows() -> dict:
    document = json.loads(_cloud(REGISTRY_JSON, "can slow or stop the purchase"))
    return {d["key"]: d for d in document["dimensions"]}


def _golden(entry_id: str, registry=None):
    return corpus_mod.load_file(fx.canon_entry(f"{entry_id}.yaml"), registry=registry or fx.registry())


def _backtest(entry_id: str, registry=None):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {path}")
    return corpus_mod.load_file(path, registry=registry or fx.registry(), backtest=True)


def _entry(entry_id: str, registry=None):
    return _golden(entry_id, registry) if entry_id[:2] < "08" else _backtest(entry_id, registry)


# ------------------------------------------------------------------------------- FR-0: the escape, one rule

@pytest.mark.parametrize("key, recorded, read", [
    (FRICTION, "cant_recall", "cant_tell"),
    (FRICTION, "CANT_RECALL", "CANT_TELL"),             # the walk's upper case kept
    (FRICTION, "cant_tell", "cant_tell"),
    (FRICTION, "rather_not_say", "rather_not_say"),
    ("problem.frequency", "cant_recall", "cant_recall"),  # Frequency's escape did not move
    ("problem.current_solution_satisfaction", "cant_recall", "cant_recall"),
    (FRICTION, None, None),
])
def test_the_one_rule_reads_purchase_frictions_cant_recall_alone(key, recorded, read):
    assert corpus_mod.spec174_escape(key, recorded) == read
    assert corpus_mod.SPEC174_ESCAPES == {FRICTION: {"cant_recall": "cant_tell"}}


def test_the_recorded_escape_is_the_registrys_before_and_after_174():
    """Rules R and A read the record through the rule: revision 19's `cant_recall` is the registry's own before 174 and
    reads `cant_tell` after it; a recorded `cant_tell` under a registry before 174 is still refused."""
    assert corpus_mod.recorded_escape_is(FRICTION, "cant_recall", "cant_tell")
    assert corpus_mod.recorded_escape_is(FRICTION, "cant_recall", "cant_recall")
    assert not corpus_mod.recorded_escape_is(FRICTION, "cant_tell", "cant_recall")
    assert not corpus_mod.recorded_escape_is("problem.frequency", "cant_recall", "cant_tell")


@pytest.mark.parametrize("entry_id", REFUSED)
def test_the_four_refused_entries_read_under_the_exported_registry_and_the_record_is_unchanged(entry_id):
    """The four master refused (174 moved the escape): each now loads against keel-cloud's own registry, and its file
    still records `cant_recall` on Purchase friction -- the record is never rewritten."""
    registry = _exported()
    entry = _entry(entry_id, registry)
    assert entry.respondent_questions[FRICTION]["escape"] == "cant_recall"
    assert "escape: cant_recall" in entry.path.read_text(encoding="utf-8")
    assert registry.by_key(FRICTION).escape["code"] == "cant_tell"
    assert corpus_mod.spec174_escape(FRICTION, entry.respondent_questions[FRICTION]["escape"]) == "cant_tell"


def test_every_entry_reads_under_the_exported_registry():
    registry = _exported()
    golden = corpus_mod.load(KEEL_CLOUD, registry=registry)
    backtest = corpus_mod.load(KEEL_CLOUD, registry=registry, backtest=True)
    recorded = [e.id for e in golden.entries + backtest.entries
                if (e.respondent_questions.get(FRICTION) or {}).get("escape") == "cant_recall"]
    assert set(REFUSED) <= set(recorded)
    assert not [e.id for e in golden.entries + backtest.entries
                if (e.respondent_questions.get(FRICTION) or {}).get("escape") == "cant_tell"], "no revision cut"


def test_a_recorded_purchase_friction_chip_is_walked_as_cant_tell():
    """Transload's one chip on Purchase friction (`{chip: cant_recall}`) is read through the rule: the person the walk
    builds carries `CANT_TELL`, the code keel-cloud 174 serves."""
    transload = _backtest("12-transload")
    raw = [p for p in transload.answers if ((p.get("picks") or {}).get(FRICTION) or {}) == {"chip": "cant_recall"}]
    assert raw, "the record keeps its chip"
    walked = {p.person: p for p in vs.person_inputs(transload)}
    for person in raw:
        chips = [k.chip for k in walked[person["person"]].picks if k.dimension == FRICTION]
        assert chips == ["CANT_TELL"]


def _friction_person(chip: str):
    return vs.PersonInputs(person="Ray Castellano", link=vs.LINK_B2B, recency=True, story="x", anchor_chip=None,
                           picks=[vs.Pick(dimension=FRICTION, chip=chip),
                                  vs.Pick(dimension=COMMITMENT, codes=["yes_start"])],
                           pilot_opt_in=False, anchoring="ANCHORED")


def test_the_walk_sends_purchase_frictions_served_code():
    """FR-0's other half: a 174 build serves `CANT_TELL` -- nothing moves, nothing is named; a build before 174 serves
    `CANT_RECALL` -- sent as served, and named."""
    person = _friction_person("CANT_TELL")
    assert vs.served_escape_picks(person, {FRICTION: {"escape": {"code": "CANT_TELL", "label": "I can't tell"}}}) == \
        (person, [])
    before, notes = vs.served_escape_picks(person, {FRICTION: {"escape": {"code": "cant_recall",
                                                                          "label": "I can't recall"}}})
    assert [p.chip for p in before.picks] == ["CANT_RECALL", None]
    assert before.picks[1] == person.picks[1]
    assert notes == ["Ray Castellano: Purchase friction's escape is served as \"I can't recall\" (a build before "
                     "keel-cloud 174); the walk's cant_tell is sent as cant_recall, the code served (spec 115 FR-0)"]
    assert before.response("tok")["answers"][0] == {"itemId": vs.item_id("tok", FRICTION), "chip": "CANT_RECALL"}
    # nothing served, or an escape that is neither of the two: unchanged
    assert vs.served_escape_picks(person, {}) == (person, [])
    assert vs.served_escape_picks(_friction_person("RATHER_NOT_SAY"),
                                  {FRICTION: {"escape": {"code": "CANT_TELL"}}})[1] == []


def test_current_solutions_re_expression_stands_beside_it():
    person = dataclasses.replace(_friction_person("CANT_TELL"), picks=[
        vs.Pick(dimension=vs.CURRENT_SOLUTION_KEY, chip="SOMEONE_ELSE_CHECKS"),
        vs.Pick(dimension=FRICTION, chip="CANT_TELL")])
    moved, notes = vs.served_escape_picks(person, {
        vs.CURRENT_SOLUTION_KEY: {"escape": {"code": "cant_recall", "label": "I can't recall"}},
        FRICTION: {"escape": {"code": "CANT_TELL", "label": "I can't tell"}}})
    assert [p.chip for p in moved.picks] == ["CANT_RECALL", "CANT_TELL"]
    assert len(notes) == 1 and "Current solution" in notes[0]


def test_the_leg_records_the_escape_served_for_the_dimension_the_note_names():
    source = inspect.getsource(corpus_scenario._answer_one)
    assert "vs.served_escape_picks(person, items)" in source
    assert 'note.startswith(f"{person.person}: Purchase friction")' in source


# ------------------------------------------------------------------------------ FR-1: the slice and the mirrors

@pytest.mark.parametrize("key, side, field", [
    ("problem.frequency", "founder", "guidance"),
    (IMPORTANCE, "founder", "belief_template"),
    (COMPATIBILITY, "founder", "belief_template"),
    (FRICTION, "founder", "belief_template"),
    (FRICTION, "respondent", "escape"),
    (FRICTION, "respondent", "option_rule"),
    (COMMITMENT, "founder", "belief_template"),
    (COMMITMENT, "founder", "belief_template_decider"),
])
def test_the_slice_says_174s_words(key, side, field):
    rows = _rows()
    sliced = {d["key"]: d for d in yaml.safe_load(SLICE.read_text(encoding="utf-8"))["dimensions"]}
    assert sliced[key][side][field] == rows[key][side][field]


def test_the_slice_holds_174s_words_and_its_invariants():
    registry = fx.registry()
    assert registry.by_key(FRICTION).escape == {"code": "cant_tell", "label": "I can't tell", "counts": "apart"}
    assert "did a typical {actor} ...?" in registry.by_key("problem.frequency").founder["guidance"]
    assert registry.by_key(COMMITMENT).founder["belief_template_decider"] == corpus_mod.COMMITMENT_DECIDER_TEMPLATE


def test_invariant_4_holds_the_decider_template_to_one_value(tmp_path):
    raw = yaml.safe_load(SLICE.read_text(encoding="utf-8"))
    row = next(d for d in raw["dimensions"] if d["key"] == COMMITMENT)
    row["founder"]["belief_template_decider"] = "In most cases {decider} would act now."
    bad = tmp_path / "slice.yaml"
    bad.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    with pytest.raises(Exception, match="decider template carries it 0 times"):
        registry_mod.load(bad)


def test_the_four_templates_are_the_registrys():
    rows = _rows()
    assert rows[COMMITMENT]["founder"]["belief_template_decider"] == corpus_mod.COMMITMENT_DECIDER_TEMPLATE
    assert rows[FRICTION]["founder"]["belief_template"] == corpus_mod.FRICTION_BELIEF_TEMPLATE
    assert rows[COMPATIBILITY]["founder"]["belief_template"] == corpus_mod.COMPATIBILITY_BELIEF_TEMPLATE
    assert rows[IMPORTANCE]["founder"]["belief_template"] == corpus_mod.IMPORTANCE_BELIEF_TEMPLATE


def test_the_rule_is_the_clouds_own():
    """`spec174_reads` is `VectorCorpusFixture.spec174Reads`, its four patterns and sentences read off the source."""
    text = _cloud(FIXTURE, "spec174Reads")
    body = text[text.index("public static String spec174Reads("):]
    body = body[:body.index("\n    }\n")]
    assert '"^Most .+? would (.+) now\\\\.$"' in body and '"In most cases "' in body and '" now."' in body
    assert '" can slow or stop the purchase."' in body and '" slows the purchase most."' in body
    assert '"For most, "' in body and '"For most " + ' in body
    assert '" things that are hard when "' in body and '" is one of the two they would most like "' in body
    assert "spec173Reads(" in body


@pytest.mark.parametrize("entry_id, key, recorded, read", [
    ("05-paidly", COMMITMENT, "Most freelance translators working for agencies would start a read-only trial now.",
     "In most cases the agency would start a read-only trial now."),
    ("05-paidly", FRICTION, "The agency owner's approval slows the purchase most.",
     "The agency owner's approval can slow or stop the purchase."),
    ("03-lullaby", COMPATIBILITY, "For most, their phone was within reach of the cot.",
     "For most parents of babies under six months, their phone was within reach of the cot."),
    ("03-lullaby", IMPORTANCE, "Of these five, knowing what the cry means is one of the two that parents of babies under "
     "six months would most like made easier when the baby cries in the night.",
     "Parents of babies under six months have five things that are hard when the baby cries in the night. Knowing what "
     "the cry means is one of the two they would most like made easier."),
    # a same-person study keeps the people's sentence (174 T002: 13-aircaps, here Lullaby)
    ("03-lullaby", COMMITMENT, "Most parents of babies under six months would allow it to use the microphone at night "
     "now.", "Most parents of babies under six months would allow it to use the microphone at night now."),
    # a back-test founder's own words are not 152's sentence: as recorded
    ("21-codyco", COMMITMENT, "Most are open to pay €3,000 for a money-back pilot at one hotel now.",
     "Most are open to pay €3,000 for a money-back pilot at one hotel now."),
    ("21-codyco", FRICTION, "A data protection review of guest calls slows the purchase most.",
     "A data protection review of guest calls can slow or stop the purchase."),
])
def test_the_record_reads_as_the_engine_writes(entry_id, key, recorded, read):
    entry = _entry(entry_id)
    assert entry.founder_calibration[key]["belief_sentence"] == recorded, "never rewritten"
    assert corpus_mod.spec174_reads(entry, key) == corpus_mod.engine_belief(entry, key) == read


def test_a_row_174_did_not_move_reads_as_recorded_and_173_still_reads_first():
    lullaby = _golden("03-lullaby")
    key = "problem.current_solution_satisfaction"
    assert corpus_mod.engine_belief(lullaby, key) == lullaby.founder_calibration[key]["belief_sentence"]
    advantage = "solution.relative_advantage"
    assert corpus_mod.engine_belief(lullaby, advantage) == \
        corpus_mod.spec173_reads(lullaby.founder_calibration[advantage]["belief_sentence"])
    assert corpus_mod.spec174_reads(types.SimpleNamespace(founder_calibration={}), FRICTION) is None


@pytest.mark.parametrize("role, said", [
    ("agency", "the agency"), ("the hotel group revenue director", "the hotel group revenue director"),
    ("CEO", "the CEO"), ("HR manager", "the HR manager"), ("Priya", "Priya"), ("their manager", "their manager"),
])
def test_the_decider_takes_the(role, said):
    """`BeliefSentence.the` (145 FR-2): a capitalised name kept, an acronym-led role takes *the*."""
    assert corpus_mod.belief_the(role) == said


def test_every_b2b_golden_commitment_names_the_decider():
    for entry_id in ("05-paidly", "06-repeatline", "07-mulchrun"):
        entry = _golden(entry_id)
        read = corpus_mod.engine_belief(entry, COMMITMENT)
        assert entry.b2b() and read.startswith(f"In most cases {corpus_mod.belief_the(entry.decision_maker_role())} "
                                               "would ") and read.endswith(" now."), read


def test_the_importance_box_counts_in_174s_first_sentence():
    belief = ("Parents of babies under six months have three things that are hard when the baby cries in the night. "
              "Knowing what the cry means is one of the two they would most like made easier.")
    assert corpus_scenario.importance_count(belief) == corpus_scenario.importance_count_words("three") == \
        "have three things that are hard"
    assert corpus_scenario.importance_count("Of these three, knowing ...") == "Of these three, knowing ..."
    assert corpus_scenario.importance_count(None) is None
    source = inspect.getsource(corpus_scenario._importance_needs_three)
    assert "corpus_mod.engine_belief(j.entry, key)" in source and "Of these three," not in source


def test_the_money_seed_says_174s_words():
    assert scope_journey.FRICTION["belief_sentence"] == "Setting it up with the POS provider can slow or stop the purchase."
    assert scope_journey.B2B_QUESTIONS[FRICTION]["escape"] == "cant_tell" == \
        fx.registry().by_key(FRICTION).escape["code"]


def test_the_fact_four_are_the_registrys_and_128s_are_kept_for_stored_items():
    registry = fx.registry()
    four = [a["label"] for a in registry.by_key(COMPATIBILITY).fixed_answers]
    assert list(spoken_mod.FACT_ANSWERS.values()) == four
    assert list(spoken_mod.FACT_ANSWERS) == list(spoken_mod.FACT_ANSWERS_128) == registry.by_key(
        COMPATIBILITY).fixed_answer_codes
    assert list(spoken_mod.FACT_ANSWERS_128.values()) == ["Yes", "Mostly", "Partly", "No"]
    labels = spoken_mod.served_labels(registry, COMPATIBILITY)
    assert set(four) | set(spoken_mod.ABILITY_ANSWERS.values()) | {"Mostly", "Partly"} <= set(labels)


def test_the_fact_labels_mirror_item_frames():
    text = _cloud(VECTORS + "ItemFrames.java", "a fact takes the registry's own four")
    assert "if (permission(condition) || fact(condition)) {" in text
    assert re.search(r'FACT_LABELS = java\.util\.Map\.of\("yes_easily", "Yes",\s*"yes_with_steps", "Mostly", '
                     r'"only_with_help", "Partly", "no", "No"\);', text)
    for word in spoken_mod.PERMISSION_WORDS:
        assert f'"{word}"' in text, word
    assert "FACT_HEADS = java.util.Set.of(" in text and all(f'"{h}"' in text for h in spoken_mod.FACT_HEADS)


@pytest.mark.parametrize("asked, label, fact", [
    ("was your phone within reach when the baby started crying", "Their phone was within reach of the cot", True),
    ("was your job's source code on the cluster alongside your submission script", "The source code sat on the cluster",
     True),
    ("was your phone with you and connected to the internet", "Their phone was with them and online", True),
    ("did your terminal's cameras already cover the doors where your crew scanned freight",
     "Cameras already covered the doors where freight was scanned", True),
    ("did you have a bank account in your own name that you could use", "They have a bank account in their own name",
     True),
    ("could you talk over the noise on site", "They could talk over the noise on site", False),
    ("could the agency have approved your invoice on a payment platform", "The agency could approve it on a platform",
     False),
    ("would you have been allowed to upload payroll data", "They are allowed to upload payroll data", False),
])
def test_a_fact_is_read_off_both_faces(asked, label, fact):
    """`ItemFrames.fact(asked, label)`, what the follow-up reads since 174 serves a fact the registry's four."""
    assert spoken_mod.is_fact(asked, label) is fact


def _compatibility(entry, code, labels):
    question = "On your last night, was your phone within reach when the baby started crying?"
    interview = {"occasion": "night", "parts": [{"part": 2, "items": [{
        "dimension": COMPATIBILITY, "question": question,
        "options": [{"optionId": vs.option_id("tok", COMPATIBILITY, c), "label": l} for c, l in labels.items()]}]}]}
    return vs.follow_up_question(entry, [vs.Pick(dimension=COMPATIBILITY, codes=[code])], vs.LINK_PRIMARY, interview,
                                 "tok")


def test_a_fact_is_said_back_as_the_fact_on_the_registrys_four():
    """174 FR-3 (T012): Lullaby's fact on the registry's four -- the third said as picked, *No* as *no to this*."""
    lullaby = _golden("03-lullaby")
    four = spoken_mod.FACT_ANSWERS
    third = _compatibility(lullaby, "only_with_help", four)
    assert third["text"] == third["spoken"] == ("You said only with help or approval: your phone was within reach of "
                                                "the cot. What got in the way?")
    assert len(third["text"].split()) <= spoken_mod.STEM_MAX_WORDS
    no = _compatibility(lullaby, "no", four)
    assert no["text"] == "You said no to this: your phone was within reach of the cot. What got in the way?"
    # an item stored before 174 keeps 128's Partly
    partly = _compatibility(lullaby, "only_with_help", spoken_mod.FACT_ANSWERS_128)
    assert partly["text"] == ("You said only partly to this: your phone was within reach of the cot. What got in the "
                              "way?")


def test_the_fact_said_back_is_the_composers():
    text = _cloud(COMPOSER, "lockFact(lock, dimension)")
    assert '"You said no to this: "' in text and '"You said only partly to this: "' in text
    assert '"You said " + lower(pick) + ": "' in text and '". What got in the way?"' in text
    assert vs.fact_said_back("no", "No", "x") == "You said no to this: x. What got in the way?"
    assert vs.fact_said_back("only_with_help", "Only with help or approval", "x") == \
        "You said only with help or approval: x. What got in the way?"
    assert vs.fact_said_back("only_with_help", None, "x") == "You said only partly to this: x. What got in the way?"


# ----------------------------------------------------------------------------------------- FR-2: Frequency

PALUS = "leave raised cash sitting in your bank's money market fund"
THREE_MONTHS = vs.Window(3, "MONTHS")
FIVE_WORKING_DAYS = vs.Window(5, "WORKING_DAYS")


def test_palus_keeps_its_unit_at_and_past_the_cap():
    """`FrequencyKeepsItsUnitTest.palusKeepsItsUnitAtAndPastTheCap`, sentence for sentence."""
    whole = vs.frequency_served(THREE_MONTHS, PALUS)
    assert whole == ("In the last 3 months, in how many months did you leave raised cash sitting in your bank's money "
                     "market fund?") and len(whole.split()) > vs.STEM_MAX_WORDS
    held = vs.frequency_held(THREE_MONTHS, PALUS)
    assert held == "In the last 3 months, in how many months did you leave raised cash sitting?"
    assert "on how many did" not in held and "how many months" in held and len(held.split()) <= vs.STEM_MAX_WORDS
    assert vs.frequency_held(THREE_MONTHS, "keep cash from your raise in the bank") == \
        "In the last 3 months, in how many months did you keep cash from your raise in the bank?"
    assert vs.frequency_held(THREE_MONTHS, "keep every single dollar of the cash that your company raised sitting idle "
                                           "and unused") == "In the last 3 months, in how many months did that happen?"
    assert vs.frequency_served(vs.Window(4, "WEEKS"), "miss a call") == \
        "In the last 4 weeks, in how many weeks did you miss a call?"
    assert vs.frequency_served(vs.Window(7, "NIGHTS"), "have to work out why your baby was crying") == \
        "In the last 7 nights, on how many nights did you have to work out why your baby was crying?"
    # 160's unit-dropped form, read only on a stored item
    assert vs.frequency_unit_dropped(THREE_MONTHS, PALUS) == \
        "In the last 3 months, on how many did you leave raised cash sitting in your bank's money market fund?"
    assert vs.frequency_unit_dropped(THREE_MONTHS, "") is None


def test_a_two_word_unit_is_said_once_more_in_its_short_form():
    fresco = vs.frequency_served(FIVE_WORKING_DAYS, "put your photos and notes into the daily log")
    assert fresco == ("In the last 5 working days, on how many days did you put your photos and notes into the daily "
                      "log?") and fresco.count("working days") == 1
    assert vs.frequency_served(FIVE_WORKING_DAYS, None) == "In the last 5 working days, on how many days did that happen?"
    assert vs.frequency_served_before174(FIVE_WORKING_DAYS, None) == \
        "In the last 5 working days, on how many working days did that happen?"
    assert [vs.counted_in(vs.Window(2, u)) for u in ("NIGHTS", "DAYS", "WORKING_DAYS", "WEEKS", "MONTHS")] == \
        ["on", "on", "on", "in", "in"]
    assert vs.short_unit(FIVE_WORKING_DAYS) == "days"


@pytest.mark.parametrize("count, unit", [(7, "NIGHTS"), (3, "MONTHS"), (4, "WEEKS"), (5, "WORKING_DAYS"),
                                         (12, "MONTHS")])
def test_the_wording_mirror_and_the_walk_say_one_frame(count, unit):
    clause = "lose your keys"
    assert wording_mod.frequency_respondent(registry_mod.RecallWindow(count, unit), clause) == \
        vs.frequency_served(vs.Window(count, unit), clause)
    assert wording_mod.frequency_respondent(registry_mod.RecallWindow(count, unit), "") == \
        vs.frequency_served(vs.Window(count, unit), None)


def test_the_unit_is_never_dropped_past_the_cap():
    for window in (THREE_MONTHS, FIVE_WORKING_DAYS, vs.Window(7, "DAYS"), vs.Window(12, "MONTHS")):
        for clause in (PALUS, "have to recount the stock by hand after a delivery",
                       "type up the daily log by hand after the site walks"):
            held = vs.frequency_held(window, clause)
            assert f" how many {vs.short_unit(window)} did " in held, held
            assert len(held.split()) <= vs.STEM_MAX_WORDS, held


def test_the_frames_are_window_frames():
    text = _cloud(VECTORS + "WindowFrame.java", "windowFirstBefore174")
    assert '"In " + w.words() + ", " + countedIn(w) + " how many " + shortUnit(w) + " "' in text
    assert "case WEEKS, MONTHS -> \"in\";" in text and 'default -> "on";' in text
    assert '", on how many did " + subjectLed(event) + "?"' in text
    held = text[text.index("private static String held("):]
    held = held[:held.index("\n    }\n")]
    assert "unitDropped(" not in held and "frequencyRespondent(window, cut)" in held, "160's judgement call 4 retired"


@pytest.mark.parametrize("count, line", [(7, "Say a number from 1 to 7."), (5, "A number from 1 to 5."),
                                         (3, "A number from 1 to 3."), (30, "Say a number from 1 to 30."),
                                         (6, "Say a number from 1 to 6.")])
def test_the_voice_says_a_range_past_five_steps(count, line):
    assert spoken_mod.count_answer_line(count) == line


def test_the_range_line_is_spoken_forms():
    text = _cloud(VECTORS + "SpokenForm.java", "Say a number from 1 to ")
    assert '(w.axisMax() > MAX_OPTIONS ? "Say a number from 1 to " : "A number from 1 to ")' in text
    assert spoken_mod.MAX_OPTIONS == 5


# ------------------------------------------------------------------------------------- FR-3: the follow-up

def test_the_only_if_line_is_the_composers():
    text = _cloud(COMPOSER, "What would have to happen for that to be true?")
    assert '"You said only if " + condition + ". What would have to happen for that to be true?"' in text
    assert fake.only_if_said_back("I could try it on one site first") == \
        "You said only if I could try it on one site first. What would have to happen for that to be true?"
    assert fake.ONLY_IF_ASK_BEFORE_174 not in text[text.index("static String onlyIfSaidBack("):]
    saved = _cloud(VECTORS + "SavedList.java", "ONLY_IF")
    assert f'ONLY_IF = "{fake.ONLY_IF}";' in saved


def _adoption(entry, label):
    codes = ("yes", "yes_if_worth_it", "probably_not", "no")
    labels = dict(zip(codes, ("Yes", label, "Probably not", "No")))
    interview = {"occasion": "night", "parts": [{"part": 2, "items": [{
        "dimension": ADOPTION, "question": "To use it, you'd hold your phone near the cot. Would you do that, or not?",
        "options": [{"optionId": vs.option_id("tok", ADOPTION, c), "label": l} for c, l in labels.items()]}]}]}
    return vs.follow_up_question(entry, [vs.Pick(dimension=ADOPTION, codes=["yes_if_worth_it"])], vs.LINK_PRIMARY,
                                 interview, "tok", stem=(ADOPTION, True))


def test_the_conditional_yes_is_said_back_as_the_persons_own_condition():
    lullaby = _golden("03-lullaby")
    owed = _adoption(lullaby, "Only if I could try it for a week first")
    assert owed["text"] == owed["spoken"] == ("You said only if I could try it for a week first. What would have to "
                                              "happen for that to be true?")
    assert owed["also"] is True
    # the registry's fixed label (no condition on the lock's item): the second stem as before
    fixed = _adoption(lullaby, "Yes, if it was clearly worth it")
    assert fixed["text"] == fake.fill(ADOPTION, {"{solution_name}": vs.served_idea_name({}) or
                                                 vs._typed_idea_name(lullaby)}, also=True)
    assert "look like" not in owed["text"]


# ------------------------------------------------------------------------- FR-4: the gallery fixtures stay

def _beliefs(path: Path) -> list[str]:
    found: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get("belief"), str):
                found.append(node["belief"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(json.loads(path.read_text(encoding="utf-8")))
    return found


def test_the_fresco_run_is_read_in_its_recorded_frame():
    """The gallery's Fresco run (2026-10-22) records the words before 174 and stays until re-recorded after the screens;
    read through the one rule it says 174's."""
    fresco = _backtest("08-fresco")
    for name in ("plan.json", "standings.json"):
        beliefs = _beliefs(FRESCO_RUN / name)
        assert "A trial on one live job slows the purchase most." in beliefs, name
        assert "For most, on their last day, they could talk over the noise on site." in beliefs, name
    recorded = types.SimpleNamespace(persona=fresco.persona, context=fresco.context, founder_calibration={
        FRICTION: {"belief_sentence": "A trial on one live job slows the purchase most."},
        COMPATIBILITY: {"belief_sentence": "For most, on their last day, they could talk over the noise on site."}})
    assert corpus_mod.spec174_reads(recorded, FRICTION) == "A trial on one live job can slow or stop the purchase."
    assert corpus_mod.spec174_reads(recorded, COMPATIBILITY) == (
        f"For most {fresco.context['actor_plural']}, on their last day, they could talk over the noise on site.")
