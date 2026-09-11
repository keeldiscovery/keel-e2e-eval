"""Stackless tests for `matrix/cells.toml` and its reader (spec 020-matrix-workflow; keel-cloud
`canon/designs/e2e-matrix-design.md` §5).

Two halves, and the first is the one that matters.

**The file as it stands must meet the design's coverage rules.** Not "the validator can express
them" -- the real `matrix/cells.toml`, the one the workflow reads, is asserted here cell by cell:
per_change covers every OS once per host and spends at least one cell on the 3.9 floor, nightly is
Ubuntu only, weekly is the full product of the axes, and every cell everywhere is a combination the
axes allow. A cells.toml that drifts from §5.2 fails `make unit` before it costs a runner minute.

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
            assert cell.host in matrix.axes["host"], f"{set_name}: {cell.id}"
            assert cell.python in matrix.axes["python"], f"{set_name}: {cell.id}"


def test_the_axes_are_the_designs_axes(matrix):
    # §5.1's three runner labels and two hosts, verbatim; the Python axis carries the floor, the
    # current, and the 3.12 §4.3's own picker sample shows -- which is what makes §5.2's eighteen
    # and six arithmetic (3 x 2 x 3 and 1 x 2 x 3) rather than aspiration.
    assert matrix.axes["os"] == ("ubuntu-24.04", "macos-latest", "windows-latest")
    assert matrix.axes["host"] == ("claude", "copilot")
    assert matrix.axes["python"] == ("3.9", "3.12", "3.13")


def test_per_change_is_six_cells(matrix):
    assert len(matrix.sets["per_change"]) == 6


def test_per_change_runs_every_os_once_per_host(matrix):
    covered = sorted((c.os, c.host) for c in matrix.sets["per_change"])
    assert covered == sorted(itertools.product(matrix.axes["os"], matrix.axes["host"]))


def test_per_change_spends_the_floor_on_ubuntu_and_the_current_elsewhere(matrix):
    # §5.2: "each OS once per host; Python 3.9 on the Ubuntu cells, 3.13 elsewhere".
    for cell in matrix.sets["per_change"]:
        assert cell.python == ("3.9" if cell.os.startswith("ubuntu") else "3.13"), cell.id


def test_per_change_touches_the_floor_at_least_once(matrix):
    assert any(c.python == "3.9" for c in matrix.sets["per_change"])


def test_nightly_is_ubuntu_only(matrix):
    assert {c.os for c in matrix.sets["nightly"]} == {"ubuntu-24.04"}


def test_nightly_is_six_cells_both_hosts_every_python(matrix):
    nightly = matrix.sets["nightly"]
    assert len(nightly) == 6
    assert sorted((c.host, c.python) for c in nightly) == sorted(
        itertools.product(matrix.axes["host"], matrix.axes["python"]))


def test_nightly_carries_the_corpus_on_exactly_one_claude_cell(matrix):
    # decision 11: "the nightly set carries the corpus scenarios on one cell ... they cost nothing
    # but minutes on a Claude cell already paid for".
    carriers = [c for c in matrix.sets["nightly"]
                if {"s005", "s006", "s007"} <= set(c.scenarios)]
    assert len(carriers) == 1
    assert carriers[0].host == "claude"
    # And it still runs the journey: the corpus rides on a cell, it does not replace one.
    assert "s012" in carriers[0].scenarios


def test_weekly_is_the_full_product(matrix):
    weekly = {(c.os, c.host, c.python) for c in matrix.sets["weekly"]}
    assert weekly == matrix.product
    assert len(matrix.sets["weekly"]) == 18


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
        "live_k": "s012",
        "eval_k": "s005 or s006",
    }


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
    assert isinstance(entries, list) and len(entries) == 6
    assert all(set(e) == {"id", "os", "host", "python", "scenarios", "live_k", "eval_k"}
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
    assert len(matrix.cells("per_change", "".split(","))) == 6
    assert len(matrix.cells("per_change", ["ubuntu-24.04-claude-py3.9", " ", ""])) == 1


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
    assert any("every OS once per host" in p for p in problems)


def test_coverage_catches_a_nightly_that_leaves_ubuntu(tmp_path):
    body = MINIMAL.replace(
        "nightly = []",
        'nightly = [{ os = "macos-latest", host = "claude", python = "3.13" }]')
    problems = m.coverage_problems(m.load(write(tmp_path, body)))
    assert any("Ubuntu only" in p for p in problems)


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
    assert "windows-latest" not in out


def test_the_cli_emits_json_for_the_workflow(capsys):
    assert m.main(["--set", "per_change", "--json"]) == 0
    entries = json.loads(capsys.readouterr().out)
    assert len(entries) == 6
    assert entries[0]["id"] == "ubuntu-24.04-claude-py3.9"


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
