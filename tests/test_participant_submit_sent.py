"""`ParticipantPage.send`'s "did it send" region, against real markup (`runs/DRIFT.md` #33, found
by the rerun `runs/20260907T161514Z-s006-paidly`; moved onto keel-web 042's pager by #71).

The same shape as `test_doors_d5_reveal_regions.py`: a real Playwright browser over the DOM
`ParticipantRoute.tsx` actually renders, because what went wrong was the *region* the page object
read, not any judgement over what it read. Strings alone cannot show it -- the word the old
locator matched is genuinely on the page, just not the one that means "sent".

`send()` presses once, and presses a second time when the first press only produced the product's
`BLANK_ANCHOR_NUDGE`. It used to decide the first press had landed by matching `/thanks/i` anywhere
on the page. `TAP_NOTE_HASNT_HAPPENED` -- *"Thanks -- that answers this part. On to the next."* --
is rendered under any anchor the person tapped *it hasn't happened* on, so it is on screen
**before** the send is pressed at all. The one corpus person who both taps and leaves another
anchor blank (`05-paidly`'s Yara Haddad, and `07-mulchrun`'s Cody Brandt) therefore had her first
press read as a send: the loop broke, the second press was never made, the response was never
stored, and S-006 went red on a `guessed` count that was keel-cloud's own correct arithmetic over
somebody who had never answered. The done state is the whole pager body replaced by `.iv-done` --
*That's it.* over *"Thanks, {person}. Your answers have gone to {founder}."* -- and the second half
of that sentence is what `send()` waits for.

**What 042 changed, and what it did not.** The button is the **last part's** primary and reads
*Send my answers*; the nudge is `p.iv-nudge` under that part; the thank-you is `.iv-done__lead`.
`INTERVIEW_DONE_LEAD`'s words are unchanged, so the region moved and the sentence did not -- which
is why these cases still read the way they did.

The companion cases below are the point of the set: the fix must not make `send()` credulous. A
send that never reaches the completion screen must still raise, and a server refusal must still be
named as a refusal rather than nudged at.
"""

from __future__ import annotations

import json

import pytest
from playwright.sync_api import sync_playwright

from harness.browser import ParticipantPage
from harness.steps import Recorder
from tests import interview_page

_TAP_NOTE = interview_page.TAP_NOTE_HASNT_HAPPENED
_NUDGE = interview_page.NUDGE
_DONE = "Thanks, Yara Haddad. Your answers have gone to Eval Founder."

_A1 = "Think of the last invoice you sent an agency and had paid."
_A2 = "Think of the last time a service offered to pay one of your invoices early."


def _page_html(*, presses_to_send: int, refusal: str = "") -> str:
    """Yara Haddad's interview, as it actually renders: **one part**, one anchor she taps *it
    hasn't happened* on (so `TAP_NOTE_HASNT_HAPPENED` is on screen before anything is pressed) and
    one anchor left blank (so the first press nudges).

    `presses_to_send=99` is the genuine dead end -- a send that never sends, however often it is
    pressed -- and `refusal` renders the `.stale` notice keel-web shows when the server refuses.

    The completion screen **replaces** the pager's body rather than sitting beside it, because that
    is what `ParticipantRoute.tsx` does: the part's `<main>` is unmounted and `.iv-done`'s is
    rendered. That matters to this test. It means the tap note and the done line are never in the
    DOM at the same moment, so the old `/thanks/i` locator never saw two elements and never
    complained -- it quietly matched the tap note, on a part that was still sitting there unsent.
    Reproducing the fault needs the real unmount, not two nodes with one hidden.
    """
    return interview_page.interview_html(
        [interview_page.part("The last invoice", [
            interview_page.anchor(_A1),
            interview_page.anchor(_A2, taps=["it hasn't happened to me"]),
        ])],
        done_lead=_DONE, presses_to_send=presses_to_send, refusal=refusal)


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _submit(tmp_path, browser, html):
    recorder = Recorder(tmp_path)
    page = browser.new_page()
    page.set_content(html)
    participant = ParticipantPage(page, recorder)
    try:
        participant.begin()
        # The tap is the product's, made the way a stranger makes it, so the tap note is on screen
        # before the send is pressed -- which is the whole of DRIFT #33.
        participant.tell_story(_A2, None, tap="HASNT_HAPPENED")
        participant.submit()
    finally:
        page.close()
    return recorder


def _steps(recorder):
    return [json.loads(line) for line in recorder.transcript_path.read_text().splitlines()]


def test_a_tapped_anchor_does_not_make_the_first_press_look_like_a_send(tmp_path, browser):
    """DRIFT #33 itself: the tap note is on screen before *Send my answers* is ever pressed, and
    the blank anchor means the first press only nudges. `send()` must press again and land on the
    completion screen -- the response is stored on the second press or not at all."""
    recorder = _submit(tmp_path, browser, _page_html(presses_to_send=1))

    step = [s for s in _steps(recorder) if s["name"] == "participant submits their answers"][0]
    assert step["ok"], step["error"]
    # It saw the nudge for what it was, rather than reading the tap note as a thank-you.
    assert step["captured_text"]["nudge"] == _NUDGE
    # And the screens it captured end on the completion screen, not on the part it started from.
    assert "answers have gone to" in step["captured_text"]["participant_page"]
    assert _TAP_NOTE in step["captured_text"]["participant_page"], (
        "the hop carries every screen the stranger was shown, tap note and all")
    assert json.loads(step["captured_text"]["completion"])["title"] == "That's it."


def test_a_page_that_never_sends_still_fails(tmp_path, browser):
    """The companion: the fix must not make `send()` credulous. Two presses that leave the part on
    screen are a failure, not a send -- which is exactly what the old locator could not tell apart
    from success on a page carrying the tap note."""
    with pytest.raises(Exception):
        _submit(tmp_path, browser, _page_html(presses_to_send=99))


def test_a_server_refusal_is_named_as_a_refusal_not_pressed_through(tmp_path, browser):
    """The other branch of the same loop: a `.stale` notice means keel-cloud refused the response.
    That is never nudged at and never pressed twice -- it is raised, naming what the page said."""
    refusal = "This link has already been answered."
    with pytest.raises(AssertionError, match="refused this response"):
        _submit(tmp_path, browser, _page_html(presses_to_send=99, refusal=refusal))
