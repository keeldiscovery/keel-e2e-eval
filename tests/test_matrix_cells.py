"""Stackless tests for `matrix/cells.toml` and its reader (spec 020-matrix-workflow; keel-cloud
`canon/designs/e2e-matrix-design.md` §5).

Two halves, and the first is the one that matters.

**The file as it stands must meet the coverage rules.** Not "the validator can express them" --
the real `matrix/cells.toml`, the one the workflow reads, is asserted here cell by cell. The rules
are **spec 021's**, not §5.2's, because the founder changed the sets on 2026-09-11 and the design
section they came from is the one being amended:

1. `per_change` is macOS and Windows, each host, the current Python, the **short** journey, S-012
   alone -- four cells.
2. `nightly` runs every one of those four again at **full** length, plus Windows on the 3.9 floor,
   both hosts -- six cells -- and the corpus scenarios ride on exactly one of them, macOS x Claude.
3. **Ubuntu is in neither cheap set** ("fewer than 5% of founders") and is in `weekly`, whole.
4. `weekly` **is** the product of the axes, eighteen cells, every one of them full.
5. Every cell everywhere is a combination the axes allow, no set names a cell twice, and `legs` is
   `short` or `full` and defaults to `full`.

A cells.toml that drifts from those fails `make unit` before it costs a runner minute.

**And the reader must refuse a bad file loudly.** The `select` job is the cheapest place in the
whole matrix to fail -- before a role is assumed, before a box is deployed, before a model is asked
anything -- so every malformation below is a `CellsError` naming the cell, with every problem in
one message rather than the first one found.
"""

from __future__ import annotations

import itertools
import json
import textwrap

import pytest

from matrix import cells as m


@pytest.fixture(scope="module")
def matrix() -> m.Matrix:
    """The real file. Every assertion about coverage is about this one, never a fixture's."""
    return m.load()


def write(tmp_path, body: str):
    path = tmp_path / "cells.toml"
    path.write_text(textwrap.dedent(body))
    return path


MINIMAL = """
    [axes]
    os = ["ubuntu-24.04", "macos-latest", "windows-latest"]
    host = ["claude", "copilot"]
    python = ["3.9", "3.13"]

    [scenarios]
    default = ["s012"]
    live = ["s004", "s012"]

    [sets]
    per_change = [{ os = "ubuntu-24.04", host = "claude", python = "3.9" }]
    nightly = []
    weekly = []
"""



#: A file whose `per_change` is the right four, with the other two sets left empty -- so a rule
#: about `nightly` or `weekly` can be caught failing without every `per_change` rule tripping
#: alongside it and hiding which one was under test.
PER_CHANGE_FOUR = MINIMAL.replace(
    'per_change = [{ os = "ubuntu-24.04", host = "claude", python = "3.9" }]',
    '\n'.join([
        'per_change = [',
        '    { os = "macos-latest", host = "claude", python = "3.13", legs = "short" },',
        '    { os = "macos-latest", host = "copilot", python = "3.13", legs = "short" },',
        '    { os = "windows-latest", host = "claude", python = "3.13", legs = "short" },',
        '    { os = "windows-latest", host = "copilot", python = "3.13", legs = "short" },',
        ']',
    ]))

# ---------------------------------------------------------------- the file, as the design wants it

def test_the_real_file_loads_and_validates(matrix):
    m.validate(matrix)
    assert m.coverage_problems(matrix) == []


def test_the_three_sets_are_exactly_the_designs_three(matrix):
    assert tuple(matrix.sets) == m.SET_NAMES == ("per_change", "nightly", "weekly")


def test_every_cell_everywhere_is_a_combination_the_axes_allow(matrix):
    for set_name, cells in matrix.sets.items():
        for cell in cells:
            assert cell.os in matrix.axes["os"], f"{set_name}: {cell.id}"
            assert cell.host in matrix.all_hosts, f"{set_name}: {cell.id}"
            assert cell.python in matrix.axes["python"], f"{set_name}: {cell.id}"


def test_the_axes_are_the_designs_axes(matrix):
    # §5.1's three runner labels and two hosts, verbatim; the Python axis carries the floor, the
    # current, and the 3.12 §4.3's own picker sample shows -- which is what makes §5.2's eighteen
    # and six arithmetic (3 x 2 x 3 and 1 x 2 x 3) rather than aspiration.
    assert matrix.axes["os"] == ("ubuntu-24.04", "macos-latest", "windows-latest")
    assert matrix.axes["host"] == ("claude", "copilot")
    assert matrix.axes["python"] == ("3.9", "3.12", "3.13")
    # keel-runtime spec 008: Codex runs and is not measured, so it is bought (nightly) and not owed
    # (per_change, the weekly product). It moves into `host` the day the gate is green for it.
    assert matrix.unmeasured_hosts == ("codex",)
    assert matrix.all_hosts == ("claude", "copilot", "codex")


def test_per_change_is_four_cells(matrix):
    """Spec 021, the founder's decision of 2026-09-11. Six became four when Ubuntu left, and each
    of the four buys the short journey rather than the whole one."""
    assert len(matrix.sets["per_change"]) == 4


def test_per_change_is_macos_and_windows_once_per_host(matrix):
    covered = sorted((c.os, c.host) for c in matrix.sets["per_change"])
    assert covered == sorted(itertools.product(["macos-latest", "windows-latest"],
                                               matrix.axes["host"]))


def test_per_change_is_the_current_python_everywhere(matrix):
    for cell in matrix.sets["per_change"]:
        assert cell.python == "3.13", cell.id


def test_per_change_runs_the_short_journey_and_only_the_journey(matrix):
    """The two halves of what makes the cheap set cheap: two model jobs instead of thirteen, and
    nothing riding along beside them."""
    for cell in matrix.sets["per_change"]:
        assert cell.legs == "short", cell.id
        assert cell.scenarios == ("s012",), cell.id


def test_ubuntu_is_in_the_weekly_set_and_nowhere_else(matrix):
    """*"Fewer than 5% of founders"* -- so Ubuntu is bought once a week rather than once a merge.
    It is not dropped, and this asserts both halves of that."""
    for name in ("per_change", "nightly"):
        assert not [c.id for c in matrix.sets[name] if c.os.startswith("ubuntu")], name
    assert len([c for c in matrix.sets["weekly"] if c.os.startswith("ubuntu")]) == 6


def test_nightly_is_six_plugin_cells_one_speckit_cell_and_one_unmeasured_host(matrix):
    nightly = matrix.sets["nightly"]
    measured = [c for c in nightly if c.install == "plugin" and c.host in matrix.axes["host"]]
    assert len(measured) == 6
    unmeasured = [c for c in nightly if c.host in matrix.unmeasured_hosts]
    assert [(c.os, c.host, c.python, c.legs, c.install) for c in unmeasured] == [
        ("macos-latest", "codex", "3.13", "full", "plugin"),
        ("windows-latest", "codex", "3.13", "full", "plugin")]
    speckit = [c for c in nightly if c.install == "speckit"]
    assert [(c.os, c.host, c.python, c.legs) for c in speckit] == [("macos-latest", "claude", "3.13", "short")]
    assert speckit[0].id == "macos-latest-claude-py3.13-speckit"


def test_the_speckit_cell_is_nightlys_alone(matrix):
    for name, cells in matrix.sets.items():
        if name != "nightly":
            assert not [c for c in cells if c.install == "speckit"], name


def test_nightly_buys_whole_what_a_merge_bought_short(matrix):
    """The rule that makes the short per-change journey safe: everything a merge measured in part
    is measured in full within the day, on the same cell."""
    full = {(c.os, c.host, c.python) for c in matrix.sets["nightly"] if c.legs == "full"}
    for cell in matrix.sets["per_change"]:
        assert (cell.os, cell.host, cell.python) in full, cell.id


def test_nightly_keeps_the_39_floor_that_per_change_gave_up(matrix):
    """spec 004's floor is a promise. It moved from per_change to nightly rather than being
    dropped -- Windows, both hosts, every night."""
    floor = [c for c in matrix.sets["nightly"] if c.python == "3.9"]
    assert sorted(c.id for c in floor) == ["windows-latest-claude-py3.9",
                                           "windows-latest-copilot-py3.9"]


def test_nightly_carries_the_corpus_on_exactly_one_claude_cell(matrix):
    # decision 11: "the nightly set carries the corpus scenarios on one cell ... they cost nothing
    # but minutes on a Claude cell already paid for".
    carriers = [c for c in matrix.sets["nightly"]
                if {"s005", "s006", "s007"} <= set(c.scenarios)]
    assert len(carriers) == 1
    assert carriers[0].host == "claude"
    assert carriers[0].os == "macos-latest", "spec 021: the Ubuntu cell it used to ride is gone"
    # And it still runs the journey: the corpus rides on a cell, it does not replace one.
    assert "s012" in carriers[0].scenarios


def test_weekly_is_the_full_product(matrix):
    weekly = {(c.os, c.host, c.python) for c in matrix.sets["weekly"]}
    assert weekly == matrix.product
    assert len(matrix.sets["weekly"]) == 18


# ------------------------------------------------------------- an unmeasured host (spec 008)

UNMEASURED = MINIMAL.replace('host = ["claude", "copilot"]',
                             'host = ["claude", "copilot"]\n    host_unmeasured = ["codex"]')


def test_an_unmeasured_host_is_allowed_in_nightly_and_weekly_and_never_owed(tmp_path):
    body = UNMEASURED.replace("nightly = []", 'nightly = [{ os = "macos-latest", host = "codex", python = "3.13" }]') \
                     .replace("weekly = []", 'weekly = [{ os = "ubuntu-24.04", host = "codex", python = "3.9" }]')
    loaded = m.load(write(tmp_path, body))
    assert loaded.unmeasured_hosts == ("codex",)
    assert [c.id for c in loaded.sets["nightly"]] == ["macos-latest-codex-py3.13"]
    problems = m.coverage_problems(loaded)
    # per_change still owes the measured hosts and nothing about codex; weekly's product is the
    # measured hosts' and the codex cell is neither missing nor unexpected.
    assert not any("codex" in p for p in problems), problems


def test_an_unmeasured_host_in_per_change_is_refused(tmp_path):
    body = UNMEASURED.replace(
        'per_change = [{ os = "ubuntu-24.04", host = "claude", python = "3.9" }]',
        'per_change = [{ os = "macos-latest", host = "codex", python = "3.13", legs = "short" }]')
    problems = m.coverage_problems(m.load(write(tmp_path, body)))
    assert any("also names" in p and "codex" in p for p in problems), problems


def test_a_host_cannot_be_both_measured_and_unmeasured(tmp_path):
    body = MINIMAL.replace('host = ["claude", "copilot"]',
                           'host = ["claude", "copilot"]\n    host_unmeasured = ["copilot"]')
    with pytest.raises(m.CellsError, match="one or the other"):
        m.load(write(tmp_path, body))


def test_a_host_outside_both_lists_is_still_refused(tmp_path):
    body = UNMEASURED.replace("nightly = []", 'nightly = [{ os = "macos-latest", host = "cursor", python = "3.13" }]')
    with pytest.raises(m.CellsError, match="cursor"):
        m.load(write(tmp_path, body))


def test_weekly_is_the_whole_journey_everywhere(matrix):
    assert {c.legs for c in matrix.sets["weekly"]} == {"full"}


def test_nothing_but_per_change_is_short(matrix):
    """One set is short; the other two are what confirms it was enough. The nightly's one Spec
    Kit cell is short by design (spec 022): it proves the road, and the plugin cells beside it
    prove the runtime at full length."""
    assert {c.legs for c in matrix.sets["nightly"] if c.install == "plugin"} == {"full"}
    assert {c.legs for c in matrix.sets["per_change"]} == {"short"}


def test_every_cell_runs_at_least_one_scenario(matrix):
    for set_name, cells in matrix.sets.items():
        for cell in cells:
            assert cell.scenarios, f"{set_name}: {cell.id} runs nothing"


def test_the_default_scenario_is_the_journey(matrix):
    assert matrix.default_scenarios == ("s012",)


def test_the_live_scenarios_are_the_two_marked_live(matrix):
    # The two `@pytest.mark.live` modules in evals/, and no others: everything else is free.
    assert set(matrix.live) == {"s004", "s012"}


def test_ids_are_unique_within_every_set(matrix):
    for set_name, cells in matrix.sets.items():
        ids = [c.id for c in cells]
        assert len(ids) == len(set(ids)), set_name


# --------------------------------------------------------------------------- what a cell hands out

def test_a_cells_id_is_os_host_python():
    cell = m.Cell(os="windows-latest", host="copilot", python="3.9", scenarios=("s012",))
    assert cell.id == "windows-latest-copilot-py3.9"


def test_a_cells_dict_carries_everything_the_job_needs():
    cell = m.Cell(os="ubuntu-24.04", host="claude", python="3.13",
                  scenarios=("s012", "s005", "s006"))
    entry = cell.as_dict(live=("s004", "s012"))
    assert entry == {
        "id": "ubuntu-24.04-claude-py3.13",
        "os": "ubuntu-24.04",
        "host": "claude",
        "python": "3.13",
        "scenarios": ["s012", "s005", "s006"],
        "legs": "full",
        "install": "plugin",
        "live_k": "s012",
        "eval_k": "s005 or s006",
    }


# ------------------------------------------------------------------------------ legs (spec 021)

def test_a_cell_that_says_nothing_about_legs_runs_the_whole_journey():
    """The default is what every cell written before spec 021 meant, so adding the field changed
    no existing cell's behaviour."""
    cell = m.Cell(os="ubuntu-24.04", host="claude", python="3.13", scenarios=("s012",))
    assert cell.legs == "full" == m.DEFAULT_LEGS
    assert cell.as_dict(live=("s012",))["legs"] == "full"


def test_legs_is_read_off_the_file_and_reaches_the_workflow(tmp_path):
    path = write(tmp_path, MINIMAL.replace('python = "3.9" }', 'python = "3.9", legs = "short" }'))
    cell = m.load(path).sets["per_change"][0]
    assert cell.legs == "short"
    assert cell.as_dict(live=("s012",))["legs"] == "short"


def test_legs_is_not_part_of_a_cells_id():
    """A cell is one (OS, host, Python). The same cell appearing short in per_change and full in
    nightly is one runner job in two sets, not two cells -- and its id is its founder in the
    twin's picker, which cannot be two people (§4.3)."""
    short = m.Cell(os="macos-latest", host="claude", python="3.13", scenarios=("s012",),
                   legs="short")
    full = m.Cell(os="macos-latest", host="claude", python="3.13", scenarios=("s012",))
    assert short.id == full.id == "macos-latest-claude-py3.13"


def test_legs_outside_the_two_is_refused_by_name(tmp_path):
    path = write(tmp_path, MINIMAL.replace('python = "3.9" }', 'python = "3.9", legs = "half" }'))
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    message = str(excinfo.value)
    assert "half" in message and "short" in message and "full" in message


def test_the_harness_and_the_matrix_agree_on_what_legs_there_are():
    """`matrix/cells.py` restates them rather than importing, so that `python -m matrix` stays
    stdlib-only. This is the seam that keeps the restatement true."""
    from harness import agent_host

    assert set(m.LEGS) == set(agent_host.LEGS)
    assert m.DEFAULT_LEGS == agent_host.DEFAULT_LEGS


def test_the_two_selectors_are_pytest_k_expressions():
    cell = m.Cell(os="ubuntu-24.04", host="claude", python="3.13",
                  scenarios=("s012", "s004", "s005"))
    assert cell.k(("s004", "s012")) == "s012 or s004"          # in the cell's own order
    assert cell.k(("s005",)) == "s005"


def test_a_cell_with_no_free_scenarios_says_so_with_an_empty_selector():
    # The workflow reads "" as "do not run `make eval` at all": an empty `-k` would collect every
    # scenario in evals/, which on a remote profile is a bill nobody asked for.
    cell = m.Cell(os="ubuntu-24.04", host="claude", python="3.13", scenarios=("s012",))
    assert cell.as_dict(live=("s012",))["eval_k"] == ""


def test_every_cell_in_every_set_is_json_serialisable(matrix):
    for set_name in m.SET_NAMES:
        json.dumps(matrix.as_matrix(set_name))


def test_as_matrix_is_the_list_a_github_strategy_takes(matrix):
    entries = matrix.as_matrix("per_change")
    assert isinstance(entries, list) and len(entries) == 4
    assert all(set(e) == {"id", "os", "host", "python", "scenarios", "legs", "install", "live_k", "eval_k"}
               for e in entries)


# ------------------------------------------------------------------------------ narrowing by id

def test_cells_can_be_narrowed_to_one_id(matrix):
    # §13 step 5: "workflow_dispatch with one cell first (ubuntu / claude / 3.13)".
    chosen = matrix.cells("weekly", ["ubuntu-24.04-claude-py3.13"])
    assert [c.id for c in chosen] == ["ubuntu-24.04-claude-py3.13"]


def test_narrowing_keeps_the_order_asked_for(matrix):
    ids = ["windows-latest-copilot-py3.9", "ubuntu-24.04-claude-py3.13"]
    assert [c.id for c in matrix.cells("weekly", ids)] == ids


def test_narrowing_ignores_blank_entries(matrix):
    # "a,b," and "" are both what a workflow input hands over when a human types loosely.
    assert len(matrix.cells("per_change", "".split(","))) == 4
    assert len(matrix.cells("per_change", ["macos-latest-claude-py3.13", " ", ""])) == 1


def test_narrowing_to_a_cell_the_set_does_not_have_raises_by_name(matrix):
    with pytest.raises(m.CellsError) as excinfo:
        matrix.cells("per_change", ["ubuntu-24.04-claude-py3.12"])
    assert "ubuntu-24.04-claude-py3.12" in str(excinfo.value)


def test_an_unknown_set_raises_naming_the_ones_there_are(matrix):
    with pytest.raises(m.CellsError) as excinfo:
        matrix.cells("hourly")
    assert "per_change" in str(excinfo.value)


# ----------------------------------------------------------------------- the reader refuses badly

def test_a_missing_file_raises_with_the_path(tmp_path):
    with pytest.raises(m.CellsError) as excinfo:
        m.load(tmp_path / "nope.toml")
    assert "nope.toml" in str(excinfo.value)


def test_broken_toml_raises_rather_than_half_loading(tmp_path):
    path = write(tmp_path, "[axes\nos = 1")
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    assert "not valid TOML" in str(excinfo.value)


def test_a_minimal_file_loads(tmp_path):
    loaded = m.load(write(tmp_path, MINIMAL))
    assert [c.id for c in loaded.sets["per_change"]] == ["ubuntu-24.04-claude-py3.9"]


def test_an_os_outside_the_axis_is_refused_by_name(tmp_path):
    path = write(tmp_path, MINIMAL.replace('os = "ubuntu-24.04", host = "claude"',
                                           'os = "ubuntu-20.04", host = "claude"'))
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    assert "ubuntu-20.04" in str(excinfo.value)


def test_a_python_outside_the_axis_is_refused(tmp_path):
    path = write(tmp_path, MINIMAL.replace('python = "3.9" }', 'python = "3.8" }'))
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    assert "3.8" in str(excinfo.value)


def test_a_cell_missing_an_axis_is_refused(tmp_path):
    path = write(tmp_path, MINIMAL.replace(
        '{ os = "ubuntu-24.04", host = "claude", python = "3.9" }',
        '{ os = "ubuntu-24.04", python = "3.9" }'))
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    assert "missing a host" in str(excinfo.value)


def test_an_unknown_key_on_a_cell_is_refused(tmp_path):
    path = write(tmp_path, MINIMAL.replace(
        'python = "3.9" }', 'python = "3.9", runner = "self-hosted" }'))
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    assert "runner" in str(excinfo.value)


def test_a_set_that_names_a_cell_twice_is_refused(tmp_path):
    twice = ('per_change = [{ os = "ubuntu-24.04", host = "claude", python = "3.9" },'
             ' { os = "ubuntu-24.04", host = "claude", python = "3.9" }]')
    path = write(tmp_path, MINIMAL.replace(
        'per_change = [{ os = "ubuntu-24.04", host = "claude", python = "3.9" }]', twice))
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    assert "more than once" in str(excinfo.value)


def test_a_missing_set_is_refused(tmp_path):
    path = write(tmp_path, MINIMAL.replace("weekly = []", ""))
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    assert "weekly" in str(excinfo.value)


def test_every_problem_is_reported_at_once(tmp_path):
    path = write(tmp_path, MINIMAL.replace(
        '{ os = "ubuntu-24.04", host = "claude", python = "3.9" }',
        '{ os = "ubuntu-20.04", host = "gemini", python = "3.8" }'))
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    message = str(excinfo.value)
    assert "ubuntu-20.04" in message and "gemini" in message and "3.8" in message


def test_a_cell_may_override_the_default_scenarios(tmp_path):
    path = write(tmp_path, MINIMAL.replace(
        'python = "3.9" }', 'python = "3.9", scenarios = ["s005"] }'))
    assert m.load(path).sets["per_change"][0].scenarios == ("s005",)


def test_a_cell_with_an_empty_scenario_list_is_refused(tmp_path):
    path = write(tmp_path, MINIMAL.replace(
        'python = "3.9" }', 'python = "3.9", scenarios = [] }'))
    with pytest.raises(m.CellsError) as excinfo:
        m.load(path)
    assert "runs no scenarios" in str(excinfo.value)


# ------------------------------------------------------------------ the coverage rules, as rules

def test_coverage_catches_a_per_change_set_that_misses_a_combination(tmp_path):
    problems = m.coverage_problems(m.load(write(tmp_path, MINIMAL)))
    assert any("once per host" in p for p in problems)


def test_coverage_catches_a_per_change_cell_on_ubuntu(tmp_path):
    """Ubuntu back in the cheap set is the decision of 2026-09-11 being undone by accident."""
    problems = m.coverage_problems(m.load(write(tmp_path, MINIMAL)))
    assert any("ubuntu-24.04" in p for p in problems), problems


def test_coverage_catches_a_per_change_cell_that_runs_the_whole_journey(tmp_path):
    body = PER_CHANGE_FOUR.replace(', legs = "short" }', ' }', 1)
    problems = m.coverage_problems(m.load(write(tmp_path, body)))
    assert any("SHORT journey" in p for p in problems), problems


def test_coverage_catches_a_per_change_cell_carrying_a_corpus_scenario(tmp_path):
    body = PER_CHANGE_FOUR.replace(
        ', legs = "short" }', ', legs = "short", scenarios = ["s012", "s005"] }', 1)
    problems = m.coverage_problems(m.load(write(tmp_path, body)))
    assert any("cheap set stopping being cheap" in p for p in problems), problems


def test_coverage_catches_a_per_change_cell_off_the_current_python(tmp_path):
    body = PER_CHANGE_FOUR.replace('python = "3.13", legs = "short" }',
                                   'python = "3.9", legs = "short" }', 1)
    problems = m.coverage_problems(m.load(write(tmp_path, body)))
    assert any("current Python" in p for p in problems), problems


def test_coverage_catches_a_nightly_that_wandered_onto_ubuntu(tmp_path):
    body = PER_CHANGE_FOUR.replace(
        "nightly = []",
        'nightly = [{ os = "ubuntu-24.04", host = "claude", python = "3.13" }]')
    problems = m.coverage_problems(m.load(write(tmp_path, body)))
    assert any("leaves 'ubuntu'" in p for p in problems), problems


def test_coverage_catches_a_nightly_that_never_buys_the_short_cells_whole(tmp_path):
    """The rule the short per-change journey rests on: what a merge measures in part, the night
    measures in full, on the same cell, within the day."""
    problems = m.coverage_problems(m.load(write(tmp_path, PER_CHANGE_FOUR)))
    assert any("bought short on a merge and never bought whole" in p for p in problems), problems


def test_coverage_catches_a_nightly_that_drops_the_floor(tmp_path):
    problems = m.coverage_problems(m.load(write(tmp_path, PER_CHANGE_FOUR)))
    assert any("spends no cell on Python 3.9" in p for p in problems), problems


def test_coverage_catches_a_weekly_cell_that_runs_short(tmp_path):
    body = MINIMAL.replace(
        "weekly = []",
        'weekly = [{ os = "macos-latest", host = "claude", python = "3.13", legs = "short" }]')
    problems = m.coverage_problems(m.load(write(tmp_path, body)))
    assert any("full journey everywhere" in p for p in problems), problems


def test_coverage_catches_a_weekly_that_is_not_the_full_product(tmp_path):
    body = MINIMAL.replace(
        "weekly = []",
        'weekly = [{ os = "macos-latest", host = "claude", python = "3.13" }]')
    problems = m.coverage_problems(m.load(write(tmp_path, body)))
    assert any("full product" in p for p in problems)


def test_validate_raises_when_coverage_is_wrong(tmp_path):
    with pytest.raises(m.CellsError):
        m.validate(m.load(write(tmp_path, MINIMAL)))


# ------------------------------------------------------------------------------------ the CLI

def test_the_cli_prints_the_three_sets(capsys):
    assert m.main([]) == 0
    out = capsys.readouterr().out
    for name in m.SET_NAMES:
        assert name in out
    assert "ubuntu-24.04-claude-py3.9" in out


def test_the_cli_prints_one_set_when_asked(capsys):
    assert m.main(["--set", "nightly"]) == 0
    out = capsys.readouterr().out
    assert "nightly" in out and "per_change" not in out
    assert "ubuntu-24.04" not in out, "spec 021: Ubuntu is weekly"


def test_the_cli_prints_how_far_each_cell_goes(capsys):
    """A founder reading `make matrix-check` before a merge is reading what it will cost, and
    `short` against `full` is most of that cost."""
    assert m.main(["--set", "per_change"]) == 0
    out = capsys.readouterr().out
    assert "short" in out
    assert "full" not in out


def test_the_cli_emits_json_for_the_workflow(capsys):
    assert m.main(["--set", "per_change", "--json"]) == 0
    entries = json.loads(capsys.readouterr().out)
    assert len(entries) == 4
    assert entries[0]["id"] == "macos-latest-claude-py3.13"
    assert entries[0]["legs"] == "short"


def test_the_cli_narrows_to_the_cells_input(capsys):
    assert m.main(["--set", "weekly", "--cells",
                   "ubuntu-24.04-claude-py3.13,windows-latest-copilot-py3.9", "--json"]) == 0
    entries = json.loads(capsys.readouterr().out)
    assert [e["id"] for e in entries] == ["ubuntu-24.04-claude-py3.13",
                                          "windows-latest-copilot-py3.9"]


def test_the_cli_exits_two_and_says_why_on_a_bad_file(tmp_path, capsys):
    path = write(tmp_path, MINIMAL.replace('python = "3.9" }', 'python = "3.8" }'))
    assert m.main(["--file", str(path)]) == 2
    assert "3.8" in capsys.readouterr().err


def test_the_cli_refuses_json_without_a_set(capsys):
    with pytest.raises(SystemExit):
        m.main(["--json"])
    assert "--set" in capsys.readouterr().err
