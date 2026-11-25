"""The film table and the gate (spec 163 FR-4, FR-8): `make read-film-table RUN=<bundle> [DRIFT=1]` -- free.

One row per entry of the bundle: the film's criteria (F1..F8; S1..S9 on a solution film), `film_pct`, flagged, the
dollars, **beside the same entry's question score (`score_pct` over the §A screens) and its founder's-page score (§B,
`after_pct`) from `make read-screens` on the same bundle**, and `founder_pct` (the founder's beats); the mean over the
entries; the bar (`quality/cycle.toml` `[film] film_bar_pct`, 80); the weak criteria (`quality/FILM-RUBRIC.md`'s weak
rule); each entry's whys in one line a criterion and its frames linked (the report's *The film, judged*, FR-8); and the
findings a cloud or web spec owes (a picture with text, a caption clipped, a limitation with no scene, a setting that
names a company, a scene served with no picture), in `runs/DRIFT.md`'s shape -- appended there with `DRIFT=1`.

**Spec 165 FR-3: one project an entry.** The §A and §B columns come from the film's own project -- the score file of
`make read-screens` on the screens bundle `walk.json` names for the entry (the film leg's), and where the score file
names its project, that project; §A is the strangers' screens of the film's link (and §G), never a founder screen. A
walk row that names only a back-test bundle (a 163 walk: the typed project) is never tabled: its columns read `--`.

It writes `quality/FILM-TABLE.md` (rewritten) and the record `quality/cycles/<yyyymmdd>-<cloud7>-film.md`. An entry
passes at `film_pct` >= the bar with no 0; a round passes when every entry does -- and a round whose holdout entries
(`[film] holdout`) fall short fails whatever the others did (`quality/decisions.toml`'s rule, *rules not cases*).
Film score files of two `FILM_RUBRIC_VERSION`s are never tabled together.

**Spec 166 FR-5: both films an entry, ranked.** One row an entry: the problem film's F criteria and `film_pct`, the
solution film's S criteria and `film_pct`, `founder_pct` over both studies' beats, §A and §B of each study (each from
its own project's screens bundle, `walk.json`'s `solution`), the dollars of each leg; an entry passes at the bar on
**each** film with no 0. The **rank**: the entries by the mean of the two films' `film_pct`, ties by the problem film; an
entry with one film (its solution leg failed or was not walked) ranks on that film alone, marked. The verdict names
every entry under the bar on either film; the weak criteria and the findings are of both kinds.

**Spec 166 FR-6: compared with the previous run.** `BASELINE=<earlier walk or bundle>` adds *Compared with <the
baseline's record>*: per entry in both, each criterion's move (F1-F8, S1-S9, founder, §A, §B, the dollars) as
`before -> after (+/-)`, the entries added and missing, and the round's means before and after -- the baseline's film
score files read from `quality/scores/` by its bundle's name. The record keeps the comparison; `FILM-TABLE.md` the same.
A record of another bundle at the same name (the same day and build) is never overwritten: this one takes its bundle's
stamp.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

from quality import film_rubric as fr
from quality import rubric

REPO = Path(__file__).resolve().parent.parent
QUALITY = REPO / "quality"
SCORES_DIR = QUALITY / "scores"
TABLE_PATH = QUALITY / "FILM-TABLE.md"
CYCLES_DIR = QUALITY / "cycles"
CYCLE_TOML = QUALITY / "cycle.toml"
DRIFT_PATH = REPO / "runs" / "DRIFT.md"
SPEC = "163-the-film-judged"


class Refused(RuntimeError):
    """A reason the table is not written, printed as one sentence (exit 2)."""


# ------------------------------------------------------------------------------------------------ the settings

def load_film_config(path: Path | None = None) -> dict:
    """`quality/cycle.toml` `[film]`: the bar (a percentage), the holdout (a list of entry ids, empty until the
    integrator writes the founder's nine), the scopes and the adviser."""
    with Path(path or CYCLE_TOML).open("rb") as handle:
        raw = tomllib.load(handle)
    film = dict(raw.get("film") or {})
    bar = film.get("film_bar_pct")
    if isinstance(bar, bool) or not isinstance(bar, (int, float)) or not 0 <= bar <= 100:
        raise Refused(f"quality/cycle.toml [film] film_bar_pct is {bar!r} -- a percentage from 0 to 100 (spec 163 FR-4)")
    holdout = film.get("holdout")
    if not isinstance(holdout, list) or not all(isinstance(e, str) and e for e in holdout):
        raise Refused("quality/cycle.toml [film] holdout must be a list of entry ids (spec 163 FR-5)")
    return {"film_bar_pct": float(bar), "holdout": list(holdout), "scopes": list(film.get("scopes") or ["PROBLEM"]),
            "five": list((raw.get("cycle") or {}).get("entries") or []),
            "adviser": {"model": film.get("adviser_model"), "effort": film.get("adviser_effort"),
                        "timeout_s": int(film.get("adviser_timeout_s") or 300)}}


# ------------------------------------------------------------------------------------------------ the files

def bundle_of(run: str) -> str:
    """The bundle's name from `RUN=` (a path or a name)."""
    return Path(str(run).rstrip("/")).name


def resolve_run(run: str) -> Path:
    path = Path(str(run)).expanduser()
    if not path.is_absolute() and not path.exists():
        path = REPO / "runs" / path
    return path


def load_films(bundle: str, scores_dir: Path | None = None) -> list[dict]:
    """Every film score file of one bundle (`<bundle>-film-<entry>.json`), validated, each with its `_path`."""
    files = []
    for path in sorted(Path(scores_dir or SCORES_DIR).glob(f"{bundle}-film-*.json")):
        try:
            obj = fr.validate_file(json.loads(path.read_text(encoding="utf-8")), name=path.name)
        except (fr.FilmRubricError, json.JSONDecodeError) as reason:
            raise Refused(f"make read-film-table refuses {path}: {reason}") from None
        obj["_path"] = str(path)
        files.append(obj)
    try:
        fr.aggregate(files)
    except fr.FilmRubricMismatch as reason:
        raise Refused(f"make read-film-table refuses: {reason}") from None
    if files and files[0]["film_rubric_version"] != fr.FILM_RUBRIC_VERSION:
        raise Refused(f"make read-film-table refuses: the bundle's film scores are at film rubric version "
                      f"{files[0]['film_rubric_version']}, this checkout reads {fr.FILM_RUBRIC_VERSION} -- never compared")
    return files


def projects_of(run: str | Path) -> dict:
    """Spec 165 FR-2 / FR-3: the walk's record (`walk.json`, `make film-walk`) -- each entry's one project, by entry:
    `{bundle, project_id}`, the bundle being the film leg's screens bundle by name. A row naming only a `backtest` (a
    163 walk's second, typed project) is left out: a typed project's scores are never tabled beside the film. `{}`
    where the walk has no record (a bundle written by hand)."""
    path = Path(run) / "walk.json"
    if not path.is_file():
        return {}
    record = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for r in record.get("entries") or []:
        screens = r.get("screens") or (Path(r["screens_bundle"]).name if r.get("screens_bundle") else None)
        if screens:
            out[r["entry"]] = {"bundle": screens, "project_id": r.get("project_id")}
    return out


def solution_projects_of(run: str | Path) -> dict:
    """Spec 166 FR-3: each entry's solution project from `walk.json` (the row's `solution`), by entry: `{bundle,
    project_id}`, the bundle the solution leg's screens bundle by name."""
    path = Path(run) / "walk.json"
    if not path.is_file():
        return {}
    out = {}
    for r in json.loads(path.read_text(encoding="utf-8")).get("entries") or []:
        sol = r.get("solution") or {}
        screens = sol.get("screens") or (Path(sol["screens_bundle"]).name if sol.get("screens_bundle") else None)
        if screens:
            out[r["entry"]] = {"bundle": screens, "project_id": sol.get("project_id")}
    return out


def typed_rows(run: str | Path) -> list[str]:
    """The entries whose walk row names a back-test bundle and no film project's screens (163's walk): said in the
    record, never tabled."""
    path = Path(run) / "walk.json"
    if not path.is_file():
        return []
    record = json.loads(path.read_text(encoding="utf-8"))
    return [r["entry"] for r in record.get("entries") or [] if r.get("backtest") and not r.get("screens_bundle")]


def _project(value) -> tuple[str | None, str | None]:
    """A `projects_of` value (or, from a caller before spec 165, a bundle's name alone): `(bundle, project_id)`."""
    if isinstance(value, dict):
        return value.get("bundle"), value.get("project_id")
    return (str(value) if value else None), None


def question_scores(bundle: str, scores_dir: Path | None = None, projects: dict | None = None) -> dict:
    """The same walk's `make read-screens` score files (`quality/scores/<entry>/*.json`) of each entry's one project
    (spec 165 FR-3): the file's `bundle` is the screens bundle `walk.json` names for the entry and, where the file names
    its project, the project is the one `walk.json` names; by entry: `qa_pct` -- §A, the strangers' screens of the
    film's link (every R, R6) and the §G readings, never a founder screen -- and `after_pct` -- §B, the founder's page
    after the answers (spec 109) -- with the file's path, project and dollars."""
    out = {}
    wanted = {e: _project(v) for e, v in (projects or {}).items()}
    for path in sorted(Path(scores_dir or SCORES_DIR).glob("*/*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if obj.get("partial"):
            continue
        entry = obj.get("entry")
        want_bundle, want_project = wanted.get(entry, (bundle, None))
        if obj.get("bundle") != want_bundle:
            continue
        if want_project and obj.get("project_id") and obj["project_id"] != want_project:
            continue
        screens = obj.get("screens") or []
        qa = rubric.summary([s for s in screens if not rubric.is_after(s.get("kind"))
                             and s.get("audience") != "founder"], obj.get("insights") or [])
        after = (obj.get("summary") or {}).get("overall", {}).get("after_pct")
        out[entry] = {"qa_pct": qa.get("score_pct"), "after_pct": after, "path": str(path),
                      "project_id": obj.get("project_id") or want_project,
                      "cost_usd": obj.get("cost_usd"), "rubric_version": obj.get("rubric_version")}
    return out


# ------------------------------------------------------------------------------------------------ the rows

def rows(files: list[dict], questions: dict, bar: float, holdout: list[str],
         solution_questions: dict | None = None) -> list[dict]:
    """One row a film (both kinds, spec 166), each beside its own study's §A and §B (`questions` the problem's,
    `solution_questions` the solution's)."""
    out = []
    order = {"problem": 0, "solution": 1}
    for f in sorted(files, key=lambda x: (x["entry"], order.get((x.get("film") or {}).get("kind"), 2))):
        film = f["film"]
        q = ((solution_questions or {}) if film["kind"] == "solution" else questions).get(f["entry"]) or {}
        out.append({"entry": f["entry"], "kind": film["kind"], "scores": film["scores"], "film_pct": film["film_pct"],
                    "flagged": film["flagged"], "founder_pct": (f.get("founder") or {}).get("founder_pct"),
                    "founder_beats": list((f.get("founder") or {}).get("beats") or []),
                    "qa_pct": q.get("qa_pct"), "after_pct": q.get("after_pct"), "project_id": q.get("project_id"),
                    "screens_usd": q.get("cost_usd"),
                    "usd": f.get("cost_usd"), "walk_usd": f.get("walk_usd"),
                    "passes": fr.passes(film, bar), "holdout": f["entry"] in holdout, "file": f["_path"],
                    "whys": film["whys"], "instead": film["instead"], "missing": film["missing"],
                    "frames": f.get("frames") or {}, "measures": f.get("measures"),
                    "cloud_sha": f.get("cloud_sha"), "web_sha": f.get("web_sha")})
    return out


def _mean(values: list) -> float | None:
    got = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return round(sum(got) / len(got), 1) if got else None


def _leg_usd(r: dict | None) -> float | None:
    """One leg's dollars: the film's reading, the walk's measured dollars and the screens' reading, where known."""
    if not r:
        return None
    parts = [r.get(k) for k in ("usd", "walk_usd", "screens_usd")]
    got = [float(v) for v in parts if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return round(sum(got), 2) if got else None


def entry_rows(table: list[dict]) -> list[dict]:
    """Spec 166 FR-5: one row an entry -- the problem film's row and the solution film's -- with the mean of the two
    films' `film_pct` (`rank_pct`; one film alone where the other is not there, marked `alone`), `founder_pct` over both
    studies' beats, whether it passes on each film, and its rank: by `rank_pct`, ties by the problem film, then by name."""
    by: dict[str, dict] = {}
    for r in table:
        row = by.setdefault(r["entry"], {"entry": r["entry"], "problem": None, "solution": None,
                                         "holdout": r["holdout"]})
        row[r["kind"]] = r
    out = []
    for row in by.values():
        films = [row[k] for k in ("problem", "solution") if row[k]]
        row["rank_pct"] = _mean([f["film_pct"] for f in films])
        row["alone"] = None if len(films) == 2 else (films[0]["kind"] if films else None)
        beats = [b for f in films for b in f.get("founder_beats") or []]
        row["founder_pct"] = fr.founder_summary(beats)["founder_pct"] if beats else \
            _mean([f.get("founder_pct") for f in films])
        row["passes"] = bool(films) and all(f["passes"] for f in films)
        row["under"] = [f["kind"] for f in films if not f["passes"]]
        row["flagged"] = [f["kind"] for f in films if f["flagged"]]
        out.append(row)
    out.sort(key=lambda r: (-(r["rank_pct"] if r["rank_pct"] is not None else -1),
                            -((r["problem"] or {}).get("film_pct") or -1), r["entry"]))
    for i, row in enumerate(out, 1):
        row["rank"] = i
    return out


def verdict(table: list[dict], holdout: list[str]) -> dict:
    """FR-4 / FR-5: the round passes when every entry passes; a tabled holdout entry that fails fails the round by name
    (the five passing does not carry it). Spec 166 FR-5: an entry passes on **each** of its films; the entries under the
    bar on either film are named with the film."""
    entries = entry_rows(table)
    failed = [e["entry"] for e in entries if not e["passes"]]
    held = [e["entry"] for e in entries if e["holdout"]]
    held_failed = [e for e in failed if e in holdout]
    pct = [r["film_pct"] for r in table if r["film_pct"] is not None]
    return {"entries": len(entries), "passed": len(entries) - len(failed), "failed": failed,
            "under": {e["entry"]: e["under"] for e in entries if e["under"]},
            "holdout_tabled": held, "holdout_failed": held_failed,
            "mean_film_pct": round(sum(pct) / len(pct), 1) if pct else None,
            "mean_problem_pct": _mean([r["film_pct"] for r in table if r["kind"] == "problem"]),
            "mean_solution_pct": _mean([r["film_pct"] for r in table if r["kind"] == "solution"]),
            "mean_rank_pct": _mean([e["rank_pct"] for e in entries]),
            "round_passes": bool(entries) and not failed}


# ------------------------------------------------------------------------------------------------ the comparison

def _move(before, after) -> str:
    """`before -> after (+/-)`, one place of decimals where a value is a percentage."""
    def show(v):
        if v is None:
            return "--"
        return f"{v:.1f}" if isinstance(v, float) else str(v)
    if before is None and after is None:
        return "--"
    if before is None or after is None:
        return f"{show(before)} -> {show(after)}"
    delta = after - before
    sign = "+" if delta > 0 else ("-" if delta < 0 else "±")
    size = f"{abs(delta):.1f}" if isinstance(delta, float) else str(abs(delta))
    return f"{show(before)} -> {show(after)} ({sign}{size})"


#: Spec 166 FR-6: what moves are told per entry, in order -- each film's criteria and `film_pct`, the founder, §A, §B and
#: the dollars of each leg.
def _measures(row: dict) -> dict:
    out = {}
    for kind, names in fr.KINDS.items():
        film = row.get(kind) or {}
        for c in names:
            out[c.upper()] = (film.get("scores") or {}).get(c) if film else None
        out[f"{kind} film_pct"] = film.get("film_pct") if film else None
    out["founder_pct"] = row.get("founder_pct")
    for kind in ("problem", "solution"):
        film = row.get(kind) or {}
        out[f"§A {kind}"] = film.get("qa_pct") if film else None
        out[f"§B {kind}"] = film.get("after_pct") if film else None
        out[f"$ {kind}"] = _leg_usd(film) if film else None
    return out


def compare(now: list[dict], before: list[dict]) -> dict:
    """Spec 166 FR-6: the run against its baseline -- per entry in both, each measure's move; the entries added (here,
    not there) and missing (there, not here); the round's means before and after."""
    a, b = {e["entry"]: e for e in entry_rows(now)}, {e["entry"]: e for e in entry_rows(before)}
    both = sorted(set(a) & set(b))
    moves = {}
    for entry in both:
        was, got = _measures(b[entry]), _measures(a[entry])
        moves[entry] = {k: _move(was[k], got[k]) for k in got if was[k] is not None or got[k] is not None}
    vb, va = verdict(before, []), verdict(now, [])
    means = {k: _move(vb[k], va[k]) for k in ("mean_problem_pct", "mean_solution_pct", "mean_rank_pct")}
    return {"both": both, "added": sorted(set(a) - set(b)), "missing": sorted(set(b) - set(a)), "moves": moves,
            "means": means, "rank_before": {e: b[e]["rank"] for e in b}, "rank_after": {e: a[e]["rank"] for e in a}}


def compared_markdown(cmp: dict, *, name: str, bundle: str) -> list[str]:
    lines = [f"## Compared with {name}", "",
             f"The baseline: bundle `{bundle}` (its film score files in `quality/scores/`). Each move is "
             "`before -> after (+/-)`.", "",
             "**The round's means**: " + "; ".join(f"{k.replace('mean_', '').replace('_pct', '')} film_pct {v}"
                                                   .replace("rank film_pct", "the mean of the two films")
                                                   for k, v in cmp["means"].items()) + ".", ""]
    if cmp["added"]:
        lines.append(f"Entries added (not in the baseline): {', '.join(cmp['added'])}.")
    if cmp["missing"]:
        lines.append(f"Entries missing (in the baseline, not here): {', '.join(cmp['missing'])}.")
    if cmp["added"] or cmp["missing"]:
        lines.append("")
    if not cmp["both"]:
        lines += ["No entry is in both runs: nothing moved to compare.", ""]
        return lines
    for entry in cmp["both"]:
        lines.append(f"### {entry} -- rank {cmp['rank_before'].get(entry)} -> {cmp['rank_after'].get(entry)}")
        lines.append("")
        lines.append("| measure | before -> after |")
        lines.append("|---|---|")
        for k, v in cmp["moves"][entry].items():
            lines.append(f"| {k} | {v} |")
        lines.append("")
    return lines


def load_baseline(baseline: str, scores_dir: Path, cfg: dict) -> tuple[list[dict], list[dict], str]:
    """The baseline's per-film rows (its own §A and §B from its own walk's record), its files and its bundle's name."""
    bundle = bundle_of(baseline)
    files = load_films(bundle, scores_dir)
    if not files:
        raise Refused(f"make read-film-table refuses BASELINE={baseline}: no film score file for {bundle} under "
                      f"{scores_dir}")
    run = resolve_run(baseline)
    table = rows(files, question_scores(bundle, scores_dir, projects_of(run)), cfg["film_bar_pct"], cfg["holdout"],
                 question_scores(bundle, scores_dir, solution_projects_of(run)))
    return table, files, bundle


def _cell(value) -> str:
    if value is None:
        return "--"
    return f"{value:.1f}" if isinstance(value, float) else str(value)


def _usd(value) -> str:
    return "--" if value is None else f"{float(value):.2f}"


def _flat(text: str) -> str:
    return " ".join(str(text or "").split()).replace("|", "/")


# ------------------------------------------------------------------------------------------------ DRIFT

#: FR-8: a criterion at 0 that names a cloud or web finding, and what the product owes.
FINDINGS = {
    "f8": ("a word garbled, text inside a picture, or a caption cut or clipped",
           "keel-cloud 273 (`PicturePrompts`' no-text rule, `picture-review.md`'s `text_seen`) or keel-web 261 (the "
           "caption band)"),
    "f4": ("a limitation of the problem statement with no scene of its own",
           "keel-cloud 268 / 273 (`story-draft.md`: one scene a limitation)"),
    "f1": ("the person or the setting is not this person's (another trade, another place, or a named company)",
           "keel-cloud 273 (`picture-setting.md`, the character)"),
    "f5": ("the pain is not shown as the person's reaction", "keel-cloud 273 (the pain scene's cue)"),
    "s9": ("a word garbled or text inside a picture on the solution film", "keel-cloud 273 / keel-web 261"),
    "s4": ("a limitation with no tick or cross on the solution film", "keel-cloud 271 / 273"),
    # spec 166 FR-5: the solution film's other product findings
    "s1": ("another person than the problem film's, or no brand on the screen, on the solution film",
           "keel-cloud 273 / 275 (the problem's character sheet reused, the brand in the scene prompts)"),
    "s6": ("the solution film does not end on what the person gets back (a feature, or no joy)",
           "keel-cloud 271 FR-9 (the joy scene) / `idea-draft.md`"),
    "s2": ("the setup shown where none was named, or missing where it was",
           "keel-cloud 271 FR-9 (the setup scene iff a setup)"),
}


#: Spec 168 FR-2: the DRIFT finding where the lock's calibration was FAILED and written again on the founder's retry.
LOCK_RETRIED_WHAT = "the lock's calibration was written again on the founder's retry"
LOCK_RETRIED_OWED = ("keel-cloud's calibration writer (the window-frame rules and spec 107's one repair turn: the first "
                     "attempt refused twice)")


def lock_retried_why(kind: str) -> str:
    scope = "SOLUTION" if kind == "solution" else "PROBLEM"
    return (f"GET calibration/{scope} read FAILED at the lock; the walk pressed FounderVoice's retry (POST "
            f"calibration/{scope}/retry) once, as a founder on that screen would")


def lock_retried_mark(row: dict) -> str:
    """Spec 168 FR-2: *lock retried* beside *flagged* in an entry's heading, where the founder's retry was pressed."""
    return ", lock retried" if (row.get("measures") or {}).get("lock_retried") else ""


def findings(table: list[dict]) -> list[dict]:
    """The findings a cloud or web spec owes: every criterion of `FINDINGS` scored 0, and every measure the capture
    held false (a scene served with no picture, a caption outside the stage or over three lines on the phone) -- each
    with the frame's path."""
    out = []
    for r in table:
        folder = (r.get("frames") or {}).get("folder") or ""
        frames = (r.get("frames") or {}).get("frames") or []
        for crit, (what, owed) in FINDINGS.items():
            if r["scores"].get(crit) == 0:
                out.append({"entry": r["entry"], "kind": r["kind"], "criterion": crit.upper(), "what": what,
                            "owed": owed,
                            "why": r["whys"].get(crit, ""), "instead": r["instead"].get(crit, ""),
                            "missing": r["missing"] if crit in ("f4", "s4") else [],
                            "frames": [f"{folder}/{p}" for p in frames[:2]], "cloud": r["cloud_sha"],
                            "web": r["web_sha"]})
        if (r.get("measures") or {}).get("lock_retried"):
            # spec 168 FR-2: the calibration writer's result refused, written again on the founder's retry
            out.append({"entry": r["entry"], "kind": r["kind"], "criterion": "capture", "what": LOCK_RETRIED_WHAT,
                        "owed": LOCK_RETRIED_OWED, "why": lock_retried_why(r["kind"]), "instead": "", "missing": [],
                        "frames": [f"{folder}/{p}" for p in frames[:2]], "cloud": r["cloud_sha"],
                        "web": r["web_sha"]})
        for m in (r.get("measures") or {}).get("faults") or []:
            out.append({"entry": r["entry"], "kind": r["kind"], "criterion": "capture", "what": m.get("what", ""),
                        "owed": m.get("owed", ""),
                        "why": m.get("detail", ""), "instead": "", "missing": [],
                        "frames": [f"{folder}/{m['frame']}"] if m.get("frame") else [], "cloud": r["cloud_sha"],
                        "web": r["web_sha"]})
    return out


def drift_text(found: list[dict], *, start: int, bundle: str) -> str:
    blocks = []
    for i, f in enumerate(found, start):
        frames = ", ".join(f"`{p}`" for p in f["frames"]) or "(no frame)"
        missing = (" Not shown: " + "; ".join(f["missing"]) + ".") if f["missing"] else ""
        film = "the solution film" if f.get("kind") == "solution" else "the film"
        blocks.append(
            f"## {i}. Observation ({film}, {f['entry']}): {f['what']}\n\n"
            f"Found by spec `{SPEC}` (`make read-film-table`, {f['criterion']}) on keel-cloud-docs `{f['cloud']}` with "
            f"keel-web `{f['web']}`, bundle `{bundle}`; the frames: {frames}. The reader: *{_flat(f['why'])}*"
            + (f" -- instead: *{_flat(f['instead'])}*" if f["instead"] else "") + f".{missing} **What the harness "
            f"does**: the film's score carries it (a 0 flags the film; nothing is patched around). **For** {f['owed']}.\n")
    return "\n".join(blocks)


def next_drift_number(path: Path | None = None) -> int:
    path = Path(path or DRIFT_PATH)
    if not path.is_file():
        return 1
    found = [int(m) for m in re.findall(r"^## (\d+)\.", path.read_text(encoding="utf-8"), flags=re.M)]
    return max(found, default=0) + 1


# ------------------------------------------------------------------------------------------------ render

def render(table: list[dict], files: list[dict], weak: list[dict], cfg: dict, *, bundle: str,
           found: list[dict], typed: list[str] | None = None, compared: list[str] | None = None) -> str:
    v = verdict(table, cfg["holdout"])
    entries = entry_rows(table)
    reader = (files[0].get("reader") if files else None) or {}
    founder_reader = (files[0].get("founder_reader") if files else None) or {}
    usd = sum(r["usd"] or 0 for r in table)
    walk = sum(r["walk_usd"] or 0 for r in table if isinstance(r["walk_usd"], (int, float)))
    under = "; ".join(f"{e} ({' and '.join(f'the {k} film' for k in kinds)})" for e, kinds in v["under"].items())
    lines = [
        "# The film, judged",
        "",
        f"Bundle `{bundle}` · FILM_RUBRIC_VERSION {fr.FILM_RUBRIC_VERSION} · the film reader "
        f"{reader.get('model', '--')} {reader.get('effort', '')} ({reader.get('door', '--')}) · the founder-reader "
        f"{founder_reader.get('model', '--')} {founder_reader.get('effort', '')} ({founder_reader.get('door', '--')}) · "
        f"the bar {cfg['film_bar_pct']:.0f}% (`quality/cycle.toml` [film] film_bar_pct) · specs 163, 166.",
        "",
        f"**This round**: {v['entries']} entr{'y' if v['entries'] == 1 else 'ies'}; mean film_pct "
        f"{_cell(v['mean_problem_pct'])} on the problem films, {_cell(v['mean_solution_pct'])} on the solution films, "
        f"{_cell(v['mean_rank_pct'])} on the mean of the two; {v['passed']} pass on each film, {len(v['failed'])} "
        "fall short" + (f" ({under})" if under else "") + "; the round "
        + ("**passes**." if v["round_passes"] else "**fails**.")
        + (f" Holdout tabled: {', '.join(v['holdout_tabled'])}" + (f"; holdout short: {', '.join(v['holdout_failed'])}"
                                                                  if v["holdout_failed"] else "") + "."
           if v["holdout_tabled"] else
           (" The holdout (`[film] holdout`) is not written yet: this is not the round of record." if not cfg["holdout"]
            else " No holdout entry is in this bundle: this is not the round of record.")),
        f"**Dollars**: the reading ${usd:.2f}" + (f", the walk ${walk:.2f}" if walk else "") + ".",
        "",
        "## The table",
        "",
        "Ranked by the mean of the two films' film_pct (ties by the problem film); an entry with one film ranks on it "
        "alone, marked. An entry passes at the bar on each of its films with no 0.",
        "",
        "| rank | entry | " + " | ".join(c.upper() for c in fr.F_CRITERIA) + " | problem film_pct | "
        + " | ".join(c.upper() for c in fr.S_CRITERIA) + " | solution film_pct | mean | flagged | founder_pct | "
        "§A problem | §B problem | §A solution | §B solution | $ problem | $ solution | passes |",
        "|---|---|" + "---|" * (len(fr.F_CRITERIA) + len(fr.S_CRITERIA) + 13),
    ]
    for e in entries:
        p, sol = e["problem"] or {}, e["solution"] or {}
        f_cells = [_cell((p.get("scores") or {}).get(c)) if p else "--" for c in fr.F_CRITERIA]
        s_cells = [_cell((sol.get("scores") or {}).get(c)) if sol else "--" for c in fr.S_CRITERIA]
        mark = f" ({e['alone']} film alone)" if e["alone"] else ""
        lines.append(f"| {e['rank']} | {e['entry']}{' (holdout)' if e['holdout'] else ''}{mark} | "
                     + " | ".join(f_cells) + f" | {_cell(p.get('film_pct'))} | " + " | ".join(s_cells)
                     + f" | {_cell(sol.get('film_pct'))} | {_cell(e['rank_pct'])} | "
                     f"{', '.join(e['flagged']) or 'no'} | {_cell(e['founder_pct'])} | {_cell(p.get('qa_pct'))} | "
                     f"{_cell(p.get('after_pct'))} | {_cell(sol.get('qa_pct'))} | {_cell(sol.get('after_pct'))} | "
                     f"{_usd(_leg_usd(p) if p else None)} | {_usd(_leg_usd(sol) if sol else None)} | "
                     f"{'yes' if e['passes'] else 'no'} |")
    lines += ["", "§A and §B are `make read-screens` on **the film's project** (spec 165: the one project an entry -- "
                  "the film told, locked, its link answered by the entry's people, its page read after them) -- and "
                  "for the solution, on the solution's own project made from the problem's (spec 166): §A the "
                  "strangers' screens of each film's link (RUBRIC.md R1-R6, and §G), §B the founder's page after the "
                  "answers (the Overview's cards, the Insights tab, the brief); `--` where it has not been read. No "
                  "typed project's score is tabled here. founder_pct is over both studies' beats. The dollars of a leg "
                  "are its film's reading, its walk and its screens' reading, where known.", ""]
    projects = [(r["entry"], r["kind"], r.get("project_id")) for r in table if r.get("project_id")]
    if projects:
        lines.append("The film's project: " + "; ".join(f"{e} `{p}`" for e, k, p in projects if k == "problem") + "."
                     if any(k == "problem" for _, k, _ in projects) else "")
        if any(k == "solution" for _, k, _ in projects):
            lines.append("The solution's project: " + "; ".join(f"{e} `{p}`" for e, k, p in projects
                                                                if k == "solution") + ".")
        lines.append("")
    if typed:
        lines.append("Not tabled (a walk before spec 165, whose §A and §B were a second, typed project's): "
                     + ", ".join(typed) + ".")
        lines.append("")
    lines += ["## Weak criteria", ""]
    if weak:
        for w in weak:
            lines.append(f"- **{w['criterion'].upper()}** ({w['kind']}): mean {w['mean']:.2f}, a 0 in {w['zeros']} "
                         f"entr{'y' if w['zeros'] == 1 else 'ies'}" + (f" ({', '.join(w['zero_entries'])})"
                                                                         if w["zero_entries"] else "")
                         + " -- `make film-advise` proposes a rule for it.")
    else:
        lines.append("None (no criterion with a 0 in two entries or more, none with a mean under 1.5).")
    lines += ["", "## Each entry's whys", ""]
    for e in entries:
        for r in (x for x in (e["problem"], e["solution"]) if x):
            folder = (r.get("frames") or {}).get("folder") or ""
            frames = (r.get("frames") or {}).get("frames") or []
            film = "the solution film" if r["kind"] == "solution" else "the problem film"
            lines.append(f"### {r['entry']} -- {film}, film_pct {_cell(r['film_pct'])}"
                         f"{', flagged' if r['flagged'] else ''}{lock_retried_mark(r)}")
            lines.append("")
            for c in fr.KINDS[r["kind"]]:
                extra = f" -- *instead*: {_flat(r['instead'][c])}" if c in r["instead"] else ""
                lines.append(f"- {c.upper()} {r['scores'][c]}: {_flat(r['whys'].get(c))}{extra}")
            if r["missing"]:
                lines.append(f"- missing: {'; '.join(_flat(m) for m in r['missing'])}")
            if frames:
                base = folder if Path(folder).is_absolute() else f"../{folder}"      # the table lives in quality/
                lines.append("- frames: " + ", ".join(f"[{Path(x).name}]({base}/{x})" for x in frames))
            lines.append("")
    lines += ["## Findings for DRIFT", ""]
    if found:
        for f in found:
            kind = " (the solution film)" if f.get("kind") == "solution" else ""
            lines.append(f"- {f['entry']}{kind} ({f['criterion']}): {f['what']} -- "
                         f"{', '.join(f['frames']) or 'no frame'}")
        lines.append("")
        lines.append("`make read-film-table RUN=... DRIFT=1` appends them to `runs/DRIFT.md` in its shape.")
    else:
        lines.append("None.")
    lines.append("")
    if compared:
        lines += compared
    return "\n".join(lines)


def record_name(files: list[dict]) -> str:
    sha = str((files[0].get("cloud_sha") if files else None) or "nosha")[:7]
    day = str((files[0].get("scored_at") if files else "") or "")[:10].replace("-", "") or "00000000"
    return f"{day}-{sha}-film.md"


def record_path(cycles_dir: Path, files: list[dict], bundle: str) -> Path:
    """The record's path: `<yyyymmdd>-<cloud7>-film.md`, or -- where a record of another bundle already stands at that
    name (the same day, the same build: the trial on two was overwritten so) -- `...-film-<bundle's stamp>.md`."""
    path = Path(cycles_dir) / record_name(files)
    if path.is_file() and f"Bundle `{bundle}`" not in path.read_text(encoding="utf-8"):
        path = path.with_name(path.stem + f"-{bundle.split('-')[0]}.md")
    return path


def baseline_record_name(files: list[dict], bundle: str, cycles_dir: Path) -> str:
    """The baseline's record as the cycles folder names it (the record whose head names its bundle), else its name."""
    for path in sorted(Path(cycles_dir).glob("*-film*.md")):
        try:
            if f"Bundle `{bundle}`" in path.read_text(encoding="utf-8").split("\n", 3)[2]:
                return f"`{path.name}`"
        except (OSError, IndexError):
            continue
    return f"`{record_name(files)}` (bundle `{bundle}`)"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="quality.film_table", description=__doc__.split("\n\n")[0])
    parser.add_argument("--run", default="")
    parser.add_argument("--scores-dir", default=str(SCORES_DIR))
    parser.add_argument("--table", default=str(TABLE_PATH))
    parser.add_argument("--cycles-dir", default=str(CYCLES_DIR))
    parser.add_argument("--cycle-toml", default=str(CYCLE_TOML))
    parser.add_argument("--drift", action="store_true")
    parser.add_argument("--drift-path", default=str(DRIFT_PATH))
    parser.add_argument("--baseline", default=None)
    args = parser.parse_args(argv)
    try:
        if not args.run:
            raise Refused("make read-film-table refuses: no RUN -- name the film-walk bundle, `make read-film-table "
                          "RUN=runs/<bundle>` (spec 163 FR-4)")
        cfg = load_film_config(Path(args.cycle_toml))
        bundle = bundle_of(args.run)
        files = load_films(bundle, Path(args.scores_dir))
        if not files:
            raise Refused(f"make read-film-table refuses: no film score file for {bundle} under {args.scores_dir} -- "
                          "`make read-films RUN=...` first")
    except Refused as reason:
        print(str(reason), file=sys.stderr)
        return 2
    run = resolve_run(args.run)
    table = rows(files, question_scores(bundle, Path(args.scores_dir), projects_of(run)),
                 cfg["film_bar_pct"], cfg["holdout"],
                 question_scores(bundle, Path(args.scores_dir), solution_projects_of(run)))
    weak = fr.weak_criteria(files)
    found = findings(table)
    compared = None
    if args.baseline:
        try:
            before, before_files, before_bundle = load_baseline(args.baseline, Path(args.scores_dir), cfg)
        except Refused as reason:
            print(str(reason), file=sys.stderr)
            return 2
        compared = compared_markdown(compare(table, before), bundle=before_bundle,
                                     name=baseline_record_name(before_files, before_bundle, Path(args.cycles_dir)))
    text = render(table, files, weak, cfg, bundle=bundle, found=found, typed=typed_rows(run), compared=compared)
    Path(args.table).write_text(text, encoding="utf-8")
    record = record_path(Path(args.cycles_dir), files, bundle)
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(text, encoding="utf-8")
    if args.drift and found:
        path = Path(args.drift_path)
        start = next_drift_number(path)
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\n" + drift_text(found, start=start, bundle=bundle))
        print(f"{len(found)} finding(s) appended to {path} as #{start}..#{start + len(found) - 1}")
    v = verdict(table, cfg["holdout"])
    print(f"{v['entries']} entries, mean film_pct {v['mean_problem_pct']} (problem) / {v['mean_solution_pct']} "
          f"(solution), {v['passed']} pass on each film; the round {'passes' if v['round_passes'] else 'fails'}; "
          f"{len(weak)} weak criteria; {len(found)} DRIFT finding(s)" + ("; compared with the baseline" if compared
                                                                        else ""))
    print(f"wrote {args.table} and {record}")
    print(f"git add {args.table} {record} " + " ".join(f["_path"] for f in files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
