"""Spec 063: the example gallery export -- the six back-test ideas' briefs, renamed, into the sample snapshot.

`make gallery RUNS=<dir>[,<dir>...] OUT=<dir>` (FR-1) reads finished `make backtest` run directories (spec 062) and
writes, for each, the 060 file set under `<OUT>/<slug>/` plus `<slug>/interview.json` (FR-3a) and `<slug>/manifest.json`
(FR-3), then one `<OUT>/index.json`. No stack, no model, no paid run: everything is read from the run directory.

What a run directory gives, and what is read from where (tasks.md, judgement calls 1-3):

- `export/` -- spec 062 FR-3's ungated 060/061 snapshot of the founder's reads (names kept, emails, the founder and
  tokens withheld), its `manifest.json` listing every file. That IS the 060 file set; it is read back, withheld again
  (a no-op on a good run, a guard on a bad one) and renamed.
- `backtest.json` -- the entry (`id`, `b2b`, `idea_name`), the stack's SHAs (`stack`), and per link
  `respondents[link].served` (the interview the stranger's page fetched, spec 062 FR-4.2) and `.drawn` (what the
  page drew for the run's one watched person: the kickers, the gate's chip labels, the follow-up screen).
- `transcript.jsonl` -- the follow-up stems the run's people were asked (`<person>: the one follow-up -- owed on ...`,
  the route's 200 `text`).
- `inputs.json` -- what the founder entered (`founder`: the project name, the four context fields, the window, the
  problem statement, the decider, the calibration answers), for `oneLine`, `problem` and the seven `axes`.

The back-test entries themselves are NOT loaded through `instructions.corpus.load`: they are corpus revision 13 in
keel-cloud now, and this eval's loader reads revision 12 until spec 064 (judgement call 1).

The rename (FR-2): every string value of every exported file is passed through `Renamer.text` -- each `replaces`
string of `instructions/gallery_names.toml`, whole word, matched without regard to case, written as the entry's `name`
with the first letter's case kept -- and nothing else changes. Then the survivors grep reads the whole output back
and refuses the export (nothing written) if any `replaces` string of any entry is left, outside the provenance fields
FR-3 itself asks for (`manifest.json`'s `entry`, `run` and `renamed`; `index.json`'s `entry` and `run`).
"""

from __future__ import annotations

import argparse
import copy
import json
import re
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

#: FR-1's seven gallery words, in the spec's order.
AXES = ("whoHasIt", "whoPays", "rhythm", "costMode", "priceShape", "firstStep", "kind")

#: The fields FR-3 asks to carry the entry id and the run directory, which spell the old name by construction
#: (`08-fresco`, `20261022T164045Z-backtest-08-fresco`, `renamed.from`); the survivors grep reads everything else.
PROVENANCE_MANIFEST = ("entry", "run", "renamed")
PROVENANCE_INDEX = ("entry", "run")

#: Keys never written into interview.json (FR-3a: tokens and ids withheld; the AI interviewer's forms are a later spec).
_DROPPED = frozenset({"itemId", "optionId", "id", "token", "costItemId", "advantagesWhen", "spoken", "clip", "clips"})

_RHYTHM = {"NIGHTS": "nightly", "DAYS": "daily", "WORKING_DAYS": "every working day", "WEEKS": "weekly",
           "MONTHS": "monthly"}
_PERIODLY = {"day": "daily", "week": "weekly", "month": "monthly", "quarter": "quarterly", "year": "yearly"}
_SLUG = re.compile(r"^[a-z][a-z0-9]*$")


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
    replaces: tuple[str, ...]
    axes: dict = field(default_factory=dict, hash=False, compare=False)


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
            problems.append(f"{entry}: slug {slug!r} is not lowercase letters and digits")
        if not (isinstance(name, str) and name.strip()):
            problems.append(f"{entry}: no name")
        if not (isinstance(replaces, list) and replaces and all(isinstance(r, str) and r.strip() for r in replaces)):
            problems.append(f"{entry}: replaces must be a list of one or more strings")
            replaces = []
        axes = row.get("axes") or {}
        unknown = sorted(set(axes) - set(AXES))
        if unknown:
            problems.append(f"{entry}: axes {unknown} are not among {list(AXES)}")
        out.append(GalleryName(entry=entry, slug=slug or "", name=name or "", replaces=tuple(replaces), axes=dict(axes)))
    for what in ("entry", "slug", "name"):
        seen = [getattr(n, what) for n in out]
        dupes = sorted({v for v in seen if seen.count(v) > 1})
        if dupes:
            problems.append(f"{what} repeated: {dupes}")
    if problems:
        raise GalleryRefused([f"{path.name}: {p}" for p in problems])
    return out


class Renamer:
    """FR-2: every whole-word occurrence of every `replaces` string, any case, becomes its `name` with the first
    letter's case kept (`Fresco` -> `Daylog`, `fresco` -> `daylog`). Longest first, so `Palus Finance` is one
    replacement and never `Idlewell Finance`."""

    def __init__(self, names: Iterable[GalleryName]):
        self.names = list(names)
        self._to: dict[str, str] = {}
        for n in self.names:
            for r in n.replaces:
                self._to[r.casefold()] = n.name
        words = sorted(self._to, key=len, reverse=True)
        self._rx = (re.compile(r"(?<!\w)(?:" + "|".join(re.escape(w) for w in words) + r")(?!\w)", re.IGNORECASE)
                    if words else None)
        self.old = [r for n in self.names for r in n.replaces]

    def _one(self, m: re.Match) -> str:
        found = m.group(0)
        new = self._to[found.casefold()]
        return (new[0].upper() if found[0].isupper() else new[0].lower()) + new[1:]

    def text(self, value: str) -> str:
        return self._rx.sub(self._one, value) if self._rx is not None else value

    def value(self, value: Any) -> Any:
        """A deep copy of a JSON value with every string value renamed; keys and every non-string kept."""
        if isinstance(value, str):
            return self.text(value)
        if isinstance(value, dict):
            return {k: self.value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.value(v) for v in value]
        return value

    def survivors(self, written: str) -> list[str]:
        """The `replaces` strings `written` still carries, whole word, any case. Empty is the pass."""
        return sorted({r for r in self.old if re.search(rf"(?<!\w){re.escape(r)}(?!\w)", written, re.IGNORECASE)})


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
           "costMode": {"HOURS": "time", "AMOUNT": "money"}.get(cost.get("mode")),
           "priceShape": _PERIODLY.get(price.get("period"), "one-off" if price and not price.get("period") else None),
           "firstStep": step,
           "kind": "business" if run.b2b else "consumer"}
    out.update({k: v for k, v in (override or {}).items() if k in AXES})
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
    reads: dict[str, Any]              # renamed and withheld, interview included -- what is written
    manifest: dict                     # FR-3's extra fields (files and exportedAt are added by the writer)
    row: dict                          # the index row


def prepare(name: GalleryName, run: Run, renamer: Renamer, *, exported_at: str) -> Slug:
    """One slug in memory: withhold again (060), rename (FR-2), the interview (FR-3a), the index row (FR-1)."""
    done = se.withhold(run.reads, founder_name=bt.IDENTITY_NAME, founder_email=bt.IDENTITY_EMAIL)
    reads = renamer.value(done.reads)
    iv = renamer.value(interview(run))
    reads[INTERVIEW] = iv
    figures = se.card(reads)
    stack = run.record.get("stack") or {}
    entry = run.record.get("entry") or {}
    manifest = {"entry": run.entry, "run": run.dir.name, "cloud": stack.get("keel-cloud"), "web": stack.get("keel-web"),
                "corpus": run.corpus, "renamed": {"from": list(name.replaces), "to": name.name}}
    row = {"slug": name.slug, "name": name.name,
           "oneLine": renamer.text(one_line(run.founder.get("project_name") or entry.get("title")) or ""),
           "problem": renamer.text(one_sentence(run.founder.get("problem_seed")) or ""),
           "decision": figures["decision"], "howSure": figures["howSure"],
           "pilot": figures["pilot"], "price": figures["price"], "b2b": run.b2b,
           "entry": run.entry, "run": run.dir.name, "cloud": stack.get("keel-cloud"), "web": stack.get("keel-web"),
           "axes": renamer.value(axes(run, name.axes)),
           "interview": {"links": [{"role": l["role"], "label": l["label"], "items": item_count(l)}
                                   for l in iv["links"]]}}
    return Slug(name=name, run=run, reads=reads, manifest={**manifest, "exportedAt": exported_at}, row=row)


def _without(d: dict, keys: Iterable[str]) -> dict:
    return {k: v for k, v in d.items() if k not in keys}


def check(slugs: list[Slug], renamer: Renamer) -> list[str]:
    """Every refusal reason over the whole output as it would be written: FR-2's survivors (any old name, any slug,
    outside the provenance fields), 060's (an email, the back-test founder, a link), and an id in interview.json."""
    reasons = []
    for s in slugs:
        written = "".join(se._dumps(v) for v in s.reads.values()) \
            + se._dumps(_without(s.manifest, PROVENANCE_MANIFEST)) + se._dumps(_without(s.row, PROVENANCE_INDEX))
        left = renamer.survivors(written)
        if left:
            reasons.append(f"{s.name.slug}: {left} survive the rename")
        held = se.survivors(written, founder_name=bt.IDENTITY_NAME, founder_email=bt.IDENTITY_EMAIL)
        if held:
            reasons.append(f"{s.name.slug}: {held} survive the withholding")
        ids = sorted({k for k in _keys(s.reads[INTERVIEW]) if k in _DROPPED})
        if ids:
            reasons.append(f"{s.name.slug}: interview.json carries {ids}")
    return reasons


def _keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from _keys(v)
    elif isinstance(value, list):
        for v in value:
            yield from _keys(v)


def export(run_dirs: list[Path], out_dir: Path, *, names: list[GalleryName] | None = None,
           exported_at: str | None = None) -> dict:
    """FR-1 to FR-3a: read every run, prepare every slug, check the whole output, and only then write
    `<out_dir>/<slug>/...` and `<out_dir>/index.json`. Returns `{index, slugs: {slug: manifest}}`."""
    names = load_names() if names is None else names
    by_entry = {n.entry: n for n in names}
    renamer = Renamer(names)
    exported_at = exported_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
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
    slugs = [prepare(by_entry[r.entry], r, renamer, exported_at=exported_at) for r in runs]
    reasons = check(slugs, renamer)
    if reasons:
        raise GalleryRefused(reasons)
    out_dir = Path(out_dir)
    manifests = {}
    for s in slugs:
        target = out_dir / s.name.slug
        written = se.write(target, s.reads, entry_id=s.run.entry, corpus_revision=s.run.corpus,
                           cloud=s.manifest["cloud"], exported_at=exported_at)
        manifest = {**s.manifest, "files": written["files"]}
        (target / se.MANIFEST).write_text(se._dumps(manifest), encoding="utf-8")
        manifests[s.name.slug] = manifest
    index = gallery_order([s.row for s in slugs])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / INDEX).write_text(se._dumps(index), encoding="utf-8")
    return {"index": index, "slugs": manifests, "dir": str(out_dir)}


# ------------------------------------------------------------------------------------------------ make gallery

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="make gallery", description="Spec 063: the example gallery export.")
    p.add_argument("--out", required=True, help="where the slugs and index.json go (keel-web's public/sample/)")
    p.add_argument("--runs", default="", help="back-test run directories, comma-separated (default: newest per entry)")
    p.add_argument("--runs-dir", default=str(RUNS_DIR), help="where the default (and bare-named) runs are found")
    a = p.parse_args(argv)
    try:
        names = load_names()
        run_dirs = resolve_runs(a.runs, Path(a.runs_dir)) if a.runs.strip() else newest_runs(names, Path(a.runs_dir))
        result = export(run_dirs, Path(a.out), names=names)
    except GalleryRefused as refusal:
        print(str(refusal), file=sys.stderr)
        return 1
    for row in result["index"]:
        m = result["slugs"][row["slug"]]
        print(f"gallery: {row['slug']:<13} {row['name']:<13} {'B2B' if row['b2b'] else 'B2C'}  {row['decision']:<17} "
              f"{len(m['files'])} files  <- {row['run']} (cloud {row['cloud']}, web {row['web']})")
    print(f"gallery: {len(result['index'])} slugs and {INDEX} under {result['dir']}; nothing committed anywhere")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
