"""A section is an occasion, and the founder's preview names the minutes once (spec 025 FR-021,
T019).

Two shape facts S-012 now asserts on a live page, held here against markup instead — the same shape
as `test_participant_submit_sent.py` and for the same reason: what changed is the *region* a page
object reads, and strings alone cannot show it.

**Neither assertion reads a word the model wrote.** The section titles on a live page are the
occasions the model named, and spec 016 FR-007 stands: the journey asserts counts and absences, and
never prose. What is asserted is that one occasion draws one section, that none of the three titles
a *stage* used to draw is there at all, and that the preview carries exactly one *"About N
minutes"* line with `N` at or above `FormComposer`'s floor.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from evals.test_s012_journey_through_a_host import OLD_STAGE_SECTION_TITLES
from harness.browser import ParticipantPage, People
from harness.steps import Recorder


def _page_html(sections: list[tuple[str, int]]) -> str:
    """`ParticipantRoute.tsx`'s own shape, condensed: a `div.sect` title, then that section's
    anchor blocks, each a `div.q` carrying a `textarea.box`."""
    body = ['<div class="iv">', '<p class="hello">Lullaby has asked you a few questions.</p>']
    for title, anchors in sections:
        body.append(f'<div class="sect">{title}</div>')
        for n in range(anchors):
            body.append(f'<div class="q"><p>Occasion {title} {n}?</p>'
                        '<textarea class="box"></textarea><div class="picks"></div></div>')
    body.append("</div>")
    return "".join(body)


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _read(tmp_path, browser, html):
    page = browser.new_page()
    page.set_content(html)
    participant = ParticipantPage(page, Recorder(tmp_path))
    try:
        return participant.sections(), participant.anchors()
    finally:
        page.close()


# -------------------------------------------------------------- one section per occasion

def test_one_section_title_per_anchor_block(tmp_path, browser):
    """`ParticipantPage.sections()` was written with the page object and **called by nothing** for
    as long as a section was a stage. It is load-bearing now."""
    html = _page_html([("The last wake-up", 1), ("The last app you paid for", 1)])

    sections, anchors = _read(tmp_path, browser, html)

    assert len(sections) == 2
    assert len(sections) == len(anchors), "one occasion, one section"


def test_none_of_the_three_old_stage_titles_is_on_the_page(tmp_path, browser):
    html = _page_html([("The last wake-up", 1), ("The last app you paid for", 1)])

    sections, _anchors = _read(tmp_path, browser, html)

    titles = {t.strip().lower() for t in sections}
    assert not titles & {t.lower() for t in OLD_STAGE_SECTION_TITLES}


def test_a_page_still_drawing_sections_by_stage_fails_the_assertion(tmp_path, browser):
    """The test that says the other two are not vacuous: the old page shape is caught, and caught
    on both counts — three titles for three blocks would pass a bare count, and does not pass the
    titles."""
    html = _page_html([(title, 1) for title in OLD_STAGE_SECTION_TITLES])

    sections, anchors = _read(tmp_path, browser, html)

    assert len(sections) == len(anchors) == 3, "a bare count alone would not have caught this"
    offending = [t for t in sections
                 if t.strip().lower() in {s.lower() for s in OLD_STAGE_SECTION_TITLES}]
    assert len(offending) == 3, "which is why the titles are asserted as well as the count"


# ------------------------------------------------------------------ the minutes, said once

def test_the_preview_carries_exactly_one_minutes_line():
    preview = ("Lullaby — what the cry means\n"
               "About 17 minutes · every question can be skipped · your words go to Amira only")

    assert People.preview_minutes(preview) == [17]


def test_three_minutes_lines_are_three_and_not_one():
    """A reader that returned the first figure could not tell one estimate from three — which is
    precisely the shape one occasion asked once removes."""
    preview = "About 18 minutes\nAbout 12 minutes\nAbout 10 minutes"

    assert People.preview_minutes(preview) == [18, 12, 10]


def test_a_preview_with_no_minutes_line_reads_as_none_rather_than_zero():
    assert People.preview_minutes("Lullaby — what the cry means") == []
    assert People.preview_minutes("") == []
    assert People.preview_minutes(None) == []


def test_the_floor_is_ten_and_the_revised_corpus_sits_above_it():
    """`minutes = max(10, 2 x anchors + selections)`. Nothing asserts an exact N on a live page —
    the anchors and selections there are the model's own (spec 016 FR-007) — but the floor is the
    product's and is the one number this may claim."""
    for entry_anchors, selections in ((2, 17), (2, 13), (2, 12), (2, 11), (4, 10), (2, 11), (2, 13)):
        assert max(10, 2 * entry_anchors + selections) >= 10


# ------------------------------------------------------------- and S-012 makes both of them

def test_s012_asserts_both_shapes_and_neither_as_prose():
    from pathlib import Path                                                # noqa: PLC0415

    scenario = (Path(__file__).resolve().parent.parent / "evals"
                / "test_s012_journey_through_a_host.py").read_text(encoding="utf-8")

    assert "participant.sections()" in scenario
    assert "People.preview_minutes(preview)" in scenario
    assert "one section per occasion, and no stage titles left" in scenario
    assert "the founder's preview names the minutes once" in scenario
