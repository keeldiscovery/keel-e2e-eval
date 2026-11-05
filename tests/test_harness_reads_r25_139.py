"""Spec 139 FR-4: the harness reads corpus revision 25 (owed by keel-cloud 217, keel-cloud-docs `4369a636`); spec 135's
test of revision 24 (owed by keel-cloud 215, keel-cloud-docs `0464e20f`), moved on to 25.

Revision 25 (keel-cloud 217, `specs/217-corpus-revision-25/tasks.md`, *Owed to keel-e2e-eval*): the fourteen gallery
entries at 25, every other entry at 23; a gallery file at 23 or 24 and any other file at 25 refused by name; the diff 24
-> 25 the gallery's alone (keel-cloud's `backtest-r24/` record). AirCaps' Compatibility is two rows, the pick
`read_and_watch` at index 1 (an ability); Code Four's Purchase friction two and Codyco's one, the founder's times kept;
Importance's rows the founder types on Check are revision 25's (nine entries now, Fresco's, Expanse's and Codyco's
reworded rivals the longer).

What follows is spec 135's account of revision 24, kept as written where it still holds:

FR-1 the loader reads the fourteen gallery entries at 24 and every other entry at 23 (`corpus.GALLERY`,
`GALLERY_REVISION`, `revision_of`), refusing by name a gallery file at 23 and any other file at 24; the diff 23 -> 24 is
the review's (spec 134's `corpus-rewording.md`) on the gallery and nothing anywhere else. FR-2 the scripted walk types
the new shapes (the three new codes, Fresco's pick at index 0 of two with its 2 weeks, AirCaps' four conditions, Issen's
pick on `speak_aloud`) and no gallery entry types the founder's own offer (`offer_rows` empty, the L32 expectation
*no own-offer row typed* reported in the transcript). FR-3 the constitution is pointed to from the cards file's head and
the gallery's map. FR-4 is `tests/test_gallery.py`'s (the recorded Fresco run marked 23, its compare skipped).

Two things revision 24 does that the review did not foresee, held here by name (tasks.md, *Left open*):

- **Six gallery entries' Importance no longer fits the 25-word Answer** (`R25_TYPED_ON_CHECK`): the reworded rivals are
  longer, so the founder's Answer names the others that fit its 25 words and types the rest on the Check screen, as a
  founder does (the coordinator's decision, 2026-11-04) -- each a finding, never a stop; `check_answer_box` stops only on
  a single row longer than the box. Current solution's two boxes are typed apart, each to its own 25 words.
- **15-voltair's tested Compatibility condition became a fact** while its record kept the registry's four
  (`corpus.R24_FACT_FOUR`): code serves a fact three and nobody picked `only_with_help`, so it is read as served.
"""

from __future__ import annotations

import json
import shutil
import tomllib
from pathlib import Path

import pytest
import yaml

from evals import backtest as bt
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

REPO = Path(__file__).resolve().parent.parent
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
MIRROR = KEEL_CLOUD / "src" / "test" / "resources" / "keel"
CONSTITUTION = KEEL_CLOUD / "canon" / "designs" / "measured-beliefs" / "backtest" / "CONSTITUTION.md"
IMPORTANCE = "problem.importance"
COMPATIBILITY = "solution.compatibility"
ADVANTAGE = "solution.relative_advantage"
PF = "commercial.purchase_friction"

#: The gallery entries whose Importance rivals outrun the 25-word Answer, and the rows the founder types on the Check
#: screen (the others past the box, in the entry's order). Spec 139 FR-4 (keel-cloud 217's Table 1): revision 25's
#: rewording moves AirCaps' typed row and adds Fresco, Expanse and Codyco (each a finding, never a stop).
R25_TYPED_ON_CHECK = {"08-fresco": ["Following up on safety issues from the walk"],
                      "09-karsa": ["Keeping cash at home safe"],
                      "12-transload": ["Finding freight sitting at the wrong door"],
                      "13-aircaps": ["Telling the people there about their hearing loss"],
                      "14-code-four": ["Logging the evidence from the call"],
                      "15-voltair": ["Spotting trees growing into the lines"],
                      "17-expanse": ["Checking the group's GPU-hour allocation before submitting"],
                      "20-lemma": ["Finding an engineer free to dig in"],
                      "21-codyco": ["Answering guests' questions about their stay"]}


@pytest.fixture(scope="module")
def backtest() -> dict:
    if not corpus_mod.backtest_dir(KEEL_CLOUD).is_dir():
        pytest.skip(f"no back-test corpus at {KEEL_CLOUD}")
    return {e.id: e for e in corpus_mod.load(KEEL_CLOUD, registry=fx.registry(), backtest=True).entries}


def _r23(name: str) -> Path:
    path = MIRROR / "backtest-r23" / name
    if not path.is_file():
        pytest.skip(f"no revision-23 record {path}")
    return path


def _r24(name: str) -> Path:
    path = MIRROR / "backtest-r24" / name
    if not path.is_file():
        pytest.skip(f"no revision-24 record {path}")
    return path


# ------------------------------------------------------------------------------- FR-1: the loader and the pins

def test_the_gallery_is_the_maps_fourteen_and_keel_clouds():
    names = tomllib.loads((REPO / "instructions" / "gallery_names.toml").read_text(encoding="utf-8"))["gallery"]
    assert sorted(row["entry"] for row in names) == sorted(corpus_mod.GALLERY)
    assert len(corpus_mod.GALLERY) == 14 and corpus_mod.GALLERY_REVISION == 25 and corpus_mod.REVISION == 23
    assert [corpus_mod.revision_of(e) for e in ("08-fresco", "21-codyco", "22-andy-ai", "03-lullaby")] == [25, 25, 23, 23]


def test_every_entry_loads_at_its_revision(backtest):
    for entry in corpus_mod.load(KEEL_CLOUD, registry=fx.registry()).entries:
        assert entry.revision == 23, entry.id
    assert {e.id for e in backtest.values() if e.revision == 25} == set(corpus_mod.GALLERY)
    assert all(e.revision == 23 for e in backtest.values() if e.id not in corpus_mod.GALLERY)


def test_a_gallery_file_at_23_or_24_and_another_at_25_are_refused_by_name(tmp_path):
    old = tmp_path / "08-fresco.yaml"
    shutil.copy(_r23("08-fresco.yaml"), old)
    with pytest.raises(corpus_mod.CorpusError, match="revision is 23; this eval reads revision 25 for a gallery entry "
                                                     "only -- revision 23 is the gallery's rows before keel-cloud 215"):
        corpus_mod.load_file(old, backtest=True)
    shutil.copy(_r24("08-fresco.yaml"), old)
    with pytest.raises(corpus_mod.CorpusError, match="revision is 24; this eval reads revision 25 for a gallery entry "
                                                     "only -- revision 24 is the gallery's rows before keel-cloud 217"):
        corpus_mod.load_file(old, backtest=True)
    raw = yaml.safe_load((corpus_mod.backtest_dir(KEEL_CLOUD) / "22-andy-ai.yaml").read_text(encoding="utf-8"))
    raw["revision"] = 25
    other = fx.write_entry(tmp_path, raw, name="22-andy-ai.yaml")
    with pytest.raises(corpus_mod.CorpusError, match="revision is 25; this eval reads revision 23 only -- revision 25 is "
                                                     "the gallery's alone"):
        corpus_mod.load_file(other, backtest=True)


def test_revision_25_moved_the_gallery_and_nothing_else():
    """The revision-24 records keel-cloud 217 kept (`backtest-r24/`): every entry outside the gallery is byte for byte
    its record; every gallery entry moved its revision line, 24 -> 25 (217: all fourteen moved a row)."""
    if not (MIRROR / "backtest-r24").is_dir():
        pytest.skip("no revision-24 records")
    for path in sorted(corpus_mod.backtest_dir(KEEL_CLOUD).glob("*.yaml")):
        before = (MIRROR / "backtest-r24" / path.name).read_text(encoding="utf-8")
        if path.stem in corpus_mod.GALLERY:
            assert (yaml.safe_load(before)["revision"], yaml.safe_load(path.read_text())["revision"]) == (24, 25)
        else:
            assert path.read_text(encoding="utf-8") == before, path.name


# ------------------------------------------------------------------------------- FR-2: the scripted walk

def test_the_splits_carry_their_new_codes_and_the_walk_types_every_row(backtest):
    palus, issen, aircaps = backtest["10-palus"], backtest["11-issen"], backtest["13-aircaps"]
    assert [i["code"] for i in palus.founder_list(ADVANTAGE)["items"]] == ["less_help_needed", "no_treasury_hire"]
    assert [i["code"] for i in issen.founder_list(ADVANTAGE)["items"]] == ["less_help_needed", "no_tutor_to_book"]
    assert [i["label"] for i in vs.saved_list(palus, ADVANTAGE)["items"]] == [
        "Higher yield on cash not needed for months", "No treasury hire to manage it"]
    assert [i["label"] for i in vs.saved_list(issen, ADVANTAGE)["items"]] == ["Speaking practice any time",
                                                                              "No tutor to book"]
    assert next(a for a in vs.calibration_answers(issen, "SOLUTION") if a.dimension == ADVANTAGE).text == \
        "Speaking practice any time; No tutor to book"
    # spec 139 FR-4 (keel-cloud 217): AirCaps' Compatibility is two conditions, the pick `read_and_watch` at index 1 --
    # an ability, its row the four codes (`phone_with_them` and `glasses_whole_time` dropped)
    saved = aircaps.founder_list(COMPATIBILITY)
    assert [i["code"] for i in saved["items"]] == ["phone_online", "read_and_watch"] and saved["picked"] == 1
    typed = vs.saved_list(aircaps, COMPATIBILITY)
    assert len(typed["items"]) == 2 and typed["pickedIndex"] == 1
    assert typed["items"][1] == {"code": "item_2", "label": "could read captions while watching faces",
                                 "asked": "could you have read captions while watching people's faces"}
    assert corpus_mod._tested_kind(aircaps) == "ABILITY"
    assert aircaps.respondent_questions[COMPATIBILITY]["codes"] == ["yes_easily", "yes_with_steps", "only_with_help",
                                                                    "no"]


def test_issens_compatibility_pick_is_speak_aloud(backtest):
    issen = backtest["11-issen"]
    saved = issen.founder_list(COMPATIBILITY)
    assert saved["items"][saved["picked"]]["code"] == "speak_aloud" and saved["picked"] == 1
    assert vs.saved_list(issen, COMPATIBILITY)["pickedIndex"] == 1
    answer = next(a for a in vs.calibration_answers(issen, "SOLUTION") if a.dimension == COMPATIBILITY)
    assert answer.listed["pickedIndex"] == 1 and (issen.tested(COMPATIBILITY) or {})["code"] == "speak_aloud"


def test_frescos_purchase_friction_is_two_with_the_pick_at_0_and_the_founders_two_weeks(backtest):
    fresco = backtest["08-fresco"]
    saved = fresco.founder_list(PF)
    assert [i["code"] for i in saved["items"]] == ["procore_check", "security_review"] and saved["picked"] == 0
    assert vs.kept_picked(fresco, PF) == 0 and vs.founder_duration(fresco) == {"count": 2, "unit": "WEEKS"}
    wire = vs.saved_list(fresco, PF)
    assert wire["pickedIndex"] == 0 and wire["duration"] == {"count": 2, "unit": "WEEKS"} and len(wire["items"]) == 2
    # spec 139 FR-4 (keel-cloud 217): Code Four two and Codyco one, each pick 0 and the founder's time kept
    for entry_id, count, weeks in (("17-expanse", 2, 6), ("14-code-four", 2, 8), ("21-codyco", 1, 4)):
        saved = backtest[entry_id].founder_list(PF)
        assert (len(saved["items"]), saved["picked"]) == (count, 0), entry_id
        assert vs.founder_duration(backtest[entry_id]) == {"count": weeks, "unit": "WEEKS"}, entry_id


def test_no_gallery_entry_types_the_founders_own_offer_and_the_transcript_says_so(backtest):
    for entry_id in corpus_mod.GALLERY:
        assert vs.offer_rows(backtest[entry_id]) == [], entry_id
        assert vs.offer_expectation(backtest[entry_id]) == vs.NO_OFFER_TYPED == "no own-offer row typed"
    # reported, never asserted: the transcript's `own_offer`, and a line in the bundle's markdown
    assert bt._offer_expectation(backtest["08-fresco"]) == vs.NO_OFFER_TYPED
    text = bt.markdown({"own_offer": vs.NO_OFFER_TYPED, "respondents": {}, "founder_screens": []})
    assert "Purchase friction's own offer (L32, spec 135): no own-offer row typed" in text


def test_the_answer_names_what_fits_and_the_rest_is_typed_on_the_check_screen(backtest):
    """The coordinator's decision (2026-11-04): Importance's Answer names the others that fit its 25 words, whole and in
    order; the rest are typed on the Check screen, never a stop -- every back-test entry walks."""
    for entry in backtest.values():
        vs.check_answer_box(entry)                                   # no stop on any of the 28
        vs.founder_inputs(entry)
        named, typed = vs.importance_named(entry), vs.importance_typed(entry)
        assert named + typed == vs.importance_others(entry), entry.id
        assert vs._words("; ".join(named)) <= vs.ANSWER_MAX_WORDS, entry.id
        assert vs.answer_text(entry, IMPORTANCE) == "; ".join(named), entry.id
        if typed:   # the next row would not have fit
            assert vs._words("; ".join(named + typed[:1])) > vs.ANSWER_MAX_WORDS, entry.id
        assert typed == R25_TYPED_ON_CHECK.get(entry.id, []), entry.id
    # countly and paidly name fewer by design, as before
    golden = {e.id: e for e in corpus_mod.load(KEEL_CLOUD, registry=fx.registry()).entries}
    assert [len(vs.importance_named(golden[e])) for e in ("01-countly", "05-paidly")] == [1, 2]


def test_a_single_row_longer_than_the_box_still_stops_at_load(tmp_path):
    raw = fx.raw_entry(fx.ENTRY)
    raw["founder_calibration"][IMPORTANCE]["answer"]["items"][1]["label"] = " ".join(["word"] * 26)
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw))
    with pytest.raises(vs.VectorsScriptError, match="is 26 words; the Answer box takes 25"):
        vs.check_answer_box(entry)


class _Corridor:
    """A Check screen that records what the walk asks of it."""
    def __init__(self):
        self.calls = []

    def list_check(self, question, **kw):
        self.calls.append((question["dimension"], kw))
        return {"screen": "check"}


def test_a_back_test_walk_types_the_rest_on_importances_check_screen(backtest):
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    for entry_id, rows in R25_TYPED_ON_CHECK.items():
        j = SimpleNamespace(entry=backtest[entry_id], strict=False, findings=[], corridor=_Corridor())
        assert cs._check_screen(j, {"dimension": IMPORTANCE}, IMPORTANCE) == {"screen": "check"}
        assert j.corridor.calls == [(IMPORTANCE, {"add": rows, "one_more": False})], entry_id
        assert [f["served"]["typed"] for f in j.findings] == rows
    # an entry whose Answer names them all types nothing there
    j = SimpleNamespace(entry=backtest["10-palus"], strict=False, findings=[], corridor=_Corridor())
    cs._check_screen(j, {"dimension": IMPORTANCE}, IMPORTANCE)
    assert j.corridor.calls == [(IMPORTANCE, {})] and j.findings == []
    # Current solution on a back-test still types its rungs through spec 067 FR-2's plan
    j = SimpleNamespace(entry=backtest["08-fresco"], strict=False, findings=[], corridor=_Corridor())
    cs._check_screen(j, {"dimension": "problem.current_solution_satisfaction"}, "problem.current_solution_satisfaction")
    assert list(j.corridor.calls[0][1]) == ["add_rungs"]


def test_each_typed_row_is_a_finding_never_a_stop(backtest):
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    j = SimpleNamespace(entry=backtest["14-code-four"], findings=[])
    cs._importance_typed_finding(j, vs.importance_typed(j.entry))
    assert [f["served"]["typed"] for f in j.findings] == ["Logging the evidence from the call"]
    assert j.findings[0]["what"].startswith("Importance: 'Logging the evidence from the call' typed on the Check screen")
    assert "named 3 of the founder's other difficulties" in j.findings[0]["what"]


def test_current_solutions_two_boxes_are_typed_apart_each_to_its_own_25_words(backtest):
    """The coordinator's decision (2026-11-04), keel-cloud's `VectorCorridorService` reading each box to 25: the first
    box is the entry's `current_solution.today`, the second the rungs that fit its own 25 words, in order; the rest are
    typed on the Check screen (spec 067 FR-2). The two are never counted together."""
    key = "problem.current_solution_satisfaction"
    for entry in backtest.values():
        first, second = vs.current_solution_boxes(entry)
        if entry.today():                       # the fourteen record what they do today; the rest type the phrase
            assert first.rstrip(".") == entry.today().rstrip("."), entry.id
        assert 0 < vs._words(first) <= vs.ANSWER_MAX_WORDS, entry.id
        assert 0 < vs._words(second) <= vs.ANSWER_MAX_WORDS, entry.id
        rungs = [i["label"] for i in entry.founder_list(key)["items"]][1 if vs.keels_working_first(entry) else 0:]
        fits = [k for k in range(1, len(rungs) + 1) if vs._words("; ".join(rungs[:k])) <= vs.ANSWER_MAX_WORDS]
        k = max(fits)
        assert second == vs._stopped("; ".join(rungs[:k])), entry.id      # as many whole rungs as fit, in order
        assert vs.answer_text(entry, key) == f"{first} {second}"
    # Fresco: 24 words of today no longer leave the second box empty (revision 25's first rung, keel-cloud 217)
    first, second = vs.current_solution_boxes(backtest["08-fresco"])
    assert vs._words(first) == 24 and second.startswith("Typed up within half an hour of the walk")


def test_voltairs_fact_is_read_as_code_serves_it_and_an_only_with_help_pick_is_refused(backtest, tmp_path):
    """Spec 137 (keel-cloud 213 FR-11a): the record now carries the fact's three codes (revision 24 amended in place), so
    it is read as recorded and the spec-135 shim reads nobody; an `only_with_help` pick is refused as no served code."""
    voltair = backtest["15-voltair"]
    assert corpus_mod._tested_kind(voltair) == "FACT" and not corpus_mod.r24_fact_read_as_three(voltair)
    assert corpus_mod.R24_FACT_FOUR == ()
    assert voltair.respondent_questions[COMPATIBILITY]["codes"] == list(corpus_mod.FACT_CODES)
    raw = yaml.safe_load(Path(voltair.path).read_text(encoding="utf-8"))
    raw["answers"][0].setdefault("picks", {})[COMPATIBILITY] = "only_with_help"
    with pytest.raises(corpus_mod.CorpusError, match="'only_with_help', not one of"):
        corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="15-voltair.yaml"), registry=fx.registry(),
                             backtest=True)


# ------------------------------------------------------------------------------- FR-3: the constitution

def test_the_cards_and_the_gallery_point_to_the_constitution():
    cards = (REPO / "quality" / "readers" / "dimensions.md").read_text(encoding="utf-8")
    head = cards.split("<!-- card:", 1)[0]
    assert "canon/designs/measured-beliefs/backtest/CONSTITUTION.md" in head and "corpus writer's law" in head
    names = (REPO / "instructions" / "gallery_names.toml").read_text(encoding="utf-8")
    assert "CONSTITUTION.md` section 9" in names and "only through the corpus writer's constitution's gate" in names
    if CONSTITUTION.is_file():
        assert "## 9. Before an entry enters the gallery" in CONSTITUTION.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------- FR-4: the recorded run

def test_the_recorded_fresco_run_stays_as_served():
    record = json.loads((REPO / "tests" / "fixtures" / "gallery" / "20261022T164045Z-backtest-08-fresco" /
                         "backtest.json").read_text(encoding="utf-8"))
    assert record["revision"] == 23
    plan = (REPO / "tests" / "fixtures" / "gallery" / "20261022T164045Z-backtest-08-fresco" / "export" /
            "plan.json").read_text(encoding="utf-8")
    assert "A trial on one live job" in plan, "the run of record is never reworded"
