"""Spec 105 FR-3: the instruction screen reads keel-cloud's back-test entries and planted probes beside the golden corpus.

keel-cloud 169 FR-6 owes screens of the two frame jobs (`PROBLEM_INTERPRET`, `SOLUTION_MECHANISM`) on three back-test
entries (08-fresco, 10-palus, 13-aircaps) and on one planted probe (`169-banking-gaming`). Until this spec
`instructions/run.py` built cases from the golden corpus alone (01-07), so `-k 08-fresco/PROBLEM_INTERPRET` matched no
case and nothing ran. Now a **screen** (a `-k` needle that is neither empty nor a kind word) also reads:

- **the back-test corpus** -- keel-cloud's `canon/designs/measured-beliefs/backtest/*.yaml` (revision 19 since
  keel-cloud 159; `build/backtest-r19/` is keel-cloud's own `BacktestCorpusTest` output, not a source), loaded through
  `corpus.load(..., backtest=True)` and its refusals. A back-test entry carries no golden expectations, so it is
  screened on **the three interpretation screens** only (`CONTEXT_INTERPRET` and the two frame screens) -- the
  screens that read what its founder typed; rendered and validated as the golden ones are, never scored;
- **the probes** -- `canon/designs/measured-beliefs/probes/*.yaml`, keel-cloud 169's planted-term fixtures: no people,
  no answers, no revision, only what the two frame builders read (`id`, `title`, `market`, `context`, `statements`,
  `interpretations`) and a `probes` list naming, per screen, the one planted term, its two senses and the first turn
  owed. A probe is screened on the screens its list names, and **marked** (`probe_mark`): the first turn is
  `NEEDS_INPUT` with one question that names the planted term and offers two readings; a COMPLETED statement or card
  -- keeping the term or rewriting it -- is a fault.

An extra entry joins only when the needle **names it** -- the needle's first segment is part of its id (`08-fresco`,
`10-palus/SOLUTION`, `169-banking-gaming`) -- so `-k PROBLEM_INTERPRET`, `-k frame` and the full eval (no needle) build
exactly the cases they built before (FR-4). Every extra case carries `meta["source"]` (`backtest` or `probe`), and the
bundle records the extras apart from the golden entries (`ScreenEntries.record`, the scorecard's `screen_entries` and
`probes`). Each extra file is hashed when read and re-hashed after the run, like the corpus.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import context as context_mod
from . import contract as contract_mod
from . import corpus as corpus_mod
from . import prompts as prompts_mod

SOURCE_BACKTEST = "backtest"
SOURCE_PROBE = "probe"

#: The screens a back-test entry is screened on: the three that read the founder's typed context and seeds.
BACKTEST_SCREENS = (contract_mod.SCREEN_CONTEXT_INTERPRET, contract_mod.SCREEN_PROBLEM_INTERPRET,
                    contract_mod.SCREEN_SOLUTION_MECHANISM)
#: The screens a probe may name (keel-cloud 169: the frame class).
PROBE_SCREENS = (contract_mod.SCREEN_PROBLEM_INTERPRET, contract_mod.SCREEN_SOLUTION_MECHANISM)

#: The keys a probe must carry for the frame builders (`instructions/context.py`) to take it as it is.
PROBE_KEYS = ("id", "context", "statements", "interpretations", "probes")
PLANT_KEYS = ("screen", "seed", "planted", "gaming_sense", "banking_sense", "first_turn")


def probes_dir(keel_cloud: Path) -> Path:
    """keel-cloud 169 FR-6: the planted probes, beside `corpus/` and `backtest/`."""
    return Path(keel_cloud) / "canon" / "designs" / "measured-beliefs" / "probes"


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------- the probes

@dataclass(frozen=True)
class Plant:
    """One planted term on one screen, as the probe's `probes` list writes it."""

    screen: str
    seed: str                 # the seed it is planted in, `statements.problem` / `statements.solution`
    planted: str
    gaming_sense: str
    banking_sense: str
    first_turn: dict

    def record(self) -> dict:
        return {"screen": self.screen, "seed": self.seed, "planted": self.planted,
                "gaming_sense": self.gaming_sense, "banking_sense": self.banking_sense,
                "first_turn": dict(self.first_turn)}


@dataclass(frozen=True)
class Probe:
    """A planted probe, under the corpus schema's own key names, so the frame builders read it as an entry."""

    id: str
    title: str
    market: dict
    context: dict
    statements: dict
    interpretations: dict
    plants: tuple
    path: Path
    sha256: str
    #: What `instructions/context.py` reads on the screens a probe is built for -- none of it on a probe.
    solution_mechanism: dict = field(default_factory=dict)
    registry: object = None
    backtest: bool = False

    def plant_for(self, screen: str) -> Plant | None:
        return next((p for p in self.plants if p.screen == screen), None)


def _refuse(probe_id, message, path) -> corpus_mod.CorpusError:
    return corpus_mod.CorpusError(f"{probe_id}: {message} (spec 105 FR-3; keel-cloud 169 FR-6). {path}")


def _seed_text(raw: dict, seed: str):
    node = raw
    for part in seed.split("."):
        node = node.get(part) if isinstance(node, dict) else None
    return node


def load_probe(path) -> Probe:
    """One probe file, checked: the keys the frame builders read, one plant a named frame screen, each planted term
    in the seed it names. A broken probe refuses by name; it never runs as half a probe."""
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise corpus_mod.CorpusError(f"{path} is not a probe")
    probe_id = raw.get("id") or path.name
    missing = [k for k in PROBE_KEYS if not raw.get(k)]
    if missing:
        raise _refuse(probe_id, f"carries no {', '.join(missing)}", path)
    plants, screens = [], set()
    for item in raw["probes"]:
        if not isinstance(item, dict) or any(not item.get(k) for k in PLANT_KEYS):
            raise _refuse(probe_id, f"a probe row must carry {', '.join(PLANT_KEYS)}: {item!r}", path)
        screen = item["screen"]
        if screen not in PROBE_SCREENS:
            raise _refuse(probe_id, f"probes a screen {screen!r}; a probe plants a term in "
                                    f"{' or '.join(PROBE_SCREENS)}", path)
        if screen in screens:
            raise _refuse(probe_id, f"plants two terms on {screen}; one term a seed", path)
        screens.add(screen)
        seed = _seed_text(raw, item["seed"])
        if not isinstance(seed, str) or not term_pattern(item["planted"]).search(seed):
            raise _refuse(probe_id, f"{screen}: the planted term {item['planted']!r} is not in {item['seed']}", path)
        plants.append(Plant(screen=screen, seed=item["seed"], planted=str(item["planted"]),
                            gaming_sense=str(item["gaming_sense"]), banking_sense=str(item["banking_sense"]),
                            first_turn=dict(item["first_turn"])))
    return Probe(id=raw["id"], title=raw.get("title", ""), market=raw.get("market") or {},
                 context=raw.get("context") or {}, statements=raw.get("statements") or {},
                 interpretations=raw.get("interpretations") or {}, plants=tuple(plants), path=path,
                 sha256=_sha256(path))


def load_probes(keel_cloud: Path, directory: Path | None = None) -> list[Probe]:
    """Every `*.yaml` in keel-cloud's probes directory, in filename order; an absent directory is no probe."""
    directory = Path(directory) if directory is not None else probes_dir(keel_cloud)
    if not directory.is_dir():
        return []
    return [load_probe(p) for p in sorted(directory.glob("*.yaml"))]


# --------------------------------------------------------------------------------------------- the probe mark

def term_pattern(term: str) -> re.Pattern:
    """The planted term, its words as typed (spaces or hyphens between them) and its last word in any plain
    inflection -- *loot box* / *loot boxes*, *respawns* / *respawn* / *respawned* -- case-insensitive."""
    words = [w for w in re.split(r"[\s-]+", term.strip()) if w]
    last = words[-1]
    stem = last[:-1] if last.lower().endswith("s") and not last.lower().endswith("ss") else last
    parts = [re.escape(w) for w in words[:-1]] + [re.escape(stem) + r"(?:s|es|ed|ing)?"]
    return re.compile(r"\b" + r"[\s-]+".join(parts) + r"\b", re.IGNORECASE)


#: Two readings joined as alternatives: *Did you mean {A}, or {B}?*
_OR = re.compile(r"\bor\b", re.IGNORECASE)


def _question_text(question) -> str:
    if isinstance(question, dict):
        return str(question.get("question") or question.get("text") or "")
    return str(question or "")


def probe_mark(probe_id: str, plant: Plant, *, outcome, questions, result) -> dict:
    """keel-cloud 169 FR-6's acceptance on one probe case's **first turn**: `first_turn.outcome` (NEEDS_INPUT) with
    `first_turn.questions` (one) question that names the planted term (`term_pattern`) and offers
    `first_turn.readings` (two) readings, joined as alternatives (*..., or ...?*). A COMPLETED statement or card is
    a fault, named for whether it keeps the term or rewrote it. Mechanical: which two senses the question offers is
    recorded for a reader (`question`, `gaming_sense`, `banking_sense`), not judged here."""
    want = plant.first_turn or {}
    pattern = term_pattern(plant.planted)
    questions = list(questions or [])
    texts = [_question_text(q) for q in questions]
    faults = []
    if outcome != want.get("outcome", "NEEDS_INPUT"):
        if outcome == "COMPLETED":
            written = json.dumps(result, ensure_ascii=False) if result is not None else ""
            what = "statement" if plant.screen == contract_mod.SCREEN_PROBLEM_INTERPRET else "card"
            how = "keeps" if pattern.search(written) else "rewrites"
            faults.append(f"the first turn is a COMPLETED {what} that {how} the planted term {plant.planted!r} "
                          f"without asking")
        else:
            faults.append(f"the first turn is {outcome or 'no outcome'}, not {want.get('outcome', 'NEEDS_INPUT')}")
    else:
        count = int(want.get("questions", 1))
        if len(questions) != count:
            faults.append(f"{len(questions)} questions, not {count}")
        text = texts[0] if texts else ""
        if want.get("names_the_term", True) and not pattern.search(text):
            faults.append(f"the question does not name the planted term {plant.planted!r}")
        if int(want.get("readings", 2)) >= 2 and not _OR.search(text):
            faults.append("the question offers no two readings (no *..., or ...?*)")
    return {"probe": probe_id, "screen": plant.screen, "planted": plant.planted,
            "gaming_sense": plant.gaming_sense, "banking_sense": plant.banking_sense,
            "outcome": outcome, "questions": texts, "question": texts[0] if texts else None,
            "held": not faults, "faults": faults}


def probe_line(mark: dict) -> str:
    """The console's line beside a probe case."""
    if mark["held"]:
        return f"  probe held: one question naming {mark['planted']!r}, two readings"
    return f"  probe FAULT: {'; '.join(mark['faults'])}"


# ------------------------------------------------------------------------------------------ the screen entries

def wanted(needle: str | None) -> bool:
    """A screen: a needle that is neither empty (the full eval) nor a kind word (`-k frame`)."""
    from .run import KIND_WORDS                                             # noqa: PLC0415 - run imports this
    return bool(needle and needle.strip()) and needle.strip().lower() not in KIND_WORDS


def names(needle: str | None, entry_id: str) -> bool:
    """Whether the needle names this extra entry: its first segment is part of the entry's id."""
    head = (needle or "").strip().split("/")[0].strip().lower()
    return bool(head) and head in entry_id.lower()


@dataclass
class ScreenEntries:
    """The back-test entries and the probes a screen's needle names, with every file's hash."""

    backtest: list = field(default_factory=list)
    probes: list = field(default_factory=list)
    hashes: dict = field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(self.backtest or self.probes)

    def verify_unchanged(self) -> None:
        for path, digest in self.hashes.items():
            current = _sha256(Path(path))
            if current != digest:
                raise corpus_mod.CorpusError(
                    f"{path} changed while the run was in flight: {digest} -> {current}. A screen's back-test "
                    "entries and probes are read frozen, like the corpus; this run has measured nothing.")

    def record(self) -> dict:
        """What the bundle says the screen read beside the golden corpus -- the probes apart from the entries."""
        return {"backtest": [{"id": e.id, "path": str(e.path), "sha256": e.sha256} for e in self.backtest],
                "probes": [{"id": p.id, "path": str(p.path), "sha256": p.sha256,
                            "plants": [x.record() for x in p.plants]} for p in self.probes]}


def load(keel_cloud: Path, needle: str | None, *, golden_ids=(), backtest_directory: Path | None = None,
         probes_directory: Path | None = None) -> ScreenEntries:
    """The back-test entries and probes the needle names -- nothing for the full eval or a kind word, and nothing
    read from disk then. Only the files whose name the needle names are read (a back-test or probe file is
    `<id>.yaml`), so a screen of a golden entry never depends on an unrelated file. An id that is also a golden one
    (or both a back-test entry and a probe) refuses by name."""
    if not wanted(needle):
        return ScreenEntries()
    backtest_directory = (Path(backtest_directory) if backtest_directory is not None
                          else corpus_mod.backtest_dir(keel_cloud))
    probes_directory = Path(probes_directory) if probes_directory is not None else probes_dir(keel_cloud)

    def named(directory):
        return [p for p in sorted(directory.glob("*.yaml")) if names(needle, p.stem)] if directory.is_dir() else []

    backtest = [e for e in (corpus_mod.load_file(p, backtest=True) for p in named(backtest_directory))
                if names(needle, e.id)]
    probes = [p for p in (load_probe(path) for path in named(probes_directory)) if names(needle, p.id)]
    seen = set(golden_ids)
    for item in [*backtest, *probes]:
        if item.id in seen:
            raise corpus_mod.CorpusError(f"{item.id} is both a golden or back-test entry and a screen entry at "
                                         f"{item.path}; an id names one thing (spec 105 FR-3)")
        seen.add(item.id)
    hashes = {str(e.path): e.sha256 for e in backtest}
    hashes.update({str(p.path): p.sha256 for p in probes})
    return ScreenEntries(backtest=backtest, probes=probes, hashes=hashes)


def _frame_cases(entry, screens, exported, instructions_by_screen, executor_module, *, n_runs, host, meta_for):
    cases = []
    for screen in screens:
        if screen == contract_mod.SCREEN_CONTEXT_INTERPRET:
            kind, content = "CONTEXT", ""
            context = context_mod.build_context_interpret(entry, exported.keys_for(screen))
        else:
            kind, content = "FRAME", context_mod.seed_of(entry, screen)
            builder = (context_mod.build_problem_interpret if screen == contract_mod.SCREEN_PROBLEM_INTERPRET
                       else context_mod.build_solution_mechanism)
            context = builder(entry, exported.keys_for(screen))
        payload = prompts_mod.payload_for(instructions_by_screen.get(screen), context, exported.for_screen(screen),
                                          content=content)
        for run_index in range(1, n_runs + 1):
            case = prompts_mod.Case(case_id=f"{entry.id}/{screen}/run{run_index}", kind=kind, entry_id=entry.id,
                                    screen=screen, subject=screen, run_index=run_index, payload=payload,
                                    meta=meta_for(screen))
            case.prompt = prompts_mod.render(executor_module, payload, job_id=prompts_mod._slug(case.case_id),
                                             host=host)
            cases.append(case)
    return cases


def build_cases(entries: ScreenEntries, exported, instructions_by_screen, executor_module, *, needle: str,
                n_runs: int = 3, host: str = "claude") -> list:
    """The extras' cases, in the golden cases' ids (`<id>/<SCREEN>/run<N>`), the needle applied as `-k` applies it
    (a case-insensitive substring of the case id). Each case's `meta["source"]` says what it is; a probe case also
    carries its plant (`meta["probe"]`), which `probe_mark` reads."""
    cases = []
    for entry in entries.backtest:
        cases += _frame_cases(entry, BACKTEST_SCREENS, exported, instructions_by_screen, executor_module,
                              n_runs=n_runs, host=host, meta_for=lambda screen: {"source": SOURCE_BACKTEST})
    for probe in entries.probes:
        screens = [s for s in PROBE_SCREENS if probe.plant_for(s) is not None]
        cases += _frame_cases(probe, screens, exported, instructions_by_screen, executor_module,
                              n_runs=n_runs, host=host,
                              meta_for=lambda screen, probe=probe: {"source": SOURCE_PROBE,
                                                                    "probe": probe.plant_for(screen).record()})
    word = needle.strip().lower()
    return [c for c in cases if word in c.case_id.lower()]


def is_extra(case) -> bool:
    return (getattr(case, "meta", None) or {}).get("source") in (SOURCE_BACKTEST, SOURCE_PROBE)


def plant_of(case) -> Plant | None:
    row = (case.meta or {}).get("probe") if (case.meta or {}).get("source") == SOURCE_PROBE else None
    return Plant(**row) if row else None
