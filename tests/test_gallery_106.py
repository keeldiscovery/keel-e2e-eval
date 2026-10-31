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
import shutil
from pathlib import Path

import pytest

from evals import backtest as bt
from evals import gallery as g
from evals import sample_export as se
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from quality import cycle, rubric
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


@pytest.fixture(autouse=True)
def _no_decisions(monkeypatch, tmp_path):
    """Spec 087: every cycle record here is read with no decision on file (as 079's tests read theirs)."""
    monkeypatch.setattr(cycle, "DECISIONS", tmp_path / "no-decisions.toml")


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




# ================================================================================ the export (FR-1, FR-2, FR-3, FR-4)

FRESCO_RUN = REPO / "tests" / "fixtures" / "gallery" / "20261022T164045Z-backtest-08-fresco"
BASE_SCORE = (REPO / "tests" / "fixtures" / "quality" / "cycle" / "scores" / "08-fresco" /
              "20261101-SOLUTION-r2-abcdef1-v13-claude-opus-5-5.json")
AT = "2026-10-31T09:00:00Z"
LATER = "2026-11-07T09:00:00Z"
DECISIONS = {"problem": "BUILD", "solution": "NOT_YET", "money": "KEEP_INTERVIEWING"}


def study_run(root: Path, entry: str, study: str, stamp: str, *, answered: int | None = None,
              decision: str | None = None) -> Path:
    """The gallery's fixture run copied as one study of `entry`, as a cycle with seven people walks it (spec 106 FR-2):
    the problem and solution studies the first seven of the person's own link, the money study (a B2B entry) the eight
    decision-makers; `answered` leaves the rest of the register OPENED; `decision` the standings' label."""
    d = Path(root) / f"{stamp}-backtest-{entry}"
    shutil.copytree(FRESCO_RUN, d)
    record = json.loads((d / bt.RECORD).read_text(encoding="utf-8"))
    record.update(scope=g.STUDY_SCOPE[study], run=d.name)
    record["entry"] = {**record["entry"], "id": entry, "path": f"backtest/{entry}.yaml"}
    (d / bt.RECORD).write_text(json.dumps(record), encoding="utf-8")
    path = d / "export" / "invitations.json"
    register = json.loads(path.read_text(encoding="utf-8"))
    rows = register["invitations"]
    keep = ([r for r in rows if r["respondentType"] == vs.LINK_B2B] if study == "money"
            else [r for r in rows if r["respondentType"] == vs.LINK_PRIMARY][:SEVEN])
    for r in keep[answered:] if answered is not None else []:
        r["status"] = "OPENED"
    register["invitations"] = keep
    path.write_text(json.dumps(register), encoding="utf-8")
    if decision:
        path = d / "export" / "standings.json"
        standings = json.loads(path.read_text(encoding="utf-8"))
        standings["facts"]["decision"]["label"] = decision
        path.write_text(json.dumps(standings), encoding="utf-8")
    return d


def cycle_runs(root: Path, entries=("08-fresco",), *, day: str = "20261031", skip=(), **kw) -> list[Path]:
    """One cycle's bundles: every entry's three studies (but `skip`: `(entry, study)` pairs), the problem study first."""
    out = []
    for i, entry in enumerate(entries):
        for j, study in enumerate(g.STUDIES):
            if (entry, study) not in skip:
                out.append(study_run(root, entry, study, f"{day}T{10 + i}{j}0000Z", decision=DECISIONS[study], **kw))
    return out


def score_file(scores: Path, run: Path, *, mark: int = 2, zero: bool = False, version: int | None = None,
               scored_at: str = "2026-10-31T12:00:00+00:00") -> Path:
    """A score file of `run` (spec 078 FR-4's shape, the 079 fixture's three screens), every mark `mark` -- 2 is
    100%, 1 is 50% -- and with `zero` one 0 (a flagged screen); the summary as the readers compute it."""
    obj = json.loads(BASE_SCORE.read_text(encoding="utf-8"))
    record = json.loads((run / bt.RECORD).read_text(encoding="utf-8"))
    obj.update(entry=record["entry"]["id"], scope=record["scope"], bundle=run.name, scored_at=scored_at)
    for screen in obj["screens"]:
        for crit in rubric.CRITERIA:
            if screen.get(crit) is not None:
                screen[crit] = mark
    if zero:
        obj["screens"][-1]["r1"] = 0
    obj["summary"] = rubric.summaries(obj["screens"], obj.get("insights") or [])
    if version is not None:
        obj["rubric_version"] = version
    path = scores / obj["entry"] / f"{run.name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


def scored(root: Path, scores: Path, *, mark: int = 2, day: str = "20261031", **kw) -> list[Path]:
    runs = cycle_runs(root, day=day, **kw)
    for run in runs:
        score_file(scores, run, mark=mark)
    return runs


def _row(out: Path, slug: str = "fresco") -> dict:
    return next(r for r in json.loads((out / g.INDEX).read_text(encoding="utf-8"))["examples"] if r["slug"] == slug)


def _manifest(out: Path, study: str, slug: str = "fresco") -> dict:
    return json.loads((out / slug / study / se.MANIFEST).read_text(encoding="utf-8"))


def _bytes(out: Path) -> dict:
    return {str(p.relative_to(out)): p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()}


# --------------------------------------------------------------------------- FR-1: three studies per example

def test_three_studies_are_exported_from_one_cycles_bundles(tmp_path):
    runs = cycle_runs(tmp_path / "runs")
    out = tmp_path / "sample"
    result = g.export(runs, out, exported_at=AT, provenance_dir=tmp_path / "prov")
    listed = json.loads((FRESCO_RUN / "export" / se.MANIFEST).read_text(encoding="utf-8"))["files"]
    assert sorted(p.name for p in (out / "fresco").iterdir()) == ["money", "problem", "solution"]
    for study, run in zip(g.STUDIES, runs):
        here = out / "fresco" / study
        assert sorted(str(p.relative_to(here)) for p in here.rglob("*") if p.is_file()) == \
            sorted([*listed, "interview.json", se.MANIFEST]), study
        standings = json.loads((here / "standings.json").read_text(encoding="utf-8"))
        assert standings["facts"]["decision"]["label"] == DECISIONS[study], "each study's own files"
        assert json.loads((here / "invitations.json").read_text(encoding="utf-8")) == \
            json.loads((run / "export" / "invitations.json").read_text(encoding="utf-8"))
    assert list(result["slugs"]["fresco"]) == list(g.STUDIES)


def test_the_index_row_carries_each_studys_own_figures_and_the_problem_studys_at_the_top(tmp_path):
    out = tmp_path / "sample"
    g.export(cycle_runs(tmp_path / "runs"), out, exported_at=AT, provenance_dir=tmp_path / "prov")
    row = _row(out)
    pilot, price = {"optedIn": 6, "finished": 20, "percent": 30}, {"edgeSaid": "$250 a month", "chose": 6, "n": 8}
    assert row["studies"] == {
        "problem": {"decision": "BUILD", "howSure": "MEDIUM", "pilot": pilot, "price": price, "answered": 7, "invited": 7},
        "solution": {"decision": "NOT_YET", "howSure": "MEDIUM", "pilot": pilot, "price": price, "answered": 7,
                     "invited": 7},
        "money": {"decision": "KEEP_INTERVIEWING", "howSure": "MEDIUM", "pilot": pilot, "price": price, "answered": 8,
                  "invited": 8}}
    assert list(row["studies"]["problem"]) == list(g.STUDY_FIGURES)
    # the old reader's fields: the problem study's
    assert (row["decision"], row["howSure"], row["pilot"], row["price"]) == ("BUILD", "MEDIUM", pilot, price)
    assert row["scope"] == "PROBLEM" and row["assumptions"] == _manifest(out, "problem")["assumptions"]
    assert row["interview"]["links"][0] == {"role": "PRIMARY", "label": "Construction superintendents", "items": 7}
    assert list(row)[-1] == "studies" and "scope_order" not in json.dumps(row)


def test_an_entry_missing_a_study_is_refused_by_name_and_nothing_is_written_for_it(tmp_path):
    runs = cycle_runs(tmp_path / "runs", entries=("08-fresco", "13-aircaps"), skip={("13-aircaps", "money")})
    said = []
    result = g.promote(runs, tmp_path / "sample", provenance_dir=tmp_path / "prov", exported_at=AT, say=said.append)
    assert said == ["refused 13-aircaps: no money study (COMMERCIAL) -- an example is three studies (problem, "
                    "solution, money), never a partial one; nothing is written for it"]
    assert [r["slug"] for r in result["index"]] == ["fresco"] and not (tmp_path / "sample" / "aircaps").exists()
    # the export itself never writes a partial example: the whole is refused, naming the entry
    with pytest.raises(g.GalleryRefused, match="13-aircaps: no money study") as refused:
        g.export(runs, tmp_path / "strict", exported_at=AT, provenance_dir=tmp_path / "prov2")
    assert not (tmp_path / "strict").exists() and not (tmp_path / "prov2").exists()
    assert len(refused.value.reasons) == 1


def test_a_study_given_twice_or_a_run_of_another_scope_is_set_aside_by_name(tmp_path):
    runs = cycle_runs(tmp_path / "runs")
    again = study_run(tmp_path / "runs", "08-fresco", "problem", "20261031T200000Z")
    whole = study_run(tmp_path / "runs", "08-fresco", "solution", "20261031T210000Z")
    record = json.loads((whole / bt.RECORD).read_text(encoding="utf-8"))
    (whole / bt.RECORD).write_text(json.dumps({**record, "scope": "ALL"}), encoding="utf-8")
    kept, reasons = g.three_studies([*runs, again, whole])
    assert kept == [] and reasons == [
        f"{whole.name}: a ALL run is not one of the gallery's three studies (problem = PROBLEM, solution = SOLUTION, "
        "money = COMMERCIAL) -- spec 106 FR-1",
        f"08-fresco: the problem study given 2 times ({runs[0].name}, {again.name}) -- nothing is written for it"]
    assert g.three_studies(runs) == (runs, [])


def test_the_scope_order_and_one_per_entry_are_retired():
    assert not hasattr(g, "one_per_entry")
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    target = makefile.split("\ngallery: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "SCOPE_ORDER" not in makefile and "scope-order" not in makefile and "scope_order" not in target
    assert '$(if $(BAR),--bar "$(BAR)",)' in target and '$(if $(CYCLE),--cycle "$(CYCLE)",)' in target
    assert "scope_order" not in (REPO / "quality" / "cycle.toml").read_text(encoding="utf-8").split("[gallery]")[1] \
        .split("#")[0]


# --------------------------------------------------------------------------- FR-2: the number, in words

def test_the_number_in_words():
    assert [g.number_words(n) for n in (1, 7, 8, 20, 21)] == ["one", "seven", "eight", "twenty", "21"]
    assert g.people_words(7) == "seven people answered" and g.people_words(1) == "one person answered"
    assert g.people_words(7, 6) == "six of the seven people invited answered"
    assert g.people_words(7, 0) == "none of the seven people invited answered"


def test_the_disclaimer_says_each_studys_own_people_never_twenty(tmp_path):
    runs = cycle_runs(tmp_path / "runs")
    shutil.rmtree(runs[1])
    runs[1] = study_run(tmp_path / "runs", "08-fresco", "solution", "20261031T101000Z", answered=6)
    out = tmp_path / "sample"
    g.export(runs, out, exported_at=AT, provenance_dir=tmp_path / "prov")
    row = _row(out)
    head = "A simulated study inspired by Fresco (Y Combinator Fall 2024): "
    assert row["disclaimer"] == _manifest(out, "problem")["disclaimer"] == (
        head + "seven people answered, all simulated. The founder's answers, the people and everything they said are "
        "fictional, written from Fresco's public material to show what Keel does. Not customer research about Fresco; "
        "not affiliated with Fresco or Y Combinator.")
    assert _manifest(out, "solution")["disclaimer"].startswith(head + "six of the seven people invited answered, all "
                                                               "simulated.")
    assert _manifest(out, "money")["disclaimer"].startswith(head + "eight people answered, all simulated.")
    assert row["studies"]["solution"]["answered"] == 6 and row["studies"]["solution"]["invited"] == 7
    for study in g.STUDIES:
        assert "twenty" not in _manifest(out, study)["disclaimer"]


def test_a_disclaimer_that_says_another_number_is_refused(tmp_path):
    runs = cycle_runs(tmp_path / "runs")
    s = g.prepare(g.load_names()[0], {st: g.read_run(r) for st, r in zip(g.STUDIES, runs)}, exported_at=AT)
    assert g.attribution_reasons(s) == []
    money = s.studies["money"]
    money.manifest = {**money.manifest, "disclaimer": g.load_names()[0].disclaimer(20)}
    assert "fresco: money/manifest: the disclaimer is missing or not the sentence for the money study's people " \
           "(eight people answered)" in g.attribution_reasons(s)
    s.studies["problem"].figures["invited"] = 0
    assert "fresco: the problem study invited nobody" in g.attribution_reasons(s)


def test_the_gallery_names_map_writes_no_disclaimer():
    text = (REPO / "instructions" / "gallery_names.toml").read_text(encoding="utf-8")
    assert "disclaimer =" not in text and "evals/gallery.py`'s DISCLAIMER" in text
    assert "twenty" not in g.DISCLAIMER and "{people}, all simulated" in g.DISCLAIMER


# --------------------------------------------------------------------------- FR-3: the gallery's own last score

def test_the_first_acceptance_passes_whatever_the_bar_and_is_recorded(tmp_path):
    scores, said = tmp_path / "scores", []
    runs = scored(tmp_path / "runs", scores, mark=1)                                     # 50%: far under the 90% bar
    result = g.promote(runs, tmp_path / "sample", scores_dir=scores, cycle="20261031-aaaaaaa",
                       provenance_dir=tmp_path / "prov", exported_at=AT, say=said.append)
    assert said == ["the gate: no accepted score yet: the first acceptance passes (score_pct 50.0%)"]
    assert result["accepted"] == {"cycle": "20261031-aaaaaaa", "score_pct": 50.0, "rubric_version": rubric.RUBRIC_VERSION}
    provenance = json.loads(Path(result["provenance"]).read_text(encoding="utf-8"))
    assert provenance["accepted"] == result["accepted"] and provenance["examples"][0]["cycle"] == "20261031-aaaaaaa"
    assert g.last_accepted(tmp_path / "prov") == {**result["accepted"], "file": f"provenance-{AT}.json"}


def test_a_cycle_below_the_last_accepted_is_refused_by_name_and_nothing_is_written(tmp_path):
    scores, out, prov = tmp_path / "scores", tmp_path / "sample", tmp_path / "prov"
    first = scored(tmp_path / "runs", scores, mark=2)                                     # 100%
    g.promote(first, out, scores_dir=scores, cycle="20261031-aaaaaaa", provenance_dir=prov, exported_at=AT,
              say=lambda _: None)
    before = _bytes(out)
    lower = scored(tmp_path / "runs2", scores, mark=1, day="20261107")                   # 50%
    with pytest.raises(g.GalleryRefused) as refused:
        g.promote(lower, out, scores_dir=scores, cycle="20261107-bbbbbbb", provenance_dir=prov, exported_at=LATER,
                  say=lambda _: None)
    assert refused.value.reasons == [
        f"the cycle's score_pct 50.0% is below the gallery's last accepted 100.0% (cycle 20261031-aaaaaaa, "
        f"provenance-{AT}.json) -- not promoted (spec 106 FR-3: the gate is the gallery's own last score); nothing "
        "is written"]
    assert not isinstance(refused.value, g.NothingToBuild)
    assert _bytes(out) == before and [p.name for p in prov.iterdir()] == [f"provenance-{AT}.json"]
    assert g.main(["--runs", ",".join(map(str, lower)), "--out", str(out), "--provenance-dir", str(prov),
                   "--scores", str(scores)]) == 1
    assert _bytes(out) == before


def test_equal_or_above_the_last_accepted_passes(tmp_path):
    scores, out, prov = tmp_path / "scores", tmp_path / "sample", tmp_path / "prov"
    g.promote(scored(tmp_path / "a", scores, mark=1), out, scores_dir=scores, cycle="c1", provenance_dir=prov,
              exported_at=AT, say=lambda _: None)
    said = []
    same = g.promote(scored(tmp_path / "b", scores, mark=1, day="20261101"), out, scores_dir=scores, cycle="c2",
                     provenance_dir=prov, exported_at="2026-11-01T09:00:00Z", say=said.append)
    assert same["accepted"]["score_pct"] == 50.0 and "at or above, promoted" in said[-1]
    above = g.promote(scored(tmp_path / "c", scores, mark=2, day="20261102"), out, scores_dir=scores, cycle="c3",
                      provenance_dir=prov, exported_at="2026-11-02T09:00:00Z", say=lambda _: None)
    assert above["accepted"] == {"cycle": "c3", "score_pct": 100.0, "rubric_version": rubric.RUBRIC_VERSION}
    assert g.last_accepted(prov)["cycle"] == "c3"


def test_the_gate_reads_the_cycles_score_over_its_studies(tmp_path):
    scores = tmp_path / "scores"
    runs = cycle_runs(tmp_path / "runs")
    for run, mark in zip(runs, (2, 2, 1)):
        score_file(scores, run, mark=mark)
    assert g.cycle_score(runs, scores) == 83.3                    # as the cycle record's head reads them together
    assert g.cycle_score(runs, tmp_path / "none") is None


def test_a_flagged_screen_still_refuses_and_takes_its_entry_with_it(tmp_path):
    scores, said = tmp_path / "scores", []
    runs = cycle_runs(tmp_path / "runs")
    for run in runs:
        score_file(scores, run, zero=run is runs[2])
    with pytest.raises(g.NothingToBuild):
        g.promote(runs, tmp_path / "sample", scores_dir=scores, provenance_dir=tmp_path / "prov", exported_at=AT,
                  say=said.append)
    assert said[0] == f"refused {runs[2].name} (08-fresco · COMMERCIAL): {runs[2].name}.json has 1 flagged screen(s)"
    assert said[-1].startswith("refused 08-fresco: no money study (COMMERCIAL)")
    assert not (tmp_path / "sample").exists() and not (tmp_path / "prov").exists()


def test_the_bar_is_an_optional_stricter_gate_off_by_default(tmp_path):
    scores = tmp_path / "scores"
    runs = scored(tmp_path / "runs", scores, mark=1)                                     # 50% each
    passing, refused = g.score_gate(runs, scores)
    assert passing == runs and refused == []
    passing, refused = g.score_gate(runs, scores, bar_pct=80)
    assert passing == [] and refused[0] == (f"{runs[0].name} (08-fresco · PROBLEM): {runs[0].name}.json has score_pct "
                                            "50.0% under the bar of 80%")
    assert g.main(["--runs", ",".join(map(str, runs)), "--out", str(tmp_path / "o"), "--provenance-dir",
                   str(tmp_path / "p"), "--scores", str(scores), "--bar", "80"]) == 1
    assert not (tmp_path / "o").exists()
    assert g.main(["--runs", ",".join(map(str, runs)), "--out", str(tmp_path / "o"), "--provenance-dir",
                   str(tmp_path / "p"), "--scores", str(scores)]) == 0


def test_a_last_score_at_another_rubric_version_or_before_106_is_never_compared(tmp_path):
    prov = tmp_path / "prov"
    prov.mkdir()
    (prov / "provenance-2026-10-23T00:00:00Z.json").write_text(json.dumps([{"slug": "fresco"}]))       # 063's list
    (prov / "provenance-2026-10-24T00:00:00Z.json").write_text(json.dumps({"accepted": None, "examples": []}))
    assert g.last_accepted(prov) is None
    refusal, compared = g.gate(10.0, None)
    assert refusal is None and "the first acceptance passes" in compared
    (prov / "provenance-2026-10-25T00:00:00Z.json").write_text(json.dumps(
        {"accepted": {"cycle": "old", "score_pct": 99.0, "rubric_version": rubric.RUBRIC_VERSION - 1}}))
    refusal, compared = g.gate(10.0, g.last_accepted(prov))
    assert refusal is None and "never compared" in compared
    refusal, _ = g.gate(None, {"cycle": "c", "score_pct": 50.0, "rubric_version": rubric.RUBRIC_VERSION, "file": "f"})
    assert "has no score_pct" in refusal


# --------------------------------------------------------------------------- FR-3 in make quality-accept

def _record(tmp_path: Path, name: str, runs: list[Path], scores: Path) -> Path:
    studies = []
    for run in runs:
        record = json.loads((run / bt.RECORD).read_text(encoding="utf-8"))
        path = scores / record["entry"]["id"] / f"{run.name}.json"
        obj = rubric.load_file(path)
        studies.append(cycle.Study(record["entry"]["id"], record["scope"], run.name, str(run), True, None, str(path),
                                   obj["summary"]["overall"]["score_pct"], obj["summary"]["overall"]["flagged_pct"]))
    cycles = tmp_path / "cycles"
    text, _ = cycle.compose(studies, name=name, why="cycle 4", door="host", cloud_sha="abcdef1", web_sha="1234567",
                            started="2026-10-31T10:00:00+00:00", ended="2026-10-31T11:00:00+00:00", seconds=60.0,
                            cfg=cycle.load_config(), baseline_path=tmp_path / "no-baseline.md", cycles_dir=cycles,
                            scores_dir=str(scores), people=SEVEN)
    cycles.mkdir(exist_ok=True)
    (cycles / f"{name}.md").write_text(text, encoding="utf-8")
    return cycles / f"{name}.md"


def _accept(tmp_path: Path, record: Path, today: str) -> int:
    return cycle.accept(["--cycle", str(record), "--runs-dir", str(tmp_path / "runs"), "--out", str(tmp_path / "sample"),
                         "--quality-out", str(tmp_path / "quality"), "--provenance-dir", str(tmp_path / "prov"),
                         "--today", today])


def test_accept_builds_the_three_studies_records_the_score_and_holds_the_next_cycle_to_it(tmp_path, capsys):
    scores = tmp_path / "scores"
    (tmp_path / "sample" / "fresco").mkdir(parents=True)
    (tmp_path / "sample" / "fresco" / "cover.jpg").write_bytes(b"JPEG")
    (tmp_path / "sample" / "fresco" / "standings.json").write_text("{}")                 # the one-study layout's
    (tmp_path / "sample" / "index.json").write_text(json.dumps({"examples": [
        {"slug": "fresco", "title": "AI documentation for construction supervisors", "decision": "OLD",
         "image": {"src": "/sample/fresco/cover.jpg", "alt": "A site"}}, {"slug": "karsa"}]}))
    first = _record(tmp_path, "20261031-abcdef1", scored(tmp_path / "runs", scores, mark=2), scores)
    assert _accept(tmp_path, first, "2026-10-31") == 0
    said = capsys.readouterr().out
    out = tmp_path / "sample"
    assert "gallery: the gate: no accepted score yet: the first acceptance passes (score_pct 100.0%)" in said
    assert "SCOPE_ORDER" not in said and "--bar" not in said and " BAR=" not in said
    assert "gallery: fresco         problem BUILD (7 of 7) · solution NOT_YET (7 of 7) · money KEEP_INTERVIEWING " \
           "(8 of 8)" in said
    assert "refreshed fresco; added none; left out of the index (their folders stay under OUT) karsa" in said
    assert "three studies an example, public/sample/<slug>/<problem|solution|money>/" in said
    assert sorted(p.name for p in (out / "fresco").iterdir()) == ["cover.jpg", "money", "problem", "solution"]
    row = _row(out)
    assert row["title"] == "AI documentation for construction supervisors" and row["image"]["alt"] == "A site"
    assert row["decision"] == "BUILD", "the export's own fields win; only keel-web's title, image and tests are kept"
    assert g.last_accepted(tmp_path / "prov")["cycle"] == "20261031-abcdef1"
    assert table_cut(tmp_path) == "2026-10-31"
    before = _bytes(out)
    # the next cycle scores lower: refused before anything is cut or written
    lower = _record(tmp_path, "20261107-abcdef1", scored(tmp_path / "runs", scores, mark=1, day="20261107"), scores)
    assert _accept(tmp_path, lower, "2026-11-07") == 1
    captured = capsys.readouterr()
    assert ("make quality-accept refuses: the cycle's score_pct 50.0% is below the gallery's last accepted 100.0% "
            "(cycle 20261031-abcdef1") in captured.err
    assert "the baseline is not cut and the gallery is left as it is" in captured.err
    assert table_cut(tmp_path) == "2026-10-31" and _bytes(out) == before
    # an equal one passes
    same = _record(tmp_path, "20261114-abcdef1", scored(tmp_path / "runs", scores, mark=2, day="20261114"), scores)
    assert _accept(tmp_path, same, "2026-11-14") == 0
    assert table_cut(tmp_path) == "2026-11-14" and g.last_accepted(tmp_path / "prov")["cycle"] == "20261114-abcdef1"


def table_cut(tmp_path: Path) -> str:
    from quality import table  # noqa: PLC0415

    return table.read_baseline(tmp_path / "quality" / "BASELINE.md")["cut"]


def test_accept_passes_the_scores_alone():
    source = (REPO / "quality" / "cycle.py").read_text(encoding="utf-8")
    body = source.split("\ndef accept(argv=None) -> int:\n", 1)[1].split("\ndef _snapshot_slugs", 1)[0]
    assert "gallery.promote(runs, out, names=names, scores_dir=scores_dir, cycle=stem, score_pct=score," in body
    assert "bar_pct" not in body and "one_per_entry" not in body and "scope_order" not in body
    assert body.index("gallery.gate(") < body.index("table.cut_baseline(")
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "BAR" not in makefile.split("\nquality-accept: venv\n", 1)[1].split("\n\n", 1)[0]


# --------------------------------------------------------------------------- FR-4: provenance and privacy

def test_the_provenance_names_cycle_entry_study_and_run_per_slug_outside_out(tmp_path):
    scores = tmp_path / "scores"
    runs = scored(tmp_path / "runs", scores)
    out, prov = tmp_path / "sample", tmp_path / "prov"
    result = g.promote(runs, out, scores_dir=scores, cycle="20261031-abcdef1", provenance_dir=prov, exported_at=AT,
                       say=lambda _: None)
    data = json.loads(Path(result["provenance"]).read_text(encoding="utf-8"))
    assert list(data) == ["exportedAt", "accepted", "examples"]
    assert data["examples"] == [{"slug": "fresco", "entry": "08-fresco", "cycle": "20261031-abcdef1",
                                 "studies": {st: {"scope": g.STUDY_SCOPE[st], "run": run.name, "cloud": "b2cf168",
                                                  "web": "9f3845a"} for st, run in zip(g.STUDIES, runs)},
                                 "renamed": {"from": [], "to": "Fresco"}}]
    assert out not in Path(result["provenance"]).parents
    everything = b"".join(_bytes(out).values()).decode("utf-8").lower()
    for needle in ("08-fresco", "20261031-abcdef1", "-backtest-", "/users/", *(r.name.lower() for r in runs)):
        assert needle not in everything, needle
    for block in (_row(out), *(_manifest(out, st) for st in g.STUDIES)):
        assert block["simulated"] is True and block["inspiredBy"]["name"] == "Fresco"
