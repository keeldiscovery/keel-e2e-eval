"""The rubric's own constants at `MARKS_VERSION` 21 (spec 078, calls 121-123: the `read` mark kind, reported, never
gating; spec 029 FR-001 to FR-003, SC-001; T008; spec 030
FR-003, T010: judgement calls 46-49; spec 031 FR-005, T010: judgement calls 50-58; spec 032 FR-005,
T007: judgement calls 59-66; spec 033, calls 67-70; ...; spec 040, calls 77-90; spec 042, calls 110-115; spec 052,
calls 116-120 --
91-109 are spec 041's journey calls, which read no mark and are written in its spec, not here).

Three things this holds, and none needs a model, a stack or a corpus:

**The judgement-call list is append-only and complete.** It is the history of what a number means.
Calls 1-27 are byte for byte what `master` `0165017` carried (`tests/fixtures/marks/
calls-1-27.at-0165017.txt`, extracted once), and 28-36 are marks-v9 §3's, each marked `**v9**`. The
list is a set, not a sorted run: call 22 sits between 16 and 17, where it was written (025 D7).
46-49 are spec 030's, each marked `**v10**`; 50-58 spec 031's, each marked `**v11**`; 59-66 spec
032's, each marked `**v12**`; 67-70 spec 033's, each marked `**v13**`.

**`marks.toml` carries the v20 header** and `DEFAULTS` follows it: ten keys -- v19's ten with `brief_answers` retired
(call 116, keel-cloud 104 deleted the BRIEF screen) and `report_overview` born (call 117) -- no
`golden_belief_recall`, no `no_claim_words`, no `brief_paragraphs` and no `brief_answers`: a verdict cannot carry a
value for a retired mark.

**An unmeasured mark is not a met mark** (call 13), on every one of the ten rows.
"""

from __future__ import annotations

import re
from pathlib import Path

from instructions import marks as marks_mod

ROOT = Path(__file__).resolve().parent.parent
CALLS_1_27 = Path(__file__).parent / "fixtures" / "marks" / "calls-1-27.at-0165017.txt"

V20_MARKS = {"dimension_coverage": 1.00, "option_validity": 1.00, "no_leak": 1.00,
             "anchoring_accuracy": 0.90, "compare_correctness": 1.00, "rule_refusal_rate": 0.02,
             "shape_refusals": 0, "spoken_form": 1.00, "brief_facts": 1.00, "report_overview": 1.00}


def judgement_calls() -> list:
    return [int(n) for n in re.findall(r"^(\d+)\.\s", marks_mod.__doc__, re.M)]


def test_marks_version_is_twenty_one():
    assert marks_mod.MARKS_VERSION == 21


def test_the_judgement_calls_are_one_to_ninety_and_110_to_123_with_none_missing_and_none_twice():
    """91-109 are spec 041's journey calls (they read no mark; `specs/041-vectors-journey-r10/spec.md`), so the
    rubric's list resumes at 110 (spec 042); 116-120 are spec 052's, 121-123 spec 078's."""
    numbers = judgement_calls()
    assert sorted(numbers) == list(range(1, 91)) + list(range(110, 124)), \
        "append-only: 1-90 and 110-123, none struck or renumbered"
    assert len(numbers) == len(set(numbers)), "no judgement call is written twice"
    assert "Calls 91-109 are spec 041's" in marks_mod.__doc__


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


def test_the_eight_v12_calls_are_marked_and_say_what_they_are():
    body = marks_mod.__doc__
    phrases = {59: "the registry is thirteen, cost first", 60: "corpus revision 6",
               61: "the code-framed questions owe no model text", 62: "`W10`",
               63: "the commercial slice is read as cost first",
               64: "the cost figures are keel-cloud's", 65: "the time-only are reported, not marked",
               66: "refuses every bundle below 12"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v12\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v12"
        said = " ".join(match.group(1).split())
        assert phrase in said, f"{number} does not carry {phrase!r}"


def test_the_eight_v13_calls_are_marked_and_say_what_they_are():
    body = marks_mod.__doc__
    phrases = {67: "Existing sacrifice is code's whole on both screens", 68: "corpus revision 7",
               69: "the registry reader at `cost_total`", 70: "refuses every bundle below 13"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v13\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v13"
        said = " ".join(match.group(1).split())
        assert phrase in said, f"{number} does not carry {phrase!r}"
    retired = " ".join(re.search(r"^67\. \*\*v13\*\*(.*?)(?=^\d+\. )", body, re.M | re.S).group(1).split())
    assert "`W10` retires" in retired and "`U1` retires" in retired


def test_the_three_v14_calls_are_marked_and_say_what_they_are():
    body = marks_mod.__doc__
    phrases = {71: "the BRIEF result is a reading, not a paragraph", 72: "five marks",
               73: "refuses every bundle below 14"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v14\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v14"
        assert phrase in " ".join(match.group(1).split()), f"{number} does not carry {phrase!r}"


def test_the_twelve_v18_calls_are_marked_and_say_what_they_are():
    body = marks_mod.__doc__
    phrases = {77: "registry 4: all thirteen decide", 78: "corpus revision 10", 79: "`spoken_form`, a deterministic mark",
               80: "three-word option floor", 81: "five corpus wording items are known",
               82: "the brief is answered, and its facts are compared",
               83: "writes the gate's clause and nothing else", 84: "eight screens: `ASKED` is a subject",
               85: "the founder-lists job, marked by code", 86: "an `L` refusal is a rule",
               87: "`ASKED` is redrawn like the question screens", 88: "refuses every bundle below 18", 89: "skip by name at revision 10",
               90: "read off the call that judges it"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v18\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v18"
        assert phrase in " ".join(match.group(1).split()), f"{number} does not carry {phrase!r}"
    said = " ".join(re.search(r"^79\. .*?(?=^80\. )", body, re.M | re.S).group(0).split())
    assert "25 on Existing sacrifice and Relative advantage" in said and "until the founder decides" in said
    said = " ".join(re.search(r"^82\. .*?(?=^83\. )", body, re.M | re.S).group(0).split())
    assert "`brief_paragraphs` retires" in said and "94 checks" in said


def test_the_six_v19_calls_are_marked_and_say_what_they_are():
    body = marks_mod.__doc__
    phrases = {110: "corpus revision 11, read from keel-cloud's canon only", 111: "holds every stem to 20 words",
               112: "no corpus item is known apart", 113: "an `L` refusal is a rule, as the validator reports it",
               114: "`brief_facts` reads keel-cloud 091's words", 115: "refuses every bundle below 19"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v19\*\*(.*?)(?=^\d+\. |^Calls |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v19"
        assert phrase in " ".join(match.group(1).split()), f"{number} does not carry {phrase!r}"
    said = " ".join(re.search(r"^110\. .*?(?=^111\. )", body, re.M | re.S).group(0).split())
    assert "revision 10 is v18's" in said and "`K3`" in said and "`S10`" in said and "108 of 108" in said


def test_the_five_v20_calls_are_marked_and_say_what_they_are():
    body = marks_mod.__doc__
    phrases = {116: "the reading marks retire, deleted, not skipped", 117: "`report_overview` is the Overview, read twice",
               118: "refuses every bundle below 20", 119: "`brief_facts` reads keel-cloud 103 / 104's numbers",
               120: "four report marks are the journey's, not the instruction eval's"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v20\*\*(.*?)(?=^\d+\. |^Calls |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v20"
        assert phrase in " ".join(match.group(1).split()), f"{number} does not carry {phrase!r}"
    said = " ".join(re.search(r"^120\. .*?(?=^121\. |^Calls |\Z)", body, re.M | re.S).group(0).split())
    for mark in ("`report_insights`", "`report_no_repeat`", "`report_pilot`", "`report_binding`", "**tokens**"):
        assert mark in said, mark


def test_the_three_v21_calls_are_marked_and_say_what_they_are():
    """Spec 078 FR-7: `read` is a mark kind, reported from committed score files and never gating."""
    body = marks_mod.__doc__
    phrases = {121: "`read` is a mark kind, reported and never gating", 122: "the readers' ruler is versioned apart",
               123: "`rescore.py` still re-scores a v20 bundle"}
    for number, phrase in phrases.items():
        match = re.search(rf"^{number}\. \*\*v21\*\*(.*?)(?=^\d+\. |^Calls |\Z)", body, re.M | re.S)
        assert match, f"{number} is not marked v21"
        assert phrase in " ".join(match.group(1).split()), f"{number} does not carry {phrase!r}"
    assert "read" not in marks_mod.ROWS and "read" not in marks_mod.DEFAULTS, "reported, never a row of judge()"


def test_the_marks_file_carries_the_v21_header_and_the_read_table():
    import tomllib
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert text.index("MARKS_VERSION 21") < text.index("MARKS_VERSION 20") < text.index("MARKS_VERSION 19")
    assert "WHY=marks:21" in text
    raw = tomllib.loads(text)
    assert raw["read"] == {"kind": "read", "source": "quality/scores", "gating": False, "bar_pct": 90}
    assert "read" not in marks_mod.load(), "load() reads [marks] alone: a verdict carries no value for `read`"


def test_the_v17_call_is_marked_and_says_what_it_is():
    body = marks_mod.__doc__
    match = re.search(r"^76\. \*\*v17\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
    assert match, "76 is not marked v17"
    said = " ".join(match.group(1).split())
    for phrase in ("`{answer: positive | neutral | negative, advantages: [...]}`", "CODE_WRITTEN_RESPONDENT_CONTROLS",
                   "on the respondent side only", "`solution.benefit`", "refuses every bundle below 17"):
        assert phrase in said, phrase


def test_the_v16_call_is_marked_and_says_what_it_is():
    body = marks_mod.__doc__
    match = re.search(r"^75\. \*\*v16\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
    assert match, "75 is not marked v16"
    said = " ".join(match.group(1).split())
    for phrase in ("`occasion`", "`idea_what`", "no `reveal`", "X3, L1-L4 and W3", "refuses every bundle below 16"):
        assert phrase in said, phrase


def test_the_v15_call_is_marked_and_says_what_it_is():
    body = marks_mod.__doc__
    match = re.search(r"^74\. \*\*v15\*\*(.*?)(?=^\d+\. |\Z)", body, re.M | re.S)
    assert match, "74 is not marked v15"
    said = " ".join(match.group(1).split())
    for phrase in ("corpus revision 8", "`stronger`", "`short`", "`NOT_TESTED`", "decision.split",
                   "decision.notTested", "refuses every bundle below 15"):
        assert phrase in said, phrase


def test_the_marks_file_carries_the_v20_header_above_v19s():
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert text.index("MARKS_VERSION 20") < text.index("MARKS_VERSION 19") < text.index("MARKS_VERSION 18") < \
        text.index("MARKS_VERSION 17") < text.index("MARKS_VERSION 16")
    assert "WHY=marks:20" in text and "founder's" in text
    assert re.search(r"^spoken_form = 1\.00$", text, re.M) and re.search(r"^report_overview = 1\.00$", text, re.M)
    assert re.search(r"^brief_facts = 1\.00$", text, re.M)
    assert re.search(r"^#\s+brief_answers = 1\.00", text, re.M), "struck through in a comment, never a key"
    assert not re.search(r"^brief_paragraphs\s*=", text, re.M) and not re.search(r"^brief_answers\s*=", text, re.M)


def test_the_marks_file_carries_the_v17_header_above_v16s():
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert text.index("MARKS_VERSION 17") < text.index("MARKS_VERSION 16") < text.index("MARKS_VERSION 15")
    assert "WHY=marks:17" in text


def test_the_marks_file_carries_the_v16_header_above_v15s():
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert text.index("MARKS_VERSION 16") < text.index("MARKS_VERSION 15")
    assert "WHY=marks:16" in text


def test_the_marks_file_carries_the_v15_header_above_v14s():
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert text.index("MARKS_VERSION 15") < text.index("MARKS_VERSION 14") < \
        text.index("MARKS_VERSION 13") < text.index("MARKS_VERSION 12")
    assert "Run of record: none yet" in text and "WHY=marks:15" in text


def test_the_marks_file_carries_the_v14_header_above_v13s():
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert text.index("MARKS_VERSION 14") < text.index("MARKS_VERSION 13") < \
        text.index("MARKS_VERSION 12")
    assert "Run of record: none yet" in text and "WHY=marks:14" in text


def test_the_marks_file_carries_the_v13_header_and_no_run_of_record_yet():
    """Spec 033 FR-005: the v13 header above v12's, the denominators' comments, and *run of record:
    none yet*."""
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert text.index("MARKS_VERSION 13") < text.index("MARKS_VERSION 12") < \
        text.index("MARKS_VERSION 11") < text.index("MARKS_VERSION 10") < text.index("MARKS_VERSION 9")
    assert "WHY=marks:14" in text
    assert "no_leak 46 + 63 = 109" in text and "108" in text


def test_the_v10_header_stays_as_history():
    """FR-003 at v10, kept: `no_claim_words` struck through as `golden_belief_recall` is."""
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert "MARKS_VERSION 10 (history" in text
    assert re.search(r"^#\s+golden_belief_recall = 0\.80", text, re.M)
    assert re.search(r"^#\s+no_claim_words\b", text, re.M)
    assert not re.search(r"^no_claim_words\s*=", text, re.M)
    assert "10 on a B2C entry, 12 on a B2B one" in text


def test_the_ten_marks_and_no_retired_one():
    assert marks_mod.load() == V20_MARKS
    assert marks_mod.DEFAULTS == V20_MARKS
    for retired in ("golden_belief_recall", "brief_paragraphs", "no_claim_words", "brief_answers"):
        assert retired not in marks_mod.DEFAULTS
    assert marks_mod.ROWS[-3:] == ("spoken_form", "brief_facts", "report_overview")
    for journey_mark in ("report_insights", "report_no_repeat", "report_pilot", "report_binding"):
        assert journey_mark not in marks_mod.ROWS, "a journey mark is evals/report_marks.py's (call 120)"


def test_the_marks_file_says_the_scores_are_not_comparable_across_the_bump():
    text = marks_mod.DEFAULT_MARKS_PATH.read_text(encoding="utf-8")
    assert "MARKS_VERSION 12" in text
    assert "not comparable" in text
    assert "cannot be re-scored" in text


def _all_met_totals() -> dict:
    return {"dimension_coverage": 1.0, "option_validity": 1.0, "no_leak": 1.0,
            "anchoring_accuracy": 0.95, "compare_correctness": 1.0, "compare_measured": True,
            "refusals_by_rule": {}, "refusals_measured": True, "refusals_shown": 50,
            "shape_refusals": 0, "spoken_form": 1.0, "spoken_measured": True, "brief_facts": 1.0,
            "brief_facts_measured": True, "report_overview": 1.0, "report_overview_measured": True}


def test_judge_returns_the_ten_rows_each_measured_and_met():
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
                        ("spoken_form", {"spoken_measured": False}),
                        ("brief_facts", {"brief_facts_measured": False}),
                        ("report_overview", {"report_overview_measured": False})):
        totals = {**_all_met_totals(), **unset}
        judged = marks_mod.judge(totals, marks_mod.load())
        assert judged["passed"] is False, name
        assert judged[name]["measured"] is False and judged[name]["met"] is False, name


def test_a_spoken_form_brief_facts_or_report_overview_below_one_fails_its_row():
    for name in ("spoken_form", "brief_facts", "report_overview"):
        judged = marks_mod.judge({**_all_met_totals(), name: 0.99}, marks_mod.load())
        assert judged[name]["measured"] and not judged[name]["met"] and judged["passed"] is False, name


def test_the_refusal_mark_is_a_rate_over_the_answers_judged():
    totals = {**_all_met_totals(), "refusals_by_rule": {"C3": 1}, "refusals_shown": 50}
    row = marks_mod.judge(totals, marks_mod.load())["refusals"]
    assert row["value"] == 0.02 and row["count"] == 1 and row["met"] is True
    totals["refusals_by_rule"] = {"C3": 2}
    assert marks_mod.judge(totals, marks_mod.load())["refusals"]["met"] is False


def test_the_header_names_the_seven_r16_digests_and_keeps_v13s_counted_denominators():
    """Spec 064 FR-10 (spec 053's before it): the Spec 064 paragraph names the seven revision-13 files by their canon
    bytes (skipped by name when the configured keel-cloud is not at revision 13), Spec 053's keeps r12's and v19's
    r11's as history; v13's dated paragraph and its counted denominators stay below it as history."""
    import hashlib                                                          # noqa: PLC0415
    from tests import v9_fixtures as fx                                     # noqa: PLC0415
    doc = marks_mod.__doc__
    header = doc[:doc.index("1.  **v1**")]
    names = ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly",
             "06-repeatline", "07-mulchrun")
    for name in names:
        path = fx.canon_entry(f"{name}.yaml")
        assert hashlib.sha256(path.read_bytes()).hexdigest() in header, name
    assert "The seven revision-12\nfiles, by sha256" in header and "The seven revision-11 files, by sha256" in header
    assert "The seven revision-13 files, by sha256" in header and "**v20 stands**: this spec bumps nothing" in header
    assert "The seven revision-14 files, by sha256" in header and "**v20\nstands**: this cut bumps nothing" in header
    assert "The seven\nrevision-15 files, by sha256" in header and "**v20 stands**: this revision bumps nothing" in header
    assert "The seven revision-16 files, by sha256" in header and "keel-cloud-docs\n`efdd37bf`" in header
    assert "65 reads at N=1" in header
    assert "135 model cases at N=1" in header and "**108**" in header and "**80**" in header
    assert "The corpus v13 judges, recorded 2026-10-10" in header
    assert "no v13\nrun of record until `WHY=marks:13` is spent" in header
    assert "**46** sweep-A and **63** sweep-B" in header and "**109**" in header
    assert "**81** an N" in header
