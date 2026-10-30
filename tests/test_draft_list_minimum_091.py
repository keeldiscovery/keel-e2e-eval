"""Spec 091 -- a drafted list is held to the draft's rule, not the save's: Importance's `L1` reads the registry's minimum
where it belongs.

FR-1 `option_validity`'s `L1` reads a drafted `rival_list` (Importance) against `founder-lists.md`'s own rule: with no
founder Answer the problem itself alone (one item), with an Answer naming N difficulties the problem itself and those N
(1 + N, at most `saves.max_items`); `saves.min_items` is the save's rule, applied where a saved list is checked
(`corpus._check_list`), never to a draft.
"""

from __future__ import annotations

import types

import pytest

from instructions import corpus as corpus_mod
from instructions import score as score_mod
from tests import v9_fixtures as fx

IMPORTANCE = "problem.importance"


def _faults(items, answers=None):
    labels = [{"label": label} for label in items]
    return score_mod.list_faults({"key": IMPORTANCE, "list": {"items": labels}}, fx.registry().by_key(IMPORTANCE),
                                 answers=answers)


def _l1(faults):
    return [f for f in faults if f.startswith("L1:")]


#: The 03-lullaby PROBLEM drafts the two founder-lists screens recorded (`runs/20261030T111940Z-instructions`,
#: `runs/20261029T193750Z-instructions`, runs 1-3): each the problem itself alone, as `answers` `{}` asks -- every one
#: faulted *takes 2 to 5 items, and 1 were written* by the save's rule (spec 091's subject).
RECORDED = ("Working out what the cry means", "Guessing why the baby is crying", "Guessing what the baby needs",
            "Figuring out what the cry means")


@pytest.mark.parametrize("own", RECORDED)
def test_the_recorded_draft_with_no_answer_is_valid(own):
    """FR-1: the faulted case scores clean -- one item, no founder Answer (the registry's `saves.min_items` is the
    save's, not the draft's)."""
    assert _faults([own]) == []
    assert _faults([own], answers={}) == []


def test_the_recorded_problem_run_scores_four_of_four():
    """FR-1's acceptance on 03-lullaby: the PROBLEM job with the recorded Importance draft is 4 of 4 valid."""
    lullaby = corpus_mod.load_file(fx.canon_entry("03-lullaby.yaml"), registry=fx.registry())
    result = fx.calibration_result(fx.registry(), "PROBLEM")
    next(q for q in result["questions"] if q["key"] == IMPORTANCE)["list"] = {"items": [{"label": RECORDED[0]}]}
    score = score_mod.score_calibration(fx.calibration_case(lullaby, "PROBLEM"), lullaby, fx.registry(), result,
                                        judge=fx.FakeJudge())
    assert not [f for f in score.faults if f["check"] == "option_validity"], score.faults
    assert (score.validity_hit, score.validity_of) == (4, 4)


def test_a_rival_keel_adds_with_no_answer_is_faulted_by_the_drafts_rule():
    """FR-1: with `answers` `{}` Keel adds none -- a second item is an `L1`, named as the draft's rule."""
    assert _l1(_faults([RECORDED[0], "Getting them back to sleep"])) == [
        "L1: problem.importance takes exactly 1 item (the problem itself alone, with no founder Answer), and 2 were "
        "written"]
    assert _l1(_faults([]))[0].startswith("L1: problem.importance takes exactly 1 item")


def test_an_answer_naming_n_is_the_problem_itself_and_those_n():
    """FR-1: an Answer naming two difficulties is three items -- the problem itself, then the two."""
    answers = {IMPORTANCE: "Getting them back to sleep; Knowing if they are hungry"}
    assert _faults([RECORDED[0], "Getting them back to sleep", "Knowing if they are hungry"], answers) == []


def test_a_draft_that_writes_fewer_than_its_answer_names_is_still_faulted():
    """FR-1: the right rule, not the save's -- two named, one written: *exactly 3*, naming the Answer's two."""
    answers = {IMPORTANCE: "Getting them back to sleep, knowing if they are hungry"}
    assert _l1(_faults([RECORDED[0], "Getting them back to sleep"], answers)) == [
        "L1: problem.importance takes exactly 3 items (the problem itself and the 2 difficulties the founder's Answer "
        "names), and 2 were written"]
    assert _l1(_faults([RECORDED[0]], answers)), "the own item alone drops what the founder named"


def test_a_draft_that_adds_to_its_answer_is_faulted():
    """`founder-lists.md`: *Add none: an answer naming one difficulty yields two items.*"""
    answers = {IMPORTANCE: "Getting them back to sleep"}
    assert _faults([RECORDED[0], "Getting them back to sleep"], answers) == []
    assert _l1(_faults([RECORDED[0], "Getting them back to sleep", "Feeding at night"], answers)) == [
        "L1: problem.importance takes exactly 2 items (the problem itself and the 1 difficulty the founder's Answer "
        "names), and 3 were written"]


def test_an_answer_naming_none_leaves_the_own_item():
    """keel-cloud 097 F9: an Answer naming no other difficulty leaves the problem itself alone."""
    answers = {IMPORTANCE: "Nothing else"}
    assert _faults([RECORDED[0]], answers) == []
    assert _l1(_faults([RECORDED[0], "Feeding at night"], answers))[0].endswith(
        "(the problem itself alone: the founder's Answer names no other), and 2 were written")


def test_an_answer_naming_more_than_the_list_holds_is_capped_at_max_items():
    """FR-1: 1 + N, at most `saves.max_items` (the fixture registry's 5)."""
    answers = {IMPORTANCE: "A one; B two; C three; D four; E five; F six"}
    assert fx.registry().by_key(IMPORTANCE).saves["max_items"] == 5
    assert _faults([RECORDED[0], "A one", "B two", "C three", "D four"], answers) == []
    assert _l1(_faults([RECORDED[0], "A one", "B two"], answers))[0].startswith(
        "L1: problem.importance takes exactly 5 items")


@pytest.mark.parametrize("answer, named", [
    ("Getting them back to sleep; Knowing if they are hungry", 2),
    ("Getting them back to sleep, knowing if they are hungry and feeding at night", 3),   # a serial list's last *and*
    ("Settling the baby and finding the bottle", 1),                                      # a lone *and*: one
    ("- Feeding at night\n- Getting them back to sleep", 2),
    (["Feeding at night", "Getting them back to sleep"], 2),
    ("Nothing else.", 0),
    ("", 0),
])
def test_the_answers_difficulties_are_read_off_its_parts(answer, named):
    assert len(score_mod.named_difficulties(answer)) == named


def test_another_list_keeps_the_registrys_bounds():
    """FR-1 moves Importance's draft alone: Compatibility's draft is still 2 to 4 (`saves`)."""
    compat = "solution.compatibility"
    one = {"items": fx.GOOD_LISTS[compat]["items"][:1]}
    faults = score_mod.list_faults({"key": compat, "list": one}, fx.registry().by_key(compat))
    assert "L1: solution.compatibility takes 2 to 4 items, and 1 were written" in faults


def test_the_saved_list_is_still_held_to_min_items():
    """FR-1: `saves.min_items` is applied where a saved list is checked -- the corpus's recorded lists
    (`corpus._check_list`): a saved Importance of one item is refused."""
    registry = fx.registry()
    low = registry.by_key(IMPORTANCE).saves["min_items"]
    saved = {"items": [{"code": "own", "label": RECORDED[0]}], "picked": None}
    entry = types.SimpleNamespace(id="91-fixture", path="91-fixture.yaml", founder_list=lambda key: saved)
    with pytest.raises(corpus_mod.CorpusError, match=rf"lists 1 items; the registry saves {low} to"):
        corpus_mod._check_list(entry, registry, IMPORTANCE)


def test_the_marks_version_moved_with_its_note():
    """FR-4: `option_validity`'s reading moved (Importance's draft count), so MARKS_VERSION moved with its note (calls
    127-128) and the marks file's header; `OLDEST` stays 20."""
    from instructions import marks as marks_mod                             # noqa: PLC0415
    from instructions import rescore as rescore_mod                         # noqa: PLC0415
    assert marks_mod.MARKS_VERSION == 23 and rescore_mod.OLDEST == 20
    assert "127. **v23**" in marks_mod.__doc__ and "128. **v23**" in marks_mod.__doc__
    assert "**`MARKS_VERSION` 23** (spec 091" in marks_mod.__doc__
    assert "MARKS_VERSION 23 (judgement calls 127-128" in marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")


# --------------------------------------------------------------------- FR-3: IM2 and the lock screen's credits line

def _lock(uses: str) -> str:
    """keel-web `beforeInterviewerSub` (130 FR-2, 132 FR-1) as L1 draws it, the title and the button around it."""
    return ("Who should ask them your questions? Daphne is picked for you. Tap the other face to hear Saskia and pick "
            f"Saskia instead. Keel records Daphne once for this project, which uses {uses}. People get the link by text "
            "message either way. The voice goes with the face. Lock and record Daphne")


@pytest.mark.parametrize("uses", ["400 credits", "Keel's credits"])
def test_the_lock_screens_credits_sentence_is_the_screens_own_words(uses):
    """FR-3: *uses 400 credits* (132) and *uses Keel's credits* (130, the faceless fallback) are L1's own sentence."""
    from evals import interviewer_marks as im                              # noqa: PLC0415
    assert im.PRICE_WORD.search(_lock(uses)), "the word IM2 caught before v15"
    assert im.price_words_on("L1", _lock(uses)) == []
    assert im.price_words_on("L1", "Keel records them once for this project, which uses Keel's credits.") == []


def test_the_credits_sentence_holds_the_served_price_and_no_currency():
    """FR-3: no number the founder typed (the sentence's number is the served `changePrice`), no currency, one line."""
    from evals import interviewer_marks as im                              # noqa: PLC0415
    assert im.price_words_on("L1", _lock("1,250 credits"))[0] == "1,250 credits is not the served price [400]"
    assert im.price_words_on("L1", _lock("1,250 credits"), {1250}) == [], "the price the wire served"
    assert "$" in im.price_words_on("L1", _lock("400 credits") + " A $2 render.")
    twice = _lock("400 credits") + " Keel records Daphne once for this project, which uses 400 credits."
    assert im.price_words_on("L1", twice)[0].startswith("a second credits sentence")
    assert im.price_words_on("L1", "Who asks the questions · 400 credits") == ["credits"], "outside the sentence"
    assert im.price_words_on("L1", _lock("400 credits") + " Your price is set.") == ["price"]


def test_the_sentence_is_read_on_l1_alone():
    """FR-3: S1 and S3 read as before -- the credits sentence on any other screen is a price word."""
    from evals import interviewer_marks as im                              # noqa: PLC0415
    assert im.price_words_on("S1", _lock("400 credits")) == ["credits"]
    assert im.price_words_on("S2", f"Recorded today at 16:02. {im.CHANGE_ACTION}") == []


def test_im2_passes_the_lock_screen_as_served_and_the_version_moved():
    """FR-3: IM2 on a record whose L1 is 132's screen is met, and names the sentence it read;
    `INTERVIEWER_MARKS_VERSION` 14 -> 15 with its note."""
    from evals import interviewer_marks as im                              # noqa: PLC0415
    record = {"screens": {"L1": _lock("400 credits"), "S1": "Saskia asks your questions.",
                          "S2": f"Recorded today at 16:02. {im.CHANGE_ACTION}", "S3": "AI interviewer · Saskia"},
              "wire_views": [{"changePrice": 400}]}
    ok, detail = im.no_price_shown(record)
    assert ok, detail
    assert detail["L1 credits sentence"] == "Keel records Daphne once for this project, which uses 400 credits."
    assert im.INTERVIEWER_MARKS_VERSION == 15
    import inspect                                                          # noqa: PLC0415
    assert "#: v15 (spec 091 FR-3" in inspect.getsource(im)


def test_the_journeys_l1_no_price_step_reads_the_same_helper():
    """FR-3: the leg's *L1 revisited ... no price on it* reads `price_words_on`, not the bare `PRICE_WORD`."""
    import inspect                                                          # noqa: PLC0415
    from evals import interviewer_leg                                       # noqa: PLC0415
    src = inspect.getsource(interviewer_leg)
    assert 'marks.price_words_on("L1", l1["text"])' in src
    assert 'marks.PRICE_WORD.search(l1["text"])' not in src
