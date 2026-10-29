"""Spec 082: the back-test under a scope -- the study's own people (FR-1), the cost box read when it is drawn (FR-2),
and a cycle record that names the walks that stopped and the sha that moved (FR-3).

Zero spend: the people from keel-cloud's back-test file and the golden B2B fixture, the cost step on a page double that
draws the *of* box only with the equation, the record composed from the 079 fixture cycle's score files.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

REPO = Path(__file__).resolve().parent.parent
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)


def _scoped(entry, scope: str):
    return dataclasses.replace(entry, scope=scope)


@pytest.fixture(scope="module")
def fresco():
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "08-fresco.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {path}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


# ------------------------------------------------------------------------------- FR-1: the study's own people

def test_08_fresco_under_problem_and_solution_is_its_primary_people_alone(fresco):
    """FR-1: the cycle's KeyError 'COMMERCIAL_B2B' -- 08-fresco's eight B2B people are the money study's (keel-cloud
    133); under PROBLEM and SOLUTION the walk sends the twelve PRIMARY people and nobody else."""
    primary = [p.person for p in fresco.people() if p.link == vs.LINK_PRIMARY]
    b2b = [p.person for p in fresco.people() if p.link == vs.LINK_B2B]
    assert vs.is_b2b(fresco) and len(primary) == 12 and len(b2b) == 8
    for scope in ("PROBLEM", "SOLUTION"):
        people = vs.person_inputs(_scoped(fresco, scope))
        assert [p.person for p in people] == primary, scope
        assert {p.link for p in people} == {vs.LINK_PRIMARY}, scope


def test_08_fresco_under_all_and_commercial_is_every_person_in_the_file(fresco):
    """FR-1: the money study and the whole study send every person, as before."""
    everyone = [p.person for p in fresco.people()]
    for entry in (fresco, _scoped(fresco, "ALL"), _scoped(fresco, "COMMERCIAL")):
        assert [p.person for p in vs.person_inputs(entry)] == everyone, vs.scope_of(entry)
    assert vs.study_people(_scoped(fresco, "SOLUTION_COMMERCIAL")) == list(fresco.people())


def test_a_b2b_entry_under_a_scope_names_nobody_downstream_who_was_not_sent():
    """FR-1: the follow-up lines, the themes screen and `inputs.json` read the list that comes back -- under PROBLEM
    and SOLUTION no decision-maker is owed a line or written into the inputs; under ALL they are, as before."""
    entry = fx.entry(fx.ENTRY_B2B)
    deciders = {p.person for p in entry.people() if p.link == vs.LINK_B2B}
    assert deciders and deciders & set(vs.follow_up_lines(entry, vs.person_inputs(entry)))
    for scope in ("PROBLEM", "SOLUTION"):
        seed = _scoped(entry, scope)
        people = vs.person_inputs(seed)
        assert not deciders & {p.person for p in people}, scope
        lines = vs.follow_up_lines(seed, people)
        assert lines and not deciders & set(lines), (scope, lines)
        assert {p.person: p.follow_up for p in people if p.follow_up} == {k: v for k, v in lines.items() if v}
        inputs = vs.inputs_json(seed, vs.founder_inputs(seed), people)
        named = {p["person"] for p in inputs["people"]}
        assert named == {p.person for p in people} and not deciders & named, scope
        themes = vs.generate(seed).screens["THEMES"]
        assert themes == vs.themes_entries(seed, vs.walked_follow_ups(seed, people)), scope


def test_the_scope_reaches_person_inputs_through_the_entry_not_a_parameter():
    """FR-1: `corpus_scenario` and `scope_journey` replace `entry.scope` before they build the people; no new
    parameter."""
    import inspect                                                     # noqa: PLC0415

    from evals import corpus_scenario, scope_journey                   # noqa: PLC0415
    assert list(inspect.signature(vs.person_inputs).parameters) == ["entry"]
    source = inspect.getsource(corpus_scenario)
    at_replace = source.index("entry = dataclasses.replace(entry, scope=scope)")
    assert at_replace < source.index("people = vs.person_inputs(entry)", at_replace)
    walk = inspect.getsource(scope_journey)
    assert walk.index("entry.scope != scope") < walk.index("people = vs.person_inputs(entry)")


# ------------------------------------------------------------------------ FR-2: the cost box read when it is drawn

class _Box:
    """One locator on the page double: present or not, by the page's state at the moment it is asked."""

    def __init__(self, page, key: str):
        self.page, self.key = page, key

    @property
    def first(self):
        return self

    def count(self) -> int:
        return 1 if self.page.drawn(self.key) else 0

    def input_value(self) -> str:
        self.page.log.append(("read", self.key))
        return self.page.values[self.key]

    def inner_text(self) -> str:
        self.page.log.append(("read", self.key))
        return self.page.texts[self.key]

    def click(self) -> None:
        self.page.press(self.key)

    def fill(self, value: str) -> None:
        self.page.log.append(("fill", self.key))
        self.page.values[self.key] = value

    def wait_for(self, state: str = "visible", timeout: float = 0) -> None:
        if not self.page.drawn(self.key):
            raise TimeoutError(f"{self.key} never drawn")


class _ChainPage:
    """keel-web 123's cost step as `FounderControl` draws it: *Per* (`chain-unit`, its helper) from the start, the
    equation -- and inside it the *of* box (`chain-base`, `#chain-base-help`) on a way with the box, and on hours the
    rate and its note -- only once a mode, a unit and a period are picked (`ready`)."""

    def __init__(self):
        self.mode = self.period = None
        self.log: list[tuple[str, str]] = []
        self.values = {"chain-unit": "superintendent", "chain-base": "job", "chain-rate": "80", "chain-low": "",
                       "chain-high": "", "chain-count": ""}
        self.texts = {"#chain-unit-help": vs_screens.CHAIN_UNIT_HELP, "[data-testid=chain-equation]":
                      "40 to 80 hours of job · per superintendent · a month", "[data-testid=chain-per]":
                      "per superintendent · a month", ".calib__note": vs_screens.HOURLY_RATE_DEFAULTED}

    @property
    def ready(self) -> bool:
        return bool(self.mode and self.values["chain-unit"] and self.period)

    def drawn(self, key: str) -> bool:
        if key in ("chain-unit", "#chain-unit-help") or key.startswith(("chain-mode-", "chain-period-")):
            return True
        if key in ("chain-equation", "[data-testid=chain-equation]", "[data-testid=chain-per]", "chain-low",
                   "chain-high", "chain-measure-percent", "chain-measure-count", "chain-count"):
            return self.ready
        if key in ("chain-base", "#chain-base-help"):
            return self.ready and self.mode in ("HOURS", "RATE")
        if key in ("chain-rate", ".calib__note"):
            return self.ready and self.mode == "HOURS"
        raise AssertionError(f"the double draws no {key}")

    def press(self, key: str) -> None:
        self.log.append(("press", key))
        if key.startswith("chain-mode-"):
            self.mode = key.removeprefix("chain-mode-")
        elif key.startswith("chain-period-"):
            self.period = key.removeprefix("chain-period-")

    def get_by_test_id(self, testid: str) -> _Box:
        return _Box(self, testid)

    def locator(self, selector: str, has_text: str | None = None) -> _Box:
        if has_text is not None and has_text != self.texts.get(selector):
            return _Box(self, "#never")
        return _Box(self, selector)

    def evaluate(self, script: str):
        return [10, 20, 30]

    @property
    def help_text(self) -> str:
        return vs_screens.CHAIN_HOURS_BASE_HELP if self.mode == "HOURS" else vs_screens.CHAIN_BASE_HELP


def _never_drawn(page: _ChainPage):
    original = page.drawn

    def drawn(key: str) -> bool:
        return False if key == "#never" else original(key)
    page.drawn = drawn
    return page


def _chain_cost(cost: dict) -> tuple[dict, _ChainPage]:
    page = _never_drawn(_ChainPage())
    page.texts["#chain-base-help"] = ""
    corridor = vs_screens.Corridor.__new__(vs_screens.Corridor)
    corridor.page = page
    original_press = page.press

    def press(key: str) -> None:
        original_press(key)
        page.texts["#chain-base-help"] = page.help_text
    page.press = press
    return corridor._chain_cost(cost), page


@pytest.mark.parametrize("mode", ["HOURS", "RATE"])
def test_the_of_box_is_read_after_the_period_once_the_equation_is_drawn(mode):
    """FR-2: on a fresh draft the *of* box is not on the page until the period is picked (cycle 1's 13-aircaps and
    17-expanse COMMERCIAL read None there); `_chain_cost` reads *Per* first, as before, then *of* and its helper -- and
    on hours the rate -- after the period pill, once `chain-equation` is visible."""
    cost = {"mode": mode, "unit": "superintendent", "period": "month", "low": 40, "high": 80, "base": "job",
            "measure": "%", "rate": None}
    seen, page = _chain_cost(cost)
    filled = seen["filled"]
    assert filled["unit"] == "superintendent" and filled["unit_help"] == vs_screens.CHAIN_UNIT_HELP
    assert filled["base"] == "job" and filled["base_help"] == page.help_text
    log = page.log
    period = log.index(("press", "chain-period-month"))
    assert log.index(("read", "chain-unit")) < log.index(("press", f"chain-mode-{mode}")) < period
    assert period < log.index(("read", "chain-base")) and period < log.index(("read", "#chain-base-help"))
    assert log.index(("read", "chain-base")) < log.index(("fill", "chain-low")), "read before anything is typed in it"
    if mode == "HOURS":
        assert filled["rate"] == "80" and filled["rate_note"] == vs_screens.HOURLY_RATE_DEFAULTED
        assert period < log.index(("read", "chain-rate"))
    else:
        assert "rate" not in filled and log.index(("read", "chain-base")) < log.index(("fill", "chain-base"))


def test_on_money_no_of_box_is_drawn_and_none_is_read():
    seen, page = _chain_cost({"mode": "AMOUNT", "unit": "superintendent", "period": "month", "low": 400, "high": 900})
    assert seen["filled"]["base"] is None and seen["filled"]["base_help"] is None
    assert ("read", "chain-base") not in page.log


def test_the_step_and_the_docstring_say_when_the_box_is_read():
    """FR-2: the step's wording and `_hold_the_cost_fill`'s docstring; the pins are unchanged."""
    import inspect                                                     # noqa: PLC0415

    from evals import corpus_scenario as cs                            # noqa: PLC0415
    source = inspect.getsource(cs._hold_the_cost_fill)
    assert "before anything is typed; " in source and "the equation is drawn (keel-web 123)" in source
    assert "Spec 082 FR-2" in source
    for pin in ('owed["base_help"] = vs_screens.CHAIN_HOURS_BASE_HELP if mode == "HOURS" else '
                'vs_screens.CHAIN_BASE_HELP', 'assert filled.get("rate_note") == vs_screens.HOURLY_RATE_DEFAULTED',
                'assert at <= base, {"the rate sits under what the time goes on"'):
        assert pin in source, pin


# ------------------------------------------------------------------- FR-3: the record names the walks that stopped

from quality import cycle, table                                       # noqa: E402
from tests import test_quality_cycle_079 as c079                       # noqa: E402

CYCLE_1 = REPO / "quality" / "cycles" / "20261028-88bfce8.md"
STOP = ("the context is confirmed on the wire: the four fields, the sentence -- the card's, word for word (keel-cloud "
        "146 FR-2)")


def _two_stopped_and_a_moved_sha() -> list[cycle.Study]:
    """The 079 fixture cycle's four studies, two of them stopped early (one at a named step, one outside any step, as
    cycle 1's KeyError walks), and the third walked on keel-cloud bcdef12 though the kick-off pinned abcdef1."""
    first, second, third, fourth = c079.studies_of_the_fixture()
    first = dataclasses.replace(first, passed=False, failed_step=STOP)
    second = dataclasses.replace(second, passed=False, failed_step=None)
    third = dataclasses.replace(third, cloud_sha="bcdef12", web_sha="1234567")
    return [first, second, third, fourth]


def _compose(tmp_path, studies):
    return cycle.compose(studies, name="20261101-abcdef1", why="spec 082's fixture", door="host", cloud_sha="abcdef1",
                         web_sha="1234567", started="2026-11-01T10:00:00+00:00", ended="2026-11-01T11:00:00+00:00",
                         seconds=3600.0, cfg=cycle.load_config(), baseline_path=c079.BASELINE, cycles_dir=tmp_path,
                         cloud_branch="master", scores_dir=c079.SCORES_REL)


WALKS_LINE = ("  - 2 of 4 walks reached their end; 2 stopped early (08-fresco · PROBLEM -- the context is confirmed on "
              "the wire; 08-fresco · SOLUTION -- no step named (stopped outside a step)); their scores are of the "
              "screens served before the stop")
MOVED_LINE = "  - keel-cloud moved mid-cycle: abcdef1 -> bcdef12 from 09-karsa · COMMERCIAL"


def test_the_record_head_names_the_walks_that_stopped_and_the_sha_that_moved(tmp_path):
    """FR-3: one line under the score -- N of M walks reached their end, K stopped (study -- the step, each), their
    scores of the screens served before the stop -- and the sha that moved mid-cycle, named, never refused."""
    text, data = _compose(tmp_path, _two_stopped_and_a_moved_sha())
    head = text.split("## The head\n\n", 1)[1].split("\n\n", 1)[0].splitlines()
    assert head[0].startswith("- **This cycle**: score_pct **95.6%**")
    assert head[1] == WALKS_LINE and head[2] == MOVED_LINE
    assert head[3].startswith("- **The baseline**") and head[4].startswith("- **The bar**")
    walks = data["walks"]
    assert walks["walks"] == 4 and walks["ended"] == 2 and walks["pins"] == {"keel-cloud": "abcdef1",
                                                                             "keel-web": "1234567"}
    assert walks["moved"] == [{"repo": "keel-cloud", "from": "abcdef1", "to": "bcdef12",
                               "study": "09-karsa · COMMERCIAL"}]
    assert [s["cloud_sha"] for s in data["studies"]] == [None, None, "bcdef12", None], "each study's own sha kept"
    assert data["studies"][0]["failed_step"] == STOP, "the data block keeps the whole step"
    assert data["head"]["score_pct"] == 95.6, "the scores are the screens served, as before"


def test_the_table_head_carries_the_same_lines(tmp_path):
    text, _ = _compose(tmp_path, _two_stopped_and_a_moved_sha())
    record = tmp_path / "20261101-abcdef1.md"
    record.write_text(text, encoding="utf-8")
    out = tmp_path / "TABLE.md"
    assert table.main(["--scores-dir", str(c079.SCORES), "--out", str(out), "--cycle", str(record),
                       "--baseline-file", str(c079.BASELINE)]) == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    at = next(i for i, line in enumerate(lines) if line.startswith("- **This cycle**"))
    assert lines[at + 1] == WALKS_LINE and lines[at + 2] == MOVED_LINE
    assert lines[at + 3].startswith("- **The baseline**")


def test_a_whole_cycle_says_so_and_names_no_move(tmp_path):
    text, data = _compose(tmp_path, c079.studies_of_the_fixture())
    assert "  - 4 of 4 walks reached their end; 0 stopped early\n" in text
    assert data["walks"]["moved"] == [] and "moved mid-cycle" not in text


def test_cycle_1_is_read_from_its_studies_and_score_files_and_never_rewritten():
    """FR-3: the record of cycle 1 is not rewritten (it carries no `walks`); TABLE.md's head reads the same facts from
    its studies and its score files' headers -- 2 of 15 walks, 13 stopped, keel-cloud 88bfce8 -> f7b0e05 at 10-palus
    COMMERCIAL."""
    record = cycle.load_record(CYCLE_1)
    assert "walks" not in record and "moved mid-cycle" not in CYCLE_1.read_text(encoding="utf-8")
    walks = cycle.table_head(record)["walks"]
    assert (walks["walks"], walks["ended"], len(walks["stopped"])) == (15, 2, 13)
    assert walks["moved"] == [{"repo": "keel-cloud", "from": "88bfce8", "to": "f7b0e05",
                               "study": "10-palus · COMMERCIAL"}]
    steps = {s["study"]: s["step"] for s in walks["stopped"]}
    assert steps["13-aircaps · COMMERCIAL"] == steps["17-expanse · COMMERCIAL"] == "the cost step"
    assert steps["21-codyco · PROBLEM"] == "no step named (stopped outside a step)"
    # the head as the table renders it for THIS cycle (the committed TABLE.md carries the latest cycle's head, so it
    # moved on when cycle 2 was walked, 2026-10-28; the facts of cycle 1 are read from its own record and score files)
    its_files = {Path(s["score_file"]).name for s in record["studies"] if s.get("score_file")}
    files = [f for f in table.load_scores() if Path(f["_path"]).name in its_files]
    assert len(files) == 15
    rendered = table.render(files, cycle=cycle.table_head(record))
    assert "  - 2 of 15 walks reached their end; 13 stopped early (08-fresco · PROBLEM -- " in rendered
    assert "  - keel-cloud moved mid-cycle: 88bfce8 -> f7b0e05 from 10-palus · COMMERCIAL" in rendered
    assert "respondent: score_pct 84.6%, spoken_pct 75.0%, insights_pct 93.8%, flagged 0.0% of 12 screens" in rendered


def test_the_walk_records_each_studys_sha_and_names_a_move_without_refusing(tmp_path, capsys):
    """FR-3: `make quality-walk` pins the shas at kick-off; a study whose bundle says another sha is recorded with it,
    and the walk goes on."""
    import json                                                        # noqa: PLC0415
    from types import SimpleNamespace                                  # noqa: PLC0415

    from evals import backtest as bt                                   # noqa: PLC0415
    runs = tmp_path / "runs"
    score = REPO / c079._score("08-fresco", "20261101", "SOLUTION")

    def fake(argv, stdout=None, stderr=None):
        if argv[4] == "backtest":
            run = runs / "20261101T110000Z-backtest-08-fresco"
            run.mkdir(parents=True)
            (run / bt.RECORD).write_text(json.dumps({"run": run.name, "passed": True, "scope": "SOLUTION",
                                                     "founder_screens": [{}], "stack": {"keel-cloud": "bcdef129",
                                                                                         "keel-web": "1234567"}}))
            stdout.write(f"run bundle: {run}\n")
        if argv[4] == "read-screens":
            out = Path(argv[6].split("=", 1)[1])
            out.mkdir(parents=True)
            (out / "score-path.txt").write_text(f"{score}\n")
        return SimpleNamespace(returncode=0)

    steps = [s for s in cycle.plan_steps(["08-fresco"], ["SOLUTION"], "host", tmp_path / "work") if s["study"]]
    study = cycle.walk_one("08-fresco", "SOLUTION", steps, door="host", runner=fake, runs_dir=runs)
    assert (study.cloud_sha, study.web_sha) == ("bcdef12", "1234567") and study.score_file
    import inspect                                                     # noqa: PLC0415
    source = inspect.getsource(cycle.walk)
    assert "recorded, not refused" in source and "cloud7, web7 = git_sha(cloud), git_sha(web)" in source
