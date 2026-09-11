"""Reads `matrix/cells.toml`, validates it, and hands out cells (spec 020-matrix-workflow;
keel-cloud `canon/designs/e2e-matrix-design.md` §5).

**One reader, two callers.** `.github/workflows/matrix.yml`'s `select` job runs
`python -m matrix --set <name> --json` and `make matrix-check` runs `python -m matrix`; they are
the same code over the same file, so a founder who edits `cells.toml` finds out on their own Mac
what the workflow would have found out on a runner -- before the runner spends a model request on
it. Nothing here touches the network, a stack, a runner or a secret: it is a TOML file, three
coverage rules and a JSON dump.

**What a cell is** (§5.3): one (OS, host, Python) combination run once, as one runner job, with a
list of scenarios. Its `id` -- `<os>-<host>-py<python>` -- is the whole of its identity: the job's
name, the artifact's name, and `KEEL_REMOTE_CELL`, which is what `stack/remote.py` names the
founder it registers with the twin's picker, which is what the founder reads the next morning
(§4.3). So ids are unique within a set, and the validator says so.

**Why the scenarios are split into two lists.** `s012` (and `s004`) are `-m live`: a real host CLI,
a real model, real money, `make eval-live`. `s005`/`s006`/`s007` are not: they drive the product's
own judgement against the frozen corpus and call no model at all. One cell can carry both -- the
nightly's Claude cell does (decision 11) -- so each cell offers the two pytest `-k` expressions its
workflow step needs, and either may be empty.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

#: The file. One directory, one name, no search path: a second cells.toml somewhere else would be
#: a second matrix nobody knew about.
CELLS_TOML = Path(__file__).resolve().parent / "cells.toml"

#: The three named sets, in the order §5.2 tables them (cheap, nightly, everything).
SET_NAMES = ("per_change", "nightly", "weekly")


class CellsError(ValueError):
    """`cells.toml` says something the design does not allow. Raised with **every** problem found,
    not the first -- a founder editing the file wants the whole list in one pass, and the workflow's
    `select` job is the cheapest place in the matrix to fail."""


@dataclass(frozen=True)
class Cell:
    """One runner job. Frozen because a cell that could be edited after validation is a cell the
    validator never saw."""

    os: str
    host: str
    python: str
    scenarios: tuple[str, ...]

    @property
    def id(self) -> str:
        """`ubuntu-24.04-claude-py3.9`. The job name, the artifact name, and `KEEL_REMOTE_CELL`."""
        return f"{self.os}-{self.host}-py{self.python}"

    def k(self, which: Sequence[str]) -> str:
        """This cell's scenarios that are in `which`, as one pytest `-k` expression (`s012 or
        s005`), or `""` when there are none. Empty means the workflow skips that step rather than
        running pytest with an empty selector, which would collect everything."""
        chosen = [s for s in self.scenarios if s in which]
        return " or ".join(chosen)

    def as_dict(self, live: Sequence[str]) -> dict[str, Any]:
        """The JSON one matrix entry is. Everything the `cell` job needs is here, so the job's
        `with:` and `env:` read values rather than computing them -- expression logic inside a
        workflow is the one thing neither `make matrix-check` nor a unit test can check."""
        return {
            "id": self.id,
            "os": self.os,
            "host": self.host,
            "python": self.python,
            "scenarios": list(self.scenarios),
            # The two pytest selectors, pre-split: live scenarios cost money and go through
            # `make eval-live`, the rest are free and go through `make eval`.
            "live_k": self.k(live),
            "eval_k": self.k([s for s in self.scenarios if s not in live]),
        }


@dataclass(frozen=True)
class Matrix:
    """The whole file, read and typed once."""

    axes: dict[str, tuple[str, ...]]
    live: tuple[str, ...]
    default_scenarios: tuple[str, ...]
    sets: dict[str, tuple[Cell, ...]]

    def cells(self, set_name: str, only: Iterable[str] | None = None) -> list[Cell]:
        """The cells of one named set, optionally narrowed to a list of ids -- the workflow's
        `cells` input, which is how §13 step 5 runs *one* cell first (`ubuntu / claude / 3.13`) and
        then the Windows / Copilot one, before ever running six."""
        if set_name not in self.sets:
            raise CellsError(f"unknown set {set_name!r} -- cells.toml names {sorted(self.sets)}")
        chosen = list(self.sets[set_name])
        if only is None:
            return chosen
        wanted = [c.strip() for c in only if c and c.strip()]
        if not wanted:
            return chosen
        by_id = {cell.id: cell for cell in chosen}
        missing = [w for w in wanted if w not in by_id]
        if missing:
            raise CellsError(
                f"{set_name}: no such cell(s) {missing} -- it has "
                f"{sorted(by_id)}")
        return [by_id[w] for w in wanted]

    def as_matrix(self, set_name: str, only: Iterable[str] | None = None) -> list[dict[str, Any]]:
        return [cell.as_dict(self.live) for cell in self.cells(set_name, only)]

    @property
    def product(self) -> set[tuple[str, str, str]]:
        """Every (os, host, python) the axes allow -- what the weekly set must be."""
        return set(itertools.product(self.axes["os"], self.axes["host"], self.axes["python"]))


# --------------------------------------------------------------------------------------- loading

def _str_list(raw: Any, where: str, problems: list[str]) -> tuple[str, ...]:
    if not isinstance(raw, list) or not all(isinstance(v, str) for v in raw):
        problems.append(f"{where} must be a list of strings")
        return ()
    return tuple(raw)


def load(path: Path | None = None) -> Matrix:
    """Read and validate `cells.toml`. Raises `CellsError` carrying every problem at once."""
    path = path or CELLS_TOML
    problems: list[str] = []
    try:
        with path.open("rb") as handle:
            raw = tomllib.load(handle)
    except FileNotFoundError:
        raise CellsError(f"no cells file at {path}") from None
    except tomllib.TOMLDecodeError as exc:
        raise CellsError(f"{path} is not valid TOML: {exc}") from None

    axes_raw = raw.get("axes", {})
    axes = {name: _str_list(axes_raw.get(name), f"[axes].{name}", problems)
            for name in ("os", "host", "python")}
    for name, values in axes.items():
        if not values:
            problems.append(f"[axes].{name} names no values")

    scenarios_raw = raw.get("scenarios", {})
    default_scenarios = _str_list(scenarios_raw.get("default", []), "[scenarios].default", problems)
    live = _str_list(scenarios_raw.get("live", []), "[scenarios].live", problems)
    if not default_scenarios:
        problems.append("[scenarios].default names no scenario -- a cell with nothing to run is "
                        "six minutes of runner for a green tick that measured nothing")

    sets_raw = raw.get("sets", {})
    if set(sets_raw) != set(SET_NAMES):
        problems.append(f"[sets] must name exactly {list(SET_NAMES)}, not {sorted(sets_raw)}")

    sets: dict[str, tuple[Cell, ...]] = {}
    for set_name in SET_NAMES:
        entries = sets_raw.get(set_name)
        if entries is None:
            continue
        if not isinstance(entries, list):
            problems.append(f"[sets].{set_name} must be a list of cells")
            continue
        cells: list[Cell] = []
        for index, entry in enumerate(entries):
            where = f"[sets].{set_name}[{index}]"
            if not isinstance(entry, dict):
                problems.append(f"{where} must be a table")
                continue
            unknown = set(entry) - {"os", "host", "python", "scenarios"}
            if unknown:
                problems.append(f"{where} has unknown key(s) {sorted(unknown)}")
            values = {}
            for axis in ("os", "host", "python"):
                value = entry.get(axis)
                if not isinstance(value, str):
                    problems.append(f"{where} is missing a {axis}")
                    value = ""
                elif axes[axis] and value not in axes[axis]:
                    problems.append(f"{where}: {axis}={value!r} is not one of "
                                    f"{list(axes[axis])}")
                values[axis] = value
            scenarios = (_str_list(entry["scenarios"], f"{where}.scenarios", problems)
                         if "scenarios" in entry else default_scenarios)
            if not scenarios:
                problems.append(f"{where} runs no scenarios")
            cells.append(Cell(os=values["os"], host=values["host"], python=values["python"],
                              scenarios=scenarios))
        ids = [cell.id for cell in cells]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            problems.append(f"[sets].{set_name} names {duplicates} more than once -- a cell's id "
                            f"is its KEEL_REMOTE_CELL, its artifact and its founder in the picker, "
                            f"and two cells cannot be one founder (design §4.3)")
        sets[set_name] = tuple(cells)

    if problems:
        raise CellsError(f"{path}:\n  - " + "\n  - ".join(problems))
    return Matrix(axes=axes, live=live, default_scenarios=default_scenarios, sets=sets)


# ------------------------------------------------------------------- the design's coverage rules

def coverage_problems(matrix: Matrix) -> list[str]:
    """The three rules §5.2 states in prose, as checks. They are here rather than only in the test
    suite so that `make matrix-check` enforces them too: the founder editing cells.toml on a
    Sunday is exactly the reader who would not run `make unit` afterwards."""
    problems: list[str] = []

    per_change = matrix.sets.get("per_change", ())
    covered = {(cell.os, cell.host) for cell in per_change}
    want = set(itertools.product(matrix.axes["os"], matrix.axes["host"]))
    if covered != want:
        missing = sorted(want - covered)
        problems.append(f"per_change must run every OS once per host (§5.2); it misses {missing}")
    if not any(cell.python == "3.9" for cell in per_change):
        problems.append("per_change spends no cell on Python 3.9 -- spec 004's floor is a promise, "
                        "and a promise nothing runs against per change is a promise")

    nightly = matrix.sets.get("nightly", ())
    not_ubuntu = sorted({cell.os for cell in nightly if not cell.os.startswith("ubuntu")})
    if not_ubuntu:
        problems.append(f"nightly is Ubuntu only (§5.2 and §10's 'Linux 6 / 0 / 0'); it names "
                        f"{not_ubuntu}")

    weekly = {(cell.os, cell.host, cell.python) for cell in matrix.sets.get("weekly", ())}
    if weekly != matrix.product:
        missing = sorted(matrix.product - weekly)
        extra = sorted(weekly - matrix.product)
        problems.append(f"weekly must be the full product of the axes (§5.2, eighteen cells)"
                        + (f"; missing {missing}" if missing else "")
                        + (f"; unexpected {extra}" if extra else ""))
    return problems


def validate(matrix: Matrix) -> None:
    problems = coverage_problems(matrix)
    if problems:
        raise CellsError("cells.toml does not meet the design's coverage rules:\n  - "
                         + "\n  - ".join(problems))


# ------------------------------------------------------------------------------------ the two CLIs

def render(matrix: Matrix, set_name: str | None = None,
           only: Iterable[str] | None = None) -> str:
    """What `make matrix-check` prints: the three sets, one line a cell, so the founder reads what
    would run before it runs."""
    lines = []
    for set_name in ((set_name,) if set_name else SET_NAMES):
        cells = matrix.cells(set_name, only)
        lines.append(f"{set_name}  ({len(cells)} cell{'s' if len(cells) != 1 else ''})")
        for cell in cells:
            live = cell.k(matrix.live)
            free = cell.k([s for s in cell.scenarios if s not in matrix.live])
            what = "  ".join(part for part in (
                f"live: {live}" if live else "", f"free: {free}" if free else "") if part)
            lines.append(f"    {cell.id:<34}  {what}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m matrix",
        description="Read matrix/cells.toml, validate it, and print or emit the cells "
                    "(spec 020-matrix-workflow).")
    parser.add_argument("--set", dest="set_name", choices=SET_NAMES,
                        help="one named set; without it, every set is printed")
    parser.add_argument("--cells", default="",
                        help="comma-separated cell ids to narrow the set to (the workflow's own "
                             "`cells` input)")
    parser.add_argument("--json", action="store_true",
                        help="emit the set as the JSON list `strategy.matrix.include` takes")
    parser.add_argument("--file", type=Path, default=None, help="a cells.toml other than the one "
                                                                "beside this module")
    args = parser.parse_args(argv)

    try:
        matrix = load(args.file)
        validate(matrix)
        only = args.cells.split(",") if args.cells.strip() else None
        if args.json:
            if not args.set_name:
                parser.error("--json needs --set")
            print(json.dumps(matrix.as_matrix(args.set_name, only), separators=(",", ":")))
        else:
            print(render(matrix, args.set_name, only), end="")
    except CellsError as exc:
        print(f"matrix/cells.toml: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover - `python -m matrix.cells`
    raise SystemExit(main())
