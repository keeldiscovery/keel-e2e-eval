"""Spec 073 (the harness follows keel-web 113 and 114, the founder's staging review of 2026-10-26).

FR-1: the context step's four states (keel-web 113 FR-1) -- the tracker the walk installs before Save, read against
keel-web's own markup in a real page, and the faults the leg names when a state is not what it should be.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens

SENTENCE = "You want to hear from restaurant managers about the delivery that did not match the invoice."


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


_FORM = """<div class="ccard__body"><h1 class="ccard__title">Who it's for</h1><div class="cfields">
  <div class="cfield"><textarea id="context-actor" class="cfield__input"></textarea></div>
  <div class="cfield"><textarea id="context-job" class="cfield__input"></textarea></div>
  <div class="cfield"><textarea id="context-circumstance" class="cfield__input"></textarea></div>
  <div class="cfield"><textarea id="context-segment" class="cfield__input"></textarea></div></div></div>
  <div class="cbtns ccard__foot pact"><button class="btn primary" data-testid="context-save">Save and continue</button></div>"""
_WAIT = """<div class="ccard__body"><h1 class="ccard__title">Who it's for</h1><div class="waitco-block">
  <p class="cnote" role="status">Keel is reading your four answers.</p>
  <div class="waitco"><span class="waitco__elapsed">0:01</span><div class="phasebar"></div><div class="truth"></div></div>
  </div></div>"""
_CARD = f"""<div class="ccard__body"><h1 class="ccard__title">Who it's for</h1><div class="understands">
  <p class="understands__kicker">Keel understands</p><p class="understands__big">{SENTENCE}</p>
  <div class="actions cbtns"><button class="btn primary">Yes, that's it</button><button class="btn">Edit</button></div>
  </div></div>"""


def _walk(browser, steps: list[tuple[str, str]]) -> list[dict]:
    """keel-web 113's step drawn as `steps` [(state, inner html)], the tracker installed on the first, each next state
    committed as React would (the attribute and the children in one change), then read back."""
    page = browser.new_page()
    try:
        state, html = steps[0]
        page.set_content(f'<div data-testid="context-step" data-context-state="{state}">{html}</div>')
        page.evaluate(vs_screens._CONTEXT_STATES_JS)
        for state, html in steps[1:]:
            page.evaluate("""([state, html]) => { const r = document.querySelector('[data-testid=context-step]');
                             r.setAttribute('data-context-state', state); r.innerHTML = html; }""", [state, html])
            page.wait_for_timeout(20)
        return page.evaluate(vs_screens._CONTEXT_STATES_READ_JS)
    finally:
        page.close()


def test_the_tracker_reads_form_wait_and_card_off_keel_webs_markup(browser):
    states = _walk(browser, [("form", _FORM), ("wait", _WAIT), ("card", _CARD)])
    assert [s["state"] for s in states] == ["form", "wait", "card"]
    form, wait, card = states
    assert form["boxes"] == 4 and form["save"] == 1
    assert wait == {"state": "wait", "status": vs_screens.CONTEXT_READING, "elapsed": True, "phasebar": True,
                    "truth": True, "fields": 0, "save": 0}
    assert card == {"state": "card", "big": SENTENCE, "yes": vs_screens.CONTEXT_YES, "edit": vs_screens.CONTEXT_EDIT,
                    "boxes": 0}
    assert cs.context_states_faults(states, SENTENCE) == []


def test_a_wait_whose_company_mounts_late_is_merged_over_its_stay(browser):
    bare = """<div class="ccard__body"><div class="waitco-block"><p class="cnote" role="status">Keel is reading your
      four answers.</p><div class="waitco"></div></div></div>"""
    states = _walk(browser, [("form", _FORM), ("wait", bare), ("wait", _WAIT), ("card", _CARD)])
    assert [s["state"] for s in states] == ["form", "wait", "card"]
    assert states[1]["elapsed"] and states[1]["phasebar"] and states[1]["truth"]
    assert cs.context_states_faults(states, SENTENCE) == []


def test_a_form_drawn_again_between_the_wait_and_the_card_is_named(browser):
    states = _walk(browser, [("form", _FORM), ("wait", _WAIT), ("form", _FORM), ("wait", _WAIT), ("card", _CARD)])
    faults = cs.context_states_faults(states, SENTENCE)
    assert faults and faults[0]["states"] == ["form", "wait", "form", "wait", "card"]


def _good() -> list[dict]:
    return [{"state": "form", "boxes": 4, "save": 1},
            {"state": "wait", "status": vs_screens.CONTEXT_READING, "elapsed": True, "phasebar": True, "truth": True,
             "fields": 0, "save": 0},
            {"state": "card", "big": SENTENCE, "yes": vs_screens.CONTEXT_YES, "edit": vs_screens.CONTEXT_EDIT,
             "boxes": 0}]


@pytest.mark.parametrize("fault", [
    lambda s: s.pop(1),                                           # no wait seen: the card came straight after Save
    lambda s: s[1].update(truth=False),                           # the wait without its truth card
    lambda s: s[1].update(elapsed=False),                         # ... without its counter
    lambda s: s[1].update(fields=4),                              # the fields still drawn under the wait
    lambda s: s[1].update(save=1),                                # Save still drawn
    lambda s: s[1].update(status="Reading..."),                   # another line
    lambda s: s[2].update(boxes=4),                               # the four boxes drawn under the card
    lambda s: s[2].update(edit="Not quite"),                      # the card's second button is not Edit
    lambda s: s[2].update(big="Another sentence."),               # the card's sentence is not the one returned
    lambda s: s[0].update(save=0),                                # a form with no Save
    lambda s: s.append({"state": "confirmed"}),                   # a state after the card
])
def test_each_state_not_as_keel_web_113_draws_it_is_a_fault(fault):
    states = _good()
    assert cs.context_states_faults(states, SENTENCE) == []
    fault(states)
    assert cs.context_states_faults(states, SENTENCE)


def test_the_four_states_and_the_selectors_are_keel_webs():
    assert vs_screens.CONTEXT_STATES == ("form", "wait", "card", "confirmed")
    assert vs_screens.CONTEXT_STEP == "[data-testid=context-step]"
    assert (vs_screens.CONTEXT_READING, vs_screens.CONTEXT_CONTINUE, vs_screens.CONTEXT_EDIT) == (
        "Keel is reading your four answers.", "Continue to the problem", "Edit")


def test_s005_alone_reopens_the_confirmed_context():
    import inspect

    from evals import test_s005_countly, test_s006_paidly, test_s007_mulchrun
    assert "context_edit=True" in inspect.getsource(test_s005_countly)
    assert "context_edit" not in inspect.getsource(test_s006_paidly)
    assert "context_edit" not in inspect.getsource(test_s007_mulchrun)
    assert inspect.signature(cs.run).parameters["context_edit"].default is False


# ------------------------------------------------------------------- FR-2: *A word from you* is not walked

from types import SimpleNamespace                                             # noqa: E402

from evals import scope_marks as sm                                           # noqa: E402


@pytest.mark.parametrize("scope, want", [("ALL", ["1 of 2", "2 of 2"]), ("COMMERCIAL", ["1 of 2", "2 of 2"]),
                                         ("SOLUTION", ["1 of 2", "2 of 2"]), ("PROBLEM", [])])
def test_step_5_counts_two_screens_and_none_in_the_problem_study(scope, want):
    assert cs.before_counters(scope) == want


class _Step:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def record_assert(self, want, got):
        pass


@pytest.fixture
def steps(monkeypatch):
    monkeypatch.setattr(cs, "_step", lambda *a, **k: _Step())


def _ready(screen: str, **over) -> dict:
    url = f"http://localhost:5173/p/p1/define/ready/{screen}"
    return {"ready": {"landed": url, "word_redirect": url, "word_drawn": 0, **over}}


@pytest.mark.parametrize("scope, screen", [("ALL", "pilot"), ("COMMERCIAL", "pilot"), ("PROBLEM", "interviewer")])
def test_the_last_step_starts_on_its_first_screen_and_the_word_redirects_there(steps, scope, screen):
    cs._hold_no_word(SimpleNamespace(scope=scope), _ready(screen))


@pytest.mark.parametrize("scope, drawn", [
    ("ALL", _ready("word")),                                                          # the word drawn first
    ("ALL", _ready("pilot", word_redirect="http://localhost:5173/p/p1/define/ready/word")),  # the address answered
    ("ALL", _ready("pilot", word_drawn=1)),                                           # *A word from you* on a screen
    ("PROBLEM", _ready("pilot")),                                                     # a pilot in the problem study
    ("ALL", {}),                                                                      # nothing read
])
def test_a_word_screen_still_walked_fails(steps, scope, drawn):
    with pytest.raises(AssertionError):
        cs._hold_no_word(SimpleNamespace(scope=scope), drawn)


THANKS = "Thank you -- your answers have gone to Maya."


def _done(**over) -> tuple[dict, dict]:
    interview = {"done": {"thanks": THANKS, "word": None, "pilot": {"label": "Count me in for the pilot"}}}
    walked = {"done": THANKS, "word_drawn": 0, "done_screen": True}
    for k, v in over.items():
        (interview["done"] if k in ("thanks", "word") else walked)[k] = v
    return interview, walked


def test_the_thank_you_is_the_default_words_as_served():
    assert cs.thanks_faults(*_done()) == []
    assert cs.thanks_faults(*_done(thanks="Thank you -- your answers have gone to The founder.",
                                   done="Thank you -- your answers have gone to The founder.")) == []


@pytest.mark.parametrize("over", [
    {"word": {"founderFirstName": "Maya", "pitch": "I started this.", "attribution": "Maya wrote this."}},
    {"word_drawn": 1},                                                                # a word section drawn
    {"done": "That's it."},                                                           # drawn other than served
    {"thanks": "Thanks!", "done": "Thanks!"},                                         # not the default words
])
def test_a_thank_you_with_a_word_or_other_words_is_named(over):
    assert cs.thanks_faults(*_done(**over))


def test_the_exit_screen_owes_no_thank_you():
    assert cs.thanks_faults(*_done(done_screen=False, done="Thanks for your time")) == []


def test_sc2_v2_counts_the_two_screens():
    assert sm.SCOPE_MARKS_VERSION == 2
    assert "_founders_word" not in vars(__import__("evals.interviewer_leg", fromlist=["x"]))
    assert not hasattr(__import__("evals.interviewer_leg", fromlist=["x"]), "FOUNDERS_WORD")


# ------------------------------------------------------------------- FR-5: the player's crop, its classes alone

from harness import interviewer_screens as ivs                                  # noqa: E402
from harness.steps import Recorder                                             # noqa: E402

#: Spec 083: the band stays LIVIA -- keel-web 125 keeps 087's picture band for the retired four only (a recording that
#: carries one); the two studio faces draw their 9:16 render with no band, as `_PLAIN` reads.
_BAND = """<div data-testid="ai-stage" data-phase="speaking"><div data-testid="ai-face" data-band="LIVIA"
  class="aiv-stage__face aiv-stage__face--band"><div class="aiv-band"><div data-testid="ai-band-blur"></div>
  <div data-testid="ai-band" class="aiv-band__picture"><video class="aiv-stage__video aiv-band__video"
  data-clip="c1"></video></div></div></div></div>"""
_PLAIN = """<div data-testid="ai-stage" data-phase="speaking"><div data-testid="ai-face" class="aiv-stage__face">
  <video class="aiv-stage__video" data-clip="c1"></video></div></div>"""


@pytest.mark.parametrize("html, want", [
    (_BAND, {"band": "LIVIA", "classed": True, "band_video": 1, "blur": 1}),
    (_PLAIN, {"band": None, "classed": False, "band_video": 0, "blur": 0}),            # a face not in the table
])
def test_the_crop_is_read_by_the_pages_own_classes(tmp_path, browser, html, want):
    page = browser.new_page()
    try:
        page.set_content(html)
        player = ivs.Player(page, Recorder(tmp_path))
        assert player.band() == want
        stage = player.stage()
        assert stage["videos"] == 1 and stage["clip"] == "c1" and stage["band"] == want   # the one video, either way
    finally:
        page.close()


def test_the_crop_is_recorded_never_scored():
    from evals import interviewer_marks
    assert all(key != "ai_band" for _, key, _ in interviewer_marks.MARKS)


def test_the_cards_words_are_the_settled_ones(browser):
    """S-015's first run (2026-10-26): the card's first render reads *Save and continue* until its occasion field is
    pre-filled by an effect, then *Yes, that's it* -- the state's words are the last it drew."""
    early = _CARD.replace("Yes, that's it", "Save and continue")
    states = _walk(browser, [("form", _FORM), ("wait", _WAIT), ("card", early), ("card", _CARD)])
    assert states[-1]["yes"] == vs_screens.CONTEXT_YES
    assert cs.context_states_faults(states, SENTENCE) == []
