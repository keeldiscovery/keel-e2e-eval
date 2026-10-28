"""Spec 063: the example gallery export -- the six back-test ideas' briefs into the sample snapshot, each a simulated
study inspired by a named company (amendment of record, 2026-10-23).

`make gallery RUNS=<dir>[,<dir>...] OUT=<dir>` (FR-1) reads finished `make backtest` run directories (spec 062) and
writes, for each, the 060 file set under `<OUT>/<slug>/` plus `<slug>/interview.json` (FR-3a) and `<slug>/manifest.json`
(FR-3), then one `<OUT>/index.json`. No stack, no model, no paid run: everything is read from the run directory.

What a run directory gives, and what is read from where (tasks.md, judgement calls 1-3):

- `export/` -- spec 062 FR-3's ungated 060/061 snapshot of the founder's reads (names kept, emails, the founder and
  tokens withheld), its `manifest.json` listing every file. That IS the 060 file set; it is read back, withheld again
  (a no-op on a good run, a guard on a bad one).
- `backtest.json` -- the entry (`id`, `b2b`, `idea_name`), the stack's SHAs (`stack`), and per link
  `respondents[link].served` (the interview the stranger's page fetched, spec 062 FR-4.2) and `.drawn` (what the
  page drew for the run's one watched person: the kickers, the gate's chip labels, the follow-up screen).
- `transcript.jsonl` -- the follow-up stems the run's people were asked (`<person>: the one follow-up -- owed on ...`,
  the route's 200 `text`).
- `inputs.json` -- what the founder entered (`founder`: the project name, the four context fields, the window, the
  problem statement, the decider, the calibration answers), for `oneLine`, `problem` and the seven `axes`.

The back-test entries themselves are NOT loaded through `instructions.corpus.load`: they are corpus revision 13 in
keel-cloud now, and this eval's loader reads revision 12 until spec 064 (judgement call 1).

Attribution (the amendment of record, 2026-10-23, over FR-2 and FR-3): the real company name is the example's
attribution, everywhere, so nothing is renamed. Each index row and `<slug>/manifest.json` carry `inspiredBy {name,
batch, ycUrl}`, `publicDescription {text, url, date}` -- the launch-era words for the studied idea -- and, where today's
one-liner differs, `statusToday {text, url, date}` (from `instructions/gallery_names.toml`), `assumptions[]` (the
founder's belief sentences the run tested, as the standings served them), `simulated: true` and the fixed
`disclaimer`. The attribution check refuses a slug missing any of them, or whose disclaimer is not the fixed sentence.

**Spec 071 FR-5** (keel-cloud 133, design §9: *each example carries its configuration*): every index row carries
`scope`, the run's own (`backtest.json`'s, spec 071 FR-4), ALL for every run recorded before a back-test could be walked
under one -- the fourteen; the attribution check accepts the five contract-38 values and refuses anything else.

**Spec 079 FR-6** (the quality cycle's acceptance; the design's §8, *the homepage examples follow the baseline*):
`--scores quality/scores` puts the readers' gate in front of the export -- a run is an example only when its latest
score file (spec 078, matched by the file's `bundle` header, at the current `RUBRIC_VERSION`) has no flagged screen and
a score_pct at or over the bar; a run refused is named with its reason and the gallery is built from the rest.
`--scope-order` keeps one run per entry (a cycle walks three studies of each). Without `--scores` nothing changes.

Provenance stays private (FR-3, amended 2026-10-22): no entry id, run name or source path is written under OUT -- the
check greps every byte under OUT for them -- and the slug -> entry / run link goes once to
`runs/gallery/provenance-<exportedAt>.json` (`[{slug, entry, run, cloud, web, renamed: {from, to}}]`), outside OUT.
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

#: The amendment of record's attribution, alike in every index row and its slug's manifest.
ATTRIBUTION = ("inspiredBy", "publicDescription", "statusToday", "simulated", "disclaimer", "assumptions")

#: FR-1's seven gallery words, in the spec's order.
AXES = ("whoHasIt", "whoPays", "rhythm", "costMode", "priceShape", "firstStep", "kind")

#: FR-3 (amended 2026-10-22): the slug -> entry / run link is written here, once an export, and never under OUT
#: (`runs/` is ignored by git, as every run file is).
PROVENANCE_DIR = RUNS_DIR / "gallery"

#: Keys never written into interview.json (FR-3a: tokens and ids withheld; the AI interviewer's forms are a later spec).
_DROPPED = frozenset({"itemId", "optionId", "id", "token", "costItemId", "advantagesWhen", "spoken", "clip", "clips"})

_RHYTHM = {"NIGHTS": "nightly", "DAYS": "daily", "WORKING_DAYS": "every working day", "WEEKS": "weekly",
           "MONTHS": "monthly"}
_PERIODLY = {"day": "daily", "week": "weekly", "month": "monthly", "quarter": "quarterly", "year": "yearly"}
_SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_YC = "https://www.ycombinator.com/companies/"

#: The amendment of record's fixed sentence, `name` and `batch` filled from `inspiredBy`.
DISCLAIMER = ("A simulated study inspired by {name} (Y Combinator {batch}). The founder's answers, the twenty "
              "participants and everything they said are fictional, written from {name}'s public material to show "
              "what Keel does. Not customer research about {name}; not affiliated with {name} or Y Combinator.")
#: The disclaimer says "the twenty participants": a run with another number is refused rather than mis-described.
PARTICIPANTS = 20


class GalleryRefused(AssertionError):
    """The export refuses, its reasons named. Nothing was written."""

    def __init__(self, reasons: list[str]):
        self.reasons = list(reasons)
        super().__init__("the gallery export refuses: " + "; ".join(self.reasons))


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

    def disclaimer(self) -> str | None:
        name, batch = (self.inspired_by or {}).get("name"), (self.inspired_by or {}).get("batch")
        return DISCLAIMER.format(name=name, batch=batch) if name and batch else None


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


def newest_runs(names: list[GalleryName], runs_dir: Path = RUNS_DIR) -> list[Path]:
    """FR-1's default: for each entry of the map, the newest `*-backtest-<entry>` directory that finished with an
    export (the stamp prefix sorts by time). Refuses an entry with none."""
    runs_dir = Path(runs_dir)
    out, problems = [], []
    for n in names:
        found = sorted(p for p in runs_dir.glob(f"*-backtest-{n.entry}") if p.is_dir()
                       and (p / bt.EXPORT_DIR / se.MANIFEST).is_file() and (p / bt.RECORD).is_file()
                       and _json(p / bt.RECORD).get("passed"))
        if found:
            out.append(found[-1])
        else:
            problems.append(f"no finished back-test run of {n.entry} under {runs_dir}")
    if problems:
        raise GalleryRefused(problems)
    return out


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
            "advantages": _labels(served.get("advantages")),
            "escape": _escape(served.get("escape")),
            "shown": list(drawn.get("rows") or [])}
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
class Slug:
    name: GalleryName
    run: Run
    reads: dict[str, Any]              # withheld, interview included -- what is written
    manifest: dict                     # cloud, web, exportedAt and the attribution
    row: dict                          # the index row
    provenance: dict                   # the slug's row of runs/gallery/provenance-<exportedAt>.json, never under OUT


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
    """The people the run invited (the founder's invitation register)."""
    return len(se.invitation_ids(reads.get("invitations")))


def attribution(name: GalleryName, reads: dict[str, Any]) -> dict:
    """The amendment of record's fields, in the order written: `statusToday` only where the map has one (the company's
    current one-liner, where it differs from the launch-era `publicDescription`)."""
    out = {"inspiredBy": {k: (name.inspired_by or {}).get(k) for k in ("name", "batch", "ycUrl")},
           "publicDescription": {k: (name.public_description or {}).get(k) for k in ("text", "url", "date")}}
    if name.status_today:
        out["statusToday"] = {k: name.status_today.get(k) for k in ("text", "url", "date")}
    return {**out,
            "simulated": True,
            "disclaimer": name.disclaimer(),
            "assumptions": assumptions(reads)}


def prepare(name: GalleryName, run: Run, *, exported_at: str) -> Slug:
    """One slug in memory: withhold again (060), the interview (FR-3a), the attribution (the amendment of record), the
    index row (FR-1), and the provenance row that is never written under OUT. Nothing is renamed (2026-10-23)."""
    reads = se.withhold(run.reads, founder_name=bt.IDENTITY_NAME, founder_email=bt.IDENTITY_EMAIL).reads
    iv = interview(run)
    reads[INTERVIEW] = iv
    figures = se.card(reads)
    stack = run.record.get("stack") or {}
    entry = run.record.get("entry") or {}
    shas = {"cloud": stack.get("keel-cloud"), "web": stack.get("keel-web")}
    credit = attribution(name, reads)
    row = {"slug": name.slug, "name": name.name, **{k: v for k, v in credit.items() if k != "assumptions"},
           "oneLine": one_line(run.founder.get("project_name") or entry.get("title")),
           "problem": one_sentence(run.founder.get("problem_seed")),
           "assumptions": credit["assumptions"],
           "decision": figures["decision"], "howSure": figures["howSure"],
           "pilot": figures["pilot"], "price": figures["price"], "b2b": run.b2b,
           # spec 071 FR-5 (keel-cloud 133, design §5 / §9): which study the example is -- the run's own scope, ALL
           # (the whole study) for every run recorded before a back-test could be walked under one
           "scope": run.record.get("scope") or bt.DEFAULT_SCOPE, **shas,
           "axes": axes(run, name.axes),
           "cluster": {k: (name.cluster or {}).get(k) for k in ("id", "label")},
           "keywords": keywords(run, name, occasion=(iv["links"][0] if iv["links"] else {}).get("occasion")),
           "interview": {"links": [{"role": l["role"], "label": l["label"], "items": item_count(l)}
                                   for l in iv["links"]]}}
    provenance = {"slug": name.slug, "entry": run.entry, "run": run.dir.name, **shas,
                  "renamed": {"from": list(name.replaces), "to": name.name}}
    return Slug(name=name, run=run, reads=reads, manifest={**shas, "exportedAt": exported_at, **credit}, row=row,
                provenance=provenance)


def index_file(examples: list[dict], generated_at: str) -> dict:
    """`index.json` as written since spec 063's a35af52: `{generatedAt, count, examples}`."""
    return {"generatedAt": generated_at, "count": len(examples), "examples": examples}


def attribution_reasons(s: Slug) -> list[str]:
    """The attribution check (replaces FR-2's survivors grep): `inspiredBy` (name, batch, a YC company page),
    `publicDescription` (text, an https URL, an ISO date; the launch-era words), `statusToday` when present (the same
    shape), `simulated`, the fixed disclaimer filled with this name
    and batch, at least one assumption -- each present, alike in the index row and the manifest; and the run's
    people the twenty the disclaimer says."""
    why = []
    for where, block in (("index", s.row), ("manifest", s.manifest)):
        inspired = block.get("inspiredBy") or {}
        if not all(isinstance(inspired.get(k), str) and inspired[k].strip() for k in ("name", "batch", "ycUrl")):
            why.append(f"{where}: inspiredBy needs name, batch and ycUrl ({inspired})")
        elif not inspired["ycUrl"].startswith(_YC):
            why.append(f"{where}: inspiredBy.ycUrl {inspired['ycUrl']!r} is not a YC company page")
        elif inspired["name"] != s.name.name:
            why.append(f"{where}: inspiredBy.name {inspired['name']!r} is not the example's name {s.name.name!r}")
        for key in ("publicDescription", "statusToday"):
            if key == "statusToday" and key not in block:
                continue                             # optional: only where today's words differ
            described = block.get(key) or {}
            if not all(isinstance(described.get(k), str) and described[k].strip() for k in ("text", "url", "date")):
                why.append(f"{where}: {key} needs text, url and date ({described})")
            elif not described["url"].startswith("https://") or not _DATE.match(described["date"]):
                why.append(f"{where}: {key} url {described['url']!r} / date {described['date']!r}")
        if block.get("simulated") is not True:
            why.append(f"{where}: simulated is not true")
        if not block.get("disclaimer") or block.get("disclaimer") != s.name.disclaimer():
            why.append(f"{where}: the disclaimer is missing or not the fixed sentence")
        if not block.get("assumptions"):
            why.append(f"{where}: no assumptions")
    if {k: s.row.get(k) for k in ATTRIBUTION} != {k: s.manifest.get(k) for k in ATTRIBUTION}:
        why.append("the index row and the manifest attribute it differently")
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
    people = participants(s.reads)
    if people != PARTICIPANTS:
        why.append(f"the run invited {people} people; the disclaimer says twenty")
    return [f"{s.name.slug}: {w}" for w in why]


def check(slugs: list[Slug]) -> list[str]:
    """Every refusal reason over the whole output as it would be written: the attribution check, 060's grep (an
    email, the back-test founder, a link), an id in interview.json, and any provenance (an entry id, a run name, a
    source path) in what is about to go under OUT."""
    reasons = []
    needles = provenance_needles(slugs)
    for s in slugs:
        reasons += attribution_reasons(s)
        written = "".join(se._dumps(v) for v in s.reads.values()) + se._dumps(s.manifest) + se._dumps(s.row)
        held = se.survivors(written, founder_name=bt.IDENTITY_NAME, founder_email=bt.IDENTITY_EMAIL)
        if held:
            reasons.append(f"{s.name.slug}: {held} survive the withholding")
        ids = sorted({k for k in _keys(s.reads[INTERVIEW]) if k in _DROPPED})
        if ids:
            reasons.append(f"{s.name.slug}: interview.json carries {ids}")
        found = sorted(n for n in needles if n.lower() in written.lower())
        if found:
            reasons.append(f"{s.name.slug}: provenance in the public files: {found}")
    return reasons


def provenance_needles(slugs: list[Slug]) -> list[str]:
    """What must never be written under OUT: each run's entry id and directory name, and the run-file words."""
    return sorted({x for s in slugs for x in (s.run.entry, s.run.dir.name)} | {"-backtest-", "/Users/"})


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


def export(run_dirs: list[Path], out_dir: Path, *, names: list[GalleryName] | None = None,
           exported_at: str | None = None, provenance_dir: Path = PROVENANCE_DIR) -> dict:
    """FR-1 to FR-3a: read every run, prepare every slug, check the whole output and whatever else already sits under
    `out_dir`, and only then write `<out_dir>/<slug>/...` (each slug's directory replaced whole) and
    `<out_dir>/index.json`, then grep every byte under `out_dir` once more. The slug -> entry / run link goes to
    `<provenance_dir>/provenance-<exportedAt>.json`, never under `out_dir`. Returns `{index, slugs: {slug: manifest +
    written}, dir, provenance}`."""
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
    seen: dict[str, str] = {}
    for r in runs:
        if r.entry not in by_entry:
            reasons.append(f"{r.dir.name}: entry {r.entry!r} is not in {NAMES_FILE.name}")
        elif r.entry in seen:
            reasons.append(f"{r.entry} given twice ({seen[r.entry]}, {r.dir.name})")
        seen.setdefault(r.entry, r.dir.name)
    if reasons:
        raise GalleryRefused(reasons)
    slugs = [prepare(by_entry[r.entry], r, exported_at=exported_at) for r in runs]
    reasons = check(slugs)
    needles = provenance_needles(slugs)
    replaced = [out_dir / s.name.slug for s in slugs] + [out_dir / INDEX]
    reasons += [f"already under OUT: {hit}" for hit in provenance_under(out_dir, needles, skip=replaced)]
    if reasons:
        raise GalleryRefused(reasons)
    manifests = {}
    for s in slugs:
        target = out_dir / s.name.slug
        if target.is_dir():
            shutil.rmtree(target)                    # the slug is the export's own: nothing stale survives
        written = se.write(target, s.reads, entry_id="", corpus_revision=0, cloud=None, exported_at=exported_at)
        (target / se.MANIFEST).write_text(se._dumps(s.manifest), encoding="utf-8")   # replaces 060's own
        manifests[s.name.slug] = {**s.manifest, "written": written["files"]}
    index = gallery_order([s.row for s in slugs])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / INDEX).write_text(se._dumps(index_file(index, exported_at)), encoding="utf-8")
    left = provenance_under(out_dir, needles)
    if left:                                         # unreachable after `check`; the last word is the bytes on disk
        raise GalleryRefused([f"written under OUT and carrying provenance: {hit}" for hit in left])
    provenance_dir.mkdir(parents=True, exist_ok=True)
    provenance = provenance_dir / f"provenance-{exported_at}.json"
    by_slug = {s.name.slug: s.provenance for s in slugs}
    provenance.write_text(se._dumps([by_slug[r["slug"]] for r in index]), encoding="utf-8")
    return {"index": index, "slugs": manifests, "dir": str(out_dir), "provenance": str(provenance)}


# ------------------------------------------------------------------------- spec 079 FR-6: the readers' gate

#: Spec 079 FR-6 (spec 063 amended): with `--scores`, a run is an example only when the readers passed it.
SCORE_GATE = ("a bundle whose latest score file at the current rubric version has a flagged screen, or a score_pct "
              "under the bar, or that has no score file, is refused by name; the gallery is built from the rest")


def _record_of(run_dir: Path) -> dict:
    try:
        return _json(Path(run_dir) / bt.RECORD)
    except (OSError, ValueError):
        return {}


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


def score_gate(run_dirs: list[Path], scores_dir: Path, *, bar_pct: float | None = None, refuse_flagged: bool = True,
               refuse_under_bar: bool = True) -> tuple[list[Path], list[str]]:
    """Spec 079 FR-6: `(the runs the readers passed, one reason per refused run, naming it)`. A run is refused when it
    has no score file at the current rubric version, when that file's latest has a flagged screen (`refuse_flagged`),
    or when its overall score_pct is under the bar (`refuse_under_bar`)."""
    from quality import rubric                                       # noqa: PLC0415

    bar = rubric.BAR_PCT if bar_pct is None else float(bar_pct)
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
        if refuse_under_bar and (pct is None or pct < bar):
            why.append(f"score_pct {pct}% under the bar of {bar:.0f}%")
        if why:
            refused.append(f"{run_dir.name} ({study}): {Path(latest['_path']).name} has {' and '.join(why)}")
        else:
            passing.append(run_dir)
    return passing, refused


def one_per_entry(run_dirs: list[Path], scope_order: list[str]) -> tuple[list[Path], list[str]]:
    """The gallery has one example per entry (its slug); a quality cycle walks several studies of one entry. Of an
    entry's runs, the first in `scope_order` (then the newest) is the example; the others are named, never dropped
    silently."""
    rank = {s: i for i, s in enumerate(scope_order)}
    by_entry: dict[str, list[tuple[Path, str]]] = {}
    for run_dir in run_dirs:
        record = _record_of(run_dir)
        by_entry.setdefault((record.get("entry") or {}).get("id") or Path(run_dir).name, []).append(
            (Path(run_dir), str(record.get("scope") or "ALL")))
    picked, notes = [], []
    for entry, runs in by_entry.items():
        runs.sort(key=lambda r: r[0].name, reverse=True)                     # the newest first (the stamp) ...
        runs.sort(key=lambda r: rank.get(r[1], len(rank)))                   # ... within the scope order (stable)
        picked.append(runs[0][0])
        if len(runs) > 1:
            notes.append(f"{entry}: the {runs[0][1]} study ({runs[0][0].name}) is the example; also passing: "
                         + ", ".join(f"{s} ({d.name})" for d, s in runs[1:]))
    return picked, notes


# ------------------------------------------------------------------------------------------------ make gallery

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="make gallery", description="Spec 063: the example gallery export.")
    p.add_argument("--out", required=True, help="where the slugs and index.json go (keel-web's public/sample/)")
    p.add_argument("--runs", default="", help="back-test run directories, comma-separated (default: newest per entry)")
    p.add_argument("--runs-dir", default=str(RUNS_DIR), help="where the default (and bare-named) runs are found")
    p.add_argument("--provenance-dir", default=str(PROVENANCE_DIR),
                   help="where provenance-<exportedAt>.json goes (never under --out)")
    p.add_argument("--scores", default="", help="spec 079 FR-6: quality/scores -- " + SCORE_GATE)
    p.add_argument("--bar", type=float, default=None, help="with --scores: the bar (default quality.rubric.BAR_PCT)")
    p.add_argument("--keep-flagged", action="store_true", help="with --scores: a flagged screen does not refuse")
    p.add_argument("--keep-under-bar", action="store_true", help="with --scores: a score_pct under the bar does not "
                                                                 "refuse")
    p.add_argument("--scope-order", default="", help="one example per entry: of an entry's runs, the first scope in "
                                                      "this comma-separated order (else an entry given twice refuses)")
    a = p.parse_args(argv)
    try:
        names = load_names()
        run_dirs = resolve_runs(a.runs, Path(a.runs_dir)) if a.runs.strip() else newest_runs(names, Path(a.runs_dir))
        if a.scores:
            run_dirs, refused = score_gate(run_dirs, Path(a.scores), bar_pct=a.bar, refuse_flagged=not a.keep_flagged,
                                           refuse_under_bar=not a.keep_under_bar)
            for reason in refused:
                print(f"gallery: refused {reason}")
            if not run_dirs:
                raise GalleryRefused(["every run was refused by the readers' gate (--scores): nothing to build"])
        if a.scope_order.strip():
            run_dirs, notes = one_per_entry(run_dirs, [s.strip() for s in a.scope_order.split(",") if s.strip()])
            for note in notes:
                print(f"gallery: {note}")
        result = export(run_dirs, Path(a.out), names=names, provenance_dir=Path(a.provenance_dir))
    except GalleryRefused as refusal:
        print(str(refusal), file=sys.stderr)
        return 1
    for row in result["index"]:
        m = result["slugs"][row["slug"]]
        print(f"gallery: {row['slug']:<13} {row['name']:<13} {'B2B' if row['b2b'] else 'B2C'}  {row['decision']:<17} "
              f"{len(m['written'])} files  (cloud {row['cloud']}, web {row['web']})")
    print(f"gallery: {len(result['index'])} slugs and {INDEX} under {result['dir']}; attributed, simulated, no provenance; "
          f"nothing committed anywhere")
    print(f"gallery: which run made which slug -> {result['provenance']} (outside OUT, not committed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
