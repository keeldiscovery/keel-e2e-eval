"""Reads `matrix/cells.toml`, validates it, and hands out cells (spec 020-matrix-workflow;
keel-cloud `canon/designs/e2e-matrix-design.md` §5).

**One reader, two callers.** `.github/workflows/matrix.yml`'s `select` job runs
`python -m matrix --set <name> --json` and `make matrix-check` runs `python -m matrix`; they are
the same code over the same file, so a founder who edits `cells.toml` finds out on their own Mac
what the workflow would have found out on a runner -- before the runner spends a model request on
it. Nothing here touches the network, a stack, a runner or a secret: it is a TOML file, six
coverage rules and a JSON dump.

**What a cell is** (§5.3): one (OS, host, Python) combination run once, as one runner job, with a
list of scenarios. Its `id` -- `<os>-<host>-py<python>` -- is the whole of its identity: the job's
name, the artifact's name, and `KEEL_REMOTE_CELL`, which is what `stack/remote.py` names the
founder it registers with the twin's picker, which is what the founder reads the next morning
(§4.3). So ids are unique within a set, and the validator says so.

**How far a cell goes is a field, not a scenario.** `legs` (spec 021) is `short` or `full` and
defaults to `full`; the workflow exports it as `KEEL_JOURNEY_LEGS` and S-012 reads it. The four
per-change cells are `short` -- the host leg plus the first model job -- and everything else is
`full`. It is deliberately **not** part of a cell's `id`: the same machine appearing short in one
set and full in another is one cell in two sets, not two cells, and its id is the founder it
registers with the twin's picker (§4.3), which cannot be two people.

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

#: How much of S-012 a cell runs (spec `021-short-journey`; `harness/agent_host.py`'s own `LEGS`,
#: restated here rather than imported so this module stays stdlib-only and importable by a
#: workflow step that has no harness). `full` is the default and is what a cell that says nothing
#: gets, so every cell written before spec 021 means what it meant.
LEGS = ("short", "full")
DEFAULT_LEGS = "full"


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
    #: `short` or `full` -- how much of the journey this cell buys (spec 021). Optional in the
    #: file and **not** part of the cell's id: a cell is still one (OS, host, Python), and the
    #: same cell appearing in `per_change` short and in `nightly` full is one runner job in two
    #: sets, not two cells. It reaches the runner as `KEEL_JOURNEY_LEGS`.
    legs: str = DEFAULT_LEGS

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
            # `KEEL_JOURNEY_LEGS` in the cell job's env. S-012 is the only scenario that reads it;
            # a cell carrying corpus scenarios beside the journey passes it all the same, and they
            # ignore it.
            "legs": self.legs,
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
            unknown = set(entry) - {"os", "host", "python", "scenarios", "legs"}
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
            legs = entry.get("legs", DEFAULT_LEGS)
            if legs not in LEGS:
                problems.append(f"{where}: legs={legs!r} is not one of {list(LEGS)} -- `short` is "
                                f"the host leg plus the first model job, `full` is the whole "
                                f"journey, and a cell that says nothing gets {DEFAULT_LEGS!r}")
                legs = DEFAULT_LEGS
            cells.append(Cell(os=values["os"], host=values["host"], python=values["python"],
                              scenarios=scenarios, legs=legs))
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


# -------------------------------------------------------------------------- the coverage rules

#: **The operating system the per-change and nightly sets deliberately leave out** (the founder's
#: decision, 2026-09-11: *"fewer than 5% of founders"*). Ubuntu is not dropped -- it is weekly, in
#: full, every Sunday. It is dropped from the sets that run on a merge and overnight, because the
#: minutes there buy more on the two operating systems founders actually install the plugin on.
#: Written as a prefix because the runner label carries a version (`ubuntu-24.04`) and the rule is
#: about the OS.
CHEAP_SETS_SKIP = "ubuntu"


def coverage_problems(matrix: Matrix) -> list[str]:
    """The design's coverage rules, as checks -- **rewritten by spec 021** (the founder's
    decisions of 2026-09-11), which is why they no longer read like §5.2's prose.

    They are here rather than only in the test suite so that `make matrix-check` enforces them
    too: the founder editing cells.toml on a Sunday is exactly the reader who would not run
    `make unit` afterwards.

    The six rules, in the order they are checked:

    1. **per_change is the two operating systems founders install on, each host, on the current
       Python, running the short journey.** Four cells. Ubuntu is not in it and neither is the
       floor: a merge buys the host leg and the first model job on macOS and Windows.
    2. **per_change runs only the journey, and only the short one.** A corpus scenario or a full
       journey in the cheap set is the cheap set stopping being cheap.
    3. **nightly carries every per_change combination again, at full length.** What a merge buys
       short, the night buys whole -- so a break the short journey cannot see is at most a day
       old.
    4. **nightly spends the 3.9 floor**, on Windows, both hosts. spec 004's floor is a promise and
       a promise nothing runs against is not one; it moved from per_change to nightly rather than
       being dropped.
    5. **Neither cheap set leaves for Ubuntu**, and nightly is six cells.
    6. **weekly is the full product of the axes, every cell at full length.** Ubuntu is here, and
       this is the confirmation that nothing is hiding in a corner.
    """
    problems: list[str] = []
    everyday = [os_ for os_ in matrix.axes["os"] if not os_.startswith(CHEAP_SETS_SKIP)]

    per_change = matrix.sets.get("per_change", ())
    covered = {(cell.os, cell.host) for cell in per_change}
    want = set(itertools.product(everyday, matrix.axes["host"]))
    if covered != want:
        missing = sorted(want - covered)
        extra = sorted(covered - want)
        problems.append("per_change must run each of "
                        f"{everyday} once per host and nothing else (spec 021)"
                        + (f"; it misses {missing}" if missing else "")
                        + (f"; it also names {extra}" if extra else ""))
    current = matrix.axes["python"][-1] if matrix.axes["python"] else ""
    off_axis = sorted({c.id for c in per_change if c.python != current})
    if off_axis:
        problems.append(f"per_change runs the current Python ({current}) and only it (spec 021); "
                        f"{off_axis} do not")
    not_short = sorted({c.id for c in per_change if c.legs != "short"})
    if not_short:
        problems.append(f"per_change runs the SHORT journey (spec 021): {not_short} would run the "
                        f"whole one on every qualifying change")
    beyond = sorted({s for c in per_change for s in c.scenarios} - set(matrix.default_scenarios))
    if beyond:
        problems.append(f"per_change runs only {list(matrix.default_scenarios)} (spec 021); it "
                        f"also names {beyond}, which is the cheap set stopping being cheap")

    nightly = matrix.sets.get("nightly", ())
    strayed = sorted({cell.os for cell in nightly if cell.os.startswith(CHEAP_SETS_SKIP)})
    if strayed:
        problems.append(f"nightly leaves {CHEAP_SETS_SKIP!r} to the weekly set (spec 021, "
                        f"'fewer than 5% of founders'); it names {strayed}")
    nightly_full = {(c.os, c.host, c.python) for c in nightly if c.legs == "full"}
    unheld = sorted({(c.os, c.host, c.python) for c in per_change} - nightly_full)
    if unheld:
        problems.append(f"nightly must run every per_change cell at full length (spec 021): "
                        f"{unheld} are bought short on a merge and never bought whole")
    floor = matrix.axes["python"][0] if matrix.axes["python"] else ""
    if not any(cell.python == floor for cell in nightly):
        problems.append(f"nightly spends no cell on Python {floor} -- spec 004's floor is a "
                        f"promise, and per_change no longer runs it, so the night is where it is "
                        f"kept")

    weekly = matrix.sets.get("weekly", ())
    combos = {(c.os, c.host, c.python) for c in weekly}
    if combos != matrix.product:
        missing = sorted(matrix.product - combos)
        extra = sorted(combos - matrix.product)
        problems.append("weekly must be the full product of the axes (§5.2, eighteen cells)"
                        + (f"; missing {missing}" if missing else "")
                        + (f"; unexpected {extra}" if extra else ""))
    shortened = sorted({c.id for c in weekly if c.legs != "full"})
    if shortened:
        problems.append(f"weekly is the full journey everywhere (spec 021); {shortened} are short")
    return problems


def validate(matrix: Matrix) -> None:
    problems = coverage_problems(matrix)
    if problems:
        raise CellsError("cells.toml does not meet the coverage rules:\n  - "
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
            lines.append(f"    {cell.id:<34}  {cell.legs:<6}  {what}")
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
