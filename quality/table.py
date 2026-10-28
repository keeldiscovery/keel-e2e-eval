"""The table of record (spec 078 FR-5 / FR-6): `make read-table [BASELINE=1]` -- free, no model, no stack.

From every committed score file under `quality/scores/`, `quality/TABLE.md`:

- **the head**: the overall `score_pct` over the latest file of every entry at the current `RUBRIC_VERSION`, per
  audience, and the founder's bar -- **90%** before the remaining entries are walked (the coordinator's decision 2);
- **the Insights grouping (§G)**: one row per (scope, dimension) under the *insights* kind, G1 and G2's means;
- **one row per (scope, dimension, audience, screen kind)** over the latest file of each (entry, scope) -- one corpus
  entry is three studies (spec 071 FR-4), so a row never mixes scopes: the five means, the count of 0s, the
  entries that gave them, the *instead* lines, and the fix location by the design's §1 (registry row / shared file /
  code transform / no model); weak rows marked by the weak rule (`quality/RUBRIC.md`);
- **the trend per study (entry · scope)**: its last three score files, `score_pct` and the five means with ↑ ↓ = beside each.

A score file at another rubric version is **set aside by name**, never averaged (FR-1); a partial file (a smoke's
`LIMIT=` / `ONLY=`) is refused by name -- it never belongs under `quality/scores/`.

`BASELINE=1` adds the comparison with `quality/BASELINE.md` (FR-6), like with like -- only the (entry, scope) studies
the baseline names are compared: each row's deltas and one verdict line, **better /
same / worse** (the rule in RUBRIC.md); refused when no baseline is cut or the baseline is at another rubric version.
`--cut-baseline` writes `BASELINE.md` from the latest files (the old one kept under `quality/baselines/<date>.md`) --
only on the founder's word, and so it is no make target.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

from quality import rubric

QUALITY = Path(__file__).resolve().parent
SCORES_DIR = QUALITY / "scores"
TABLE_PATH = QUALITY / "TABLE.md"
BASELINE_PATH = QUALITY / "BASELINE.md"
BASELINES_DIR = QUALITY / "baselines"

#: A move of the overall score_pct smaller than this is *same* (RUBRIC.md, the verdict).
SAME_BAND_PCT = 1.0

_DATA_BEGIN = "<!-- baseline:data -->"


class TableRefused(RuntimeError):
    """A reason the table cannot be built or compared, printed as one sentence (exit 2)."""


# ------------------------------------------------------------------------------------------- the files

def load_scores(scores_dir: Path | None = None) -> list[dict]:
    """Every score file under `scores_dir`, validated, each with its `_path`. A partial file is refused by name."""
    files = []
    for path in sorted(Path(scores_dir or SCORES_DIR).glob("*/*.json")):
        obj = rubric.load_file(path)
        if obj.get("partial"):
            raise TableRefused(f"{path} is a partial run (LIMIT / ONLY): a part of a walk is not a score of record "
                               "and never belongs under quality/scores/")
        obj["_path"] = str(path)
        files.append(obj)
    return files


def split_by_version(files: list[dict], version: int | None = None) -> tuple[list[dict], list[dict]]:
    version = rubric.RUBRIC_VERSION if version is None else version
    return ([f for f in files if f["rubric_version"] == version],
            [f for f in files if f["rubric_version"] != version])


def _order(f: dict):
    return (f.get("scored_at") or "", Path(f.get("_path", "")).name)


def scope_of(f: dict) -> str:
    """A score file's study scope (spec 071 FR-4): one corpus entry is three studies; ALL when the file says none."""
    return str(f.get("scope") or "ALL")


def study(f: dict) -> str:
    """The key a score file is latest for, compared and trended under: `<entry> · <scope>` (like with like)."""
    return f"{f['entry']} · {scope_of(f)}"


def latest_per_entry(files: list[dict]) -> dict:
    """The latest score file of every (entry, scope), keyed `<entry> · <scope>`."""
    latest = {}
    for f in sorted(files, key=_order):
        latest[study(f)] = f
    return dict(sorted(latest.items()))


def history_per_entry(files: list[dict], keep: int = 3) -> dict:
    out = {}
    for f in sorted(files, key=_order):
        out.setdefault(study(f), []).append(f)
    return {key: runs[-keep:] for key, runs in sorted(out.items())}


# ---------------------------------------------------------------------------------------- fix locations

_FOUNDER_FILES = {
    "problem-seed": ("shared file", "problem-interpret.md"),
    "problem-card": ("shared file", "problem-interpret.md"),
    "solution-seed": ("shared file", "solution-mechanism.md"),
    "solution-card": ("shared file", "solution-mechanism.md"),
    "idea": ("shared file", "solution-mechanism.md"),
    "failed-solution-calibration": ("shared file", "solution-mechanism.md"),
    "context": ("shared file", "context-interpret.md, and code (ReadBack, Qualifiers)"),
    "context-card": ("shared file", "context-interpret.md, and code (ReadBack, Qualifiers)"),
}


def fix_location(audience: str, kind: str, dimension: str | None) -> tuple[str, str]:
    """Where a weak row is fixed, by the design's §1 table: (category, place)."""
    if audience == "founder":
        if kind in _FOUNDER_FILES:
            return _FOUNDER_FILES[kind]
        if kind in ("q", "answer", "check", "choose") and dimension:
            return ("registry row", f"{dimension}'s founder guidance (else founder-lists.md, shared: every "
                                    "dimension re-read)")
        return ("no model", "the page's own words (keel-web / keel-cloud code)")
    if kind in ("screener", "gate"):
        return ("shared file", "respondent-questions.md (the story clause, the screener question)")
    if kind in ("reveal", "idea"):
        return ("shared file", "solution-mechanism.md (the idea card)")
    if kind == "follow_up":
        return ("registry row", "the follow-up ladder (registry data; code writes the words)")
    if dimension in ("solution.compatibility", "solution.adoption_friction"):
        return ("shared file", f"asked.md (the clause), else {dimension}'s respondent wording")
    if dimension:
        return ("registry row", f"{dimension}'s respondent wording, else the code transform (no model)")
    return ("code transform", "the respondent page's code")


# ------------------------------------------------------------------------------------------------ rows

def rows(latest: dict) -> list[dict]:
    """One row per (scope, dimension, audience, kind) over the latest file of each (entry, scope) -- refused across
    rubric versions."""
    files = list(latest.values())
    rubric.aggregate(files)                                     # refuses a mix of rubric versions
    grouped: dict = {}
    for f in files:
        for s in f["screens"]:
            key = (scope_of(f), s.get("dimension") or "-", s["audience"], s["kind"])
            grouped.setdefault(key, []).append((f["entry"], s))
    out = []
    for (scope, dimension, audience, kind), pairs in sorted(
            grouped.items(), key=lambda kv: (kv[0][0], kv[0][2], kv[0][1], kv[0][3])):
        scores = [s for _, s in pairs]
        stats = rubric.summary(scores)
        zero_entries = {c: sorted({e for e, s in pairs if s.get(c) == 0}) for c in rubric.CRITERIA}
        weak_on = [c for c in rubric.CRITERIA
                   if len(zero_entries[c]) >= rubric.WEAK_ZERO_ENTRIES
                   or (stats["means"][c] is not None and stats["means"][c] < rubric.WEAK_MEAN)]
        category, place = fix_location(audience, kind, None if dimension == "-" else dimension)
        out.append({"scope": scope, "dimension": dimension, "audience": audience, "kind": kind, "screens": len(scores),
                    "entries": sorted({e for e, _ in pairs}), "means": stats["means"], "zeros": stats["zeros"],
                    "zero_entries": zero_entries, "score_pct": stats["score_pct"], "weak": bool(weak_on),
                    "weak_on": weak_on, "fix": {"category": category, "place": place},
                    "instead": [f"{e}: {s['instead']}" for e, s in pairs if s.get("instead")]})
    out += insight_rows(files)
    return out


def insight_rows(files: list[dict]) -> list[dict]:
    """§G: one row per (scope, dimension) under the *insights* kind -- G1 and G2's means, the 0s, the weak rule."""
    grouped: dict = {}
    for f in files:
        for reading in f.get("insights") or []:
            grouped.setdefault((scope_of(f), reading.get("dimension") or "-"), []).append((f["entry"], reading))
    out = []
    for (scope, dimension), pairs in sorted(grouped.items()):
        readings = [r for _, r in pairs]
        means = {c: round(sum(r[c] for r in readings) / len(readings), 3) for c in rubric.G_CRITERIA}
        zeros = {c: sum(1 for r in readings if r[c] == 0) for c in rubric.G_CRITERIA}
        zero_entries = {c: sorted({e for e, r in pairs if r[c] == 0}) for c in rubric.G_CRITERIA}
        weak_on = [c for c in rubric.G_CRITERIA
                   if len(zero_entries[c]) >= rubric.WEAK_ZERO_ENTRIES or means[c] < rubric.WEAK_MEAN]
        total = sum(r[c] for r in readings for c in rubric.G_CRITERIA)
        out.append({"scope": scope, "dimension": dimension, "audience": "respondent", "kind": "insights",
                    "screens": len(readings), "entries": sorted({e for e, _ in pairs}), "means": means,
                    "zeros": zeros, "zero_entries": zero_entries,
                    "score_pct": round(100.0 * total / (2 * len(readings) * len(rubric.G_CRITERIA)), 1),
                    "weak": bool(weak_on), "weak_on": weak_on,
                    "fix": {"category": "shared file", "place": "the THEMES grouping instruction (themes.md)"},
                    "instead": [f"{e}: G1 {r['whys'].get('g1', '')} / G2 {r['whys'].get('g2', '')}"
                                for e, r in pairs if 0 in (r["g1"], r["g2"])]})
    return out


def row_key(row: dict) -> str:
    return f"{row['scope']} · {row['audience']} · {row['dimension']} · {row['kind']}"


def head(latest: dict) -> dict:
    """The overall score_pct over the latest files (the insight readings folded in, §G), per audience and per scope,
    against the bar."""
    files = list(latest.values())
    screens, readings = rubric.aggregate(files), rubric.aggregate_insights(files)
    sums = rubric.summaries(screens, readings)
    overall = sums["overall"]["score_pct"]
    scopes = {}
    for f in files:
        bucket = scopes.setdefault(scope_of(f), ([], []))
        bucket[0].extend(f["screens"])
        bucket[1].extend(f.get("insights") or [])
    return {"entries": len(latest), "summary": sums, "score_pct": overall, "bar_pct": rubric.BAR_PCT,
            "meets_bar": overall is not None and overall >= rubric.BAR_PCT,
            "by_scope": {scope: rubric.summary(sc, ins) for scope, (sc, ins) in sorted(scopes.items())}}


# ------------------------------------------------------------------------------------------- rendering

def _num(value, digits=2) -> str:
    return "–" if value is None else f"{value:.{digits}f}"


def _arrow(now, before) -> str:
    if now is None or before is None:
        return ""
    return " ↑" if now > before + 1e-9 else " ↓" if now < before - 1e-9 else " ="


def _cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def render(files: list[dict], *, comparison: dict | None = None) -> str:
    current, aside = split_by_version(files)
    latest = latest_per_entry(current)
    lines = ["# The question-quality table", "",
             f"Built by `make read-table` from `quality/scores/` (spec 078 FR-5) at RUBRIC_VERSION "
             f"{rubric.RUBRIC_VERSION}. Regenerated and committed with every score file; never edited by hand.", ""]
    if not latest:
        lines += ["**No score file yet at this rubric version.** The bar is **90%** (the overall score_pct over the "
                  "latest file of every entry) before the remaining entries are walked.", ""]
    else:
        top = head(latest)
        by = top["summary"]
        verdict = "meets the bar" if top["meets_bar"] else "is BELOW the bar"
        lines += [f"**Overall score_pct {_num(top['score_pct'], 1)}%** over the latest file of each of "
                  f"{top['entries']} studies (entry · scope) -- {verdict} of **{rubric.BAR_PCT:.0f}%** the founder named before the "
                  "remaining entries are walked.", "",
                  f"- founder: score_pct {_num(by['founder']['score_pct'], 1)}%, flagged "
                  f"{_num(by['founder']['flagged_pct'], 1)}% of {by['founder']['screens']} screens",
                  f"- respondent: score_pct {_num(by['respondent']['score_pct'], 1)}%, flagged "
                  f"{_num(by['respondent']['flagged_pct'], 1)}% of {by['respondent']['screens']} screens",
                  *[f"- scope {scope}: score_pct {_num(sc['score_pct'], 1)}%, flagged {_num(sc['flagged_pct'], 1)}% "
                    f"of {sc['screens']} screens" for scope, sc in top["by_scope"].items()],
                  f"- studies: {', '.join(f'{e} ({Path(f['_path']).name})' for e, f in latest.items())}", ""]
    if aside:
        lines += ["Set aside (another rubric version, never averaged): "
                  + ", ".join(Path(f["_path"]).name for f in aside), ""]
    table = rows(latest) if latest else []
    weak = [r for r in table if r["weak"]]
    lines += ["## The rows", "",
              "Weak = a 0 on one criterion in two or more entries, or a mean under 1.5 (RUBRIC.md). "
              f"{len(weak)} of {len(table)} rows are weak.", "",
              "| | scope | audience | dimension | kind | n | R1 | R2 | R3 | R4 | R5 | 0s | entries with a 0 | fix |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in [r for r in table if r["kind"] != "insights"]:
        zeros = sum(r["zeros"].values())
        with_zero = sorted({e for c in rubric.CRITERIA for e in r["zero_entries"][c]})
        lines.append("| " + " | ".join([
            "**WEAK**" if r["weak"] else "", r["scope"], r["audience"], _cell(r["dimension"]), r["kind"], str(r["screens"]),
            *[_num(r["means"][c]) for c in rubric.CRITERIA], str(zeros), ", ".join(with_zero),
            _cell(f"{r['fix']['category']}: {r['fix']['place']}")]) + " |")
    grouped = [r for r in table if r["kind"] == "insights"]
    lines += ["", "## Insights -- the grouping of the follow-up lines (§G)", ""]
    if not grouped:
        lines.append("No grouping read yet (a study with no follow-up line of two answers records *no grouping to "
                     "read*, and is not penalised).")
    else:
        lines += ["| | scope | dimension | kind | lines | G1 | G2 | insights % | 0s | entries with a 0 | fix |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in grouped:
            with_zero = sorted({e for c in rubric.G_CRITERIA for e in r["zero_entries"][c]})
            lines.append("| " + " | ".join([
                "**WEAK**" if r["weak"] else "", r["scope"], _cell(r["dimension"]), "insights", str(r["screens"]),
                *[_num(r["means"][c]) for c in rubric.G_CRITERIA], _num(r["score_pct"], 1),
                str(sum(r["zeros"].values())), ", ".join(with_zero),
                _cell(f"{r['fix']['category']}: {r['fix']['place']}")]) + " |")
    if weak:
        lines += ["", "## The weak rows, with their *instead* lines", ""]
        for r in weak:
            lines.append(f"### {row_key(r)} -- weak on {', '.join(c.upper() for c in r['weak_on'])}")
            lines.append(f"Fix: **{r['fix']['category']}** -- {r['fix']['place']}.")
            lines += [f"- {_cell(line)}" for line in r["instead"]] or ["- (no instead line)"]
            lines.append("")
    lines += ["", "## The trend per study (entry · scope; the last three score files)", "",
              "| study | file | scored | cloud | founder % | respondent % | overall % | flagged % | R1 | R2 | R3 | R4 "
              "| R5 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for entry, runs in history_per_entry(current).items():
        before = None
        for f in runs:
            s = f["summary"]
            now = {"founder": s["founder"]["score_pct"], "respondent": s["respondent"]["score_pct"],
                   "overall": s["overall"]["score_pct"], "flagged": s["overall"]["flagged_pct"],
                   **{c: s["overall"]["means"][c] for c in rubric.CRITERIA}}
            cells = [entry, Path(f["_path"]).name, (f.get("scored_at") or "")[:10], str(f.get("cloud_sha") or "")[:7]]
            for key, digits in (("founder", 1), ("respondent", 1), ("overall", 1), ("flagged", 1),
                                *((c, 2) for c in rubric.CRITERIA)):
                arrow = _arrow(now[key], before[key]) if before else ""     # flagged: ↓ is the good direction
                cells.append(_num(now[key], digits) + arrow)
            lines.append("| " + " | ".join(cells) + " |")
            before = now
    if comparison:
        lines += ["", "## Against the baseline", "", f"**Verdict: {comparison['verdict'].upper()}** -- "
                  f"{comparison['why']}", "",
                  f"Baseline: {comparison['baseline']['cut']} ({comparison['baseline']['score_pct']}%), now "
                  f"{comparison['score_pct']}%.", "",
                  "| row | ΔR1 / ΔG1 | ΔR2 / ΔG2 | ΔR3 | ΔR4 | ΔR5 | weak then | weak now |",
                  "|---|---|---|---|---|---|---|---|"]
        for d in comparison["rows"]:
            deltas = list(d["delta"].values()) + [None] * (5 - len(d["delta"]))
            lines.append("| " + " | ".join([_cell(d["row"]), *[_num(v) for v in deltas],
                                             "yes" if d["weak_then"] else "", "yes" if d["weak_now"] else ""]) + " |")
    return "\n".join(lines).rstrip() + "\n"


# ------------------------------------------------------------------------------------------- the baseline

def baseline_data(latest: dict, *, cut: str) -> dict:
    top = head(latest)
    return {"cut": cut, "rubric_version": rubric.RUBRIC_VERSION, "score_pct": top["score_pct"],
            "files": [Path(f["_path"]).name for f in latest.values()],
            "studies": list(latest), "cloud_shas": sorted({str(f.get("cloud_sha")) for f in latest.values()}),
            "routing_versions": sorted({str(f.get("routing_version")) for f in latest.values()}),
            "readers": sorted({f"{f['reader']['model']} ({f['reader']['effort']})" for f in latest.values()}),
            "rows": {row_key(r): {"means": r["means"], "weak": r["weak"]} for r in rows(latest)}}


def render_baseline(data: dict) -> str:
    lines = ["# The baseline", "",
             f"Cut {data['cut']} on the founder's word (spec 078 FR-6). Every later run is compared with it by "
             "`make read-table BASELINE=1`; a new baseline is cut only on his word, and this file is then kept under "
             "`quality/baselines/<date>.md`.", "",
             f"- RUBRIC_VERSION {data['rubric_version']}; overall score_pct {data['score_pct']}%",
             f"- studies (entry · scope): {', '.join(data['studies'])}",
             f"- score files: {', '.join(data['files'])}",
             f"- cloud sha(s): {', '.join(data['cloud_shas'])}; routing version(s): {', '.join(data['routing_versions'])}",
             f"- reader(s): {', '.join(data['readers'])}", "",
             "| row | R1 / G1 | R2 / G2 | R3 | R4 | R5 | weak |", "|---|---|---|---|---|---|---|"]
    for key, row in data["rows"].items():
        means = list(row["means"].values()) + [None] * (5 - len(row["means"]))
        lines.append("| " + " | ".join([_cell(key), *[_num(v) for v in means],
                                         "yes" if row["weak"] else ""]) + " |")
    lines += ["", _DATA_BEGIN, "```json", json.dumps(data, indent=1, ensure_ascii=False), "```", ""]
    return "\n".join(lines)


def read_baseline(path: Path | None = None) -> dict:
    path = Path(path or BASELINE_PATH)
    if not path.is_file():
        raise TableRefused("make read-table BASELINE=1 refuses: no baseline is cut yet (quality/BASELINE.md) -- it "
                           "is cut once, on the founder's word (spec 078 FR-6)")
    text = path.read_text(encoding="utf-8")
    match = re.search(re.escape(_DATA_BEGIN) + r"\s*```json\s*(.*?)```", text, re.S)
    if not match:
        raise TableRefused(f"{path} carries no baseline data block")
    data = json.loads(match.group(1))
    if data.get("rubric_version") != rubric.RUBRIC_VERSION:
        raise TableRefused(f"make read-table BASELINE=1 refuses: the baseline is at rubric version "
                           f"{data.get('rubric_version')} and the scores at {rubric.RUBRIC_VERSION} -- two rubric "
                           "versions are never compared (spec 078 FR-1)")
    return data


def compare(baseline: dict, latest: dict) -> dict:
    """Each row's deltas against the baseline and the verdict (RUBRIC.md, *The verdict against the baseline*)."""
    if baseline.get("rubric_version") != rubric.RUBRIC_VERSION:
        raise rubric.RubricMismatch("a baseline at another rubric version is never compared")
    studies = baseline.get("studies")
    if studies is not None:                              # like with like: the same entry AND scope only
        latest = {key: f for key, f in latest.items() if key in set(studies)}
        if not latest:
            raise TableRefused("no score file now for any study (entry · scope) the baseline names: "
                               + ", ".join(studies))
    now_rows = {row_key(r): r for r in rows(latest)}
    then_rows = baseline.get("rows") or {}
    diffs, became_weak, stopped_weak = [], [], []
    for key in sorted(set(now_rows) | set(then_rows)):
        now, then = now_rows.get(key), then_rows.get(key)
        crits = list((now or {}).get("means") or (then or {}).get("means") or {})
        delta = {c: (None if not now or not then or now["means"].get(c) is None or then["means"].get(c) is None
                     else round(now["means"][c] - then["means"][c], 3)) for c in crits}
        weak_then, weak_now = bool(then and then["weak"]), bool(now and now["weak"])
        if weak_now and not weak_then:
            became_weak.append(key)
        if weak_then and not weak_now and now:
            stopped_weak.append(key)
        diffs.append({"row": key, "delta": delta, "weak_then": weak_then, "weak_now": weak_now})
    score_now = head(latest)["score_pct"]
    moved = None if score_now is None or baseline.get("score_pct") is None else score_now - baseline["score_pct"]
    if became_weak or (moved is not None and moved <= -SAME_BAND_PCT):
        verdict = "worse"
        why = (f"{len(became_weak)} row(s) became weak ({', '.join(became_weak)})" if became_weak
               else f"the overall score_pct fell by {abs(moved):.1f} points")
    elif stopped_weak or (moved is not None and moved >= SAME_BAND_PCT):
        verdict = "better"
        why = (f"{len(stopped_weak)} weak row(s) are no longer weak ({', '.join(stopped_weak)})" if stopped_weak
               else f"the overall score_pct rose by {moved:.1f} points") + "; no row became weak"
    else:
        verdict = "same"
        why = "no row changed weak, and the overall score_pct moved by less than a point"
    return {"verdict": verdict, "why": why, "rows": diffs, "score_pct": score_now,
            "baseline": {"cut": baseline.get("cut"), "score_pct": baseline.get("score_pct")}}


def cut_baseline(files: list[dict], entries: list[str] | None, *, path: Path | None = None,
                 archive_dir: Path | None = None, today: str | None = None) -> Path:
    path = Path(path or BASELINE_PATH)
    current, _ = split_by_version(files)
    latest = latest_per_entry(current)
    if entries:
        picked = {key: f for key, f in latest.items() if f["entry"] in entries or key in entries}
        missing = [e for e in entries if not any(f["entry"] == e or key == e for key, f in picked.items())]
        if missing:
            raise TableRefused(f"no score file at rubric version {rubric.RUBRIC_VERSION} for {missing}")
        latest = picked
    if not latest:
        raise TableRefused("no score file to cut a baseline from")
    today = today or dt.date.today().isoformat()
    if path.is_file():
        archive = Path(archive_dir or BASELINES_DIR)
        archive.mkdir(parents=True, exist_ok=True)
        old = re.search(r'"cut": "([^"]+)"', path.read_text(encoding="utf-8"))
        (archive / f"{old.group(1) if old else today}.md").write_text(path.read_text(encoding="utf-8"),
                                                                      encoding="utf-8")
    path.write_text(render_baseline(baseline_data(latest, cut=today)), encoding="utf-8")
    return path


# ------------------------------------------------------------------------------------------------ main

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="quality.table", description=__doc__.split("\n\n")[0])
    parser.add_argument("--baseline", action="store_true", help="compare with quality/BASELINE.md")
    parser.add_argument("--cut-baseline", default=None, metavar="ENTRIES",
                        help="write BASELINE.md from the latest files of these entries (comma-separated; 'all') -- "
                             "on the founder's word only")
    parser.add_argument("--scores-dir", default=str(SCORES_DIR))
    parser.add_argument("--out", default=str(TABLE_PATH))
    args = parser.parse_args(argv)
    try:
        files = load_scores(Path(args.scores_dir))
        if args.cut_baseline:
            entries = None if args.cut_baseline == "all" else [e for e in args.cut_baseline.split(",") if e]
            print(f"baseline cut: {cut_baseline(files, entries)}")
        comparison = None
        if args.baseline:
            current, _ = split_by_version(files)
            comparison = compare(read_baseline(), latest_per_entry(current))
        Path(args.out).write_text(render(files, comparison=comparison), encoding="utf-8")
    except (TableRefused, rubric.RubricError) as reason:
        print(str(reason), file=sys.stderr)
        return 2
    current, _ = split_by_version(files)
    latest = latest_per_entry(current)
    top = head(latest) if latest else None
    print(f"table: {args.out} ({len(latest)} studies"
          + (f", overall score_pct {top['score_pct']}% against the bar of {rubric.BAR_PCT:.0f}%" if top else "")
          + ")")
    if comparison:
        print(f"against the baseline: {comparison['verdict'].upper()} -- {comparison['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
