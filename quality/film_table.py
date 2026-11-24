"""The film table and the gate (spec 163 FR-4, FR-8): `make read-film-table RUN=<bundle> [DRIFT=1]` -- free.

One row per entry of the bundle: the film's criteria (F1..F8; S1..S9 on a solution film), `film_pct`, flagged, the
dollars, **beside the same entry's question score (`score_pct` over the §A screens) and its founder's-page score (§B,
`after_pct`) from `make read-screens` on the same bundle**, and `founder_pct` (the founder's beats); the mean over the
entries; the bar (`quality/cycle.toml` `[film] film_bar_pct`, 80); the weak criteria (`quality/FILM-RUBRIC.md`'s weak
rule); each entry's whys in one line a criterion and its frames linked (the report's *The film, judged*, FR-8); and the
findings a cloud or web spec owes (a picture with text, a caption clipped, a limitation with no scene, a setting that
names a company, a scene served with no picture), in `runs/DRIFT.md`'s shape -- appended there with `DRIFT=1`.

It writes `quality/FILM-TABLE.md` (rewritten) and the record `quality/cycles/<yyyymmdd>-<cloud7>-film.md`. An entry
passes at `film_pct` >= the bar with no 0; a round passes when every entry does -- and a round whose holdout entries
(`[film] holdout`) fall short fails whatever the others did (`quality/decisions.toml`'s rule, *rules not cases*).
Film score files of two `FILM_RUBRIC_VERSION`s are never tabled together.
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


def backtests_of(run: str | Path) -> dict:
    """The walk's record (`walk.json`, `make film-walk`): each entry's back-test bundle, by entry -- `{}` where the
    bundle has none (a free walk, or a bundle written by hand)."""
    path = Path(run) / "walk.json"
    if not path.is_file():
        return {}
    record = json.loads(path.read_text(encoding="utf-8"))
    return {r["entry"]: r["backtest"] for r in record.get("entries") or [] if r.get("backtest")}


def question_scores(bundle: str, scores_dir: Path | None = None, backtests: dict | None = None) -> dict:
    """The same walk's `make read-screens` score files (`quality/scores/<entry>/*.json` whose `bundle` is the entry's
    back-test bundle as `walk.json` names it, else this bundle), by entry: `qa_pct` -- the score over the §A screens
    (every R, and the §G readings) -- and `after_pct` -- §B, the founder's page after the answers (spec 109) -- with the
    file's path and dollars."""
    out = {}
    wanted = set((backtests or {}).values()) | {bundle}
    for path in sorted(Path(scores_dir or SCORES_DIR).glob("*/*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if obj.get("bundle") not in wanted or obj.get("partial"):
            continue
        screens = obj.get("screens") or []
        qa = rubric.summary([s for s in screens if not rubric.is_after(s.get("kind"))], obj.get("insights") or [])
        after = (obj.get("summary") or {}).get("overall", {}).get("after_pct")
        out[obj.get("entry")] = {"qa_pct": qa.get("score_pct"), "after_pct": after, "path": str(path),
                                 "cost_usd": obj.get("cost_usd"), "rubric_version": obj.get("rubric_version")}
    return out


# ------------------------------------------------------------------------------------------------ the rows

def rows(files: list[dict], questions: dict, bar: float, holdout: list[str]) -> list[dict]:
    out = []
    for f in sorted(files, key=lambda x: x["entry"]):
        film = f["film"]
        q = questions.get(f["entry"]) or {}
        out.append({"entry": f["entry"], "kind": film["kind"], "scores": film["scores"], "film_pct": film["film_pct"],
                    "flagged": film["flagged"], "founder_pct": (f.get("founder") or {}).get("founder_pct"),
                    "qa_pct": q.get("qa_pct"), "after_pct": q.get("after_pct"),
                    "usd": f.get("cost_usd"), "walk_usd": f.get("walk_usd"),
                    "passes": fr.passes(film, bar), "holdout": f["entry"] in holdout, "file": f["_path"],
                    "whys": film["whys"], "instead": film["instead"], "missing": film["missing"],
                    "frames": f.get("frames") or {}, "measures": f.get("measures"),
                    "cloud_sha": f.get("cloud_sha"), "web_sha": f.get("web_sha")})
    return out


def verdict(table: list[dict], holdout: list[str]) -> dict:
    """FR-4 / FR-5: the round passes when every entry passes; a tabled holdout entry that fails fails the round by name
    (the five passing does not carry it)."""
    failed = [r["entry"] for r in table if not r["passes"]]
    held = [r["entry"] for r in table if r["holdout"]]
    held_failed = [e for e in failed if e in holdout]
    pct = [r["film_pct"] for r in table if r["film_pct"] is not None]
    return {"entries": len(table), "passed": len(table) - len(failed), "failed": failed,
            "holdout_tabled": held, "holdout_failed": held_failed,
            "mean_film_pct": round(sum(pct) / len(pct), 1) if pct else None,
            "round_passes": bool(table) and not failed}


def _cell(value) -> str:
    if value is None:
        return "--"
    return f"{value:.1f}" if isinstance(value, float) else str(value)


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
}


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
                out.append({"entry": r["entry"], "criterion": crit.upper(), "what": what, "owed": owed,
                            "why": r["whys"].get(crit, ""), "instead": r["instead"].get(crit, ""),
                            "missing": r["missing"] if crit in ("f4", "s4") else [],
                            "frames": [f"{folder}/{p}" for p in frames[:2]], "cloud": r["cloud_sha"],
                            "web": r["web_sha"]})
        for m in (r.get("measures") or {}).get("faults") or []:
            out.append({"entry": r["entry"], "criterion": "capture", "what": m.get("what", ""), "owed": m.get("owed", ""),
                        "why": m.get("detail", ""), "instead": "", "missing": [],
                        "frames": [f"{folder}/{m['frame']}"] if m.get("frame") else [], "cloud": r["cloud_sha"],
                        "web": r["web_sha"]})
    return out


def drift_text(found: list[dict], *, start: int, bundle: str) -> str:
    blocks = []
    for i, f in enumerate(found, start):
        frames = ", ".join(f"`{p}`" for p in f["frames"]) or "(no frame)"
        missing = (" Not shown: " + "; ".join(f["missing"]) + ".") if f["missing"] else ""
        blocks.append(
            f"## {i}. Observation (the film, {f['entry']}): {f['what']}\n\n"
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
           found: list[dict]) -> str:
    v = verdict(table, cfg["holdout"])
    kinds = sorted({r["kind"] for r in table}) or ["problem"]
    names = [c for k in kinds for c in fr.KINDS[k]]
    reader = (files[0].get("reader") if files else None) or {}
    founder_reader = (files[0].get("founder_reader") if files else None) or {}
    usd = sum(r["usd"] or 0 for r in table)
    walk = sum(r["walk_usd"] or 0 for r in table if isinstance(r["walk_usd"], (int, float)))
    lines = [
        "# The film, judged",
        "",
        f"Bundle `{bundle}` · FILM_RUBRIC_VERSION {fr.FILM_RUBRIC_VERSION} · the film reader "
        f"{reader.get('model', '--')} {reader.get('effort', '')} ({reader.get('door', '--')}) · the founder-reader "
        f"{founder_reader.get('model', '--')} {founder_reader.get('effort', '')} ({founder_reader.get('door', '--')}) · "
        f"the bar {cfg['film_bar_pct']:.0f}% (`quality/cycle.toml` [film] film_bar_pct) · spec 163.",
        "",
        f"**This round**: mean film_pct {_cell(v['mean_film_pct'])} over {v['entries']} entr"
        f"{'y' if v['entries'] == 1 else 'ies'}; {v['passed']} pass, {len(v['failed'])} fall short"
        + (f" ({', '.join(v['failed'])})" if v["failed"] else "") + "; the round "
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
        "| entry | " + " | ".join(c.upper() for c in names) + " | film_pct | flagged | founder_pct | §A score_pct | "
        "§B after_pct | $ | passes |",
        "|---|" + "---|" * (len(names) + 7),
    ]
    for r in table:
        cells = [_cell(r["scores"].get(c)) for c in names]
        lines.append(f"| {r['entry']}{' (holdout)' if r['holdout'] else ''} | " + " | ".join(cells)
                     + f" | {_cell(r['film_pct'])} | {'yes' if r['flagged'] else 'no'} | {_cell(r['founder_pct'])} | "
                     f"{_cell(r['qa_pct'])} | {_cell(r['after_pct'])} | {_cell(r['usd'])} | "
                     f"{'yes' if r['passes'] else 'no'} |")
    lines += ["", "§A and §B are `make read-screens` on the same bundle (RUBRIC.md: the respondent's and the founder's "
                  "screens, and the founder's page after the answers -- the Overview's cards, the Insights tab, the "
                  "brief); `--` where it has not been read. The solution film's column joins once the solution batch "
                  "is walked.", "", "## Weak criteria", ""]
    if weak:
        for w in weak:
            lines.append(f"- **{w['criterion'].upper()}** ({w['kind']}): mean {w['mean']:.2f}, a 0 in {w['zeros']} "
                         f"entr{'y' if w['zeros'] == 1 else 'ies'}" + (f" ({', '.join(w['zero_entries'])})"
                                                                         if w["zero_entries"] else "")
                         + " -- `make film-advise` proposes a rule for it.")
    else:
        lines.append("None (no criterion with a 0 in two entries or more, none with a mean under 1.5).")
    lines += ["", "## Each entry's whys", ""]
    for r in table:
        folder = (r.get("frames") or {}).get("folder") or ""
        frames = (r.get("frames") or {}).get("frames") or []
        lines.append(f"### {r['entry']} -- film_pct {_cell(r['film_pct'])}{', flagged' if r['flagged'] else ''}")
        lines.append("")
        for c in fr.KINDS[r["kind"]]:
            extra = f" -- *instead*: {_flat(r['instead'][c])}" if c in r["instead"] else ""
            lines.append(f"- {c.upper()} {r['scores'][c]}: {_flat(r['whys'].get(c))}{extra}")
        if r["missing"]:
            lines.append(f"- missing: {'; '.join(_flat(m) for m in r['missing'])}")
        if frames:
            lines.append("- frames: " + ", ".join(f"[{Path(p).name}]({folder}/{p})" for p in frames))
        lines.append("")
    lines += ["## Findings for DRIFT", ""]
    if found:
        for f in found:
            lines.append(f"- {f['entry']} ({f['criterion']}): {f['what']} -- {', '.join(f['frames']) or 'no frame'}")
        lines.append("")
        lines.append("`make read-film-table RUN=... DRIFT=1` appends them to `runs/DRIFT.md` in its shape.")
    else:
        lines.append("None.")
    lines.append("")
    return "\n".join(lines)


def record_name(files: list[dict]) -> str:
    sha = str((files[0].get("cloud_sha") if files else None) or "nosha")[:7]
    day = str((files[0].get("scored_at") if files else "") or "")[:10].replace("-", "") or "00000000"
    return f"{day}-{sha}-film.md"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="quality.film_table", description=__doc__.split("\n\n")[0])
    parser.add_argument("--run", default="")
    parser.add_argument("--scores-dir", default=str(SCORES_DIR))
    parser.add_argument("--table", default=str(TABLE_PATH))
    parser.add_argument("--cycles-dir", default=str(CYCLES_DIR))
    parser.add_argument("--cycle-toml", default=str(CYCLE_TOML))
    parser.add_argument("--drift", action="store_true")
    parser.add_argument("--drift-path", default=str(DRIFT_PATH))
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
    table = rows(files, question_scores(bundle, Path(args.scores_dir), backtests_of(resolve_run(args.run))),
                 cfg["film_bar_pct"], cfg["holdout"])
    weak = fr.weak_criteria(files)
    found = findings(table)
    text = render(table, files, weak, cfg, bundle=bundle, found=found)
    Path(args.table).write_text(text, encoding="utf-8")
    record = Path(args.cycles_dir) / record_name(files)
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(text, encoding="utf-8")
    if args.drift and found:
        path = Path(args.drift_path)
        start = next_drift_number(path)
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\n" + drift_text(found, start=start, bundle=bundle))
        print(f"{len(found)} finding(s) appended to {path} as #{start}..#{start + len(found) - 1}")
    v = verdict(table, cfg["holdout"])
    print(f"{v['entries']} entries, mean film_pct {v['mean_film_pct']}, {v['passed']} pass; the round "
          f"{'passes' if v['round_passes'] else 'fails'}; {len(weak)} weak criteria; {len(found)} DRIFT finding(s)")
    print(f"wrote {args.table} and {record}")
    print(f"git add {args.table} {record} " + " ".join(f["_path"] for f in files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
