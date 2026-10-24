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
    few and Keel's draft carries what it was given -- a redrafted row is typed over (the rows are positional), a rung
    past the drawn rows is typed into a new row, in the entry's order; past the screen's rows the walk stops naming
    the rung."""
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "16-pairio.yaml"
    if not path.is_file():
        pytest.skip("no 16-pairio")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    rungs = [i["label"] for i in vs.founder_list(entry, "problem.current_solution_satisfaction")["items"]]
    assert len(rungs) == 5
    drawn = [rungs[0], rungs[1].upper() + "."]                       # case and a full stop are no difference
    assert vs.rungs_plan(entry, drawn, 5) == {"edit": [], "add": rungs[2:], "cannot": []}
    # Keel redrafted the third row (Karsa, 2026-10-23): typed over, not added
    assert vs.rungs_plan(entry, drawn + ["Keel's own rung"], 5) == {"edit": [(2, rungs[2])], "add": rungs[3:],
                                                                   "cannot": []}
    assert vs.rungs_plan(entry, rungs, 5) == {"edit": [], "add": [], "cannot": []}
    # a screen of four rows cannot hold the fifth rung
    assert vs.rungs_plan(entry, rungs[:4], 4) == {"edit": [], "add": [], "cannot": [rungs[4]]}


# ------------------------------------------------------------------------------- FR-3: a line belongs to a rung

def _with_follow_up(value) -> dict:
    raw = fx.raw_entry(fx.ENTRY_B2B)
    raw.pop("expected", None)
    raw.update(id="96-rung", idea_name="Whistle key tag", sources="96-rung.sources.md")
    who = next(i for i, p in enumerate(raw["answers"]) if p.get("recency") == "yes")
    raw["answers"][who] = dict(raw["answers"][who], follow_up=value)
    return raw, raw["answers"][who]["person"]


def test_a_follow_up_names_its_rung_and_the_reader_keeps_it(tmp_path):
    raw, who = _with_follow_up({"dimension": "commercial.commitment", "text": "We'd start with one site first."})
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="96-rung.yaml"), registry=fx.registry(),
                                 backtest=True)
    person = entry.person(who)
    assert (person.follow_up, person.follow_up_dimension) == ("We'd start with one site first.", "commercial.commitment")
    inputs = next(p for p in vs.person_inputs(entry) if p.person == who)
    assert inputs.follow_up_dimension == "commercial.commitment"
    # a bare line is still read at revision 15 (judgement call 3): no rung
    raw, who = _with_follow_up("A bare line, as every r15 entry writes it.")
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="96-rung.yaml"), registry=fx.registry(),
                                 backtest=True)
    assert entry.person(who).follow_up_dimension is None and entry.person(who).follow_up


@pytest.mark.parametrize("value, why", [
    ({"dimension": "problem.frequency", "text": "Twice a week."}, "which is asked no follow-up"),
    ({"dimension": "commercial.commitment", "text": "  "}, "carries no words"),
    ({"dimension": "commercial.commitment"}, "it is {dimension, text}"),
    (["a list"], "it is {dimension, text}"),
])
def test_a_follow_up_off_its_shape_is_refused(tmp_path, value, why):
    raw, _ = _with_follow_up(value)
    assert why in _refused(tmp_path, raw)


# ------------------------------------------------------------------------------- FR-4: the served bar

def test_current_solution_is_counted_against_by_the_served_line():
    """Spec 067 FR-4 (keel-cloud 117 FR-3 / 128 FR-16, Pairio's Walter): with the served line at 1 only `outcome_1` is
    against; the registry's `outcome_1, outcome_2` stand only where no line is served (D4's 2, every golden entry)."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    walter = {"dimension": "problem.current_solution_satisfaction", "codes": ["outcome_2"], "chip": None}
    key = "problem.current_solution_satisfaction"
    assert fake.against(key, walter, fake.Founder()) is True
    assert fake.against(key, walter, fake.Founder(current_line=1)) is False
    assert fake.against(key, dict(walter, codes=["outcome_1"]), fake.Founder(current_line=1)) is True
    assert fake.against(key, dict(walter, codes=["outcome_3"]), fake.Founder(current_line=3)) is True
    assert fake.against(key, dict(walter, codes=["outcome_4"]), fake.Founder(current_line=3)) is False


def test_a_two_step_price_below_on_either_step_is_against():
    """keel-cloud 128 FR-21 (`Ladder.against`, AirCaps's Diego and Amaka): up front then a plan, held on both steps."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    founder = fake.Founder(price_low=20.0, upfront_low=100.0, chain_price=True)
    pick = lambda *codes: {"dimension": "commercial.price", "codes": list(codes), "chip": None}  # noqa: E731
    assert fake.against("commercial.price", pick("upfront.band_50_100", "band_20_50"), founder) is True
    assert fake.against("commercial.price", pick("upfront.band_100_250", "band_10_20"), founder) is True
    assert fake.against("commercial.price", pick("upfront.band_100_250", "band_20_50"), founder) is False


def test_the_composer_says_a_fact_back_as_the_fact_and_quotes_worse():
    """keel-cloud 128 FR-13b / FR-16 (`FollowUpComposer`): a fact answered No reads *You said no to this: {the fact}.
    What got in the way?* and is said as it reads; Relative advantage's worse is quoted."""
    assert vs.fact_said("Their phone was within reach of the cot.") == "your phone was within reach of the cot"
    assert vs.from_served("Think of your last shift. Did the list come straight out of the EMR?", "No") == \
        "You said no to this: did the list come straight out of the EMR? What got in the way?"
    assert vs.served_idea_name({"reveal": {"what": "Imagine Pairio."}}) == "Pairio"


# ------------------------------------------------------------------------------- FR-5: needs-input answered once

def _asking_journey(view: dict, *, strict: bool = False):
    from types import SimpleNamespace                                   # noqa: PLC0415
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "20-lemma.yaml"
    if not path.is_file():
        pytest.skip("no 20-lemma")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    posted = []
    j = SimpleNamespace(strict=strict, entry=entry, founder=vs.founder_inputs(entry), findings=[], posted=posted,
                        get=lambda path: view,
                        call=lambda method, path, body=None, ok=(): posted.append((method, path, body)) or (201, {}))
    return j


def test_a_needs_input_is_answered_once_from_the_entrys_fields_and_a_second_ask_stops(monkeypatch):
    """Spec 067 FR-5 (keel-cloud 128 FR-15, Lemma): AWAITING_INPUT is answered once with the entry's own words, the
    question a finding; asked again it stops at once, never a 660 s wait; a golden walk stops at the first ask."""
    import contextlib                                                   # noqa: PLC0415
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    monkeypatch.setattr(cs, "_step", lambda *a, **k: contextlib.nullcontext(SimpleNamespace(
        record_wire=lambda *x: None)))
    view = {"status": "AWAITING_INPUT", "turns": [{"turnNumber": 1}],
            "questions": [{"id": "q1", "question": "In your own words: who has this problem?"}]}
    j = _asking_journey(view)
    asked: dict = {}
    cs._needs_input(j, "iid", asked)
    assert len(j.posted) == 1 and j.posted[0][1] == "/v2/inference-interactions/iid/answers"
    content = j.posted[0][2]["content"]
    assert j.founder.context_fields["actor"] in content and j.founder.context_fields["segment"] in content
    assert j.findings and "answered once" in j.findings[0]["what"]
    cs._needs_input(j, "iid", asked)                                    # the same turn, still on its way: nothing
    assert len(j.posted) == 1
    view["turns"].append({"turnNumber": 2})                             # asked again
    with pytest.raises(AssertionError, match="asked the founder back again"):
        cs._needs_input(j, "iid", asked)
    with pytest.raises(AssertionError, match="spec 067 FR-5"):
        cs._needs_input(_asking_journey(dict(view), strict=True), "iid", {})
    quiet = _asking_journey({"status": "PENDING"})
    cs._needs_input(quiet, "iid", {})
    cs._needs_input(quiet, None, {})
    assert not quiet.posted and not quiet.findings


# ------------------------------------------------------------------------------- FR-8: the spoken guard

def test_the_backtest_record_holds_every_served_item_to_the_spoken_form():
    """Spec 067 FR-8 (keel-cloud 128 FR-10): each served item, as the page fetched it, read back through S1-S10 with its
    stem's length; keel-cloud's own composed Lullaby items are clean, and a 21-word stem is a red line, not a note."""
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import backtest as bt                                    # noqa: PLC0415
    from instructions import cloud_corpus as cloud_mod                  # noqa: PLC0415
    try:
        registry = cloud_mod.registry_of_record(KEEL_CLOUD)
        corpus = corpus_mod.load(KEEL_CLOUD).bind(registry)
        cloud = cloud_mod.read(KEEL_CLOUD, corpus=corpus, registry=registry)
    except Exception as missing:                                        # noqa: BLE001
        pytest.skip(f"no keel-cloud record: {missing}")
    lullaby = corpus.by_id("03-lullaby")
    items = cloud.items_of("03-lullaby")

    def served(ci, stem=None):
        return {"dimension": ci.key, "question": ci.question if stem is None else stem,
                "options": [{"optionId": str(n), "label": o} for n, o in enumerate(ci.options)],
                "escape": {"code": "X", "label": ci.escape} if ci.escape else None,
                "spoken": {"anchor": ci.anchor, "stem": ci.stem if stem is None else stem, "countLine": ci.count_line,
                           "optionsLine": ci.options_line, "escapeLine": ci.escape_line, "transform": ci.transform}}
    long = " ".join(["word"] * 20) + " too?"
    interview = {"kind": "FULL", "parts": [{"part": 1, "items": [served(ci) for ci in items]
                                            + [dict(served(items[0], stem=long), dimension=items[0].key)]}]}
    j = SimpleNamespace(entry=lullaby, registry=registry, interviews={"Amira Saleh": interview, "Twin": interview})
    guard = bt.spoken_guard(j)
    assert guard["items"] == len(items) + 1                             # the second person's same words are one row
    assert guard["clean"] == len(items) and guard["longest_stem"] == 21
    red = guard["red"][0]
    assert red["stem_words"] == 21 and any(f.startswith("S1") for f in red["faults"])
    md = bt.markdown({"spoken_guard": guard, "respondents": {}, "founder_screens": []})
    assert "**RED**" in md and f"{len(items)} of {len(items) + 1} items clean" in md


# ------------------------------------------------------------------------------- FR-7: the changed screens, read

def test_the_changed_screens_are_read_as_findings_on_a_back_test():
    """Spec 067 FR-7 (judgement call 6): a consumer link saying *per person*, a plan drawn after *I wouldn't pay for
    this*, *People disagree* on a bar line -- each recorded; a B2B study's own words are not consumer words."""
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import backtest as bt                                    # noqa: PLC0415
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "13-aircaps.yaml"
    if not path.is_file():
        pytest.skip("no 13-aircaps")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    andrea = next(p.person for p in entry.people() if (p.picks or {}).get("commercial.price")
                  and bt._closed_price(p.picks["commercial.price"]) and isinstance(p.picks["commercial.price"], list))
    assert andrea == "Andrea Whitlock"
    interview = {"kind": "FULL", "parts": [{"part": 3, "items": [
        {"dimension": "commercial.price", "question": "What would AirCaps be worth to you a month, per person?",
         "options": [{"optionId": "o", "label": "Under $10"}]}]}]}
    standings = {"facts": {"cards": [{"key": "solution.compatibility", "number": "3 of 7",
                                      "statusWords": "People disagree"},
                                     {"key": "problem.importance", "number": "4 of 7",
                                      "statusWords": "People disagree"}]}}
    walked = {andrea: {"screens": [{"dimension": "commercial.price", "plan": {"question": "And after that ..."}}]}}
    j = SimpleNamespace(entry=entry, interviews={andrea: interview}, walked=walked)
    got = bt.changed_screens(j, standings)
    assert [r["word"] for r in got["consumer_words"]] == ["per person"]
    assert [r["person"] for r in got["plan_after_closed_price"]] == [andrea]
    assert [r["key"] for r in got["people_disagree_on_a_bar_line"]] == ["solution.compatibility"]
    assert "*per person*" in bt.markdown({"changed_screens": got, "respondents": {}, "founder_screens": []})


# ------------------------------------------------------------------------------- the register's Re-run column

def test_the_rerun_row_carries_the_run_and_the_registers_last_score():
    """Spec 067 (keel-cloud 128 acceptance 4): the row a re-run adds -- read, never written -- names the run, the door,
    the decision, the score (to be judged) and the score of the entry's last row in the register."""
    from evals import backtest as bt                                    # noqa: PLC0415
    register = ("| Entry | Judged | Run | Door | Decision | Score | Zeros | What went wrong (top three) | Fixed by |\n"
                "|---|---|---|---|---|---|---|---|---|\n"
                "| 09-karsa | 2026-10-23 | 20261023T115825Z | host | BUILD_BUT_CHANGE · MEDIUM | 60% (94/156) | 11 | a | b |\n"
                "| 10-palus | 2026-10-23 | 20261023T121135Z | host | NOT_YET · MEDIUM | 60% (82/136) | 10 | c | d |\n")
    assert bt.register_scores(register, "09-karsa") == ["60% (94/156)"]
    row = {"id": "09-karsa", "run": "20261024T010000Z", "door": "host", "decision": "NOT_YET", "score": None}
    assert bt.rerun_row(row, register) == ("re-run row: | 09-karsa | (judged: to fill) | 20261024T010000Z | host | "
                                           "NOT_YET | to be judged | Re-run: after 128 · was 60% (94/156) |")
    assert bt.rerun_row(dict(row, id="11-issen"), register).endswith("was no earlier row |")
    real = bt._register_text()
    if real:                                                            # keel-cloud's own register, read as data
        assert bt.register_scores(real, "09-karsa"), "the register's Karsa row"
