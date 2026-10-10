"""The rubric's own constants at `MARKS_VERSION` 11 (spec 029 FR-001 to FR-003, SC-001; T008; spec 030
FR-003, T010: judgement calls 46-49; spec 031 FR-005, T010: judgement calls 50-58).

Three things this holds, and none needs a model, a stack or a corpus:

**The judgement-call list is append-only and complete.** It is the history of what a number means.
Calls 1-27 are byte for byte what `master` `0165017` carried (`tests/fixtures/marks/
calls-1-27.at-0165017.txt`, extracted once), and 28-36 are marks-v9 §3's, each marked `**v9**`. The
list is a set, not a sorted run: call 22 sits between 16 and 17, where it was written (025 D7).
46-49 are spec 030's, each marked `**v10**`; 50-58 spec 031's, each marked `**v11**`.

**`marks.toml` carries the v11 header** and `DEFAULTS` follows it: eight keys, no
`golden_belief_recall` and no `no_claim_words` -- a verdict cannot carry a value for a retired mark,
and both are struck through in a comment.

**An unmeasured mark is not a met mark** (call 13), on every one of the eight rows.
"""

from __future__ import annotations

import re
from pathlib import Path

from instructions import marks as marks_mod

ROOT = Path(__file__).resolve().parent.parent
CALLS_1_27 = Path(__file__).parent / "fixtures" / "marks" / "calls-1-27.at-0165017.txt"

V9_MARKS = {"dimension_coverage": 1.00, "option_validity": 1.00, "no_leak": 1.00,
            "anchoring_accuracy": 0.90, "compare_correctness": 1.00, "rule_refusal_rate": 0.02,
            "shape_refusals": 0, "brief_paragraphs": 1.00}


def judgement_calls() -> list:
    return [int(n) for n in re.findall(r"^(\d+)\.\s", marks_mod.__doc__, re.M)]


def test_marks_version_is_eleven():
    assert marks_mod.MARKS_VERSION == 11


def test_the_judgement_calls_are_one_to_fifty_eight_with_none_missing_and_none_twice():
    numbers = judgement_calls()
    assert sorted(numbers) == list(range(1, 59)), "append-only: 1-58, none struck or renumbered"
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


def test_the_four_v10_calls_are_marked_and_say_what_they_are():
    body = marks_mod.__doc__
    phrases = {46: "twelve, calibrated and asked alike", 47: "per link and per persona",
               48: "`no_claim_words` retires", 49: "corpus revision 4"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v10\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v10"
        said = " ".join(match.group(1).split())
        assert phrase in said, f"{number} does not carry {phrase!r}"


def test_the_nine_v11_calls_are_marked_and_say_what_they_are():
    body = marks_mod.__doc__
    phrases = {50: "the registry is thirteen", 51: "corpus revision 5", 52: "the window is code's",
               53: "Price is code's on both sides", 54: "the money, the hint and the unit",
               55: "held only to a name the corpus records", 56: "reported, never marked",
               57: "the brief's commercial figures are keel-cloud's",
               58: "refuses every bundle below 11"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v11\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v11"
        said = " ".join(match.group(1).split())
        assert phrase in said, f"{number} does not carry {phrase!r}"


def test_the_marks_file_carries_the_v11_header_and_no_run_of_record_yet():
    """Spec 031 FR-005: the v11 header above v10's, the denominators' comments, and *run of record:
    none yet* -- the run on hold by the founder."""
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert text.index("MARKS_VERSION 11") < text.index("MARKS_VERSION 10") < \
        text.index("MARKS_VERSION 9")
    assert "Run of record: none yet" in text and "WHY=marks:11" in text
    assert "ON HOLD by the founder" in text
    assert "11 (B2C) / 13 (B2B)" in text and "104" in text


def test_the_v10_header_stays_as_history():
    """FR-003 at v10, kept: `no_claim_words` struck through as `golden_belief_recall` is."""
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert "MARKS_VERSION 10 (history" in text
    assert re.search(r"^#\s+golden_belief_recall = 0\.80", text, re.M)
    assert re.search(r"^#\s+no_claim_words\b", text, re.M)
    assert not re.search(r"^no_claim_words\s*=", text, re.M)
    assert "10 on a B2C entry, 12 on a B2B one" in text


def test_the_eight_marks_and_no_golden_belief_recall():
    assert marks_mod.load() == V9_MARKS
    assert marks_mod.DEFAULTS == V9_MARKS
    assert "golden_belief_recall" not in marks_mod.DEFAULTS


def test_the_marks_file_says_the_scores_are_not_comparable_across_the_bump():
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert "MARKS_VERSION 11" in text
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


def test_the_v11_header_names_the_seven_r5_digests_and_the_counted_denominators():
    """Spec 031 US2: one dated paragraph above the call list -- never a call, never a line of
    `marks.toml`. The digests are keel-cloud's canon's own bytes (skipped by name when the
    configured keel-cloud is not at revision 5); v10's paragraph stays below it as history."""
    import hashlib                                                          # noqa: PLC0415
    from tests import v9_fixtures as fx                                     # noqa: PLC0415
    doc = marks_mod.__doc__
    header = doc[:doc.index("1.  **v1**")]
    names = ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly",
             "06-repeatline", "07-mulchrun")
    for name in names:
        path = fx.canon_entry(f"{name}.yaml")
        assert hashlib.sha256(path.read_bytes()).hexdigest() in header, name
    assert "65 reads at N=1" in header
    assert "135 model cases at N=1" in header and "**104**" in header and "**97**" in header
    assert "The corpus v11 judges, recorded 2026-10-09" in header
    assert "no v11\nrun of record until `WHY=marks:11` is spent" in header
    assert "46 sweep-A and 71 sweep-B" in header
