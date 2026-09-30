"""The rubric's own constants (spec 025 FR-001 to FR-004, T010).

Two things this holds, and neither needs a model, a stack or a corpus:

**The judgement-call list is append-only and complete.** It is the history of what a number means,
so a missing entry is not a formatting slip -- judgement call 23 was cited by `marks.toml` from v7
and absent from `marks.py`'s list until v8 transcribed it back in, and nothing but a test noticed.

**No number in `marks.toml` moves at v8.** `model-routing-design.md` §7 step 3: *"The marks are not
touched. A candidate that misses a mark is not the table's problem; the prompt or the model changes,
never the number."* The rubric moved three ways at v8 and the five numbers are the ones v7 judged by.
"""

from __future__ import annotations

import re

from instructions import marks as marks_mod

#: Every mark, at its value on `master` `aa3b584` -- v7's numbers, written out rather than read out
#: of the file they are checking.
V7_MARKS = {
    "anchoring_accuracy": 0.90,
    "golden_belief_recall": 0.80,
    "rule_refusal_rate": 0.02,
    "shape_refusals": 0,
    "brief_paragraphs": 1.00,
}


def judgement_calls() -> list:
    """The numbers of the calls in `marks.py`'s module docstring, in the order they are written."""
    return [int(n) for n in re.findall(r"^(\d+)\.\s", marks_mod.__doc__, re.M)]


def test_marks_version_is_eight():
    assert marks_mod.MARKS_VERSION == 8


def test_the_judgement_calls_are_one_to_twenty_seven_with_none_missing():
    numbers = judgement_calls()
    assert sorted(numbers) == list(range(1, 28)), \
        "the list is append-only: 1-27, none struck, none renumbered"
    assert len(numbers) == len(set(numbers)), "no judgement call is written twice"


def test_the_four_v8_calls_are_appended_and_say_what_they_are():
    body = marks_mod.__doc__
    for number in (24, 25, 26, 27):
        assert re.search(rf"^{number}\. \*\*v8", body, re.M), f"{number} is not marked v8"
    assert "bare `anchorId`" in body                       # 24
    assert "`stages`, a list" in body                      # 25
    assert "reads another belief's measurement" in body    # 26
    assert "align.resolve_reads" in body                   # 27


def test_judgement_call_23_was_transcribed_and_is_v7():
    assert re.search(r"^23\. \*\*v7\*\*", marks_mod.__doc__, re.M), \
        "23 is v7's, transcribed at v8 from marks.toml (FR-003) -- it is not a new call"


def test_no_number_in_the_marks_table_moved():
    assert marks_mod.load() == V7_MARKS
    assert marks_mod.DEFAULTS == V7_MARKS


def test_the_marks_file_says_the_scores_are_not_comparable_across_the_bump():
    text = (marks_mod.DEFAULT_MARKS_PATH).read_text(encoding="utf-8")
    assert "MARKS_VERSION 8" in text
    assert "not comparable" in text
    assert "cannot be re-scored" in text, \
        "the corpus moved, so rescore.py is not an escape hatch across this bump"
