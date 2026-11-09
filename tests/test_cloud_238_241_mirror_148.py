"""Spec 148 -- the harness mirrors round A: keel-cloud 238 to 241 (keel-cloud-docs master `155eaca9`) and keel-web 183
(master `36d069ed`).

- FR-1 the digest: `quality/readers/dimensions.md` is keel-cloud's `dimension-cards.md` byte for byte at
  `RespondentReview.CARDS_SHA256` (238: Prevalence §2; 239: Existing sacrifice §2, §6; 241: Ability to pay §2, §5, §6),
  the pin chain moved through 238's and 239's digests.

No stack, no model, no key: the cloud's and the web's files are read where the checkouts are there, else skipped by name.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from quality import cards
from stack.config import load_config

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
KEEL_WEB = Path(CONFIG.keel_web)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
PROJECT = "src/main/java/com/keeldiscovery/cloud/domain/project/"
CARDS = "src/main/resources/keel/dimension-cards.md"
#: keel-cloud 238 (`5222bd06`, merged): Prevalence §2, one bullet (was `42fa94dd...`, 237).
CARDS_SHA256_238 = "d764f34fd23127c001ac61f1cfddbedc1adf7ce9ec520144765161cfceaa81d2"
#: keel-cloud 239 (`1260f4fe`; 240 moved no card): Existing sacrifice §2, §6.
CARDS_SHA256_239 = "94f9edc648dd57e76df30d788e7fff86f8cf5fc1ef7f785e36d71574eaf809a7"
#: keel-cloud 241 (`155eaca9`, the round's final sha): Ability to pay §2, §5, §6.
CARDS_SHA256_241 = "78bd11674018b1e2644b2de99256e1fe3c2c781e0f6fca7cefab68fe98e86307"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD} ({rel})")
    return path.read_text(encoding="utf-8")


def _web(rel: str) -> str:
    path = KEEL_WEB / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_WEB}")
    return path.read_text(encoding="utf-8")


def _cards() -> str:
    return " ".join(cards.CARDS_PATH.read_text(encoding="utf-8").split())


# ------------------------------------------------------------------------------------------- FR-1 the digest

def test_the_reader_digest_is_241s_cards():
    """FR-1: the reader's cards are the cloud's vendored copy byte for byte, at 241's digest (`CARDS_SHA256_141`, the one
    constant the earlier pins read, moved in place); 238's and 239's the steps between, each its own."""
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    from tests.test_cloud_236_237_mirror_147 import CARDS_SHA256_237   # noqa: PLC0415
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    ours = cards.CARDS_PATH.read_bytes()
    assert hashlib.sha256(ours).hexdigest() == sha == CARDS_SHA256_241 == CARDS_SHA256_141
    assert (KEEL_CLOUD / CARDS).read_bytes() == ours
    assert len({CARDS_SHA256_237, CARDS_SHA256_238, CARDS_SHA256_239, CARDS_SHA256_241}) == 4


def test_prevalence_reads_the_act_that_hurts_against_the_segment():
    """FR-1 (238 FR-6): Prevalence §2's new bullet -- E7 against the segment, the hurt's kind and a new word; E9 names its
    No by a word of the hurt; E8's two verdicts and its blame."""
    text = _cards()
    assert "**The act that hurts, read against the segment (keel-cloud 238).**" in text
    assert "*less than it could* and *more than it should* as verdicts" in text
    assert "*let*, *allowed* or *failed to* at the head as blame" in text
    assert "(*had the call ring out*), never as their choice (*let the call ring out*)" in text


def test_existing_sacrifice_names_the_thing_they_see_go():
    """FR-1 (239 FR-6): Existing sacrifice §2 -- the base the line's, the unit kept, no neutral verb; §6 the pitfall."""
    text = _cards()
    assert "Never *lose*, *lost*, *miss*, *go without* or *fell through*" in text
    assert "*unanswered*: *did not get answered*; *lost track of*: *did you not keep track of*" in text
    assert "the typed *per {unit}* kept in the question and the label on the decision-maker's link, said once" in text
    assert "on a money-only study by its part-3 job; two repair turns" in text
    assert "never *go without* or *fell through* where the writer can say it" not in text


def test_ability_to_pay_labels_fit_every_organisation_on_the_card():
    """FR-1 (241 FR-2): Ability to pay §2, §5, §6 -- the two labels as served; no unit of one kind of organisation."""
    text = _cards()
    assert "`charged_to_users` *Charged back to whoever uses it*" in text
    assert "`outside_funding` *New money from outside, such as a grant*" in text
    assert "**Each source holds in any organisation** (keel-cloud 241)" in text
    assert "`charged_to_users` *Charged to the teams" not in text and "· A grant or outside funding ·" not in text
    assert "*A grant or outside funding* blurred with a grant already in an existing line" in text


# ------------------------------------------------------------------------------------------- FR-2 the gate (238)

from instructions import wording as wording_mod                             # noqa: E402
from instructions.context import RecallWindow                               # noqa: E402

SEVEN_DAYS = RecallWindow(7, "DAYS")
THREE_MONTHS = RecallWindow(3, "MONTHS")
#: keel-cloud `VectorFixtures` (Lullaby).
LULLABY_ROUTINE = "settle the baby"
LULLABY_WENT_WRONG = "did not know why the baby cried"
LULLABY_NO_SAYER = "a parent who knew at once what the cry meant"
LULLABY_EVENT = "had to work out why their baby was crying"
LULLABY_PEOPLE = "parents of babies under six months"
LULLABY_CIRCUMSTANCE = "the baby cries in the night"
LULLABY_SEED = ("When a baby cries in the night, parents don't know what it needs, so they try feeding, changing and "
                "rocking until something works, and it takes about twenty minutes each time.")
#: `TheGateAsksTheActThatHurtsTest`'s invented florist's round.
FLORISTS = "florists"
WRAPPED = "the day's bouquets are wrapped and the cards still have to be signed"
WRAP = "wrap the day's bouquets"
SIGNED_LATE = "signed the cards after the van had gone"
FLORIST_SEED = ("Florists wrap forty bouquets a day, and the cards get signed in a rush; when the van goes early a "
                "bouquet goes out without its card and the customer calls to complain.")


def test_e7_reads_the_event_against_the_segment():
    """FR-2 (238 FR-1, `theEventIsReadAgainstTheSegment`, word for word): every word the segment line's or the routine's
    is refused, naming the segment's words and the card's test; a word of the hurt beyond them, or a negation, passes."""
    assert wording_mod.routine_fault("sign the cards for the bouquets", WRAP, SIGNED_LATE, FLORISTS) is None
    assert wording_mod.routine_fault("sign the cards for the bouquets", WRAP, SIGNED_LATE, FLORISTS, WRAPPED) == (
        "E7: event 'sign the cards for the bouquets' is what every one of them does in the segment: 'sign', 'cards' and "
        f"'bouquets' are the circumstance's ('{WRAPPED}') -- so everyone would answer Yes. The test: would every one of "
        "them who did the day's work in the window say Yes to event? If every one would, it is the routine; write the "
        "part that hurt instead -- the thing that failed, was lost, came back wrong, sat idle or had to be done twice "
        f"-- event from went_wrong ('{SIGNED_LATE}')")
    fault = wording_mod.routine_fault("settled the baby once it cried", LULLABY_ROUTINE, LULLABY_WENT_WRONG,
                                      LULLABY_PEOPLE, LULLABY_CIRCUMSTANCE)
    assert fault.startswith("E7: event 'settled the baby once it cried' is what every one of them does in the segment: "
                            "'cried' is the circumstance's ('the baby cries in the night'), the rest the routine's "
                            "('settle the baby')") and wording_mod.HURT_SENTENCE in fault
    assert wording_mod.routine_fault(SIGNED_LATE, WRAP, SIGNED_LATE, FLORISTS, WRAPPED, FLORIST_SEED) is None
    assert wording_mod.routine_fault("had a bouquet go out without its card", WRAP,
                                     "a bouquet went out in the van without its card", FLORISTS,
                                     "the bouquets go out in the van") is None
    assert wording_mod.routine_fault(LULLABY_EVENT, LULLABY_ROUTINE, LULLABY_WENT_WRONG, "parents",
                                     LULLABY_CIRCUMSTANCE, LULLABY_SEED) is None


def test_e7_keeps_the_hurts_kind():
    """FR-2 (238 FR-3, `theEventKeepsTheHurtsKind`): an event that drops went_wrong's own words is refused; an event E8
    faults is E8's (served with its note), never refused here."""
    send, halted = "send a print job to the press", "a print job stopped halfway for want of paper"
    assert wording_mod.routine_fault("had a print job come out late", send, halted, "printers") == (
        "E7: event 'had a print job come out late' carries none of went_wrong's own words ('stopped', 'halfway', 'want' "
        f"and 'paper', in '{halted}') -- the kind of thing that went wrong is dropped, so one who met another kind would "
        "answer Yes; write event from went_wrong, keeping one of its words. The test: would every one of them who did "
        "the day's work in the window say Yes to event? If every one would, it is the routine; write the part that hurt "
        "instead -- the thing that failed, was lost, came back wrong, sat idle or had to be done twice")
    assert wording_mod.routine_fault("had a print job stop for want of paper", send, halted, "printers") is None
    assert wording_mod.routine_fault("had a print job stop halfway", send, halted, "printers") is None
    assert wording_mod.routine_fault("left a print job sitting in the tray", send, halted, "printers") is None


def test_e7_adds_no_word_the_founder_never_gave():
    """FR-2 (238 FR-3, `theEventAddsNoWordTheFounderNeverGave`): a setting the founder never gave is refused where the
    seed is in hand; the seed's words, its typos read as meant, pass; E8's own words are never a new word."""
    sing, lost = "sing with the choir", "lost the beat when the hall echoed"
    echoes = "the choir sings in a hall that echoes"
    seed = "Choir singers lose the beatt when a hall echoes, and the conductor cannot be seen from the back row."
    assert wording_mod.routine_fault("lost the beat in a church hall", sing, lost, "choir singers", echoes, seed) == (
        "E7: event 'lost the beat in a church hall' says 'church', a word the founder never gave -- in none of "
        "went_wrong, the routine, the circumstance or the founder's problem; a setting or a kind they did not name "
        "turns away people who had the problem; write the part that hurt instead -- the thing that failed, was lost, "
        "came back wrong, sat idle or had to be done twice, from went_wrong in the founder's words")
    assert wording_mod.new_word("lost the beat in a church hall", "choir singers", lost, sing, echoes, seed) == "church"
    assert wording_mod.routine_fault("lost the beat in the back row", sing, lost, "choir singers", echoes, seed) is None
    assert wording_mod.routine_fault("lost the beat in the hall", sing, lost, "choir singers", echoes, seed) is None
    assert wording_mod.routine_fault("lost the beat in a church hall", sing, lost, "choir singers", echoes) is None
    assert wording_mod.new_word("lost the beat and stayed lost", "choir singers", lost, sing, echoes, seed) is None
    assert wording_mod.new_word("worked out why the baby cried in the car", None, LULLABY_WENT_WRONG, LULLABY_ROUTINE,
                                LULLABY_CIRCUMSTANCE, LULLABY_SEED) == "car"


OPEN = "open the bakery at six"
COLD = "the oven was still cold when the first loaves went in"
BAKERY = "the bakery opens before the first customers"


def test_e9_names_its_no_by_a_word_of_the_hurt():
    """FR-2 (238 FR-2, `theNoSayerNamesItsNo`, word for word): a no-sayer who names nothing of the hurt is refused with
    the card's test; one whose No is a word of went_wrong, denied or not, passes; 216's refusals first."""
    assert wording_mod.no_sayer_fault("a baker who had a quiet morning", OPEN, COLD, BAKERY, "baker", "bakers") == (
        "E9: no_sayer 'a baker who had a quiet morning' names none of what went wrong ('oven', 'cold' and 'loaves', in "
        f"'{COLD}') -- one set apart by nothing the hurt names is set apart by the routine, so every one of them who did "
        "the day's work would answer Yes to event; name their No by a word of went_wrong, denied. The test: would every "
        "one of them who did the day's work in the window say Yes to event? If every one would, it is the routine; "
        "write the part that hurt instead -- the thing that failed, was lost, came back wrong, sat idle or had to be "
        "done twice -- and no_sayer, one of them who did the day's work and truly answers No, naming what was different "
        "for them")
    for passing in ("a baker whose oven was hot before the first loaves", "a baker whose oven never went cold"):
        assert wording_mod.no_sayer_fault(passing, OPEN, COLD, BAKERY, "baker", "bakers") is None, passing
    assert wording_mod.no_sayer_fault("a baker who opened at six on a quiet day", OPEN, COLD, BAKERY, "baker",
                                      "bakers").startswith("E9: no_sayer 'a baker who opened at six on a quiet day' "
                                                           "differs from the rest by the routine")
    assert wording_mod.no_sayer_fault(LULLABY_NO_SAYER, LULLABY_ROUTINE, LULLABY_WENT_WRONG, LULLABY_CIRCUMSTANCE,
                                      "parent", LULLABY_PEOPLE) is None
    assert wording_mod.no_sayer_fault("a parent who had a quiet night", LULLABY_ROUTINE, LULLABY_WENT_WRONG,
                                      LULLABY_CIRCUMSTANCE, "parent", LULLABY_PEOPLE).startswith(
        "E9: no_sayer 'a parent who had a quiet night' names none of what went wrong ('know' and 'cried'")


def test_e8_reads_blame_and_two_more_verdicts():
    """FR-2 (238 FR-4, `blameAndVerdictAreEights`): blame at the head and the two new verdicts, each named; what happened
    to them, its subject first, passes."""
    assert wording_mod.packed_fault("let the milk spill", "the milk spilled", SEVEN_DAYS) == (
        "E8: event 'let the milk spill' opens on 'let', blame -- what happened to them said as their choice, which the "
        "founder's words do not say; a thing that happened to them is its subject first after had (had {the thing} {do} "
        "...: had the call ring out, never let the call ring out); write the act from went_wrong as a person saw it on "
        "a given day")
    assert "opens on 'allowed', blame" in wording_mod.packed_fault("allowed a parcel to go missing",
                                                                   "a parcel went missing", SEVEN_DAYS)
    assert "opens on 'failed to', blame" in wording_mod.packed_fault("failed to answer the door",
                                                                     "nobody answered the door", SEVEN_DAYS)
    assert "'let'" in wording_mod.packed_fault("already let the milk spill", "the milk spilled", SEVEN_DAYS)
    verdict = wording_mod.packed_fault("had the savings earn less than it could", "the savings earned little",
                                       THREE_MONTHS)
    assert "carries 'less than it could', a verdict on the act" in verdict and verdict.endswith("on a given month")
    assert "'more than it should'" in wording_mod.packed_fault("paid for a heater that cost more than it should",
                                                               "the heater cost a lot", THREE_MONTHS)
    assert wording_mod.packed_fault("had the milk spill", "the milk spilled", SEVEN_DAYS) is None
    assert wording_mod.packed_fault("had a parcel go missing", "a parcel went missing", SEVEN_DAYS) is None
    # cycle 14's Codyco clause (keel-cloud 238 judgement call 8): blame now, its subject-first form the passing clause
    assert "opens on 'let', blame" in wording_mod.packed_fault("let a booking call ring out unanswered", None)
    assert wording_mod.packed_fault("had a booking call ring out unanswered", None) is None


def test_the_refusal_texts_and_the_lists_are_the_clouds():
    """FR-2 (238 FR-5): the card's sentence and test, the blame heads, the verdict list and E9's test are the cloud's,
    word for word."""
    text = re.sub(r'"\s*\+\s*"', "", _cloud(VECTORS + "WindowFrame.java"))
    assert f'HURT_SENTENCE = "{wording_mod.HURT_SENTENCE}"' in text
    assert 'ROUTINE_TEST = "the test: would every one of them who did the day\'s work in the window say Yes to event? ' \
           'If every one would, it is the routine; " + HURT_SENTENCE' in text
    assert wording_mod.ROUTINE_TEST.endswith(wording_mod.HURT_SENTENCE)
    assert 'NO_SAYER_TEST = ROUTINE_TEST + " -- and no_sayer, one of them who did the day\'s work and truly answers No, ' \
           'naming what was different for them"' in text
    heads = text.split("BLAME_HEADS = List.of(", 1)[1].split(");", 1)[0]
    assert tuple(re.findall(r'"([^"]+)"', heads)) == wording_mod.BLAME_HEADS
    fails = text.split("FAIL_FORMS = java.util.Set.of(", 1)[1].split(");", 1)[0]
    assert set(re.findall(r'"([^"]+)"', fails)) == wording_mod.FAIL_FORMS
    verdicts = text.split("VERDICT_WORDS = List.of(", 1)[1].split(");", 1)[0]
    assert tuple(re.findall(r'"([^"]+)"', verdicts)) == wording_mod.VERDICT_WORDS
    for prefix in ("is what every one of them does in the segment: ", "' carries none of went_wrong's own words (",
                   "', a word the founder never gave -- in none of ", "' names none of what went wrong (",
                   "' opens on '"):
        assert prefix in text, prefix


# ------------------------------------------------------------------------- FR-2 the walk: named stops, notes, the gate

from evals import backtest as bt                                            # noqa: E402
from evals import corpus_scenario as cs                                     # noqa: E402

#: The five refusal texts as keel-cloud 238 words them (its tasks.md, *Refusal texts as written*), each as the walk reads
#: a refused interaction (`status: path: why`), and the rule and refusal it is named by.
REFUSED = [
    (f"RESULT_INVALID: result.questions[0].event: E7: event 'sign the cards for the bouquets' is what every one of them "
     f"does in the segment: 'sign', 'cards' and 'bouquets' are the circumstance's ('{WRAPPED}') -- so everyone would "
     "answer Yes. The test: ...", "E7", "the segment", "238 FR-1"),
    ("RESULT_INVALID: result.questions[0].event: E7: event 'had a print job come out late' carries none of went_wrong's "
     "own words ('stopped' and 'paper', in 'a print job stopped for want of paper') -- the kind of thing that went wrong "
     "is dropped", "E7", "the hurt's kind dropped", "238 FR-3"),
    # the project step's seed refusal (238 FR-3, `wordTheFounderGave`): the same path, the same rule
    ("RESULT_INVALID: result.questions[0].event: E7: event 'worked out why the baby cried in the car' says 'car', a word "
     "the founder never gave -- in none of went_wrong, the routine, the circumstance or the founder's problem", "E7",
     "a word the founder never gave", "238 FR-3"),
    ("RESULT_INVALID: result.questions[0].no_sayer: E9: no_sayer 'a parent who had a quiet night' names none of what "
     "went wrong ('know' and 'cried', in 'did not know why the baby cried') -- one set apart by nothing the hurt names",
     "E9", "the no-sayer names no word of the hurt", "238 FR-2"),
    # cycle 18's Fresco refusal, as the bundle recorded it (216's E9)
    ("RESULT_INVALID: result.questions[0].no_sayer: E9: no_sayer 'a superintendent who logged notes during the walks' "
     "differs from the rest by the routine ('walk the site and log the day's work': 'log')", "E9",
     "the no-sayer set apart by the routine", "216 FR-1"),
    ("RESULT_INVALID: result.questions[0].event: E7: event 'typed the log' is the routine ('type the log'), what every "
     "one of them does", "E7", "the routine", "212 FR-2"),
]


@pytest.mark.parametrize("said, rule, refusal, spec", REFUSED)
def test_the_gates_e7_and_e9_are_named_by_rule(said, rule, refusal, spec):
    """FR-2 (238 FR-5): each E7 / E9 refusal past the repair turn is RESULT_INVALID, named by its rule and refusal, on
    `result.questions[0]`'s path -- the seed refusal at the project step reads as one at the parse."""
    got = cs.gate_refusal(said, "PROBLEM")
    assert got["rule"] == rule and got["refusal"] == refusal and got["spec"] == f"keel-cloud {spec}"
    assert got["vector"] == "PROBLEM" and got["path"].startswith("result.questions[0].")
    assert got["said"].startswith(f"{rule}: ")


def test_e8_and_the_other_rules_are_never_a_named_stop():
    """FR-2 (238 FR-4): blame and the two new verdicts are E8's -- served with the note, never a stop; another rule's
    refusal, or E7 not RESULT_INVALID, is no gate refusal either."""
    for said in ("RESULT_INVALID: result.questions[0].event: E8: event 'let the milk spill' opens on 'let', blame",
                 "RESULT_INVALID: result.questions[0].event: E2: event 'typed site walk notes' is 11 words",
                 "JOB_FAILED: result.questions[0].event: E7: event 'x' is the routine ('y')", None, ""):
        assert cs.gate_refusal(said) is None, said
    assert cs.gate_refusal("result.questions[0].event: E7: event 'x' is the routine ('y')") is None


class _FailedJourney:
    """A journey whose PROBLEM calibration is refused for good: no retries left (the strict walk's)."""

    def __init__(self, diagnostic: str, retries: int = 0):
        self.diagnostic, self.retries, self.patience = diagnostic, retries, 1.0
        self.gate_refusals, self.findings = [], []

    def project(self, path: str) -> str:
        return "/v2/projects/p" + path

    def get(self, path: str) -> dict:
        if "/calibration/" in path:
            return {"state": "FAILED", "interactionId": "i1"}
        return {"status": "RESULT_INVALID", "diagnostic": self.diagnostic}


def test_the_walk_stops_on_e7_by_name_and_the_record_keeps_the_rule():
    """FR-2 / FR-7: a gate refused past the repair turn stops the walk with the rule in the step's error, and
    `backtest.json` carries every gate refusal (`gate_refusals`) and the one it stopped on (`stop_rule`)."""
    j = _FailedJourney(REFUSED[0][0].split(": ", 1)[1])
    with pytest.raises(AssertionError) as stop:
        cs._wait_calibration(j, "PROBLEM", timeout_s=5)
    assert "PROBLEM's calibration questions FAILED -- stopped by E7 (the segment, keel-cloud 238 FR-1) past the repair " \
           "turn: RESULT_INVALID: result.questions[0].event: E7: event 'sign the cards" in str(stop.value)
    assert [(r["rule"], r["refusal"], r["stopped"]) for r in j.gate_refusals] == [("E7", "the segment", True)]
    assert bt.gate_stop(j) == {"rule": "E7", "refusal": "the segment", "spec": "keel-cloud 238 FR-1",
                               "vector": "PROBLEM", "path": "result.questions[0].event"}
    md = bt.markdown({"entry": {"id": "x"}, "passed": False, "failed_step": "leg_calibrate PROBLEM",
                      "stop_rule": bt.gate_stop(j)})
    assert "stopped at: leg_calibrate PROBLEM -- **stopped by E7** (the segment, keel-cloud 238 FR-1) on PROBLEM" in md
    # another rule stops the walk as before, unnamed
    other = _FailedJourney("result.questions[0].event: E2: event 'x' is 11 words")
    with pytest.raises(AssertionError, match=r"^PROBLEM's calibration questions FAILED: RESULT_INVALID: "):
        cs._wait_calibration(other, "PROBLEM", timeout_s=5)
    assert other.gate_refusals == [] and bt.gate_stop(other) is None


def test_the_lock_notes_name_e7_e8_e9():
    """FR-2: the lock notes read E7 (a repair turn's refusal), E8 (a note: blame, a verdict) and E9 by name, each
    meaning naming keel-cloud 238; E8's says it is served, never a stop."""
    rows = [{"screen": "CALIBRATION_QUESTIONS", "detail": "breach result.questions[0].event: E8: event 'let the milk "
                                                          "spill' opens on 'let', blame -- what happened to them"},
            {"screen": "CALIBRATION_QUESTIONS", "turns": [{"content": REFUSED[0][0].split(": ", 2)[2]}]},
            {"screen": "CALIBRATION_QUESTIONS", "diagnostic": REFUSED[3][0].split(": ", 2)[2]}]
    found = bt.lock_notes(None, rows)
    assert [n["rule"] for n in found] == ["E8", "E7", "E9"]
    assert "never a stop" in bt.LOCK_NOTES["E8"] and "238 FR-4" in bt.LOCK_NOTES["E8"]
    assert "a named stop" in bt.LOCK_NOTES["E7"] and "238 FR-1" in bt.LOCK_NOTES["E7"]
    assert "238 FR-2" in bt.LOCK_NOTES["E9"]


def test_a_served_gate_inside_the_segment_is_a_finding():
    """FR-2 (238 FR-1, the mirror's own test): a served gate whose every word is the context's circumstance's asks what
    every one of them does -- read off the served text; the act that hurts, or a negation, is not."""
    assert wording_mod.gate_clause("In the last 7 nights, did you have to work out why your baby was crying?") == \
        "have to work out why your baby was crying"
    assert wording_mod.gate_clause("In the last 5 working days, did a booking call ring out?") == \
        "a booking call ring out"
    assert wording_mod.gate_clause("Did it?") is None
    assert wording_mod.inside_the_segment("sign the cards for the bouquets", WRAPPED, FLORISTS) == \
        ["sign", "cards", "bouquets"]
    assert wording_mod.inside_the_segment("sign the cards after the van had gone", WRAPPED, FLORISTS) is None
    assert wording_mod.inside_the_segment("have a bouquet go out without its card", "the bouquets go out", FLORISTS) \
        is None


@pytest.fixture(scope="module")
def golden() -> dict:
    from harness import vectors_script as vs                               # noqa: PLC0415
    from instructions import corpus as corpus_mod                          # noqa: PLC0415
    if not corpus_mod.corpus_dir(KEEL_CLOUD).is_dir():
        pytest.skip(f"no corpus at {KEEL_CLOUD}")
    return {e.id: e for e in vs.load(KEEL_CLOUD).entries}


#: The golden entries the scripted journeys walk (S-005 Countly, S-006 / S-014 Paidly, S-007 Mulchrun, S-015 / S-016
#: Countly's seeds); Lullaby is walked live only (S-012, the host's model).
WALKED = ("01-countly", "05-paidly", "07-mulchrun")


def test_every_scripted_gate_holds_238(golden):
    """FR-2 (238 FR-1 to FR-3): every golden scripted Prevalence holds E7 on the context's circumstance and, at the
    project step, the founder's seed (the entry's problem statement), its no-sayer E9 and its served gate is never
    the segment -- except Lullaby's *work* (the founder's job's word, none of 238's four sources: judgement call), never
    walked on the scripted runtime."""
    from harness import vectors_script as vs                               # noqa: PLC0415
    for entry_id, (event, gate) in vs.PROBLEM_CLAUSES.items():
        entry = golden[entry_id]
        ctx = vs._ctx(entry)
        routine, went_wrong = vs.act_that_hurts(entry)
        seed = " ".join(str(entry.statements["problem"]).split())
        fault = wording_mod.routine_fault(event, routine, went_wrong, ctx.get("actor_plural"), ctx.get("circumstance"),
                                          seed)
        if entry_id == "03-lullaby":
            assert fault == wording_mod.new_word_fault(event, "work") and "work" in ctx["job"], fault
            assert entry_id not in WALKED
        else:
            assert fault is None, (entry_id, fault)
        assert wording_mod.routine_fault(event, routine, went_wrong, ctx.get("actor_plural"),
                                         ctx.get("circumstance")) is None, entry_id
        assert wording_mod.inside_the_segment(gate, ctx.get("circumstance"), ctx.get("actor_plural")) is None, entry_id
        assert wording_mod.no_sayer_fault(vs.no_sayer(entry), routine, went_wrong, ctx.get("circumstance"),
                                          ctx.get("actor"), ctx.get("actor_plural")) is None, entry_id


#: The instruction files' bytes at the round's final sha (238: respondent-questions 9,952, problem-interpret 15,391;
#: 239: respondent-questions 9,957; 240: solution-mechanism 8,747) -- recorded here, where the eval read them.
INSTRUCTION_BYTES = {"respondent-questions.md": 9_957, "problem-interpret.md": 15_391, "solution-mechanism.md": 8_747}


def test_the_instruction_bytes_are_the_rounds():
    for name, size in INSTRUCTION_BYTES.items():
        path = KEEL_CLOUD / "src/main/resources/keel/inference-instructions" / name
        if not path.is_file():
            pytest.skip(f"no {name} at {KEEL_CLOUD}")
        assert path.stat().st_size == size, name
    assert INSTRUCTION_BYTES["respondent-questions.md"] <= 9_969          # 170's cap


# ------------------------------------------------------------------------------- FR-3 Existing sacrifice (239)

from harness import vectors_script as vs                                    # noqa: E402


def _rate(measure, base, unit, period, line):
    return {"mode": "RATE", "low": 3, "high": 5, "measure": measure, "base": base, "unit": unit, "period": period,
            "currency": "USD", "lossPhrase": line}


#: `ExistingSacrificeNamesTheThingTest`'s three invented shapes.
RANG_OUT = _rate("%", "the after-hours enquiries", "clinic", "month", "Enquiries that rang out unanswered")
GAVE_UP = _rate("%", "the stored harvest", "farm", "year", "Value they gave up by holding the harvest in storage too long")
LOST_TRACK = _rate("recipes", "the recipes they save", "household", "month", "Recipes they lost track of")
BANNED = ("go without", "goes without", "went without", "fell through", "fall through", "lose", "lost", "miss",
          "missed")


def test_the_three_shapes_after_two_failures_are_the_clouds():
    """FR-3 (239 FR-2, `Fr2ThePlainNotDone`): with no clause landed, code's plain not-done -- never the banned verb --
    else the founder's own line said to the person, and the Check says so."""
    assert vs.cost_question(True, "shift", None, RANG_OUT) == \
        "Last month, about what percent of the after-hours enquiries per clinic did not get answered?"
    assert vs.cost_question(False, "night", None, {**LOST_TRACK, "unit": None}) == \
        "Last month, about how many recipes did you not keep track of?"
    served = vs.cost_question(True, "delivery", None, GAVE_UP)
    assert served == "Last year, about what percent of the stored harvest per farm was value you gave up?"
    assert vs.check_note(True, "delivery", GAVE_UP, served) == (
        f'{vs.AS_TYPED_NOTE} "{served}" Reword it as what happens to the thing, in their words.')
    assert vs.check_note(False, "night", LOST_TRACK, "Last month, about how many recipes did you not keep track of?") \
        is None
    assert vs.check_note(True, "delivery", GAVE_UP, None) is None
    for wanted in (RANG_OUT, GAVE_UP):
        assert vs.loss_clause_wanted(True, "shift", wanted) is True


def test_the_other_banned_verbs_and_the_place_rung():
    """FR-3 (239 FR-2, FR-3, `theOtherBannedVerbs`, `thePlaceRungIsGone`)."""
    assert vs.cost_question(True, "shift", None, _rate("%", "the export orders", "depot", "month",
                                                        "Export orders that fell through at customs")) == \
        "Last month, about what percent of the export orders per depot did not go through?"
    assert vs.cost_question(False, "night", None, _rate("nights", "the nights on call", None, "month",
                                                         "Nights of sleep they go without")) == \
        "Last month, about how many nights did you not get?"
    assert vs.cost_question(True, "shift", None, _rate("callbacks", "the callbacks booked", "office", "month",
                                                        "Callbacks they missed")) == \
        "Last month, about how many callbacks per office did you not get?"
    interest = _rate("%", "the balance", "company", "year", "Interest on cash that sits in the operating account")
    assert vs.loss_clause_wanted(True, "cash review", interest) is True
    assert vs.cost_question(True, "cash review", None, interest) == (
        "Last year, about what percent of the balance per company was interest on cash that sat in the operating "
        "account?")


def test_the_base_is_the_loss_lines_and_the_unit_is_kept():
    """FR-3 (239 FR-4, FR-5, `Fr4Fr5TheBaseAndTheUnit`)."""
    on_the_line = _rate("%", "the long-term reserve", "company", "year", "Interest on operating cash")
    assert vs.asked_base(on_the_line) == "the operating cash"
    assert "of the operating cash" in vs.cost_question(True, "cash review", None, on_the_line)
    assert vs.stranger_cost_label(on_the_line, "cash review", None, True) == \
        "% of the operating cash per company last year"
    assert vs.base_note(on_the_line) == "People are asked about the operating cash, the base your loss line names."
    assert vs.cost_question(True, "cash review", None, on_the_line, "earned no interest") == \
        "Last year, about what percent of the operating cash per company earned no interest?"
    assert vs.asked_base(RANG_OUT) == "the after-hours enquiries" and vs.asked_base(GAVE_UP) == "the stored harvest"
    assert vs.asked_base(_rate("%", "the operating account", "company", "year", "Interest on the operating account")) \
        == "the operating account"
    assert vs.asked_base(_rate("%", "the balance", "company", "year",
                               "Interest on cash that sits in the operating account")) == "the balance"
    assert vs.asked_base(LOST_TRACK) == "the recipes they save" and vs.base_note(RANG_OUT) is None
    idle = _rate("%", "the booked machine hours", "workshop", "month", "Booked machine hours that sit idle")
    assert vs.cost_question(True, "shift", None, idle) == \
        "Last month, about what percent of the booked machine hours per workshop sat idle?"
    assert vs.stranger_cost_label(idle, "shift", None, True) == "% of the booked machine hours per workshop last month"
    owned = _rate("%", "the workshop's machine hours", "workshop", "month", "Booked machine hours that sit idle")
    assert vs.cost_question(True, "shift", None, owned) == \
        "Last month, about what percent of the workshop's machine hours sat idle?"
    assert vs.stranger_cost_label(owned, "shift", None, True) == "% of machine hours per workshop last month"
    assert vs.cost_question(True, "shift", None, _rate("deals", "the deals in the pipeline", "sales team", "month",
                                                        "Deals lost to a faster competitor"),
                            "went to a faster competitor") == \
        "Last month, about how many deals per sales team went to a faster competitor?"
    assert "per household" not in vs.cost_question(False, "night", None, LOST_TRACK)
    long_unit = _rate("%", "the after-hours enquiries sent in by patients", "dental clinic", "month",
                      "Enquiries that rang out unanswered")
    assert len(vs.cost_question(True, "shift", None, long_unit).split()) <= vs.STEM_MAX_WORDS


def test_the_check_note_is_the_webs_fixture_shape():
    """FR-3 (239 FR-2, FR-4; keel-web 183 T008): `base_note` then `check_note`, one space, on an invented choir."""
    fees = _rate("%", "the choir's budget", "choir", "month", "Fees on rehearsal space")
    served = vs.cost_question(True, "rehearsal", None, fees)
    note = vs.sacrifice_note(True, "rehearsal", fees, served)
    assert vs.asked_base(fees) == "the rehearsal space" and "of the rehearsal space per choir" in served
    assert note.startswith("People are asked about the rehearsal space, the base your loss line names.")
    if vs.check_note(True, "rehearsal", fees, served) is not None:
        assert note == vs.base_note(fees) + " " + vs.check_note(True, "rehearsal", fees, served)
    assert vs.sacrifice_note(True, "shift", RANG_OUT, vs.cost_question(True, "shift", None, RANG_OUT)) is None


def test_no_served_item_says_a_banned_verb(golden):
    """FR-3 (239 FR-2): every corpus and back-test entry's chain item as served with no clause, and every rung code's
    fallback can serve on it, says no banned verb in any form -- the frames read for each word."""
    from instructions import corpus as corpus_mod                          # noqa: PLC0415
    entries = list(golden.values())
    if corpus_mod.backtest_dir(KEEL_CLOUD).is_dir():
        entries += vs.load(KEEL_CLOUD, backtest=True).entries
    checked = 0
    for entry in entries:
        item = vs.cost_item(entry)
        if not item:
            continue
        checked += 1
        assert vs.banned_word(item["question"]) is None, (entry.id, item["question"])
        cost = entry.cost()
        if cost.get("mode") == "RATE":
            for team in (True, False):
                over = cost.get("period") if cost.get("period") in vs._COST_OPENERS else "month"
                base = None if vs.asked_base(cost) is None else vs._said(vs.asked_base(cost), team)
                measure = vs.cost_measure(cost)
                share = measure is None or measure.strip() == "%"
                for rung in vs.loss_not_done_rungs(vs._COST_OPENERS[over], cost, base if share else None,
                                                   vs.per_unit(cost, team, base if share else measure),
                                                   None if share else measure):
                    assert vs.banned_word(rung) is None, (entry.id, rung)
    assert checked >= 20
    for word in BANNED:
        assert vs.banned_word(f"Last month, about how many calls did you {word} today?") is not None, word


def test_the_part_three_job_on_a_money_only_study(golden):
    """FR-3 (239 FR-1): on money alone part 3 is the lock's one model job where its item wants the clause -- on the
    decision-maker's link on B2B -- and its result carries `loss_clause` where the script holds one; a line code reads
    whole starts none; a study with part 1 keeps its job there."""
    import dataclasses                                                     # noqa: PLC0415
    from instructions import corpus as corpus_mod                          # noqa: PLC0415
    if not corpus_mod.backtest_dir(KEEL_CLOUD).is_dir():
        pytest.skip("no back-test entries")
    backtest = {e.id: e for e in vs.load(KEEL_CLOUD, backtest=True).entries}
    money = {k: dataclasses.replace(e, scope="COMMERCIAL") for k, e in backtest.items()}
    assert vs.respondent_jobs(money["21-codyco"]) == [(3, vs.LINK_B2B)]
    assert vs.respondent_jobs(money["10-palus"]) == [(3, vs.LINK_B2B)]
    assert vs.respondent_jobs(money["13-aircaps"]) == [(3, vs.LINK_PRIMARY)]
    assert vs.respondent_jobs(money["17-expanse"]) == []                   # the line code reads whole
    assert vs.respondent_jobs(backtest["21-codyco"]) == [(1, vs.LINK_PRIMARY)] or not vs.serves_gate(
        backtest["21-codyco"])
    for entry in golden.values():                                           # off the chain: as before
        assert vs.respondent_jobs(dataclasses.replace(entry, scope="COMMERCIAL")) == []
    codyco = money["21-codyco"]
    assert "loss_clause" not in vs.respondent_result(codyco, 3, vs.LINK_B2B)
    held = dict(vs.LOSS_CLAUSES)
    try:
        vs.LOSS_CLAUSES["21-codyco"] = "rang out unanswered"
        assert vs.respondent_result(codyco, 3, vs.LINK_B2B)["loss_clause"] == "rang out unanswered"
        assert "loss_clause" not in vs.respondent_result(codyco, 3, vs.LINK_PRIMARY)
        assert vs.cost_item(codyco)["question"] == \
            "Last month, about what percent of the reservation calls per hotel rang out unanswered?"
    finally:
        vs.LOSS_CLAUSES.clear()
        vs.LOSS_CLAUSES.update(held)


class _Walk:
    def __init__(self, view):
        self.view, self.findings = view, []

    def project(self, path):
        return path

    def get(self, path):
        return self.view


def test_the_walk_names_the_check_note_and_a_banned_verb_never_a_stop(golden):
    """FR-3: the Check's note is a finding with its words (as typed / the base), and a served banned verb a fault named
    in the findings -- the walk goes on."""
    note = (f'{vs.AS_TYPED_NOTE} "Last year, about what percent of the stored harvest per farm was value you gave up?" '
            "Reword it as what happens to the thing, in their words.")
    j = _Walk({"questions": [{"dimension": "commercial.price"},
                             {"dimension": "commercial.existing_sacrifice", "note": note}]})
    found = cs.sacrifice_note_finding(j)
    assert found == {"what": cs.SACRIFICE_NOTE, "note": note, "as_typed": True, "base": False} and j.findings == [found]
    assert cs.sacrifice_note_finding(_Walk({"questions": [{"dimension": "commercial.existing_sacrifice"}]})) is None
    walk = _Walk({})
    walk.entry = golden["01-countly"]
    cs.cost_item_drift(walk, {"dimension": "commercial.existing_sacrifice",
                              "question": "Last month, about how many deliveries fell through?"})
    assert [f for f in walk.findings if f["what"] == cs.SACRIFICE_BANNED] == [
        {"what": cs.SACRIFICE_BANNED, "said": "fell through",
         "served": "Last month, about how many deliveries fell through?"}]


def test_the_lossnotdone_words_are_the_clouds():
    """FR-3: the neutral phrases, the card's banned verbs' plain not-done and the note's opening, word for word."""
    text = re.sub(r'"\s*\+\s*"', "", _cloud(VECTORS + "LossNotDone.java"))
    phrases = text.split("NEUTRAL_PHRASES = List.of(", 1)[1].split(");", 1)[0]
    assert tuple(re.findall(r'"([^"]+)"', phrases)) == vs.NEUTRAL_PHRASES
    assert 'new NotDone("keep", false, 1)' in text and 'new NotDone("go through", true, 2)' in text
    chain = re.sub(r'"\s*\+\s*"', "", _cloud(VECTORS + "CommercialChain.java"))
    assert f'AS_TYPED_NOTE = "{vs.AS_TYPED_NOTE}"' in chain
    assert '"People are asked about " + line + ", the base your loss line names."' in chain


# ------------------------------------------------------------------------------- FR-4 the reveal heard once (240)

FRAME = "The people building it believe it would "


def test_m8_hears_what_the_cloud_hears():
    """FR-4 (240 FR-4, `IdeaLines.saidTwice`; tasks.md's two reveals): one check over name, what line, how and belief --
    the what line's phrase or kind said again on the how, the how said again in the belief; the redrafts heard once."""
    assert vs.said_twice(None, "a pantry app that reads receipts", "After a shop, the pantry app reads your receipt.",
                         FRAME + "list what runs low before the next shop.") == [("pantry app", "how")]
    assert vs.said_twice("Sproutcap", "a soil probe that tells you when a bed needs water",
                         "When you plant a bed, you push your soil probe into it. Your probe pairs to your phone.",
                         FRAME + "save 20 percent of the water your clock uses.") == [("soil probe", "how")]
    assert vs.said_twice("Shelfwise", "a pantry app that reads receipts", "After a shop, you snap the receipt. It keeps "
                         "a count of each item. Before the next shop, it lists what runs low.",
                         FRAME + "mean nothing is bought twice.") == []
    assert vs.said_twice("Sproutcap", "a soil probe that tells you when a bed needs water",
                         "When you plant a bed, you push it into the soil. It pairs to your phone.",
                         FRAME + "target 20 percent less water than watering by the clock.") == []
    shelf = vs.said_twice(None, "a pantry app that reads receipts", "After a shop, you snap the receipt. Before the "
                          "next shop, it lists what runs low.", FRAME + "list what runs low before the next shop.")
    assert shelf == [("runs low", "belief"), ("next shop", "belief")]
    assert vs.kind_of("an AI reservation agent for missed hotel calls") == "agent"
    assert vs.kind_of("an app on lightweight glasses that shows live captions") == "app"
    assert vs.said_twice(None, "a tool", "It is government-backed. A government-backed fund.", None) == \
        [("government-backed", "how")]


def test_m8_breaches_carry_the_lines_path_and_the_clouds_words():
    """FR-4: each breach on the path of the line it is heard again in, worded as `ScreenResultApplier` words it; the
    back-test's lock notes read it whole (`M8: 'X'[, 'Y'] is|are heard again in the (what line|how line|belief)`)."""
    got = vs.m8_breaches(None, "a pantry app that reads receipts", "After a shop, the pantry app reads your receipt.",
                         FRAME + "list what runs low before the next shop.", how_decider="Before the next shop, "
                         "the pantry app lists what runs low.")
    assert [g[0] for g in got] == ["result.idea_how.primary", "result.idea_how.decider", "result.idea_belief"]
    assert got[0][1].startswith("M8: 'pantry app' is heard again in the how line; the name, what it is, the how and "
                                "the belief are one reveal heard in a row")
    applier = " ".join(re.sub(r'"\s*\+\s*"', "", _cloud(APPLICATION + "ScreenResultApplier.java")).split())
    assert '" heard again in the " + (where.equals("what") ? "what line" : where.equals("how") ? "how line" : ' \
           '"belief") + "; the name, what it is, the how and the belief are one reveal heard in a row, so each thing ' \
           'is said once -- the what line\'s kind is \'it\' after it, and the belief points back (\'all of that\')"' \
        in applier
    rows = [{"screen": "SOLUTION_MECHANISM", "detail": "breach result.idea_how.primary: " + got[0][1]},
            {"screen": "SOLUTION_MECHANISM", "detail": "breach result.idea_belief: M8: 'runs low', 'next shop' are "
                                                      "heard again in the belief; the name ..."},
            {"screen": "SOLUTION_MECHANISM", "detail": "M8: the belief names PMS, OPERA Cloud again"}]
    notes = bt.lock_notes(None, rows)
    assert [n.get("heard_again") for n in notes] == [
        {"words": ["pantry app"], "line": "how line", "path": "result.idea_how.primary"},
        {"words": ["runs low", "next shop"], "line": "belief", "path": "result.idea_belief"}, None]
    assert "keel-cloud 240 FR-4" in bt.LOCK_NOTES["M8"] and "heard twice across the reveal" in bt.LOCK_NOTES["M8"]
    assert bt.m8_heard_again("M8: 'Codyco' is heard again in the what line") == \
        {"words": ["Codyco"], "line": "what line", "path": "result.idea_what"}


def test_the_scripted_reveals_are_heard_once(golden):
    """FR-4 (240's owed list): every golden scripted reveal -- the what line Keel suggests, the how, the belief -- says
    nothing twice, so no scripted result spends a repair turn; the walked three (Countly, Paidly's redrafted how aside,
    Mulchrun) keep their lines where they already held."""
    for entry in golden.values():
        lines = vs.idea_lines(entry)
        what = entry.idea_what() or vs.short_name(entry)
        assert vs.m8_breaches(vs.seed_named(entry.statements.get("solution")), what, lines["how"],
                              lines["belief"]) == [], entry.id
        assert lines["belief"].startswith(FRAME) and len(lines["how"].split(". ")) <= 5
    m = golden["01-countly"].solution_mechanism
    assert vs.idea_lines(golden["01-countly"])["how"] == vs._sentence(
        f"{m['trigger']}, {m['actor']} {m['mechanism']}; it gives {m['output']}.")
    assert vs.idea_lines(golden["02-compliancelog"])["belief"] == FRAME + vs.BELIEF_POINTS_BACK


def test_the_walk_reads_the_served_reveal_and_the_hedge():
    """FR-4 (240 FR-1, FR-4): the served reveal said twice is a finding on its path; the belief keeps the founder's verb
    after *would* (*would target*, never *would earn*) -- a finding, never a stop."""
    seed = "Sproutcap is a soil probe. We target 20% less water than watering by the clock."
    assert cs.belief_hedge_dropped(FRAME + "earn 20 percent less water use.", seed) == {"hedge": "target",
                                                                                       "said": "earn"}
    assert cs.belief_hedge_dropped(FRAME + "target 20 percent less water than watering by the clock.", seed) is None
    assert cs.belief_hedge_dropped(FRAME + "save water.", "A soil probe that tells you when to water.") is None

    class _J:
        findings: list = []
        founder = type("F", (), {"solution_seed": seed})()
        entry = None
    j = _J()
    j.findings = []
    seen = {"typed": "Sproutcap", "lines": {"whatItIs": "a soil probe that tells you when a bed needs water",
                                            "how": "When you plant a bed, you push your soil probe into it.",
                                            "belief": FRAME + "earn 20 percent less water use."}}
    found = cs.reveal_heard_once(j, seen)
    assert [f["what"] for f in found] == [cs.M8_SERVED, cs.HEDGE_SERVED] and j.findings == found
    assert found[0]["path"] == "result.idea_how.primary" and found[0]["said"] == \
        "M8: 'soil probe' is heard again in the how line"


def test_the_guidelines_and_the_instruction_say_heard_once():
    """FR-4 (240 FR-4, FR-6): guidelines §23 and the instruction's closing check, as the cloud wrote them."""
    guidelines = _cloud("canon/designs/spoken-questions-guidelines.md")
    assert "## 23. Amendment of 2026-11-09 (keel-cloud spec 240): the reveal is heard once, name to belief" in guidelines
    instruction = " ".join(_cloud("src/main/resources/keel/inference-instructions/solution-mechanism.md").split())
    assert "Say the reveal aloud once: nothing twice, nothing brought *your*." in instruction


# ------------------------------------------------------------------------------- FR-5 Ability to pay (241)

ABILITY_LABELS_241 = {"existing_line": "An existing budget line", "charged_to_users": "Charged back to whoever uses it",
                      "new_line_signed_off": "A new budget line, signed off for it",
                      "outside_funding": "New money from outside, such as a grant",
                      "taken_from_other_spend": "Taken from other spending"}


def test_ability_to_pays_labels_are_241s_codes_unchanged():
    """FR-5 (241 FR-1): the registry serves the two new labels under their old codes, in order; no served label names a
    unit of one kind of organisation; the walk's sides (`BUDGET_SUPPORTS`) read the codes, unmoved."""
    import json                                                             # noqa: PLC0415
    from harness import vectors_screens as vs_screens                      # noqa: PLC0415
    from tests.test_dimension_cards_131 import EXAMPLES                    # noqa: PLC0415
    registry = json.loads(_cloud("src/main/resources/keel/dimension-registry.json"))
    entries = registry.get("dimensions") or registry.get("entries") or registry
    row = next(d for d in (entries if isinstance(entries, list) else entries.values())
               if isinstance(d, dict) and d.get("key") == "commercial.ability_to_pay")
    found = {o.get("code"): o.get("label") for o in _options(row)}
    assert found == ABILITY_LABELS_241, found
    for label in found.values():
        assert not re.search(r"(?i)\b(teams?|sites?|departments?|branch(es)?)\b", label), label
    good = EXAMPLES["commercial.ability_to_pay"]["good"]
    assert dict(zip(good["codes"], good["options"])) == ABILITY_LABELS_241
    assert vs_screens.BUDGET_SUPPORTS == ("from_spend", "existing_line", "charged_to_users", "taken_from_other_spend")


def _options(row: dict) -> list:
    """Every `{code, label}` an entry carries, wherever the registry nests its options."""
    out: list = []

    def walk(node):
        if isinstance(node, dict):
            if "code" in node and "label" in node and isinstance(node.get("label"), str):
                out.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(row)
    return [o for o in out if o["code"] in ABILITY_LABELS_241]


# ------------------------------------------------------------------------------- FR-6 the window question (web 183)

WHO_183 = "Volunteer choir leader"
PEOPLE_183 = "volunteer choir leaders"
WHEN_183 = "rehearsal starts and half the singers have not got the new score"
FALLBACK_183 = f"How far back should {PEOPLE_183} look for the last time it happened?"


def test_the_typed_when_is_the_clause_before_the_read():
    """FR-6 (keel-web 183 FR-1, `window-names-the-moment-183.test.tsx` case for case)."""
    from harness import vectors_screens as vss                             # noqa: PLC0415
    assert vss.typed_when_clause_of(WHEN_183) == f"the last time {WHEN_183}"
    assert vss.window_label_of(WHO_183, typed_when=WHEN_183) == \
        f"How far back should {PEOPLE_183} look for the last time {WHEN_183}?"
    assert vss.typed_when_clause_of("  When rehearsal starts   and half the singers have not got the new score.  ") \
        == f"the last time {WHEN_183}"
    assert vss.typed_when_clause_of("Whenever the hall is double-booked") == "the last time the hall is double-booked"
    assert vss.typed_when_clause_of("The week before a concert, with the programme still not printed") == \
        "the last time the week before a concert, with the programme still not printed"
    assert vss.typed_when_clause_of("Saturday rehearsals run past the hall's booking") == \
        "the last time Saturday rehearsals run past the hall's booking"
    assert vss.typed_when_clause_of("After the warm-up, the altos are still missing") == \
        "the last time after the warm-up, the altos are still missing"
    assert vss.typed_when_clause_of("You hand out the parts and your copies run short") == \
        "the last time they hand out the parts and their copies run short"
    assert vss.typed_when_clause_of("the singers arrive and you're still setting up") == \
        "the last time the singers arrive and they're still setting up"
    assert vss.typed_when_clause_of("a singer emails you the night before") is None
    assert vss.window_label_of(WHO_183, typed_when="a singer emails you the night before") == FALLBACK_183
    for blank in (None, "   ", "When."):
        assert vss.typed_when_clause_of(blank) is None, blank
    assert vss.window_label_of(WHO_183) == FALLBACK_183
    # FR-2: after the read, its clauses first
    read = ("Volunteer choir leaders at community choirs. When a rehearsal starts and half the singers do not have the "
            "new score, they want to start on time with everyone singing. We'll ask about the last 2 weeks.")
    assert vss.window_label_of(WHO_183, understands=read, typed_when=WHEN_183) == (
        f"How far back should {PEOPLE_183} look for the last time a rehearsal starts and half the singers do not have "
        "the new score?")
    assert vss.window_label_of(WHO_183, "a rehearsal", read, WHEN_183) == \
        f"How far back should {PEOPLE_183} look for a rehearsal?"


def test_the_window_question_is_one_plain_sentence():
    """FR-6 (keel-web 183 FR-3, `windowPeopleOf`): the people up to the first comma or semicolon, in the plural."""
    from harness import vectors_screens as vss                             # noqa: PLC0415
    comma = ("Choir leaders at community choirs in the county, who rehearse every week, singing with a pianist or a "
             "backing track")
    assert vss.window_people_of(comma) == "choir leaders at community choirs in the county"
    assert vss.window_label_of(comma, typed_when=WHEN_183) == \
        f"How far back should choir leaders at community choirs in the county look for the last time {WHEN_183}?"
    assert vss.window_people_of("A volunteer choir leader; mostly unpaid") == PEOPLE_183
    assert vss.window_people_of(WHO_183) == PEOPLE_183
    assert vss.window_people_of("Parents of babies under six months") == "parents of babies under six months"
    assert vss.window_people_of("A choir leader who runs two choirs") == "choir leaders who run two choirs"
    assert vss.window_people_of("") == "people"
    # the web's own owed example: Codyco's walk, its typos the persona file's
    assert vss.window_label_of("reservation agent", typed_when="bokoing calls come in on every shift, after hours, at "
                               "peak and on holidays, and not every one gets answeed") == (
        "How far back should reservation agents look for the last time bokoing calls come in on every shift, after "
        "hours, at peak and on holidays, and not every one gets answeed?")


def test_the_window_page_holds_the_typed_when_and_the_note_hook():
    """FR-6: on the walk's 2 of 2 the heading is the typed when's (a fault where it reads *the last time it happened*
    over a typed when, or parts from the mirror); the note hook and 2 of 2's read-back."""
    from harness import vectors_screens as vss                             # noqa: PLC0415
    window = {"count": 7, "unit": "NIGHTS"}
    drawn = {"screen": "window", "counter": "2 of 2", "count": "", "unit": "", "pressed": []}
    typed = {"actor": WHO_183, "circumstance": WHEN_183}
    good = {"drawn": {**drawn, "question": vss.window_label_of(WHO_183, typed_when=WHEN_183)},
            "picked": {"count": "7", "unit": "NIGHTS"}}
    assert cs.window_page_faults(good, window, typed) == []
    old = {"drawn": {**drawn, "question": FALLBACK_183}, "picked": {"count": "7", "unit": "NIGHTS"}}
    assert [f["rule"] for f in cs.window_page_faults(old, window, typed)] == [
        "keel-web 183 FR-1: the typed when, never the last time it happened"]
    assert cs.window_page_faults(old, window) == []                         # no typed fields in hand: 162's shape alone
    assert vss.SACRIFICE_NOTE_TESTID == "sacrifice-note"
    web = _web("src/components/calibration/CalibrationPage.tsx")
    assert 'data-testid="sacrifice-note"' in web and 'id="sacrifice-note"' in web
    assert bt.read_back(None, "context-window", {"context": {"understands": "X."}}) == {
        "understands": None, "summary": bt.CONTEXT_WINDOW_NO_SUMMARY, "next_screen_understands": "X."}
    source = _web("src/lib/contextReach.ts")
    assert "export function typedWhenClauseOf" in source and "export function windowPeopleOf" in source


# ------------------------------------------------------------------------------- FR-7 the record

def test_the_record_cites_round_a_and_names_the_gate_stops(tmp_path):
    """FR-7: on a record of 148's walks (bundles that record `gate_refusals`) the review line cites keel-cloud 238 to 241
    and a gate line counts the E7 / E9 refusals and names each walk stopped by rule; a record before 148 reads as 147
    wrote it."""
    import json                                                             # noqa: PLC0415
    from quality import cycle                                              # noqa: PLC0415
    from tests.test_record_review_147 import BUNDLES, _walk                 # noqa: PLC0415
    stop = {"rule": "E7", "refusal": "the segment", "spec": "keel-cloud 238 FR-1", "vector": "PROBLEM",
            "path": "result.questions[0].event"}
    bundles = {"17-expanse": {**BUNDLES["17-expanse"], "gate_refusals": []},
               "21-codyco": {**BUNDLES["21-codyco"], "gate_refusals": [{**stop, "said": "E7: ...", "stopped": False},
                                                                       {**stop, "said": "E7: ...", "stopped": True}],
                             "stop_rule": stop}}
    studies = [_walk(tmp_path, e, b) for e, b in bundles.items()]
    assert (studies[0].gate_refused, studies[0].stop_rule) == (0, None)
    assert studies[1].gate_refused == 2 and studies[1].stop_rule == {k: stop[k] for k in
                                                                     ("rule", "refusal", "spec", "vector")}
    kw = dict(name="20261110-155eaca", why="spec 148", door="keel", cloud_sha="155eaca", web_sha="36d069e",
              started="s", ended="e", seconds=1.0, cfg=cycle.load_config(), baseline_path=tmp_path / "BASELINE.md",
              cycles_dir=tmp_path, decisions=[])
    text, _ = cycle.compose(studies, review="ON", **kw)
    review = next(x for x in text.splitlines() if x.startswith("  - the review (spec 209"))
    assert review.startswith("  - the review (spec 209, keel-cloud 232, 233, 235, 236, 237, 238, 239, 240, 241): ")
    gate = next(x for x in text.splitlines() if x.startswith("  - the gate (keel-cloud 238"))
    assert gate == ("  - the gate (keel-cloud 238, 239, 240, 241: the round's mirrors, spec 148): 2 E7 / E9 refusals of "
                    "Keel's AI over 2 walks (each bundle's `gate_refusals`, retried as the founder's screen retries); "
                    "stopped by rule on 1: 21-codyco · SOLUTION E7 (the segment, keel-cloud 238 FR-1)")
    path = tmp_path / "20261110-155eaca.md"
    path.write_text(text, encoding="utf-8")
    rendered = cycle.render_record(cycle.load_record(path)).splitlines()
    assert review in rendered and gate in rendered
    before = [_walk(tmp_path / "before", e, b) for e, b in BUNDLES.items()]
    old, _ = cycle.compose(before, review="ON", **{**kw, "cycles_dir": tmp_path / "before"})
    assert "keel-cloud 238" not in old and "  - the gate (" not in old
    assert "gate_refused" not in cycle._study_data(before[0])
    assert json.dumps(cycle._study_data(studies[1]))
