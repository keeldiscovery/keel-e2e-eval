"""Spec 135: the harness reads corpus revision 24 (owed by keel-cloud 215, keel-cloud-docs `0464e20f`).

FR-1 the loader reads the fourteen gallery entries at 24 and every other entry at 23 (`corpus.GALLERY`,
`GALLERY_REVISION`, `revision_of`), refusing by name a gallery file at 23 and any other file at 24; the diff 23 -> 24 is
the review's (spec 134's `corpus-rewording.md`) on the gallery and nothing anywhere else. FR-2 the scripted walk types
the new shapes (the three new codes, Fresco's pick at index 0 of two with its 2 weeks, AirCaps' four conditions, Issen's
pick on `speak_aloud`) and no gallery entry types the founder's own offer (`offer_rows` empty, the L32 expectation
*no own-offer row typed* reported in the transcript). FR-3 the constitution is pointed to from the cards file's head and
the gallery's map. FR-4 is `tests/test_gallery.py`'s (the recorded Fresco run marked 23, its compare skipped).

Two things revision 24 does that the review did not foresee, held here by name (tasks.md, *Left open*):

- **Six gallery entries' Importance no longer fits the 25-word Answer** (`R24_ANSWER_OVERFLOW`): the reworded rivals are
  longer, so the founder's Answer cannot name every other difficulty and spec 067 FR-1's stop (`check_answer_box`)
  refuses the walk at load, before any spend, naming the row it would drop. The stop is kept; the corpus owes the fix.
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

#: The six gallery entries whose revision-24 Importance rivals outrun the 25-word Answer, and the row each would drop
#: (the first that does not fit). Spec 067 FR-1's stop holds them at load; a keel-cloud corpus spec owes shorter rows.
R24_ANSWER_OVERFLOW = {"09-karsa": "Keeping cash at home safe",
                       "12-transload": "Finding freight sitting at the wrong door",
                       "13-aircaps": "Knowing who is talking in a group",
                       "14-code-four": "Logging the evidence from the call",
                       "15-voltair": "Spotting trees growing into the lines",
                       "20-lemma": "Finding an engineer free to dig in"}


def stops_at_the_answer_box(entry) -> bool:
    """For the tests that walk every back-test entry: True for a revision-24 entry the Answer box stops at load."""
    return entry.id in R24_ANSWER_OVERFLOW and entry.revision == corpus_mod.GALLERY_REVISION


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


# ------------------------------------------------------------------------------- FR-1: the loader and the pins

def test_the_gallery_is_the_maps_fourteen_and_keel_clouds():
    names = tomllib.loads((REPO / "instructions" / "gallery_names.toml").read_text(encoding="utf-8"))["gallery"]
    assert sorted(row["entry"] for row in names) == sorted(corpus_mod.GALLERY)
    assert len(corpus_mod.GALLERY) == 14 and corpus_mod.GALLERY_REVISION == 24 and corpus_mod.REVISION == 23
    assert [corpus_mod.revision_of(e) for e in ("08-fresco", "21-codyco", "22-andy-ai", "03-lullaby")] == [24, 24, 23, 23]


def test_every_entry_loads_at_its_revision(backtest):
    for entry in corpus_mod.load(KEEL_CLOUD, registry=fx.registry()).entries:
        assert entry.revision == 23, entry.id
    assert {e.id for e in backtest.values() if e.revision == 24} == set(corpus_mod.GALLERY)
    assert all(e.revision == 23 for e in backtest.values() if e.id not in corpus_mod.GALLERY)


def test_a_gallery_file_at_23_and_another_at_24_are_refused_by_name(tmp_path):
    old = tmp_path / "08-fresco.yaml"
    shutil.copy(_r23("08-fresco.yaml"), old)
    with pytest.raises(corpus_mod.CorpusError, match="revision is 23; this eval reads revision 24 for a gallery entry "
                                                     "only -- revision 23 is the gallery's rows before keel-cloud 215"):
        corpus_mod.load_file(old, backtest=True)
    raw = yaml.safe_load((corpus_mod.backtest_dir(KEEL_CLOUD) / "22-andy-ai.yaml").read_text(encoding="utf-8"))
    raw["revision"] = 24
    other = fx.write_entry(tmp_path, raw, name="22-andy-ai.yaml")
    with pytest.raises(corpus_mod.CorpusError, match="revision is 24; this eval reads revision 23 only -- revision 24 is "
                                                     "the gallery's alone"):
        corpus_mod.load_file(other, backtest=True)


def test_revision_24_moved_the_gallery_and_nothing_else():
    """The revision-23 records keel-cloud 215 kept: every entry outside the gallery is byte for byte its record; every
    gallery entry moved its revision line."""
    if not (MIRROR / "backtest-r23").is_dir():
        pytest.skip("no revision-23 records")
    for path in sorted(corpus_mod.backtest_dir(KEEL_CLOUD).glob("*.yaml")):
        before = (MIRROR / "backtest-r23" / path.name).read_text(encoding="utf-8")
        if path.stem in corpus_mod.GALLERY:
            assert (yaml.safe_load(before)["revision"], yaml.safe_load(path.read_text())["revision"]) == (23, 24)
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
    # AirCaps' Compatibility: four conditions, the pick on the first of the split pair
    saved = aircaps.founder_list(COMPATIBILITY)
    assert [i["code"] for i in saved["items"]][:2] == ["phone_with_them", "phone_online"] and len(saved["items"]) == 4
    typed = vs.saved_list(aircaps, COMPATIBILITY)
    assert len(typed["items"]) == 4 and typed["pickedIndex"] == 0
    assert typed["items"][0] == {"code": "item_1", "label": "had their phone with them", "asked": "was your phone with you"}


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
    for entry_id in ("17-expanse", "21-codyco"):
        assert len(backtest[entry_id].founder_list(PF)["items"]) == 2, entry_id


def test_no_gallery_entry_types_the_founders_own_offer_and_the_transcript_says_so(backtest):
    for entry_id in corpus_mod.GALLERY:
        assert vs.offer_rows(backtest[entry_id]) == [], entry_id
        assert vs.offer_expectation(backtest[entry_id]) == vs.NO_OFFER_TYPED == "no own-offer row typed"
    # reported, never asserted: the transcript's `own_offer`, and a line in the bundle's markdown
    assert bt._offer_expectation(backtest["08-fresco"]) == vs.NO_OFFER_TYPED
    text = bt.markdown({"own_offer": vs.NO_OFFER_TYPED, "respondents": {}, "founder_screens": []})
    assert "Purchase friction's own offer (L32, spec 135): no own-offer row typed" in text


def test_the_answer_box_stops_the_six_at_load_and_every_other_entry_fits(backtest):
    for entry in backtest.values():
        if stops_at_the_answer_box(entry):
            with pytest.raises(vs.VectorsScriptError, match=f"'{R24_ANSWER_OVERFLOW[entry.id]}' would be dropped"):
                vs.check_answer_box(entry)
            assert vs.answer_drops(entry, IMPORTANCE)[0] == R24_ANSWER_OVERFLOW[entry.id]
        else:
            vs.check_answer_box(entry)


def test_voltairs_fact_is_read_as_code_serves_it_and_an_only_with_help_pick_is_refused(backtest, tmp_path):
    voltair = backtest["15-voltair"]
    assert corpus_mod._tested_kind(voltair) == "FACT" and corpus_mod.r24_fact_read_as_three(voltair)
    assert voltair.respondent_questions[COMPATIBILITY]["codes"] == ["yes_easily", "yes_with_steps", "only_with_help", "no"]
    raw = yaml.safe_load(Path(voltair.path).read_text(encoding="utf-8"))
    raw["answers"][0].setdefault("picks", {})[COMPATIBILITY] = "only_with_help"
    with pytest.raises(corpus_mod.CorpusError, match="the registry's four on a fact"):
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
