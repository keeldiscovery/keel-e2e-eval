"""`ParticipantPage.anchors()`'s own region, against the markup `ParticipantRoute.tsx` renders
(`runs/DRIFT.md` #44, found by the fourth live S-004 run
`runs/20260907T223817Z-s004-stranger-who-gives-orders-live`).

The same shape as `test_participant_submit_sent.py` and `test_doors_d5_reveal_regions.py`: a real
Playwright browser over real DOM, because what went wrong was the *region* the page object read
and no amount of string-matching can show it.

`AnchorBlock` returns a **fragment** -- `<div class="q">…story box…</div>` followed by
`<div class="picks">…</div>` (`class="picks off"` when a tap dims them). `anchors()` read
`block.locator(".picks > div.q")`, a `.picks` *inside* the anchor's own block, which does not
exist; so every anchor came back with `selections: []` and nothing raised, because an empty list
is a legal answer to *what does this anchor ask*.

S-004 is the only caller. Both of its choices of what to attack -- `_carried_choice` (the corpus's
preferred `GUESSED` control, if this link still carries it) and `_page_choice` (the fallback: the
first control on the page offering a *say roughly*) -- read `anchors()["selections"]`, so both were
searching an empty list. The live run's own captured page shows three *say roughly* rows and the
run stopped on *"this link carries no anchor with a say roughly control at all"*. `answer_as`, which
every scripted scenario uses, goes through `_selection_block` instead and was never affected -- six
green runs said nothing about this.

The companion case is the point of the pair: the fix must not make `anchors()` credulous. An anchor
whose picks are genuinely absent -- `hidePicks`, what keel-web renders for a person who tapped *it
hasn't happened* -- must still read as no selections, and one anchor's picks must never be read as
another's.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from harness.browser import ParticipantPage
from harness.steps import Recorder

_A1 = "Think of the last delivery where what arrived didn't match the invoice."
_A2 = "Think of that same delivery arriving. Who was there?"
_A3 = "Think of the last piece of software this restaurant started paying for."

_S1 = "Before that one, when was the previous mismatch?"
_S2 = "How long did the recount and fixing the numbers take, that time?"
_S3 = "Who took it in?"


def _anchor(prompt: str, *, taps: list[str] | None = None, selections: list[tuple[str, list[str]]],
            dim: bool = False, hide: bool = False) -> str:
    """One `AnchorBlock`, as it renders: a `div.q` carrying the story box, then a **sibling**
    `div.picks` -- or, where the person tapped *it hasn't happened*, no `div.picks` at all."""
    chips = "".join(f'<span class="chip">{t}</span>' for t in (taps or []))
    body = f'<div class="taps">{chips}</div>' if chips else ""
    head = (f'<div class="q"><p>{prompt}</p>'
            f'<textarea class="box" aria-label="{prompt}"></textarea>{body}</div>')
    if hide:
        return head
    picks = ""
    for selection_prompt, options in selections:
        rows = "".join(f'<div><span class="opt">{o}</span></div>' for o in options)
        picks += (f'<div class="q"><p>{selection_prompt}</p>'
                  f'<div class="opts">{rows}<div><span class="opt esc">can\'t recall</span></div>'
                  "</div></div>")
    klass = "picks off" if dim else "picks"
    return head + f'<div class="{klass}">{picks}</div>'


_PAGE = "<div class='iv'>" + "".join([
    _anchor(_A1, taps=["It hasn't happened", "I can't recall"], selections=[
        (_S1, ["under 1 day", "1 day to 2 days", "more than 3 months, say roughly"]),
        (_S2, ["under 15 min", "more than 1 day, say roughly"]),
    ]),
    # Dimmed by a tap, and still asked: `class="picks off"` is the same picks block.
    _anchor(_A2, taps=["I can't recall"], selections=[(_S3, ["me", "a member of staff"])], dim=True),
    # `hidePicks`: the person tapped *it hasn't happened*, so keel-web renders no picks at all.
    _anchor(_A3, taps=["It hasn't happened"], selections=[], hide=True),
]) + "</div>"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _anchors(tmp_path, browser, html):
    page = browser.new_page()
    page.set_content(html)
    try:
        return ParticipantPage(page, Recorder(tmp_path)).anchors()
    finally:
        page.close()


def test_every_anchor_reads_the_selections_its_own_sibling_picks_block_carries(tmp_path, browser):
    """The fault itself: `.picks` is a sibling of the anchor's `div.q`, never a child."""
    read = _anchors(tmp_path, browser, _PAGE)
    assert [a["prompt"] for a in read] == [_A1, _A2, _A3]
    assert read[0]["selections"] == [_S1, _S2]
    assert read[1]["selections"] == [_S3], "a dimmed `picks off` block is still this anchor's picks"


def test_an_anchor_whose_picks_are_hidden_reads_as_no_selections(tmp_path, browser):
    """The companion. `hidePicks` renders no `div.picks` for a person who tapped *it hasn't
    happened*, and the fix must not reach past this anchor into the next one's block."""
    read = _anchors(tmp_path, browser, _PAGE)
    assert read[2]["selections"] == []


def test_the_taps_still_come_back_with_each_anchor(tmp_path, browser):
    read = _anchors(tmp_path, browser, _PAGE)
    assert read[0]["taps"] == ["It hasn't happened", "I can't recall"]


def test_the_say_roughly_control_s004_hunts_for_is_findable_from_this_read(tmp_path, browser):
    """What B8 actually needs: the fallback walks `anchors()` and asks `options_for` of every
    selection prompt it names. With `selections: []` there was nothing to ask, on a page rendering
    three *say roughly* rows -- which is exactly what the live run reported."""
    page = browser.new_page()
    page.set_content(_PAGE)
    try:
        participant = ParticipantPage(page, Recorder(tmp_path))
        found = []
        for anchor in participant.anchors():
            for selection_prompt in anchor["selections"]:
                labels = participant.options_for(selection_prompt,
                                                  anchor_prompt=anchor["prompt"])
                if any(l.strip().lower().endswith("say roughly") for l in labels):
                    found.append((anchor["prompt"], selection_prompt))
        assert found == [(_A1, _S1), (_A1, _S2)]
    finally:
        page.close()
