"""`ParticipantPage` against keel-web 042's pager, in a real browser (`runs/DRIFT.md` #71).

**This is the test that would have caught it.** The matrix lost the whole participant leg on every
cell of 2026-10-03 -- every host, plus the `keel` door that runs no host CLI, no plugin and no
runtime -- because `open()` waited fifteen seconds for `.iv p.hello` on a page keel-web had stopped
drawing it on. Nothing in this repository could see that: the scenarios are the only callers, a
stack is the only way to run them, and a selector that matches nothing is indistinguishable from a
slow page until the bundle is read. The three tests that already hold this page object to real
markup (`test_participant_anchor_selections.py`, `test_participant_submit_sent.py`,
`test_participant_quotations.py`) each hold **one** region. This one holds the **shape**: the three
screens, the gate, the counter, Next and Back, the one nudge, the send, and the completion screen.

It is the same bargain as those three. A real Playwright browser over the DOM
`ParticipantRoute.tsx` renders (`tests/interview_page.py`, which copies every class and label from
that route and from `src/lib/translate.ts`), because what goes stale is a *region* and a string
comparison cannot show it. It does not run a stack, spend a model or need a product checkout.

The companion cases are as much the point as the happy ones: a gate whose label nobody wrote down
must raise rather than be pressed blind, a Next asked for on the last part must raise rather than
send, and a send that never lands must raise rather than be believed.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from harness.browser import (INTERVIEW_BACK, INTERVIEW_BEGIN, INTERVIEW_CONTINUE,
                             INTERVIEW_DONE_TITLE, INTERVIEW_HEAD_WHAT, INTERVIEW_NEXT,
                             INTERVIEW_SEND, ParticipantPage)
from harness.steps import Recorder
from tests import interview_page

_A1 = "Think of the last night the baby woke and would not settle."
_A2 = "Think of the last baby app you paid for."
_A3 = "Think of the last time you asked somebody else what to try."

_S1 = "How long were you up, that time?"
_S2 = "What did you try first?"


def _three_parts() -> list[dict]:
    return [
        interview_page.part("The last wake-up", [interview_page.anchor(
            _A1, taps=["it hasn't happened to me", "it has, but I can't recall one"],
            selections=[
                interview_page.selection(_S1, ["under 15 min", "15 to 60 min",
                                               "more than 2 hours, say roughly"],
                                         escapes=["rather not say"]),
                interview_page.selection(_S2, ["fed them", "walked them", "an app"], other=True),
            ])]),
        interview_page.part("The last app you paid for", [interview_page.anchor(
            _A2, selections=[interview_page.selection(_S1, ["under 15 min", "15 to 60 min"])])]),
        interview_page.part("The last time you asked somebody", [interview_page.anchor(_A3)]),
    ]


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _participant(tmp_path, browser, html):
    page = browser.new_page()
    page.set_content(html)
    return ParticipantPage(page, Recorder(tmp_path)), page


# --------------------------------------------------------------- the opening screen, and the gate

def test_the_opening_screen_is_what_a_stranger_is_shown_first(tmp_path, browser):
    """Every line `open()` captures, where 042 draws it. The selector that went stale was the
    introduction's, and the rest of this screen never existed before."""
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        assert participant.screen() == "opening"
        opening = participant.opening()
        assert opening["head"]["what"] == INTERVIEW_HEAD_WHAT
        assert "KEEL" in opening["head"]["words"]
        assert opening["introduction"].startswith("Eval Founder asked if you'd answer")
        assert opening["consent"]["heading"] == interview_page.CONSENT_HEADING
        assert opening["consent"]["lines"] == [interview_page.CONSENT_LINE]
        assert "skip" in opening["facts"].lower(), "the skip affordance is on the facts line now"
        assert opening["button"] == INTERVIEW_BEGIN
        assert opening["kept answers"] == "", "a fresh link is holding nothing"
        # And the asides, which used to be `.iv > p.hint` on one scroll.
        assert interview_page.METHOD in participant.hints()
        assert interview_page.FACTS in participant.hints()
    finally:
        page.close()


def test_the_old_intro_selector_is_not_on_the_opening_screen_at_all(tmp_path, browser):
    """The fault itself, stated as a fact about the page: `p.hello` is **not** what the open form
    draws, so a wait on it can only ever time out. It survives on the notice states, which is why
    `open_expect_notice` still reads it."""
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        assert page.locator("p.hello").count() == 0
        assert page.locator(".iv p.hello").count() == 0
        assert page.locator("main.iv-body p.iv-intro").count() == 1
    finally:
        page.close()


def test_begin_opens_the_first_part(tmp_path, browser):
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        landed = participant.begin()
        assert landed == {"index": 1, "total": 3, "title": "The last wake-up", "counter": "1 of 3"}
        assert participant.screen() == "part"
        assert participant.part_count() == 3
        assert participant.primary_label() == INTERVIEW_NEXT
    finally:
        page.close()


def test_continue_resumes_at_the_part_the_kept_answers_were_left_on(tmp_path, browser):
    """042 FR-014: unsent answers live in `localStorage` per link, the gate reads **Continue**, and
    `p.iv-draft` is the only sentence the page says about them. The harness presses whichever of
    the two labels it finds and **reads** where it landed rather than assuming part one -- which is
    the whole of what a reload mid-journey changes."""
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts(), draft_at=1))
    try:
        assert participant.primary_label() == INTERVIEW_CONTINUE
        assert participant.draft_line() == interview_page.DRAFT_LINE
        landed = participant.begin()
        assert landed["index"] == 2, "Continue resumes; it does not start over"
        # ...and the walk still reads the whole interview, because it goes back first.
        assert [p["title"] for p in participant.questionnaire()] == [
            "The last wake-up", "The last app you paid for", "The last time you asked somebody"]
        assert participant.part()["index"] == 1, "the walk leaves the stranger on part one"
    finally:
        page.close()


def test_a_gate_label_nobody_wrote_down_raises_rather_than_being_pressed(tmp_path, browser):
    """The companion to `begin()`. A third label on that button is a copy change in keel-web, and
    pressing it blind would walk the interview somewhere nobody wrote down."""
    # The label is swapped where the page gets it from -- its own copy of keel-web's constants --
    # so the button really does render a word this harness has never been told about.
    html = interview_page.interview_html(_three_parts()).replace(
        f'"begin": "{interview_page.BEGIN}"', '"begin": "Start the survey"')
    participant, page = _participant(tmp_path, browser, html)
    try:
        with pytest.raises(AssertionError, match="Start the survey"):
            participant.begin()
    finally:
        page.close()


# ------------------------------------------------------------------------------------- the pager

def test_the_whole_interview_is_read_by_walking_it_and_it_comes_back_to_part_one(tmp_path, browser):
    """`questionnaire()`: every occasion, every anchor and every option list the page drew, in page
    order -- which is what `stranger_stories.plan`'s **global** matching needs, and what one screen
    at a time cannot give it any other way."""
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        parts = participant.questionnaire()
        assert [(p["part"], p["of"], p["title"]) for p in parts] == [
            (1, 3, "The last wake-up"), (2, 3, "The last app you paid for"),
            (3, 3, "The last time you asked somebody")]
        assert [[a["prompt"] for a in p["anchors"]] for p in parts] == [[_A1], [_A2], [_A3]]
        first = parts[0]["anchors"][0]
        assert first["selections"] == [_S1, _S2]
        assert first["taps"] == ["it hasn't happened to me", "it has, but I can't recall one"]
        # The option rows, as drawn: the escape and *other, say what* dropped, exactly as
        # `options_for` drops them on one screen.
        assert first["options"][_S1] == ["under 15 min", "15 to 60 min",
                                         "more than 2 hours, say roughly"]
        assert first["options"][_S2] == ["fed them", "walked them", "an app"]
        assert parts[1]["anchors"][0]["options"][_S1] == ["under 15 min", "15 to 60 min"]
        assert parts[2]["anchors"][0]["selections"] == []
        assert participant.part()["index"] == 1
        # Asked twice, walked once: the second call is the cache, and a second walk would press
        # Next over a page the first pass has already measured.
        assert participant.questionnaire() is parts
    finally:
        page.close()


def test_sections_are_the_parts_and_anchors_are_the_screen_showing(tmp_path, browser):
    """The two reads whose meaning 042 split. `sections()` is the whole interview (it walks);
    `anchors()` is the occasion on screen (it does not)."""
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        assert participant.sections() == ["The last wake-up", "The last app you paid for",
                                          "The last time you asked somebody"]
        assert [a["prompt"] for a in participant.anchors()] == [_A1], "one occasion, one screen"
        assert participant.offers(_A1) is True
        assert participant.offers(_A2) is False, "part two is not on this screen"
    finally:
        page.close()


def test_next_and_back_move_one_occasion_at_a_time(tmp_path, browser):
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        participant.begin()
        assert participant.next_part()["index"] == 2
        assert participant.primary_label() == INTERVIEW_NEXT
        assert participant.back()["index"] == 1
        assert participant.go_to_part(3)["index"] == 3
        assert participant.primary_label() == INTERVIEW_SEND, "the last part sends"
        assert participant.go_to_first_part()["index"] == 1
    finally:
        page.close()


def test_the_first_part_draws_no_back_and_the_last_part_has_no_next(tmp_path, browser):
    """Both companions in one: 042 draws Back from part 2 on, and the last part's primary sends.
    Asking for either where it does not exist is a mistake worth a sentence -- not a click on
    whatever button happens to be there."""
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        participant.begin()
        assert page.locator("main.iv-body .iv-actions button.btn.link").count() == 0
        with pytest.raises(AssertionError, match="the first one"):
            participant.back()
        participant.go_to_part(3)
        assert page.locator("main.iv-body .iv-actions button.btn.link").inner_text() == \
            INTERVIEW_BACK
        with pytest.raises(AssertionError, match="the last one"):
            participant.next_part()
    finally:
        page.close()


def test_the_one_nudge_is_pressed_through_and_only_once(tmp_path, browser):
    """The product's `BLANK_ANCHOR_NUDGE` fires on the first Next pressed with a blank story in
    that part, is global-once, and the second press proceeds. `p.iv-nudge` is where the pager draws
    it; it was the last `.iv .hint` on the scroll."""
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        participant.begin()
        assert participant.nudge() == "", "nothing is nudged before anything is pressed"
        assert participant.next_part()["index"] == 2
        assert participant.nudge() == "", "the nudge belongs to the part it fired on"
        # Spent: part two is just as blank, and no later Next is held.
        assert participant.next_part()["index"] == 3
    finally:
        page.close()


def test_a_story_and_a_pick_are_typed_on_the_screen_that_draws_them(tmp_path, browser):
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        participant.begin()
        participant.tell_story(_A1, "He woke at two and we were up till four.")
        participant.pick(_S1, ["15 to 60 min"], anchor_prompt=_A1)
        assert page.locator("main.iv-body textarea.box").first.input_value().startswith("He woke")
        assert page.locator("main.iv-body .opts .opt.on").first.inner_text() == "15 to 60 min"
        # And a prompt on another screen is not reachable from this one -- it is a sentence, not a
        # silent miss.
        with pytest.raises(AssertionError, match="no story box"):
            participant.tell_story(_A2, "wrong screen")
    finally:
        page.close()


# --------------------------------------------------------------- the send, and what answers it

def test_the_last_part_sends_and_the_completion_screen_answers_it(tmp_path, browser):
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        participant.begin()
        participant.tell_story(_A1, "He woke at two and we were up till four.")
        done = participant.submit()
        assert participant.screen() == "done"
        assert done["title"] == INTERVIEW_DONE_TITLE
        assert done["lead"] == ("Thanks, Yara Haddad. Your answers have gone to Eval Founder.")
        assert done["what_is_keel"].startswith("What is Keel?")
        assert participant.completion() == done
    finally:
        page.close()


def test_submit_walks_to_the_last_part_from_wherever_it_is_asked(tmp_path, browser):
    """`submit()` is the name every scenario calls, and 042 moved the send to the last part. Asked
    on the opening screen it presses Begin and walks; asked on the last part it finds nothing to
    walk."""
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        assert participant.screen() == "opening"
        assert participant.submit()["title"] == INTERVIEW_DONE_TITLE
    finally:
        page.close()


def test_a_send_that_never_lands_raises_rather_than_being_believed(tmp_path, browser):
    """The companion that keeps the walk honest: two presses that leave the last part on screen
    are a failure. 15 s of clock is spent on the second press on purpose -- a slow server is a
    thing a run should go red about, not a thing to shorten a timeout over."""
    participant, page = _participant(tmp_path, browser, interview_page.interview_html(
        _three_parts(), presses_to_send=99))
    try:
        participant.begin()
        participant.tell_story(_A1, "He woke at two.")
        participant.go_to_part(3)
        participant.tell_story(_A3, "I asked my sister.")
        with pytest.raises(AssertionError, match="neither moved the interview on nor said why"):
            participant.send()
    finally:
        page.close()


def test_the_hop_carries_every_screen_the_stranger_was_shown(tmp_path, browser):
    """`seen_text()`, and why it exists. `evals/corpus_facts.py` scores the Q5 **absences** against
    the `participant_page` hop -- no belief statement, no band value, no expected option anywhere a
    stranger can read -- and on a pager a capture of `body` is one occasion, not the questionnaire.
    """
    participant, page = _participant(tmp_path, browser,
                                     interview_page.interview_html(_three_parts()))
    try:
        participant.submit()
        seen = participant.seen_text()
        for words in (interview_page.CONSENT_LINE, _A1, _A2, _A3, _S1,
                      "more than 2 hours, say roughly", INTERVIEW_DONE_TITLE):
            assert words in seen, f"the hop lost {words!r}"
        assert "answers have gone to" in seen
    finally:
        page.close()
