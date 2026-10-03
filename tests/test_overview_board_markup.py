"""What the overview draws since keel-web spec **038** `overview-board`, and what §1.7 reads off it
(this repo's `029-deck-038` pass; `runs/DRIFT.md` **#73**).

The same shape as `tests/test_journey_brief_ship_markup.py` and
`tests/test_participant_interview_pager.py`, and for the same reason: what changed is the
**region** a page object reads, and a source grep cannot show it. keel-web's own markup goes into
a Playwright page and comes back out through `Overview`.

**Four facts, and between them they are why this pass exists.**

1. **The status word is in `span.panel__pill` now**, not `span.panel__word`, and it carries
   `measuredStatus(verdict).label` **alone** with a leading glyph (FR-006/FR-007). That one
   selector is what went red on matrix run 37147770058: every panel came back `word: ""`,
   `tone: null` on a board that was drawing *Will they pay · both deal-breakers hold · 5 people
   answered* perfectly well, and §1.7's own message was *"a panel carries no status word at all"*.
2. **The card's body is a deal-breaker snapshot in three states** (FR-009 … FR-012), exhaustive
   and disjoint, keyed by `data-state` on the card itself: **C** below the floor (one grey row and
   **no foot**), **A** every deal-breaker holding (*No major blockers*, then the foot), **B**
   otherwise (at most **two** failing deal-breakers, contradicted before mixed, then `+N more ›`
   when more failed, then the foot). There is no *Held* / *Did not hold* `<dl>`, so
   `part_of`/`lines_of`/`tail_of` answer empty here rather than raising -- *retired, not deleted*.
3. **The whole card is the link** (FR-008): `<a class="panel" href="/p/{id}/s/{stage}">`, and
   nothing inside it is a second control. `.panel__name` is a `<span>`, so `AFFORDANCE` leads with
   `a.panel[data-stage]` and the tail is **text**, not a `button.more` -- which is why
   `open_every_tail()` has no subject here and must answer `0` without paying a wait.
4. **`p.ship__caption` is gone** (FR-004) and the ship column is `p.overall`, `p.overall__why` and
   two `.tiles .tile`s (FR-001 … FR-003). The line count the card's own count line used to carry
   is the first of those tiles.

**No word a model wrote is asserted anywhere below.** The headings and clauses in these fixtures
are the test's own; what is read off them is structure, presence, count, tone and scope. The five
status words and the three state letters are keel-web `translate.ts` constants and `data-state`
values -- the founder's copy and the product's own rule, never a model's prose.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from evals.test_s012_journey_through_a_host import (VERDICT_PEOPLE_FLOOR, _expected_card,
                                                    _stage_deal_breakers, _status_tone)
from harness.browser import Overview
from harness.steps import Recorder

PROJECT = "p-0001"

STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: keel-web's own hull path, abbreviated -- nothing here measures geometry.
_D = "M4 14C8 30 12 42 22 42L48 42C53 42 56 36 56 22Z"

#: `translate.ts`'s `STAGE_LABEL`, which both the band's accessible name and the card's own
#: `.panel__name` are built from.
_LABEL = {"PROBLEM": "The problem", "SOLUTION": "Your solution", "COMMERCIAL": "Will they pay"}

#: `StagePanel.PILL_GLYPH` -- a second carrier beside the tint, never the only one (FR-006).
_PILL_GLYPH = {"good": "✓", "warn": "!", "bad": "✕", "none": "–"}


# ------------------------------------------------------------------------------- the board's markup

def _band(stage: str, wash: str, word: str) -> str:
    """`ShipFigure`'s own band, unchanged by 038 (FR-027): a `path.band[data-stage].band--{wash}`
    inside the stage page's own `<a>`, whose `aria-label` is the stage and its word."""
    return (f'<a href="/p/{PROJECT}/s/{stage}" aria-label="{_LABEL[stage]} — {word}">'
            f'<path class="band band--{wash}" data-stage="{stage}" d="{_D}"/></a>')


def _head(stage: str, wash: str, word: str) -> str:
    """`StagePanel`'s head, in one row that can never wrap (FR-006): the 21 px chip, the stage name
    in ink as a **span**, the tinted pill with its glyph and the status word alone, and a
    decorative chevron."""
    return (
        '<span class="panel__head">'
        f'<span class="panel__chip chip--{wash}"><svg><path class="on" d="{_D}"/></svg></span>'
        f'<span class="panel__name">{_LABEL[stage]}</span>'
        f'<span class="panel__pill panel__pill--{wash}">'
        f'<i aria-hidden="true">{_PILL_GLYPH[wash]}</i>{word}</span>'
        '<span class="panel__chev" aria-hidden="true">›</span>'
        "</span>")


def _snap(box: str, glyph: str, text: str) -> str:
    """States A and C's single row: one `span.snap`, the glyph in an `i.gl`, and the words as a
    bare text node beside it -- which is why `_PANEL_JS` reads a row's words by taking the glyph
    out rather than by looking for an inner element."""
    return (f'<span class="snap snap--{box}"><i class="gl gl--{box}" aria-hidden="true">{glyph}'
            f"</i>{text}</span>")


def _fail(tone: str, heading: str) -> str:
    """One state-B row (FR-010): the round glyph -- `✕` for `CONTRADICTED`, `!` for `MIXED` -- and
    `beliefHeading` **alone** in `span.ln`, clamped by CSS and never cut in the DOM."""
    return (f'<span class="snaprow"><i class="gl gl--{tone}" aria-hidden="true">'
            f'{"✕" if tone == "bad" else "!"}</i><span class="ln">{heading}</span></span>')


def _tail(label: str) -> str:
    """The tail (FR-011): a `span.tailrow` holding `span.tail`. **Text inside the card's own
    link** -- no `button`, no handler, nothing to click open, which is the whole difference from
    the `button.more` the founder struck on 2026-09-30."""
    return ('<span class="snaprow tailrow"><i class="gl gl--wait" aria-hidden="true">+</i>'
            f'<span class="tail">{label}</span></span>')


def _card(stage: str, wash: str, word: str, state: str, *, body: str, foot: str = "",
          worst: bool = False) -> str:
    """One stage's card -- **an `<a>`, because the whole card is the link** (FR-008)."""
    return (f'<a class="panel panel--{wash}{" panel--worst" if worst else ""}" '
            f'href="/p/{PROJECT}/s/{stage}" data-stage="{stage}" data-state="{state}">'
            + _head(stage, wash, word) + body
            + (f'<span class="panel__count">{foot}</span>' if foot else "")
            + "</a>")


#: The three cards of the fixture board, one per state, and they are the three the live run met.
#:
#: - **COMMERCIAL** is state **A**: every deal-breaker holds, so one green row and the foot.
#: - **SOLUTION** is state **B** at the cap: four deal-breakers failed, two are shown -- the
#:   `CONTRADICTED` one first -- and `+2 more ›` stands for the rest.
#: - **PROBLEM** is state **C**: below the floor, so one grey row carrying the count, and **no
#:   foot** at all. It is also the worst stage, so it carries `panel--worst`.
_CARDS = [
    _card("COMMERCIAL", "good", "Holding up", "A",
          body=_snap("ok", "✓", "No major blockers"),
          foot="both deal-breakers hold · 5 people answered"),
    _card("SOLUTION", "warn", "People disagree", "B",
          body=('<span class="snaps">'
                + _fail("bad", "A tablet is at hand")
                + _fail("warn", "They check it the same day")
                + _tail("+2 more ›")
                + "</span>"),
          foot="1 of 5 deal-breakers holds · 5 people answered"),
    _card("PROBLEM", "none", "Too few to call", "C",
          body=_snap("wait", "–", f"3 people answered · {VERDICT_PEOPLE_FLOOR} needed"),
          worst=True),
]


def _board_html(*, headline: str = "Too few to call", tone: str = "mute", why: bool = True,
                tiles: bool = True) -> str:
    """`OverviewRoute`'s `Deck` as spec 038 draws it, condensed to the nodes the page object reads.

    `why` is FR-002's slot -- `TIP_TOO_FEW_TO_CALL` stands there **only** while the headline reads
    *Too few to call* -- and `tiles` is FR-003's two.
    """
    words = " · ".join(f"{_LABEL[s]}: {w.lower()}" for s, w in
                           (("COMMERCIAL", "Holding up"), ("SOLUTION", "People disagree"),
                            ("PROBLEM", "Too few to call")))
    bands = (_band("COMMERCIAL", "good", "Holding up")
             + _band("SOLUTION", "warn", "People disagree")
             + _band("PROBLEM", "none", "Too few to call"))
    column = [f'<svg class="ship" role="img" aria-label="{words}">{bands}</svg>',
              f'<p class="overall st-{tone}">{headline}</p>']
    if why:
        column.append('<p class="overall__why">Fewer than five people have answered this.</p>')
    if tiles:
        column.append(
            '<div class="tiles">'
            '<div class="tile"><span class="tile__ic"><svg/></span><b>16</b>'
            '<span class="tile__label">lines</span></div>'
            '<div class="tile"><span class="tile__ic"><svg/></span><b>5</b>'
            '<span class="tile__label">people asked</span></div>'
            "</div>")
    return ('<div class="deck"><div class="deck__ship">' + "".join(column) + "</div>"
            f'<div class="panels">{"".join(_CARDS)}</div></div>'
            '<div class="deck__foot"><span class="left">Every band opens its stage page.</span>'
            '<span class="right"><span class="five">Every line, every answer, named.</span>'
            f'<a class="btn primary btn--sheet" href="/p/{PROJECT}/print" target="_blank">'
            "Download the brief</a></span></div>")


# ---------------------------------------------------------------------------------- the fixtures

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


#: **A short auto-wait, and it is this module's own point too.** *Absent* is half of what is under
#: test here -- no `.panel__word`, no `.panel__claim`, no `dl.panel__body`, no `button.more`, no
#: `.ship__caption` -- so every absent node would otherwise cost the full auto-wait before a
#: `_safe_text` swallowed the timeout. `_optional_text`'s own note has the measurement.
_ABSENT_IS_THE_POINT_MS = 250


def _board(tmp_path, browser, html):
    page = browser.new_page()
    page.set_default_timeout(_ABSENT_IS_THE_POINT_MS)
    page.set_content(html)
    return page, Overview(page, Recorder(tmp_path), "http://example.invalid")


# ------------------------------------------------------------- the pill: what actually went red

def test_the_status_word_is_read_off_the_pill_with_its_tone_and_its_glyph(tmp_path, browser):
    """**DRIFT #73, held against markup so it can never come back.** keel-web 038 FR-006/FR-007:
    the word is `span.panel__pill`'s, tinted `panel__pill--<tone>`, with a leading glyph, and it is
    `measuredStatus(verdict).label` **alone** -- never `statusWithDrift`."""
    page, overview = _board(tmp_path, browser, _board_html())
    try:
        panels = {p["stage"]: p for p in overview.panels()}
        assert [p["word"] for p in overview.panels()] == ["Holding up", "People disagree",
                                                          "Too few to call"]
        assert [p["tone"] for p in overview.panels()] == ["good", "warn", "none"]
        assert [p["glyph"] for p in overview.panels()] == ["✓", "!", "–"]
        assert all(p["word"].casefold() in Overview.STATUS_WORDS for p in panels.values())
        assert all("·" not in p["word"] for p in panels.values()), (
            "the pill carries the word alone; a middle dot in it is a drift clause (FR-007)")
        # The two carriers agree, which is what §1.7 asserts without holding keel-web's strings.
        labels = {b["stage"]: b["label"] for b in overview.bands()}
        assert all(panels[s]["word"].casefold() in labels[s].casefold() for s in STAGES)
    finally:
        page.close()


def test_the_old_panel_word_read_really_would_have_come_back_empty(tmp_path, browser):
    """The red step, reproduced without staging and without a model call: `.panel__word` is not a
    node on this screen, so the reader that looked for it answered `''` for all three stages and
    §1.7 said *a panel carries no status word at all*.

    Unlike `.ocards`, this one is not a live class on another screen -- 038 renamed it -- but the
    failure shape is the same and the cost was the matrix's last step on every cell that reached
    it."""
    page, _ = _board(tmp_path, browser, _board_html())
    try:
        assert page.locator(".panel__word").count() == 0
        assert page.locator(".panel__claim").count() == 0
        assert page.locator("dl.panel__body").count() == 0
        assert page.locator(".panel__pill").count() == 3
    finally:
        page.close()


# ----------------------------------------------------------------- the card's three states

def test_each_card_carries_its_state_and_that_states_own_rows(tmp_path, browser):
    """FR-009 … FR-012, and the three are exhaustive and disjoint. One card per state, which is
    what the live board on the twin draws."""
    page, overview = _board(tmp_path, browser, _board_html())
    try:
        cards = {p["stage"]: p for p in overview.panels()}
        assert [Overview.state_of(cards[s]) for s in STAGES] == ["C", "B", "A"]
        # **A**: one green row, then the foot.
        rows = Overview.rows_of(cards["COMMERCIAL"])
        assert [r["box"] for r in rows] == ["ok"]
        assert rows[0]["text"] == "No major blockers"
        assert cards["COMMERCIAL"]["count"].endswith("5 people answered")
        # **B**: two failing rows at the cap, contradicted before mixed, each a heading alone.
        fails = Overview.fails_of(cards["SOLUTION"])
        assert [r["tone"] for r in fails] == ["bad", "warn"]
        assert [r["heading"] for r in fails] == ["A tablet is at hand",
                                                 "They check it the same day"]
        assert len(fails) == Overview.ROW_CAP
        assert Overview.card_tail(cards["SOLUTION"]) == "+2 more ›"
        # **C**: one grey row carrying the count, and **no foot** -- the row *is* the count.
        rows = Overview.rows_of(cards["PROBLEM"])
        assert [r["box"] for r in rows] == ["wait"]
        assert f"{VERDICT_PEOPLE_FLOOR} needed" in rows[0]["text"]
        assert cards["PROBLEM"]["count"] == ""
        assert Overview.card_tail(cards["PROBLEM"]) is None
    finally:
        page.close()


def test_the_tail_is_not_in_the_rows_and_the_rows_are_not_in_the_tail(tmp_path, browser):
    """`rows_of()` drops the tail and `card_tail()` is only the tail, so a scenario can never count
    *+2 more ›* as a third failing deal-breaker against the cap of two (FR-009/FR-011)."""
    page, overview = _board(tmp_path, browser, _board_html())
    try:
        card = overview.panel("SOLUTION")
        assert len(card["rows"]) == 3, "two failing rows and the tail, in the DOM's own order"
        assert len(Overview.rows_of(card)) == Overview.ROW_CAP
        assert [r["tail"] for r in card["rows"]] == [False, False, True]
    finally:
        page.close()


def test_the_retired_two_part_reads_answer_empty_rather_than_raising(tmp_path, browser):
    """*Retired, not deleted* -- the rule this harness has worked to since spec 027. The board has
    no *Held* / *Did not hold* `<dl>` (FR-009/FR-013), so the three readers that walked it answer
    empty here, which is a finding a scenario can assert rather than a crash."""
    page, overview = _board(tmp_path, browser, _board_html())
    try:
        card = overview.panel("PROBLEM")
        assert card["parts"] == {}
        assert card["claim"] == ""
        assert Overview.part_of(card, Overview.PANEL_HELD) == []
        assert Overview.lines_of(card, Overview.PANEL_DID_NOT_HOLD) == []
        assert Overview.tail_of(card, Overview.PANEL_DID_NOT_HOLD) is None
    finally:
        page.close()


def test_opening_every_tail_has_nothing_to_open_and_pays_nothing_for_it(tmp_path, browser):
    """FR-011: the tail opens nothing, holds nothing, fetches nothing and moves nothing -- it is
    text inside the card's own link. So `open_every_tail()` answers `0`, and answers it off a
    `count()` rather than a wait, which is the pattern the `028-interview-pager` pass introduced."""
    page, overview = _board(tmp_path, browser, _board_html())
    try:
        assert page.locator(".panel button").count() == 0
        assert page.locator(".panel .fails button.more").count() == 0
        assert overview.open_every_tail() == 0
        assert overview.open_every_tail() == 0
    finally:
        page.close()


# ------------------------------------------------------------------- the card is the door (FR-008)

def test_the_whole_card_is_the_link_and_the_name_is_no_longer_one(tmp_path, browser):
    """FR-008, the founder's own default on design open question 5. `.panel__name` is a `<span>`
    now, so `AFFORDANCE` leads with `a.panel[data-stage]` -- GUI-U1 reads a way onward off this
    screen, and on the board the way onward is the card itself."""
    page, overview = _board(tmp_path, browser, _board_html())
    try:
        for card in overview.panels():
            assert card["href"] == f"/p/{PROJECT}/s/{card['stage']}", card
        assert page.locator("a.panel[data-stage]").count() == 3
        assert page.locator("a.panel__name").count() == 0
        assert page.locator(Overview.AFFORDANCE).count() >= 3
    finally:
        page.close()


# ------------------------------------------------------------------- the ship column (FR-001 … 004)

def test_the_ship_column_leads_with_the_worst_stages_word_and_two_tiles(tmp_path, browser):
    """FR-001 … FR-003. This is where *the worst panel is open at rest* stands now: a card does not
    expand, and the worst stage's own word leads the column, bare and in that stage's tone."""
    page, overview = _board(tmp_path, browser, _board_html())
    try:
        assert overview.headline() == {"word": "Too few to call", "tone": "mute"}
        assert overview.worst_panel() == "PROBLEM"
        # The headline and the worst card's own pill are both `measuredStatus` on one verdict.
        assert overview.headline()["word"] == overview.panel("PROBLEM")["word"]
        assert overview.headline_note().startswith("Fewer than five")
        assert overview.tiles() == [{"value": 16, "label": "lines"},
                                    {"value": 5, "label": "people asked"}]
    finally:
        page.close()


def test_the_tip_slot_is_empty_in_every_other_state(tmp_path, browser):
    """FR-002. The other three tips are written about one belief and are false about a project, and
    there is no shipped sentence that is true of a project in a good state -- so the slot is empty,
    and `headline_note()` answers `''` off a `count()` rather than a timeout."""
    page, overview = _board(tmp_path, browser,
                            _board_html(headline="Holding up", tone="good", why=False))
    try:
        assert overview.headline() == {"word": "Holding up", "tone": "good"}
        assert overview.headline_note() == ""
    finally:
        page.close()


def test_the_ship_caption_is_gone_and_its_numbers_are_the_tiles(tmp_path, browser):
    """FR-004: `shipCaption` lost its only caller. `ship_caption()` and `ship_counts()` are kept
    and answer empty here -- the same *retired, not deleted* rule -- and the line count a scenario
    used to take off the caption is the first tile."""
    page, overview = _board(tmp_path, browser, _board_html())
    try:
        assert page.locator(".ship__caption").count() == 0
        assert overview.ship_caption() == ""
        assert overview.ship_counts() is None
        assert overview.tiles()[0]["value"] == 16
        with pytest.raises(PlaywrightError):
            page.wait_for_selector(".ship__caption", timeout=400)
    finally:
        page.close()


def test_a_column_with_no_tiles_is_read_as_a_finding_not_a_crash(tmp_path, browser):
    """A board that drew no tiles is a fault §1.7 reports, so the reader has to come back with
    something to report rather than raising inside the page object."""
    page, overview = _board(tmp_path, browser, _board_html(tiles=False))
    try:
        assert overview.tiles() == []
    finally:
        page.close()


def test_the_deck_wait_still_answers_on_the_board(tmp_path, browser):
    """`Overview.DECK` is what `open()` waits for, and 038 changed none of the three nodes it
    names -- `.deck`, `.ship` and `.panels` are all still drawn (FR-027)."""
    page, overview = _board(tmp_path, browser, _board_html())
    try:
        page.wait_for_selector(Overview.DECK, timeout=1_000)
        assert overview.is_deck()
    finally:
        page.close()


# ----------------------------------------------- the rule, restated in Python (§1.7's own helpers)

#: `GET /v2/projects/{id}/standing`, cut to what `_stage_deal_breakers` reads: the two failing
#: lists, their `stage`, their `risk` and their heading. Four deal-breakers failed on SOLUTION, one
#: `CONTRADICTED` and three `MIXED`, which is the fixture card's state B at the cap with `+2 more`.
_STANDING = {
    "holdingUp": [{"stage": "COMMERCIAL", "risk": "LOAD_BEARING", "assumptionId": "a-1",
                   "heading": "They would pay monthly"}],
    "notHoldingUp": [{"stage": "SOLUTION", "risk": "LOAD_BEARING", "assumptionId": "a-2",
                      "heading": "A tablet is at hand"},
                     {"stage": "SOLUTION", "risk": "SUPPORTING", "assumptionId": "a-3",
                      "heading": "Worth knowing, and not a deal-breaker"}],
    "peopleDisagree": [{"stage": "SOLUTION", "risk": "LOAD_BEARING", "assumptionId": "a-4",
                        "heading": "They check it the same day"},
                       {"stage": "SOLUTION", "risk": "LOAD_BEARING", "assumptionId": "a-5",
                        "heading": "Deliveries land before noon"},
                       {"stage": "SOLUTION", "risk": "LOAD_BEARING", "assumptionId": "a-6",
                        "statement": "A statement, where the belief has no heading"}],
    "untested": [{"stage": "PROBLEM", "risk": "LOAD_BEARING", "assumptionId": "a-7",
                  "heading": "Woken more than twice a night"}],
}


def test_the_failing_deal_breakers_are_the_wires_own_two_lists_in_order():
    """FR-010: `notHoldingUp` before `peopleDisagree`, each in the wire's own order, filtered to
    the stage **and to `LOAD_BEARING`** -- so the two the cap shows are the two worst (P5). A
    `SUPPORTING` line is not a deal-breaker and has no row on this card at all (FR-013)."""
    failed = _stage_deal_breakers(_STANDING, "SOLUTION")
    assert [row["tone"] for row in failed] == ["bad", "warn", "warn", "warn"]
    assert [row["heading"] for row in failed] == ["A tablet is at hand",
                                                  "They check it the same day",
                                                  "Deliveries land before noon",
                                                  "A statement, where the belief has no heading"]
    assert "Worth knowing, and not a deal-breaker" not in [row["heading"] for row in failed]
    assert _stage_deal_breakers(_STANDING, "COMMERCIAL") == []


@pytest.mark.parametrize("summary,state,rows,tail,foot", [
    # C: the verdict is UNTESTED, or absent entirely -- the floor's own state.
    ({"verdict": "UNTESTED", "peopleAnswered": 3}, "C", 1, 0, False),
    ({"peopleAnswered": 0}, "C", 1, 0, False),
    # A: every deal-breaker holds. And FR-012's edge case: none to hold means no row at all.
    ({"verdict": "SUPPORTED", "dealBreakersHolding": 2, "dealBreakersTotal": 2}, "A", 1, 0, True),
    ({"verdict": "SUPPORTED", "dealBreakersHolding": 0, "dealBreakersTotal": 0}, "A", 0, 0, True),
    # B: otherwise -- the cap of two, and the tail only past it.
    ({"verdict": "MIXED", "dealBreakersHolding": 1, "dealBreakersTotal": 5}, "B", 2, 2, True),
])
def test_the_three_states_are_exhaustive_disjoint_and_ordered(summary, state, rows, tail, foot):
    """FR-009, and the order *is* the rule. `_expected_card` is what §1.7 puts the card's own
    `data-state` against, and every input is a `StageSummary` field the wire sent."""
    want = _expected_card(summary, _stage_deal_breakers(_STANDING, "SOLUTION"))
    assert want["state"] == state
    assert want["rows"] == rows
    assert want["tail"] == tail
    assert want["foot"] is foot


def test_state_b_shows_the_first_two_and_counts_the_rest():
    """FR-011: nothing is lost to the cap -- the tail says how many more failed and the foot says
    out of how many, so four failures on a card of two rows is still four on the screen."""
    failed = _stage_deal_breakers(_STANDING, "SOLUTION")
    want = _expected_card({"verdict": "MIXED", "dealBreakersHolding": 1, "dealBreakersTotal": 5},
                          failed)
    assert want["the two the cap shows"] == ["A tablet is at hand", "They check it the same day"]
    assert want["their own glyphs"] == ["bad", "warn"]
    assert want["tail"] == len(failed) - Overview.ROW_CAP == 2


def test_the_headlines_tone_is_unwashed_where_a_bands_is_not():
    """FR-001: `OverviewRoute` writes `st-${headline.tone}` straight off `measuredStatus`, so an
    `UNTESTED` project's headline is `st-mute` where its band and its pill are `--none`. Two
    mappings, deliberately, and §1.7 reads each off its own node."""
    assert _status_tone({"verdict": "CONTRADICTED"}) == "bad"
    assert _status_tone({"verdict": "MIXED"}) == "warn"
    assert _status_tone({"verdict": "SUPPORTED"}) == "good"
    assert _status_tone({"verdict": "UNTESTED"}) == "mute"
    assert _status_tone({}) == "mute"
