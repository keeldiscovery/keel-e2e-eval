"""`People.close_popup()`'s own region, against the markup the People screen really renders when
a send popup and a reading toast are on it at the same time.

The same shape as `test_participant_anchor_selections.py` and `test_doors_d5_reveal_regions.py`: a
real Playwright browser over real DOM, because what went wrong was the *scope* the page object
searched, and a string-match over `browser.py` cannot tell a page-wide locator from a scoped one.

**What was observed**, `runs/20260909T070205Z-s002-agent-optional` step 27 and
`runs/20260909T070207Z-s003-every-door` step 12, both on the same line:

    strict mode violation: get_by_role("button", name=re.compile(r"^Done$|^close$", re.I))
      resolved to 2 elements:
        1) <button class="btn" type="button">Done</button>
        2) <button class="x" type="button" aria-label="Close">x</button>

Two different components, one page. `SendPopup.tsx` renders the *Done* button inside its
`div.pop`; `SaidBox.tsx` -- the reading toast -- renders an `aria-label="Close"` x of its own, and
since keel-web `b0a5015` ("The reading toast goes away") that toast stands for **thirty seconds**
rather than until the next page load. The referee walks the whole of People inside one of those
thirty seconds, so the toast is up, legitimately, for every click the send popup needs.

**Nobody's product moved.** A toast that outlives the click that raised it, and offers its own way
out, is exactly what `b0a5015` shipped and what a founder wants. The `|^close$` alternative in the
locator was there for a popup whose only dismissal is an x, and page-wide it reached out of the
dialog and into the toast. Playwright's strict mode is the reason this is a caught fault and not a
run that quietly dismissed the toast, left the popup standing, and failed ten steps later on
something unrelated -- which is what a `.first` would have bought.

The fix is one word of scope: look inside `.pop`, the node the detach-wait on the next line
already names. The companion case below is the point of the pair -- the fallback must still work
for a dialog whose only affordance *is* an x, or the fix would have bought its precision by
deleting a capability.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from harness.browser import People
from harness.steps import Recorder

# keel-web `SaidBox.tsx`, near enough for the collision: the x is a real button with a real
# accessible name, and it lives outside any `.pop`.
_TOAST = (
    '<div class="said">'
    '<button type="button" class="x" aria-label="Close">×</button>'
    '<span class="n">Wei Zhang</span>'
    '<span class="r">read as <b>It costs hours, not minutes</b></span>'
    "</div>"
)

# `SendPopup.tsx` step three: the link, and *Done*.
_SEND_POPUP = (
    '<div class="pop" role="dialog" aria-modal="true" aria-label="Send the questions">'
    '<p class="linkbox">http://localhost:5173/i/7hzLKUZ6irfFnM_S1swPbw</p>'
    '<button class="btn" type="button">Copy link</button>'
    '<button class="btn" type="button">Done</button>'
    "</div>"
)

# A dialog whose only way out is its own x -- what `|^close$` was written for.
_X_ONLY_POPUP = (
    '<div class="pop" role="dialog" aria-modal="true" aria-label="Wei Zhang’s answers">'
    '<button type="button" class="x" aria-label="Close">×</button>'
    "<p>Their answers</p>"
    "</div>"
)

_DISMISS = """
  for (const b of document.querySelectorAll('.pop button')) {
    b.addEventListener('click', (e) => {
      if (e.target.textContent.trim() === 'Done' || e.target.getAttribute('aria-label') === 'Close') {
        e.target.closest('.pop').remove();
      }
    });
  }
"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _people(tmp_path, browser, html):
    page = browser.new_page()
    page.set_content(f"<div class='ppl'>{html}</div>")
    page.evaluate(_DISMISS)
    return page, People(page, Recorder(tmp_path), "http://localhost:5173")


def test_the_send_popup_closes_with_the_reading_toast_standing_beside_it(tmp_path, browser):
    """The fault itself. Both buttons are on the page and only one of them is the dialog's."""
    page, people = _people(tmp_path, browser, _TOAST + _SEND_POPUP)
    try:
        people.close_popup()
        assert page.locator(".pop").count() == 0, "the dialog is the thing that closes"
        assert page.locator(".said").count() == 1, (
            "and the toast is untouched -- dismissing somebody else's component to get out of "
            "this one is the failure this test exists to prevent")
    finally:
        page.close()


def test_the_toast_is_not_clicked_even_when_the_dialog_has_no_matching_button(tmp_path, browser):
    """The scope holds when the dialog cannot satisfy the locator: it fails inside `.pop` rather
    than succeeding on the toast. A page-wide locator would have clicked the toast and then hung
    on the detach-wait for a `.pop` nothing had closed."""
    page, people = _people(tmp_path, browser, _TOAST + _SEND_POPUP.replace(">Done<", ">Next<"))
    try:
        with pytest.raises(Exception):
            people.close_popup()
        assert page.locator(".said").count() == 1
        assert page.locator(".pop").count() == 1
    finally:
        page.close()


def test_a_dialog_whose_only_way_out_is_its_own_x_still_closes(tmp_path, browser):
    """The companion: `|^close$` is still load-bearing, and scoping it did not delete it."""
    page, people = _people(tmp_path, browser, _TOAST + _X_ONLY_POPUP)
    try:
        people.close_popup()
        assert page.locator(".pop").count() == 0
        assert page.locator(".said").count() == 1
    finally:
        page.close()


def test_close_popup_searches_inside_the_dialog_and_not_the_page(tmp_path, browser):
    """The grip on the fix, so a later edit that reaches for `self.page` again is caught by a
    unit test rather than by S-002 thirteen minutes into an eval-all."""
    import inspect

    source = inspect.getsource(People.close_popup)
    body = source.split('"""')[-1]
    assert 'self.page.get_by_role(' not in body, (
        "the dismissing button is found within `.pop`, never page-wide (the reading toast has an "
        "aria-label=\"Close\" of its own)")
    assert '.locator(".pop")' in body
