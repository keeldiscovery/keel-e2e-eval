"""Spec 106 -- the gallery holds three studies per example, each from its own walk, with seven people.

FR-2 the seven-people walk: `vectors_script.study_people` narrowed by `Entry.people_cap` (the first seven on the
person's own link, in corpus order, the decision-makers whole), `make backtest PEOPLE=` / `KEEL_BACKTEST_PEOPLE`, and
`quality/cycle.toml`'s `people = 7` riding on every back-test of `make quality-walk`. The export's half (FR-1 three
studies, FR-2's number in words, FR-3 the gate, FR-4 provenance) is below it.

No browser, no stack, no model: the back-test files in keel-cloud's canon, the gallery's fixture run copied as one
cycle's three studies, and score files written here."""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from evals import backtest as bt
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from quality import cycle
from stack.config import load_config
from tests import v9_fixtures as fx

REPO = Path(__file__).resolve().parent.parent
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
SEVEN = 7


def _bt(name: str):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{name}.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {path}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


def _study(entry, scope: str, people: int | None = SEVEN):
    return dataclasses.replace(entry, scope=scope, people_cap=people)


def _names(people) -> list[str]:
    return [p.person for p in people]


def _own(entry) -> list[str]:
    return [p.person for p in entry.people() if p.link != vs.LINK_B2B]


def _deciders(entry) -> list[str]:
    return [p.person for p in entry.people() if p.link == vs.LINK_B2B]


# ------------------------------------------------------------------------------- FR-2: who a study sends

@pytest.mark.parametrize("name", ["08-fresco", "10-palus", "17-expanse", "21-codyco"])
def test_a_b2b_problem_and_solution_study_sends_the_first_seven_of_its_people(name):
    entry = _bt(name)
    assert vs.is_b2b(entry) and len(_own(entry)) > SEVEN
    for scope in ("PROBLEM", "SOLUTION"):
        study = _study(entry, scope)
        assert _names(vs.study_people(study)) == _own(entry)[:SEVEN], scope          # corpus order, no skipping
        assert _names(vs.person_inputs(study)) == _own(entry)[:SEVEN], scope
        assert {p.link for p in vs.person_inputs(study)} == {vs.LINK_PRIMARY}


@pytest.mark.parametrize("name", ["08-fresco", "10-palus", "17-expanse", "21-codyco"])
def test_a_b2b_money_study_sends_its_deciders_whole(name):
    """FR-2: *on a B2B money study its deciders* -- never narrowed. The spec says seven today; the canon says eight on
    08-fresco, 10-palus and 21-codyco and seven on 17-expanse (tasks.md: what the spec did not foresee)."""
    entry = _bt(name)
    money = _study(entry, "COMMERCIAL")
    assert _names(vs.study_people(money)) == _deciders(entry)
    assert _names(vs.study_people(money)) == _names(vs.study_people(_study(entry, "COMMERCIAL", None)))
    assert len(_deciders(entry)) == (7 if name == "17-expanse" else 8)


def test_a_b2c_entry_sends_its_first_seven_on_the_one_full_link():
    aircaps = _bt("13-aircaps")
    assert not vs.is_b2b(aircaps) and len(aircaps.people()) == 20
    for scope in ("PROBLEM", "SOLUTION", "COMMERCIAL"):
        assert _names(vs.study_people(_study(aircaps, scope))) == _names(aircaps.people())[:SEVEN], scope


def test_the_whole_study_caps_the_persons_link_and_keeps_every_decider():
    fresco = _bt("08-fresco")
    for scope in ("ALL", "SOLUTION_COMMERCIAL"):
        sent = _names(vs.study_people(_study(fresco, scope)))
        assert sent == [p.person for p in fresco.people() if p.person in _own(fresco)[:SEVEN] or
                        p.link == vs.LINK_B2B], scope


def test_no_cap_is_every_person_as_before():
    fresco = _bt("08-fresco")
    for scope in ("PROBLEM", "SOLUTION", "COMMERCIAL", "ALL"):
        assert vs.study_people(_study(fresco, scope, None)) == vs.study_people(dataclasses.replace(fresco, scope=scope))
    assert corpus_mod.Entry.__dataclass_fields__["people_cap"].default is None
    assert vs.capped(_study(fresco, "PROBLEM", None)) == []


def test_a_cap_over_the_list_sends_everyone():
    fresco = _bt("08-fresco")
    assert _names(vs.study_people(_study(fresco, "PROBLEM", 50))) == _own(fresco)
    assert vs.capped(_study(fresco, "PROBLEM", 50)) == []


def test_the_people_past_the_cap_are_named_with_their_reason():
    fresco = _bt("08-fresco")
    left, why = vs.not_on_study(_study(fresco, "PROBLEM"))
    assert left == [p.person for p in fresco.people() if p.person not in _own(fresco)[:SEVEN]]
    assert why == "; ".join([vs.NOT_ON_STUDY["PRIMARY_ONLY"], vs.NOT_ON_STUDY["PAST_THE_CAP"].format(n=SEVEN)])
    assert "past the study's first 7 on the person's own link" in why
    assert vs.capped(_study(fresco, "PROBLEM")) == _own(fresco)[SEVEN:]
    aircaps = _bt("13-aircaps")
    left, why = vs.not_on_study(_study(aircaps, "COMMERCIAL"))
    assert left == _names(aircaps.people())[SEVEN:] and why == vs.NOT_ON_STUDY["PAST_THE_CAP"].format(n=SEVEN)
    assert vs.not_on_study(_study(fresco, "COMMERCIAL")) == (_own(fresco), vs.NOT_ON_STUDY["DECIDERS_ONLY"])


def test_downstream_names_nobody_past_the_cap():
    """The follow-up lines and `inputs.json` are worked out over the study's people (spec 082 FR-1)."""
    study = _study(_bt("13-aircaps"), "SOLUTION")
    people = vs.person_inputs(study)
    past = set(vs.capped(study))
    assert len(people) == SEVEN and past and not past & set(vs.follow_up_lines(study, people))
    named = {p["person"] for p in vs.inputs_json(study, vs.founder_inputs(study), people)["people"]}
    assert named == {p.person for p in people} and not past & named


# ------------------------------------------------------------------------------- FR-2: PEOPLE= on the walk

def test_make_backtest_reads_people_and_refuses_what_is_not_a_number():
    assert bt.people({}) is None and bt.people({bt.PEOPLE_VAR: " 7 "}) == 7
    for raw in ("seven", "0", "-1", "7.5"):
        with pytest.raises(bt.UnknownDoor, match="is not a number of people"):
            bt.people({bt.PEOPLE_VAR: raw})
        assert "spec 106 FR-2" in bt.door_refusal({bt.PEOPLE_VAR: raw})
    assert bt.door_refusal({bt.PEOPLE_VAR: "7"}) is None
    assert bt.Backtest.__dataclass_fields__["people"].default is None


def test_the_runner_and_the_journey_carry_the_cap():
    runner = (REPO / "evals" / "run_backtest.py").read_text(encoding="utf-8")
    assert runner.count("people=backtest.people()") == 2                          # the KEEL door and the host door
    journey = (REPO / "evals" / "corpus_scenario.py").read_text(encoding="utf-8")
    assert 'people_cap = getattr(backtest, "people", None)' in journey
    assert "entry = dataclasses.replace(entry, people_cap=int(people_cap))" in journey
    assert journey.index("people_cap=int(people_cap)") < journey.index("people = vs.person_inputs(entry)")
    record = (REPO / "evals" / "backtest.py").read_text(encoding="utf-8")
    assert '**({"people": bt.people} if bt.people else {}),' in record


def test_the_makefile_passes_people_to_the_backtest_and_the_walk():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    back = makefile.split("\nbacktest:\n", 1)[1].split("\n\n", 1)[0]
    assert "$(if $(PEOPLE),KEEL_BACKTEST_PEOPLE=$(PEOPLE) ,)" in back
    walk = makefile.split("\nquality-walk: venv\n", 1)[1].split("\n\n", 1)[0]
    assert '$(if $(PEOPLE),--people "$(PEOPLE)",)' in walk


def test_the_cycle_sends_seven_people_a_study_by_default(tmp_path):
    cfg = cycle.load_config()
    assert cfg["people"] == SEVEN
    assert cycle.resolve_people("", cfg) == SEVEN and cycle.resolve_people("5", cfg) == 5
    with pytest.raises(cycle.Refused, match="PEOPLE='many' is not a number of people"):
        cycle.resolve_people("many", cfg)
    steps = cycle.plan_steps(["08-fresco"], ["PROBLEM", "COMMERCIAL"], "host", tmp_path, cfg["people"])
    back = [s["argv"][4:] for s in steps if s["what"] == "backtest"]
    assert back == [["backtest", "ENTRY=08-fresco", "SCOPE=PROBLEM", "DOOR=host", "PEOPLE=7"],
                    ["backtest", "ENTRY=08-fresco", "SCOPE=COMMERCIAL", "DOOR=host", "PEOPLE=7"]]
    assert all("PEOPLE=" not in " ".join(s["argv"]) for s in cycle.plan_steps(["08-fresco"], ["PROBLEM"], "host",
                                                                                tmp_path))


@pytest.mark.parametrize("value", ["0", "true", "'seven'", "7.0"])
def test_cycle_toml_refuses_people_that_is_not_a_number(tmp_path, value):
    text = (REPO / "quality" / "cycle.toml").read_text(encoding="utf-8").replace("people = 7", f"people = {value}")
    path = tmp_path / "cycle.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(cycle.Refused, match="is not a number of people"):
        cycle.load_config(path)


def test_the_record_names_the_people_only_when_the_walk_capped():
    from tests import test_quality_cycle_079 as t079  # noqa: PLC0415 - 079's fixture cycle

    _, data = t079.compose_the_fixture()
    assert "people" not in data, "a 079 record reads as it did"
    text, data = cycle.compose(t079.studies_of_the_fixture(), name="20261101-abcdef1", why="seven a study",
                               door="host", cloud_sha="abcdef1", web_sha="1234567", started="2026-11-01T10:00:00+00:00",
                               ended="2026-11-01T11:00:00+00:00", seconds=3600.0, cfg=cycle.load_config(),
                               baseline_path=t079.BASELINE, cycles_dir=t079.FX / "cycles", cloud_branch="master",
                               scores_dir=t079.SCORES_REL, entries_arg="08-fresco,09-karsa", people=SEVEN)
    assert data["people"] == SEVEN and "; 7 people a study on the person's own link (spec 106)." in text
    assert "DOOR=host PEOPLE=7 WHY=" in text


@pytest.fixture(autouse=True)
def _no_decisions(monkeypatch, tmp_path):
    monkeypatch.setattr(cycle, "DECISIONS", tmp_path / "no-decisions.toml")
