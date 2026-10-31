"""Spec 105 FR-3: the instruction screen reads keel-cloud's back-test entries and planted probes beside the golden corpus.

keel-cloud 169 FR-6 owes screens of the two frame jobs (`PROBLEM_INTERPRET`, `SOLUTION_MECHANISM`) on three back-test
entries (08-fresco, 10-palus, 13-aircaps) and on one planted probe (`169-banking-gaming`). Until this spec
`instructions/run.py` built cases from the golden corpus alone (01-07), so `-k 08-fresco/PROBLEM_INTERPRET` matched no
case and nothing ran. Now a **screen** (a `-k` needle that is neither empty nor a kind word) also reads:

- **the back-test corpus** -- keel-cloud's `canon/designs/measured-beliefs/backtest/*.yaml` (revision 19 since
  keel-cloud 159; `build/backtest-r19/` is keel-cloud's own `BacktestCorpusTest` output, not a source), loaded through
  `corpus.load(..., backtest=True)` and its refusals. A back-test entry carries no golden expectations, so it is
  screened on **the three interpretation screens** (`CONTEXT_INTERPRET` and the two frame screens) -- the
  screens that read what its founder typed -- and, since spec 110 (keel-cloud 170 FR-7), on **part 1 of
  `RESPONDENT_QUESTIONS`** (`<id>/RESPONDENT_PART1`, the job that writes the gate from the founder's `problem`);
  rendered and validated as the golden ones are, never scored;
- **the probes** -- `canon/designs/measured-beliefs/probes/*.yaml`, keel-cloud 169's planted-term fixtures: no people,
  no answers, no revision, only what the two frame builders read (`id`, `title`, `market`, `context`, `statements`,
  `interpretations`) and a `probes` list naming, per screen, the one planted term, its two senses and the first turn
  owed. A probe is screened on the screens its list names, and **marked** (`probe_mark`): the first turn is
  `NEEDS_INPUT` with one question that names the planted term and offers two readings; a COMPLETED statement or card
  -- keeping the term or rewriting it -- is a fault. Since spec 110 a probe may instead carry a `RESPONDENT_QUESTIONS`
  job's context as keel-cloud's `ScreenContextBuilder` writes it (`job_context`, with `recall_window` beside it:
  keel-cloud 170's `170-judgement-verb`), screened as `<id>/RESPONDENT_PART1` and marked by `respondent_probe_mark`:
  COMPLETED, part 1, the gate's one `event` free of every verdict word and keeping the object (`keeps`).

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

#: The screens a back-test entry is screened on: the three that read the founder's typed context and seeds, since
#: spec 110 (keel-cloud 170 FR-7) the respondent job's part 1 -- the gate, written from the founder's `problem` -- and
#: since spec 112 (keel-cloud 171 FR-6) the founder-lists job's redraft of each list the entry typed, handed its Answer.
BACKTEST_SCREENS = (contract_mod.SCREEN_CONTEXT_INTERPRET, contract_mod.SCREEN_PROBLEM_INTERPRET,
                    contract_mod.SCREEN_SOLUTION_MECHANISM, contract_mod.SCREEN_RESPONDENT,
                    contract_mod.SCREEN_CALIBRATION)
#: Spec 112 FR-3: the mark a back-test entry's Adoption friction redraft is held to (keel-cloud 171 FR-6's acceptance).
STEPS_MARK = "171"
STEPS_KEY = "solution.adoption_friction"
#: Spec 113 FR-4: the mark a back-test entry's Relative advantage redraft is held to (keel-cloud 173 FR-3's acceptance:
#: one row per benefit the Answer names, as typed, never split; Keel adds none).
BENEFITS_MARK = "173"
BENEFITS_KEY = "solution.relative_advantage"
#: The registry's `saves.max_words` for the benefit list (keel-cloud 173: *tidied to the limits only*).
BENEFIT_MAX_WORDS = 9
#: The respondent part a back-test entry and a respondent probe are screened on (`<id>/RESPONDENT_PART1`).
RESPONDENT_PART = 1
#: The screens a probe may name (keel-cloud 169: the frame class; keel-cloud 170: the respondent job).
PROBE_SCREENS = (contract_mod.SCREEN_PROBLEM_INTERPRET, contract_mod.SCREEN_SOLUTION_MECHANISM)
RESPONDENT_PROBE_SCREENS = (contract_mod.SCREEN_RESPONDENT,)

#: The keys a probe must carry for the frame builders (`instructions/context.py`) to take it as it is.
PROBE_KEYS = ("id", "context", "statements", "interpretations", "probes")
PLANT_KEYS = ("screen", "seed", "planted", "gaming_sense", "banking_sense", "first_turn")
#: Spec 110 FR-4 (keel-cloud 170 FR-7): a respondent probe hands the job its context as it is -- `job_context` under
#: `ScreenContextBuilder`'s own keys -- and each row names the item, the planted words, the verdict words the event
#: must not say, the words it must keep and the first turn owed.
RESPONDENT_PROBE_KEYS = ("id", "job_context", "probes")
RESPONDENT_PLANT_KEYS = ("screen", "item", "planted", "verdict_words", "keeps", "first_turn")


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
    #: Spec 110 FR-4: a respondent probe's job context, as `ScreenContextBuilder` writes it, and its recall window.
    job_context: dict | None = None
    recall_window: dict | None = None

    def plant_for(self, screen: str):
        return next((p for p in self.plants if p.screen == screen), None)

    def respondent(self) -> bool:
        return self.job_context is not None


@dataclass(frozen=True)
class RespondentPlant:
    """Spec 110 FR-4 (keel-cloud 170 FR-7): one respondent probe row -- the gate item, the verdict planted in the
    founder's words, the verdict words its `event` must not say, the words it must keep, the register a reader holds
    it to, and the recall window it is framed in."""

    screen: str
    item: str
    planted: tuple
    verdict_words: tuple
    keeps: tuple
    first_turn: dict
    register: str | None = None
    in_the_frame: str | None = None
    recall_window: dict | None = None

    def record(self) -> dict:
        return {"screen": self.screen, "item": self.item, "planted": list(self.planted),
                "verdict_words": list(self.verdict_words), "keeps": list(self.keeps),
                "first_turn": dict(self.first_turn), "register": self.register, "in_the_frame": self.in_the_frame,
                "recall_window": dict(self.recall_window) if self.recall_window else None}


def _refuse(probe_id, message, path) -> corpus_mod.CorpusError:
    return corpus_mod.CorpusError(f"{probe_id}: {message} (spec 105 FR-3; keel-cloud 169 FR-6). {path}")


def _seed_text(raw: dict, seed: str):
    node = raw
    for part in seed.split("."):
        node = node.get(part) if isinstance(node, dict) else None
    return node


def _words(value) -> tuple:
    return tuple(str(v) for v in (value if isinstance(value, list) else [value]) if str(v).strip())


def load_respondent_probe(raw: dict, path: Path) -> Probe:
    """Spec 110 FR-4 (keel-cloud 170 FR-7): a probe that hands `RESPONDENT_QUESTIONS` its job context as it is -- part
    1, the items by key, `problem` and `condition` -- and names, per row, the gate item, the planted verdict, the words
    its event must not say and must keep. Each planted word is in the founder's words the job reads (`problem` or
    `context.circumstance`). A broken probe refuses by name."""
    probe_id = raw.get("id") or path.name
    missing = [k for k in RESPONDENT_PROBE_KEYS if not raw.get(k)]
    if missing:
        raise _refuse(probe_id, f"carries no {', '.join(missing)}", path)
    job = raw["job_context"]
    if not isinstance(job, dict) or job.get("part") != RESPONDENT_PART or not job.get("items"):
        raise _refuse(probe_id, f"job_context must be part {RESPONDENT_PART}'s, with its items by key", path)
    founder_words = " ".join(str(x) for x in (job.get("problem"), (job.get("context") or {}).get("circumstance"))
                             if x)
    plants, screens = [], set()
    for item in raw["probes"]:
        if not isinstance(item, dict) or any(not item.get(k) for k in RESPONDENT_PLANT_KEYS):
            raise _refuse(probe_id, f"a respondent probe row must carry {', '.join(RESPONDENT_PLANT_KEYS)}: "
                                    f"{item!r}", path)
        screen = item["screen"]
        if screen not in RESPONDENT_PROBE_SCREENS:
            raise _refuse(probe_id, f"probes a screen {screen!r} beside a job_context; a respondent probe names "
                                    f"{' or '.join(RESPONDENT_PROBE_SCREENS)}", path)
        if screen in screens:
            raise _refuse(probe_id, f"names {screen} twice; one row a screen", path)
        screens.add(screen)
        if item["item"] not in [i.get("key") for i in job["items"] if isinstance(i, dict)]:
            raise _refuse(probe_id, f"{screen}: the item {item['item']!r} is not among job_context's items", path)
        planted = _words(item["planted"])
        absent = [w for w in planted if not term_pattern(w).search(founder_words)]
        if absent:
            raise _refuse(probe_id, f"{screen}: the planted words {absent} are in neither problem nor "
                                    "context.circumstance", path)
        plants.append(RespondentPlant(screen=screen, item=str(item["item"]), planted=planted,
                                      verdict_words=_words(item["verdict_words"]), keeps=_words(item["keeps"]),
                                      first_turn=dict(item["first_turn"]), register=item.get("register"),
                                      in_the_frame=item.get("in_the_frame"),
                                      recall_window=raw.get("recall_window")))
    return Probe(id=raw["id"], title=raw.get("title", ""), market=raw.get("market") or job.get("market") or {},
                 context=job.get("context") or {}, statements={}, interpretations={}, plants=tuple(plants),
                 path=path, sha256=_sha256(path), job_context=dict(job), recall_window=raw.get("recall_window"))


def load_probe(path) -> Probe:
    """One probe file, checked: the keys the frame builders read, one plant a named frame screen, each planted term
    in the seed it names -- or, since spec 110, a respondent probe (`job_context`, `load_respondent_probe`). A broken
    probe refuses by name; it never runs as half a probe."""
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise corpus_mod.CorpusError(f"{path} is not a probe")
    if "job_context" in raw:
        return load_respondent_probe(raw, path)
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


def _word_pattern(word: str) -> re.Pattern:
    """A verdict word or phrase standing whole, case-insensitive (*sit* never in *deposit*, *have to* as two words)."""
    parts = [re.escape(w) for w in re.split(r"\s+", word.strip()) if w]
    return re.compile(r"(?<![\w'])" + r"\s+".join(parts) + r"(?![\w'])", re.IGNORECASE)


def respondent_probe_mark(probe_id: str, plant: RespondentPlant, *, outcome, result) -> dict:
    """Spec 110 FR-4 (keel-cloud 170 FR-7's acceptance) on one respondent probe case's first turn: `first_turn.outcome`
    (COMPLETED), the result's part `first_turn.part` (1), and the planted item's one `event`: E1-E3 clean in the probe's
    window (one clause, no time word, not the frame's words), **no verdict word** (`verdict_words`, whole words) and
    **the object kept** (every word of `keeps`, in any plain inflection). Its framing by code (`wording.gate`) and the
    probe's register are recorded for a reader, not judged here."""
    from . import wording as wording_mod                                    # noqa: PLC0415
    from .registry import RecallWindow                                      # noqa: PLC0415
    want = plant.first_turn or {}
    faults, event, framed = [], None, None
    window = RecallWindow.read(plant.recall_window) if plant.recall_window else None
    if outcome != want.get("outcome", "COMPLETED"):
        faults.append(f"the first turn is {outcome or 'no outcome'}, not {want.get('outcome', 'COMPLETED')}")
    else:
        result = result if isinstance(result, dict) else {}
        if want.get("part") is not None and result.get("part") != want.get("part"):
            faults.append(f"the result is part {result.get('part')!r}, not part {want.get('part')}")
        gates = [i for i in result.get("items") or [] if isinstance(i, dict) and i.get("key") == plant.item]
        events = [i.get("event") for i in gates if isinstance(i.get("event"), str) and i.get("event").strip()]
        if len(events) != 1:
            faults.append(f"{len(events)} `event` clauses on {plant.item}, not one")
        else:
            event = events[0]
            fault = wording_mod.event_fault(event, window) if window is not None else None
            if fault:
                faults.append(f"the event is not one clause: {fault}")
            said = [w for w in plant.verdict_words if _word_pattern(w).search(event)]
            if want.get("no_verdict_word", True) and said:
                faults.append(f"the event says the verdict: {said}")
            lost = [w for w in plant.keeps if not term_pattern(w).search(event)]
            if want.get("object_kept", True) and lost:
                faults.append(f"the event drops the object: {lost}")
            framed = wording_mod.gate(window, event) if window is not None else None
    return {"probe": probe_id, "screen": plant.screen, "item": plant.item, "planted": list(plant.planted),
            "outcome": outcome, "event": event, "framed": framed, "register": plant.register,
            "in_the_frame": plant.in_the_frame, "held": not faults, "faults": faults}


def probe_line(mark: dict) -> str:
    """The console's line beside a probe case (and, spec 112 FR-3, a back-test case's 171 mark)."""
    if mark["held"] and mark.get("mark") == BENEFITS_MARK:
        return f"  173 held: one row per typed benefit ({len(mark['typed'])}), as typed, none added"
    if mark["held"] and mark.get("mark") == STEPS_MARK:
        tail = f"; Keel suggested {mark['suggested'][0]['label']!r}" if mark.get("suggested") else ", none suggested"
        return f"  171 held: the founder's {len(mark['typed'])} efforts first, as typed{tail}"
    if mark["held"] and "event" in mark:
        return f"  probe held: the gate's event says no verdict and keeps the object -- {mark['framed'] or mark['event']}"
    if mark["held"]:
        return f"  probe held: one question naming {mark['planted']!r}, two readings"
    return f"  probe FAULT: {'; '.join(mark['faults'])}"


def mark_for(probe_id: str, plant, *, outcome, questions, result) -> dict:
    """The probe's mark for its kind: a respondent plant's (`respondent_probe_mark`), else the frame's (`probe_mark`)."""
    if isinstance(plant, RespondentPlant):
        return respondent_probe_mark(probe_id, plant, outcome=outcome, result=result)
    return probe_mark(probe_id, plant, outcome=outcome, questions=questions, result=result)


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


def _respondent_meta(source: str, part: int, link: str, plan: list, **more) -> dict:
    """What `validate.py` hands keel-cloud's validator for a `RESPONDENT` case (part, link, plan, founder values none),
    with the case's source."""
    return {"source": source, "part": part, "link": link, "plan": list(plan), "swept": [], "founder_values": None,
            **more}


def _respondent_cases(stem: str, entry_id: str, context: dict, meta: dict, exported, instructions_by_screen,
                      executor_module, *, n_runs, host) -> list:
    screen = contract_mod.SCREEN_RESPONDENT
    payload = prompts_mod.payload_for(instructions_by_screen.get(screen), context, exported.for_screen(screen))
    cases = []
    for run_index in range(1, n_runs + 1):
        case = prompts_mod.Case(case_id=f"{stem}/run{run_index}", kind="RESPONDENT", entry_id=entry_id,
                                screen=screen, subject=f"PART{RESPONDENT_PART}", run_index=run_index,
                                payload=payload, meta=dict(meta))
        case.prompt = prompts_mod.render(executor_module, payload, job_id=prompts_mod._slug(case.case_id), host=host)
        cases.append(case)
    return cases


def backtest_respondent_cases(entry, exported, instructions_by_screen, executor_module, *, n_runs, host) -> list:
    """Spec 110 FR-4: a back-test entry's part 1 of `RESPONDENT_QUESTIONS` on its primary link, built as the golden
    corpus's (`context.build_respondent`, now handed `problem` and `condition`) on the export's registry."""
    registry = getattr(exported, "registry", None) or entry.registry
    plan = entry.plan(registry)
    context = context_mod.build_respondent(entry, RESPONDENT_PART, plan, registry,
                                           exported.keys_for(contract_mod.SCREEN_RESPONDENT),
                                           link=context_mod.LINK_PRIMARY)
    meta = _respondent_meta(SOURCE_BACKTEST, RESPONDENT_PART, context_mod.LINK_PRIMARY, plan.get(RESPONDENT_PART) or [],
                            validation_mechanism=context_mod.validation_mechanism(entry),
                            validation_problem_statement=context_mod.problem_statement(entry),
                            offer_name=context_mod.offer_name_of(entry))
    return _respondent_cases(f"{entry.id}/RESPONDENT_PART{RESPONDENT_PART}", entry.id, context, meta, exported,
                             instructions_by_screen, executor_module, n_runs=n_runs, host=host)


def redraft_context(entry, vector: str, key: str, answer: str, registry, keys) -> dict:
    """Spec 112 FR-3 (keel-cloud 087 judgement call 8, `ScreenContextBuilder`'s CALIBRATION_QUESTIONS): the redraft job
    of one list dimension -- the seed-time job (`context.build_calibration`) with `dimensions` cut to that one and
    `answers` the founder's typed Answer for it, `{key: answer}`. Before this spec no screen handed the writer an
    Answer (`answers` was always `{}`), so keel-cloud 171's *the founder's efforts first* could not be screened."""
    context = context_mod.build_calibration(entry, vector, registry, keys)
    if "dimensions" in context:
        context["dimensions"] = [d for d in context.get("dimensions") or [] if d.get("key") == key]
    if "answers" in context:
        context["answers"] = {key: answer}
    return context


def brand_names(entry) -> list[str]:
    """Spec 112 FR-3: the names an `asked` clause must never carry (keel-cloud 171 FR-4: *no idea, company or product
    name*) -- the entry's own name (its title before the dash, *Codyco*), the idea's short name and the offer's name
    where the entry records them."""
    title = str(getattr(entry, "title", "") or "")
    names = [title.split(" \u2014 ")[0].strip()] if " \u2014 " in title else []
    names += [n for n in (context_mod.short_name_of(entry), context_mod.offer_name_of(entry)) if n]
    out = []
    for name in names:
        if name and name.lower() not in [o.lower() for o in out]:
            out.append(name)
    return out


def backtest_calibration_cases(entry, exported, instructions_by_screen, executor_module, *, n_runs, host) -> list:
    """Spec 112 FR-3 (keel-cloud 171 FR-6): a back-test entry's `CALIBRATION_QUESTIONS` redraft of every list
    dimension it typed an Answer for (the walk's own words, `vectors_script.calibration_answers`' `text`), one case a
    dimension -- `<id>/CALIBRATION_<VECTOR>/<DIMENSION>/run<N>`, so `-k 21-codyco/CALIBRATION_SOLUTION` names the
    vector's and `.../ADOPTION_FRICTION` the one. Adoption friction's carries its 171 mark row (`meta["steps"]`): the
    typed efforts in their order and the names no `asked` may say; since spec 113 FR-4 Relative advantage's carries its
    173 mark row (`meta["benefits"]`): the typed benefits, each one row as typed. Rendered and validated, never
    scored."""
    from harness import vectors_script as vs                               # noqa: PLC0415
    registry = getattr(exported, "registry", None) or entry.registry
    keys = exported.keys_for(contract_mod.SCREEN_CALIBRATION)
    screen = contract_mod.SCREEN_CALIBRATION
    cases = []
    for vector in context_mod.VECTORS:
        if vector not in vs.scope_vectors(entry):
            continue
        for answer in vs.calibration_answers(entry, vector):
            key = answer.dimension
            if not vs.is_list(key) or answer.unsure or not (answer.text or "").strip():
                continue
            context = redraft_context(entry, vector, key, answer.text, registry, keys)
            subject = key.split(".", 1)[-1].upper()
            meta = {"source": SOURCE_BACKTEST, "vector": vector, "dimension": key, "registry_slice": [key],
                    "answer": answer.text, "short_name": context_mod.short_name_of(entry),
                    "offer_name": context_mod.offer_name_of(entry),
                    "validation_mechanism": context_mod.validation_mechanism(entry),
                    "validation_problem_statement": context_mod.problem_statement(entry)}
            if key == STEPS_KEY:
                meta["steps"] = {"mark": STEPS_MARK, "dimension": key, "typed": answer.text.split("; "),
                                 "names": brand_names(entry)}
            if key == BENEFITS_KEY:
                # spec 113 FR-4 (keel-cloud 173 FR-3): the typed benefits, each one row as typed
                meta["benefits"] = {"mark": BENEFITS_MARK, "dimension": key, "typed": answer.text.split("; ")}
            payload = prompts_mod.payload_for(instructions_by_screen.get(screen), context,
                                              exported.for_screen(screen))
            for run_index in range(1, n_runs + 1):
                case = prompts_mod.Case(case_id=f"{entry.id}/CALIBRATION_{vector}/{subject}/run{run_index}",
                                        kind="CALIBRATION", entry_id=entry.id, screen=screen,
                                        subject=f"{vector}/{subject}", run_index=run_index, payload=payload,
                                        meta=dict(meta))
                case.prompt = prompts_mod.render(executor_module, payload, job_id=prompts_mod._slug(case.case_id),
                                                 host=host)
                cases.append(case)
    return cases


def _named(name: str, text: str) -> bool:
    return bool(re.search(r"(?<![\w'])" + re.escape(name) + r"(?![\w])", text or "", re.IGNORECASE))


def steps_mark(entry_id: str, row: dict, *, outcome, result) -> dict:
    """Spec 112 FR-3, keel-cloud 171 FR-6's acceptance on one back-test Adoption friction redraft's first turn:
    COMPLETED, one `solution.adoption_friction` question, its draft **the founder's efforts first and as typed** (the
    first rows the typed labels word for word, in their order, and no other unmarked row), **at most one `suggested`
    row, last, with a `suggested_why`**, and **no brand in any `asked`** (`row["names"]`, whole words, any case).
    Mechanical: whether the suggestion fits this actor (another role's step, one the idea removes, one with no footing)
    is recorded for a reader -- `suggested`, each clause's words -- never judged here; the 10-word clause is the
    registry's option rule, recorded (`clause_words`), the frame's `K2` the validator's."""
    from . import spoken as spoken_mod                                      # noqa: PLC0415
    typed, names = list(row.get("typed") or []), list(row.get("names") or [])
    faults, items = [], []
    if outcome != "COMPLETED":
        faults.append(f"the first turn is {outcome or 'no outcome'}, not COMPLETED")
    else:
        result = result if isinstance(result, dict) else {}
        drafted = [q for q in result.get("questions") or [] if isinstance(q, dict) and q.get("key") == STEPS_KEY]
        if len(drafted) != 1:
            faults.append(f"{len(drafted)} {STEPS_KEY} questions, not one")
        else:
            items = [i for i in ((drafted[0].get("list") or {}).get("items") or []) if isinstance(i, dict)]
            labels = [str(i.get("label") or "") for i in items]
            if labels[:len(typed)] != typed:
                faults.append(f"the founder's efforts are not first and as typed: drafted {labels!r}, typed {typed!r}")
            unmarked = [str(i.get("label") or "") for i in items if not i.get("suggested")
                        and str(i.get("label") or "") not in typed]
            if unmarked:
                faults.append(f"a row the founder did not type is not marked suggested: {unmarked!r}")
            marked = [n for n, i in enumerate(items) if i.get("suggested")]
            if len(marked) > 1:
                faults.append(f"{len(marked)} suggested rows; at most one")
            if marked and marked[-1] != len(items) - 1:
                faults.append(f"the suggested row {labels[marked[-1]]!r} is not last")
            for n in marked:
                if not str(items[n].get("suggested_why") or "").strip():
                    faults.append(f"the suggested row {labels[n]!r} carries no suggested_why")
            for n, item in enumerate(items):
                said = [name for name in names if _named(name, str(item.get("asked") or ""))]
                if said:
                    faults.append(f"item {n + 1}'s asked {item.get('asked')!r} names {said!r}")
    suggested = [{"label": i.get("label"), "why": i.get("suggested_why")} for i in items if i.get("suggested")]
    return {"entry": entry_id, "screen": contract_mod.SCREEN_CALIBRATION, "mark": STEPS_MARK,
            "dimension": STEPS_KEY, "typed": typed, "drafted": [i.get("label") for i in items],
            "suggested": suggested, "names": names,
            "clause_words": [spoken_mod.words(i.get("asked")) for i in items],
            "outcome": outcome, "held": not faults, "faults": faults}


def _said(text) -> list[str]:
    """A row's words as the mark compares them: case folded, punctuation at either end of a word dropped."""
    return [w for w in (re.sub(r"^\W+|\W+$", "", t) for t in str(text or "").lower().split()) if w]


def _as_typed(drafted: str, typed: str) -> bool:
    """keel-cloud 173's *as typed (tidied to the limits only)*: the row is the typed benefit word for word (case and
    end punctuation aside), or, where the typed benefit is past `BENEFIT_MAX_WORDS`, its own words in their order with
    some left out, within the limit -- never a word the founder did not type."""
    row, said = _said(drafted), _said(typed)
    if row == said:
        return True
    if len(said) <= BENEFIT_MAX_WORDS or not row or len(row) > BENEFIT_MAX_WORDS:
        return False
    rest = iter(said)
    return all(word in rest for word in row)


def benefits_mark(entry_id: str, row: dict, *, outcome, result) -> dict:
    """Spec 113 FR-4, keel-cloud 173 FR-3's acceptance on one back-test Relative advantage redraft's first turn:
    COMPLETED, one `solution.relative_advantage` question, its draft **one row per benefit the Answer names, as typed**
    (tidied to the limits only, `_as_typed`), in the typed order, **never split** (a *without* or *while keeping* clause
    stays in its row: more rows than typed benefits is a fault) and **Keel adds none** (no `suggested` row, 173 T009).
    10-palus's *Higher yield without hiring for treasury* is one row. Mechanical; the `outcome_not_difference` mark, if
    any, is the validator's, and each row's words are recorded for a reader (`row_words`)."""
    typed = list(row.get("typed") or [])
    faults, items = [], []
    if outcome != "COMPLETED":
        faults.append(f"the first turn is {outcome or 'no outcome'}, not COMPLETED")
    else:
        result = result if isinstance(result, dict) else {}
        drafted = [q for q in result.get("questions") or [] if isinstance(q, dict) and q.get("key") == BENEFITS_KEY]
        if len(drafted) != 1:
            faults.append(f"{len(drafted)} {BENEFITS_KEY} questions, not one")
        else:
            items = [i for i in ((drafted[0].get("list") or {}).get("items") or []) if isinstance(i, dict)]
            labels = [str(i.get("label") or "") for i in items]
            if len(labels) > len(typed):
                faults.append(f"{len(labels)} rows for {len(typed)} typed benefits: one row per benefit, never split "
                              f"and none added -- drafted {labels!r}, typed {typed!r}")
            elif len(labels) < len(typed):
                faults.append(f"{len(labels)} rows for {len(typed)} typed benefits: a typed benefit is missing or "
                              f"merged -- drafted {labels!r}, typed {typed!r}")
            for n, (label, said) in enumerate(zip(labels, typed)):
                if not _as_typed(label, said):
                    faults.append(f"row {n + 1} {label!r} is not the typed benefit {said!r} as typed")
            added = [str(i.get("label") or "") for i in items if i.get("suggested")]
            if added:
                faults.append(f"Keel adds no benefit: {added!r} is marked suggested")
    return {"entry": entry_id, "screen": contract_mod.SCREEN_CALIBRATION, "mark": BENEFITS_MARK,
            "dimension": BENEFITS_KEY, "typed": typed, "drafted": [i.get("label") for i in items],
            "row_words": [len(_said(i.get("label"))) for i in items],
            "outcome": outcome, "held": not faults, "faults": faults}


def respondent_probe_context(probe: Probe, registry, keys) -> dict:
    """A respondent probe's `job_context` as the job is handed it: the export's keys in their order, each item filled
    with the registry's respondent fields and the window the way `context.respondent_item` / `fill_window` fill them; a
    key the builder does not write on part 1 (`mechanism`, `offer_name`) left out, as `ScreenContextBuilder` leaves it."""
    from .registry import RecallWindow, fill_window                         # noqa: PLC0415
    job = dict(probe.job_context or {})
    link = job.get("link") or context_mod.LINK_PRIMARY
    window = RecallWindow.read(probe.recall_window) if probe.recall_window else None
    items = [context_mod.respondent_item(registry.by_key(i["key"]), link=link) for i in job.get("items") or []]
    job["items"] = fill_window(items, window) if window is not None else items
    return {key: job.get(key) for key in keys if key in job}


def probe_respondent_cases(probe: Probe, exported, instructions_by_screen, executor_module, *, n_runs, host) -> list:
    """Spec 110 FR-4: one respondent probe's part-1 cases, marked by `respondent_probe_mark` (`meta["probe"]`)."""
    plant = probe.plant_for(contract_mod.SCREEN_RESPONDENT)
    keys = exported.keys_for(contract_mod.SCREEN_RESPONDENT)
    context = respondent_probe_context(probe, exported.registry, keys)
    meta = _respondent_meta(SOURCE_PROBE, RESPONDENT_PART, (probe.job_context or {}).get("link")
                            or context_mod.LINK_PRIMARY, [i["key"] for i in probe.job_context["items"]],
                            probe=plant.record())
    return _respondent_cases(f"{probe.id}/RESPONDENT_PART{RESPONDENT_PART}", probe.id, context, meta, exported,
                             instructions_by_screen, executor_module, n_runs=n_runs, host=host)


def build_cases(entries: ScreenEntries, exported, instructions_by_screen, executor_module, *, needle: str,
                n_runs: int = 3, host: str = "claude") -> list:
    """The extras' cases, in the golden cases' ids (`<id>/<SCREEN>/run<N>`), the needle applied as `-k` applies it
    (a case-insensitive substring of the case id). Each case's `meta["source"]` says what it is; a probe case also
    carries its plant (`meta["probe"]`), which `probe_mark` reads."""
    cases = []
    for entry in entries.backtest:
        frames = [s for s in BACKTEST_SCREENS
                  if s not in (contract_mod.SCREEN_RESPONDENT, contract_mod.SCREEN_CALIBRATION)]
        cases += _frame_cases(entry, frames, exported, instructions_by_screen, executor_module,
                              n_runs=n_runs, host=host, meta_for=lambda screen: {"source": SOURCE_BACKTEST})
        cases += backtest_respondent_cases(entry, exported, instructions_by_screen, executor_module,
                                           n_runs=n_runs, host=host)
        cases += backtest_calibration_cases(entry, exported, instructions_by_screen, executor_module,
                                            n_runs=n_runs, host=host)
    for probe in entries.probes:
        if probe.respondent():
            cases += probe_respondent_cases(probe, exported, instructions_by_screen, executor_module,
                                            n_runs=n_runs, host=host)
            continue
        screens = [s for s in PROBE_SCREENS if probe.plant_for(s) is not None]
        cases += _frame_cases(probe, screens, exported, instructions_by_screen, executor_module,
                              n_runs=n_runs, host=host,
                              meta_for=lambda screen, probe=probe: {"source": SOURCE_PROBE,
                                                                    "probe": probe.plant_for(screen).record()})
    word = needle.strip().lower()
    return [c for c in cases if word in c.case_id.lower()]


def is_extra(case) -> bool:
    return (getattr(case, "meta", None) or {}).get("source") in (SOURCE_BACKTEST, SOURCE_PROBE)


def plant_of(case):
    row = (case.meta or {}).get("probe") if (case.meta or {}).get("source") == SOURCE_PROBE else None
    if not row:
        return None
    if "verdict_words" in row:
        return RespondentPlant(**{**row, "planted": tuple(row["planted"]), "verdict_words": tuple(row["verdict_words"]),
                                  "keeps": tuple(row["keeps"])})
    return Plant(**row)


def steps_row_of(case):
    """Spec 112 FR-3: a back-test Adoption friction redraft's 171 mark row, else None."""
    meta = getattr(case, "meta", None) or {}
    return meta.get("steps") if meta.get("source") == SOURCE_BACKTEST else None


def benefits_row_of(case):
    """Spec 113 FR-4: a back-test Relative advantage redraft's 173 mark row, else None."""
    meta = getattr(case, "meta", None) or {}
    return meta.get("benefits") if meta.get("source") == SOURCE_BACKTEST else None
