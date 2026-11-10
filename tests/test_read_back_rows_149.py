"""Spec 149 FR-2 -- the read-back mirror (keel-cloud 243 FR-1 to FR-4): every read-back hands numbered rows; an answer
counted from 1 is read shifted (`review.shift: 1`), one counted from 0 as handed, an index outside both a refusal line;
a suggestion beside each drop stands where the dropped row stood (`inPlaceOf` / `replacedBy`); the floor counts only
the drops with no row in place; the band counts both, and the walk's band reader reads both off a served line.

The fixtures are keel-cloud 243's own invented study (`TheReadBackIndexIsNeverMisappliedTest`, a payroll-shaped study
and an invented idea); the cloud's test file is read where the checkout is there, else its strings stand as pinned here.
No stack, no model, no key.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from harness import vectors_script as vs
from stack.config import load_config

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
FIXTURE = "src/test/java/com/keeldiscovery/cloud/protocol/founder/TheReadBackIndexIsNeverMisappliedTest.java"
IMPORTANCE, CURRENT, RA, COMPAT = ("problem.importance", "problem.current_solution_satisfaction",
                                   "solution.relative_advantage", "solution.compatibility")

# keel-cloud 243's staging shape (the founder's list of 2026-11-09, as the cloud's fixture writes it)
OWN = "Checking the payroll register for errors"
GAMES = "Playing video games"
OVERTIME = "Getting overtime hours from managers"
NEW_HIRE = "Getting new hire information from HR"
STAGING = [OWN, GAMES, OVERTIME, NEW_HIRE]
GAMES_WHY = "Playing video games is no difficulty in their work, so it is outside the work altogether."
OVERTIME_WHY = "Overtime hours are an input to the run that causes the errors, so they are a cause of the first row."
NEW_HIRE_WHY = "New hire details are another input to the run, a cause of the first row."
RECONCILING = "Reconciling timesheets against the register before the run"
RERUNNING = "Re-running payroll after a late correction"
EXPLAINING = "Explaining a wrong payslip to an employee"
STAGING_BAND = ("Keel put three rows aside and suggested three in their place, so every row sits at the moment your "
                "problem names.")
NOTES_ALONE_BAND = "Keel put one row aside so the rest sit at the moment your problem names."


def note(index, words, drop=False, suggest=None, why=None) -> dict:
    out = {"index": index, "note": words}
    if drop:
        out["drop"] = True
    if suggest is not None:
        out["suggest"] = {"label": suggest, "why": why}
    return out


def staging_answer(base: int = 1) -> dict:
    """The staging shape's answer: drops at 2, 3 and 4 counted from 1 (`base` 1), or 1, 2 and 3 from 0."""
    return {"notes": [note(base + 1, GAMES_WHY, True, RECONCILING, "The step at this moment that takes them the longest."),
                      note(base + 2, OVERTIME_WHY, True, RERUNNING, "What a late input costs them inside the run."),
                      note(base + 3, NEW_HIRE_WHY, True, EXPLAINING, "What an error turns into once the run has gone out.")]}


def _cloud_fixture() -> str | None:
    path = KEEL_CLOUD / FIXTURE
    return " ".join(path.read_text(encoding="utf-8").split()) if path.is_file() else None


# ------------------------------------------------------------------------------------ FR-1 numbered rows (243)

def test_every_read_back_hands_numbered_rows():
    """243 FR-1: Importance's rows, Current solution's rungs, Relative advantage's benefits and the ladder beside them
    are handed `[{index, label}]` from 0 -- the own row, the first rung, the lead benefit index 0."""
    rows = vs.read_back_context(IMPORTANCE, STAGING)["rows"]
    assert rows == [{"index": i, "label": r} for i, r in enumerate(STAGING)] and rows[0] == {"index": 0, "label": OWN}
    rungs = vs.read_back_context(CURRENT, ["a", "b", "c", "d", "e"], phrase="getting it", line_after=2)
    assert rungs == {"phrase": "getting it", "rungs": vs.numbered(["a", "b", "c", "d", "e"]), "line_after": 2}
    ladder = {"phrase": "getting it", "rungs": ["a", "b"], "line_after": 0}
    benefits = vs.read_back_context(RA, ["lead", "kept"], clause={"routine": "r"}, ladder=ladder)
    assert benefits["rows"] == vs.numbered(["lead", "kept"]) and benefits["clause"] == {"routine": "r"}
    assert benefits["ladder"]["rungs"] == [{"index": 0, "label": "a"}, {"index": 1, "label": "b"}]
    # a job queued before 243 handed words; both shapes read to the same labels
    assert vs.labels_of(rows) == vs.labels_of(STAGING) == STAGING
    with pytest.raises(vs.VectorsScriptError, match="236's"):
        vs.read_back_context(COMPAT, STAGING)


# ------------------------------------------------------------------------------- FR-2 the shift (243 FR-2)

def test_a_one_based_answer_is_read_shifted_and_a_zero_based_one_as_handed():
    """243 FR-2 (`shiftOf`): own + 3 handed, drops at 2, 3 and 4 -- the largest index equals the count, none is 0 --
    `review.shift: 1`; the same answer from 0 applies unchanged; each reading lands on its own row either way."""
    one = vs.read_back_answer(staging_answer(1), STAGING)
    zero = vs.read_back_answer(staging_answer(0), STAGING)
    assert one["shift"] == 1 and zero["shift"] == 0
    assert one["refused"] == zero["refused"] == []
    assert [(r["at"], r["note"]) for r in one["readings"]] == [(r["at"], r["note"]) for r in zero["readings"]] == \
        [(1, GAMES_WHY), (2, OVERTIME_WHY), (3, NEW_HIRE_WHY)]
    assert vs.review_shift([{"index": 0}, {"index": 3}], 4) == 0, "a 0 is never a 1-based answer"
    assert vs.review_shift([{"index": 1}, {"index": 3}], 4) == 0, "one that never names the last row is read as handed"
    assert vs.review_shift([], 4) == 0


def test_an_index_outside_both_readings_is_a_refusal_line():
    """243 FR-2: *index 7 is outside the 4 rows handed (0 to 3)* -- nothing applied for it, the rest as handed."""
    out = vs.read_back_answer({"notes": [note(0, None), note(1, GAMES_WHY, True, RECONCILING, "The longest step."),
                                         note(7, OVERTIME_WHY, True, RERUNNING, "A late input.")]}, STAGING)
    assert out["shift"] == 0
    assert out["refused"] == ["index 7 is outside the 4 rows handed (0 to 3)"]
    listed = vs.in_place_applied(STAGING, out["readings"], floor=3)
    assert [a["typed"] for a in listed["putAside"]] == [GAMES]
    assert [i["label"] for i in listed["items"]] == [OWN, RECONCILING, OVERTIME, NEW_HIRE]
    fixture = _cloud_fixture()
    if fixture is not None:
        assert '"index 7 is outside the 4 rows handed (0 to 3)"' in fixture


def test_the_notes_alone_are_read_shifted_onto_their_own_rows():
    """243 FR-2 (`readBackNotes`): the notes of a 1-based answer land each on the row it was written for."""
    said = vs.read_back_notes({"notes": [note(2, GAMES_WHY), note(3, OVERTIME_WHY), note(4, NEW_HIRE_WHY)]}, STAGING)
    assert said == [(GAMES, GAMES_WHY), (OVERTIME, OVERTIME_WHY), (NEW_HIRE, NEW_HIRE_WHY)]


# ------------------------------------------------------------------- FR-3 in place of each put aside (243 FR-3)

def test_the_staging_shape_puts_three_aside_with_a_keel_row_in_each_place():
    """243 FR-3 / FR-4 (`theStagingShape`): each reason on its own row, the three put aside in their order, a Keel row
    where each stood (`suggested`, `suggestedWhy`, `inPlaceOf`), `replacedBy` on the record, the band counting both."""
    listed = vs.in_place_applied(STAGING, vs.read_back_answer(staging_answer(1), STAGING)["readings"], floor=3)
    assert listed["refused"] == [] and listed["notes"] == []
    assert [i["label"] for i in listed["items"]] == [OWN, RECONCILING, RERUNNING, EXPLAINING]
    assert [vs.in_place_of(i) for i in listed["items"]] == [None, GAMES, OVERTIME, NEW_HIRE]
    assert all(i.get("suggested") and i.get("suggestedWhy") for i in listed["items"][1:])
    assert [(a["typed"], a["why"], a["replacedBy"]) for a in listed["putAside"]] == [
        (GAMES, GAMES_WHY, RECONCILING), (OVERTIME, OVERTIME_WHY, RERUNNING), (NEW_HIRE, NEW_HIRE_WHY, EXPLAINING)]
    assert vs.band_line(IMPORTANCE, listed) == STAGING_BAND
    assert vs.band_counts(STAGING_BAND) == {"changed": 0, "put_aside": 3, "in_place": 3}
    fixture = _cloud_fixture()
    if fixture is not None:
        assert '"Keel put three rows aside and suggested three in their place, so every row " + "sits at the moment ' \
               'your problem names."' in fixture


def test_the_notes_alone_keep_the_floor_the_last_rows_first():
    """243 FR-3 (`theNotesAloneLandOnTheirRows`): with no suggestion the floor of three holds -- video games put aside
    with its own reason, overtime and new hire kept with theirs as notes (never the row above's)."""
    answer = {"notes": [note(2, GAMES_WHY, True), note(3, OVERTIME_WHY, True), note(4, NEW_HIRE_WHY, True)]}
    listed = vs.in_place_applied(STAGING, vs.read_back_answer(answer, STAGING)["readings"], floor=3)
    assert listed["putAside"] == [{"typed": GAMES, "why": GAMES_WHY}]
    assert listed["notes"] == [{"row": OVERTIME, "note": OVERTIME_WHY}, {"row": NEW_HIRE, "note": NEW_HIRE_WHY}]
    assert vs.band_line(IMPORTANCE, listed) == NOTES_ALONE_BAND
    assert vs.band_counts(NOTES_ALONE_BAND) == {"changed": 0, "put_aside": 1, "in_place": 0}


def test_a_suggestion_is_refused_beside_no_drop_without_a_why_or_saying_a_row_again():
    """243 FR-3 (`ReviewedRows.held`): a suggestion beside no row put aside, with no why, or saying again a row as saved
    is a refusal line, and its drop keeps today's floor (the note alone)."""
    answer = {"notes": [note(1, "fine as it is", False, RECONCILING, "beside nothing"),
                        note(2, OVERTIME_WHY, True, RERUNNING, None),
                        note(3, NEW_HIRE_WHY, True, "playing  video games", "said again")]}
    listed = vs.in_place_applied(STAGING, vs.read_back_answer(answer, STAGING)["readings"], floor=3)
    assert listed["refused"][:3] == [
        f"suggest '{RECONCILING}' in place of '{GAMES}': beside no row put aside",
        f"suggest '{RERUNNING}' in place of '{OVERTIME}': no why: a row in another's place says why",
        f"suggest 'playing video games' in place of '{NEW_HIRE}': L14: 'playing video games' means what '{GAMES}' means"]
    assert not any(vs.in_place_of(i) for i in listed["items"])
    assert [a["typed"] for a in listed["putAside"]] == [OVERTIME], "the floor of three, the last row first"


def test_the_benefits_and_the_conditions_siblings():
    """243's siblings: the benefits (lead + 2, drops at 2 and 3 counted from 1 -- both put aside, a Keel benefit in each
    place) and the conditions (a row put aside at 2 counted from 1, the first row not fixed, the floor of two)."""
    benefits = ["Errors caught before the run", "No more checking by hand", "Fewer hours on the register"]
    answer = {"notes": [note(2, "Today's way already spares them it.", True, "No payslip explained after the run",
                             "Only the idea."),
                        note(3, "One gain with the first.", True, "Late corrections caught before they go out",
                             "Only the idea, in the hard case.")]}
    read = vs.read_back_answer(answer, benefits)
    assert read["shift"] == 1
    listed = vs.in_place_applied(benefits, read["readings"], floor=1)
    assert [i["label"] for i in listed["items"]] == [benefits[0], "No payslip explained after the run",
                                                     "Late corrections caught before they go out"]
    assert vs.band_line(RA, listed) == ("Keel put two benefits aside and suggested two in their place, so what is "
                                        "left is what only your idea would have given them.")
    conditions = ["could export the payroll register to a spreadsheet", "had a payroll system that keeps an audit trail",
                  "could see last month's register beside this month's"]
    answer = {"notes": [note(1, None), note(2, "Most of your segment already has this.", True,
                                             "were allowed to let an outside tool read the payroll register",
                                             "No row asks whether they may."), note(3, None)]}
    read = vs.read_back_answer(answer, conditions)
    assert read["shift"] == 1
    listed = vs.in_place_applied(conditions, read["readings"], floor=2, first_fixed=False)
    assert listed["putAside"][0]["replacedBy"] == "were allowed to let an outside tool read the payroll register"
    assert vs.band_line(COMPAT, listed) == ("Keel put one condition aside because your segment already has it, and "
                                            "suggested one in its place.")


# --------------------------------------------------------------------- the band reads both (243 FR-4)

@pytest.mark.parametrize("line, counts", [
    (STAGING_BAND, (0, 3, 3)),
    ("Keel changed one row, put two aside and suggested two in their place, so every row sits at the moment your "
     "problem names.", (1, 2, 2)),
    ("Keel put three rows aside and suggested two in their place, so the rest sit at the moment your problem names.",
     (0, 3, 2)),
    ("Keel put one benefit aside and suggested one in its place, so what is left is what only your idea would have "
     "given them, and changed the moment the question asks about so it is the one that went wrong.", (0, 1, 1)),
    ("Keel changed one condition so strangers are asked what they can do themselves, put one condition aside because "
     "your segment already has it, and suggested one in its place.", (1, 1, 1)),
    ("Keel changed one row and put one aside so the rest sit at the moment your problem names.", (1, 1, 0)),
    ("Keel changed three answers so they sit on one scale.", (3, 0, 0)),
    ("Keel rewrote the scale so every answer is a step in how long it took.", (0, 0, 0)),
    (None, (0, 0, 0)),
])
def test_the_band_counts_changed_put_aside_and_suggested_in_place(line, counts):
    """243 FR-4: the walk reads the served band's three counts off its words, 232's lines (none in place) and 243's."""
    assert tuple(vs.band_counts(line).values()) == counts


def test_the_band_mirror_is_243s_on_each_list():
    """243 FR-4 (`ReviewedRows.changed`): the line the mirror composes is the cloud's on a rewrite beside the pairs, and
    232's / 233's lines stand where nothing is in place."""
    mixed = {"items": [{"label": OWN}, {"label": "Re-checking the register", "typed": GAMES, "why": "w"},
                       {"label": RERUNNING, "suggested": True, "suggestedWhy": "x", "inPlaceOf": OVERTIME},
                       {"label": EXPLAINING, "suggested": True, "suggestedWhy": "y", "inPlaceOf": NEW_HIRE}],
             "putAside": [{"typed": OVERTIME, "why": "o"}, {"typed": NEW_HIRE, "why": "n"}]}
    assert vs.band_line(IMPORTANCE, mixed) == ("Keel changed one row, put two aside and suggested two in their place, "
                                               "so every row sits at the moment your problem names.")
    compat = {"items": [{"label": "a", "typed": "b"}, {"label": "c", "suggested": True, "suggestedWhy": "w",
                                                       "inPlaceOf": "d"}], "putAside": [{"typed": "d", "why": "s"}]}
    assert vs.band_line(COMPAT, compat) == ("Keel changed one condition so strangers are asked what they can do "
                                            "themselves, put one condition aside because your segment already has it, "
                                            "and suggested one in its place.")
    assert vs.band_line(IMPORTANCE, {"items": [{"label": "x", "typed": "y"}]}) == (
        "Keel changed one row so it sits at the moment your problem names.")
    assert vs.band_line(IMPORTANCE, {"items": [{"label": "x"}]}) is None


# ------------------------------------------------------------------ the record's words for a pair (contract 64)

def test_the_record_carries_in_place_of_and_replaced_by():
    """243 FR-4 on the bundle: `review_changed` gives the put-aside row its `replacedBy` (served, else read off the
    rows) and `keels`, a changed row its `typedKeels`; `review_in_place` lists Keel's rows with the row each stands for;
    `lists_reviewed` carries them; Keel's row in place is never the founder's words (`founder_words`, `as_drafted`)."""
    listed = vs.in_place_applied(STAGING, vs.read_back_answer(staging_answer(1), STAGING)["readings"], floor=3)
    served = {"items": listed["items"], "putAside": [{k: v for k, v in a.items() if k != "replacedBy"}
                                                     for a in listed["putAside"]],
              "changed": {"line": STAGING_BAND, "why": GAMES_WHY}}
    changed = vs.review_changed(served)
    assert [(c["typed"], c["label"], c.get("replacedBy")) for c in changed] == [
        (GAMES, None, RECONCILING), (OVERTIME, None, RERUNNING), (NEW_HIRE, None, EXPLAINING)], "read off the rows"
    assert vs.review_in_place(served) == [{"label": RECONCILING, "inPlaceOf": GAMES,
                                           "why": "The step at this moment that takes them the longest."},
                                          {"label": RERUNNING, "inPlaceOf": OVERTIME,
                                           "why": "What a late input costs them inside the run."},
                                          {"label": EXPLAINING, "inPlaceOf": NEW_HIRE,
                                           "why": "What an error turns into once the run has gone out."}]
    assert sorted(vs.founder_words(served)) == sorted(STAGING) == sorted(vs.as_drafted(served))
    view = {"PROBLEM": {"questions": [{"dimension": IMPORTANCE, "answer": {"list": served}}]}}
    reviewed = vs.lists_reviewed(view)[IMPORTANCE]
    assert reviewed["in_place"] == vs.review_in_place(served) and reviewed["band"]["line"] == STAGING_BAND
    keels = {"items": [{"label": "x", "typed": "y", "why": "w", "typedKeels": True}],
             "putAside": [{"typed": "z", "why": "s", "keels": True}]}
    assert vs.review_changed(keels) == [{"typed": "y", "label": "x", "why": "w", "typedKeels": True},
                                        {"typed": "z", "label": None, "why": "s", "keels": True}]
    # a list before 243 reads as 143 wrote it: no new key
    before = {"items": [{"label": "x", "typed": "y", "why": "w"}], "putAside": [{"typed": "z", "why": "s"}],
              "changed": {"line": "l", "why": "w"}}
    assert vs.review_changed(before) == [{"typed": "y", "label": "x", "why": "w"},
                                         {"typed": "z", "label": None, "why": "s"}]
    assert "in_place" not in vs.lists_reviewed({"P": {"questions": [{"dimension": IMPORTANCE,
                                                                       "answer": {"list": before}}]}})[IMPORTANCE]
