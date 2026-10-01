"""What a review card draws when the questions are not written yet, and what an approved card
draws when they are (spec `026-journey-one-questionnaire`, T017).

The same shape as `tests/test_participant_sections_are_occasions.py` and for the same reason: what
changed is the *region* a page object reads, and a source grep cannot show it. keel-web's own markup
goes into a Playwright page and comes back out through `ReviewCard` and `OpenedCard`.

**Two facts, and between them they are why this spec exists.**

1. `ReviewLine` renders `{selection ? <Chips …/> : null}` (keel-web spec 026 FR-012), so a line with
   no control draws **no `.chips` node at all** -- not an empty one. `ReviewCard.lines()` therefore
   answers `chips: []`, and `assert all(line["chips"] …)` is false on every card a founder reviews
   under keel-cloud spec 048. That is the assertion matrix run 36862514753 died on, held here
   against markup so it can never be put back by accident.
2. The approved card's own slot is `span.strip__read` (keel-web spec 026 FR-020) and
   `OpenedCard.strips()` already reads it as `read_line` -- written for spec 030 and load-bearing
   for the first time here, which is worth proving rather than assuming.

**No word the model wrote is asserted anywhere below.** The prompts and headings in these fixtures
are the test's own, and what is read off them is presence and count.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from harness.browser import OpenedCard, ReviewCard
from harness.steps import Recorder


def _review_html(lines: list[tuple[str, bool]]) -> str:
    """`StageRoute.tsx`'s `DraftReview` plus `ReviewLine.tsx`, condensed to the nodes the page
    object reads: the card, its `.bet`, one `p.rule-line`, and a `div.belief` per line carrying a
    `.b-num`, a `.b-heading` and -- only where that line resolves a control -- a `.chips`."""
    body = ['<div class="card openc">',
            '<div class="card-top"><span class="bet">The problem</span>'
            '<span class="status">Reviewing</span></div>',
            '<p class="claim">A claim the model wrote.</p>',
            '<div class="who"><h4>A parent can settle three of these</h4>',
            '<p class="rule-line">If any of these is wrong, there is no deal-breaker left</p>']
    for n, (heading, chipped) in enumerate(lines, start=1):
        body.append(f'<div class="belief"><div class="b-top"><div class="b-text">'
                    f'<span class="b-num">{n}.</span><span class="b-heading">{heading}</span>'
                    f'</div></div>')
        if chipped:
            body.append('<div class="chips"><span class="chip">0 to 1</span>'
                        '<span class="chip expected">1 to 2</span>'
                        '<span class="chip esc">rather not say</span></div>')
        body.append("</div>")
    body.append("</div></div>")
    return "".join(body)


def _approved_html(reads: list[str | None]) -> str:
    """`StageRoute.tsx`'s `ApprovedCard`, condensed: `div.strip` rows with a `.b-num`, a heading and
    -- where the line resolves a control, or reads another line's -- a `span.strip__read`."""
    body = ['<div class="card openc">',
            '<div class="card-top"><span class="bet">The problem</span>'
            '<span class="status">Approved · nobody asked yet</span></div>',
            '<div class="measures lines">']
    for n, read in enumerate(reads, start=1):
        body.append(f'<div class="strip"><div class="strip__head"><span class="caret">▸</span>'
                    f'<span class="b-num">{n}.</span><b>Line {n}</b></div>'
                    f'<span class="strip__status">Nobody asked yet</span>')
        if read is not None:
            body.append(f'<span class="strip__read">{read}</span>')
        body.append("</div>")
    body.append("</div></div>")
    return "".join(body)


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


#: **A short auto-wait, and it is the fixtures' own point** (Discovered D-12). Playwright's default
#: is thirty seconds, and the page objects read optional nodes through `_safe_text` -- a belief with
#: no `p.you-said`, a strip with no `.strip__read`. *Absent* is exactly what these fixtures are
#: about, so every absent node would otherwise cost half a minute of auto-wait before `_safe_text`
#: swallowed the timeout, and this module alone would take longer than the whole suite does. One
#: quarter of a second is far longer than a `set_content` page ever needs and is never the thing under
#: test; it takes this module from thirty-three seconds to under ten.
_ABSENT_IS_THE_POINT_MS = 250


def _read_review(tmp_path, browser, html):
    page = browser.new_page()
    page.set_default_timeout(_ABSENT_IS_THE_POINT_MS)
    page.set_content(html)
    card = ReviewCard(page, Recorder(tmp_path), "http://example.invalid")
    try:
        return card.lines(), card.rule_lines()
    finally:
        page.close()


def _read_approved(tmp_path, browser, html):
    page = browser.new_page()
    page.set_default_timeout(_ABSENT_IS_THE_POINT_MS)
    page.set_content(html)
    card = OpenedCard(page, Recorder(tmp_path), "http://example.invalid")
    try:
        return card.strips()
    finally:
        page.close()


# ----------------------------------------- a review card under 048 carries lines and no pick lists

def test_a_card_drawn_before_the_questions_exist_has_numbered_lines_and_no_chips(tmp_path, browser):
    """FR-001 and FR-002 in one fixture: everything the step still asserts is there, and the thing
    it stopped asserting is not -- which is exactly the card keel-cloud 048 makes every review card
    be, because the questionnaire is written after the last approval."""
    lines, rule_lines = _read_review(
        tmp_path, browser,
        _review_html([("Crying they couldn't read, recently", False),
                      ("Woken more than twice a night", False)]))
    assert len(lines) == 2
    assert [line["number"] for line in lines] == ["1.", "2."]
    assert all(line["chips"] == [] for line in lines), (
        "a line with no control drew chips anyway -- then keel-web is rendering an empty Chips row "
        "and 026 FR-012 is not what shipped")
    assert any("deal-breaker" in line.lower() for line in rule_lines)


def test_the_old_assertion_really_would_have_failed_on_that_card(tmp_path, browser):
    """The red run, reproduced without a browser against staging and without a model call: this is
    `assert all(line.get("chips") for line in lines)` on the card 36862514753 was shown."""
    lines, _ = _read_review(tmp_path, browser,
                            _review_html([("Crying they couldn't read, recently", False)]))
    assert not all(line.get("chips") for line in lines)


def test_a_line_that_reads_an_earlier_stages_measurement_still_draws_chips(tmp_path, browser):
    """FR-003 and Discovered D-4. keel-cloud 049 FR-013 writes the referent's own `selectionId`
    onto a belief that reads an earlier stage's line, so that line owns a control the earlier
    approval already wrote and draws a pick list on a card whose own stage is unapproved. Asserting
    the *absence* of chips would go red on exactly the run that proves 049 works."""
    lines, _ = _read_review(tmp_path, browser,
                            _review_html([("Its own new line", False),
                                          ("Measured with the problem's line 3", True)]))
    assert lines[0]["chips"] == []
    assert len(lines[1]["chips"]) == 3
    assert [chip["expected"] for chip in lines[1]["chips"]] == [False, True, False]
    assert [chip["escape"] for chip in lines[1]["chips"]] == [False, False, True]


# -------------------------------------- an approved card carries its slice, and the page object reads it

def test_the_approved_cards_slot_is_read_as_read_line(tmp_path, browser):
    """FR-014. `OpenedCard.strips()` has read `.strip__read` since spec 030; the journey had never
    asked it for one. Three readings go through that one slot (keel-web 026 FR-020) and the
    scenario asserts that one of them is drawn, never which."""
    strips = _read_approved(tmp_path, browser, _approved_html([
        'Asked with “How long did it take?”',
        "Same pick list as line 1.",
        "Measured with the problem's line 3.",
    ]))
    assert len(strips) == 3
    assert [strip["number"] for strip in strips] == ["1.", "2.", "3."]
    assert all(strip["read_line"] for strip in strips)


def test_a_line_with_no_control_draws_no_slot_and_that_is_not_a_failure(tmp_path, browser):
    """A belief can legitimately resolve no control -- `Q2`/`Q4` share them, and not every line
    owns one. So the scenario asserts *at least one across the three cards*, never all."""
    strips = _read_approved(tmp_path, browser, _approved_html([None, "Same pick list as line 1."]))
    assert strips[0]["read_line"] == ""
    assert strips[1]["read_line"] == "Same pick list as line 1."
    assert any(strip["read_line"] for strip in strips)


def test_a_card_that_shows_no_slice_at_all_is_what_the_scenario_refuses(tmp_path, browser):
    """The failure the screen half exists to catch: a questionnaire on the wire that no card is
    showing."""
    strips = _read_approved(tmp_path, browser, _approved_html([None, None]))
    assert not any(strip["read_line"] for strip in strips)
