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
weekly's macOS Claude cell does (decision 11) -- so each cell offers the two pytest `-k`
expressions its workflow step needs, and either may be empty.

**The nightly is suspended** (design §15, the founder, 2026-09-13: *"we cannot afford to do a
nightly run; only the weekly"*). The set name stays -- a hand dispatch may still name it and gets
nothing -- and the coverage rules hold it EMPTY, so a cell put back there is a decision being
undone by accident until the rule is rewritten with the cron.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import tomllib
import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

#: The file. One directory, one name, no search path: a second cells.toml somewhere else would be
#: a second matrix nobody knew about.
CELLS_TOML = Path(__file__).resolve().parent / "cells.toml"

#: The three named sets, in the order §5.2 tables them (cheap, nightly, everything). `nightly`
#: is suspended since 2026-09-13 (design §15) and must be empty; the name is kept so a hand
#: `inputs[set]=nightly` resolves to "no cells" rather than to an error.
SET_NAMES = ("per_change", "nightly", "weekly")

#: How much of S-012 a cell runs (spec `021-short-journey`; `harness/agent_host.py`'s own `LEGS`,
#: restated here rather than imported so this module stays stdlib-only and importable by a
#: workflow step that has no harness). `full` is the default and is what a cell that says nothing
#: gets, so every cell written before spec 021 means what it meant.
LEGS = ("short", "full")
DEFAULT_LEGS = "full"
#: How leg one puts the skill in front of the host (spec 022; `harness/agent_host.py`'s own
#: `INSTALLS`): the marketplace `plugin`, or the Spec Kit extension (`speckit`). Reaches the
#: runner as `KEEL_JOURNEY_INSTALL`, and IS part of the cell's id -- the same OS, host and Python
#: through Spec Kit is a different runner job with its own bundle and its own founder in the picker.
INSTALLS = ("plugin", "speckit")
DEFAULT_INSTALL = "plugin"


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
    #: `plugin` or `speckit` (spec 022). Part of the id, unlike `legs`.
    install: str = DEFAULT_INSTALL

    @property
    def id(self) -> str:
        """`ubuntu-24.04-claude-py3.9`. The job name, the artifact name, and `KEEL_REMOTE_CELL`."""
        base = f"{self.os}-{self.host}-py{self.python}"
        return base if self.install == DEFAULT_INSTALL else f"{base}-{self.install}"

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
            # `KEEL_JOURNEY_INSTALL` in the cell job's env (spec 022): the marketplace plugin, or
            # the Spec Kit extension. The workflow installs Spec Kit's CLI only when it says so.
            "install": self.install,
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
    #: Hosts the matrix may buy but does not owe (keel-runtime spec 008, 2026-09-12): a host that
    #: runs but has not passed keel-skill-design §5.5's four-part gate. Allowed in weekly, never
    #: in per_change (a merge buys the measured hosts and nothing else), and not part of the
    #: product the weekly set must cover. `[axes].host_unmeasured` in cells.toml; empty since
    #: Codex passed the gate (2026-09-13).
    unmeasured_hosts: tuple[str, ...] = ()
    #: Operating systems the axis still names but no set owes or may name (the founder,
    #: 2026-09-13: Ubuntu, *"fewer than 5% of founders"*, suspended everywhere to cut cost).
    #: `[axes].os_suspended`. The weekly product is the axis minus these.
    suspended_os: tuple[str, ...] = ()
    #: The hosts a merge and the night pay for (the founder, 2026-09-12: *"Claude Code is the one
    #: we want to run daily in the night; Copilot and Codex only once a week"*). A measured host
    #: not named here is bought weekly, whole, and nowhere else. `[axes].host_everyday`; defaults
    #: to every measured host, which is what the file meant before the founder narrowed it.
    everyday_hosts: tuple[str, ...] = ()

    @property
    def all_hosts(self) -> tuple[str, ...]:
        return tuple(self.axes["host"]) + tuple(self.unmeasured_hosts)

    @property
    def active_os(self) -> tuple[str, ...]:
        """The axis minus the suspended: what any set may name and what the weekly must cover."""
        return tuple(os_ for os_ in self.axes["os"] if os_ not in self.suspended_os)

    def cells(self, set_name: str, only: Iterable[str] | None = None,
              scenarios: Iterable[str] | None = None) -> list[Cell]:
        """The cells of one named set, optionally narrowed to a list of ids -- the workflow's
        `cells` input, which is how §13 step 5 runs *one* cell first (`ubuntu / claude / 3.13`) and
        then the Windows / Copilot one, before ever running six -- and optionally to a list of
        scenarios (the workflow's `scenarios` input, 2026-09-13): each chosen cell keeps only the
        scenarios named, which must all be ones it already carries. The founder's use: the weekly
        macOS Claude cell with the journey alone, no corpus riders, so the twin holds one project
        for review. A cell left with nothing is dropped."""
        if set_name not in self.sets:
            raise CellsError(f"unknown set {set_name!r} -- cells.toml names {sorted(self.sets)}")
        chosen = self._narrow_scenarios(list(self.sets[set_name]), scenarios)
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

    @staticmethod
    def _narrow_scenarios(chosen: list[Cell], scenarios: Iterable[str] | None) -> list[Cell]:
        if scenarios is None:
            return chosen
        keep = [x.strip() for x in scenarios if x and x.strip()]
        if not keep:
            return chosen
        narrowed: list[Cell] = []
        for cell in chosen:
            kept = tuple(sc for sc in cell.scenarios if sc in keep)
            if kept:
                narrowed.append(dataclasses.replace(cell, scenarios=kept))
        if not narrowed:
            raise CellsError(f"no chosen cell carries any of {keep} -- the `scenarios` input keeps "
                             f"scenarios cells already run; the set's cells carry "
                             f"{sorted({sc for cell in chosen for sc in cell.scenarios})}")
        return narrowed

    def as_matrix(self, set_name: str, only: Iterable[str] | None = None,
                  scenarios: Iterable[str] | None = None) -> list[dict[str, Any]]:
        return [cell.as_dict(self.live) for cell in self.cells(set_name, only, scenarios)]

    @property
    def product(self) -> set[tuple[str, str, str]]:
        """Every (os, host, python) the axes allow, the suspended OS left out -- what the weekly
        set must be (design §15: eighteen since 2026-09-13, two OS x three hosts x three Pythons)."""
        return set(itertools.product(self.active_os, self.axes["host"], self.axes["python"]))


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
    unmeasured = (_str_list(axes_raw.get("host_unmeasured"), "[axes].host_unmeasured", problems)
                  if "host_unmeasured" in axes_raw else ())
    suspended = (_str_list(axes_raw.get("os_suspended"), "[axes].os_suspended", problems)
                 if "os_suspended" in axes_raw else ())
    unknown_os = sorted(set(suspended) - set(axes["os"]))
    if unknown_os:
        problems.append(f"[axes].os_suspended names {unknown_os}, which [axes].os does not: only "
                        f"an operating system the axis knows can be suspended")
    if axes["os"] and set(suspended) >= set(axes["os"]):
        problems.append("[axes].os_suspended suspends every operating system -- a matrix with "
                        "nowhere to run")
    overlap = sorted(set(unmeasured) & set(axes["host"]))
    if overlap:
        problems.append(f"[axes].host_unmeasured names {overlap}, which [axes].host already "
                        f"names as measured -- a host is one or the other")
    everyday = (_str_list(axes_raw.get("host_everyday"), "[axes].host_everyday", problems)
                if "host_everyday" in axes_raw else axes["host"])
    stray = sorted(set(everyday) - set(axes["host"]))
    if stray:
        problems.append(f"[axes].host_everyday names {stray}, which [axes].host does not: only a "
                        f"measured host is bought on a merge")

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
            unknown = set(entry) - {"os", "host", "python", "scenarios", "legs", "install"}
            if unknown:
                problems.append(f"{where} has unknown key(s) {sorted(unknown)}")
            values = {}
            for axis in ("os", "host", "python"):
                value = entry.get(axis)
                allowed = axes[axis] + (unmeasured if axis == "host" else ())
                if not isinstance(value, str):
                    problems.append(f"{where} is missing a {axis}")
                    value = ""
                elif allowed and value not in allowed:
                    problems.append(f"{where}: {axis}={value!r} is not one of "
                                    f"{list(allowed)}")
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
            install = entry.get("install", DEFAULT_INSTALL)
            if install not in INSTALLS:
                problems.append(f"{where}: install={install!r} is not one of {list(INSTALLS)} -- the "
                                f"marketplace plugin, or the Spec Kit extension")
                install = DEFAULT_INSTALL
            cells.append(Cell(os=values["os"], host=values["host"], python=values["python"],
                              scenarios=scenarios, legs=legs, install=install))
        ids = [cell.id for cell in cells]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            problems.append(f"[sets].{set_name} names {duplicates} more than once -- a cell's id "
                            f"is its KEEL_REMOTE_CELL, its artifact and its founder in the picker, "
                            f"and two cells cannot be one founder (design §4.3)")
        sets[set_name] = tuple(cells)

    if problems:
        raise CellsError(f"{path}:\n  - " + "\n  - ".join(problems))
    return Matrix(axes=axes, live=live, default_scenarios=default_scenarios, sets=sets,
                  unmeasured_hosts=unmeasured, everyday_hosts=everyday, suspended_os=suspended)


# -------------------------------------------------------------------------- the coverage rules

def coverage_problems(matrix: Matrix) -> list[str]:
    """The design's coverage rules, as checks -- **rewritten by spec 021** (the founder's
    decisions of 2026-09-11) and **again by design §15** (2026-09-13: the nightly suspended, Ubuntu
    suspended, Codex measured), which is why they no longer read like §5.2's prose.

    They are here rather than only in the test suite so that `make matrix-check` enforces them
    too: the founder editing cells.toml on a Sunday is exactly the reader who would not run
    `make unit` afterwards.

    The rules, in the order they are checked:

    1. **per_change is the active operating systems, each everyday host, on the current Python,
       running the short journey.** Two cells today (macOS and Windows x Claude Code). Neither a
       suspended OS nor the floor: a merge buys the host leg and the first model job.
    2. **per_change runs only the journey, and only the short one.** A corpus scenario or a full
       journey in the cheap set is the cheap set stopping being cheap.
    3. **nightly is empty.** Suspended 2026-09-13 to cut cost; a cell here is the decision being
       undone by accident. When a night returns, this rule is rewritten with its cron.
    4. **No set names a suspended operating system.** Ubuntu is not dropped from the axis, it is
       bought nowhere.
    5. **weekly buys whole what a merge bought short**, keeps the 3.9 floor, carries the corpus
       riders on one macOS Claude cell and exactly one Spec Kit cell (spec 022), and is otherwise
       **the full product of the active axes at full length** -- eighteen cells: two OS x three
       measured hosts x three Pythons. An unmeasured host may ride it and is not owed by it.
    """
    problems: list[str] = []
    active = list(matrix.active_os)

    per_change = matrix.sets.get("per_change", ())
    covered = {(cell.os, cell.host) for cell in per_change}
    # A merge buys the everyday hosts and nothing else: never an unmeasured host, and -- since
    # 2026-09-12 -- not a measured host the founder moved to the weekly set either.
    want = set(itertools.product(active, matrix.everyday_hosts))
    if covered != want:
        missing = sorted(want - covered)
        extra = sorted(covered - want)
        problems.append("per_change must run each of "
                        f"{active} once per everyday host {list(matrix.everyday_hosts)} and "
                        "nothing else (spec 021, narrowed 2026-09-12)"
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
    if nightly:
        problems.append(f"nightly is suspended (design §15, the founder, 2026-09-13: 'we cannot "
                        f"afford a nightly run'); it names {sorted(c.id for c in nightly)} -- put "
                        f"the cron back in matrix.yml and rewrite this rule before any cell")

    for name, cells in matrix.sets.items():
        strayed = sorted({c.id for c in cells if c.os in matrix.suspended_os})
        if strayed:
            problems.append(f"{name} names a suspended operating system "
                            f"{list(matrix.suspended_os)} (design §15, 2026-09-13): {strayed}")

    weekly = matrix.sets.get("weekly", ())
    # spec 022: exactly one Spec Kit cell, macOS through Claude, short -- the extension is the
    # same tree as the plugin, so one cell proves the road and not the runtime twice. It rode
    # the nightly until 2026-09-13; it rides the weekly now. Every other rule reads plugin cells.
    speckit = [c for c in weekly if c.install == "speckit"]
    if [(c.os, c.host, c.legs) for c in speckit] != [("macos-latest", "claude", "short")]:
        problems.append("weekly carries exactly one Spec Kit cell, macOS through Claude, the short "
                        f"journey (spec 022, moved from nightly 2026-09-13); it carries "
                        f"{[c.id for c in speckit]}")
    elsewhere = sorted(c.id for name, cells in matrix.sets.items() if name != "weekly"
                       for c in cells if c.install == "speckit")
    if elsewhere:
        problems.append(f"the Spec Kit cell is weekly's alone (spec 022): {elsewhere}")
    plugin_weekly = tuple(c for c in weekly if c.install == "plugin")
    weekly_full = {(c.os, c.host, c.python) for c in plugin_weekly if c.legs == "full"}
    unheld = sorted({(c.os, c.host, c.python) for c in per_change} - weekly_full)
    if unheld:
        problems.append(f"weekly must run every per_change cell at full length (spec 021, the "
                        f"night's duty since 2026-09-13): {unheld} are bought short on a merge and "
                        f"never bought whole")
    floor = matrix.axes["python"][0] if matrix.axes["python"] else ""
    if not any(cell.python == floor for cell in plugin_weekly):
        problems.append(f"weekly spends no cell on Python {floor} -- spec 004's floor is a "
                        f"promise, and no other set runs it")
    # An unmeasured host may ride the weekly set but is not owed by it: the product is the
    # measured hosts' (keel-runtime spec 008).
    combos = {(c.os, c.host, c.python) for c in plugin_weekly
              if c.host not in matrix.unmeasured_hosts}
    if combos != matrix.product:
        missing = sorted(matrix.product - combos)
        extra = sorted(combos - matrix.product)
        problems.append("weekly must be the full product of the active axes (design §15, "
                        "eighteen cells: two OS x three hosts x three Pythons)"
                        + (f"; missing {missing}" if missing else "")
                        + (f"; unexpected {extra}" if extra else ""))
    shortened = sorted({c.id for c in plugin_weekly if c.legs != "full"})
    if shortened:
        problems.append(f"weekly is the full journey everywhere but the Spec Kit cell (spec 021); "
                        f"{shortened} are short")
    return problems


def validate(matrix: Matrix) -> None:
    problems = coverage_problems(matrix)
    if problems:
        raise CellsError("cells.toml does not meet the coverage rules:\n  - "
                         + "\n  - ".join(problems))


# ------------------------------------------------------------------------------------ the two CLIs

def render(matrix: Matrix, set_name: str | None = None,
           only: Iterable[str] | None = None, scenarios: Iterable[str] | None = None) -> str:
    """What `make matrix-check` prints: the three sets, one line a cell, so the founder reads what
    would run before it runs."""
    lines = []
    for set_name in ((set_name,) if set_name else SET_NAMES):
        cells = matrix.cells(set_name, only, scenarios)
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
    parser.add_argument("--scenarios", default="",
                        help="comma-separated scenario ids to keep on every chosen cell (the "
                             "workflow's own `scenarios` input); each must be one the cell carries")
    parser.add_argument("--json", action="store_true",
                        help="emit the set as the JSON list `strategy.matrix.include` takes")
    parser.add_argument("--file", type=Path, default=None, help="a cells.toml other than the one "
                                                                "beside this module")
    args = parser.parse_args(argv)

    try:
        matrix = load(args.file)
        validate(matrix)
        only = args.cells.split(",") if args.cells.strip() else None
        keep = args.scenarios.split(",") if args.scenarios.strip() else None
        if args.json:
            if not args.set_name:
                parser.error("--json needs --set")
            print(json.dumps(matrix.as_matrix(args.set_name, only, keep), separators=(",", ":")))
        else:
            print(render(matrix, args.set_name, only, keep), end="")
    except CellsError as exc:
        print(f"matrix/cells.toml: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover - `python -m matrix.cells`
    raise SystemExit(main())
