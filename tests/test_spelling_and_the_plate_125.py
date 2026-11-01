"""Spec 125 -- the referee follows keel-cloud 195 and keel-web 160 / 161 (keel-cloud-docs `2d848360`, keel-web `2b84758`).

FR-1 spelling corrected, words kept: `instructions/spelling.py` ports `Spelling.sameWord` / `inText` / `runIn` (the
first-letter guard included), and `no_leak`'s vocabulary subtracts the founder's typed words through it (beside it,
`CommercialChain.sameWords` and `Qualifiers.sameQualifier`, which 195 routed too). FR-2 the condition heard before it is
answered (keel-web 160): the AI walk waits for `clips.condition`, the decision-maker's AI link asks its screener, the
heading counts the condition. FR-3 the brand plate (keel-web 161): the plate read and held; the stranger's line read
whole around `idea-mark`. No mark number moves.
"""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import interviewer_leg as il
from harness import qualifiers as q
from harness import vectors_screens as vs_screens
from instructions import chain as chain_mod
from instructions import corpus as corpus_mod
from instructions import marks as marks_mod
from instructions import spelling as sp
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
SPELLING = "src/main/java/com/keeldiscovery/cloud/domain/vectors/Spelling.java"


def _cloud(path: str) -> str:
    full = KEEL_CLOUD / path
    if not full.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    return full.read_text(encoding="utf-8")


# --------------------------------------------------------------------------------------------- FR-1: the port

def test_the_founders_examples_read_as_one_word():
    assert sp.same_word("withot", "without") and sp.same_word("erros", "errors")
    assert sp.same_word("recieve", "receive") and sp.distance("recieve", "receive") == 1, "an adjacent swap is one"
    assert sp.same_word("Payroll", "payroll") and sp.same_word("PAYROL", "payroll")
    assert not sp.same_word("errors", "mistakes"), "a different word is a different word"
    assert not sp.same_word(None, "x") and not sp.same_word("", "") and not sp.same_word("  ", "a")


def test_the_thresholds_and_digits():
    assert not sp.same_word("cat", "cot") and sp.same_word("cat", "CAT"), "under four letters: exact only"
    assert sp.same_word("form", "fork") and not sp.same_word("form", "fame"), "four letters: one edit"
    assert sp.same_word("ledger", "ledgre") and sp.same_word("payroll", "payrool")
    assert not sp.same_word("errors", "eros"), "the shorter word's allowance: four letters, one edit"
    assert not sp.same_word("payroll", "pyrlo"), "three edits refused"
    assert not sp.same_word("250000", "250,000") and not sp.same_word("12th", "13th") and sp.same_word("4x4", "4X4")
    assert [sp.allowed(n) for n in (3, 4, 5, 9)] == [0, 1, 2, 2]


@pytest.mark.parametrize("a, b", [("apps", "maps"), ("device", "advice"), ("night", "light"), ("four", "your")])
def test_the_first_letter_guard_keeps_dictionary_neighbours_apart(a, b):
    """keel-cloud 195 *Not foreseen*: the first letter the same, beyond the spec's letter."""
    assert not sp.same_word(a, b)


def test_in_text_and_run_in():
    assert sp.in_text("withot", "run payroll without errors") and not sp.in_text("withot", "run payroll fast")
    assert sp.run_in("evry evening", "at about 6 every evening") and not sp.run_in("evry morning", "every evening")
    assert not sp.run_in("", "anything") and not sp.run_in("a b c", "a b")
    assert sp.words("Don't  stop -- the payroll’s run!") == ["don't", "stop", "the", "payroll's", "run"]


def test_the_port_is_spellings_own():
    text = _cloud(SPELLING)
    assert "x.charAt(0) == y.charAt(0)" in text, "the first-letter guard"
    assert "return length < 4 ? 0 : length == 4 ? 1 : 2;" in text
    assert "hasDigit(x) || hasDigit(y)" in text
    assert "a.charAt(i - 1) == b.charAt(j - 2) && a.charAt(i - 2) == b.charAt(j - 1)" in text, "OSA's swap"


# ------------------------------------------------------------------------------- FR-1: no_leak's vocabulary

@pytest.fixture(scope="module")
def corpus():
    return corpus_mod.load(KEEL_CLOUD)


def _entry(corpus, job, mechanism):
    base = corpus.entries[0]
    return replace(base, context={**(base.context or {}), "job": job},
                   solution_mechanism={**(base.solution_mechanism or {}), "mechanism": mechanism, "output": "",
                                       "not_assumed": [], "mechanism_terms": []})


def test_the_vocabulary_subtracts_the_founders_typed_words_spelt_right(corpus):
    """keel-cloud 195 FR-2 (`LeakStems.vocabulary`'s four-argument form): the typed *erros* is the problem's *errors*."""
    typed = _entry(corpus, "run payroll withot erros", "flags errors before the payroll run closes")
    assert "error" not in typed.vocabulary()
    other = _entry(corpus, "run payroll without mistakes", "flags errors before the payroll run closes")
    assert "error" in other.vocabulary(), "a different word subtracts nothing"
    assert typed.typed_problem_texts()[:4] == [str(typed.context[k]) for k in corpus_mod.FOUNDER_CONTEXT_FIELDS
                                               if typed.context.get(k)]


def test_no_mark_number_moves():
    assert marks_mod.MARKS_VERSION == 24


# ---------------------------------------------------------------------- FR-1: the other two 195 routed

def test_the_loss_line_typed_misspelt_is_the_base():
    assert chain_mod._same_words("late shipmnts", "the late shipments")
    assert not chain_mod._same_words("late errors", "late mistakes")
    assert not chain_mod._same_words("late shipmnts here", "late shipments")


def test_the_founders_qualifier_is_kept_spelt_right_and_the_cores_parts_stay_exact():
    assert q.dropped("withot a payrol buerau", "without a payroll bureau") != []
    assert q.dropped_as_spelt("withot a payrol buerau", "without a payroll bureau") == []
    assert q.dropped_as_spelt("withot a payroll bureau", "with a payroll bureau") == ["withot"], \
        "with is a different word (under four letters, exact)"
    text = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/Qualifiers.java")
    assert "sameQualifier(condition, part, false)" in text, "inCore reads the core exactly"


# ------------------------------------------------------------------------- FR-2: the condition heard first

class _Page:
    def __init__(self, step=None, starts=()):
        self.step, self.starts = step, list(starts)

    def get_by_test_id(self, _testid):
        step = self.step
        return SimpleNamespace(count=lambda: 1 if step else 0,
                               first=SimpleNamespace(get_attribute=lambda _name: step))

    def evaluate(self, _script):
        return {"starts": self.starts, "stops": [], "cancels": [], "sound_at": None, "released": []}


class _Player:
    patience = 1.0

    def __init__(self, events, step="condition", starts=()):
        self.page, self.events = _Page(step, starts), events

    def timeline(self):
        return self.events

    def stage(self):
        return {"clip": None}


def test_the_walk_waits_for_the_condition_clip_then_the_window():
    player = _Player([{"kind": "play", "clip": "c-1", "t": 1200.0}], starts=[1500.0])
    seen = il.wait_condition_clip(player, "c-1", timeout_s=1)
    assert seen == {"step": "condition", "clip": "c-1", "played": True, "at": 1200.0}
    # a lock from before keel-cloud 194: no clip served, nothing waited for, the page asks it as text
    assert il.wait_condition_clip(_Player([]), None) == {"step": "condition", "clip": None, "played": False,
                                                         "at": None}
    with pytest.raises(AssertionError, match="the condition's clip never played"):
        il.wait_condition_clip(_Player([]), "c-1", timeout_s=0.2)


def test_the_deciders_ai_link_asks_its_screener_and_the_heading_counts_it():
    decider = {"kind": "COMMERCIAL_LINK", "condition": {"question": "Does your team call patients?", "inCodes": ["YES"]},
               "parts": [{"part": 3, "items": [{"itemId": "a"}, {"itemId": "b"}, {"itemId": "c"}]}],
               "interviewer": {"clips": {"condition": {"clipId": "c-9"}}}}
    walk = il._Walk(None, decider, {})
    assert walk.screener == decider["condition"] and walk.condition_clip == "c-9"
    assert il.ai_question_count(decider) == 4
    full = {"kind": "FULL", "gate": {"itemId": "g", "condition": {"question": "Do you run payroll?"}},
            "parts": [{"part": 1, "items": [{"itemId": i} for i in "abc"]}, {"part": 2, "items": [{"itemId": "d"}]}]}
    assert il.ai_question_count(full) == 6, "the condition, the gate and every item (Question 1 of 6 the condition)"
    assert il.ai_question_count({**full, "gate": {"itemId": "g"}}) == 5
    assert il._Walk(None, {**decider, "condition": None}, {}).screener == {}


# ------------------------------------------------------------------------------- FR-3: the brand plate

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


_PLATE = """<main><div class="brandplate" data-testid="brand-plate"><p class="brandplate__k">How strangers meet it</p>
<p class="brandplate__mark" data-testid="brand-plate-mark">Titam  Pay</p>
<p class="brandplate__line" data-testid="brand-plate-line">Imagine <b>Titam Pay</b>, a payroll anomaly detection
 tool.</p></div><input id="idea-what" value="Titam Pay"></main>"""
_CARD = """<div class="iv-ideacard"><p class="iv-ideacard__what"><b class="iv-mark" data-testid="idea-mark">Imagine</b>
</p></div>""".replace('<b class="iv-mark" data-testid="idea-mark">Imagine</b>',
                      'Imagine <b class="iv-mark" data-testid="idea-mark">Titam</b>, a payroll anomaly detection tool.')


def test_the_plate_is_read_and_held(browser):
    page = browser.new_page()
    try:
        page.set_content("<main><input id='idea-what' value=''></main>")
        before = vs_screens.Corridor.brand_plate(SimpleNamespace(page=page))
        page.set_content(_PLATE)
        named = vs_screens.Corridor.brand_plate(SimpleNamespace(page=page))
    finally:
        page.close()
    assert before == {"drawn": False}
    assert named == {"drawn": True, "mark": "Titam Pay",
                     "line": "Imagine Titam Pay, a payroll anomaly detection tool.", "focusable": 0}
    plate = {"before": before, "named": named}
    assert vs_screens.brand_plate_faults(plate, "Titam Pay", "A payroll anomaly detection tool.") == []
    assert vs_screens.brand_plate_faults(plate, "Titam", "A payroll anomaly detection tool.")
    assert vs_screens.brand_plate_faults({"before": named, "named": named}, "Titam Pay", "a payroll anomaly "
                                         "detection tool")[0] == {"plate before the name": named}
    assert vs_screens.brand_plate_faults({"before": before, "named": before}, "Titam Pay", None) == \
        [{"no plate once named": before}]
    assert vs_screens.brand_plate_faults({"before": before, "named": {**named, "focusable": 1}}, "Titam Pay",
                                         "a payroll anomaly detection tool") == [{"focusable in the plate": 1}]


def test_the_strangers_line_is_read_whole_around_its_mark(browser):
    page = browser.new_page()
    try:
        page.set_content(_CARD)
        line = vs_screens._line_text(page, ".iv-ideacard__what")
        mark = vs_screens.idea_mark(page)
        text_node = page.evaluate("() => document.querySelector('.iv-ideacard__what').firstChild.textContent")
        page.set_content("<div class='iv-ideacard'><p class='iv-ideacard__what'>Imagine Fresco.</p></div>")
        bare = (vs_screens._line_text(page, ".iv-ideacard__what"), vs_screens.idea_mark(page))
    finally:
        page.close()
    assert line == "Imagine Titam, a payroll anomaly detection tool." and mark == "Titam"
    assert text_node.strip() == "Imagine", "one text node is never the line"
    assert bare == ("Imagine Fresco.", None), "a bare *Imagine Fresco.* carries no mark"
    assert re.search(r'"idea_card": _line_text\(page, "\.iv-ideacard__what"\)',
                     Path(vs_screens.__file__).read_text(encoding="utf-8"))
