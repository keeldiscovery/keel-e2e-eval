"""Spec 074 FR-3: the noise-capture check's report and its certificate -- the canon's `report.py` (keel-cloud
`canon/designs/noise-capture-check-2026-10-26/`) moved here for Keel's path alone, with the founder's bar in it.

`write(run_dir)` reads `results.jsonl` and writes beside it:

* `summary.json` -- the canon's aggregates (`agg`: by level, room, bed, control, control at level, tag) and the
  certificate;
* `noise-check.md` -- the certificate line, the canon page's **rooms** table (closed answers right per bed and level,
  confident wrong, stories' meaning kept) and **controls** table, then every miss with its transcript;
* `page/index.html` -- the evidence page from `page_template.html`, its clips copied from the samples where present;
* `register-row.md` -- the run's row for the register (`runs/noise-check-register.md`, appended, kept with the runs).

**The certificate** (the founder's bar, 2026-10-26): the quiet room -- closed answers right **100%**; every bed at 20,
10 and 5 dB -- closed answers right **> 90%**; confident-wrong **<= 2%** and stories' meaning kept **>= 90%** in each of
those cells (the quiet room's included). PASS, or FAIL with the first failing cell named, in the order quiet, then
each bed at 20, 10, 5 dB. A gated cell with no rows (a partial run: `--only`, `--snrs`, `--limit`) is INCOMPLETE,
never PASS. Every 0 dB cell -- the café at 0 dB the stress case -- is reported in the same tables, outside the bar.
"""

from __future__ import annotations

import json
import shutil
import statistics as st
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from evals.noise.dataset import BEDS, ITEMS, SNRS, UTTERANCES, voices_for

HERE = Path(__file__).resolve().parent
RESULTS = "results.jsonl"
SUMMARY = "summary.json"
MARKDOWN = "noise-check.md"
REGISTER_ROW = "register-row.md"
REGISTER = "noise-check-register.md"

#: The founder's bar (2026-10-26).
QUIET_CLOSED_OK = 100.0
LOUD_CLOSED_OK_ABOVE = 90.0
CONFIDENT_WRONG_AT_MOST = 2.0
MEANING_KEPT_AT_LEAST = 90.0
GATED_SNRS = (20, 10, 5)
STRESS_SNR = 0

ENV_LABEL = {"construction": "Construction site", "traffic": "Busy road", "cafe": "Café, people talking",
             "music": "Music playing", "wind": "Wind outdoors", "clean": "Quiet room"}
CONTROLS = ["yes/no", "number", "radio", "checkbox", "free text"]
PASS_KEY = "stt-none"
PASS_LABEL = "Keel's path: transcribe, then classify"


def load(run_dir: Path) -> list[dict]:
    """The run's rows, one a sample id (the first kept, as the canon's `load`)."""
    seen: dict = {}
    path = Path(run_dir) / RESULTS
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                seen.setdefault(r["id"], r)
    return list(seen.values())


def env_of(r: dict) -> str:
    return "clean" if r["bed"] == "clean" else f"{r['bed']}@{r['snr']}"


def level_of(r: dict):
    return "clean" if r["snr"] is None else r["snr"]


def pct(a, b):
    return None if not b else round(100 * a / b, 1)


def agg(rows: list[dict], key) -> dict:
    """The canon's aggregate per group: closed answers right, confident wrong, asked again; stories' meaning kept and
    WER; median latency, mean cost."""
    g: dict = {}
    for r in rows:
        g.setdefault(key(r), []).append(r)
    out = {}
    for k, rs in g.items():
        closed = [r for r in rs if r["control"] != "free text"]
        free = [r for r in rs if r["control"] == "free text"]
        out[str(k)] = {
            "n": len(rs), "ok": pct(sum(bool(r["ok"]) for r in rs), len(rs)),
            "closed_n": len(closed), "closed_ok": pct(sum(bool(r["ok"]) for r in closed), len(closed)),
            "false_support": pct(sum(bool(r.get("false_support")) for r in closed), len(closed)),
            "unclear": pct(sum(1 for r in closed if (r.get("got") or {}).get("unclear")), len(closed)),
            "free_n": len(free), "meaning_kept": pct(sum(bool(r["ok"]) for r in free), len(free)),
            "wer": round(100 * st.mean(r["wer"] for r in free), 1) if free else None,
            "latency_ms": int(st.median([r["latency_ms"] for r in rs if "latency_ms" in r]))
            if any("latency_ms" in r for r in rs) else None,
            "cost_usd": round(st.mean((r.get("cost_usd") or 0) for r in rs), 5)}
    return out


def summarize(rows: list[dict]) -> dict:
    return {"n": len(rows), "all": agg(rows, lambda r: "all").get("all", {}),
            "by_level": agg(rows, level_of), "by_env": agg(rows, env_of), "by_bed": agg(rows, lambda r: r["bed"]),
            "by_control": agg(rows, lambda r: r["control"]),
            "by_control_level": agg(rows, lambda r: f"{r['control']}@{level_of(r)}"),
            "by_tag": agg(rows, lambda r: r["tag"]),
            "cost_usd": round(sum((r.get("cost_usd") or 0) for r in rows), 4),
            "cut": sum(1 for r in rows if r.get("cut"))}


# ------------------------------------------------------------------------------------------ the certificate

def gated_cells() -> list[str]:
    """The bar's cells, in the order the first failing one is named: the quiet room, then each bed at 20, 10, 5 dB."""
    return ["clean"] + [f"{b}@{snr}" for b in BEDS for snr in GATED_SNRS]


def _cell_faults(cell: str, a: dict | None) -> list[str]:
    if not a or not a.get("n"):
        return ["not measured"]
    faults = []
    closed = a.get("closed_ok")
    if a.get("closed_n"):
        if cell == "clean" and closed < QUIET_CLOSED_OK:
            faults.append(f"closed answers right {closed}% < {QUIET_CLOSED_OK:g}%")
        if cell != "clean" and not closed > LOUD_CLOSED_OK_ABOVE:
            faults.append(f"closed answers right {closed}% not > {LOUD_CLOSED_OK_ABOVE:g}%")
        if a.get("false_support") is not None and a["false_support"] > CONFIDENT_WRONG_AT_MOST:
            faults.append(f"confident wrong {a['false_support']}% > {CONFIDENT_WRONG_AT_MOST:g}%")
    if a.get("free_n") and a.get("meaning_kept") is not None and a["meaning_kept"] < MEANING_KEPT_AT_LEAST:
        faults.append(f"stories' meaning kept {a['meaning_kept']}% < {MEANING_KEPT_AT_LEAST:g}%")
    return faults


def certificate(rows: list[dict]) -> dict:
    """The founder's bar over the rows: `{verdict, failing, cells, stress, line}`. `verdict` is PASS (every gated cell
    measured and inside the bar), FAIL (the first failing cell named in `failing`) or INCOMPLETE (no measured cell
    fails, some are not measured)."""
    by_env = agg(rows, env_of)
    cells = {}
    for cell in gated_cells():
        a = by_env.get(cell)
        cells[cell] = {"faults": _cell_faults(cell, a), **({k: a.get(k) for k in (
            "n", "closed_n", "closed_ok", "false_support", "free_n", "meaning_kept")} if a else {"n": 0})}
    failing = next((c for c, v in cells.items() if v["faults"] and v["faults"] != ["not measured"]), None)
    unmeasured = [c for c, v in cells.items() if v["faults"] == ["not measured"]]
    stress = {f"{b}@{STRESS_SNR}": {k: (by_env.get(f"{b}@{STRESS_SNR}") or {}).get(k) for k in (
        "n", "closed_ok", "false_support", "meaning_kept")} for b in BEDS}
    if failing:
        verdict = "FAIL"
    elif unmeasured:
        verdict = "INCOMPLETE"
    else:
        verdict = "PASS"
    line = certificate_line(verdict, failing, cells, unmeasured, stress)
    return {"verdict": verdict, "failing": failing, "failing_faults": cells[failing]["faults"] if failing else [],
            "unmeasured": unmeasured, "cells": cells, "stress": stress, "line": line,
            "bar": {"quiet_closed_ok": QUIET_CLOSED_OK, "loud_closed_ok_above": LOUD_CLOSED_OK_ABOVE,
                    "confident_wrong_at_most": CONFIDENT_WRONG_AT_MOST, "meaning_kept_at_least": MEANING_KEPT_AT_LEAST,
                    "gated_snrs": list(GATED_SNRS), "outside_the_bar": STRESS_SNR}}


def _cell_name(cell: str) -> str:
    if cell == "clean":
        return "the quiet room (clean)"
    bed, snr = cell.split("@")
    return f"{ENV_LABEL.get(bed, bed)} at {snr} dB ({cell})"


def certificate_line(verdict: str, failing: str | None, cells: dict, unmeasured: list[str], stress: dict) -> str:
    quiet = cells["clean"]
    worst = min((v.get("closed_ok") for c, v in cells.items() if c != "clean" and v.get("closed_ok") is not None),
                default=None)
    cafe0 = stress.get(f"cafe@{STRESS_SNR}") or {}
    head = (f"Certificate (the founder's bar, 2026-10-26: quiet 100%, every bed at 20/10/5 dB > 90%, confident wrong "
            f"<= 2%, stories >= 90%): {verdict}")
    if verdict == "FAIL":
        head += f" -- the first failing cell is {_cell_name(failing)}: {'; '.join(cells[failing]['faults'])}"
    elif verdict == "INCOMPLETE":
        head += f" -- {len(unmeasured)} of {len(cells)} cells not measured (a partial run certifies nothing)"
    tail = f". Quiet closed {quiet.get('closed_ok')}%"
    if worst is not None:
        tail += f", the worst loud cell {worst}%"
    if cafe0.get("n"):
        tail += f"; the café at 0 dB (outside the bar) {cafe0.get('closed_ok')}% closed, {cafe0.get('false_support')}% " \
                f"confident wrong"
    return head + tail + "."


# --------------------------------------------------------------------------------------------- the files

def _p(v) -> str:
    return "–" if v is None else f"{v:.1f}%"


def markdown(summary: dict, cert: dict, rows: list[dict], *, header: dict | None = None) -> str:
    """The certificate line, the canon page's rooms and controls tables, and the misses with their transcripts."""
    s = summary
    a = s.get("all") or {}
    levels = ["clean"] + SNRS
    w = [f"# Noise-capture check{' -- ' + header['stamp'] if header and header.get('stamp') else ''}", "",
         f"**{cert['line']}**", ""]
    if header:
        w += [f"Samples {header.get('samples')}; keel-cloud {header.get('keel_cloud') or '?'}; selection "
              f"{json.dumps(header.get('selection') or {})}; n={s['n']}; cost ${s.get('cost_usd')}; replies cut at "
              f"max_tokens {s.get('cut', 0)}.", ""]
    w += [f"All levels: closed answers right **{_p(a.get('closed_ok'))}**, confident wrong {_p(a.get('false_support'))}, "
          f"asked again {_p(a.get('unclear'))}; stories' meaning kept **{_p(a.get('meaning_kept'))}**, WER "
          f"{a.get('wer')}%; latency median {a.get('latency_ms')} ms.", "",
          "## The rooms", "",
          "Closed answers right, by room and signal-to-noise; the bar covers quiet and 20 / 10 / 5 dB, the 0 dB column "
          "is reported outside it.", "",
          "| Room | " + " | ".join("quiet" if lv == "clean" else f"{lv} dB" for lv in levels) + " |",
          "|---|" + "---|" * len(levels)]
    for b in BEDS:
        cells = [_p((s["by_level"].get("clean") or {}).get("closed_ok"))]
        cells += [_p((s["by_env"].get(f"{b}@{lv}") or {}).get("closed_ok")) for lv in SNRS]
        w.append(f"| {ENV_LABEL[b]} | " + " | ".join(cells) + " |")
    for label, key in (("**all rooms, closed**", "closed_ok"), ("confident wrong", "false_support"),
                       ("stories, meaning kept", "meaning_kept")):
        w.append(f"| {label} | " + " | ".join(_p((s["by_level"].get(str(lv)) or {}).get(key)) for lv in levels) + " |")
    w += ["", "Per cell, against the bar:", "", "| Cell | n | closed right | confident wrong | stories kept | |",
          "|---|---|---|---|---|---|"]
    for cell, v in cert["cells"].items():
        mark = "ok" if not v["faults"] else ("not measured" if v["faults"] == ["not measured"] else
                                              "**" + "; ".join(v["faults"]) + "**")
        w.append(f"| {cell} | {v.get('n', 0)} | {_p(v.get('closed_ok'))} | {_p(v.get('false_support'))} | "
                 f"{_p(v.get('meaning_kept'))} | {mark} |")
    for cell, v in cert["stress"].items():
        w.append(f"| {cell} (outside the bar) | {v.get('n') or 0} | {_p(v.get('closed_ok'))} | "
                 f"{_p(v.get('false_support'))} | {_p(v.get('meaning_kept'))} | reported |")
    w += ["", "## The controls", "",
          "| Control | " + " | ".join("quiet" if lv == "clean" else f"{lv} dB" for lv in levels) + " | latency |",
          "|---|" + "---|" * (len(levels) + 1)]
    for c in CONTROLS:
        key = "meaning_kept" if c == "free text" else "ok"
        cells = [_p((s["by_control_level"].get(f"{c}@{lv}") or {}).get(key)) for lv in levels]
        w.append(f"| {c} | " + " | ".join(cells) + f" | {(s['by_control'].get(c) or {}).get('latency_ms')} ms |")
    misses = sorted((r for r in rows if not r.get("ok")), key=lambda r: (r["utterance"], r["bed"], -(r["snr"] or 99)))
    w += ["", f"## The misses ({len(misses)})", "", "| Sample | Heard | Read | Expected |", "|---|---|---|---|"]
    for r in misses:
        read = "meaning lost: " + ", ".join(c for c, k in zip(r.get("critical") or [], r.get("critical_kept") or [])
                                            if not k) if r["control"] == "free text" else json.dumps(r.get("got"))
        heard = (r.get("heard") or "").replace("|", "/")
        w.append(f"| {r['id']} | {heard} | {read} | {json.dumps(r['expected'])[:80]} |")
    return "\n".join(w) + "\n"


def register_row(cert: dict, summary: dict, *, stamp: str, keel_cloud: str | None, run_dir: str) -> str:
    """The run's row for the register: when, the build, the verdict and its first failing cell, the quiet room, the
    worst loud cell, the café at 0 dB, n and cost."""
    cells = cert["cells"]
    worst = min(((v.get("closed_ok"), c) for c, v in cells.items() if c != "clean" and v.get("closed_ok") is not None),
                default=(None, None))
    cafe0 = cert["stress"].get(f"cafe@{STRESS_SNR}") or {}
    verdict = cert["verdict"] + (f" ({cert['failing']})" if cert.get("failing") else "")
    return (f"| {stamp} | {keel_cloud or '?'} | {verdict} | {_p(cells['clean'].get('closed_ok'))} | "
            f"{_p(worst[0])} {worst[1] or ''} | {_p(cafe0.get('closed_ok'))} | {summary['n']} | "
            f"${summary.get('cost_usd')} | {run_dir} |")


REGISTER_HEAD = ("# The noise-capture check's register (spec 074 FR-3)\n\nOne row a `make noise-check` run; a row is never "
                 "rewritten.\n\n| Run | keel-cloud | Certificate | Quiet closed | Worst loud cell | Café 0 dB (outside "
                 "the bar) | n | Cost | Folder |\n|---|---|---|---|---|---|---|---|---|\n")


def git_sha(path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "--short=8", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip() or None
    except Exception:  # noqa: BLE001 - not a checkout
        return None


def build_page(run_dir: Path, rows: list[dict], summary: dict, *, root: Path | None) -> Path:
    """The canon's evidence page for this run (`page_template.html`): its data the run's rows on the shown clips, the
    clips copied from the samples where present."""
    page = Path(run_dir) / "page"
    clips = page / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    shown = {u[0]: voices_for(i)[0] for i, u in enumerate(UTTERANCES)}
    levels = [10, 5, 0]
    by_id = {r["id"]: r for r in rows}
    sids = []
    for uid, v in shown.items():
        for env in ["clean"] + [f"{b}-{lv}" for b in BEDS for lv in levels]:
            sid = f"{uid}-{v}-{env}"
            src = None if root is None else root / ("clean" if env == "clean" else "mix") / (
                f"{uid}-{v}.m4a" if env == "clean" else f"{sid}.m4a")
            dst = clips / f"{sid}.mp4"
            if src is not None and src.is_file() and not dst.exists():
                shutil.copy(src, dst)
            sids.append(sid)

    def slim(r):
        d = {"heard": r.get("heard"), "got": r.get("got"), "ok": r["ok"], "ms": r.get("latency_ms"),
             "fs": r.get("false_support", False)}
        if "wer" in r:
            d.update(wer=r["wer"], kept=r.get("critical_kept"), critical=r.get("critical"))
        if r.get("confidence"):
            d["conf"] = r["confidence"]
        return d

    data = {"items": {k: {"control": v["control"], "question": v["question"], "options": v["options"],
                          "escape": v["escape"]} for k, v in ITEMS.items()},
            "utterances": [{"id": u[0], "item": u[1], "said": u[2], "expected": u[3], "tag": u[4],
                            "voice": shown[u[0]]} for u in UTTERANCES],
            "beds": BEDS, "levels": levels, "env_label": ENV_LABEL, "passes": [PASS_KEY],
            "labels": {PASS_KEY: PASS_LABEL},
            "results": {PASS_KEY: {sid: slim(by_id[sid]) for sid in sids if sid in by_id}},
            "summary": {"passes": {PASS_KEY: {"label": PASS_LABEL, **summary}}}}
    template = (HERE / "page_template.html").read_text(encoding="utf-8")
    html = template.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (page / "index.html").write_text(html, encoding="utf-8")
    return page / "index.html"


def write(run_dir: Path, *, root: Path | None = None, selection: dict | None = None,
          keel_cloud_sha: str | None = None) -> dict:
    """Everything the run folder keeps, from its `results.jsonl`; returns the certificate."""
    run_dir = Path(run_dir)
    rows = load(run_dir)
    summary = summarize(rows)
    cert = certificate(rows)
    if keel_cloud_sha is None:
        try:
            keel_cloud_sha = (json.loads((run_dir / "run.json").read_text(encoding="utf-8")).get("classify") or {}) \
                .get("keel_cloud")
        except (OSError, ValueError):
            keel_cloud_sha = None
    stamp = run_dir.name.split("-noise-check")[0]
    header = {"stamp": stamp, "samples": str(root) if root else None, "keel_cloud": keel_cloud_sha,
              "selection": selection}
    (run_dir / SUMMARY).write_text(json.dumps({"written": datetime.now(timezone.utc).isoformat(), **header,
                                               "certificate": cert, "pass": summary}, indent=1), encoding="utf-8")
    (run_dir / MARKDOWN).write_text(markdown(summary, cert, rows, header=header), encoding="utf-8")
    row = register_row(cert, summary, stamp=stamp, keel_cloud=keel_cloud_sha, run_dir=run_dir.name)
    (run_dir / REGISTER_ROW).write_text(row + "\n", encoding="utf-8")
    register = run_dir.parent / REGISTER
    if not register.exists():
        register.write_text(REGISTER_HEAD, encoding="utf-8")
    with register.open("a", encoding="utf-8") as f:
        f.write(row + "\n")
    build_page(run_dir, rows, summary, root=root)
    return cert


if __name__ == "__main__":
    import sys

    print(write(Path(sys.argv[1]))["line"])
