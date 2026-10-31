"""Spec 063: the example gallery export -- the back-test ideas' briefs into the sample snapshot, each a simulated study
inspired by a named company (amendment of record, 2026-10-23). **Spec 106**: each example is three studies.

`make gallery RUNS=<dir>[,<dir>...] OUT=<dir>` (FR-1) reads finished `make backtest` run directories (spec 062) and
writes, for each entry, its three studies -- `<OUT>/<slug>/<study>/` for `problem`, `solution` and `money`, each the 060
file set plus `interview.json` (FR-3a) and `manifest.json` (FR-3) -- then one `<OUT>/index.json`. No stack, no model, no
paid run: everything is read from the run directories.

What a run directory gives, and what is read from where (tasks.md, judgement calls 1-3):

- `export/` -- spec 062 FR-3's ungated 060/061 snapshot of the founder's reads (names kept, emails, the founder and
  tokens withheld), its `manifest.json` listing every file. That IS the 060 file set; it is read back, withheld again
  (a no-op on a good run, a guard on a bad one).
- `backtest.json` -- the entry (`id`, `b2b`, `idea_name`), the study's `scope` (spec 071 FR-4), the stack's SHAs
  (`stack`), and per link `respondents[link].served` (the interview the stranger's page fetched, spec 062 FR-4.2) and
  `.drawn` (what the page drew for the run's one watched person: the kickers, the gate's chip labels, the follow-up
  screen).
- `transcript.jsonl` -- the follow-up stems the run's people were asked (`<person>: the one follow-up -- owed on ...`,
  the route's 200 `text`).
- `inputs.json` -- what the founder entered (`founder`: the project name, the four context fields, the window, the
  problem statement, the decider, the calibration answers), for `oneLine`, `problem` and the seven `axes`.

The back-test entries themselves are NOT loaded through `instructions.corpus.load`: they are corpus revision 13 in
keel-cloud now, and this eval's loader reads revision 12 until spec 064 (judgement call 1).

Attribution (the amendment of record, 2026-10-23, over FR-2 and FR-3): the real company name is the example's
attribution, everywhere, so nothing is renamed. Each index row and every study's `manifest.json` carry `inspiredBy
{name, batch, ycUrl}`, `publicDescription {text, url, date}` -- the launch-era words for the studied idea -- and, where
today's one-liner differs, `statusToday {text, url, date}` (from `instructions/gallery_names.toml`), `assumptions[]`
(the founder's belief sentences the study tested, as the standings served them), `simulated: true` and the
`disclaimer`. The attribution check refuses a slug missing any of them, or whose disclaimer is not the sentence.

**Spec 071 FR-5** (keel-cloud 133, design §9: *each example carries its configuration*): every index row carries
`scope`, the run's own (`backtest.json`'s, spec 071 FR-4); the attribution check accepts the five contract-38 values
and refuses anything else. Since spec 106 it is the problem study's, PROBLEM.

**Spec 079 FR-6** (the quality cycle's acceptance; the design's §8, *the homepage examples follow the baseline*):
`--scores quality/scores` puts the readers' gate in front of the export -- a run is an example only when its latest
score file (spec 078, matched by the file's `bundle` header, at the current `RUBRIC_VERSION`) has no flagged screen; a
run refused is named with its reason. Spec 106 FR-3 replaced its bar with the gallery's own last accepted score and
retired `--scope-order`. Without `--scores` there is no gate.

**Spec 106** (the founder, 2026-10-30: *"reduce it to three toggles -- problem, solution and commercial -- so the output
of each can be printed there; and instead of twenty, seven agents answer it"*):

- **FR-1 Three studies per example.** A cycle walks each entry as three studies (`quality/cycle.toml`: PROBLEM,
  SOLUTION, COMMERCIAL); the export writes all three, `problem` / `solution` / `money` (`STUDIES`). The index row
  carries `studies: {problem, solution, money}`, each with its own `decision`, `howSure`, `pilot`, `price`, `answered`
  and `invited`; the row's top-level fields are the problem study's (`TOP_STUDY`), so a reader of the one-study index
  still works (`scope` reads PROBLEM). An entry lacking one of the three, or given one twice, is refused by name and
  nothing is written for it (`three_studies`); a run of another scope (ALL, SOLUTION_COMMERCIAL) is no study of the
  gallery's. Spec 079's `--scope-order` and `one_per_entry` (one run per entry) are retired.
- **FR-2 The number of people, in words.** The disclaimer says the study's own count (`people_words`: *seven people
  answered, all simulated*; *six of the seven people invited answered* where one did not), read from the study's
  invitation register -- never a fixed twenty. Each study's manifest says its own; the row says the problem study's.
- **FR-3 The gate is the gallery's own last score** (the founder: *"the only time we should not do it is if the next
  rating comes below what we already have"*). With `--scores`, a study with no score file at the current rubric
  version, or with a flagged screen, is refused by name (spec 079 FR-6, kept); then the cycle's overall score_pct (the
  cycle record's head, or the runs' latest score files read as one) is held to the last accepted one, which every gated
  export records in its provenance file (`accepted`): **below it, the export is refused by name and nothing is
  written**; equal or above passes, whatever the 90% bar says, and with no accepted score yet (or one at another rubric
  version) the export passes. `--bar <pct>` is an optional stricter gate (a study under it is refused), off by default.
- **FR-4 Provenance and privacy as today.** The slug -> entry / study / run link goes once to
  `runs/gallery/provenance-<exportedAt>.json` (`{exportedAt, accepted, examples: [{slug, entry, cycle, studies: {study:
  {scope, run, cloud, web}}, renamed}]}`), outside OUT; no entry id, run name or source path is written under OUT --
  the check greps every byte under OUT for them.

A slug's directory is replaced whole; what keel-web adds to the snapshot by hand is kept across the refresh: the slug's
`cover.jpg` (keel-web spec 103) and the index row's `title`, `image` and `tests` (keel-web 103 / 104 / 107; `KEPT_KEYS`).
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import sys
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from evals import backtest as bt
from evals import sample_export as se

REPO = Path(__file__).resolve().parent.parent
NAMES_FILE = REPO / "instructions" / "gallery_names.toml"
RUNS_DIR = REPO / "runs"

INDEX = "index.json"
INTERVIEW = "interview"            # the read key; written as interview.json beside the 060 files
LINK_ORDER = ("PRIMARY", "COMMERCIAL_B2B")

#: Spec 106 FR-1: the gallery's three studies, in the index's order, and the back-test scope each is walked under
#: (keel-cloud 133's StudyScope; the money study is COMMERCIAL, *money alone*).
STUDIES = ("problem", "solution", "money")
STUDY_SCOPE = {"problem": "PROBLEM", "solution": "SOLUTION", "money": "COMMERCIAL"}
SCOPE_STUDY = {scope: study for study, scope in STUDY_SCOPE.items()}
#: FR-1: the index row's top-level fields are this study's, so a reader of the one-study index still works.
TOP_STUDY = "problem"
#: FR-1: what `studies[<study>]` carries on the index row, each the study's own.
STUDY_FIGURES = ("decision", "howSure", "pilot", "price", "answered", "invited")

#: The amendment of record's attribution, alike in every index row and its slug's manifest.
ATTRIBUTION = ("inspiredBy", "publicDescription", "statusToday", "simulated", "disclaimer", "assumptions")
#: The attribution that is the example's, not a study's: alike in the row and all three manifests (the disclaimer
#: names each study's own people and the assumptions are each study's own beliefs).
SHARED_ATTRIBUTION = ("inspiredBy", "publicDescription", "statusToday", "simulated")

#: What keel-web writes into the snapshot by hand and a refresh keeps: the index row's keys (keel-web 103's `image`,
#: 104's `tests`, 107's `title`) and the slug's own files beside its studies (103's cover).
KEPT_KEYS = ("title", "image", "tests")
KEPT_FILES = ("cover.jpg",)

#: FR-1's seven gallery words, in the spec's order.
AXES = ("whoHasIt", "whoPays", "rhythm", "costMode", "priceShape", "firstStep", "kind")

#: FR-3 (amended 2026-10-22): the slug -> entry / run link is written here, once an export, and never under OUT
#: (`runs/` is ignored by git, as every run file is).
PROVENANCE_DIR = RUNS_DIR / "gallery"
PROVENANCE_GLOB = "provenance-*.json"

#: Keys never written into interview.json (FR-3a: tokens and ids withheld; the AI interviewer's forms are a later spec).
_DROPPED = frozenset({"itemId", "optionId", "id", "token", "costItemId", "advantagesWhen", "spoken", "clip", "clips"})

_RHYTHM = {"NIGHTS": "nightly", "DAYS": "daily", "WORKING_DAYS": "every working day", "WEEKS": "weekly",
           "MONTHS": "monthly"}
_PERIODLY = {"day": "daily", "week": "weekly", "month": "monthly", "quarter": "quarterly", "year": "yearly"}
_SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_YC = "https://www.ycombinator.com/companies/"

#: The amendment of record's sentence, `name` and `batch` filled from `inspiredBy` and, since spec 106 FR-2, `people`
#: from the study's own invitation register (`people_words`) -- never a fixed number.
DISCLAIMER = ("A simulated study inspired by {name} (Y Combinator {batch}): {people}, all simulated. The founder's "
              "answers, the people and everything they said are fictional, written from {name}'s public material to "
              "show what Keel does. Not customer research about {name}; not affiliated with {name} or Y Combinator.")
#: Spec 106 FR-2: the numbers the disclaimer spells (keel-web's `COUNT_WORDS`, one to twenty); past twenty, digits.
NUMBER_WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
                "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty")
#: Invitation status keel-cloud's register says of a link whose person answered (`FounderViewAssembler.status`).
ANSWERED = "ANSWERED"


class GalleryRefused(AssertionError):
    """The export refuses, its reasons named. Nothing was written."""

    def __init__(self, reasons: list[str]):
        self.reasons = list(reasons)
        super().__init__("the gallery export refuses: " + "; ".join(self.reasons))


class NothingToBuild(GalleryRefused):
    """Every study was refused by the readers' gate, or no entry has its three studies: the gallery is left as it is."""


def number_words(n: int) -> str:
    """Spec 106 FR-2: *seven*; past twenty the digits."""
    return NUMBER_WORDS[n] if 0 <= n < len(NUMBER_WORDS) else str(n)


def people_words(invited: int, answered: int | None = None) -> str:
    """Spec 106 FR-2: who answered, in words -- *seven people answered*; where fewer answered than the study invited
    (a gate No walked nowhere on money alone, spec 102), *six of the seven people invited answered*."""
    answered = invited if answered is None else answered
    noun = "person" if invited == 1 else "people"
    if answered == invited:
        return f"{number_words(invited)} {noun} answered"
    return f"{'none' if answered == 0 else number_words(answered)} of the {number_words(invited)} {noun} invited answered"


# ------------------------------------------------------------------------------------------------ FR-2 the map

@dataclass(frozen=True)
class GalleryName:
    entry: str
    slug: str
    name: str
    replaces: tuple[str, ...]          # () since 2026-10-23: the rename map went
    inspired_by: dict = field(default_factory=dict, hash=False, compare=False)
    public_description: dict = field(default_factory=dict, hash=False, compare=False)   # launch-era (1d42c51)
    status_today: dict = field(default_factory=dict, hash=False, compare=False)         # optional: what they say now
    cluster: dict = field(default_factory=dict, hash=False, compare=False)              # {id, label} (a35af52)
    keywords: tuple[str, ...] = ()                     # optional: overrides the derived keywords
    axes: dict = field(default_factory=dict, hash=False, compare=False)

    def disclaimer(self, invited: int, answered: int | None = None) -> str | None:
        """The sentence for one study of this example: its people in words (spec 106 FR-2)."""
        name, batch = (self.inspired_by or {}).get("name"), (self.inspired_by or {}).get("batch")
        if not (name and batch):
            return None
        return DISCLAIMER.format(name=name, batch=batch, people=people_words(invited, answered))


def load_names(path: Path = NAMES_FILE) -> list[GalleryName]:
    """`instructions/gallery_names.toml`, in its order; refuses a malformed table by name."""
    raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    rows = raw.get("gallery") or []
    out: list[GalleryName] = []
    problems: list[str] = []
    for i, row in enumerate(rows):
        entry, slug, name, replaces = row.get("entry"), row.get("slug"), row.get("name"), row.get("replaces")
        if not (isinstance(entry, str) and entry):
            problems.append(f"gallery[{i}] has no entry")
            continue
        if not (isinstance(slug, str) and _SLUG.match(slug)):
            problems.append(f"{entry}: slug {slug!r} is not lowercase letters, digits and hyphens")
        if not (isinstance(name, str) and name.strip()):
            problems.append(f"{entry}: no name")
        if replaces not in (None, []):
            problems.append(f"{entry}: replaces must be [] -- the rename map went (spec 063, 2026-10-23)")
        replaces = []
        axes = row.get("axes") or {}
        unknown = sorted(set(axes) - set(AXES))
        if unknown:
            problems.append(f"{entry}: axes {unknown} are not among {list(AXES)}")
        out.append(GalleryName(entry=entry, slug=slug or "", name=name or "", replaces=tuple(replaces),
                               inspired_by=dict(row.get("inspired_by") or {}),
                               public_description=dict(row.get("public_description") or {}),
                               status_today=dict(row.get("status_today") or {}),
                               cluster=dict(row.get("cluster") or {}), keywords=tuple(row.get("keywords") or ()),
                               axes=dict(axes)))
    for what in ("entry", "slug", "name"):
        seen = [getattr(n, what) for n in out]
        dupes = sorted({v for v in seen if seen.count(v) > 1})
        if dupes:
            problems.append(f"{what} repeated: {dupes}")
    if problems:
        raise GalleryRefused([f"{path.name}: {p}" for p in problems])
    return out


# --------------------------------------------------------------------------------------------- the run directory

@dataclass
class Run:
    """What one back-test run directory gives the export (read-only)."""
    dir: Path
    record: dict                       # backtest.json
    founder: dict                      # inputs.json `founder`
    reads: dict[str, Any]              # export/ -- the 060 file set, keyed as 060 keys it
    corpus: int | None
    follow_ups: list[dict]             # [{link, dimension, question, kicker, note}] in transcript order

    @property
    def entry(self) -> str:
        return (self.record.get("entry") or {}).get("id") or ""

    @property
    def b2b(self) -> bool:
        return bool((self.record.get("entry") or {}).get("b2b"))

    @property
    def scope(self) -> str:
        """Spec 071 FR-4: the study's scope the run was walked under; ALL for a run recorded before scopes."""
        return str(self.record.get("scope") or bt.DEFAULT_SCOPE)

    @property
    def study(self) -> str | None:
        """Spec 106 FR-1: which of the gallery's three studies the run is (`problem`, `solution`, `money`), or None."""
        return SCOPE_STUDY.get(self.scope)


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_follow_ups(transcript: Path) -> list[dict]:
    """Every follow-up the run's pages showed (the route answered 200 with a filled `text`), in transcript order."""
    out: list[dict] = []
    if not transcript.is_file():
        return out
    for line in transcript.read_text(encoding="utf-8").splitlines():
        if "the one follow-up" not in line:
            continue
        try:
            step = json.loads(line)
        except ValueError:
            continue
        req, resp = step.get("request") or {}, step.get("response") or {}
        if "the one follow-up" not in (step.get("name") or "") or not isinstance(req, dict):
            continue
        if req.get("route") != 200 or not req.get("text"):
            continue
        screen = req.get("screen") or {}
        out.append({"link": (resp or {}).get("link"), "dimension": req.get("dimension"), "question": req["text"],
                    "kicker": screen.get("kicker"), "note": screen.get("note")})
    return out


def read_run(run_dir: Path) -> Run:
    """One run directory, or `GalleryRefused` naming what it lacks."""
    run_dir = Path(run_dir)
    missing = [p for p in (bt.RECORD, "inputs.json", f"{bt.EXPORT_DIR}/{se.MANIFEST}") if not (run_dir / p).is_file()]
    if missing:
        raise GalleryRefused([f"{run_dir.name}: no {', '.join(missing)}"])
    record = _json(run_dir / bt.RECORD)
    if not record.get("passed"):
        raise GalleryRefused([f"{run_dir.name}: the back-test did not pass (failed at {record.get('failed_step')!r})"])
    manifest = _json(run_dir / bt.EXPORT_DIR / se.MANIFEST)
    reads: dict[str, Any] = {}
    for rel in manifest.get("files") or []:
        path = run_dir / bt.EXPORT_DIR / rel
        if not path.is_file():
            raise GalleryRefused([f"{run_dir.name}: export/{rel} is listed and missing"])
        reads[rel[:-len(".json")] if rel.endswith(".json") else rel] = _json(path)
    absent = [k for k in se.TOP_READS if k not in reads]
    if absent:
        raise GalleryRefused([f"{run_dir.name}: the export lacks {absent}"])
    return Run(dir=run_dir, record=record, founder=(_json(run_dir / "inputs.json") or {}).get("founder") or {},
               reads=reads, corpus=manifest.get("corpus"), follow_ups=read_follow_ups(run_dir / "transcript.jsonl"))


def _finished(path: Path) -> dict | None:
    """A run directory's record when the back-test finished with an export, else None."""
    if not (path.is_dir() and (path / bt.EXPORT_DIR / se.MANIFEST).is_file() and (path / bt.RECORD).is_file()):
        return None
    try:
        record = _json(path / bt.RECORD)
    except (OSError, ValueError):
        return None
    return record if record.get("passed") else None


def newest_runs(names: list[GalleryName], runs_dir: Path = RUNS_DIR) -> tuple[list[Path], list[str]]:
    """FR-1's default: for each entry of the map and each of the three studies (spec 106), the newest
    `*-backtest-<entry>` directory walked under that study's scope that finished with an export (the stamp prefix sorts
    by time) -- `(the runs, one reason per entry lacking a study)`; such an entry is refused by name, never built from
    what it has."""
    runs_dir = Path(runs_dir)
    out, missing = [], []
    for n in names:
        found: dict[str, Path] = {}
        for p in sorted(runs_dir.glob(f"*-backtest-{n.entry}")):
            record = _finished(p)
            study = SCOPE_STUDY.get(str((record or {}).get("scope") or bt.DEFAULT_SCOPE)) if record else None
            if study:
                found[study] = p                                          # sorted: the newest wins
        lacking = [s for s in STUDIES if s not in found]
        if lacking:
            missing.append(f"{n.entry}: no finished back-test run of its {', '.join(lacking)} "
                           f"stud{'y' if len(lacking) == 1 else 'ies'} "
                           f"({', '.join(STUDY_SCOPE[s] for s in lacking)}) under {runs_dir} -- an example is three "
                           "studies; nothing is written for it")
            continue
        out.extend(found[s] for s in STUDIES)
    return out, missing


def resolve_runs(spec: str, runs_dir: Path = RUNS_DIR) -> list[Path]:
    """`RUNS=a,b,...`: each a path, or a directory name under `runs_dir`."""
    out = []
    for part in (p.strip() for p in spec.split(",")):
        if not part:
            continue
        path = Path(part).expanduser()
        if not path.is_dir() and (Path(runs_dir) / part).is_dir():
            path = Path(runs_dir) / part
        out.append(path)
    return out


def _record_of(run_dir: Path) -> dict:
    try:
        return _json(Path(run_dir) / bt.RECORD)
    except (OSError, ValueError):
        return {}


def _not_a_study(name: str, scope: str) -> str:
    return (f"{name}: a {scope} run is not one of the gallery's three studies ("
            + ", ".join(f"{s} = {STUDY_SCOPE[s]}" for s in STUDIES) + ") -- spec 106 FR-1")


def _lacks(entry: str, studies: Iterable[str]) -> str:
    lacking = [s for s in STUDIES if s not in set(studies)]
    return (f"{entry}: no {' and no '.join(f'{s} study ({STUDY_SCOPE[s]})' for s in lacking)} -- an example is three "
            "studies (problem, solution, money), never a partial one; nothing is written for it")


def three_studies(run_dirs: list[Path]) -> tuple[list[Path], list[str]]:
    """Spec 106 FR-1: the runs of every entry that has its three studies, each once, in the order given -- and one
    reason per run or entry set aside, by name: a run of another scope (ALL, SOLUTION_COMMERCIAL), an entry given one
    study twice, an entry lacking one. What is set aside is never written; the rest are."""
    by_entry: dict[str, dict[str, list[Path]]] = {}
    order: list[str] = []
    reasons = []
    for run_dir in run_dirs:
        run_dir = Path(run_dir)
        record = _record_of(run_dir)
        entry = (record.get("entry") or {}).get("id") or run_dir.name
        scope = str(record.get("scope") or bt.DEFAULT_SCOPE)
        if scope not in SCOPE_STUDY:
            reasons.append(_not_a_study(run_dir.name, scope))
            continue
        if entry not in by_entry:
            order.append(entry)
        by_entry.setdefault(entry, {}).setdefault(SCOPE_STUDY[scope], []).append(run_dir)
    kept = []
    for entry in order:
        studies = by_entry[entry]
        twice = {s: runs for s, runs in studies.items() if len(runs) > 1}
        if twice:
            reasons.append(f"{entry}: " + "; ".join(f"the {s} study given {len(r)} times ({', '.join(p.name for p in r)})"
                                                    for s, r in twice.items()) + " -- nothing is written for it")
        elif set(studies) != set(STUDIES):
            reasons.append(_lacks(entry, studies))
        else:
            kept.extend(studies[s][0] for s in STUDIES)
    return kept, reasons


# ------------------------------------------------------------------------------------------ FR-3a the interview

def _scrub(value: Any) -> Any:
    """A JSON value with every id, token and AI-interviewer form dropped (FR-3a)."""
    if isinstance(value, dict):
        return {k: _scrub(v) for k, v in value.items() if k not in _DROPPED}
    if isinstance(value, list):
        return [_scrub(v) for v in value]
    return value


def _labels(rows: Any) -> list:
    return [r.get("label") if isinstance(r, dict) else r for r in rows or []]


def _escape(value: Any) -> str | None:
    return value.get("label") if isinstance(value, dict) else value


def _item(served: dict, drawn: dict) -> dict:
    item = {"dimension": served.get("dimension"),
            "kicker": served.get("kicker") or drawn.get("kicker") or None,
            "question": served.get("question"),
            "control": served.get("control"),
            "hint": served.get("hint") or drawn.get("hint") or None,
            "options": _labels(served.get("options")),
            "escape": _escape(served.get("escape")),
            "shown": list(drawn.get("rows") or [])}
    if served.get("advantages"):
        # spec 090 FR-2 (keel-web 135 H-9): contract 47 serves no `advantages` (keel-cloud 159's one scale); a run
        # recorded before it keeps its benefits, read as recorded, beside the options -- never an empty list
        item = {**{k: item[k] for k in ("dimension", "kicker", "question", "control", "hint", "options")},
                "advantages": _labels(served.get("advantages")), "escape": item["escape"], "shown": item["shown"]}
    if served.get("advantagesPrompt"):
        item["advantagesPrompt"] = served["advantagesPrompt"]
    for key in ("scale", "numeric", "costTotal", "valueBox", "whatYouGet"):
        if served.get(key) not in (None, "", [], {}):
            item[key] = _scrub(served[key])
    plan = served.get("plan")
    if plan:
        item["plan"] = {"question": plan.get("question"), "options": _labels(plan.get("options"))}
    return item


def link_interview(link: str, respondent: dict, *, label: str | None, follow_ups: list[dict]) -> dict:
    """One link's interview as the stranger's page received it (backtest.json's `served`), with what only the page
    drew filled from `drawn` (the item kickers, the gate chip labels), and the follow-up stems the link's people were
    asked."""
    served = respondent.get("served") or {}
    drawn = respondent.get("drawn") or []
    by_dimension = {d.get("dimension"): d for d in drawn if d.get("screen") == "item" and d.get("dimension")}
    gate_drawn = next((d for d in drawn if d.get("screen") == "gate"), {})
    follow_drawn = next((d for d in drawn if d.get("screen") == "follow_up"), {})
    gate_served = served.get("gate") or None
    gate = None
    if gate_served:
        codes = list(gate_served.get("chips") or [])
        shown = list(gate_drawn.get("chips") or [])
        occasion = served.get("occasion") or "time"
        gate = {"kicker": gate_served.get("kicker") or gate_drawn.get("kicker"),
                "question": gate_served.get("question"),
                "chips": [{"code": c, "label": shown[i] if i < len(shown) else
                           (f"I can't recall one particular {occasion}" if c == "CANT_RECALL" else None)}
                          for i, c in enumerate(codes)],
                "exitText": gate_served.get("exitText")}
        if gate_served.get("condition"):
            gate["condition"] = _scrub(gate_served["condition"])
    parts = [{"part": p.get("part"), **({"title": p["title"]} if p.get("title") else {}),
              "items": [_item(i, by_dimension.get(i.get("dimension")) or {}) for i in p.get("items") or []]}
             for p in served.get("parts") or []]
    asked = []
    for f in follow_ups:
        if f.get("link") == link and f["question"] not in [a["question"] for a in asked]:
            asked.append({"dimension": f.get("dimension"), "question": f["question"]})
    first = next((f for f in follow_ups if f.get("link") == link), {})
    follow_up = ({"kicker": first.get("kicker") or follow_drawn.get("kicker"),
                  "note": first.get("note") or follow_drawn.get("note"), "asked": asked} if asked else None)
    return {"role": link, "label": label, "kind": served.get("kind"), "occasion": served.get("occasion"),
            "idea": _scrub(served.get("idea")) if served.get("idea") else None,
            "gate": gate,
            "storyPrompt": (gate_served or {}).get("storyPrompt"),
            "storyHint": (gate_served or {}).get("storyHint"),
            "parts": parts,
            "reveal": _scrub(served.get("reveal")) if served.get("reveal") else None,
            "followUp": follow_up}


def role_labels(plan: dict) -> dict[str, str]:
    """`{link: role label}` from the plan's respondent types (the decision-makers' is the commercial link)."""
    out = {}
    for t in (plan or {}).get("respondentTypes") or []:
        out["COMMERCIAL_B2B" if t.get("commercialLink") else "PRIMARY"] = t.get("label")
    return out


def interview(run: Run) -> dict:
    """FR-3a: every link of the run, the primary first, the decider's after it on B2B."""
    labels = role_labels(run.reads.get("plan") or {})
    respondents = run.record.get("respondents") or {}
    links = sorted(respondents, key=lambda k: (LINK_ORDER.index(k) if k in LINK_ORDER else len(LINK_ORDER), k))
    return {"links": [link_interview(k, respondents[k], label=labels.get(k), follow_ups=run.follow_ups)
                      for k in links]}


def item_count(link: dict) -> int:
    """The questions one link asks: the gate and every part's items (the roles' `questionCount`); the follow-up is
    not counted."""
    return (1 if link.get("gate") else 0) + sum(len(p.get("items") or []) for p in link.get("parts") or [])


# ------------------------------------------------------------------------------------------- FR-1 the index

def one_sentence(text: str | None) -> str | None:
    """The problem statement in one sentence: the words before the founder's `; based on ...` evidence clause, to
    the first full stop (judgement call 4). Word for word otherwise."""
    if not text:
        return None
    head = re.split(r";\s+based on\b", text, maxsplit=1)[0].strip()
    first = re.split(r"(?<=[.!?])\s+(?=[A-Z])", head, maxsplit=1)[0].strip()
    return first if first.endswith((".", "!", "?")) else first + "."


def one_line(project_name: str | None) -> str | None:
    """The project name's own tag line, after its dash ("Fresco -- the scribe for ..."), its first letter raised."""
    if not project_name:
        return None
    parts = re.split(r"\s+[—–-]{1,2}\s+", project_name, maxsplit=1)
    tail = (parts[1] if len(parts) > 1 else parts[0]).strip()
    return tail[:1].upper() + tail[1:] if tail else None


def _calibration(founder: dict, dimension: str) -> dict:
    for rows in (founder.get("calibration") or {}).values():
        for row in rows or []:
            if row.get("dimension") == dimension:
                return row
    return {}


def axes(run: Run, override: dict | None = None) -> dict:
    """FR-1's seven gallery words, read from what the founder entered (`inputs.json`) and the run's entry; any word
    `gallery_names.toml` writes for the entry wins (none does today)."""
    f = run.founder
    decider = f.get("decider") or {}
    window = f.get("window") or {}
    cost = _calibration(f, "commercial.existing_sacrifice").get("cost") or {}
    price = _calibration(f, "commercial.price").get("price") or {}
    step = ((_calibration(f, "commercial.commitment").get("list") or {}).get("items") or [{}])[0].get("label")
    who_pays = ("themselves" if decider.get("kind") == "SAME_PERSON"
                else decider.get("role") if decider.get("kind") == "SOMEONE_ELSE" else None)
    out = {"whoHasIt": (f.get("context_fields") or {}).get("actor"),
           "whoPays": who_pays,
           "rhythm": _RHYTHM.get(window.get("unit")),
           # The cost's mode as the calibration has carried it since keel-cloud's cost-first design (2026-10-10): HOURS
           # (time lost), MONEY (an amount, once AMOUNT), RATE (a share of a base, "1.5% of the rupees they move"),
           # COUNT (things missed). A mode this map does not know is written as it is, lower-cased, never left null.
           "costMode": {"HOURS": "time", "AMOUNT": "money", "MONEY": "money", "RATE": "share", "COUNT": "count"}.get(
               cost.get("mode"), (cost.get("mode") or "").lower() or None),
           "priceShape": _PERIODLY.get(price.get("period"), "one-off" if price and not price.get("period") else None),
           "firstStep": step,
           "kind": "business" if run.b2b else "consumer"}
    out.update({k: v for k, v in (override or {}).items() if k in AXES})
    return out


#: Words that carry no search meaning on their own: function words and the common verbs and adjectives the founders'
#: sentences are built from (a keyword is a thing to search for, so nouns are what survive).
_STOP = frozenset("""a able about accurate across actual after again all almost also always an and another any are
around as at away back based be because become been before being best better between big both bring but by can
cannot come comes could day days decide decides did do does doing done down during each easily easy else end enough
even ever every fast faster few find first for from full get gets give given go goes going good got great had happen
happens hard has have having help here high hold hours how however if in into is it its just keep keeps kind know
last least left less like little long lose loses losing lot low made make makes many may means more most much must
need needed needs never new next no nor not now of off often old on once one only or other our out over own part
people per real really right run same says see set should since six slow slowing small so some something sometimes
spend spends still such sure take takes than that the their them then there these they thing things think this
those three through time times to too true try turn two under until up upon use used uses using very want wants was
way week weeks well were what when where which while who whom why will with within without work works would year
years yet you your""".split())
KEYWORDS_MIN, KEYWORDS_MAX = 5, 12


def keywords(run: Run, name: GalleryName, *, occasion: str | None) -> list[str]:
    """5 to 12 plain lower-case words or short phrases for search and the radar's mail, drawn from what the founder
    entered and the run served: the actor and the occasion first, then the content words of the one-sentence problem
    statement and the four context fields together, the most repeated first (ties in reading order, the problem
    statement read first), no stop words, numbers or company names; a word is skipped when a phrase already carries it
    or when it is the plural of one taken. The map's `keywords` list, when written, is used instead."""
    if name.keywords:
        return [k.strip().lower() for k in name.keywords][:KEYWORDS_MAX]
    context = run.founder.get("context_fields") or {}
    banned = {w.lower() for w in (name.name, (name.inspired_by or {}).get("name") or "") if w}
    banned |= {part for w in banned for part in w.split()}
    out: list[str] = []

    def taken(word: str) -> bool:
        have = set(" ".join(out).split())
        return word in have or word.rstrip("s") in have or f"{word}s" in have

    for phrase in (context.get("actor"), occasion):
        phrase = " ".join((phrase or "").lower().split())
        if phrase and phrase not in out and phrase not in banned:
            out.append(phrase)
    text = " ".join(t or "" for t in (one_sentence(run.founder.get("problem_seed")), context.get("segment"),
                                      context.get("job"), context.get("circumstance")))
    words = [w.strip("'-") for w in re.findall(r"[a-z][a-z'-]+", text.lower())]
    words = [w for w in words if w not in _STOP and w not in banned and len(w) > 3 and not w.endswith("'s")]
    for w in sorted(dict.fromkeys(words), key=lambda w: (-words.count(w), words.index(w))):
        if len(out) >= KEYWORDS_MAX:
            break
        if not taken(w):
            out.append(w)
    return out


def gallery_order(rows: list[dict]) -> list[dict]:
    """B2B and B2C alternating, B2B first, each side in the map's order; the longer side's rest at the end."""
    b2b = [r for r in rows if r.get("b2b")]
    b2c = [r for r in rows if not r.get("b2b")]
    out = []
    for i in range(max(len(b2b), len(b2c))):
        out.extend(x[i] for x in (b2b, b2c) if i < len(x))
    return out


# --------------------------------------------------------------------------------------------- the one export

@dataclass
class Study:
    """One of an example's three studies (spec 106 FR-1): what goes under `OUT/<slug>/<key>/`."""
    key: str                           # problem | solution | money
    run: Run
    reads: dict[str, Any]              # withheld, interview included -- what is written
    manifest: dict                     # cloud, web, exportedAt and the attribution (the disclaimer the study's own)
    figures: dict                      # the index row's studies[key]: decision, howSure, pilot, price, answered, invited


@dataclass
class Slug:
    name: GalleryName
    studies: dict[str, Study]          # the three, in STUDIES order
    row: dict                          # the index row
    provenance: dict                   # the slug's row of runs/gallery/provenance-<exportedAt>.json, never under OUT

    @property
    def top(self) -> Study:
        """FR-1: the study whose fields are the row's own (the problem study)."""
        return self.studies[TOP_STUDY]

    @property
    def run(self) -> Run:
        return self.top.run


def assumptions(reads: dict[str, Any]) -> list[str]:
    """The founder's belief sentences the run tested, as the standings served them, stage by stage: every dimension
    asked (not left out, not yet asked) that carries a `belief`."""
    out = []
    for vector in (reads.get("standings") or {}).get("vectors") or []:
        for d in vector.get("dimensions") or []:
            text = (d.get("belief") or "").strip()
            if text and d.get("status") not in se.NOT_ASKED and text not in out:
                out.append(text)
    return out


def participants(reads: dict[str, Any]) -> int:
    """The people the study invited (the founder's invitation register): spec 106 FR-2's `invited`."""
    return len(se.invitation_ids(reads.get("invitations")))


def answered(reads: dict[str, Any]) -> int:
    """Spec 106 FR-2's `answered`: the study's links whose person answered (the register's `status` ANSWERED)."""
    register = reads.get("invitations")
    rows = ((register or {}).get("invitations") or []) if isinstance(register, dict) else (register or [])
    return sum(1 for r in rows if isinstance(r, dict) and r.get("status") == ANSWERED)


def attribution(name: GalleryName, reads: dict[str, Any], *, invited: int, answered_n: int) -> dict:
    """The amendment of record's fields, in the order written: `statusToday` only where the map has one (the company's
    current one-liner, where it differs from the launch-era `publicDescription`); the disclaimer names the study's own
    people (spec 106 FR-2)."""
    out = {"inspiredBy": {k: (name.inspired_by or {}).get(k) for k in ("name", "batch", "ycUrl")},
           "publicDescription": {k: (name.public_description or {}).get(k) for k in ("text", "url", "date")}}
    if name.status_today:
        out["statusToday"] = {k: name.status_today.get(k) for k in ("text", "url", "date")}
    return {**out,
            "simulated": True,
            "disclaimer": name.disclaimer(invited, answered_n),
            "assumptions": assumptions(reads)}


def prepare_study(name: GalleryName, key: str, run: Run, *, exported_at: str) -> Study:
    """One study in memory: withhold again (060), the interview (FR-3a), the attribution, the study's figures."""
    reads = se.withhold(run.reads, founder_name=bt.IDENTITY_NAME, founder_email=bt.IDENTITY_EMAIL).reads
    reads[INTERVIEW] = interview(run)
    card = se.card(reads)
    invited, answered_n = participants(reads), answered(reads)
    stack = run.record.get("stack") or {}
    shas = {"cloud": stack.get("keel-cloud"), "web": stack.get("keel-web")}
    figures = {"decision": card["decision"], "howSure": card["howSure"], "pilot": card["pilot"], "price": card["price"],
               "answered": answered_n, "invited": invited}
    return Study(key=key, run=run, reads=reads,
                 manifest={**shas, "exportedAt": exported_at,
                           **attribution(name, reads, invited=invited, answered_n=answered_n)},
                 figures=figures)


def prepare(name: GalleryName, runs: dict[str, Run], *, exported_at: str, cycle: str | None = None) -> Slug:
    """One slug in memory: its three studies (spec 106 FR-1), the index row (FR-1: the problem study's fields at the
    top, `studies` beside them), and the provenance row that is never written under OUT. Nothing is renamed
    (2026-10-23)."""
    studies = {key: prepare_study(name, key, runs[key], exported_at=exported_at) for key in STUDIES}
    top = studies[TOP_STUDY]
    run, iv, credit = top.run, top.reads[INTERVIEW], top.manifest
    entry = run.record.get("entry") or {}
    shas = {"cloud": credit["cloud"], "web": credit["web"]}
    row = {"slug": name.slug, "name": name.name, **{k: credit[k] for k in ATTRIBUTION if k in credit and
                                                     k != "assumptions"},
           "oneLine": one_line(run.founder.get("project_name") or entry.get("title")),
           "problem": one_sentence(run.founder.get("problem_seed")),
           "assumptions": credit["assumptions"],
           **{k: top.figures[k] for k in ("decision", "howSure", "pilot", "price")}, "b2b": run.b2b,
           # spec 071 FR-5: which study the row's own fields are -- since spec 106 the problem study's (PROBLEM)
           "scope": run.scope, **shas,
           "axes": axes(run, name.axes),
           "cluster": {k: (name.cluster or {}).get(k) for k in ("id", "label")},
           "keywords": keywords(run, name, occasion=(iv["links"][0] if iv["links"] else {}).get("occasion")),
           "interview": {"links": [{"role": l["role"], "label": l["label"], "items": item_count(l)}
                                   for l in iv["links"]]},
           # spec 106 FR-1: the three studies, each its own decision, how sure, pilot, price and people
           "studies": {key: dict(s.figures) for key, s in studies.items()}}
    provenance = {"slug": name.slug, "entry": run.entry, "cycle": cycle,
                  "studies": {key: {"scope": s.run.scope, "run": s.run.dir.name, "cloud": s.manifest["cloud"],
                                    "web": s.manifest["web"]} for key, s in studies.items()},
                  "renamed": {"from": list(name.replaces), "to": name.name}}
    return Slug(name=name, studies=studies, row=row, provenance=provenance)


def index_file(examples: list[dict], generated_at: str) -> dict:
    """`index.json` as written since spec 063's a35af52: `{generatedAt, count, examples}`."""
    return {"generatedAt": generated_at, "count": len(examples), "examples": examples}


def _attribution_block(where: str, block: dict, s: Slug) -> list[str]:
    why = []
    inspired = block.get("inspiredBy") or {}
    if not all(isinstance(inspired.get(k), str) and inspired[k].strip() for k in ("name", "batch", "ycUrl")):
        why.append(f"{where}: inspiredBy needs name, batch and ycUrl ({inspired})")
    elif not inspired["ycUrl"].startswith(_YC):
        why.append(f"{where}: inspiredBy.ycUrl {inspired['ycUrl']!r} is not a YC company page")
    elif inspired["name"] != s.name.name:
        why.append(f"{where}: inspiredBy.name {inspired['name']!r} is not the example's name {s.name.name!r}")
    for key in ("publicDescription", "statusToday"):
        if key == "statusToday" and key not in block:
            continue                                 # optional: only where today's words differ
        described = block.get(key) or {}
        if not all(isinstance(described.get(k), str) and described[k].strip() for k in ("text", "url", "date")):
            why.append(f"{where}: {key} needs text, url and date ({described})")
        elif not described["url"].startswith("https://") or not _DATE.match(described["date"]):
            why.append(f"{where}: {key} url {described['url']!r} / date {described['date']!r}")
    if block.get("simulated") is not True:
        why.append(f"{where}: simulated is not true")
    if not block.get("assumptions"):
        why.append(f"{where}: no assumptions")
    return why


def attribution_reasons(s: Slug) -> list[str]:
    """The attribution check (replaces FR-2's survivors grep): `inspiredBy` (name, batch, a YC company page),
    `publicDescription` (text, an https URL, an ISO date; the launch-era words), `statusToday` when present (the same
    shape), `simulated`, at least one assumption -- each present in the index row and in every study's manifest, the
    row attributing it as the problem study's manifest does and the example's own attribution alike in all three; and
    (spec 106 FR-2) the disclaimer the sentence filled with this name, batch and **the study's own people** -- the
    row's the problem study's -- every study having invited someone."""
    why = _attribution_block("index", s.row, s)
    for key, study in s.studies.items():
        why += _attribution_block(f"{key}/manifest", study.manifest, s)
        invited, answered_n = study.figures["invited"], study.figures["answered"]
        if invited < 1:
            why.append(f"the {key} study invited nobody")
        elif not (0 <= answered_n <= invited):
            why.append(f"the {key} study says {answered_n} answered of {invited} invited")
        elif study.manifest.get("disclaimer") != s.name.disclaimer(invited, answered_n):
            why.append(f"{key}/manifest: the disclaimer is missing or not the sentence for the {key} study's people "
                       f"({people_words(invited, answered_n)})")
    top = s.top.figures
    if not s.row.get("disclaimer") or s.row.get("disclaimer") != s.name.disclaimer(top["invited"], top["answered"]):
        why.append(f"index: the disclaimer is missing or not the sentence for the {TOP_STUDY} study's people")
    if {k: s.row.get(k) for k in ATTRIBUTION} != {k: s.top.manifest.get(k) for k in ATTRIBUTION}:
        why.append(f"the index row and the {TOP_STUDY} study's manifest attribute it differently")
    if any({k: st.manifest.get(k) for k in SHARED_ATTRIBUTION} != {k: s.top.manifest.get(k) for k in SHARED_ATTRIBUTION}
           for st in s.studies.values()):
        why.append("the three studies' manifests attribute the example differently")
    studies = s.row.get("studies") or {}
    if list(studies) != list(STUDIES) or any(list(v) != list(STUDY_FIGURES) for v in studies.values()):
        why.append(f"index: studies must be {list(STUDIES)}, each {list(STUDY_FIGURES)} ({studies})")
    cluster = s.row.get("cluster") or {}
    if not (isinstance(cluster.get("id"), int) and isinstance(cluster.get("label"), str) and cluster["label"].strip()):
        why.append(f"index: cluster needs an integer id and a label ({cluster})")
    words = s.row.get("keywords") or []
    if not (KEYWORDS_MIN <= len(words) <= KEYWORDS_MAX):
        why.append(f"index: {len(words)} keywords, not {KEYWORDS_MIN} to {KEYWORDS_MAX}")
    elif any(not isinstance(w, str) or w != w.lower() or not w.strip() for w in words):
        why.append(f"index: keywords are not plain lower-case words ({words})")
    elif any(s.name.name.lower() in w for w in words):
        why.append(f"index: a keyword names the company ({words})")
    if s.row.get("scope") not in bt.SCOPES:
        why.append(f"index: scope {s.row.get('scope')!r} is not one of {', '.join(bt.SCOPES)}")
    return [f"{s.name.slug}: {w}" for w in why]


def _written(s: Slug) -> str:
    """Every byte the slug would put under OUT: its studies' reads and manifests and its index row."""
    return ("".join(se._dumps(v) for st in s.studies.values() for v in st.reads.values())
            + "".join(se._dumps(st.manifest) for st in s.studies.values()) + se._dumps(s.row))


def check(slugs: list[Slug]) -> list[str]:
    """Every refusal reason over the whole output as it would be written: the attribution check, 060's grep (an
    email, the back-test founder, a link), an id in any study's interview.json, and any provenance (an entry id, a run
    name, a source path) in what is about to go under OUT."""
    reasons = []
    needles = provenance_needles(slugs)
    for s in slugs:
        reasons += attribution_reasons(s)
        written = _written(s)
        held = se.survivors(written, founder_name=bt.IDENTITY_NAME, founder_email=bt.IDENTITY_EMAIL)
        if held:
            reasons.append(f"{s.name.slug}: {held} survive the withholding")
        for key, study in s.studies.items():
            ids = sorted({k for k in _keys(study.reads[INTERVIEW]) if k in _DROPPED})
            if ids:
                reasons.append(f"{s.name.slug}: {key}/interview.json carries {ids}")
        found = sorted(n for n in needles if n.lower() in written.lower())
        if found:
            reasons.append(f"{s.name.slug}: provenance in the public files: {found}")
    return reasons


def provenance_needles(slugs: list[Slug]) -> list[str]:
    """What must never be written under OUT: each study's entry id and run directory name, and the run-file words."""
    return sorted({x for s in slugs for st in s.studies.values() for x in (st.run.entry, st.run.dir.name)}
                  | {"-backtest-", "/Users/"})


def provenance_under(out_dir: Path, needles: Iterable[str], *, skip: Iterable[Path] = ()) -> list[str]:
    """Every byte of every file under `out_dir` (but `skip`), any case, no exclusions: the hits as `<path>: [...]`.
    Empty is the pass."""
    out_dir = Path(out_dir)
    skip = [Path(p).resolve() for p in skip]
    needles = [n.lower() for n in needles]
    hits = []
    if not out_dir.is_dir():
        return hits
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file()):
        resolved = path.resolve()
        if any(resolved == s or s in resolved.parents for s in skip):
            continue
        text = path.read_bytes().decode("utf-8", errors="replace").lower()
        found = sorted(n for n in needles if n in text)
        if found:
            hits.append(f"{path.relative_to(out_dir)}: {found}")
    return hits


def _keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from _keys(v)
    elif isinstance(value, list):
        for v in value:
            yield from _keys(v)


def kept_rows(out_dir: Path) -> dict[str, dict]:
    """What keel-web wrote by hand on the snapshot's index rows (`KEPT_KEYS`), by slug -- kept across the refresh, as
    the slug's cover is. An index that is not there, or not JSON, keeps nothing."""
    path = Path(out_dir) / INDEX
    try:
        raw = _json(path) if path.is_file() else {}
    except (OSError, ValueError):
        return {}
    rows = raw if isinstance(raw, list) else (raw or {}).get("examples") or []
    return {r["slug"]: {k: copy.deepcopy(r[k]) for k in KEPT_KEYS if k in r}
            for r in rows if isinstance(r, dict) and isinstance(r.get("slug"), str)}


def _grouped(runs: list[Run], by_entry: dict[str, GalleryName]) -> tuple[dict[str, dict[str, Run]], list[str]]:
    """The runs by entry and study, strictly: every reason the set is not three studies per known entry, each once."""
    groups: dict[str, dict[str, Run]] = {}
    reasons = []
    for r in runs:
        if r.study is None:
            reasons.append(_not_a_study(r.dir.name, r.scope))
        elif r.entry not in by_entry:
            reasons.append(f"{r.dir.name}: entry {r.entry!r} is not in {NAMES_FILE.name}")
        elif r.study in groups.get(r.entry, {}):
            reasons.append(f"{r.entry}: the {r.study} study given twice ({groups[r.entry][r.study].dir.name}, "
                           f"{r.dir.name})")
        else:
            groups.setdefault(r.entry, {})[r.study] = r
    reasons += [_lacks(entry, studies) for entry, studies in groups.items() if set(studies) != set(STUDIES)]
    return groups, reasons


def export(run_dirs: list[Path], out_dir: Path, *, names: list[GalleryName] | None = None,
           exported_at: str | None = None, provenance_dir: Path = PROVENANCE_DIR,
           accepted: dict | None = None) -> dict:
    """FR-1 to FR-3a, three studies per entry (spec 106 FR-1): read every run, group them by entry and study (an entry
    lacking one, or given one twice, or a run of another scope refuses the export -- `three_studies` sets such entries
    aside first), prepare every slug, check the whole output and whatever else already sits under `out_dir`, and only
    then write `<out_dir>/<slug>/<study>/...` (each slug's directory replaced whole, its `cover.jpg` kept) and
    `<out_dir>/index.json` (keel-web's `title`, `image` and `tests` kept on a refreshed row), then grep every byte under
    `out_dir` once more. The slug -> entry / study / run link and `accepted` (FR-3: the cycle and the score_pct the
    gallery was promoted on, when gated) go to `<provenance_dir>/provenance-<exportedAt>.json`, never under `out_dir`.
    Returns `{index, slugs: {slug: {study: manifest + written}}, dir, provenance, accepted}`."""
    names = load_names() if names is None else names
    by_entry = {n.entry: n for n in names}
    exported_at = exported_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out_dir, provenance_dir = Path(out_dir), Path(provenance_dir)
    if provenance_dir.resolve() == out_dir.resolve() or out_dir.resolve() in provenance_dir.resolve().parents:
        raise GalleryRefused([f"the provenance directory {provenance_dir} is under OUT {out_dir}"])
    runs, reasons = [], []
    for d in run_dirs:
        try:
            runs.append(read_run(d))
        except GalleryRefused as refusal:
            reasons.extend(refusal.reasons)
    groups, grouping = _grouped(runs, by_entry)
    reasons += grouping
    if not runs and not reasons:
        reasons.append("no run given: nothing to build")
    if reasons:
        raise GalleryRefused(reasons)
    cycle = (accepted or {}).get("cycle")
    slugs = [prepare(by_entry[entry], studies, exported_at=exported_at, cycle=cycle)
             for entry, studies in groups.items()]
    kept = kept_rows(out_dir)
    for s in slugs:
        s.row.update(kept.get(s.name.slug) or {})
    reasons = check(slugs)
    needles = provenance_needles(slugs)
    replaced = [out_dir / s.name.slug for s in slugs] + [out_dir / INDEX]
    reasons += [f"already under OUT: {hit}" for hit in provenance_under(out_dir, needles, skip=replaced)]
    if reasons:
        raise GalleryRefused(reasons)
    manifests = {}
    for s in slugs:
        target = out_dir / s.name.slug
        keep = {f: (target / f).read_bytes() for f in KEPT_FILES if (target / f).is_file()}
        if target.is_dir():
            shutil.rmtree(target)                    # the slug is the export's own: nothing stale survives ...
        target.mkdir(parents=True)
        for f, data in keep.items():                 # ... but what keel-web put beside it (the cover, keel-web 103)
            (target / f).write_bytes(data)
        manifests[s.name.slug] = {}
        for key, study in s.studies.items():
            written = se.write(target / key, study.reads, entry_id="", corpus_revision=0, cloud=None,
                               exported_at=exported_at)
            (target / key / se.MANIFEST).write_text(se._dumps(study.manifest), encoding="utf-8")  # replaces 060's own
            manifests[s.name.slug][key] = {**study.manifest, "written": written["files"]}
    index = gallery_order([s.row for s in slugs])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / INDEX).write_text(se._dumps(index_file(index, exported_at)), encoding="utf-8")
    left = provenance_under(out_dir, needles)
    if left:                                         # unreachable after `check`; the last word is the bytes on disk
        raise GalleryRefused([f"written under OUT and carrying provenance: {hit}" for hit in left])
    provenance_dir.mkdir(parents=True, exist_ok=True)
    provenance = provenance_dir / f"provenance-{exported_at}.json"
    by_slug = {s.name.slug: s.provenance for s in slugs}
    provenance.write_text(se._dumps({"exportedAt": exported_at, "accepted": accepted,
                                     "examples": [by_slug[r["slug"]] for r in index]}), encoding="utf-8")
    return {"index": index, "slugs": manifests, "dir": str(out_dir), "provenance": str(provenance),
            "accepted": accepted}


# ----------------------------------------------------- spec 079 FR-6 / spec 106 FR-3: the readers' gate

#: Spec 106 FR-3 (spec 079 FR-6 amended): with `--scores`, a study is an example only when the readers passed it, and
#: the gallery is promoted only when the cycle scores at or above the gallery's own last accepted score.
SCORE_GATE = ("a bundle with no score file at the current rubric version, or whose latest has a flagged screen, is "
              "refused by name; the cycle's overall score_pct below the gallery's last accepted one (its provenance) "
              "refuses the export; equal or above passes, whatever the bar")


def latest_score_file(run_dir: Path, scores_dir: Path) -> tuple[dict | None, list[str]]:
    """The latest score file (spec 078 FR-4) of this very bundle at the current `RUBRIC_VERSION` under
    `<scores_dir>/<entry>/`, matched by the file's `bundle` header to the run's name; partial files never count. Returns
    `(file, the names of files set aside at another rubric version)`."""
    from quality import rubric                                       # noqa: PLC0415 - the gate is opt-in

    run_dir = Path(run_dir)
    record = _record_of(run_dir)
    entry = (record.get("entry") or {}).get("id") or ""
    names = {run_dir.name, str(record.get("run") or run_dir.name)}
    found, aside = [], []
    for path in sorted((Path(scores_dir) / entry).glob("*.json")) if entry else []:
        try:
            obj = rubric.load_file(path)
        except (rubric.RubricError, ValueError, OSError):
            continue
        if obj.get("partial") or str(obj.get("bundle")) not in names:
            continue
        if obj["rubric_version"] != rubric.RUBRIC_VERSION:
            aside.append(path.name)
            continue
        obj["_path"] = str(path)
        found.append(obj)
    found.sort(key=lambda f: (f.get("scored_at") or "", Path(f["_path"]).name))
    return (found[-1] if found else None), aside


def score_gate(run_dirs: list[Path], scores_dir: Path, *, bar_pct: float | None = None,
               refuse_flagged: bool = True) -> tuple[list[Path], list[str]]:
    """Spec 079 FR-6 as spec 106 FR-3 leaves it: `(the runs the readers passed, one reason per refused run, naming
    it)`. A run is refused when it has no score file at the current rubric version or when that file's latest has a
    flagged screen (a screen the reader marked out of place or leaking is never published); with `bar_pct` (`--bar`,
    off by default) also when its overall score_pct is under it."""
    from quality import rubric                                       # noqa: PLC0415

    passing, refused = [], []
    for run_dir in run_dirs:
        run_dir = Path(run_dir)
        record = _record_of(run_dir)
        study = f"{(record.get('entry') or {}).get('id') or '?'} · {record.get('scope') or 'ALL'}"
        latest, aside = latest_score_file(run_dir, scores_dir)
        if latest is None:
            extra = f" (set aside at another rubric version: {', '.join(aside)})" if aside else ""
            refused.append(f"{run_dir.name} ({study}): no score file at rubric version {rubric.RUBRIC_VERSION} under "
                           f"{scores_dir}{extra} -- a bundle the readers have not passed is not an example")
            continue
        overall = (latest.get("summary") or {}).get("overall") or {}
        flagged, pct = int(overall.get("flagged") or 0), overall.get("score_pct")
        why = []
        if refuse_flagged and flagged:
            why.append(f"{flagged} flagged screen(s)")
        if bar_pct is not None and (pct is None or pct < float(bar_pct)):
            why.append(f"score_pct {pct}% under the bar of {float(bar_pct):.0f}%")
        if why:
            refused.append(f"{run_dir.name} ({study}): {Path(latest['_path']).name} has {' and '.join(why)}")
        else:
            passing.append(run_dir)
    return passing, refused


def cycle_score(run_dirs: list[Path], scores_dir: Path) -> float | None:
    """Spec 106 FR-3: the overall score_pct of the runs read as one cycle -- the latest score file of each study at the
    current rubric version, read together as the cycle record's head reads them (`quality.table.head`); None with
    none."""
    from quality import table                                        # noqa: PLC0415

    files = [f for f in (latest_score_file(d, scores_dir)[0] for d in run_dirs) if f]
    return table.head(table.latest_per_entry(files))["score_pct"] if files else None


def last_accepted(provenance_dir: Path = PROVENANCE_DIR) -> dict | None:
    """Spec 106 FR-3: the gallery's own last score -- the newest provenance file that records one (`accepted`: the
    cycle, its score_pct, the rubric version), with the file's name; None when no gated export was ever recorded (an
    export without `--scores`, and every provenance file before spec 106, records none)."""
    for path in sorted(Path(provenance_dir).glob(PROVENANCE_GLOB), reverse=True):
        try:
            data = _json(path)
        except (OSError, ValueError):
            continue
        got = data.get("accepted") if isinstance(data, dict) else None
        if isinstance(got, dict) and isinstance(got.get("score_pct"), (int, float)):
            return {**got, "file": path.name}
    return None


def gate(score_pct: float | None, last: dict | None) -> tuple[str | None, str]:
    """Spec 106 FR-3 (the founder, 2026-10-30): `(refusal, what was compared)` -- a refusal only when the cycle's
    score_pct is below the gallery's last accepted one at the same rubric version; equal or above passes, whatever the
    90% bar says; no accepted score yet passes (the first acceptance), and so does one at another rubric version (two
    rubric versions are never compared, spec 078 FR-1)."""
    from quality import rubric                                       # noqa: PLC0415

    if last is None:
        return None, f"no accepted score yet: the first acceptance passes (score_pct {score_pct}%)"
    then = f"{last['score_pct']}% (cycle {last.get('cycle') or 'not named'}, {last['file']})"
    if last.get("rubric_version") != rubric.RUBRIC_VERSION:
        return None, (f"the last accepted score {then} is at rubric version {last.get('rubric_version')}, the scores at "
                      f"{rubric.RUBRIC_VERSION}: never compared -- the first acceptance at this version passes")
    if score_pct is None:
        return (f"the cycle has no score_pct to hold to the gallery's last accepted {then} (no score file at rubric "
                f"version {rubric.RUBRIC_VERSION}) -- not promoted; nothing is written"), then
    if score_pct < last["score_pct"]:
        return (f"the cycle's score_pct {score_pct}% is below the gallery's last accepted {then} -- not promoted "
                "(spec 106 FR-3: the gate is the gallery's own last score); nothing is written"), then
    return None, f"score_pct {score_pct}% against the last accepted {then}: at or above, promoted"


def promote(run_dirs: list[Path], out_dir: Path, *, names: list[GalleryName] | None = None,
            scores_dir: Path | None = None, bar_pct: float | None = None, cycle: str | None = None,
            score_pct: float | None = None, provenance_dir: Path = PROVENANCE_DIR, exported_at: str | None = None,
            say=print) -> dict:
    """`make gallery` and `make quality-accept`'s one path (spec 106): behind the readers' gate when `scores_dir` is
    given (every study refused named through `say`; the cycle's score_pct -- `score_pct`, else `cycle_score` of the
    runs -- held to the gallery's last accepted one, a refusal of the whole), then three studies per entry (an entry
    set aside named through `say`), then `export`, the score recorded as `accepted` in the provenance. Raises
    `NothingToBuild` when every study or entry was set aside, `GalleryRefused` on any other refusal; nothing is
    written then."""
    names = load_names() if names is None else names
    run_dirs = [Path(d) for d in run_dirs]
    if not run_dirs:
        raise NothingToBuild(["no run to build from: nothing to build"])
    accepted = None
    if scores_dir is not None:
        from quality import rubric                                   # noqa: PLC0415

        scored = cycle_score(run_dirs, scores_dir) if score_pct is None else score_pct
        passing, refused = score_gate(run_dirs, Path(scores_dir), bar_pct=bar_pct)
        for reason in refused:
            say(f"refused {reason}")
        refusal, compared = gate(scored, last_accepted(provenance_dir))
        if refusal:
            raise GalleryRefused([refusal])
        say(f"the gate: {compared}")
        if not passing:
            raise NothingToBuild(["every run was refused by the readers' gate (--scores): nothing to build"])
        run_dirs = passing
        accepted = {"cycle": cycle, "score_pct": scored, "rubric_version": rubric.RUBRIC_VERSION}
    complete, set_aside = three_studies(run_dirs)
    for reason in set_aside:
        say(f"refused {reason}")
    if not complete:
        raise NothingToBuild(["no entry has its three studies (problem, solution, money): nothing to build"])
    return export(complete, out_dir, names=names, exported_at=exported_at, provenance_dir=provenance_dir,
                  accepted=accepted)


# ------------------------------------------------------------------------------------------------ make gallery

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="make gallery", description="Spec 063 / 106: the example gallery export.")
    p.add_argument("--out", required=True, help="where the slugs and index.json go (keel-web's public/sample/)")
    p.add_argument("--runs", default="", help="back-test run directories, comma-separated, three studies an entry "
                                              "(default: the newest of each study per entry)")
    p.add_argument("--runs-dir", default=str(RUNS_DIR), help="where the default (and bare-named) runs are found")
    p.add_argument("--provenance-dir", default=str(PROVENANCE_DIR),
                   help="where provenance-<exportedAt>.json goes (never under --out)")
    p.add_argument("--scores", default="", help="spec 079 FR-6 / 106 FR-3: quality/scores -- " + SCORE_GATE)
    p.add_argument("--bar", type=float, default=None, help="with --scores: an optional stricter gate -- a study whose "
                                                           "score_pct is under it is refused (off by default)")
    p.add_argument("--cycle", default="", help="with --scores: the cycle record's name, recorded in the provenance")
    a = p.parse_args(argv)
    try:
        names = load_names()
        if a.runs.strip():
            run_dirs = resolve_runs(a.runs, Path(a.runs_dir))
        else:
            run_dirs, missing = newest_runs(names, Path(a.runs_dir))
            for reason in missing:
                print(f"gallery: refused {reason}")
        result = promote(run_dirs, Path(a.out), names=names, scores_dir=Path(a.scores) if a.scores else None,
                         bar_pct=a.bar, cycle=a.cycle or None, provenance_dir=Path(a.provenance_dir),
                         say=lambda line: print(f"gallery: {line}"))
    except GalleryRefused as refusal:
        print(str(refusal), file=sys.stderr)
        return 1
    for row in result["index"]:
        files = sum(len(m["written"]) for m in result["slugs"][row["slug"]].values())
        decisions = " · ".join(f"{k} {v['decision']}" for k, v in row["studies"].items())
        print(f"gallery: {row['slug']:<13} {row['name']:<13} {'B2B' if row['b2b'] else 'B2C'}  {decisions}  "
              f"{files} files  (cloud {row['cloud']}, web {row['web']})")
    print(f"gallery: {len(result['index'])} slugs of three studies each and {INDEX} under {result['dir']}; attributed, "
          "simulated, no provenance; nothing committed anywhere")
    print(f"gallery: which run made which study -> {result['provenance']} (outside OUT, not committed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
