"""Spec 089 (keel-cloud 158, contract 46; 159, contract 47; 160): the three moved respondent controls, stackless.

FR-2, Frequency from 1: a count is sent 1..N (`segmented_1_to_n`, a number box from `numeric.min` 1); corpus revision 19's
five recorded 0s after a yes (04-linerly Bruno Costa, Dmitri Volkov, Gwen Price; 05-paidly Petra Novak, Talia Ben-David)
are replayed as the item's escape, CANT_RECALL, each named in the scripted person's notes, and the corpus is unchanged.
FR-3, one pick then one more: the second ask's words and escape held to keel-cloud's `ItemFrames`, the classifier's
`ask: second`, one pick with *Nothing else* a whole answer, the screens' and the AI link's walks in that order. FR-4,
one scale: the question in `ScaleFour`'s frame (the plain frame past 20 words), one code sent and no `advantageIds`, no
transform, the brief's line and the two decision sentences held to keel-cloud's `BriefFacts` and `DecisionChangeCorpusTest`.
FR-5, the frames in the people's words (keel-cloud 160): the served Frequency window first and held to the cap (the unit
said once, then the cut), E4 still measured on the frame before 160, and the registry's Lullaby examples read as the
harness composes them.
"""

from __future__ import annotations

import inspect
import re
from types import SimpleNamespace

import pytest
import yaml

from evals import corpus_scenario, interviewer_leg
from evals import interviewer_marks as im
from harness import interviewer_fake as fake
from harness import vectors_screens
from stack.config import load_config

from harness import classifier_guard as guard
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from instructions import registry as registry_mod
from tests import v9_fixtures as fx

KEEL_CLOUD = load_config(validate=False).keel_cloud
ITEM_FRAMES = "src/main/java/com/keeldiscovery/cloud/domain/vectors/ItemFrames.java"
SCALE_FOUR = "src/main/java/com/keeldiscovery/cloud/domain/vectors/ScaleFour.java"
BRIEF_FACTS = "src/main/java/com/keeldiscovery/cloud/application/BriefFacts.java"
DECISION_TEST = "src/test/java/com/keeldiscovery/cloud/corpus/DecisionChangeCorpusTest.java"
WINDOW_FRAME = "src/main/java/com/keeldiscovery/cloud/domain/vectors/WindowFrame.java"

FIVE = {("04-linerly", "Bruno Costa"), ("04-linerly", "Dmitri Volkov"), ("04-linerly", "Gwen Price"),
        ("05-paidly", "Petra Novak"), ("05-paidly", "Talia Ben-David")}


def _entry(name: str):
    return corpus_mod.load_file(fx.canon_entry(f"{name}.yaml"), registry=fx.registry())


# ------------------------------------------------------------------------------------- FR-2: Frequency from 1

def test_the_five_recorded_zeros_are_named_and_nobody_else_is_replayed():
    """158's *What did not hold*: the five 0s after a yes, exactly, are the harness's replayed escapes; every other
    Frequency pick on the golden seven is sent 1..N as recorded."""
    replayed = set()
    for name in ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly", "06-repeatline",
                 "07-mulchrun"):
        entry = _entry(name)
        for person in vs.person_inputs(entry):
            frequency = next((p for p in person.picks if p.dimension == "problem.frequency"), None)
            if person.notes:
                replayed.add((entry.id, person.person))
                assert frequency.chip == vs.FREQUENCY_ESCAPE and frequency.scale is None, person.person
                assert frequency.as_wire("t") == {"itemId": vs.item_id("t", "problem.frequency"),
                                                  "chip": "CANT_RECALL"}
                assert person.notes == (vs.zero_note(person.person, entry.id),)
                assert "0 after a yes" in person.notes[0] and vs.ZERO_DECISION in person.notes[0]
            elif frequency is not None and frequency.scale is not None:
                assert frequency.scale >= registry_mod.FREQUENCY_MIN, (entry.id, person.person)
    assert replayed == FIVE == set(vs.ZERO_AS_CANT_RECALL)


def test_the_corpus_still_records_the_five_zeros_and_the_reader_reads_them():
    """The corpus is never edited: the file still says 0 after a yes for each of the five, and the reader keeps it (the
    engine reads them as recorded; only the wire refuses a 0)."""
    for (entry_id, name), window in vs.ZERO_AS_CANT_RECALL.items():
        raw = yaml.safe_load(fx.canon_entry(f"{entry_id}.yaml").read_text(encoding="utf-8"))
        person = next(p for p in raw["answers"] if p["person"] == name)
        assert person["recency"] == "yes" and person["picks"]["problem.frequency"] == 0, (entry_id, name)
        window_raw = raw["context"]["recall_window"]
        assert f"{window_raw['count']} {window_raw['unit']}" == window
        entry = _entry(entry_id)
        assert next(p for p in entry.people() if p.person == name).picks["problem.frequency"] == 0


def test_a_zero_anywhere_is_replayed_and_named_never_sent(tmp_path):
    """A 0 the five do not name (01-countly's first person with a count, moved here) is replayed and named the same way
    -- never posted as a 0, never dropped."""
    raw = yaml.safe_load(fx.canon_entry("01-countly.yaml").read_text(encoding="utf-8"))
    person = next(p for p in raw["answers"] if isinstance(p.get("picks", {}).get("problem.frequency"), int))
    person["picks"]["problem.frequency"] = 0
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="01-countly.yaml"), registry=fx.registry())
    walked = next(p for p in vs.person_inputs(entry) if p.person == person["person"])
    assert walked.notes and person["person"] in walked.notes[0]
    sent = [a for a in walked.response("t").get("answers") or [] if a["itemId"] == vs.item_id("t", "problem.frequency")]
    assert sent == [{"itemId": vs.item_id("t", "problem.frequency"), "chip": "CANT_RECALL"}]


def test_the_classifier_reads_the_count_from_one():
    """keel-cloud 158 T004: the served scale and the number box start at 1 (`numeric.min`), so the classifier's range
    does; a number box served before 46 (no `min`) reads from 0 as it did."""
    interview = {"parts": [{"part": 1, "items": [
        {"itemId": "a", "dimension": "problem.frequency", "control": "segmented_1_to_n",
         "scale": {"min": 1, "max": 7, "minLabel": "just one", "maxLabel": "every one"},
         "escape": {"label": "I can't recall"}},
        {"itemId": "b", "dimension": "problem.frequency", "control": "number_with_unit",
         "numeric": {"defaultUnit": "days out of 30", "min": 1}, "escape": {"label": "I can't recall"}},
        {"itemId": "c", "dimension": "problem.frequency", "control": "number_with_unit",
         "spoken": {"optionsLine": "A number from 1 to 30."}, "numeric": {"min": 1}, "escape": None},
        {"itemId": "d", "dimension": "problem.frequency", "control": "number_with_unit",
         "numeric": {"defaultUnit": "months out of 3"}, "escape": None}]}]}
    got = guard.served_items(interview)
    assert [(s.kind, s.low, s.high) for s in got] == [("number", 1, 7), ("number", 1, 30), ("number", 1, 30),
                                                      ("number", 0, 3)]
    assert registry_mod.FREQUENCY_CONTROL == "segmented_1_to_n" and "segmented_0_to_7" not in \
        registry_mod.RESPONDENT_CONTROLS


# ------------------------------------------------------------------------------- FR-3: one pick, then one more

def _java_string(text: str, name: str) -> str | None:
    m = re.search(rf"\b{name} = \"([^\"]*)\";", text)
    return m.group(1) if m else None


def test_the_second_ask_is_keel_clouds_item_frames():
    """keel-cloud 158 T010 / T013: *And one more?* (the ITEM_MORE clip and the written second ask) and *Nothing else*
    (`nothing_else`, `NOTHING_ELSE` on the wire) are `ItemFrames`' -- the fake's MORE, the registry's and the screens'
    words are the same; skipped by name on a keel-cloud before 158."""
    path = KEEL_CLOUD / ITEM_FRAMES
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if "ONE_MORE" not in text:
        pytest.skip("keel-cloud predates spec 158 (no ItemFrames.ONE_MORE)")
    assert _java_string(text, "ONE_MORE") == fake.MORE == registry_mod.ONE_MORE == vs.ONE_MORE \
        == vectors_screens.IV_ONE_MORE == "And one more?"
    assert _java_string(text, "NOTHING_ELSE") == registry_mod.NOTHING_ELSE == "nothing_else"
    assert _java_string(text, "NOTHING_ELSE_LABEL") == registry_mod.NOTHING_ELSE_LABEL == vectors_screens.IV_NOTHING_ELSE
    assert registry_mod.NOTHING_ELSE_CHIP == vs.NOTHING_ELSE_CHIP == "NOTHING_ELSE"


def test_the_registry_of_record_asks_one_then_one_more():
    """The registry keel-cloud exports: Importance `pick_one_then_one`, its option rule naming *Nothing else*."""
    from instructions import cloud_corpus as cloud_mod                     # noqa: PLC0415
    if not (KEEL_CLOUD / cloud_mod.REGISTRY_FILE).is_file():
        pytest.skip(f"no registry of record at {KEEL_CLOUD / cloud_mod.REGISTRY_FILE}")
    registry = cloud_mod.registry_of_record(KEEL_CLOUD)
    importance = registry.by_key("problem.importance")
    if importance.respondent_control != registry_mod.IMPORTANCE_CONTROL:
        pytest.skip("keel-cloud predates spec 158 (Importance is not pick_one_then_one)")
    assert "Nothing else" in importance.respondent["option_rule"]
    assert registry.by_key("problem.frequency").respondent_control == registry_mod.FREQUENCY_CONTROL


def test_the_classifier_reads_the_second_ask_with_its_own_escape():
    """keel-cloud 158 T014: the first ask is a multi of two with *None of these*; the second (`ask: second`) one pick
    over the same labels with *Nothing else* -- so a spoken *nothing else* is never read as *None of these*."""
    interview = {"parts": [{"part": 1, "items": [
        {"itemId": "a", "dimension": "problem.importance", "control": "pick_one_then_one",
         "options": [{"optionId": "o1", "label": "One"}, {"optionId": "o2", "label": "Two"},
                     {"optionId": "o3", "label": "Three"}],
         "escape": {"code": "NONE_OF_THESE", "label": "None of these"},
         "secondAsk": {"question": "And one more?", "escape": {"code": "NOTHING_ELSE", "label": "Nothing else"}}}]}]}
    got = guard.served_items(interview)
    assert [(s.kind, s.pick, s.escape, s.ask) for s in got] == [("multi", 2, "None of these", None),
                                                                ("single", 0, "Nothing else", "second")]
    assert got[1].options == ("One", "Two", "Three") and got[1].shape == "problem.importance/second (single, 3 options)"


def test_one_pick_and_nothing_else_is_a_whole_answer():
    """FR-3: where one of the two picks is not offered, the other is kept with *Nothing else* (keel-cloud 158: stored as
    the one code) -- the item is not left to its escape, as `pick_two` with one still is."""
    from evals.corpus_scenario import _without_the_unoffered            # noqa: PLC0415
    items = {"problem.importance": {"itemId": "i1", "dimension": "problem.importance", "control": "pick_one_then_one",
                                    "options": [{"optionId": "a", "label": "A"}, {"optionId": "b", "label": "B"}]}}
    j = SimpleNamespace(findings=[])
    out = _without_the_unoffered(j, SimpleNamespace(person="Lakisha", picks=[]),
                                 {"recency": True, "answers": [{"itemId": "i1", "optionIds": ["nope", "b"]}]}, items,
                                 "tok")
    assert out["answers"] == [{"itemId": "i1", "optionIds": ["b"], "chip": "NOTHING_ELSE"}]
    assert "the first pick kept, then Nothing else" in j.findings[0]["what"]
    assert corpus_scenario.PICKS_NEEDED["pick_one_then_one"] == 2 and "pick_one_then_one" in corpus_scenario.ROW_CONTROLS


def test_the_screens_tap_one_wait_for_the_second_ask_then_the_other():
    """keel-web 135 FR-2 on the text link: the first option tapped, *And one more?* waited for, then the second option or
    *Nothing else*; the item's screen is read on the first ask and keeps what the second drew."""
    src = inspect.getsource(vectors_screens.Interview._one_then_one)
    # spec 090 FR-2 (keel-web 135 H-11): the wait is on the second ask's own test id, `second-ask`, not its words
    first, wait, second = (src.index("option(options[ids[0]]).click()"), src.index('get_by_test_id("second-ask")'),
                           src.index("option(options[ids[1]]).click()"))
    assert first < wait < second and "name=nothing, exact=True" in src
    answer = inspect.getsource(vectors_screens.Interview._answer)
    assert answer.index("self._one_then_one(item, answer, options)") < answer.index('if answer.get("chip"):')
    loop = inspect.getsource(vectors_screens.Interview._items)
    assert loop.index("first_ask = self._item_screen(item)") < loop.index("self._answer(item, answer)")


def test_the_ai_link_taps_one_hears_and_one_more_then_the_second():
    """keel-web 135 FR-2 on the AI link: the first tap, the item's `more` clip waited for, then the second tap or
    *Nothing else*; IM20 (v14) reads that walk."""
    src = inspect.getsource(interviewer_leg._Walk.tap_one_then_one)
    assert src.index("p.tap(want[0])") < src.index("_played_at(p, more_clip) < tapped_at") < src.index("p.tap(second)")
    # spec 090 FR-2 (keel-web 135 H-1): *Nothing else* is the item's served `secondAsk.escape.label`, the registry's
    # label where none is served
    assert "p.tap_chip_named(nothing)" in src and "or vs.NOTHING_ELSE_LABEL" in src
    assert im.INTERVIEWER_MARKS_VERSION == 14
    record = {"taps": {"question": "Which one?", "want": ["A", "B"], "next": "Which fits?", "sent": ["B", "A"],
                       "sent_how": "TAPPED",
                       "one": {"question_same": True, "phase": "listening", "ring": False, "checked": ["A"],
                               "more_played": True},
                       "two": {"ring": False}}}
    assert im.taps_wait_for_save(record)[0] is True
    record["taps"]["one"]["more_played"] = False
    assert im.taps_wait_for_save(record)[0] is False


# ------------------------------------------------------------------------------------------- FR-4: one scale

def _cloud(path: str, marker: str) -> str:
    text = (KEEL_CLOUD / path).read_text(encoding="utf-8") if (KEEL_CLOUD / path).is_file() else ""
    if marker not in text:
        pytest.skip(f"keel-cloud predates spec 159 (no {marker} in {path})")
    return text


def test_the_question_is_scale_fours_and_the_plain_frame_past_the_cap():
    """keel-cloud 159 T002 (`ScaleFour.question`): *On your last {occasion}, would {name} have made it go better for you,
    or not?*; where that passes 20 words, *Would {name} ...* (06-repeatline's came to 22)."""
    text = _cloud(SCALE_FOUR, "FRAME")
    assert _java_string(text, "FRAME") == vs.BENEFIT_FRAME
    assert vs.benefit_question("invoice", "invoice payout service") == \
        "On your last invoice, would invoice payout service have made it go better for you, or not?"
    long = vs.benefit_question("shift on the phones", "refill requests filed for you")
    assert long == "Would refill requests filed for you have made it go better for you, or not?"
    assert len(f"On your last shift on the phones, would refill requests filed for you {vs.BENEFIT_FRAME}".split()) == 22
    assert vs.benefit_question("", "") == "On your last time, would the idea have made it go better for you, or not?"


def test_one_code_is_sent_and_no_benefit():
    """keel-cloud 159 T004 (contract 47): the answer is one `optionIds` entry on the scale's four; `advantageIds` is gone
    from every scripted body, and the scripted pick is the corpus's code as it stands."""
    import dataclasses                                                     # noqa: PLC0415
    assert "advantages" not in {f.name for f in dataclasses.fields(vs.Pick)}
    for name in ("01-countly", "05-paidly", "07-mulchrun"):
        entry = _entry(name)
        recorded = {p.person: (p.picks or {}).get(registry_mod.BENEFIT_KEY) for p in entry.people()}
        for person in vs.person_inputs(entry):
            for pick in person.picks:
                wire = pick.as_wire("t")
                assert "advantageIds" not in wire
                if pick.dimension == registry_mod.BENEFIT_KEY and not pick.chip:
                    assert pick.codes == [recorded[person.person]] and wire["optionIds"] == [
                        vs.option_id("t", registry_mod.BENEFIT_KEY, recorded[person.person])]


def test_the_one_rule_is_scale_fours():
    """keel-cloud 159 FR-3 (`ScaleFour.fromThree`): positive with a benefit a lot better, with none a little better,
    neutral no difference, negative worse; the chip as it was."""
    text = _cloud(SCALE_FOUR, "fromThree")
    assert "case OLD_POSITIVE -> benefitTicked ? A_LOT_BETTER : A_LITTLE_BETTER;" in text
    assert registry_mod.from_three({"answer": "positive", "advantages": ["x"]}) == "a_lot_better"
    assert registry_mod.from_three({"answer": "positive"}) == "a_little_better"
    assert registry_mod.from_three({"answer": "neutral"}) == "no_difference"
    assert registry_mod.from_three({"answer": "negative"}) == "worse"
    assert registry_mod.from_three({"chip": "cant_tell"}) == {"chip": "cant_tell"}
    assert list(registry_mod.BENEFIT_CODES) == [_java_string(text, c) for c in
                                                ("A_LOT_BETTER", "A_LITTLE_BETTER", "NO_DIFFERENCE", "WORSE")]


def test_the_scale_is_spoken_without_a_transform():
    """keel-cloud 159 T005: one question and four short options -- `yes_no_per_benefit` retired, S9 refuses it."""
    from instructions import spoken as spoken_mod                          # noqa: PLC0415
    assert registry_mod.BENEFIT_KEY not in spoken_mod.TRANSFORMS
    assert "yes_no_per_benefit" not in spoken_mod.TRANSFORMS.values()


def test_the_brief_line_and_the_two_decisions_are_keel_clouds():
    """keel-cloud 159 T010 (`BriefFacts.goneBetterLine`, `DecisionChangeCorpusTest`): *N of M · said it would have gone
    better, K of them a lot*, and 02-compliancelog's and 06-repeatline's decisions in those words."""
    from instructions import brief_facts as bf                             # noqa: PLC0415
    text = _cloud(BRIEF_FACTS, "goneBetterLine")
    assert '"said it would have gone better, " + aLot + " of them a lot"' in text
    assert bf.gone_better_line(4) == "said it would have gone better, 4 of them a lot"
    test = re.sub(r'"\s*\+\s*"', "", _cloud(DECISION_TEST, "of them a lot"))
    for entry_id in ("02-compliancelog", "06-repeatline"):
        change = bf.DECISION_CHANGE[entry_id]
        said = change["sentence"] + (" " + change["also"]["sentence"] if change.get("also") else "")
        assert f'CHANGE.put("{entry_id}", "{said}");' in test, entry_id
    entry = _entry("02-compliancelog")
    card = next(c for c in bf.cards_for(entry, fx.registry()) if c["key"] == registry_mod.BENEFIT_KEY)
    assert (card["number"], card["line"]) == ("4 of 9", "said it would have gone better, 4 of them a lot")


# ------------------------------------------------------------------------------------ FR-5: the frames (160)

def test_the_served_frequency_opens_with_the_window_and_e4_keeps_its_measure():
    """keel-cloud 160 FR-2 / judgement call 2: *In {window}, on how many {unit} did ...?* served; `frequencyMeasured`
    (*On how many of those ...*) is what E4 and the gate's fallbacks measure a clause on, so no gate moves."""
    from instructions import wording as wording_mod                        # noqa: PLC0415
    text = _cloud(WINDOW_FRAME, "frequencyMeasured")
    assert '", on how many " + w.timeUnit().plural() + " "' in text and '"On how many of those "' in text
    nights = vs.Window(7, "NIGHTS")
    assert vs.frequency_served(nights, "have to work out why your baby was crying") == \
        "In the last 7 nights, on how many nights did you have to work out why your baby was crying?"
    assert vs.frequency_served(nights, "") == "In the last 7 nights, on how many nights did that happen?"
    assert vs.frequency_question(nights, "have to work out why your baby was crying") == \
        "On how many of those 7 nights did you have to work out why your baby was crying?"
    window = registry_mod.RecallWindow(7, "NIGHTS")
    assert wording_mod.frequency_respondent(window, "have to work out why your baby was crying") == \
        vs.frequency_served(nights, "have to work out why your baby was crying")
    assert wording_mod.frequency_measured(window, "lose your keys") == "On how many of those 7 nights did you lose your keys?"


def test_the_registrys_lullaby_examples_are_the_frames_the_harness_composes():
    """keel-cloud 160 T009 / T015: the registry of record's Lullaby questions follow the frames -- Frequency window first,
    Importance *Think of your last night. Which one of these ...?*, Current solution *How did {phrase} go?*."""
    from instructions import cloud_corpus as cloud_mod                     # noqa: PLC0415
    path = KEEL_CLOUD / cloud_mod.REGISTRY_FILE
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if "on how many nights did you" not in text:
        pytest.skip("keel-cloud predates spec 160 (the registry's Lullaby Frequency is not window first)")
    assert vs.frequency_served(vs.Window(7, "NIGHTS"), "have to work out why your baby was crying") in text
    assert "Think of your last night. Which one of these would you most like made easier?" in text
    assert "How did your way of working out what the baby needed go?" in text


# ---------------------------------------------------------------------------------------- FR-6: decided before

def test_the_five_zeros_are_held_for_the_founder_and_158_159_are_marked_merged():
    """FR-6: D-2026-10-29-13 / -14 carry 158's merge (`e3d34831`), -15 159's (`1cf2ebc3`); the five 0s are a `held`
    entry, D-2026-10-30-01, `spec-merged` with no spec (087's validator takes it: a spec is required on `taken` only),
    still active, on the Frequency item, and naming each of the five; its fix names no location the cycle writes, so it
    snoozes no weak row."""
    from quality import decisions as dec                                    # noqa: PLC0415
    found = {d["id"]: d for d in dec.load(dec.DECISIONS_PATH)}
    assert (found["D-2026-10-29-13"]["merged"], found["D-2026-10-29-14"]["merged"],
            found["D-2026-10-29-15"]["merged"]) == ("e3d34831", "e3d34831", "1cf2ebc3")
    held = found[vs.ZERO_DECISION]
    assert (held["decision"], held["until"], "spec" in held, "merged" in held) == ("held", "spec-merged", False, False)
    assert dec.active(held, "20261028-f48f256") and held["_row"]["dimension"] == {"problem.frequency"}
    assert all(name in held["why"] for _, name in vs.ZERO_AS_CANT_RECALL)
    assert not dec.fix_matches(held, {"category": "registry row", "place": "dimension-registry.json problem.frequency"})
