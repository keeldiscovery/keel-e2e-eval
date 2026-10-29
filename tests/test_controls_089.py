"""Spec 089 (keel-cloud 158, contract 46; 159, contract 47; 160): the three moved respondent controls, stackless.

FR-2, Frequency from 1: a count is sent 1..N (`segmented_1_to_n`, a number box from `numeric.min` 1); corpus revision 19's
five recorded 0s after a yes (04-linerly Bruno Costa, Dmitri Volkov, Gwen Price; 05-paidly Petra Novak, Talia Ben-David)
are replayed as the item's escape, CANT_RECALL, each named in the scripted person's notes, and the corpus is unchanged.
"""

from __future__ import annotations

import yaml

from harness import classifier_guard as guard
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from instructions import registry as registry_mod
from tests import v9_fixtures as fx

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
