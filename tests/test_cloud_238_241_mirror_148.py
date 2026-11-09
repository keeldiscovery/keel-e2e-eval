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
