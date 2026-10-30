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

from evals import interviewer_marks as im
from stack.config import load_config

WEB = load_config(validate=False).keel_web


def _web_source(relative: str) -> str:
    path = WEB / relative
    if not path.is_file():
        pytest.skip(f"keel-web is not checked out at {WEB}")
    return path.read_text(encoding="utf-8")


def record_at_lock_switch(face: str, credits: int) -> str:
    """keel-web 132 `recordAtLockSwitch(face, credits)`, restated (held to the checkout below)."""
    return f"Record {face} at lock · {credits} credits"


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
    step = _web_source("src/components/corridor/BeforeStep.tsx")
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
    """FR-1: `INTERVIEWER_MARKS_VERSION` 15 -> 16 with its note."""
    assert im.INTERVIEWER_MARKS_VERSION == 16
    source = inspect.getsource(im)
    assert "#: v16 (spec 094 FR-1" in source and "#: v15 (spec 091 FR-3" in source
