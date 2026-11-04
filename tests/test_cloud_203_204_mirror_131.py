"""Spec 131 -- the mirrors owed by keel-cloud 203 (the Current solution scale has a working rung) and 204 (Keel's rows
fit the row cap) that no cycle has tested yet (their tasks.md, *Owed elsewhere*: keel-e2e-eval).

- 203: `founder_rungs` and `rungs_plan` counted from the top with Keel's working rung first where an entry's Answer
  types only shortfalls (`vectors_script.keels_working_first`: the saved list's first rung marked `keel: true`, never
  typed in the Answer's how box, the line under it); an entry whose first rung is a shortfall refused at load by name
  (the Save refuses it); `WorkingRung` restated (`harness/working_rung.py`, held to the Java in
  `test_dimension_cards_131`); `L30` named where refusals are reported.
- 204: `RowCap.cut` restated (`instructions/spoken.row_cap_cut`); the scripted founder-lists writer cuts a corpus row
  over its cap; `instructions/score.py` names `L31` for a row of the founder's own words over the cap (Keel's own words
  stay `L2`); `L31` named where refusals are reported.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import backtest as bt
from harness import vectors_script as vs
from harness import working_rung as wr
from instructions import score as score_mod
from instructions import spoken as spoken_mod
from stack.config import load_config
from tests.test_vectors_journey import _entry

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
CS = "problem.current_solution_satisfaction"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_CLOUD}")
    return path.read_text(encoding="utf-8")


def _with_rungs(entry, items: list[dict]):
    """`entry` with Current solution's saved list replaced by `items` (codes kept from the entry's own)."""
    out = copy.deepcopy(entry)
    answer = out.founder_calibration[CS]["answer"]
    codes = [i["code"] for i in answer["items"]]
    answer["items"] = [{"code": code, **item} for code, item in zip(codes, items)]
    return out


#: An Answer that types only shortfalls (spec 203's case), with Keel's working rung on top, marked as Keel's.
SHORTFALLS = [{"label": "Paid on the agreed terms", "keel": True},
              {"label": "Payment terms failed, paid a little late"},
              {"label": "Reminders failed, paid late after a chase"},
              {"label": "Chasing failed, paid after many calls"},
              {"label": "Collection failed outright, still not paid"}]


# ------------------------------------------------------------------------------------- 203: the working rung first

def test_founder_rungs_are_counted_from_the_top_below_keels_working_rung():
    paidly = _entry("05-paidly")
    # spec 135 re-pin: 117's golden table typed 3 on one joined box; the second box's own 25 words carry 4
    assert not vs.keels_working_first(paidly) and vs.founder_rungs(paidly) == 4
    entry = _with_rungs(paidly, SHORTFALLS)
    assert vs.keels_working_first(entry)
    what, how = vs.current_solution_boxes(entry)
    assert "Paid on the agreed terms" not in how, "the founder never typed Keel's working rung"
    assert how.startswith("Payment terms failed, paid a little late")
    rungs = vs.founder_rungs(entry)
    assert rungs == len(how.rstrip(".").split("; ")) >= 1
    draft = vs.drafted_list(entry, CS)
    assert draft["items"][0]["label"] == "Paid on the agreed terms"
    assert (draft["founder_rungs"], draft["line"]) == (rungs, 1), "the line under Keel's working rung (203 FR-2)"
    assert wr.working([i["label"] for i in draft["items"]], draft["line"]) == 1, "no L30: a rung above the line works"
    vs.check_answer_box(entry)


def test_rungs_plan_counts_from_the_top_with_keels_working_rung_in_row_0():
    entry = _with_rungs(_entry("05-paidly"), SHORTFALLS)
    labels = [i["label"] for i in SHORTFALLS]
    drawn = ["Evidence of payment arrived on the agreed terms", *labels[1:3]]          # Keel's own words on top
    assert vs.rungs_plan(entry, drawn, 5) == {"edit": [(0, labels[0])], "add": labels[3:], "cannot": []}
    assert vs.rungs_plan(entry, labels, 5) == {"edit": [], "add": [], "cannot": []}


def test_an_entry_whose_first_rung_is_a_shortfall_is_refused_at_load_by_name():
    unmarked = _with_rungs(_entry("05-paidly"), [{"label": i["label"]} for i in SHORTFALLS[1:]] +
                           [{"label": "Still waiting to be paid"}])
    with pytest.raises(vs.VectorsScriptError, match=r"is a shortfall \('failed'\).*keel-cloud 203"):
        vs.check_answer_box(unmarked)
    wrong = _with_rungs(_entry("05-paidly"), [{"label": "Paid on the agreed terms", "keel": True},
                                              {"label": "Paid a little late, no chasing"}, *SHORTFALLS[2:]])
    with pytest.raises(vs.VectorsScriptError, match="marked Keel's"):
        vs.keels_working_first(wrong)


def test_no_golden_entrys_first_rung_is_a_shortfall():
    for entry_id in ("01-countly", "05-paidly", "07-mulchrun"):
        entry = _entry(entry_id)
        first = entry.founder_list(CS)["items"][0]["label"]
        assert wr.works(first) and not vs.keels_working_first(entry), entry_id


# ------------------------------------------------------------------------------------------- 204: the row cap

def test_the_row_caps_are_the_registrys():
    registry = json.loads(_cloud("src/main/resources/keel/dimension-registry.json"))
    caps = {d["key"]: d["founder"]["saves"]["max_words"] for d in registry["dimensions"]
            if (d["founder"].get("saves") or {}).get("max_words")}
    assert vs.ROW_CAP == caps


@pytest.mark.parametrize("label, most, cut", [
    # keel-cloud's KeelsRowsFitTheRowCapTest: the 13-word rung of a 25-word Answer, at the screen's 9
    ("Half the time the screening call slips a week because partners never confirm", 9,
     "Half the time the screening call slips a week"),
    ("The screening call slipped more than a week because the partners never confirmed", 9,
     "The screening call slipped more than a week"),
    ("Keep the caption glasses paired to the phone for the whole conversation", 9,
     "Keep the caption glasses paired to the phone"),
    # spec 130 FR-5 (Karsa): the trailing phrase first
    ("They would have a bank account or wallet in their name", 9, "They would have a bank account or wallet"),
    ("The board and the project executive", 4, "The board"),
    ("Paid on the agreed terms", 9, "Paid on the agreed terms")])
def test_row_cap_cut_is_rowcaps(label, most, cut):
    got = spoken_mod.row_cap_cut(label, most)
    assert got == cut and 1 <= len(got.split()) <= most and label.startswith(got)


def test_the_scripted_writer_cuts_a_corpus_rung_over_the_cap():
    long = "Half the time the screening call slips a week because partners never confirm"
    entry = _with_rungs(_entry("05-paidly"), [{"label": "Paid on the agreed terms"}, {"label": long},
                                              *[{"label": i["label"]} for i in SHORTFALLS[2:]]])
    draft = vs.drafted_list(entry, CS)
    assert draft["items"][1]["label"] == "Half the time the screening call slips a week"
    assert all(len(i["label"].split()) <= vs.ROW_CAP[CS] for i in draft["items"])


def _dimension(key: str, control: str, saves: dict):
    return SimpleNamespace(key=key, founder_control=control, saves=saves, part=1)


def test_score_names_l31_for_the_founders_own_row_over_the_cap_and_l2_for_keels():
    answer = ("We email angels the deck and chase replies by phone; half the time the screening call slips a week "
              "because partners never confirm in time.")
    own = "Half the time the screening call slips a week because partners never confirm"
    keels = "The screening call slipped more than a week because the partners never confirmed"
    question = {"key": CS, "list": {"phrase": "chasing angels for replies",
                                    "items": [{"label": "Every call was confirmed in time"}, {"label": own},
                                              {"label": keels}, {"label": "The call slipped about a month"},
                                              {"label": "The call never happened"}]}}
    dim = _dimension(CS, "scale_lines", {"min_items": 5, "max_items": 5, "max_words": 9, "phrase": True})
    faults = score_mod.list_faults(question, dim, answers={CS: answer})
    l31 = [f for f in faults if f.startswith("L31:")]
    l2 = [f for f in faults if f.startswith("L2:")]
    assert len(l31) == 1 and "item 2" in l31[0] and "the founder's own words" in l31[0]
    assert len(l2) == 1 and "item 3" in l2[0]
    assert [f[:3] for f in score_mod.list_faults(question, dim, answers={})].count("L2:") == 2, \
        "no Answer: every over-cap row is Keel's"


# ------------------------------------------------------------------------------- the rule names, reported by name

def test_l30_and_l31_are_named_where_refusals_are_reported():
    applier = _cloud(APPLICATION + "ScreenResultApplier.java")
    for rule in ("L30", "L31"):
        assert f'"{rule}: ' in applier, rule
        assert rule in bt.LOCK_NOTES, rule
    rows = [{"screen": "CALIBRATION_QUESTIONS", "detail": "breach result.questions[0].list.items[0].label: L30: no rung "
                                                          "above the line reads as today's way working"},
            {"screen": "CALIBRATION_QUESTIONS", "turns": [{"content": "L31: 'Half the time the screening call slips a "
                                                                      "week because partners never confirm' is the "
                                                                      "founder's own rung, 13 words"}]}]
    found = bt.lock_notes(None, rows)
    assert [f["rule"] for f in found] == ["L30", "L31"]
    assert found[0]["means"] == bt.LOCK_NOTES["L30"] and "keel-cloud 204" in found[1]["means"]
