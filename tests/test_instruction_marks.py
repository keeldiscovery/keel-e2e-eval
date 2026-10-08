"""The rubric's own constants at `MARKS_VERSION` 9 (spec 029 FR-001 to FR-003, SC-001; T008).

Three things this holds, and none needs a model, a stack or a corpus:

**The judgement-call list is append-only and complete.** It is the history of what a number means.
Calls 1-27 are byte for byte what `master` `0165017` carried (`tests/fixtures/marks/
calls-1-27.at-0165017.txt`, extracted once), and 28-36 are marks-v9 §3's, each marked `**v9**`. The
list is a set, not a sorted run: call 22 sits between 16 and 17, where it was written (025 D7).

**`marks.toml` is the draft, byte for byte,** and `DEFAULTS` follows it: eight keys and no
`golden_belief_recall` -- a v9 verdict cannot carry a value for a retired mark.

**An unmeasured mark is not a met mark** (call 13), on every one of the eight rows.
"""

from __future__ import annotations

import re
from pathlib import Path

from instructions import marks as marks_mod

ROOT = Path(__file__).resolve().parent.parent
CALLS_1_27 = Path(__file__).parent / "fixtures" / "marks" / "calls-1-27.at-0165017.txt"
DRAFT_TOML = ROOT / "specs" / "029-marks-v9-vectors" / "contracts" / "marks-v9.toml"

V9_MARKS = {"dimension_coverage": 1.00, "option_validity": 1.00, "no_leak": 1.00,
            "anchoring_accuracy": 0.90, "compare_correctness": 1.00, "rule_refusal_rate": 0.02,
            "shape_refusals": 0, "brief_paragraphs": 1.00}


def judgement_calls() -> list:
    return [int(n) for n in re.findall(r"^(\d+)\.\s", marks_mod.__doc__, re.M)]


def test_marks_version_is_nine():
    assert marks_mod.MARKS_VERSION == 9


def test_the_judgement_calls_are_one_to_forty_one_with_none_missing_and_none_twice():
    numbers = judgement_calls()
    assert sorted(numbers) == list(range(1, 42)), "append-only: 1-41, none struck or renumbered"
    assert len(numbers) == len(set(numbers)), "no judgement call is written twice"


def test_calls_one_to_twenty_seven_are_byte_for_byte_v8s():
    doc = marks_mod.__doc__
    frozen = CALLS_1_27.read_text(encoding="utf-8")
    start = doc.index("1.  **v1**")
    end = doc.index("28. **v9**")
    assert doc[start:end] == frozen, "SC-001: calls 1-27 unchanged, byte for byte"


def test_the_nine_v9_calls_are_marked_and_say_what_they_are():
    body = marks_mod.__doc__
    phrases = {28: "New subjects", 29: "retired", 30: "absolute", 31: "fixes the codes",
               32: "golden mechanism", 33: "One anchoring judgement", 34: "spends nothing",
               35: "no_claim_words", 36: "keeps 0.02"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v9\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v9"
        said = " ".join(match.group(1).split())          # a phrase may wrap across lines
        assert phrase in said, f"{number} does not carry {phrase!r}"
    assert "amended 2026-10-07" in re.search(r"^33\. .*?(?=^34\. )", body, re.M | re.S).group(0)


def test_the_marks_file_is_the_draft_byte_for_byte():
    assert marks_mod.DEFAULT_MARKS_PATH.read_bytes() == DRAFT_TOML.read_bytes(), "FR-002"


def test_the_eight_marks_and_no_golden_belief_recall():
    assert marks_mod.load() == V9_MARKS
    assert marks_mod.DEFAULTS == V9_MARKS
    assert "golden_belief_recall" not in marks_mod.DEFAULTS


def test_the_marks_file_says_the_scores_are_not_comparable_across_the_bump():
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert "MARKS_VERSION 9" in text
    assert "not comparable" in text
    assert "cannot be re-scored" in text


def _all_met_totals() -> dict:
    return {"dimension_coverage": 1.0, "option_validity": 1.0, "no_leak": 1.0,
            "anchoring_accuracy": 0.95, "compare_correctness": 1.0, "compare_measured": True,
            "refusals_by_rule": {}, "refusals_measured": True, "refusals_shown": 50,
            "shape_refusals": 0, "brief_paragraphs": 1.0, "brief_measured": True}


def test_judge_returns_the_eight_rows_each_measured_and_met():
    judged = marks_mod.judge(_all_met_totals(), marks_mod.load())
    assert [k for k in judged if k != "passed"] == list(marks_mod.ROWS)
    for name in marks_mod.ROWS:
        assert set(judged[name]) >= {"value", "mark", "measured", "met"}
        assert judged[name]["measured"] and judged[name]["met"], name
    assert judged["passed"] is True
    assert "golden_belief_recall" not in judged


def test_one_unmeasured_mark_fails_the_run_and_says_so_on_its_row():
    for name, unset in (("no_leak", {"no_leak": None}),
                        ("compare_correctness", {"compare_measured": False}),
                        ("refusals", {"refusals_measured": False}),
                        ("brief_paragraphs", {"brief_measured": False})):
        totals = {**_all_met_totals(), **unset}
        judged = marks_mod.judge(totals, marks_mod.load())
        assert judged["passed"] is False, name
        assert judged[name]["measured"] is False and judged[name]["met"] is False, name


def test_the_refusal_mark_is_a_rate_over_the_answers_judged():
    totals = {**_all_met_totals(), "refusals_by_rule": {"C3": 1}, "refusals_shown": 50}
    row = marks_mod.judge(totals, marks_mod.load())["refusals"]
    assert row["value"] == 0.02 and row["count"] == 1 and row["met"] is True
    totals["refusals_by_rule"] = {"C3": 2}
    assert marks_mod.judge(totals, marks_mod.load())["refusals"]["met"] is False


def test_the_v9_header_names_the_seven_r3_digests_and_the_counted_denominator():
    """US4.2, O-4: one dated paragraph above the call list -- never a call, never a line of
    `marks.toml`. The digests are the recorded revision's own bytes."""
    import hashlib                                                          # noqa: PLC0415
    from instructions import corpus as corpus_mod                           # noqa: PLC0415
    doc = marks_mod.__doc__
    header = doc[:doc.index("1.  **v1**")]
    files = sorted(Path(corpus_mod.FIXTURE_DIR).glob("*.yaml"))
    assert len(files) == 7
    for path in files:
        assert hashlib.sha256(path.read_bytes()).hexdigest() in header, path.name
    assert "65 reads at N=1" in header
    assert "recorded 2026-10-07" in header
