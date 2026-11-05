"""Spec 141 FR-8 (keel-web 178, its tasks.md *Owed: keel-e2e-eval*): the walk reads the note and the line and leaves
them. Real chromium on static pages drawn as keel-web 178's `ListQuestion.tsx` draws them; no stack, no model.

- the note: a served note under a Check row (`[data-testid=row-note]`, a locked row's too) is the row's own `note`,
  never its `warn`; a Choose option's note is read by its `aria-describedby` id (`choose-{dim}-note-{i}`); the reader's
  row scrape keeps the row's words apart from the note (`row_notes`);
- the line: its words inside `[data-testid=line-control]` (`data-line` on both), read and left where drawn;
- *Per* arrives empty (`corpus_scenario.chain_fill`), and *· per {unit} ·* beside a percent of a named base is owed
  (`chain.equation_per_drawn`; FR-7).
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from instructions import chain as chain_mod
from stack.config import load_config

KEEL_WEB = Path(load_config(validate=False).keel_web)
NOTE = "This reads as what every one of them does. Strangers pick what hurts; name the part that goes wrong."
SETTLED = "Everyone in the segment already meets this, so it tests nothing."


def _web(rel: str) -> str:
    path = KEEL_WEB / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_WEB}")
    return path.read_text(encoding="utf-8")


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


CHECK = f"""<main><div class="listcheck"><p class="listcheck__title">The difficulties</p><ul class="listrows">
<li class="listrow"><div class="listrow__line"><span class="listrow__ed listrow__ed--lock" aria-describedby="n0">Settling
the baby</span><span class="listrow__tag">Keel's</span></div>
<p class="listrow__warn" role="note" id="n0" data-testid="row-note">{NOTE}</p></li>
<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">Getting back to sleep yourself</textarea>
<span class="listrow__wc">5 / 9</span></div><p class="listrow__warn">Reword this row</p>
<p class="listrow__warn" role="note" id="n1" data-testid="row-note">{SETTLED}</p></li>
<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">Early morning wake-ups</textarea>
<span class="listrow__wc">3 / 9</span></div></li></ul>
<div class="listcheck__linectl" data-testid="line-control" data-line="2"><p class="listcheck__line" data-line="2"
id="list-line-words">Below here counts as falling short</p></div></div></main>"""

CHOOSE = f"""<main><h1 class="calib__q">Which one would you test?</h1>
<button type="button" role="radio" aria-checked="false" aria-describedby="choose-solution.compatibility-note-0"
class="calib__opt">Had a phone to hand</button>
<p class="listrow__warn calib__optnote" role="note" id="choose-solution.compatibility-note-0" data-testid="row-note">
{SETTLED}</p>
<button type="button" role="radio" aria-checked="false" class="calib__opt">Could forward calls</button></main>"""


def test_the_markup_is_keel_webs():
    """keel-web 178 FR-1 / FR-2 (`ListQuestion.tsx`): the note's testid and its Choose id, the line control."""
    source = _web("src/components/calibration/ListQuestion.tsx")
    assert f'data-testid="{vs_screens.ROW_NOTE_TESTID}"' in source
    assert "const noteId = `choose-${question.dimension}-note-${i}`;" in source
    assert f'data-testid="{vs_screens.LINE_CONTROL_TESTID}" data-line={{line}}' in source
    assert '<p className="listcheck__line" data-line={line}' in source


def test_the_check_reads_each_rows_note_apart_and_the_line(page):
    """The walk's Check read (`Corridor._list_rows`): the note is the row's `note`, a locked row's too, and never its
    `warn`; the line's words and place read inside the control."""
    page.set_content(CHECK)
    read = vs_screens.Corridor._list_rows(SimpleNamespace(page=page, _commitment_block=lambda: None))
    rows = read["rows"]
    assert rows[0]["locked"] and rows[0]["text"] == "Settling the baby" and rows[0]["note"] == NOTE
    assert rows[1]["warn"] == "Reword this row" and rows[1]["note"] == SETTLED
    assert "note" not in rows[2] and rows[2]["warn"] == ""
    assert read["line"] == "Below here counts as falling short" and read["line_at"] == 2 and read["line_control"]


def test_the_reader_keeps_the_rows_words_and_the_notes_apart(page):
    """`backtest.READ_JS`: the row scrape never takes a note as the row's words; `row_notes` and a Choose option's
    `note` (by its `-note-` describedby id) carried as read."""
    page.set_content(CHECK)
    shot = page.evaluate(bt.READ_JS)
    assert NOTE not in " ".join(shot["rows"]) and SETTLED not in " ".join(shot["rows"])
    # a locked row reads as the scrape always read it (its words and the tag's, `innerText`), the note off its end
    assert shot["row_notes"] == [{"row": "Settling the babyKeel's", "note": NOTE},
                                 {"row": "Getting back to sleep yourself", "note": SETTLED}]
    page.set_content(CHOOSE)
    choose = page.evaluate(bt.READ_JS)
    assert choose["choices"][0] == {"label": "Had a phone to hand", "suggested": False, "why": None, "note": SETTLED}
    assert "note" not in choose["choices"][1]
    page.set_content("<main><h1>Plain</h1><button role='radio'>A</button></main>")
    plain = page.evaluate(bt.READ_JS)
    assert plain["choices"] is None and plain["row_notes"] is None


def test_per_arrives_empty_and_per_unit_is_owed_beside_a_percent():
    """keel-web 178 FR-4 (keel-cloud 227 FR-3): *Per* arrives empty; the equation keeps *· per {unit} ·* beside a
    percent of a named base (`CHAIN_UNIT_HELP` unchanged)."""
    source = _web("src/lib/translate.ts")
    assert f'CHAIN_UNIT_HELP = "{vs_screens.CHAIN_UNIT_HELP}"' in source
    persona = {"decider": {"role": "Finance manager"}, "problemActor": "payroll practitioner"}
    assert cs.chain_fill(persona, {"state": "CONFIRMED", "occasion": {"noun": "invoice run"}}, True)["unit"] is None
    palus = {"mode": "RATE", "low": 2, "high": 2, "period": "year", "unit": "company", "measure": "%",
             "base": "the balance"}
    assert chain_mod.equation_per_drawn(palus) == "· per company · a year"
    assert cs.chain_words_owed("commercial.existing_sacrifice", palus, None, True) == (["a year"], [])
