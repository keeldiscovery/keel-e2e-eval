"""Spec 067 FR-6: corpus revision 15 (keel-cloud 128 FR-11, keel-cloud-docs `423f0983`), stackless.

Three things are held here. **Rule Q** (`check_corpus_r15.py`'s, mirrored by the reader): a person's `condition` is
YES or NO, on the primary link only, and only where the context records a condition -- and NO is a person outside the
segment. **Rule D15**, the eval's own diff: every entry read beside its revision-14 record (keel-cloud's test mirrors
`corpus-r14/` and `backtest-r14/`), every leaf difference one of 128's edits, and the count per entry exactly the
listing 128's tasks.md prints. And **the cloud's own checker** prints OK on all 35 entries. The mirrors and the
checker are keel-cloud's; where its checkout lacks them the tests skip by name (judgement call 4 of 067's tasks.md).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
MIRROR = KEEL_CLOUD / "src" / "test" / "resources" / "keel"
SIM = KEEL_CLOUD / "canon" / "designs" / "measured-beliefs" / "sim" / "check_corpus_r15.py"

#: keel-cloud 128 tasks.md, *The checker's diff, entry by entry* (leaf paths): every other entry moves by its revision.
DIFF_COUNTS = {"10-palus": 3, "11-issen": 64, "12-transload": 4, "13-aircaps": 45, "17-expanse": 3,
               "18-careforce": 14, "19-veles": 2, "21-codyco": 2, "25-bidflow": 2}
#: 128 FR-11 / FR-14: the entries whose context gains the segment's condition, and who answers it NO.
CONDITIONS = {"11-issen": ("are past the beginner stage", {"Nikos Ferrante"}),
              "18-careforce": ("work outreach lists by phone", {"Olga Petrenko", "Miguel Ferreira"})}
#: 128 FR-11: 12-transload's two managers who opt in to the pilot.
PILOTS = {"12-transload": {"Nadine Fournier", "Oluwaseun Adebayo"}}
COST = "commercial.existing_sacrifice"
_ABSENT = object()


def _walk(before, after, path, out):
    """`check_corpus_r15.py`'s `_walk`: every leaf that differs, a key or index absent on one side named `_ABSENT`."""
    if isinstance(before, dict) and isinstance(after, dict):
        for k in list(before) + [k for k in after if k not in before]:
            _walk(before.get(k, _ABSENT), after.get(k, _ABSENT), path + (k,), out)
    elif isinstance(before, list) and isinstance(after, list):
        for i in range(max(len(before), len(after))):
            _walk(before[i] if i < len(before) else _ABSENT, after[i] if i < len(after) else _ABSENT,
                  path + (i,), out)
    elif before != after or type(before) is not type(after):
        out.append((path, before, after))


def _kind(path: tuple, doc: dict) -> str | None:
    """Which of 128's edits one difference is (`check_corpus_r15.py`'s D15 classes), or None: not one of them."""
    entry = doc.get("id")
    if path == ("revision",):
        return "revision"
    if path == ("context", "condition") and entry in CONDITIONS:
        return "condition"
    if len(path) >= 3 and path[0] == "answers" and isinstance(path[1], int):
        who = doc["answers"][path[1]].get("person")
        if path[2] == "condition" and entry in CONDITIONS:
            return "chip"
        if path[2] == "pilot_opt_in" and who in PILOTS.get(entry, set()):
            return "pilot"
        if path[2:4] == ("picks", COST) and entry in ("11-issen", "13-aircaps"):
            return "cost"
    if path[:4] == ("founder_calibration", "problem.importance", "answer", "items") and path[-1] == "label":
        return "label"
    return None


def _pairs():
    out = []
    for directory, mirror, backtest in ((corpus_mod.corpus_dir(KEEL_CLOUD), MIRROR / "corpus-r14", False),
                                        (corpus_mod.backtest_dir(KEEL_CLOUD), MIRROR / "backtest-r14", True)):
        for path in sorted(directory.glob("*.yaml")) if directory.is_dir() else []:
            out.append((path, mirror / path.name, backtest))
    return out


def _need_mirrors():
    if not (MIRROR / "corpus-r14").is_dir() or not (MIRROR / "backtest-r14").is_dir():
        pytest.skip(f"keel-cloud at {KEEL_CLOUD} carries no revision-14 mirrors (128 T041's corpus-r14/, backtest-r14/)")


# ------------------------------------------------------------------------------------------------ rule D15

def test_every_entry_moves_by_exactly_128s_edits():
    """D15, the eval's own: 35 entries, each beside its revision-14 record; every difference one of 128's edits, the
    count per entry 128's listing, the golden seven by their revision line alone."""
    _need_mirrors()
    pairs = _pairs()
    assert len(pairs) == 35, [p.name for p, _, _ in pairs]
    counts, strays = {}, []
    for path, before_path, backtest in pairs:
        after = yaml.safe_load(path.read_text(encoding="utf-8"))
        before = yaml.safe_load(before_path.read_text(encoding="utf-8"))
        out: list = []
        _walk(before, after, (), out)
        counts[after["id"]] = len(out)
        for p, old, new in out:
            kind = _kind(p, after)
            if kind is None or (kind != "revision" and not backtest):
                strays.append((after["id"], p, old, new))
            if kind == "revision":
                assert (old, new) == (14, 15), (after["id"], old, new)
            if kind == "pilot":
                assert (old, new) == (False, True), (after["id"], p)
            if kind == "chip":
                who = after["answers"][p[1]]["person"]
                assert old is _ABSENT and new == ("NO" if who in CONDITIONS[after["id"]][1] else "YES"), (who, new)
            if kind == "condition":
                assert old is _ABSENT and new == CONDITIONS[after["id"]][0], new
    assert not strays, strays
    want = {entry: DIFF_COUNTS.get(entry, 1) for entry in counts}
    assert counts == want


def test_the_cloud_checker_prints_ok_on_every_entry():
    """`check_corpus_r15.py` itself (the cloud's D15 and Q, with every older rule) over the 35 entries."""
    _need_mirrors()
    if not SIM.is_file():
        pytest.skip(f"keel-cloud at {KEEL_CLOUD} carries no {SIM.name}")
    failed = {}
    for path, _, _ in _pairs():
        run = subprocess.run([sys.executable, "-I", str(SIM), str(path)], cwd=SIM.parent, capture_output=True,
                             text=True, timeout=120)
        last = (run.stdout.strip().splitlines() or [""])[-1]
        if run.returncode != 0 or not last.startswith("OK "):
            failed[path.name] = run.stdout[-800:] + run.stderr[-400:]
    assert not failed, failed


# ------------------------------------------------------------------------------------------------- rule Q

def _issen_raw() -> dict:
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "11-issen.yaml"
    if not path.is_file():
        pytest.skip(f"no 11-issen at {path.parent}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _refused(tmp_path, raw) -> str:
    path = fx.write_entry(tmp_path, raw, name=f"{raw['id']}.yaml")
    with pytest.raises(corpus_mod.CorpusError) as refused:
        corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    return str(refused.value)


def test_the_condition_is_read_per_person_and_no_is_outside_the_segment():
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "11-issen.yaml"
    if not path.is_file():
        pytest.skip(f"no 11-issen at {path.parent}")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    outside = [p.person for p in entry.people() if not p.in_segment]
    assert outside == ["Nikos Ferrante"]
    assert {p.condition for p in entry.people() if p.link == corpus_mod.LINK_PRIMARY} == {"YES", "NO"}
    nikos = next(p for p in vs.person_inputs(entry) if p.person == "Nikos Ferrante")
    assert nikos.in_segment is False and nikos.picks == [] and nikos.response("t") == {"outsideSegment": True,
                                                                                      "answers": []}


def test_a_condition_answer_is_yes_or_no_on_the_primary_link_where_the_context_records_one(tmp_path):
    raw = _issen_raw()
    bad = dict(raw, answers=[dict(raw["answers"][0], condition="MOSTLY")] + raw["answers"][1:])
    assert "condition 'MOSTLY' is not YES or NO (rule Q)" in _refused(tmp_path, bad)
    bare = dict(raw, context={k: v for k, v in raw["context"].items() if k != "condition"})
    assert "where the context records no condition (rule Q)" in _refused(tmp_path, bare)
    both = dict(raw, answers=[dict(raw["answers"][0], condition="NO", in_segment=True)] + raw["answers"][1:])
    assert "in_segment True disagrees with condition 'NO'" in _refused(tmp_path, both)


def test_a_condition_on_the_decision_makers_link_is_refused(tmp_path):
    raw = fx.raw_entry(fx.ENTRY_B2B)
    raw.pop("expected", None)
    raw.update(id="97-cond", idea_name="Whistle key tag", sources="97-cond.sources.md")
    raw["context"] = dict(raw["context"], condition="keep keys on a hook")
    decider = next(i for i, p in enumerate(raw["answers"]) if p.get("link") == corpus_mod.LINK_B2B)
    raw["answers"][decider] = dict(raw["answers"][decider], condition="YES")
    assert "the condition chip is asked on the primary link only (rule Q)" in _refused(tmp_path, raw)


def test_transloads_two_managers_opt_in_to_the_pilot():
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "12-transload.yaml"
    if not path.is_file():
        pytest.skip("no 12-transload")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    opted = {p.person for p in vs.person_inputs(entry) if p.pilot_opt_in}
    assert PILOTS["12-transload"] <= opted, opted


def test_a_person_outside_is_walked_inside_where_the_page_serves_no_chip():
    """FR-6: Keel's AI writes the gate's segment chip (keel-cloud 120 FR-2); where it writes none, Nikos Ferrante (NO) is
    walked on his recorded gate answer, story and picks (`vs.inside_inputs`), and the journey names it."""
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "11-issen.yaml"
    if not path.is_file():
        pytest.skip(f"no 11-issen at {path.parent}")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    nikos = vs.inside_inputs(entry, "Nikos Ferrante")
    assert nikos.in_segment and nikos.recency is True and nikos.picks and nikos.story
    assert nikos.response("t")["recency"] is True


# ------------------------------------------------------------------------------- FR-1: the Answer box at load

def test_every_entry_fits_the_answer_box_and_revision_14s_transload_stops_at_load(tmp_path):
    """Spec 067 FR-1 (keel-cloud 128 FR-17, FR-20): all 35 revision-15 entries name every Importance item inside the
    25-word Answer; revision 14's 12-transload (*Running the shift with too few workers*) did not, and the harness
    then lost *Finding freight sitting at the wrong door* -- read at revision 15, it stops at load naming the label."""
    _need_mirrors()
    for path, _, backtest in _pairs():
        vs.check_answer_box(corpus_mod.load_file(path, registry=fx.registry(), backtest=backtest))
    raw = yaml.safe_load((MIRROR / "backtest-r14" / "12-transload.yaml").read_text(encoding="utf-8"))
    raw["revision"] = corpus_mod.REVISION
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="12-transload.yaml"), registry=fx.registry(),
                                 backtest=True)
    with pytest.raises(vs.VectorsScriptError) as stopped:
        vs.founder_inputs(entry)
    assert "'Finding freight sitting at the wrong door' would be dropped" in str(stopped.value), str(stopped.value)
    assert vs.answer_drops(entry, "problem.importance") == ["Finding freight sitting at the wrong door"]


def test_a_list_label_past_the_answer_box_stops_at_load(tmp_path):
    """Bound to the registry a label is held to its `saves.max_words` (nine) first; read unbound, the harness's own
    stop names it."""
    raw = fx.raw_entry(fx.ENTRY)
    items = raw["founder_calibration"]["problem.importance"]["answer"]["items"]
    items[1]["label"] = " ".join(["word"] * 26)
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw))
    with pytest.raises(vs.VectorsScriptError, match="is 26 words; the Answer box takes 25"):
        vs.check_answer_box(entry)


# ------------------------------------------------------------------------------- FR-2: every founder rung typed

def test_the_rungs_the_draft_left_out_are_typed_and_past_the_screen_they_stop():
    """Spec 067 FR-2 (keel-cloud 128 FR-16): 16-pairio's founder has five rungs; the Answer's 25 words carry the first
    few and Keel's draft carries what it was given -- every other rung is typed on the Check screen, in the entry's
    order; with no room left the walk stops naming the rung."""
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "16-pairio.yaml"
    if not path.is_file():
        pytest.skip("no 16-pairio")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    rungs = [i["label"] for i in vs.founder_list(entry, "problem.current_solution_satisfaction")["items"]]
    assert len(rungs) == 5
    drawn = [rungs[0], rungs[1].upper() + "."]                       # case and a full stop are no difference
    typed, cannot = vs.rungs_to_type(entry, drawn, 5)
    assert typed == rungs[2:] and cannot == []
    typed, cannot = vs.rungs_to_type(entry, drawn + ["Keel's own rung"], 5)
    assert typed == rungs[2:4] and cannot == [rungs[4]]
    assert vs.rungs_to_type(entry, rungs, 5) == ([], [])
