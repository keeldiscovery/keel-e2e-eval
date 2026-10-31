"""Spec 094 -- IM2 knows the staging switch: the lock screen's one switch label is the screen's own words too.

keel-web 132 FR-2 draws, where the server serves `recordOnSend: true` (staging's overlay sets
`KEEL_V2_INTERVIEWER_LOCK_RECORD_OPTIONAL=true`), one switch at the top of the lock card:
`<label class="before__switch" data-testid="record-at-lock"><input type="checkbox" role="switch" checked>
<span>Record {face} at lock · 400 credits</span></label>`. The eval stack never sets the variable, so the switch's shape
is held here, built from keel-web's source words: IM2 with the switch drawn (staging's shape) and without (the local
stack's). Stackless.
"""

from __future__ import annotations

import inspect
import re

import pytest

from evals import interviewer_leg as leg
from evals import interviewer_marks as im
from harness import vectors_screens as vs_screens
from harness.steps import Recorder
from stack.config import load_config

WEB = load_config(validate=False).keel_web


def _web_source(relative: str) -> str:
    path = WEB / relative
    if not path.is_file():
        pytest.skip(f"keel-web is not checked out at {WEB}")
    return path.read_text(encoding="utf-8")


record_at_lock_switch = vs_screens.record_at_lock_switch      # keel-web 132 `recordAtLockSwitch`, held below


SUB = ("Daphne is picked for you. Tap the other face to hear Saskia and pick Saskia instead. Keel records Daphne once "
       "for this project, which uses 400 credits. People get the link by text message either way. The voice goes "
       "with the face.")


def _lock(switch: str | None = None) -> str:
    """L1 as the leg reads it (the main column's whole text, `textContent` with whitespace folded): the title, the sub
    (keel-web 130 / 132 `beforeInterviewerSub`), staging's switch as the card's first child where it is drawn -- with no
    space between the sub's last word and the label, as `textContent` joins sibling elements -- the faces, the button."""
    card = (switch or "") + "Daphne Saskia"
    return f"Who should ask them your questions?{SUB}{card} Lock and record Daphne"


def _record(l1: str, served: int = 400) -> dict:
    return {"screens": {"L1": l1, "S1": "Saskia asks your questions.",
                        "S2": f"Recorded today at 16:02. {im.CHANGE_ACTION}", "S3": "AI interviewer · Saskia"},
            "wire_views": [{"changePrice": served}]}


# ------------------------------------------------------------------------------ the words, from keel-web's checkout

def test_the_switch_label_is_keel_webs_words():
    """keel-web 132 FR-2: `recordAtLockSwitch` is *Record {face} at lock · {credits} credits*, and the lock card draws
    it inside `<label className="before__switch" data-testid="record-at-lock">` with a `role="switch"` checkbox, only
    where the server serves `recordOnSend: true` (`lockOptional`), with the served `changePrice`."""
    translate = _web_source("src/lib/translate.ts")
    assert ("export const recordAtLockSwitch = (face: string, credits: number): string => "
            "`Record ${face} at lock · ${credits} credits`;") in translate
    assert record_at_lock_switch("Daphne", 400) == "Record Daphne at lock · 400 credits"
    step = _web_source("src/components/corridor/BeforeStep.tsx")
    assert im.LOCK_SWITCH_TESTID == vs_screens.RECORD_AT_LOCK == "record-at-lock"
    assert f'data-testid="{im.LOCK_SWITCH_TESTID}"' in step and 'className="before__switch"' in step
    assert 'role="switch"' in step and "checked={!recordOnSend}" in step
    assert "faces.data?.recordOnSend === true" in step
    assert re.search(r"recordAtLockSwitch\(pickedFace\?\.name \?\? \"the interviewer\", faces\.data\.changePrice\)",
                     step)


@pytest.mark.parametrize("face", ["Daphne", "Saskia", "the interviewer"])
def test_the_label_pattern_reads_every_label_keel_web_draws(face):
    """The face picked (*the interviewer* before one is) and the served price: the pattern reads each whole."""
    label = record_at_lock_switch(face, 400)
    m = im.LOCK_SWITCH_LABEL.fullmatch(label)
    assert m and m.group("credits") == "400", label
    assert im.PRICE_WORD.search(label), "the word IM2 would catch before v16"


# ----------------------------------------------------------------------------------------- FR-1: IM2 on L1

def test_without_the_switch_im2_reads_as_091_left_it():
    """The local stack's shape (`recordOnSend: false`, production's too): no switch drawn, the sub's sentence alone."""
    assert im.LOCK_SWITCH_LABEL.search(_lock()) is None
    assert im.price_words_on("L1", _lock()) == []
    ok, detail = im.no_price_shown(_record(_lock()))
    assert ok, detail
    assert detail["L1 credits sentence"] == "Keel records Daphne once for this project, which uses 400 credits."
    assert detail["L1 switch"] is None


def test_with_the_switch_im2_reads_its_label_as_the_screens_own_words():
    """Staging's shape (`recordOnSend: true`): the switch's label beside the sub's sentence, both at the served
    `changePrice`; IM2 met, and it names the label it read."""
    l1 = _lock(record_at_lock_switch("Daphne", 400))
    assert im.LOCK_SWITCH_LABEL.search(l1)
    assert im.price_words_on("L1", l1) == []
    ok, detail = im.no_price_shown(_record(l1))
    assert ok, detail
    assert detail["L1 switch"] == "Record Daphne at lock · 400 credits"
    assert detail["L1 credits sentence"] == "Keel records Daphne once for this project, which uses 400 credits."


def test_the_label_follows_a_pick_and_the_served_price():
    """The label names the face picked (Saskia) and the price the wire served, whatever it is."""
    l1 = _lock(record_at_lock_switch("Saskia", 1250)).replace("uses 400 credits", "uses 1,250 credits")
    assert im.price_words_on("L1", l1, {1250}) == []
    assert im.no_price_shown(_record(l1, 1250))[0]


def test_a_second_switch_faults():
    """Only one switch is the screen's own."""
    l1 = _lock(record_at_lock_switch("Daphne", 400) + record_at_lock_switch("Saskia", 400))
    words = im.price_words_on("L1", l1)
    assert words == ["a second switch: 'Record Saskia at lock · 400 credits'"], words
    assert not im.no_price_shown(_record(l1))[0]


def test_a_label_with_another_number_faults():
    """The only number in the label is the served `changePrice`."""
    l1 = _lock(record_at_lock_switch("Daphne", 900))
    assert im.price_words_on("L1", l1) == ["900 credits is not the served price [400]"]
    assert not im.no_price_shown(_record(l1))[0]


def test_a_label_with_a_currency_or_another_word_faults():
    """No currency anywhere on L1; a label that is not keel-web's (no number, *AI credits*, a price word) is a price
    word outside the screen's own. (A space closes each made-up label: `textContent` glues the label to the faces'
    first name, and `PRICE_WORD` reads whole words -- tasks.md judgement call 4.)"""
    assert "$" in im.price_words_on("L1", _lock("Record Daphne at lock · 400 credits ($2)"))
    assert im.price_words_on("L1", _lock("Record Daphne at lock · Keel's credits ")) == ["credits"]
    assert im.price_words_on("L1", _lock("Record Daphne at lock · 400 AI credits ")) == ["credits"]
    assert im.price_words_on("L1", _lock(record_at_lock_switch("Daphne", 400) + "Price set.")) == ["Price"]


def test_the_switch_is_read_on_l1_alone():
    """S1, S2 and S3 read as before: the label anywhere else is a price word."""
    label = record_at_lock_switch("Daphne", 400)
    assert im.price_words_on("S1", label) == ["credits"]
    assert im.price_words_on("S3", label) == ["credits"]
    assert im.price_words_on("S2", f"Recorded today at 16:02. {im.CHANGE_ACTION} {label}") == ["credits"]


def test_the_version_moved_with_its_note():
    """FR-1: `INTERVIEWER_MARKS_VERSION` 15 -> 16 with its note (spec 099 moved it on to 17: IM17 / IM19)."""
    assert im.INTERVIEWER_MARKS_VERSION == 17
    source = inspect.getsource(im)
    assert "#: v16 (spec 094 FR-1" in source and "#: v15 (spec 091 FR-3" in source and "spec 094 FR-1a" in source


# ------------------------------------------------------------------------- FR-1a: Send more's credits note

#: S3 as journey s006 read it on 2026-10-30 (bundle `runs/20261030T125356Z-s006-paidly`, `screens.S3`): the popup's
#: `textContent`, the elements glued, keel-web 131's note between the rows and the state line.
S3_AS_READ = ("Send more · Freelance translators working for agenciesHow should they answer?1 How they answer2 Who3 Their "
              "linksAI interviewer · SaskiaSaskia asks each question aloud on video. They answer by talking, typing or "
              "tapping.Every answer in a quiet room. More than 9 in 10 where it is loud: a building site, a busy road, a "
              "café. Hear itText onlyThey read each question and tap or type their answer.Let them chooseBoth are "
              "offered; they pick Saskia or text when they open the link.Each person who answers uses 30 credits, "
              "whichever way they answer.The interviewer is already recorded for this project.CancelContinue · AI "
              "interviewer")


def test_the_credits_note_is_keel_webs_words_and_the_interview_price():
    """keel-web 131 `FORMAT_CREDITS_NOTE`, read off the checkout and the harness's copy, is the note IM2 reads; its
    number is the interview's price (`interview_charge.INTERVIEW_CREDITS`, 30)."""
    from harness import interview_charge as charge                          # noqa: PLC0415
    from harness import interviewer_screens as ivs                          # noqa: PLC0415
    translate = _web_source("src/lib/translate.ts")
    assert f'export const FORMAT_CREDITS_NOTE = "{ivs.FORMAT_CREDITS_NOTE}";' in translate
    m = im.FORMAT_CREDITS_NOTE.fullmatch(ivs.FORMAT_CREDITS_NOTE)
    assert m and int(m.group("credits")) == charge.INTERVIEW_CREDITS == 30


def test_im2_reads_s3_as_s006_drew_it():
    """FR-1a: the s006 fault of 2026-10-30 -- S3's *credits* was the note -- reads clean; IM2 names the note it read."""
    assert im.PRICE_WORD.search(S3_AS_READ), "the word IM2 v15 caught"
    assert im.price_words_on("S3", S3_AS_READ) == []
    record = _record(_lock())
    record["screens"]["S3"] = S3_AS_READ
    ok, detail = im.no_price_shown(record)
    assert ok, detail
    assert detail["S3 credits note"] == "Each person who answers uses 30 credits, whichever way they answer."


def test_s3_without_the_note_reads_as_before():
    """A Send more drawn before keel-web 131 (no note): nothing to take away, nothing priced."""
    assert im.price_words_on("S3", "AI interviewer · Saskia Text only Let them choose") == []
    assert im.no_price_shown(_record(_lock()))[1]["S3 credits note"] is None


def test_a_second_credits_line_or_another_price_on_s3_faults():
    """FR-1a: a second note, a note at another number, a currency, any other price word on S3."""
    note = "Each person who answers uses 30 credits, whichever way they answer."
    assert im.price_words_on("S3", S3_AS_READ + note)[0] == f"a second credits note: {note!r}"
    assert im.price_words_on("S3", S3_AS_READ.replace("uses 30", "uses 45")) == [
        "45 credits is not the interview's price [30]"]
    assert "$" in im.price_words_on("S3", S3_AS_READ + " About $0.12 each.")
    assert im.price_words_on("S3", S3_AS_READ + " AI interviewer · 400 credits") == ["credits"]
    assert im.price_words_on("S3", S3_AS_READ + " The price is set.") == ["price"]


def test_the_note_is_read_on_s3_alone():
    """S1 and L1 do not take the note: there it is a price word."""
    note = "Each person who answers uses 30 credits, whichever way they answer."
    assert im.price_words_on("S1", note) == ["credits"]
    assert im.price_words_on("L1", _lock() + " " + note) == ["credits"]


# ------------------------------------------------------------------------- FR-2: the lock step leaves it on

def test_the_lock_body_carries_the_flag_only_with_the_switch_off():
    """keel-web 132's three states, read off the checkout: the lock sends `recordOnSend` only when the switch is off
    (`recordOnSend` is `lockOptional && skipRenderFor === projectId`), and a fresh mount draws it on."""
    step = _web_source("src/components/corridor/BeforeStep.tsx")
    assert "...(recordOnSend ? { recordOnSend } : {})" in step
    assert "const recordOnSend = lockOptional && skipRenderFor === projectId;" in step
    assert "useState<string | undefined>(undefined)" in step


SWITCH = ('<label class="before__switch" data-testid="record-at-lock"><input type="checkbox" role="switch" CHECKED>'
          '<span>LABEL</span></label>')


def _card(switch: str = "") -> str:
    """keel-web 132's lock screen (`BeforeStep`, `define/ready/interviewer`): the title, the sub, the card -- the switch
    as its first child where the server serves `recordOnSend: true` -- the carousel and the button, no whitespace
    between the elements (as React renders them)."""
    return ('<!doctype html><html><body><div class="corridor before"><h1>Who should ask them your questions?</h1>'
            f'<p class="ccard__sub">{SUB}</p><section class="ccard before__card" aria-label="Who asks">{switch}'
            '<div data-testid="face-carousel" role="radiogroup">'
            '<button type="button" role="radio" data-face="DAPHNE" aria-checked="true">Daphne</button>'
            '<button type="button" role="radio" data-face="SASKIA" aria-checked="false">Saskia</button></div>'
            '</section><button type="button" data-testid="lock-and-record">Lock and record Daphne</button></div>'
            '</body></html>')


@pytest.fixture(scope="module")
def chromium():
    from playwright.sync_api import sync_playwright                         # noqa: PLC0415
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _read_l1(chromium, tmp_path, html: str) -> dict:
    page = chromium.new_page()
    try:
        page.set_content(html)
        return vs_screens.Corridor(page, Recorder(tmp_path), "http://localhost:5173").l1()
    finally:
        page.close()


def test_l1_reads_staging_switch_on_and_im2_reads_the_text_as_the_screens_own(chromium, tmp_path):
    """Staging's shape: the switch drawn, on, its label the screen's words; the main column's text (the sub's last word
    glued to the label, the label to the first face) passes IM2."""
    label = record_at_lock_switch("Daphne", 400)
    l1 = _read_l1(chromium, tmp_path, _card(SWITCH.replace("CHECKED", "checked").replace("LABEL", label)))
    assert l1["switch"] == {"drawn": 1, "label": label, "role": "switch", "on": True, "disabled": False}
    assert "face.Record Daphne at lock · 400 credits" in l1["text"]
    assert im.price_words_on("L1", l1["text"]) == []
    assert l1["button"] == vs_screens.before_lock_record("Daphne")


def test_l1_reads_no_switch_on_the_local_stacks_screen(chromium, tmp_path):
    """The local stack's shape (`recordOnSend: false`): no switch drawn, IM2 as 091 left it."""
    l1 = _read_l1(chromium, tmp_path, _card())
    assert l1["switch"] == {"drawn": 0}
    assert im.LOCK_SWITCH_LABEL.search(l1["text"]) is None and im.price_words_on("L1", l1["text"]) == []


def test_l1_reads_a_switch_turned_off_as_off(chromium, tmp_path):
    """The reader reports what is drawn: a switch off (by someone else) reads `on: False`, which the leg refuses."""
    label = record_at_lock_switch("Daphne", 400)
    l1 = _read_l1(chromium, tmp_path, _card(SWITCH.replace("CHECKED", "").replace("LABEL", label)))
    assert l1["switch"]["on"] is False and l1["switch"]["drawn"] == 1


def test_the_harness_never_turns_the_switch_off():
    """FR-2: nothing in the lock walk or the reader presses, unchecks or sets the switch."""
    source = inspect.getsource(vs_screens.Corridor.word_pilot_and_lock) + inspect.getsource(vs_screens.Corridor.l1) \
        + inspect.getsource(vs_screens.Corridor.lock_switch) + inspect.getsource(vs_screens.Corridor.relock)
    for verb in (".uncheck(", ".set_checked(", ".check(", "RECORD_AT_LOCK).click", "record-at-lock\").click"):
        assert verb not in source, verb


def _journey(tmp_path, l1: dict | None):
    from types import SimpleNamespace                                       # noqa: PLC0415
    screens = {} if l1 is None else {"L1": l1}
    return SimpleNamespace(screens=screens, recorder=Recorder(tmp_path))


ON = {"drawn": 1, "label": "Record Daphne at lock · 400 credits", "role": "switch", "on": True, "disabled": False}
BODY = {"expectedRevision": 41, "interviewer": {"face": "DAPHNE"}}


def test_the_lock_step_records_the_switch_on_and_no_flag(tmp_path):
    """Staging's lock: the switch drawn and on, the body `{expectedRevision, interviewer: {face}}`."""
    record: dict = {}
    leg._lock_switch(_journey(tmp_path, {"switch": ON, "sent": BODY}), record)
    assert record["lock"] == {"switch": ON, "sent": BODY, "flags": [], "price words": []}


def test_the_lock_step_records_no_switch_on_the_local_stack(tmp_path):
    """The local stack's lock (and the own-AI one, `{expectedRevision}`): no switch, no flag."""
    for body in (BODY, {"expectedRevision": 41}):
        record: dict = {}
        leg._lock_switch(_journey(tmp_path, {"switch": {"drawn": 0}, "sent": body}), record)
        assert record["lock"]["switch"] == {"drawn": 0} and record["lock"]["flags"] == []
    record = {}
    leg._lock_switch(_journey(tmp_path, {"sent": BODY}), record)          # read before 094: no `switch` key
    assert record["lock"]["switch"] == {"drawn": 0}


@pytest.mark.parametrize("l1", [
    {"switch": {**ON, "on": False}, "sent": BODY},                                              # turned off
    {"switch": ON, "sent": {"expectedRevision": 41, "interviewer": {"face": "DAPHNE", "recordOnSend": True}}},
    {"switch": {"drawn": 0}, "sent": {"expectedRevision": 41, "recordOnSend": True}},           # a flag, no switch
    {"switch": {**ON, "drawn": 2}, "sent": BODY},                                               # a second switch
    {"switch": {**ON, "role": None}, "sent": BODY},                                             # not a switch
], ids=["off", "flag-with-switch-on", "flag-without-switch", "two-switches", "no-role"])
def test_the_lock_step_fails_a_switch_turned_off_or_a_flag_sent(tmp_path, l1):
    with pytest.raises(AssertionError):
        leg._lock_switch(_journey(tmp_path, l1), {})


def test_a_leg_handed_no_lock_screen_records_nothing(tmp_path):
    record: dict = {}
    leg._lock_switch(_journey(tmp_path, None), record)
    assert "lock" not in record


def test_lock_flags_finds_the_flag_at_any_depth():
    assert leg.lock_flags({"interviewer": {"face": "DAPHNE", "recordOnSend": True}}) == ["interviewer.recordOnSend"]
    assert leg.lock_flags({"recordOnSend": True}) == ["recordOnSend"]
    assert leg.lock_flags(BODY) == [] and leg.lock_flags(None) == []


def test_the_leg_reads_the_lock_first_on_both_profiles():
    """FR-2: the step runs before the own-AI refusals, so the remote profile records it too."""
    source = inspect.getsource(leg._leg)
    assert source.index("_lock_switch(j, record)") < source.index("_own_ai(j, wire, record)") \
        < source.index("j.stack.is_remote")
