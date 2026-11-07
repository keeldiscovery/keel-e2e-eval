"""Spec 143 -- the harness mirrors keel-cloud spec 232 (keel-cloud-docs master `ac81bf6f`).

- FR-4 the mirrors: `quality/readers/dimensions.md` is keel-cloud's `dimension-cards.md` byte for byte at 232's
  `CARDS_SHA256` (Importance §2 and Current solution §2: the review may change a row, Put back); the Palus anchor (232
  FR-7, `ItemFrames.thinkOf`) -- *last* said once where the occasion opens on it -- in `instructions/wording.think_of`
  and the two ScaleFour anchors the harness builds (`instructions/spoken.at_stake`, `hard_case`).
- FR-2 the walk leaves a changed row alone: `harness/vectors_script`'s served-list readers (`row_present`,
  `missing_rows`, `held_by_review`, `review_changed`, `review_band`, `lists_reviewed`, `changed_over_cap`,
  `founder_words`) on 232's recorded Codyco lists (its tasks.md, the journey's fixture), and the walk's strict checks that
  read them (`corpus_scenario._choose_label`, `keel_left_out`, `keel_added`, `reviewed_as_saved`, `review_defects`,
  `_not_held_by_review`, `vectors_script.rungs_plan`), the Check as keel-web 179 draws it (`_list_rows`,
  `_cut_over_cap_rows`), the bundle (`backtest.lists_reviewed`, `backtest.md`) and the record (`cycle.review_line`).

No stack, no model, no key: the cloud's files are read where the checkout is there, else skipped by name.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import spoken as spoken_mod
from quality import cycle
from instructions import wording as wording_mod
from quality import cards
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
#: keel-cloud 232 FR-6: `RespondentReview.CARDS_SHA256` at keel-cloud-docs `ac81bf6f` (was `06fcd867...`, 231).
CARDS_SHA256_232 = "2f4f0bf810dc9a5eb75e5af7986fa1a60ba1937e88af8a1923905e95149618f7"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD} ({rel})")
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------- FR-4 the cards

def test_the_reader_digest_is_232s_cards():
    """FR-4: the reader's cards are the cloud's vendored copy byte for byte, at 232's digest -- or a later round's (eval
    spec 144 moved the copy to keel-cloud 233's, `CARDS_SHA256_141`)."""
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    ours = cards.CARDS_PATH.read_bytes()
    assert hashlib.sha256(ours).hexdigest() == sha == CARDS_SHA256_141
    assert sha in (CARDS_SHA256_232, CARDS_SHA256_141)
    assert (KEEL_CLOUD / "src/main/resources/keel/dimension-cards.md").read_bytes() == ours


def test_the_two_amended_sections_say_the_review_may_change_a_row():
    """FR-4 (232 FR-6): Importance §2 and Current solution §2 say the review may change a row that breaks the card, the
    Check says so in one line, the founder's words behind Put back; *never rewritten* / *Never a rewrite* are cut."""
    text = " ".join(cards.CARDS_PATH.read_text(encoding="utf-8").split())
    assert "**The review may change such a rival** (keel-cloud 232)" in text
    assert "*Answering group requests that come by email* -> *Taking group enquiries over the phone*" in text
    assert "**The review may change such a rung** (spec 232)" in text
    assert "(*Never called back*, never *simply lost*)" in text
    # eval spec 144 (keel-cloud 233 FR-5): Compatibility §2 says it a third time
    assert text.count("behind **Put back**") >= 2
    assert "The rows are never rewritten" not in text and "Never a rewrite" not in text


# ------------------------------------------------------------------------------------- FR-4 the Palus anchor

@pytest.mark.parametrize("whose,occasion,want", [
    ("your", "last 3 months", "Think of the last 3 months."),
    ("your", "the last 3 months", "Think of the last 3 months."),
    ("your", "Your last site walk", "Think of the last site walk."),
    ("the", "last 5 working days", "Think of the last 5 working days."),
    ("your", "their last shift", "Think of the last shift."),
    ("your", "last 3 months holding raise cash", "Think of the last 3 months holding raise cash."),
    ("your", "daily log", "Think of your last daily log."),
    ("the", "daily log", "Think of the last daily log."),
    ("your", "last-minute booking", "Think of your last last-minute booking."),     # a word that only begins with last
])
def test_think_of_says_last_once(whose, occasion, want):
    """FR-4 (232 FR-7): `ItemFrames.thinkOf`'s cases (`TheAnchorSaysLastOnceTest.theOpenings`), mirrored."""
    assert wording_mod.think_of(whose, occasion) == want


def test_the_mirror_reads_the_clouds_openings():
    """FR-4: the openings are the cloud's (`ItemFrames.LAST_OPENINGS`), in its order."""
    frames = _cloud(VECTORS + "ItemFrames.java")
    found = re.search(r"LAST_OPENINGS = java\.util\.List\.of\(([^)]*)\)", frames)
    assert found, "ItemFrames.LAST_OPENINGS"
    assert tuple(re.findall(r'"([^"]*)"', found.group(1))) == wording_mod.LAST_OPENINGS
    assert '"Think of the last " + noun.substring(opening.length()).strip() + "."' in frames


def test_the_scale_four_anchors_say_last_once():
    """FR-4 (232 FR-7: ScaleFour's two anchors through `thinkOf`): the at-stake and hard-case anchors the harness builds
    say *last* once on a window occasion, and read as before on *daily log*."""
    assert spoken_mod.at_stake("last 3 months", "hold raise cash") == \
        "Think of the last 3 months when you had to hold raise cash."
    assert spoken_mod.at_stake("daily log", "write up the site notes") == \
        "Think of the last daily log when you had to write up the site notes."
    assert spoken_mod.at_stake("time", "hold raise cash") == "Think of the most recent time you had to hold raise cash."
    four = _cloud(VECTORS + "ScaleFour.java")
    assert four.count('ItemFrames.thinkOf("the", noun).replaceAll("\\\\.$", "")') == 2


# --------------------------------------------------------------------- FR-2 the walk leaves a changed row alone
#
# keel-cloud 232 tasks.md, *What a Codyco Check serves with the switch on* (the journey's fixture), as the wire serves it
# (contract 62: `items[i].typed` / `why`, `putAside`, `changed`).

RUNGS_TYPED = ["Every missed call called back within the hour", "All called back that day",
               "Some called back when there was time", "Few were ever called back",
               "Calls that rang out were simply lost"]
HOW_MANY = "This rung grades how many were called back, not how soon."
CURRENT_SOLUTION = {
    "items": [{"code": "outcome_1", "label": RUNGS_TYPED[0]}, {"code": "outcome_2", "label": RUNGS_TYPED[1]},
              {"code": "outcome_3", "label": "Called back the next day", "typed": RUNGS_TYPED[2], "why": HOW_MANY},
              {"code": "outcome_4", "label": "Called back days later", "typed": RUNGS_TYPED[3], "why": HOW_MANY},
              {"code": "outcome_5", "label": "Never called back", "typed": RUNGS_TYPED[4],
               "why": "This rung grades what happened to the call, not how soon it was called back."}],
    "phrase": "calling back missed calls", "line": 1, "lineAfter": 0,
    "changed": {"line": "Keel changed three answers so they sit on one scale.", "why": HOW_MANY}}
ROWS_TYPED = ["Picking up booking calls before they ring out", "Answering group requests that come by email",
              "Chasing deposits on held bookings", "Updating the booking system after each call"]
EMAIL = "This happens by email, not at the moment a booking call rings."
IMPORTANCE = {
    "items": [{"code": "own", "label": ROWS_TYPED[0]},
              {"code": "rival_1", "label": "Taking group enquiries over the phone", "typed": ROWS_TYPED[1], "why": EMAIL},
              {"code": "rival_2", "label": ROWS_TYPED[2]}],
    "putAside": [{"typed": ROWS_TYPED[3], "why": "This comes after the call, not when it rings."}],
    "changed": {"line": "Keel changed one row and put one aside so the rest sit at the moment your problem names.",
                "why": EMAIL}}
UNTOUCHED = {"items": [{"code": "own", "label": ROWS_TYPED[0]}, {"code": "rival_1", "label": ROWS_TYPED[2]}]}


def test_a_changed_row_and_a_put_aside_row_count_as_present():
    assert vs.missing_rows(RUNGS_TYPED, CURRENT_SOLUTION) == []
    assert vs.missing_rows(ROWS_TYPED, IMPORTANCE) == []
    assert vs.row_present("answering group requests that come by email.", IMPORTANCE), "read as _same_words reads"
    assert vs.missing_rows(["Taking group enquiries over the phone"], IMPORTANCE) == [], "the row as served, too"
    assert vs.missing_rows(ROWS_TYPED, UNTOUCHED) == [ROWS_TYPED[1], ROWS_TYPED[3]]
    assert vs.held_by_review(ROWS_TYPED, IMPORTANCE) == [ROWS_TYPED[1], ROWS_TYPED[3]]
    assert vs.held_by_review(ROWS_TYPED, UNTOUCHED) == []
    assert vs.put_aside_of({"put_aside": [{"typed": "x"}]}) == [{"typed": "x"}], "the spec's spelling read too"


def test_what_the_review_did_is_recorded_per_list():
    assert vs.review_changed(IMPORTANCE) == [
        {"typed": ROWS_TYPED[1], "label": "Taking group enquiries over the phone", "why": EMAIL},
        {"typed": ROWS_TYPED[3], "label": None, "why": "This comes after the call, not when it rings."}]
    assert [c["label"] for c in vs.review_changed(CURRENT_SOLUTION)] == \
        ["Called back the next day", "Called back days later", "Never called back"]
    assert vs.review_band(CURRENT_SOLUTION) == {"line": "Keel changed three answers so they sit on one scale.",
                                                "why": HOW_MANY}
    assert vs.review_changed(UNTOUCHED) == [] and vs.review_band(UNTOUCHED) is None
    views = {"PROBLEM": {"questions": [
        {"dimension": "problem.importance", "answer": {"list": IMPORTANCE}},
        {"dimension": "problem.current_solution_satisfaction", "answer": {"list": CURRENT_SOLUTION}},
        {"dimension": "problem.prevalence", "answer": {"value": 3}}]}, "SOLUTION": {}, "COMMERCIAL": None}
    got = vs.lists_reviewed(views)
    assert set(got) == {"problem.importance", "problem.current_solution_satisfaction"}
    assert got["problem.importance"]["band"]["line"].startswith("Keel changed one row and put one aside")
    assert vs.lists_reviewed({"PROBLEM": {"questions": [{"dimension": "problem.importance",
                                                         "answer": {"list": UNTOUCHED}}]}}) == {}
    assert vs.founder_words(IMPORTANCE) == [ROWS_TYPED[0], ROWS_TYPED[1], ROWS_TYPED[2], ROWS_TYPED[3]]


def test_a_changed_row_over_the_cap_is_a_defect_to_file_never_a_retype():
    long = {"items": [{"label": "Called back some days later by whoever happened to be in the office",
                       "typed": RUNGS_TYPED[3], "why": HOW_MANY}]}
    assert vs.changed_over_cap(CURRENT_SOLUTION, 9) == []
    assert vs.changed_over_cap(long, 9) == [{"label": long["items"][0]["label"], "typed": RUNGS_TYPED[3],
                                             "words": 13, "cap": 9}]
    j = SimpleNamespace(findings=[])
    assert cs.review_defects(j, "problem.current_solution_satisfaction", long, 9)
    assert j.findings[0]["what"].startswith("DEFECT (keel-cloud 232): the review changed the founder's row "
                                            f"'{RUNGS_TYPED[3]}'") and "13 words, over the 9-word cap" in \
        j.findings[0]["what"]


def test_the_rungs_plan_never_types_over_a_changed_rung(monkeypatch):
    monkeypatch.setattr(vs, "founder_list", lambda entry, key: {"items": [{"label": r} for r in RUNGS_TYPED]})
    drawn = [i["label"] for i in CURRENT_SOLUTION["items"]]
    assert vs.rungs_plan(None, drawn, 5) == {"edit": [(2, RUNGS_TYPED[2]), (3, RUNGS_TYPED[3]),
                                                      (4, RUNGS_TYPED[4])], "add": [], "cannot": []}, "before 143"
    typed = vs.typed_by_label(CURRENT_SOLUTION)
    assert vs.rungs_plan(None, drawn, 5, typed) == {"edit": [], "add": [], "cannot": []}


def test_the_walk_reads_the_typed_words_off_the_wire_and_the_was_line(monkeypatch):
    monkeypatch.setattr(vs, "founder_list", lambda entry, key: {"items": [{"label": r} for r in RUNGS_TYPED]})
    j = SimpleNamespace(entry=None, findings=[])
    question = {"dimension": "problem.current_solution_satisfaction", "saves": {"maxItems": 5}, "draft": None,
                "answer": {"list": CURRENT_SOLUTION}}
    drawn = {"rows": [{"text": i["label"]} for i in CURRENT_SOLUTION["items"]]}
    monkeypatch.setattr(cs, "_step", _no_step)
    assert cs._rungs_to_type(j, question, drawn) == {"edit": [], "add": [], "cannot": []}
    # off the screen alone (keel-web 179's *Was:* line), the wire saying nothing
    drawn = {"rows": [{"text": i["label"], **({"was": i["typed"]} if i.get("typed") else {})}
                      for i in CURRENT_SOLUTION["items"]]}
    assert cs._rungs_to_type(j, {**question, "answer": None}, drawn)["edit"] == []


class _no_step:
    def __init__(self, *a, **k):
        self.h = SimpleNamespace(record_assert=lambda *x, **y: None)

    def __enter__(self):
        return self.h

    def __exit__(self, *exc):
        return False


def test_importance_rows_the_review_holds_are_never_typed_again():
    j = SimpleNamespace(findings=[])
    question = {"dimension": "problem.importance", "draft": None, "answer": {"list": IMPORTANCE}}
    assert cs._not_held_by_review(j, question, "problem.importance", ROWS_TYPED[1:]) == [ROWS_TYPED[2]]
    assert j.findings[0]["served"]["held"] == [ROWS_TYPED[1], ROWS_TYPED[3]]
    assert "never retyped" in j.findings[0]["what"]
    j = SimpleNamespace(findings=[])
    assert cs._not_held_by_review(j, {"draft": UNTOUCHED}, "problem.importance", ROWS_TYPED[1:]) == ROWS_TYPED[1:]
    assert j.findings == []


def _answer(labels: list[str], picked: int) -> vs.CalibrationAnswer:
    return vs.CalibrationAnswer("x", {"dimension": "x", "list": {"items": [{"label": label} for label in labels],
                                                                 "pickedIndex": picked}})


def test_the_choose_pick_stays_by_label_as_served():
    """104 FR-1 / 108 FR-2 on a list served with a changed row: the pick is the row whose `typed` is the founder's,
    by its label as served (never put back); a changed row is neither left out nor Keel's; a put-aside picked row stops by
    name."""
    j = SimpleNamespace(strict=False, findings=[])
    question = {"dimension": "solution.compatibility", "draft": IMPORTANCE}
    assert cs._choose_label(j, question, _answer(ROWS_TYPED, 1)) == ("Taking group enquiries over the phone", 1)
    assert "picked as served" in j.findings[0]["what"] and "DRIFT" not in j.findings[0]["what"]
    assert cs.keel_left_out(question, _answer(ROWS_TYPED, 0)) == []
    assert cs.keel_added(question, _answer(ROWS_TYPED, 0)) == []
    with pytest.raises(vs.VectorsScriptError, match="put aside by the review"):
        cs._choose_label(j, question, _answer(ROWS_TYPED, 3))
    assert cs.keel_left_out({"dimension": "solution.compatibility", "draft": UNTOUCHED},
                            _answer(ROWS_TYPED, 0)) == [ROWS_TYPED[1], ROWS_TYPED[3]], "untouched: as before"


def test_the_stored_list_is_the_founders_as_saved_read_back_to_their_words():
    want = {"items": [{"code": f"outcome_{n + 1}", "label": r} for n, r in enumerate(RUNGS_TYPED)],
            "pickedIndex": None, "phrase": "calling back missed calls"}
    assert cs.reviewed_as_saved(want, CURRENT_SOLUTION)
    assert not cs.reviewed_as_saved(want, {**CURRENT_SOLUTION, "phrase": "other"})
    assert not cs.reviewed_as_saved(want, UNTOUCHED), "a list the review left alone is compared as it was"


def test_the_bundle_and_the_record_say_what_the_review_did():
    j = SimpleNamespace(project=lambda path: path,
                        get=lambda path: {"questions": [{"dimension": "problem.importance",
                                                         "answer": {"list": IMPORTANCE}}]}
                        if path == "/calibration/PROBLEM" else {})
    reviewed = bt.lists_reviewed(j)
    assert list(reviewed) == ["problem.importance"]
    md = bt.markdown({"lists_reviewed": reviewed, "respondents": {}, "founder_screens": []})
    assert ("- The review changed problem.importance: *Keel changed one row and put one aside so the rest sit at the "
            f"moment your problem names.* '{ROWS_TYPED[1]}' -> 'Taking group enquiries over the phone'; "
            f"'{ROWS_TYPED[3]}' -> put aside") in md
    assert cycle.review_rows(reviewed) == {"changed": 1, "put_aside": 1}
    d = {"review_switch": "ON", "studies": [{"review_rows": {"changed": 1, "put_aside": 1}},
                                            {"review_rows": {"changed": 3, "put_aside": 0}}, {}]}
    assert cycle.review_line(d) == ["  - the review (spec 209, keel-cloud 232): 4 founder rows changed and 1 put aside "
                                    "over 2 walks (each bundle's `lists_reviewed`); the readers scored the screens as "
                                    "served"]
    assert cycle.review_line({**d, "review_switch": "OFF"}) == []


# ------------------------------------------------------------------- FR-2 the Check as keel-web 179 draws it

def check_page() -> str:
    """keel-web 179's Check as built (master `ed646e8d`, `ListQuestion.tsx`): the band (`list-changed`, `role=status`,
    `.calib__changed-line` / `-why`), a changed row (the tag `row-changed` in place of the word count, its why
    `row-why` -- also a `.listrow__warn` -- and `row-was`: *Was:* + `.listrow__was-said` + Put back), a changed row over
    the cap (a keel-cloud defect; no word count drawn), and the put-aside rows (`put-aside` > `put-aside-row`,
    `li.listrow.listrow--aside` in a second `ul.listrows`, the words in `s`, the why in `[role=note]`), Save disabled."""
    def row(label, *, was=None, why=None):
        if was is None:
            return ('<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">' + label
                    + '</textarea><span class="listrow__wc">7 / 9</span></div></li>')
        return ('<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">' + label + '</textarea>'
                '<span class="listrow__tag listrow__tag--changed" data-testid="row-changed">changed</span></div>'
                + (f'<p class="listrow__warn listrow__warn--why" role="note" data-testid="row-why">{why}</p>'
                   if why else "")
                + '<p class="listrow__was" data-testid="row-was"><span class="listrow__was-k">Was:</span> '
                f'<span class="listrow__was-said">{was}</span><button type="button" class="listrow__putback" '
                f'data-testid="row-put-back">Put back</button></p></li>')
    return ('<main><div class="ccard calib"><div class="ccard__body"><div class="calib__changed" role="status" '
            'data-testid="list-changed"><p class="calib__changed-line">Keel changed one row and put one aside so the '
            f'rest sit at the moment your problem names.</p><p class="calib__changed-why">{EMAIL}</p></div>'
            '<div class="listcheck"><ul class="listrows">'
            + row(ROWS_TYPED[0])
            + row("Taking group enquiries over the phone", was=ROWS_TYPED[1], why=EMAIL)
            + row("Called back some days later by whoever happened to be in the office", was=ROWS_TYPED[2])
            + '</ul><div class="listcheck__aside" data-testid="put-aside"><p class="listcheck__k">Put aside</p>'
            '<ul class="listrows"><li class="listrow listrow--aside" data-testid="put-aside-row"><p class="listrow__aside">'
            f'<s class="listrow__struck">{ROWS_TYPED[3]}</s></p><p class="listrow__warn listrow__warn--why" '
            'role="note">This comes after the call, not when it rings.</p><p class="listrow__was"><button type="button" '
            'data-testid="put-aside-back">Put back</button></p></li></ul></div></div></div></div>'
            '<button class="corridor__primary" disabled>Save</button></main>')


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def test_the_check_reads_the_changed_rows_and_never_cuts_one(browser):
    page = browser.new_page()
    try:
        page.set_content(check_page())
        corridor = object.__new__(vs_screens.Corridor)
        corridor.page = page
        read = corridor._list_rows()
        assert [r["text"] for r in read["rows"]] == [ROWS_TYPED[0], "Taking group enquiries over the phone",
                                                     "Called back some days later by whoever happened to be in the "
                                                     "office"], "a put-aside row is never a row of the list"
        changed = [r for r in read["rows"] if r.get("changed")]
        assert [r["was"] for r in changed] == [ROWS_TYPED[1], ROWS_TYPED[2]]
        assert changed[0]["why"] == EMAIL and changed[0]["warn"] == "", "the why is read apart, never as `warn`"
        assert read["band"] == {"line": "Keel changed one row and put one aside so the rest sit at the moment your "
                                        "problem names.", "why": EMAIL}
        assert read["put_aside"] == [{"typed": ROWS_TYPED[3], "why": "This comes after the call, not when it rings."}]
        assert corridor._cut_over_cap_rows("problem.importance") == [], "a changed row over the cap is never cut"
        assert page.locator("textarea").nth(2).input_value().startswith("Called back some days later by whoever")
    finally:
        page.close()
    assert vs_screens._was_line("Was: Answering group requests Put back") == "Answering group requests"
    assert vs_screens._was_line("no line") is None


def test_the_camera_records_what_the_review_changed(browser):
    """The bundle's shot of the Check (`backtest.READ_JS`): the put-aside rows are never rows; the band, the changed rows
    (as served, the founder's words, the why) and the put-aside rows go into `review`, and through
    `founder_screens` into `backtest.json`."""
    page = browser.new_page()
    try:
        page.set_content(check_page())
        shot = page.evaluate(bt.READ_JS)
    finally:
        page.close()
    assert shot["rows"] == [ROWS_TYPED[0], "Taking group enquiries over the phone",
                            "Called back some days later by whoever happened to be in the office"]
    assert shot["review"]["band"]["line"].startswith("Keel changed one row and put one aside")
    assert shot["review"]["changed"][0] == {"row": "Taking group enquiries over the phone", "was": ROWS_TYPED[1],
                                            "why": EMAIL}
    assert shot["review"]["put_aside"] == [{"typed": ROWS_TYPED[3],
                                            "why": "This comes after the call, not when it rings."}]
    cam = SimpleNamespace(founder_shots=[{"n": 9, "slug": "check-problem.importance", **shot}])
    assert bt.founder_screens(None, cam, {})[0]["review"] == shot["review"]


def test_the_choose_shot_reads_a_changed_rows_why(browser):
    """keel-web 179 FR-4: the option's why by the radio's `aria-describedby` id `choose-{dim}-changed-{i}`."""
    page = browser.new_page()
    try:
        page.set_content('<main><div role="radiogroup"><button role="radio" aria-checked="false" '
                         'aria-describedby="choose-x-changed-0">Taking group enquiries over the phone</button>'
                         f'<p class="listrow__warn listrow__warn--why calib__optnote" role="note" id="choose-x-changed-0" '
                         f'data-testid="row-why">{EMAIL}</p></div></main>')
        shot = page.evaluate(bt.READ_JS)
    finally:
        page.close()
    assert shot["choices"] == [{"label": "Taking group enquiries over the phone", "suggested": False, "why": None,
                                "changed": EMAIL}]


def test_the_walk_never_presses_put_back():
    """FR-2: no line of the walk's code presses Put back -- it is read (the *Was:* line), never clicked."""
    root = Path(__file__).resolve().parent.parent
    for rel in ("harness/vectors_screens.py", "evals/corpus_scenario.py", "evals/backtest.py"):
        for line in (root / rel).read_text(encoding="utf-8").splitlines():
            if "Put back" in line:
                assert ".click(" not in line and "get_by_role(" not in line and "get_by_text(" not in line, (rel, line)
