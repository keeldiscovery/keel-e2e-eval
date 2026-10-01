"""What the overview draws since keel-web spec 027 `brief-ship`, and what the brief draws now that
the paragraph prints on it (spec `027-journey-brief-ship`, T020/T021).

The same shape as `tests/test_review_card_chips_markup.py` and for the same reason: what changed is
the **region** a page object reads, and a source grep cannot show it. keel-web's own markup goes
into a Playwright page and comes back out through `Overview` and `PrintPage`.

**Three facts, and between them they are why this spec exists.**

1. `OverviewRoute` renders **the deck** -- `div.deck` with `svg.ship`'s three
   `path.band[data-stage]` and `div.panels`' three `div.panel[data-stage]` -- and draws **no
   `.ocards` node at all**. `Overview.open()` waited for `".ocards, .guided-step"` for thirty
   seconds and timed out, which is where matrix run 36870786241 died. `.ocards` was not deleted from
   keel-web: `StageRoute`'s own opened card still draws it (keel-web 027 Discovered **D-10**), so
   the selector matched a real class on a different screen, which is the worst shape a wait can
   have. Held here against markup so it can never be put back by accident.
2. **`Overview.whatThisSays` is not on the overview any more** (keel-web FR-020), and page 1 of the
   sheet prints it under `WHAT_THIS_SAYS_HEADING` (FR-027). Pages 2-4 each draw a `p.pclaim` of
   their own -- `StageSummary.claim`, a different field with a different author -- so a sheet-wide
   `p.pclaim` read compares a stage's claim against the paragraph on the wire and passes on the
   wrong sentence. `PrintPage.what_this_says_paragraph()` is scoped to page 1, and that scope is
   what the second print fixture below exists to prove.
3. **`.ptitle` is gone** (FR-030, SC-008: five pages and *zero* `.ptitle` blocks), and
   `PrintPage.title_page()` read it for three specs. The reader is re-pointed at page 1, so every
   assertion made through it stands where it stood.

**No word a model wrote is asserted anywhere below.** The headings, claims and clauses in these
fixtures are the test's own; what is read off them is structure, presence, count and scope.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from harness.browser import Overview, PrintPage
from harness.steps import Recorder

PROJECT = "p-0001"

#: One stage's row in these fixtures: its `data-stage`, its wash, its status word, its count line,
#: the lines that held, and the lines that did not with their tags.
STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: keel-web's own three paths, abbreviated -- nothing here measures geometry, and a `d` string that
#: is not the mark's is still a `path.band[data-stage]` to a page object.
_D = "M4 14C8 30 12 42 22 42L48 42C53 42 56 36 56 22Z"


# --------------------------------------------------------------------------------- the deck's markup

def _band(stage: str, wash: str, word: str, *, linked: bool = True) -> str:
    """`ShipFigure`'s own band: a `path.band[data-stage].band--{wash}` inside the stage page's own
    `<a>`, whose `aria-label` is the stage and its word -- *colour is never the only carrier*."""
    band = f'<path class="band band--{wash}" data-stage="{stage}" d="{_D}"/>'
    if not linked:
        return f"<g>{band}</g>"
    return (f'<a href="/p/{PROJECT}/s/{stage}" aria-label="{_label(stage)} — {word}">{band}'
            f'<rect class="hit" x="20" y="12" width="19" height="19"/></a>')


def _label(stage: str) -> str:
    """`translate.ts`'s `STAGE_LABEL`, which is what the band's accessible name is built from."""
    return {"PROBLEM": "The problem", "SOLUTION": "Your solution",
            "COMMERCIAL": "Will they pay"}[stage]


def _line(heading: str, clause: str, pip: str, tag: str | None = None) -> str:
    """One row of a part: the pip, the founder's own words in bold, the risk tag where the part
    carries one, then `StandingLines.line` **verbatim in its own node**."""
    tagged = (f'<span class="tag {"db" if tag == "Deal-breaker" else "wk"}">{tag}</span>'
              if tag else "")
    return (f'<li><i class="pip {pip}" aria-hidden="true"></i><span>'
            f'<b>{heading}</b>{tagged} — <span class="fails__line">{clause}</span></span></li>')


def _tail(label: str) -> str:
    """The part's own tail. `onclick` removes the row, so `open_every_tail()` makes progress in a
    `set_content` page exactly as it does against a React handler that opens the rest in place --
    the loop is what is under test, never the animation."""
    return ('<li><i class="pip" aria-hidden="true"></i><span>'
            f'<button type="button" class="more" onclick="this.closest(\'li\').remove()">'
            f'{label}</button></span></li>')


def _part(label: str, rows: list[str]) -> str:
    """`StagePanel`'s `Part`: a `dt` and a `dd`, and **nothing at all** where the list is empty --
    `Part` returns `null`, so an absent part is an absent `dt`, not an empty one."""
    if not rows:
        return ""
    return f'<dt>{label}</dt><dd><ul class="fails">{"".join(rows)}</ul></dd>'


def _panel(stage: str, wash: str, word: str, count: str, *, held: list[str], failed: list[str],
           claim: str = "A claim the model wrote.", worst: bool = False) -> str:
    body = _part("Held", held) + _part("Did not hold", failed)
    return (f'<div class="panel panel--{wash}{" panel--worst" if worst else ""}" '
            f'data-stage="{stage}">'
            f'<div class="panel__head">'
            f'<a class="panel__name" href="/p/{PROJECT}/s/{stage}">{_label(stage)} ›</a>'
            f'<span class="panel__word st-{"mute" if wash == "none" else wash}">{word}</span>'
            f"</div>"
            + (f'<p class="panel__claim clamp2">{claim}</p>' if claim else "")
            + f'<p class="panel__count">{count}</p>'
            + (f'<dl class="panel__body">{body}</dl>' if body else "")
            + "</div>")


#: The three panels of the fixture deck. The problem stage is the worst (`CONTRADICTED`), so its
#: panel carries `panel--worst` and **no tail**; the solution stage has four failed lines and shows
#: three with a tail, which is the rest-of-three budget keel-web FR-015 sets.
_PANELS = [
    _panel("COMMERCIAL", "good", "Holding up",
           "5 of 5 lines holding · both deal-breakers hold · 12 people answered",
           held=[_line("They would pay monthly", "nine of twelve inside your band", "up"),
                 _line("Price is not the blocker", "ten of twelve inside your band", "up")],
           failed=[]),
    _panel("SOLUTION", "warn", "People disagree",
           "2 of 6 lines holding · 1 of 3 deal-breakers holds · 12 people answered",
           held=[_line("They already log deliveries", "eight of twelve inside your band", "up")],
           failed=[_line("A tablet is at hand", "three of twelve inside your band", "down",
                         tag="Deal-breaker"),
                   _line("They check it the same day", "people split either side", "split",
                         tag="Deal-breaker"),
                   _line("Deliveries are logged the same day", "four of twelve", "down",
                         tag="Worth knowing"),
                   _tail("1 more, worth knowing ›")]),
    _panel("PROBLEM", "bad", "Not holding up",
           "3 of 7 lines holding · 1 of 3 deal-breakers holds · 12 people answered",
           held=[_line("Woken more than twice a night", "seven of twelve inside your band", "up")],
           failed=[_line("Crying they couldn't read", "two of twelve inside your band", "down",
                         tag="Deal-breaker"),
                   _line("It costs them a morning", "people split either side", "split",
                         tag="Worth knowing")],
           worst=True),
]


def _deck_html(*, download: str = "ready", people_line: bool = True) -> str:
    """`OverviewRoute`'s `Deck`, condensed to the nodes the page object reads.

    `download` is one of keel-web FR-025's two overview states: `ready` is the filled primary with
    `target="_blank"`, `nothing` is the present-disabled-and-says-why control.
    """
    words = " · ".join(f"{_label(stage)}: {word.lower()}" for stage, word in
                       (("COMMERCIAL", "Holding up"), ("SOLUTION", "People disagree"),
                        ("PROBLEM", "Not holding up")))
    bands = (_band("COMMERCIAL", "good", "Holding up")
             + _band("SOLUTION", "warn", "People disagree")
             + _band("PROBLEM", "bad", "Not holding up"))
    if download == "ready":
        control = (f'<a class="btn primary btn--sheet" href="/p/{PROJECT}/print" target="_blank" '
                   f'rel="noopener">Download the brief</a>')
    else:
        control = ('<span class="hint deck__why">The brief fills as your AI reads answers.</span>'
                   '<a class="btn btn--sheet" aria-disabled="true">Nothing to hand over yet</a>')
    return (
        '<div class="deck">'
        '<div class="deck__ship">'
        f'<svg class="ship" viewBox="0 9 64 48" role="img" aria-label="{words}" focusable="false">'
        f'{bands}<path class="sea" d="M0 30H64"/><path class="rig" d="{_D}"/></svg>'
        '<p class="ship__caption">Countly · 18 lines · 12 asked</p>'
        + ('<p class="deck__people hint">12 people asked · 12 answered · 9 read by your AI</p>'
           if people_line else "")
        + "</div>"
        f'<div class="panels">{"".join(_PANELS)}</div>'
        "</div>"
        '<div class="deck__foot">'
        '<span class="left">Every band opens its stage page, with the claim, every line and '
        "every person’s answer.</span>"
        '<span class="right"><span class="five">Every line, every answer, named.</span>'
        f"{control}</span></div>"
    )


# -------------------------------------------------------------------------------- the sheet's markup

#: The paragraph page 1 prints, and the three stage claims it must never be confused with.
_PARAGRAPH = ("Twelve people answered, and the thing that does not hold is the tablet: three of "
              "them have one at hand where you expected nine.")
_STAGE_CLAIMS = {"PROBLEM": "Parents are woken more than twice a night.",
                 "SOLUTION": "A tablet is at hand when the delivery lands.",
                 "COMMERCIAL": "They would pay monthly for this."}

#: Two people the sheet names on a stage page, and must not name on page 5.
_PEOPLE = ("Amara Odili", "Jonas Berg")


def _print_html(*, paragraph: str | None = _PARAGRAPH, names_on_page_five: bool = False) -> str:
    """`PrintRoute`'s five pages, condensed: page 1 with the hand-off line, the 16:9 block and the
    paragraph under its heading; one page a stage with its own `p.pclaim` and its table; the
    evidence page with four named columns and nobody's name.

    `names_on_page_five` draws the thing FR-029 forbids, so the reader can be shown to find it.
    """
    block = "".join(
        f'<div class="ppanel ppanel--{wash}">'
        f'<p class="ppanel__head">{_label(stage)} '
        f'<span class="ppanel__word st-{wash}">{word}</span></p>'
        f'<p class="ppanel__in">{count}</p></div>'
        for stage, wash, word, count in (
            ("COMMERCIAL", "good", "Holding up", "5 of 5 lines holding · both deal-breakers hold"),
            ("SOLUTION", "warn", "People disagree", "2 of 6 lines holding · 1 of 3 deal-breakers holds"),
            ("PROBLEM", "bad", "Not holding up", "3 of 7 lines holding · 1 of 3 deal-breakers holds")))
    page_one = (
        '<div class="page">'
        '<div class="pkicker"><svg class="pkicker__mark"></svg>Keel brief · 1 October 2026</div>'
        "<h1>Countly</h1>"
        '<p class="psub">Operations lead · United Kingdom</p>'
        '<p class="pmeta">12 people asked · 12 answered · 18 of 18 lines have answers</p>'
        '<p class="pmeta">The problem: not holding up · Your solution: people disagree</p>'
        '<p class="phandoff">Hand it to whoever builds this: your own AI, your team, an agency.</p>'
        '<div class="p169"><div>'
        '<svg class="ship" viewBox="0 9 64 48" aria-hidden="true" focusable="false">'
        + _band("COMMERCIAL", "good", "", linked=False)
        + _band("SOLUTION", "warn", "", linked=False)
        + _band("PROBLEM", "bad", "", linked=False)
        + "</svg></div>"
        f"<div>{block}</div></div>"
        '<p class="p169__cap">16:9 · lift this block straight into a deck</p>'
        + (f"<h3>What this says</h3><p class=\"pclaim\">{paragraph}</p>" if paragraph else "")
        + "</div>")

    def stage_page(stage: str) -> str:
        return (
            '<div class="page">'
            f'<h2>{_label(stage)} <span class="st-bad">Not holding up</span></h2>'
            f'<p class="pclaim">{_STAGE_CLAIMS[stage]}</p>'
            '<p class="pmeta">12 asked · 12 answered · 1 of 3 deal-breakers holds</p>'
            '<p class="plab">Held</p>'
            '<ul class="plist"><li><i class="pip up"></i><span><b>A line that held</b> — '
            'eight of twelve inside your band</span></li></ul>'
            '<p class="plab">Did not hold</p>'
            '<ul class="plist"><li><i class="pip down"></i><span><b>A line that did not</b> — '
            'three of twelve inside your band</span></li></ul>'
            '<table class="ptab"><thead><tr><th>What it measures</th><th>You said</th>'
            "<th>The answers</th><th></th></tr></thead>"
            "<tbody><tr><td>A line that held</td><td>about eight</td>"
            '<td>eight of twelve</td><td class="st-good">Holding up</td></tr></tbody></table>'
            f'<div class="pquotes"><b>In their words</b><p>“It takes a morning.” '
            f"<span>{_PEOPLE[0]}</span></p></div></div>")

    names = ("".join(f'<div class="pquotes"><p>“x” <span>{who}</span></p></div>'
                     for who in _PEOPLE) if names_on_page_five else "")
    evidence = (
        '<div class="page">'
        "<h2>The evidence</h2>"
        '<p class="pmeta">Every line, the question that measured it, and where the answers '
        "landed.</p>"
        '<table class="ptab"><thead><tr><th>Line</th><th>The question asked</th>'
        "<th>Where they landed</th><th>Counted</th></tr></thead><tbody>"
        "<tr><td>A line that held</td><td>How many nights last week?</td>"
        '<td><span class="pdist"></span> <span>mostly inside</span></td>'
        "<td>12 of 12 counted</td></tr>"
        f"<tr><td>A line that did not</td><td>Was a tablet at hand?</td>"
        f'<td><span class="pdist"></span> <span>mostly outside</span></td>'
        f"<td>12 of 12 counted{', said by ' + _PEOPLE[1] if names_on_page_five else ''}</td></tr>"
        f"</tbody></table>{names}</div>")
    return ('<div class="pages">' + page_one
            + "".join(stage_page(stage) for stage in STAGES) + evidence + "</div>")


# ---------------------------------------------------------------------------------- the fixtures

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


#: **A short auto-wait, and it is the fixtures' own point** (`test_review_card_chips_markup.py`'s
#: D-12, same reason). *Absent* is what half of these fixtures are about -- no `.ocards`, no
#: `.next`, no `.ptitle`, no tail on the worst panel -- so every absent node would otherwise cost
#: thirty seconds of Playwright auto-wait before `_safe_text` swallowed the timeout.
_ABSENT_IS_THE_POINT_MS = 250


def _overview(tmp_path, browser, html):
    page = browser.new_page()
    page.set_default_timeout(_ABSENT_IS_THE_POINT_MS)
    page.set_content(html)
    return page, Overview(page, Recorder(tmp_path), "http://example.invalid")


def _print(tmp_path, browser, html):
    page = browser.new_page()
    page.set_default_timeout(_ABSENT_IS_THE_POINT_MS)
    page.set_content(html)
    return page, PrintPage(page, Recorder(tmp_path), "http://example.invalid")


# ------------------------------------------------- what `open()` waits for, and what it waited for

def test_the_deck_matches_what_open_waits_for(tmp_path, browser):
    """FR-001. `Overview.DECK` is what `open()` passes to `wait_for_selector`, and the deck answers
    it -- on the ship, on the panels and on `.deck` itself, so a phone shell that wraps the deck in
    other chrome (keel-web specs 028/029) still satisfies it."""
    page, overview = _overview(tmp_path, browser, _deck_html())
    try:
        page.wait_for_selector(Overview.DECK, timeout=1_000)
        assert overview.is_deck()
        for one in (".deck", ".ship", ".panels"):
            assert page.locator(one).count() > 0, one
    finally:
        page.close()


def test_the_old_wait_really_would_have_timed_out_on_the_deck(tmp_path, browser):
    """The red run, reproduced without a browser against staging and without a model call: this is
    `wait_for_selector(".ocards, .guided-step")` on the screen matrix run 36870786241 was shown.

    `.ocards` is still a live class in keel-web -- on `StageRoute`'s opened card (keel-web 027
    **D-10**) -- so the wait was not for a deleted node but for a node on another screen, and it
    could only ever end in the full thirty seconds.
    """
    page, _ = _overview(tmp_path, browser, _deck_html())
    try:
        assert page.locator(".ocards, .guided-step").count() == 0
        with pytest.raises(PlaywrightError):
            page.wait_for_selector(".ocards, .guided-step", timeout=400)
    finally:
        page.close()


def test_the_walks_current_step_still_satisfies_the_wait(tmp_path, browser):
    """`OverviewRoute` renders `GuidedStep` instead of the deck while any stage is still a draft,
    which is the state this page object is opened in for most of the journey. `.guided-step` stays
    in `DECK` for exactly that, and `is_deck()` is how a scenario tells the two apart."""
    page, overview = _overview(
        tmp_path, browser,
        '<div class="guided-step"><div class="guided-step__kicker">Step 1 of 4</div></div>')
    try:
        page.wait_for_selector(Overview.DECK, timeout=1_000)
        assert not overview.is_deck()
    finally:
        page.close()


# ------------------------------------------------------------------------------ the bands and words

def test_the_ship_reads_three_bands_each_with_a_verdict_class_and_a_word(tmp_path, browser):
    """FR-002/FR-003. Position means stage and colour means verdict -- and the verdict is a **word**
    on the band's own link as well, so a deck stripped of every colour still reports all three."""
    page, overview = _overview(tmp_path, browser, _deck_html())
    try:
        bands = overview.bands()
        assert [b["stage"] for b in bands] == ["COMMERCIAL", "SOLUTION", "PROBLEM"], bands
        assert [b["wash"] for b in bands] == ["good", "warn", "bad"], bands
        assert all(b["href"].endswith(f"/s/{b['stage']}") for b in bands), bands
        assert all(_label(b["stage"]) in b["label"] for b in bands), bands
        assert overview.ship_label().count("·") == 2, overview.ship_label()
        assert overview.ship_counts() == (18, 12), overview.ship_caption()
    finally:
        page.close()


def test_a_band_with_no_link_is_still_read(tmp_path, browser):
    """The sheet's 16:9 block renders the same figure without a `projectId`, so its bands are a
    drawing and say so with `aria-hidden`. `bands()` reads the wash off the path either way; the
    link is where there is one."""
    page, overview = _overview(
        tmp_path, browser,
        f'<div class="deck"><svg class="ship">{_band("PROBLEM", "none", "", linked=False)}</svg>'
        "</div>")
    try:
        assert overview.bands() == [{"stage": "PROBLEM", "wash": "none", "lit": False,
                                     "label": "", "href": ""}]
    finally:
        page.close()


# --------------------------------------------------------------------------------- the three panels

def test_each_panel_names_its_stage_its_word_and_its_count_line(tmp_path, browser):
    """FR-008/FR-009. The successor to `stage_cards()`: three panels, in the bands' own order, each
    with the stage's name as a link, one status word with its tone, and one count line."""
    page, overview = _overview(tmp_path, browser, _deck_html())
    try:
        panels = overview.panels()
        assert [p["stage"] for p in panels] == ["COMMERCIAL", "SOLUTION", "PROBLEM"]
        assert [p["word"] for p in panels] == ["Holding up", "People disagree", "Not holding up"]
        assert [p["wash"] for p in panels] == ["good", "warn", "bad"]
        assert [p["tone"] for p in panels] == ["good", "warn", "bad"]
        assert all(_label(p["stage"]) in p["name"] for p in panels), panels
        assert all("lines holding" in p["count"] for p in panels), panels
        assert all("people answered" in p["count"] for p in panels), panels
        assert all(p["claim"] for p in panels), "PANEL_SHOWS_CLAIM is on by default (FR-031)"
        assert overview.panel("PROBLEM")["word"] == "Not holding up"
    finally:
        page.close()


def test_a_panels_two_parts_are_read_with_their_lines_tags_and_pips(tmp_path, browser):
    """FR-011/FR-012. Evidence both ways, HELD first, and the risk tag on the failed part alone --
    *Worth knowing* is a thing to say about a failure, not about something that holds (keel-web 027
    **D-07**). The clause is read out of its own node, so nothing around it can be read as part of
    it."""
    page, overview = _overview(tmp_path, browser, _deck_html())
    try:
        panel = overview.panel("PROBLEM")
        held = Overview.lines_of(panel, Overview.PANEL_HELD)
        failed = Overview.lines_of(panel, Overview.PANEL_DID_NOT_HOLD)
        assert [row["pip"] for row in held] == ["up"]
        assert [row["pip"] for row in failed] == ["down", "split"]
        assert [row["tag"] for row in held] == [""], "a line that held carries no tag"
        assert [row["tag"] for row in failed] == ["Deal-breaker", "Worth knowing"]
        assert held[0]["line"] == "seven of twelve inside your band"
        assert "—" not in held[0]["line"], "the clause's own node, not the row's whole text"
    finally:
        page.close()


def test_a_part_with_no_lines_draws_no_heading_at_all(tmp_path, browser):
    """keel-web's own edge case: no failing line means `DID NOT HOLD` is **absent**, not an empty
    heading. So an absent key is a finding, and `lines_of` answers `[]` for it rather than
    raising."""
    page, overview = _overview(tmp_path, browser, _deck_html())
    try:
        panel = overview.panel("COMMERCIAL")
        assert Overview.part_of(panel, Overview.PANEL_DID_NOT_HOLD) == []
        assert len(Overview.lines_of(panel, Overview.PANEL_HELD)) == 2
    finally:
        page.close()


def test_the_worst_panel_is_marked_and_open_at_rest_and_the_others_carry_tails(tmp_path, browser):
    """FR-015/FR-016. The worst stage's panel is the one open at rest -- read as *no tail*, because
    a tail only renders behind the three a closed part shows. The marker itself is asserted beside
    it, because that marker is what the phone's CSS hoists (FR-018)."""
    page, overview = _overview(tmp_path, browser, _deck_html())
    try:
        assert overview.worst_panel() == "PROBLEM"
        worst = overview.panel("PROBLEM")
        assert Overview.tail_of(worst, Overview.PANEL_HELD) is None
        assert Overview.tail_of(worst, Overview.PANEL_DID_NOT_HOLD) is None
        solution = overview.panel("SOLUTION")
        assert Overview.tail_of(solution, Overview.PANEL_DID_NOT_HOLD) == "1 more, worth knowing ›"
        assert len(Overview.lines_of(solution, Overview.PANEL_DID_NOT_HOLD)) == 3, (
            "a part at rest shows at most three lines (FR-015)")
    finally:
        page.close()


def test_opening_every_tail_leaves_none_behind(tmp_path, browser):
    """A budget moves a number; it never deletes one. `open_every_tail()` is how a scenario counts
    a stage's lines off the screen instead of off the three a panel shows at rest."""
    page, overview = _overview(tmp_path, browser, _deck_html())
    try:
        assert overview.open_every_tail() == 1
        assert page.locator(".panel .fails button.more").count() == 0
        assert overview.open_every_tail() == 0
    finally:
        page.close()


# --------------------------------------------------------------- the foot, and the download's states

def test_the_foot_carries_the_band_sentence_the_five_words_and_a_live_download(tmp_path, browser):
    """FR-019/FR-025 state 1. `target="_blank"` is why `Overview.download()` waits for a popup and
    why `PrintPage.stub_print()` installs on the context."""
    page, overview = _overview(tmp_path, browser, _deck_html())
    try:
        assert overview.foot_line().startswith("Every band opens its stage page")
        assert overview.five_words() == "Every line, every answer, named."
        state = overview.download_state()
        assert state["label"] == "Download the brief"
        assert state["enabled"] is True
        assert state["href"] == f"/p/{PROJECT}/print"
        assert overview.download_link_text() == "Download the brief"
        link = page.locator(".deck__foot a.btn--sheet")
        assert link.first.get_attribute("target") == "_blank"
    finally:
        page.close()


def test_before_a_reading_the_download_is_present_disabled_and_says_why(tmp_path, browser):
    """FR-025 state 3. An anchor with no `href` navigates nowhere, which is the whole mechanism --
    and a disabled control that does not say why is a bug the founder has to guess at."""
    page, overview = _overview(tmp_path, browser, _deck_html(download="nothing"))
    try:
        state = overview.download_state()
        assert state["label"] == "Nothing to hand over yet"
        assert state["enabled"] is False
        assert state["href"] is None
        assert state["why"] == "The brief fills as your AI reads answers."
    finally:
        page.close()


def test_the_people_line_is_absent_when_every_answer_is_read(tmp_path, browser):
    """FR-021: the line stands only while an answer is waiting on a reader -- absent on Countly,
    where all twelve are read. Absence is the assertion, so `people_line()` answers `""`."""
    page, overview = _overview(tmp_path, browser, _deck_html(people_line=False))
    try:
        assert overview.people_line() == ""
        assert overview.deck_text(), "the deck still has text; only that one line is gone"
    finally:
        page.close()


# ------------------------------------------------- what the overview stopped drawing, read as absent

def test_the_overview_no_longer_draws_the_bar_the_legend_the_cards_or_the_paragraph(tmp_path, browser):
    """FR-020, from this side. **Every retired reader is kept and answers empty**, so a scenario can
    assert the old screen is gone instead of discovering it as a crash -- and so no assertion had to
    be deleted to make this branch green."""
    page, overview = _overview(tmp_path, browser, _deck_html())
    try:
        assert overview.evidence_line() == ""
        assert overview.percent_line() == ""
        assert overview.lines_with_answers() is None
        assert overview.legend_present() is False
        assert overview.legend() == {word: 0 for word in Overview.LEGEND_WORDS}, (
            "four zeroes, which is why `legend_present()` exists beside it")
        assert overview.stage_cards() == []
        assert overview.carries_what_this_says() is False
        assert overview.what_this_says() == ""
        assert overview.what_this_says_paragraph() == ""
    finally:
        page.close()


def test_guidance_still_finds_a_way_onward_on_the_deck(tmp_path, browser):
    """GUI-U1's reader, re-pointed and not re-scoped (`harness/rubric.py::_need_exists`): the check
    asks *where a stage still needs something, does this screen offer a way onward*. The evidence
    bar's `.evidence__people a` and the cards' `.see` are gone; the panels' stage links, the bands
    and the download are what the deck offers, and `Overview.AFFORDANCE` is the one list."""
    page, _ = _overview(tmp_path, browser, _deck_html())
    try:
        found = page.locator(Overview.AFFORDANCE).count()
        assert found >= 7, (
            f"the affordance sweep found {found} doors on the deck; there are three panel links, "
            f"three bands and the download")
        assert page.locator(".ocards .see, .evidence__people a").count() == 0, (
            "the two retired selectors are kept in the list for older bundles and match nothing "
            "here, which is what makes keeping them free")
    finally:
        page.close()


# --------------------------------------------------------------------------- the brief, five pages

def test_the_brief_is_five_pages_and_the_title_page_is_gone(tmp_path, browser):
    """FR-030 / SC-008: exactly five `.page` elements and **zero `.ptitle`**. `title_page()` is
    re-pointed at page 1, so every assertion made through it stands where it stood."""
    page, sheet = _print(tmp_path, browser, _print_html())
    try:
        assert sheet.page_count() == 5
        assert page.locator(".ptitle").count() == 0
        title = sheet.title_page()
        assert title["name"] == "Countly"
        assert title["kicker"].startswith("Keel brief")
        assert title["sub"] == "Operations lead · United Kingdom"
        assert "12 people asked" in title["meta"] and "The problem: not holding up" in title["meta"]
        assert not sheet.has_founder_chrome()
    finally:
        page.close()


def test_page_one_carries_the_paragraph_under_its_heading_and_the_block(tmp_path, browser):
    """FR-022/FR-026/FR-027: the hand-off line, the ruled 16:9 block with its three bands, three
    `ppanel`s and its caption, and the paragraph under `WHAT_THIS_SAYS_HEADING`."""
    page, sheet = _print(tmp_path, browser, _print_html())
    try:
        one = sheet.page_one()
        assert one["handoff"].startswith("Hand it to whoever builds this")
        assert sheet.what_this_says_heading() == "What this says"
        assert sheet.what_this_says_paragraph() == _PARAGRAPH
        assert sheet.what_this_says().startswith("What this says ")
        block = sheet.block_169()
        assert block["present"] is True
        assert [b["stage"] for b in block["bands"]] == ["COMMERCIAL", "SOLUTION", "PROBLEM"]
        assert [b["wash"] for b in block["bands"]] == ["good", "warn", "bad"]
        assert len(block["panels"]) == 3
        assert block["panels"][0]["word"] == "Holding up"
        assert "lines holding" in block["panels"][0]["count"]
        assert block["caption"] == "16:9 · lift this block straight into a deck"
    finally:
        page.close()


def test_the_paragraph_reader_is_scoped_to_page_one_and_never_reads_a_stages_claim(tmp_path, browser):
    """**The scope is the assertion.** Pages 2-4 each draw a `p.pclaim` -- `StageSummary.claim`, a
    different field with a different author -- so a sheet-wide read would compare the problem
    stage's claim against `Overview.whatThisSays` on the wire and fail on a correct product. With
    the paragraph absent the reader answers `""`, and the three stage claims are still there."""
    page, sheet = _print(tmp_path, browser, _print_html(paragraph=None))
    try:
        assert sheet.what_this_says_paragraph() == ""
        assert sheet.what_this_says_heading() == "", (
            "PrintRoute draws the heading and the paragraph together or neither, and prints no "
            "*not yet* note in their place")
        assert page.locator("p.pclaim").count() == 3, (
            "the three stage claims are what a sheet-wide `p.pclaim` read would have picked up")
        assert sheet.page_count() == 5
    finally:
        page.close()


def test_the_stage_tables_are_read_and_the_evidence_table_is_not_counted_among_them(tmp_path, browser):
    """The break this reader had to be re-scoped for: page 5's evidence table is a `table.ptab`
    too, so the sheet-wide read answered four rows and the fourth's columns are the evidence
    page's -- a caller's assertion failing on a correct product."""
    page, sheet = _print(tmp_path, browser, _print_html())
    try:
        columns = sheet.table_columns()
        assert len(columns) == 3, columns
        for row in columns:
            assert tuple(row[:3]) == PrintPage.COLUMNS, row
        assert page.locator("table.ptab").count() == 4, (
            "four tables on the sheet, three of them a stage's")
        assert sheet.table_rows(3)[0][0] == "A line that held", (
            "`table_rows` is still indexed over the sheet's own tables, so 3 is the evidence one")
        assert len(sheet.parts(1)["Held"]) == 1
        assert len(sheet.parts(1)["Did not hold"]) == 1
    finally:
        page.close()


def test_the_evidence_page_counts_every_line_and_names_nobody(tmp_path, browser):
    """FR-029 / SC-009, principle **P8**. This is the page most likely to be forwarded, and the
    named quotes stay on the stage pages where a founder can check them -- which is asserted too."""
    page, sheet = _print(tmp_path, browser, _print_html())
    try:
        evidence = sheet.evidence_page()
        assert evidence["heading"] == "The evidence"
        assert tuple(evidence["columns"]) == PrintPage.EVIDENCE_COLUMNS
        assert len(evidence["rows"]) == 2
        assert evidence["names"] == []
        assert all(who not in " ".join(sum(evidence["rows"], [])) for who in _PEOPLE)
        assert sheet.participant_names() == [_PEOPLE[0]] * 3, (
            "one named quote on each of the three stage pages, and none on page 5")
        assert len(sheet.quotes()) == 3
    finally:
        page.close()


def test_a_name_on_the_evidence_page_is_found_rather_than_missed(tmp_path, browser):
    """The failure SC-009 exists to catch, drawn on purpose: a reader that cannot see a leak is not
    a check. Both shapes -- a name in a cell and an *In their words* block on page 5 -- are
    found."""
    page, sheet = _print(tmp_path, browser, _print_html(names_on_page_five=True))
    try:
        evidence = sheet.evidence_page()
        assert _PEOPLE[1] in " ".join(sum(evidence["rows"], []))
        assert evidence["names"] == list(_PEOPLE)
    finally:
        page.close()
