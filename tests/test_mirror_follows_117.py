"""Spec 117 -- the harness's mirrors follow keel-cloud 178/179 and keel-web 152/153/154 (all merged 2026-10-31).

FR-1 (keel-cloud 179): the brief's Purchase friction bar, line and words in the question's tense (pinned in
`test_instruction_brief_facts.py`; here the bar agrees with the page's Choose bar, and the recorded S-006 read, in the old
words, still exports); Compatibility's served Choose title. FR-2 (keel-cloud 178): the answers view's NOTHING word.
FR-3 (keel-web 153): the hints, titles, intro, bars, the box's kept line and the range hint, read by the page objects in
Chromium against stand-ins and held by `corpus_scenario.said_faults`. FR-4 (keel-web 152 / 154): the story sheet's two
chips and the spoken refusal; the after-answers leg reads the stage page by 154's ids, its classes as the fallback.
"""

from __future__ import annotations

import inspect
import json
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from evals import interviewer_leg as il
from harness import interviewer_fake as fake
from harness import interviewer_screens as ivs
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.steps import Recorder
from instructions import brief_facts as bf

BASE = "http://keel.test"
FRICTION = "commercial.purchase_friction"
COMPAT = "solution.compatibility"
ADOPTION = "solution.adoption_friction"
WANT_TITLE = "Which one do you want to test?"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


# ----------------------------------------------------------------------------------- FR-1: keel-cloud 179's tense

def test_the_briefs_bar_is_the_choose_bar_in_the_briefs_shape():
    """keel-cloud 179 T005: the brief's `keelBar` is the page's Choose bar (keel-web 153) lower-cased and unstopped, as
    it is drawn after *Keel's bar: *. So the founder reads one bar on the Choose screen and on the brief."""
    choose = vs_screens.PURCHASE_FRICTION_CHOOSE_BAR
    assert bf.KEEL_BAR[FRICTION] == choose[0].lower() + choose[1:-1]


@pytest.mark.parametrize("counts, want", [
    ("yes_long=5, yes_quick=1, not_needed=1", "Yes, switching suppliers would slow it. Plan for it."),
    ("yes_long=1, yes_quick=3, not_needed=3", "Your fear was switching suppliers. 6 of 7 said it would be quick or not "
                                              "needed. Not the blocker you expected."),
    ("yes_long=3, yes_quick=2, not_needed=2", "Did not hold")])
def test_the_friction_words_are_179s_and_a_split_keeps_its_words(counts, want):
    standing = {"status": "HOLDING_UP", "n": 7, "optionCounts": counts}
    assert bf.friction_words(FRICTION, standing, "Switching suppliers", "Did not hold") == want


def test_the_recorded_s006_read_is_the_old_tense_and_still_exports(tmp_path):
    """`tests/fixtures/sample/s006-reads.json` is a recorded read (05-paidly on a build before keel-cloud 118 and 179):
    its Purchase friction drift clause and status line say *was quick*. It is never hand-edited -- it is re-recorded
    (`make sample`, the coordinator's). Until then the export takes it as it is: `sample_export` passes the served words
    through and holds none of the friction words to a mirror, so either tense exports (the same read re-tensed as 179
    serves it, too)."""
    from evals import sample_export as se                                 # noqa: PLC0415
    from tests import test_sample_export as t                             # noqa: PLC0415
    try:
        entry = vs.entry_for(t.KEEL_CLOUD, "05-paidly")[1]
    except Exception as missing:  # noqa: BLE001
        pytest.skip(f"the corpus is not readable here: {missing}")
    reads = t._seeded()
    rows = [d for v in reads["standings"]["vectors"] for d in v["dimensions"] if d["dimension"] == FRICTION]
    assert rows and "said it was quick or not needed" in rows[0]["statusLine"], "re-recorded: drop this tolerance"
    old = se.export_sample(t._journey(tmp_path / "old", reads, entry), tmp_path / "old" / "out")
    for row in rows:
        for field in ("statusLine", "driftClause"):
            row[field] = row[field].replace("said it was quick", "said it would be quick")
    new = se.export_sample(t._journey(tmp_path / "new", reads, entry), tmp_path / "new" / "out")
    assert old["people"] == new["people"] == 20


# ------------------------------------------------------------------------------- FR-2: keel-cloud 178's None

def test_the_answers_view_says_none_as_the_chip_does():
    assert vs.ANSWERS_VIEW_NOTHING == "None" == vs.VALUE_BOX_LABELS["NOTHING"]
    source = " ".join(inspect.getsource(vs).replace("#: ", " ").split())
    assert "The labels were *Nothing* and *I don't know* until keel-cloud 170" in source, \
        "the 170 note stays (keel-cloud 178's tasks.md)"


# ------------------------------------------------------- FR-1 / FR-3: the Choose screens of 153, read in Chromium

#: keel-web 153's Choose screen, as far as the walker reads it: the intro (`.corridor__intro`), the title
#: (`.listcheck__title`), the radiogroup, the *Keel will test* box (`.keeltest__t`, `.keeltest__b`, and on
#: Compatibility `p.keeltest__n[data-testid=keeltest-note]` before and after a pick) and Continue (the PUT).
_CHOOSE = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const O = %(opts)s;
let pick = null;
const pid = location.pathname.split('/')[2];
function render() {
  const app = document.getElementById('app');
  if (/\\/next$/.test(location.pathname)) { app.innerHTML = '<main><h1>Next</h1></main>'; return; }
  const radios = O.rows.map((r, i) => `<button type="button" role="radio" aria-checked="${pick === i}" data-i="${i}">${r}</button>`).join('');
  app.innerHTML = `<main class="corridor"><p class="corridor__intro">${O.intro}</p><section class="ccard"><div class="ccard__body">
    <div class="listcheck"><p class="listcheck__title" id="t">${O.title}</p>
    <div role="radiogroup" aria-labelledby="t">${radios}</div></div>
    <div class="keeltest"><p class="keeltest__t">${pick === null ? 'Pick one and the test appears here.' : O.rows[pick] + ' can slow or stop the purchase.'}</p>
      <p class="keeltest__b">${O.bar}</p>${O.note ? `<p class="keeltest__n" data-testid="keeltest-note">${O.note}</p>` : ''}</div></div>
    <div class="ccard__foot"><button type="button" class="btn primary" ${pick === null ? 'disabled' : ''}>Continue</button></div>
    </section></main>`;
  app.querySelectorAll('[role=radio]').forEach((b) => b.addEventListener('click', () => { pick = Number(b.dataset.i); render(); }));
  app.querySelector('.btn.primary').addEventListener('click', async () => {
    const r = await fetch(`/v2/projects/${pid}/calibration/${O.vector}`, {method: 'PUT',
      headers: {'content-type': 'application/json'}, body: JSON.stringify({answers: [
        {dimension: O.dim, list: {items: O.rows.map((label) => ({label})), pickedIndex: pick}}]})});
    await r.json(); history.pushState({}, '', `/p/${pid}/next`); render();
  });
}
render();
</script></body></html>"""

ROWS = ["The office manager's sign-off", "Switching suppliers"]
SCREENS = {
    FRICTION: {"vector": "COMMERCIAL", "intro": vs_screens.PURCHASE_FRICTION_CHOOSE_INTRO, "title": WANT_TITLE,
               "bar": vs_screens.PURCHASE_FRICTION_CHOOSE_BAR, "note": ""},
    COMPAT: {"vector": "SOLUTION", "intro": "Strangers get one question for this test. Pick the condition most likely "
                                            "to stop them; nothing is reworded here.", "title": WANT_TITLE,
             "bar": "Holds if no more than 1 in 3 say only with help or approval, or no.",
             "note": vs_screens.COMPATIBILITY_KEPT_NOTE},
    ADOPTION: {"vector": "SOLUTION", "intro": "Strangers get one question for this test.",
               "title": "Which one is most likely to stop them?",
               "bar": "Holds if no more than 1 in 3 say probably not or no.", "note": ""},
}
#: The same screens with the words before 153 / 179.
OLD = {
    FRICTION: {"intro": "The person who decides gets one question for this test, about the last thing they paid for. "
                        "Pick the one step; nothing is reworded here.",
               "title": "Which one is most likely to slow it down?",
               "bar": "Holds if at least 2 in 3 say it was needed last time and took a long time."},
    COMPAT: {"title": "Which of these is most likely to be missing?", "note": ""},
}


def _choose(browser, tmp_path, key, **opts):
    page = browser.new_page()
    screen = {**SCREENS[key], "rows": ROWS, "dim": key, **opts}

    def serve(route):
        if route.request.method == "PUT":
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"revision": 2}))
        else:
            route.fulfill(status=200, content_type="text/html", body=_CHOOSE % {"opts": json.dumps(screen)})
    page.route(f"{BASE}/**", serve)
    page.goto(f"{BASE}/p/p1/define/x/q/3/choose", wait_until="load")
    try:
        corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
        corridor.camera = lambda slug: None
        return corridor.list_choose({"dimension": key}, ROWS[1])
    finally:
        page.close()


@pytest.mark.parametrize("key", [FRICTION, COMPAT, ADOPTION])
def test_the_choose_screen_reads_its_intro_title_bar_and_kept_line(browser, tmp_path, key):
    seen = _choose(browser, tmp_path, key)
    assert seen["intro"] == SCREENS[key]["intro"] and seen["prompt"] == SCREENS[key]["title"]
    assert seen["test_before"]["bar"] == seen["test"]["bar"] == SCREENS[key]["bar"]
    assert seen["note_before"] == seen["note"] == SCREENS[key]["note"]
    assert seen["test_before"]["belief"] == cs.KEEL_TEST_PENDING, "_keel_test unchanged: the note is not the belief"
    assert cs.said_faults(seen, key, b2b=True) == []
    assert cs.choose_faults(seen, key, row=1) == []


def test_the_choose_words_before_153_and_179_are_faults(browser, tmp_path):
    friction = _choose(browser, tmp_path, FRICTION, **OLD[FRICTION])
    assert [f["what"] for f in cs.said_faults(friction, FRICTION, b2b=True)] == [
        "the Choose title", "the Choose intro", "the bar before a pick", "the bar after the pick"]
    compat = _choose(browser, tmp_path, COMPAT, **OLD[COMPAT])
    assert [f["what"] for f in cs.said_faults(compat, COMPAT, b2b=False)] == [
        "the Choose title", "the box's line before a pick", "the box's line after the pick"]
    stray = _choose(browser, tmp_path, FRICTION, note=vs_screens.COMPATIBILITY_KEPT_NOTE)
    assert [f["what"] for f in cs.said_faults(stray, FRICTION, b2b=True)] == [
        "the box's line before a pick", "the box's line after the pick"], "the kept line is Compatibility's alone"


# ------------------------------------------------------------------- FR-3: the Answer hints and Commitment's bar

COMPAT_HINT = ("What must already be true at first-time parents in the US with a baby under six months for this to "
               "work? Tools they use, time they can wait, rules they work under. Two to four things. Up to 25 words.")


@pytest.mark.parametrize("key, hint, faults", [
    ("problem.importance", vs_screens.IMPORTANCE_ANSWER_HINT, []),
    ("problem.importance", "Name the other difficulties of the same moment. Up to 25 words.", ["the Answer hint"]),
    (COMPAT, COMPAT_HINT, []),
    (COMPAT, COMPAT_HINT.replace(" at first-time parents in the US with a baby under six months", ""), []),
    (COMPAT, "What they already have or do that it plugs into. Up to 25 words.", ["the Answer hint"]),
    (ADOPTION, "Anything at all.", [])])
def test_the_answer_hints_are_153s(key, hint, faults):
    seen = {"screen": "answer", "hint": hint}
    assert [f["what"] for f in cs.said_faults(seen, key, b2b=False)] == faults


BAR_B2B = "Set by Keel. Holds if no more than 1 in 3 partners who pay the household bills say probably not or no."
BAR_THEM = "Set by Keel. Holds if no more than 1 in 3 of them say probably not or no."


@pytest.mark.parametrize("bar, b2b, faults", [
    (BAR_B2B, True, []), (BAR_THEM, True, []), (vs_screens.COMMITMENT_BAR, False, []),
    (vs_screens.COMMITMENT_BAR, True, ["the Commitment bar"]), (BAR_B2B, False, ["the Commitment bar"])])
def test_commitments_bar_names_the_deciders_on_a_b2b_study(bar, b2b, faults):
    seen = {"screen": "check", "test": {"belief": "x", "bar": bar, "shown": True}}
    assert [f["what"] for f in cs.said_faults(seen, "commercial.commitment", b2b=b2b)] == faults
    assert vs_screens.commitment_bar(BAR_B2B) == {"case": "decider",
                                                  "deciders": "partners who pay the household bills"}
    assert vs_screens.commitment_bar(BAR_THEM)["deciders"] == "of them"
    assert vs_screens.commitment_bar("Holds if no more than 1 in 3 say probably not or no.") is None


def test_importance_count_free_box_is_read_as_what_it_is():
    """keel-web 153 FR-4: the box before the list exists reads 174's second sentence alone; the walk reads it once the
    list holds more, so `importance_count` gives it back whole (the hold names what it saw)."""
    free = "Knowing what the cry means is one of the two they would most like made easier."
    assert vs_screens.importance_count_free(free) == "Knowing what the cry means"
    assert cs.importance_count(free) == free
    counted = "Parents of babies under six months have five things that are hard in a night with the baby. " + free
    assert vs_screens.importance_count_free(counted) is None
    assert cs.importance_count(counted) == "have five things that are hard"


# ------------------------------------------------------------------------- FR-3: Frequency's range hint, read

_FREQUENCY = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const O = %(opts)s;
function render() {
  const app = document.getElementById('app');
  if (/\\/next$/.test(location.pathname)) { app.innerHTML = '<main><h1>Next</h1></main>'; return; }
  app.innerHTML = `<main class="corridor"><section class="ccard"><div class="ccard__body">
    <h1 class="calib__q">How often does it happen?</h1>
    <div class="calib__numeric"><div class="calib__nums"><input class="calib__num"><input class="calib__num"></div>
    ${O.hint ? `<p class="calib__hint calib__rangehint" data-testid="frequency-range-hint">${O.hint}</p>` : ''}</div>
    <p class="calib__belief-text">It happens most weeks.</p></div>
    <div class="ccard__foot"><button type="button" class="btn primary">Continue</button></div></section></main>`;
  app.querySelector('.btn.primary').addEventListener('click', () => { history.pushState({}, '', '/p/p1/next'); render(); });
}
render();
</script></body></html>"""


@pytest.mark.parametrize("hint, faults", [(vs_screens.FREQUENCY_RANGE_HINT, []), ("", ["the range hint"])])
def test_frequency_reads_its_range_hint(browser, tmp_path, hint, faults):
    page = browser.new_page()
    page.route(f"{BASE}/**", lambda route: route.fulfill(status=200, content_type="text/html",
                                                         body=_FREQUENCY % {"opts": json.dumps({"hint": hint})}))
    page.goto(f"{BASE}/p/p1/define/problem/q/2", wait_until="load")
    try:
        corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
        corridor.camera = lambda slug: None
        seen = corridor.single({"dimension": "problem.frequency", "control": "numeric_interval"},
                               {"interval": {"low": 1, "high": 3, "unit": "week"}})
    finally:
        page.close()
    assert seen["range_hint"] == (hint or None)
    assert [f["what"] for f in cs.said_faults(seen, "problem.frequency", b2b=False)] == faults


def test_one_calibrate_step_holds_what_each_screen_says():
    source = inspect.getsource(cs.leg_calibrate)
    assert "said_faults(screen, key, b2b=j.entry.b2b())" in source
    assert "keel-web 153, keel-cloud 179; spec 117" in source


# ------------------------------------------------------------- FR-4: keel-web 152's two chips and the refusal said

_SHEET = """<!doctype html><html><body><div data-testid="ai-sheet"><p class="iv-q">Tell me about the last payroll run.</p>
<div class="iv-chips">%s</div></div></body></html>"""


def test_the_story_sheet_reads_both_chips_the_first_still_cant_recall(browser, tmp_path):
    chips = ["I can't recall one particular payroll run", "I'd rather not say"]
    page = browser.new_page()
    page.set_content(_SHEET % "".join(f'<button class="chip" aria-pressed="false">{c}</button>' for c in chips))
    try:
        player = ivs.Player(page, Recorder(tmp_path))
        sheet = player.sheet()
        assert sheet["chip"] == chips[0] and sheet["chips"] == chips
        page.evaluate("""() => document.querySelectorAll('.iv-chips .chip').forEach((b) => b.addEventListener('click',
            () => b.setAttribute('aria-pressed', 'true')))""")
        player.tap_chip_named(fake.story_chip_word("RATHER_NOT_SAY", "payroll run"))
        assert page.locator(".iv-chips .chip[aria-pressed=true]").all_inner_texts() == [chips[1]]
    finally:
        page.close()


class _Stub:
    """The player as `_Walk.story` drives it on a chip: the taps, and the done screen at once (`_wait_next`)."""
    patience = 1.0

    def __init__(self):
        self.did: list = []
        self.page = SimpleNamespace(get_by_test_id=lambda _id: SimpleNamespace(count=lambda: 1))

    def tap_chip(self):
        self.did.append("first")

    def tap_chip_named(self, label):
        self.did.append(label)

    def question(self):
        return None


@pytest.mark.parametrize("chip, tapped", [("CANT_RECALL", "first"), ("RATHER_NOT_SAY", "I'd rather not say")])
def test_the_walk_taps_the_scripted_chip_by_its_words(chip, tapped):
    player = _Stub()
    walk = il._Walk(player, {"gate": {"chips": ["CANT_RECALL", "RATHER_NOT_SAY"]}},
                    {"recency": True, "anchorChip": chip, "answers": []})
    walk.story({"question": "Tell me about the last payroll run.", "did": []})
    assert player.did == [tapped]


@pytest.mark.parametrize("said, refusal", [
    ("I'd rather not say", True), ("I would rather not say", True), ("I'd prefer not to say", True),
    ("I don't want to say", True), ("rather not", True), ("No, sorry, I'd rather not talk about it", True),
    ("I'd rather not say, that's my answer", True),
    ("They did not say when the payroll would be fixed", False),
    ("It was for my work account. I'd rather not say what it was.", False),
    ("I can't recall one particular payroll run", False), ("", False)])
def test_a_spoken_refusal_is_152s_chip_said(said, refusal):
    assert fake.story_chip_said(fake.STORY_RATHER_NOT_SAY, said) is refusal


def test_a_scripted_story_that_is_the_refusal_stops_the_walk_by_name():
    walk = il._Walk(_Stub(), {"gate": {"chips": ["CANT_RECALL", "RATHER_NOT_SAY"]}},
                    {"recency": True, "story": "I'd rather not say.", "answers": []})
    with pytest.raises(AssertionError, match="the refusal said aloud"):
        walk.story({"question": "Tell me about the last payroll run.", "did": []})


def test_no_corpus_story_is_a_refusal_said():
    """The walk speaks each scripted story; keel-web 152 ends the interview on one that IS the refusal. None of the
    corpus's is (the ones that carry *I'd rather not say ...* say more), so every person's expected body still holds."""
    from stack.config import load_config                                  # noqa: PLC0415
    keel_cloud = load_config(validate=False).keel_cloud
    try:
        corpora = [vs.load(keel_cloud), vs.load(keel_cloud, backtest=True)]   # the golden 01-07, the back-test 08-35
    except Exception as missing:  # noqa: BLE001
        pytest.skip(f"the corpus is not readable here: {missing}")
    stories = [(e.id, person.person, person.story) for corpus in corpora for e in corpus.entries
               for person in vs.person_inputs(e) if person.story]
    assert stories
    assert [s for s in stories if fake.story_chip_said(fake.STORY_RATHER_NOT_SAY, s[2])] == []


# --------------------------------------------------------------- FR-4: the stage page by keel-web 154's ids

_ROW_154 = """<div class="dimrow" id="{key}" data-testid="stage-dimension" data-dim="{key}" data-opens="{opens}"
  data-open="{open}">{head}<span class="dimrow__name">{name}</span>
  <span class="status" data-testid="dimension-verdict">Holding up<span class="status__insight"> · most said yes</span>
  <span class="sub" data-testid="dimension-count">7 of 9 said yes</span></span>{body}</div>"""
_ROW_OLD = """<div class="dimrow" id="{key}" data-open="{open}">{head}<span class="dimrow__name">{name}</span>
  <span class="status">Holding up<span class="status__insight"> · most said yes</span>
  <span class="sub">7 of 9 said yes</span></span>{body}</div>"""


def _stage(ids: bool) -> str:
    rows = []
    for key, name, opens, open_ in (("problem.prevalence", "Prevalence", True, True),
                                    ("problem.frequency", "Frequency", False, False)):
        head = ('<button class="dimrow__head" data-testid="stage-dimension-open">open</button>' if ids
                else '<button class="dimrow__head">open</button>') if opens else '<div class="dimrow__head"></div>'
        body = ('<div class="dimrow__body"><div class="dimrow__drawing"'
                + (' data-testid="dimension-chart"' if ids else "")
                + '><div class="achart" data-chart="bars"><p class="achart__caption">Most weeks</p></div></div>'
                  '</div>') if open_ else ""
        rows.append((_ROW_154 if ids else _ROW_OLD).format(key=key, name=name, opens=str(opens).lower(),
                                                           open=str(open_).lower(), head=head, body=body))
    root = 'class="corridor answers"' + (' data-testid="stage-page" data-stage="PROBLEM"' if ids else "")
    verdict = '<p class="answers__headline"' + (' data-testid="stage-verdict"' if ids else "") + '>It holds.</p>'
    return (f'<main><div {root}><p class="corridor__kicker">Problem</p><h1 class="ccard__title">Is it real</h1>'
            f'{verdict}{"".join(rows)}</div></main>')


def test_the_leg_reads_154s_ids_and_falls_back_to_the_classes(browser):
    page = browser.new_page()
    try:
        read = {}
        for ids in (True, False):
            page.set_content(_stage(ids))
            read[ids] = {"stage": page.evaluate(bt.STAGE_JS), "card": page.evaluate(bt.CARD_JS, "problem.prevalence")}
            assert page.locator(bt.STAGE_ROW).count() == 2
            assert page.locator(bt.card_selector("problem.prevalence", bt.CARD_OPEN)).count() == 1
            assert page.locator(bt.card_selector("problem.prevalence", bt.CARD_BODY)).count() == 1
            assert page.locator(bt.card_selector("problem.frequency", bt.CARD_OPEN)).count() == 0
    finally:
        page.close()
    new, old = read[True], read[False]
    assert new["stage"]["page"]["by_ids"] is True and old["stage"]["page"]["by_ids"] is False
    assert new["stage"]["page"]["stage"] == "PROBLEM" and old["stage"]["page"]["stage"] is None
    assert new["card"].pop("by_ids") is True and old["card"].pop("by_ids") is False
    for side in (new, old):
        side["stage"]["page"].pop("by_ids")
        side["stage"]["page"].pop("stage")
    assert new == old, "the same words whichever way the page is read"
    page_ = new["stage"]["page"]
    assert page_["headline"] == "It holds." and page_["kicker"] == "Problem" and page_["title"] == "Is it real"
    assert [(r["dimension"], r["opens"], r["open"]) for r in page_["rows"]] == [
        ("problem.prevalence", True, True), ("problem.frequency", False, False)]
    chart = new["card"]["chart"]
    assert chart["chart"] == "bars" and chart["caption"] == "Most weeks"
    assert chart["count"] == "7 of 9 said yes" and chart["insight"] == "· most said yes"
    assert chart["verdict"].startswith("Holding up")


def test_the_card_selector_names_154s_id_first_then_the_class():
    assert bt.card_selector("problem.prevalence", bt.CARD_OPEN) == (
        "[data-testid=stage-dimension][data-dim='problem.prevalence'] [data-testid=stage-dimension-open], "
        ".dimrow[id='problem.prevalence'] button.dimrow__head")
    assert bt.card_selector("problem.prevalence") == (
        "[data-testid=stage-dimension][data-dim='problem.prevalence'], .dimrow[id='problem.prevalence']")
    assert bt.STAGE_ROW == "[data-testid=stage-dimension], .dimrow"
