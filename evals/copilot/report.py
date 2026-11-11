"""Spec 151 FR-6 / FR-7: the sheet, the page and the register row of a `make copilot-bench` run.

Per stack: `sheet-<n>-<name>.json` and `sheet-<n>-<name>.md` (the cells against the bars, A's confusion matrix by habit
kind, B by control, tier and behaviour, C, D, E, G's split, the misses, the cost); the run's `sheet.json` (every stack)
and `sheet.md` (every stack's certificate line first, then each stack's sheet); `page/index.html` (the sheet, and each
script's turns -- words, what the stack heard, the truth and every stack's event -- with the clips beside them where the
audio was rendered); `register-row.md`, a row a stack, appended to `runs/copilot-bench-register.md` (not on DRY).
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from evals.copilot import bars as B

REGISTER = "copilot-bench-register.md"
REGISTER_HEAD = ("# The copilot call bench's register (spec 151 FR-7)\n\nOne row a stack a `make copilot-bench` run; "
                 "a row is never rewritten.\n\n| Run | Round | Level | Stack | Certificate | A same meaning | "
                 "A own-words options | B offered | G question | G answer | Scripts | Cost | Folder |\n"
                 "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")


def _v(cell: dict) -> str:
    v = cell.get("value")
    if v is None:
        return "–"
    seconds = cell.get("name", "").endswith("_s") or cell.get("what", "").find("seconds") >= 0
    return f"{v} s" if seconds else f"{v}%"


def stack_markdown(sh: dict) -> str:
    cert = sh["certificate"]
    w = [f"## Stack {sh['number']} -- {sh['stack']}", "", f"**{cert['line']}**", "",
         f"{sh['n_scripts']} scripts, {sh['n_turns']} turns; cost ${sh['cost']['total_usd']} "
         f"(per 30-minute call ${sh['cost']['per_30_min_call_usd']}).", "",
         "| Cell | What | Value | Bar | n | |", "|---|---|---|---|---|---|"]
    for name, *_ in B.BARS:
        c = sh["cells"][name]
        mark = ("not applicable" if name in cert["not_applicable"] else
                {"ok": "ok", "fail": "**FAIL**", "not measured": "not measured"}[c["status"]])
        bar = f"{c['op']} {c['bar']:g}{' s' if name.endswith('_s') else '%'}"
        w.append(f"| {name} | {c['what']} | {_v(c)} | {bar} | {c['n']} | {mark} |")
    w += ["", "### A -- mapping, by the kind the turn was written for", "",
          "| Kind | n | right | right question | read as |", "|---|---|---|---|---|"]
    for k, row in sh["A"]["confusion"].items():
        got = ", ".join(f"{v} {n}" for v, n in sorted(row["got"].items(), key=lambda kv: -kv[1]))
        w.append(f"| {k} | {row['n']} | {row['right']} | {row['q_right']} | {got} |")
    for title, table in (("B -- answers by control", sh["B"]["by_control"]), ("B -- by the truth's tier",
                                                                                 sh["B"]["by_tier"]),
                         ("B -- by respondent behaviour", sh["B"]["by_kind"]),
                         ("B -- noisy scripts (reported, not gated)", sh["B"]["noisy"])):
        if not table:
            continue
        w += ["", f"### {title}", "", "| | n | right |", "|---|---|---|"]
        w += [f"| {k} | {v['n']} | {v['pct']}% |" for k, v in table.items()]
    w += ["", "### C, D, E, G", "",
          f"- C: own notes kept apart {sh['C']['notes_apart']}%; follow-up replies read as answers "
          f"{sh['C']['read_as_answers']}; stretches {sh['C']['stretches']}.",
          f"- D: moves {sh['D']['moves']}, missed {sh['D']['missed']}, false {sh['D']['false']}.",
          f"- E: unsure on every answer {sh['E']['unsure_of_all_answers']}% ({sh['E']['written_unclear']} of "
          f"{sh['E']['answers']} answers written unclear on purpose).",
          f"- G: question recognised split {json.dumps(sh['G']['question_parts'])}; answer shown split "
          f"{json.dumps(sh['G']['answer_parts'])}; shown after the next turn began "
          f"{sh['G']['after_the_next_turn_began']}.",
          f"- Cost: {json.dumps(sh['cost']['usd'])}" + (f"; counted, not priced: {', '.join(sh['cost']['unpriced'])}"
                                                        if sh["cost"]["unpriced"] else ""), ""]
    if sh["misses"]:
        w += [f"### Misses ({len(sh['misses'])} shown)", "",
              "| Script | Turn | Who | Kind | Words | Heard | Truth | Read |", "|---|---|---|---|---|---|---|---|"]
        for m in sh["misses"]:
            truth = f"{m.get('truth_q')} {m.get('truth_v')}" if "truth_v" in m else json.dumps(m.get("expected"))
            read = (f"{m.get('got_q')} {m.get('got_v')}" if "got_v" in m
                    else f"{json.dumps(m.get('got'))} {m.get('tier')}")
            words = (m.get("text") or "").replace("|", "/")[:120]
            heard = (m.get("heard") or "").replace("|", "/")[:120]
            w.append(f"| {m['script']} | {m['turn']} | {m['who']} | {m.get('kind') or ''} | {words} | {heard} | "
                     f"{truth} | {read} |")
    return "\n".join(w) + "\n"


def register_row(sh: dict, *, stamp: str, run_dir: str, run_cost: float) -> str:
    c = sh["cells"]
    cert = sh["certificate"]
    verdict = cert["verdict"] + (f" ({cert['failing']})" if cert.get("failing") else "")
    return (f"| {stamp} | {sh['round']} | {sh['level']} | {sh['number']} {sh['stack']} | {verdict} | "
            f"{_v(c['A.same_meaning'])} | {_v(c['A.options_own_words'])} | {_v(c['B.offered'])} | "
            f"{_v(c['G.question_s'])} | {_v(c['G.answer_s'])} | {sh['n_scripts']} | "
            f"${round(sh['cost']['total_usd'] + run_cost, 4)} | {run_dir} |")


def page(run_dir: Path, sheets: list[dict], scripts: list[dict], events: dict, *, audio: bool) -> Path:
    """One self-contained page: each stack's certificate and cells, then each script's turns with the truth and every
    stack's event, the two tracks' clips above each script where they were rendered."""
    out = Path(run_dir) / "page"
    out.mkdir(parents=True, exist_ok=True)
    e = html.escape
    parts = ["<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' "
             "content='width=device-width, initial-scale=1'><title>Copilot call bench</title><style>"
             ":root{--bg:#fff;--fg:#1b1b1b;--mute:#666;--line:#ddd;--bad:#b3261e;--good:#1e6b34}"
             "@media (prefers-color-scheme: dark){:root{--bg:#141414;--fg:#eee;--mute:#aaa;--line:#333;--bad:#ff8a80;"
             "--good:#7fd38f}}body{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;"
             "margin:0 auto;max-width:1200px;padding:16px}table{border-collapse:collapse;width:100%;margin:8px 0 20px}"
             "td,th{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}"
             ".bad{color:var(--bad)}.good{color:var(--good)}.mute{color:var(--mute)}.wrap{overflow-x:auto}"
             "</style></head><body><h1>Copilot call bench</h1>"]
    for sh in sheets:
        parts.append(f"<h2>Stack {sh['number']} {e(sh['stack'])}</h2><p><b>{e(sh['certificate']['line'])}</b></p>"
                     "<div class='wrap'><table><tr><th>Cell</th><th>What</th><th>Value</th><th>Bar</th><th>n</th></tr>")
        for name, *_ in B.BARS:
            c = sh["cells"][name]
            cls = "bad" if c["status"] == "fail" else ("good" if c["status"] == "ok" else "mute")
            parts.append(f"<tr class='{cls}'><td>{name}</td><td>{e(c['what'])}</td><td>{e(_v(c))}</td>"
                         f"<td>{c['op']} {c['bar']:g}</td><td>{c['n']}</td></tr>")
        parts.append("</table></div>")
    parts.append("<h2>Scripts</h2>")
    names = [f"{sh['number']}" for sh in sheets]
    for s in scripts:
        parts.append(f"<h3 id='{e(s['id'])}'>{e(s['id'])}</h3>")
        if audio:
            for track in ("founder", "them"):
                parts.append(f"<p>{track}: <audio controls preload='none' src='../audio/{e(s['id'])}/{track}.wav'>"
                             f"</audio></p>")
        parts.append("<div class='wrap'><table><tr><th>t</th><th>who</th><th>words</th><th>truth</th>"
                     + "".join(f"<th>stack {n}</th>" for n in names) + "</tr>")
        for i, t in enumerate(s["turns"]):
            tr = t["truth"]
            truth = " ".join(str(x) for x in (tr.get("q"), tr.get("verdict"), json.dumps(tr.get("option"))
                                               if tr.get("option") else None, tr.get("tier"), tr.get("state_after"))
                             if x)
            cells = []
            for sh in sheets:
                ev = next((x for x in (events.get(sh["number"]) or {}).get(s["id"]) or [] if x["turn"] == i), {})
                got = " ".join(str(x) for x in (ev.get("q"), ev.get("verdict"), json.dumps(ev.get("option"))
                                                 if ev.get("option") else None, ev.get("tier"), ev.get("state"))
                               if x)
                heard = f"<br><span class='mute'>{e(ev['heard'])}</span>" if ev.get("heard") and ev["heard"] != t[
                    "text"] else ""
                cells.append(f"<td>{e(got)} <span class='mute'>{ev.get('t_emitted', '')} s</span>{heard}</td>")
            parts.append(f"<tr><td>{t['t']}</td><td>{t['who']}</td><td>{e(t['text'])}</td><td>{e(truth)}</td>"
                         + "".join(cells) + "</tr>")
        parts.append("</table></div>")
    parts.append("</body></html>")
    (out / "index.html").write_text("".join(parts), encoding="utf-8")
    return out / "index.html"


def write(run_dir: Path, sheets: list[dict], scripts: list[dict], events: dict, *, header: dict, audio: bool,
          register: bool) -> list[str]:
    """Everything the run folder keeps; returns the certificate lines."""
    run_dir = Path(run_dir)
    for sh in sheets:
        stem = f"sheet-{sh['number']}-{sh['stack']}"
        (run_dir / f"{stem}.json").write_text(json.dumps(sh, indent=1, ensure_ascii=False), encoding="utf-8")
        (run_dir / f"{stem}.md").write_text(f"# Copilot call bench -- {header['stamp']}\n\n" + stack_markdown(sh),
                                            encoding="utf-8")
    (run_dir / "sheet.json").write_text(json.dumps({**header, "stacks": sheets}, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    lines = [sh["certificate"]["line"] for sh in sheets]
    md = [f"# Copilot call bench -- {header['stamp']}", "",
          f"Round {header['round']}, level {header['level']}, questionnaire {header['questionnaire']}; "
          f"{header['scripts_kept']} scripts kept, {header['scripts_dropped']} dropped after one rewrite; writer "
          f"${header['run_cost']['writer_usd']}, voices ${header['run_cost']['tts_usd']}"
          f"{'; DRY (fake writer, canned events, nothing spent)' if header.get('dry') else ''}.", ""]
    md += [f"- **{line}**" for line in lines] + [""]
    md += [stack_markdown(sh) for sh in sheets]
    (run_dir / "sheet.md").write_text("\n".join(md), encoding="utf-8")
    page(run_dir, sheets, scripts, events, audio=audio)
    run_cost = header["run_cost"]["writer_usd"] + header["run_cost"]["tts_usd"]
    rows = [register_row(sh, stamp=header["stamp"], run_dir=run_dir.name, run_cost=run_cost if i == 0 else 0.0)
            for i, sh in enumerate(sheets)]
    (run_dir / "register-row.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    if register:
        reg = run_dir.parent / REGISTER
        if not reg.exists():
            reg.write_text(REGISTER_HEAD, encoding="utf-8")
        with reg.open("a", encoding="utf-8") as f:
            f.write("\n".join(rows) + "\n")
    return lines
