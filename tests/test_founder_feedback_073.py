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
