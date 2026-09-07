"""D5's region choice, against real markup (spec 010 `## Discovered`, the S-003 run
`runs/20260907T154237Z-s003-every-door`).

`test_doors_d5.py` proves `judge_opener` over canned strings. These two openers went red on their
first walk of that run for a reason strings alone cannot show -- the *region* `open_opener` read
was wrong, not the judgement over what it read. Real Playwright browsers, real DOM, real CSS,
condensed from what `StageRoute.tsx`/`app.css` and `SaidBox.tsx` actually render (and from that
run's own screenshots) -- same approach `test_browser_failure_capture.py` takes for its fixture: a
real browser exercising the real failure path, nothing stubbed out but the product itself.

- **The strip row** (`031-opener.png` -> `032-strip-toggled.png`): keel-web renders every line's
  chart, "Asked: ..." quote and said-box unconditionally and shows or hides them with
  `display:none` / `display:block`, never by mounting or unmounting them. The old `_deep_text`
  walked past `display:none` (it only skipped the `hidden` attribute), so a strip's hidden content
  was already counted in the "before" read and toggling it open changed nothing D5 could see --
  a real reveal read as `opens_nothing`. `harness/doors.py`'s `_DEEP_TEXT_JS` now skips a subtree
  CSS has hidden, same as `innerText` would, while still walking into the SVG `innerText` drops.

- **The popover** (`033-opener.png` -> `034-opener.png`): DRIFT #31 (keel-web's coincident-dot
  fault, left alone here) can put a different person's said box on screen than the one the walk
  meant to click -- in that run, Marisol Ortega's over Brittany Hale's. `evals/test_s003_every_door
  .py`'s `_walk_openers` used to name the *see all* button's promise from the dot it meant to
  click rather than from the said box actually open, so the button (whose own label reads "See
  all of Marisol's answers") was checked against "Brittany" and failed even though it opened
  exactly what it said. It now reads the promise from `.said .n` -- the region the button's own
  label is drawn from -- which the second test below shows does not let a *wrong* reveal pass.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from harness import doors

# ------------------------------------------------------------------ the strip row (opened card)

# Condensed from `StageRoute.tsx`'s `OpenedCard` and `app.css`'s "collapsed lines" rules: every
# line's chart and "Asked" quote are always in the DOM; only the `.strip.open` class shows them.
_STRIP_HTML = """
<div class="card openc">
  <div class="measures lines">
    <div class="strip open" id="line2">
      <div class="strip__head"><span class="caret">&#9662;</span><b>About 45 minutes at the yard</b></div>
      <div class="strip__svg">you said 35 to 55</div>
      <div class="strip__read">Asked: &ldquo;How long were you at the yard, in the line and getting loaded?&rdquo;</div>
    </div>
    <div class="strip" id="line1">
      <div class="strip__head"><span class="caret">&#9656;</span><b>Picked up mulch in the last two weeks</b></div>
      <div class="strip__svg">you said under 14</div>
      <div class="strip__read">Asked: &ldquo;When was that?&rdquo;</div>
    </div>
  </div>
</div>
<style>
  .lines .strip .strip__svg, .lines .strip .strip__read { display: none; }
  .lines .strip.open .strip__svg, .lines .strip.open .strip__read { display: block; }
</style>
<script>
  document.querySelectorAll(".strip__head").forEach((head) => {
    head.addEventListener("click", () => head.closest(".strip").classList.toggle("open"));
  });
</script>
"""

# ------------------------------------------------------------------ the popover (said -> modal)

# Condensed from `SaidBox.tsx` and `PersonAnswersModal.tsx`, as `033-opener.png`/`034-opener.png`
# actually rendered: the said box open for Marisol Ortega (DRIFT #31 put her dot's box on screen
# instead of Brittany Hale's), and the modal `onSeeAll` mounts -- a real DOM insertion, not a CSS
# toggle, so this half was never about `_deep_text`'s visibility blindness.
_POPOVER_HTML = """
<div class="said">
  <button type="button" class="x" aria-label="Close">&times;</button>
  <span class="n">Marisol Ortega</span>
  <span class="k">Crew leads</span>
  <span class="w">&ldquo;Thursday. Quick one, twenty minutes at the yard, four yards.&rdquo;</span>
  <span class="r">Read as <b>2 days to 1 week</b> &middot; anchored to something that happened, so it counts</span>
  <span class="a"><button type="button" class="btn link" id="see-all">See all of Marisol's answers</button></span>
</div>
<script>
  document.getElementById("see-all").addEventListener("click", () => {
    const pop = document.createElement("div");
    pop.className = "pop";
    pop.setAttribute("role", "dialog");
    pop.innerHTML = "<h2>Marisol's answers</h2>"
      + "<p class='hint'>Their own words, exactly as typed. Seeing them changes nothing.</p>";
    document.body.appendChild(pop);
  });
</script>
"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


# --------------------------------------------------------------------------------- the strip row

def test_a_strip_row_that_opens_by_css_is_a_reveal_not_opens_nothing(browser):
    """The bug: `.strip__svg`/`.strip__read` are always in the DOM, CSS-hidden until `.open`. The
    old deep-text walk read past `display:none`, so toggling the row changed nothing it could see.
    """
    page = browser.new_page()
    page.set_content(_STRIP_HTML)
    control = page.locator("#line1 .strip__head")
    verdict = doors.open_opener(page, control, region=".card.openc",
                                 names="Picked up mulch in the last two weeks", closer=control)
    page.close()
    assert verdict.verdict == "opens"
    assert "closed back" in verdict.detail


def test_a_strip_row_with_nothing_behind_the_toggle_still_fails(browser):
    """D5 is not weakened by reading CSS visibility: a row whose class toggles but whose content
    stays equally hidden (no matching CSS rule reveals anything) is still a dead control."""
    page = browser.new_page()
    page.set_content(_STRIP_HTML.replace(
        '.lines .strip.open .strip__svg, .lines .strip.open .strip__read { display: block; }', ''))
    control = page.locator("#line1 .strip__head")
    verdict = doors.open_opener(page, control, region=".card.openc",
                                 names="Picked up mulch in the last two weeks", closer=control)
    page.close()
    assert verdict.verdict == "opens_nothing"
    assert "nothing appeared" in verdict.detail


# ------------------------------------------------------------------------------------ the popover

def test_the_popovers_promise_is_read_from_the_open_said_box(browser):
    """The fix: name the *see all* button's promise from `.said .n` -- the region its own label is
    drawn from -- rather than from whichever dot the walk meant to click."""
    page = browser.new_page()
    page.set_content(_POPOVER_HTML)
    shown_name = page.locator(".said .n").first.inner_text()
    see_all = page.locator(".said .a button").first
    verdict = doors.open_opener(page, see_all, region="body", names=shown_name.split()[0])
    page.close()
    assert shown_name == "Marisol Ortega"
    assert verdict.verdict == "opens"
    assert "opened what it names" in verdict.detail


def test_the_popover_still_fails_when_checked_against_a_stale_name(browser):
    """Same DOM (Marisol's said box, Marisol's modal) -- naming the promise after the *dot the walk
    meant to click* (`Brittany`, as `_walk_openers` used to) still fails, exactly as it did in the
    captured run. D5 was never wrong to fail this; only which name it failed against was."""
    page = browser.new_page()
    page.set_content(_POPOVER_HTML)
    see_all = page.locator(".said .a button").first
    verdict = doors.open_opener(page, see_all, region="body", names="Brittany")
    page.close()
    assert verdict.verdict == "opens_nothing"
    assert "not what the control names" in verdict.detail
