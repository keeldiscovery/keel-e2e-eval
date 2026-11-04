"""Spec 134 -- the reader judges what the screen showed.

FR-1: on an Answer and a Check screen the read-back carries the belief the screen drew, never the wire's row `belief`
(read after the walk, it carried purchase friction's time typed later on Choose: six zeros in cycle 11). FR-2: the
founder note keel-web 168 draws in the list (`li.listrow--note`, *Your own offer ... stays off this list*) is the screen's
`note`, never a row -- in the camera's read, in the corridor's and in what the founder-reader is handed. FR-3: a Check
screen the founder typed rungs into is recorded and judged as they left it, and what they did is said, never *saved as
Keel drafted it*. Real chromium on static pages; no stack, no model.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from harness import vectors_screens as vs
from quality import readers

KEY = "commercial.purchase_friction"
RUNGS = "problem.current_solution_satisfaction"
NOTE = ("Your own offer (a trial, a pilot, a guarantee) is not a step the buyer's side must clear, so it stays off this "
        "list.")
GUIDANCE = "One to four steps, biggest first."
TIMED = "Most hotel group revenue directors would get through a data protection review of guest calls within about 4 " \
        "weeks, or not need it."
DRAWN = "Most hotel group revenue directors would get through a data protection review of guest calls, or not need it."

CHECK = f"""<main><div class="listcheck"><p class="listcheck__title">What has to happen first</p>
<ul class="listrows">
<li class="listrow"><textarea class="listrow__ed">A data protection review of guest calls</textarea>
<span class="listrow__tag"></span></li>
<li class="listrow"><textarea class="listrow__ed">A check that bookings land in our PMS</textarea>
<span class="listrow__tag">suggested</span></li>
<li class="listrow listrow--note" role="note" data-testid="list-founder-note"><p class="listrow__warn">{NOTE}</p></li>
</ul><p class="listcheck__note">{GUIDANCE}</p></div>
<div class="keeltest"><p class="keeltest__t">{DRAWN}</p><p class="keeltest__b">Holds if no more than 1 in 3 say longer.</p>
</div></main>"""

RUNGS_CHECK = """<main><div class="listcheck"><ul class="listrows">
<li class="listrow"><textarea class="listrow__ed">Log done on site</textarea></li>
<li class="listrow"><textarea class="listrow__ed">Done quickly in the trailer</textarea></li>
<li class="listrow"><textarea class="listrow__ed">Took a while</textarea></li>
</ul><p class="listcheck__note">Five outcomes, best first.</p></div>
<div class="keeltest"><p class="keeltest__t">Keel's first belief</p><p class="keeltest__b">Holds if at least 2 in 3 land
below 'Done quickly in the trailer'.</p></div></main>"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture()
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


# ------------------------------------------------------------------------------------------ FR-1 the read-back

def _journey(screen: str, drawn: dict, *, belief: str = TIMED, key: str = KEY) -> SimpleNamespace:
    return SimpleNamespace(framing={key: [{"screen": screen, **drawn}]})


def _wire(key: str = KEY, belief: str = TIMED) -> dict:
    vector = "COMMERCIAL" if key.startswith("commercial.") else "PROBLEM"
    return {f"review/{vector}": {"rows": [{"dimension": key, "belief": belief}]}}


@pytest.mark.parametrize("slug,screen", [(f"answer-{KEY}", "answer"), (f"check-{KEY}", "check")])
def test_an_answer_and_a_check_read_back_carry_the_drawn_belief_never_the_wires(slug, screen):
    drawn = {"test": {"belief": DRAWN, "bar": "Holds if no more than 1 in 3 say longer."}} if screen == "check" else {}
    back = bt.read_back(_journey(screen, drawn), slug, _wire())
    assert "belief" not in back, back
    assert TIMED not in repr(back), "the time typed later on Choose never reaches an earlier screen's read-back"
    if screen == "check":
        assert back["keel will test"] == DRAWN and back["bar"].startswith("Holds if")


def test_a_check_read_back_takes_the_box_after_the_founders_edit():
    drawn = {"test": {"belief": "before", "bar": "bar before"}, "test_after": {"belief": "after", "bar": "bar after"}}
    back = bt.read_back(_journey("check", drawn, key=RUNGS), f"check-{RUNGS}", _wire(RUNGS, "the wire's"))
    assert back == {"keel will test": "after", "bar": "bar after"}


@pytest.mark.parametrize("slug,screen", [(f"choose-{KEY}", "choose"), (f"q-{KEY}", "single")])
def test_a_choose_and_a_q_read_back_keep_the_wires_belief(slug, screen):
    assert bt.read_back(_journey(screen, {}), slug, _wire())["belief"] == TIMED
    assert set(bt.SCREEN_DRAWN_BELIEF) == {"answer", "check"}


# ------------------------------------------------------------------------------------------- FR-2 rows are rows

def test_the_camera_reads_the_founder_note_as_the_note_never_a_row(page):
    page.set_content(CHECK)
    shot = page.evaluate(bt.READ_JS)
    assert shot["rows"] == ["A data protection review of guest calls", "A check that bookings land in our PMS"]
    assert shot["note"] == [NOTE, GUIDANCE]


def test_the_corridor_reads_the_founder_note_as_the_note_never_a_row(page):
    page.set_content(CHECK)
    corridor = object.__new__(vs.Corridor)
    corridor.page = page
    read = corridor._list_rows()
    assert [r["text"] for r in read["rows"]] == ["A data protection review of guest calls",
                                                 "A check that bookings land in our PMS"]
    assert read["note"] == f"{NOTE} {GUIDANCE}"
    assert read["founder_note"] == NOTE and read["guidance"] == GUIDANCE
    # the walk's own reads (edit_rows, rungs_plan) count the rows the same way
    assert page.locator(vs.LIST_ROW).count() == 2


def test_the_reader_is_handed_the_note_labelled_under_the_rows(page):
    page.set_content(CHECK)
    shot = page.evaluate(bt.READ_JS)
    record = {"n": 20, "screen": f"check-{KEY}", "kicker": "", "question": "", "hint": "", "options": [],
              "rows": shot["rows"], "note": shot["note"], "chips": [], "answer": bt.CHECK_AS_DRAFTED}
    full = readers.founder_screens({"founder_screens": [record]})[0].full
    assert f"Rows:\n  - A data protection review of guest calls\n  - A check that bookings land in our PMS\n" \
           f"{readers.NOTE_LABEL}:\n  - {NOTE}\n  - {GUIDANCE}" in full
    assert f"  - {NOTE}" not in full.split(readers.NOTE_LABEL)[0], "the note is never among the rows"


# ---------------------------------------------------------------------------- FR-3 the Check after the edit

def test_what_the_founder_did_on_a_check_is_said():
    assert bt.check_did({}) == "saved as Keel drafted it" == bt.CHECK_AS_DRAFTED
    edited = {"rungs_edited": {"edited": [{"row": 1, "was": "x", "now": "y"}, {"row": 2, "was": "x", "now": "z"}]}}
    assert bt.check_did(edited) == "typed 2 of their own rungs over Keel's draft, then saved"
    assert bt.check_did({**edited, "rungs": {"added": ["a"]}}) == (
        "typed 2 of their own rungs over Keel's draft, and typed 1 more of their own rung into new rows, then saved")
    assert bt.check_did({"importance": {"added": ["a", "b"]}}) == (
        "typed 2 more of their own difficulties into the list, then saved")


def _founder(key: str) -> SimpleNamespace:
    answer = SimpleNamespace(dimension=key, unsure=False)
    return SimpleNamespace(calibration={"PROBLEM": [answer]})


def test_the_check_record_is_the_screen_as_the_founder_left_it(page, tmp_path):
    page.set_content(RUNGS_CHECK)
    cam = bt.Camera(run_dir=tmp_path, page=page, watched={})
    corridor = object.__new__(vs.Corridor)
    corridor.page = page
    corridor.camera = cam.founder
    slug = f"check-{RUNGS}"
    corridor._shot(slug)
    rows = page.locator(vs.LIST_ROW + " textarea.listrow__ed")
    rows.nth(1).fill("Done in the trailer in under an hour")
    rows.nth(2).fill("Took a couple of hours after the walk")
    page.evaluate("() => { document.querySelector('.keeltest__t').textContent = 'The belief after the edit';"
                  " document.querySelector('.keeltest__b').textContent = 'The bar after the edit'; }")
    corridor._reshot(slug)
    seen = {"screen": "check", "test": {"belief": "Keel's first belief"},
            "test_after": {"belief": "The belief after the edit", "bar": "after"},
            "rungs_edited": {"edited": [{"row": 1}, {"row": 2}]}}
    j = SimpleNamespace(founder=_founder(RUNGS), framing={RUNGS: [seen]})
    record = bt.founder_screens(j, cam, _wire(RUNGS, "the wire's belief"))[0]
    assert record["rows"] == ["Log done on site", "Done in the trailer in under an hour",
                              "Took a couple of hours after the walk"]
    assert record["keel_test"]["belief"] == "The belief after the edit"
    assert record["file"].endswith(f"founder-01-{slug}-after-edit.png") and record["edited"] is True
    assert record["before_edit"]["rows"] == ["Log done on site", "Done quickly in the trailer", "Took a while"]
    assert (tmp_path / record["file"]).is_file() and (tmp_path / record["before_edit"]["file"]).is_file()
    assert record["answer"] == "typed 2 of their own rungs over Keel's draft, then saved"
    assert record["keel read back"] == {"keel will test": "The belief after the edit", "bar": "after"}
    full = readers.founder_screens({"founder_screens": [record]})[0].full
    assert f"{readers.ROWS_EDITED}:\n  - Log done on site\n  - Done in the trailer in under an hour" in full
    assert "Done quickly in the trailer" not in full, "Keel's first draw is not what the reader judges"


def test_a_check_left_as_drafted_is_not_shot_again(page, tmp_path):
    page.set_content(RUNGS_CHECK)
    cam = bt.Camera(run_dir=tmp_path, page=page, watched={})
    cam.founder(f"check-{RUNGS}")
    cam.after_edit("check-never-shot")
    assert len(cam.founder_shots) == 1 and "edited" not in cam.founder_shots[0]
    corridor = object.__new__(vs.Corridor)
    corridor.camera = None
    corridor._reshot(f"check-{RUNGS}")          # no camera: nothing, never a raise
    corridor.camera = lambda slug: None         # a camera with no after_edit: nothing
    corridor._reshot(f"check-{RUNGS}")
