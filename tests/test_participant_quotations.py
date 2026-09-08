"""`harness/browser.py`'s participant-quotation read, against the markup keel-web actually renders
(policy v9, `evals/policy.py` judgement call 12).

The same shape as `test_participant_anchor_selections.py` and `test_doors_d5_reveal_regions.py`: a
real Playwright browser over real DOM, because what v9 turns on is a **region**, and a string
comparison could never show that the region is the right one.

keel-web carries no `<blockquote>`, no `<q>`, no `cite` and no `data-*` on any quotation -- the
whole tree has exactly one `data-testid` (`median-tick`). So the structure *is* three places:

    `.pquotes p`   `PrintRoute.tsx`, the download page's *In their words* block. The person's own
                   words are the `<p>`'s **own text nodes**; the attribution is a child `<span>`
                   beside them and must stay swept.
    `.said .w`     `SaidBox.tsx`, the popover one dot opens, beside `.n`/`.k`/`.r`.
    `.pop .story`  `PersonAnswersModal.tsx`, the same `Testimony.quote`.

The companion cases are the point of the set: product-authored prose that sits beside a name must
never be read as a quotation, and `AnswersPopup`'s `.p-a` -- a participant's typed answer with no
quotation marking of any kind -- is deliberately *not* read, because there is no structure there
to key on and inventing one would be this repo deciding what keel-web meant.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from harness.browser import _participant_quotations

_WORDS = "we chase him every month, and his invoices are always late"
_STORY = "she calls me before the van leaves"

# `PrintRoute.tsx:219-228`, verbatim in shape: a `.pquotes` div, a product-authored `<b>` heading,
# then one `<p>` per quote holding the words and a bare `<span>` with the person's name.
_PRINT = """
<div class="pages"><div class="page">
  <h2>The problem</h2>
  <div class="pquotes">
    <b>In their words</b>
    <p>&ldquo;""" + _WORDS + """&rdquo; <span>Dana Okafor</span></p>
  </div>
</div></div>
"""

# `SaidBox.tsx:38-59`.
_SAID = """
<div class="card openc"><div class="strip open">
  <div class="said">
    <button type="button" class="x" aria-label="Close">&times;</button>
    <span class="n">Dana Okafor</span>
    <span class="k">Restaurant manager</span>
    <span class="w">&ldquo;""" + _STORY + """&rdquo;</span>
    <span class="r">Read as <b>1 to 2 h</b> &middot; anchored to something that happened, so it
      counts</span>
    <span class="a"><button type="button" class="btn link">See all of Dana&rsquo;s
      answers</button></span>
  </div>
</div></div>
"""

# `PersonAnswersModal.tsx:64-69`.
_MODAL = """
<div class="pop" role="dialog">
  <h2>Dana&rsquo;s answers</h2>
  <p class="hint">Their own words, exactly as typed. Seeing them changes nothing.</p>
  <p class="story">&ldquo;""" + _STORY + """&rdquo;</p>
  <div class="p-sec">What they picked</div>
</div>
"""

# `AnswersPopup.tsx:75` -- a participant's own answer with no quotation marking at all.
_ANSWERS_POPUP = """
<div class="pop" role="dialog">
  <h2>Dana&rsquo;s answers</h2>
  <div class="preview"><p class="p-q">How long did it take?
    <span class="p-a">""" + _WORDS + """</span></p></div>
</div>
"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _read(browser, html: str) -> list[str]:
    page = browser.new_page()
    page.set_content(html)
    try:
        return _participant_quotations(page)
    finally:
        page.close()


def test_the_download_pages_quote_is_read_without_the_attribution(browser):
    """The `<p>`'s own text nodes and not its `<span>`: the name is the product's, not the
    person's, and CLA-U5 must go on sweeping it."""
    read = _read(browser, _PRINT)
    assert read == [f"“{_WORDS}”"]
    assert "Dana Okafor" not in read[0]


def test_the_product_authored_heading_above_the_quotes_is_not_read(browser):
    assert "In their words" not in " ".join(_read(browser, _PRINT))


def test_the_said_boxs_words_are_read_and_its_read_as_line_is_not(browser):
    """`.w` is the quotation; `.r` (*Read as…*) and the *See all…* button are product prose that
    names the person, and both stay in CLA-U5's swept text."""
    read = _read(browser, _SAID)
    assert read == [f"“{_STORY}”"]
    joined = " ".join(read)
    assert "Read as" not in joined and "See all" not in joined


def test_the_person_modals_story_is_read(browser):
    assert _read(browser, _MODAL) == [f"“{_STORY}”"]


def test_the_answers_popups_unmarked_answer_is_deliberately_not_read(browser):
    """Judgement call 12's own limit, asserted rather than left implicit: `.p-a` carries no
    quotation marking, so there is nothing to key on and nothing is exempted. If CLA-U5 ever fires
    there it is a `runs/DRIFT.md` finding about keel-web, not a fourth selector typed into
    `harness/browser.py`."""
    assert _read(browser, _ANSWERS_POPUP) == []


def test_a_screen_that_quotes_nobody_reads_as_no_quotations(browser):
    """Every other screen keeps exactly the CLA-U5 policy v6 wrote."""
    assert _read(browser, "<div class='pages'><p>Holding up. Seven of nine.</p></div>") == []


def test_the_quotation_comes_back_as_the_page_rendered_it(browser):
    """Curly quotation marks included -- `policy.text_outside_quotations` anchors its removal on
    the product's own glyphs, so a one-word quotation cannot blow a hole in the sweep."""
    read = _read(browser, _PRINT)
    assert read[0].startswith("“") and read[0].endswith("”")


def test_whitespace_is_collapsed_the_way_the_screen_capture_collapses_it(browser):
    """`_SCREEN_TEXT_JS` collapses per text node, and the quotation has to match its own copy
    inside the whole screen's captured text character for character."""
    html = _PRINT.replace(_WORDS, "we chase\n   him   every month")
    assert _read(browser, html) == ["“we chase him every month”"]
