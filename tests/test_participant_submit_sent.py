"""`ParticipantPage.submit`'s "did it send" region, against real markup (`runs/DRIFT.md` #33,
found by the rerun `runs/20260907T161514Z-s006-paidly`).

The same shape as `test_doors_d5_reveal_regions.py`: a real Playwright browser over the DOM
`ParticipantRoute.tsx` actually renders, because what went wrong was the *region* the page object
read, not any judgement over what it read. Strings alone cannot show it -- the word the old
locator matched is genuinely on the page, just not the one that means "sent".

`submit()` presses once, and presses a second time when the first press only produced the
product's `BLANK_ANCHOR_NUDGE`. It used to decide the first press had landed by matching
`/thanks/i` anywhere on the page. `TAP_NOTE_HASNT_HAPPENED` -- *"Thanks -- that answers this part.
On to the next."* -- is rendered under any anchor the person tapped *it hasn't happened* on
(`ParticipantRoute.tsx` line 296), so it is on screen **before** Submit is pressed at all. The one
corpus person who both taps and leaves another anchor blank (`05-paidly`'s Yara Haddad, and
`07-mulchrun`'s Cody Brandt) therefore had her first press read as a send: the loop broke, the
second press was never made, the response was never stored, and S-006 went red on a `guessed`
count that was keel-cloud's own correct arithmetic over somebody who had never answered. The done
state is the whole form replaced by one line -- *"Thanks, {person}. Your answers have gone to
{founder}."* -- and the second half of that sentence is what `submit()` now waits for.

The companion cases below are the point of the pair: the fix must not make `submit()` credulous.
A Submit that never reaches the done state must still raise, and a server refusal must still be
named as a refusal rather than nudged at.
"""

from __future__ import annotations

import json

import pytest
from playwright.sync_api import sync_playwright

from harness.browser import ParticipantPage
from harness.steps import Recorder

# The two lines the product actually renders, copied from keel-web `src/lib/translate.ts`.
_TAP_NOTE = "Thanks — that answers this part. On to the next."
_NUDGE = "Can you think of one specific time this happened? When was it, roughly?"
_DONE = "Thanks, Yara Haddad. Your answers have gone to Eval Founder."


def _page_html(*, presses_to_send: int, refusal: str = "") -> str:
    """Condensed from `ParticipantRoute.tsx`, as Yara Haddad's page actually renders: one anchor
    tapped *it hasn't happened* (so `TAP_NOTE_HASNT_HAPPENED` is on screen from the start), one
    anchor left blank (so the first press nudges), and a done state that replaces the whole form.

    `presses_to_send=99` is the genuine dead end -- Submit that never sends, however often it is
    pressed -- and `refusal` renders the `.stale` notice keel-web shows when the server refuses.

    The done state **replaces** the form rather than hiding it beside it, because that is what
    `ParticipantRoute.tsx`'s `if (done) return ...` does: React unmounts the whole questionnaire.
    That matters to this test. It means the tap note and the done line are never in the DOM at the
    same moment, so the old `/thanks/i` locator never saw two elements and never complained -- it
    quietly matched the tap note, on a form that was still sitting there unsent. Reproducing the
    fault needs the real unmount, not two nodes with one hidden.
    """
    return f"""
<div id="root"></div>
<script>
  const root = document.getElementById("root");
  const FORM = `
    <div class="iv" id="form">
      <p class="hello">Paidly has asked if you'd answer a few questions.</p>
      <div class="sect">About your work 1 of 2</div>
      <div class="anch">
        <p>Think of the last invoice you sent an agency and had paid.</p>
        <textarea></textarea>
      </div>
      <div class="anch">
        <p>Think of the last time a service offered to pay one of your invoices early.</p>
        <p class="hint" style="margin-top: 6px">{_TAP_NOTE}</p>
      </div>
      <p class="hint" id="nudge" hidden>{_NUDGE}</p>
      {f'<div class="stale">{refusal}</div>' if refusal else ''}
      <div class="actions">
        <button type="button" class="btn primary" id="send">Submit</button>
      </div>
    </div>`;
  const DONE = `<div class="iv"><p class="hello">{_DONE}</p></div>`;

  let presses = 0;
  function render() {{
    root.innerHTML = FORM;
    if (presses > 0) {{ document.getElementById("nudge").hidden = false; }}
    document.getElementById("send").addEventListener("click", () => {{
      presses += 1;
      if (presses >= {presses_to_send}) {{ root.innerHTML = DONE; }} else {{ render(); }}
    }});
  }}
  render();
</script>
"""


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
        participant.submit()
    finally:
        page.close()
    return recorder


def _steps(recorder):
    return [json.loads(line) for line in recorder.transcript_path.read_text().splitlines()]


def test_a_tapped_anchor_does_not_make_the_first_press_look_like_a_send(tmp_path, browser):
    """DRIFT #33 itself: the tap note is on screen before Submit is ever pressed, and the blank
    anchor means the first press only nudges. `submit()` must press again and land on the done
    state -- the response is stored on the second press or not at all."""
    recorder = _submit(tmp_path, browser, _page_html(presses_to_send=2))

    step = [s for s in _steps(recorder) if s["name"] == "participant submits their answers"][0]
    assert step["ok"], step["error"]
    # It saw the nudge for what it was, rather than reading the tap note as a thank-you.
    assert step["captured_text"]["nudge"] == _NUDGE
    # And the page it captured is the done state, not the form it started on.
    assert "answers have gone to" in step["captured_text"]["participant_page"]


def test_a_page_that_never_sends_still_fails(tmp_path, browser):
    """The companion: the fix must not make `submit()` credulous. Two presses that leave the form
    on screen are a failure, not a send -- which is exactly what the old locator could not tell
    apart from success on a page carrying the tap note."""
    with pytest.raises(Exception):
        _submit(tmp_path, browser, _page_html(presses_to_send=99))


def test_a_server_refusal_is_named_as_a_refusal_not_pressed_through(tmp_path, browser):
    """The other branch of the same loop: a `.stale` notice means keel-cloud refused the response.
    That is never nudged at and never pressed twice -- it is raised, naming what the page said."""
    refusal = "This link has already been answered."
    with pytest.raises(AssertionError, match="refused this response"):
        _submit(tmp_path, browser, _page_html(presses_to_send=99, refusal=refusal))
