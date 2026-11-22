"""Spec 157 FR-3: the one run's report -- `runs/157/<cloud sha>-<web sha>/report.md`, every leg with every named check,
a failure naming its screen and its view, and the stack's log scan (no HeyGen, no OpenAI, no Anthropic host contacted).
Spec 158 FR-6: *The beats* -- every conversation the founder's legs told, beat by beat: the question Keel asked, how
much was said, what Keel read back, the red crosses (or the ticks and crosses), the orb's states and where it went.
Spec 158b: *The drawn story* -- every story measured while it played (the founder's on a desktop and a phone, the
stranger's story card on a phone): the three verdicts, the numbers, and every text found on a drawn element.
Spec 158c: *The turn* -- every conversation's hand-overs as keel-web 249 makes them plain: the chime counted once per
hand-over, the state line in the frame the orb first listens, the microphone open, and the guide sheets met (one film).

Pure functions over the legs and a log's text, so `tests/test_three_views_157.py` holds them with no stack.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

#: The vendors a paid run would reach: their hosts, and the adapters keel-cloud logs when one is used.
VENDOR_HOSTS = ("api.heygen.com", "api.openai.com", "api.anthropic.com")
VENDOR_MARKS = ("HeyGenRenderer", "OpenAiTranscriber", "OpenAiSpeech", "AnthropicMessagesExecutor", "KeelsAiClassifier")
#: keel-cloud 259 `KeelVoice`: every clip made carries its measured cost -- the fake's is 0.
SPEECH_LINE = re.compile(r"speech clip made: .*?cost_micro_usd=(\d+)")


def log_scan(text: str | None) -> dict:
    """The cloud log of the run's window, read for a vendor reached: any vendor host or paid adapter named, and the
    speech clips' measured cost (FakeSpeech: 0 each). `None` text (the remote profile: no log here) is not measured."""
    if text is None:
        return {"measured": False, "why": "no keel-cloud log on this profile (the remote twin's is the coordinator's)"}
    hosts = {h: text.count(h) for h in VENDOR_HOSTS}
    marks = {m: text.count(m) for m in VENDOR_MARKS}
    costs = [int(c) for c in SPEECH_LINE.findall(text)]
    return {"measured": True, "hosts": hosts, "adapters": marks, "speech_clips": len(costs),
            "speech_cost_micro_usd": sum(costs),
            "clean": not any(hosts.values()) and not any(marks.values()) and sum(costs) == 0}


def scan_line(scan: dict) -> str:
    if not scan.get("measured"):
        return f"Log scan: not measured -- {scan.get('why')}."
    if scan.get("clean"):
        return (f"Log scan: no HeyGen, no OpenAI, no Anthropic host contacted (0 of {', '.join(VENDOR_HOSTS)}; no paid "
                f"adapter named); {scan.get('speech_clips', 0)} Keel AI clips made, every one FakeSpeech at 0 µUSD.")
    return ("Log scan: A VENDOR WAS REACHED -- hosts " + json.dumps(scan.get("hosts")) + ", adapters "
            + json.dumps(scan.get("adapters")) + f", speech cost {scan.get('speech_cost_micro_usd')} µUSD.")


def leg_line(leg) -> str:
    why = f" -- {leg.why}" if leg.why and leg.status != "green" else ""
    return f"| {leg.id} | {leg.title} | **{leg.status}**{why} | {leg.seconds:g} s |"


def _cell(text, n: int = 160) -> str:
    words = " ".join(str(text if text is not None else "").split()).replace("|", "/")
    return words if len(words) <= n else words[: n - 3] + "..."


def beats_markdown(told: list[dict] | None) -> list[str]:
    """Spec 158 FR-6: one table a conversation -- beat, question, said (characters), readback, crosses (or ticks and
    crosses), the orb's states, where the beat went."""
    if not told:
        return []
    out = ["## The beats (spec 158)", ""]
    for one in told:
        out += [f"### {one.get('label')} -- `{str(one.get('project') or '')[:8]}`", "",
                "| Beat | Question | Said | Readback | Crosses | Orb | Next |", "|---|---|---|---|---|---|---|"]
        for b in one.get("beats") or []:
            put = b.get("put") or {}
            said = (put.get("sent") or {}).get("text") or ""
            body = put.get("body") or {}
            readback = body.get("readback")
            marks = (b.get("readback") or {}).get("marks") or []
            crosses = ("; ".join(f"{'✓' if m.get('mark') == 'tick' else '×'} {m.get('text')}" for m in marks) if marks
                       else "; ".join((b.get("readback") or {}).get("limits") or []))
            if b.get("correction"):
                readback = f"{readback} -- then *{((b['correction'].get('sent') or {}).get('text'))}*: " \
                           f"{(b['correction'].get('body') or {}).get('readback')}"
            out.append(f"| {b.get('turn')} | {_cell((b.get('asked') or {}).get('question'), 70)} | "
                       f"{len(said)} chars | {_cell(readback, 200)} | {_cell(crosses, 200)} | "
                       f"{' > '.join(b.get('orb') or [])} | {b.get('next') or '-'} |")
        out.append("")
    return out


def _yes(ok) -> str:
    return "-" if ok is None else ("yes" if ok else "**no**")


def _box(b) -> str:
    return f"{b.get('w')}x{b.get('h')}" if isinstance(b, dict) and b.get("w") is not None else "-"


def drawn_story_markdown(fits: list[dict] | None) -> list[str]:
    """Spec 158b: one row a story measured -- where and on what, the three verdicts, the frame, the person's height
    over the frame's, the pictograms, the longest spoken line in rows; then every overlap, and every moment it did not
    fit, by name."""
    if not fits:
        return []
    out = ["## The drawn story (spec 158b)", "",
           "| Story | Where | View | No text on the drawing | Fits on a phone | Line at most 3 rows | Frame | Person / frame "
           "| Pictograms | Line (rows, font / line height) | Reads |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for f in fits:
        m = f.get("measured") or {}
        v = f.get("verdicts") or {}
        n = m.get("numbers") or {}
        lines = m.get("lines") or {}
        most = max(lines.values(), key=lambda line: line.get("rows") or 0) if lines else {}
        pictos = ", ".join(_box(p) for p in (n.get("pictograms") or [])[:6]) or "-"
        line = f"{most.get('rows')} rows, {most.get('font')} / {most.get('line_height')}" if most else "-"
        out.append(f"| {_cell(f.get('label'), 60)} | {_cell(f.get('where'), 50)} | {f.get('view')} | "
                   f"{_yes(v.get('drawn'))} | {_yes(v.get('fits')) if f.get('phone') else '-'} | {_yes(v.get('rows'))} | "
                   f"{_box(n.get('frame'))} | {n.get('person_ratio') if n.get('person_ratio') is not None else '-'} | "
                   f"{pictos} | {line} | {m.get('samples', 0)}{'' if m.get('played') else ' (never seen playing)'} |")
    out.append("")
    for f in fits:
        m = f.get("measured") or {}
        overlaps = m.get("overlaps") or []
        unfit = (m.get("unfit") or []) if f.get("phone") else []
        long = {t: line for t, line in (m.get("lines") or {}).items() if (line.get("rows") or 0) > 3}
        if f.get("phone") and m.get("page_scrolls"):
            out_vp = ((m.get("numbers") or {}).get("viewport") or {}).get("h")
            footer = f"- the page is {m['page_scrolls']} px tall on a {out_vp} px screen: the site's footer under the story " \
                     "(the story itself fits)"
        else:
            footer = None
        if not (overlaps or unfit or long or footer):
            continue
        out += [f"### {f.get('label')} -- {f.get('view')}", ""]
        for o in overlaps:
            out.append(f"- text on the drawing: *{_cell(o.get('text'), 80)}* over `{o.get('drawn')}` ({o.get('kind')}); "
                       f"text {json.dumps(o.get('text_box'))}, drawn {json.dumps(o.get('drawn_box'))}")
        for u in unfit:
            out.append(f"- does not fit: {', '.join(u.get('what') or [])}; band {json.dumps(u.get('band'))}, frame "
                       f"{json.dumps(u.get('frame'))}, line {json.dumps(u.get('line'))}, document {json.dumps(u.get('doc'))}")
        for text, line in long.items():
            out.append(f"- {line.get('rows')} rows: *{_cell(text, 120)}*")
        if footer:
            out.append(footer)
        out.append("")
    return out


def turn_markdown(turns: list[dict] | None) -> list[str]:
    """Spec 158c: one row a conversation -- the hand-overs, the chimes, one each, the state lines at the hand-over, the
    microphone open; the sheets met on the conversation's routes, the most at once, the guide seen after."""
    if not turns:
        return []
    out = ["## The turn (spec 158c, keel-web 249)", "",
           "| Conversation | Hand-overs | Chimes | One each | *Your turn.* at the hand-over | Mic open | Opener on | "
           "Welcome on | Sheets at once | Guide seen after |", "|---|---|---|---|---|---|---|---|---|---|"]
    for t in turns:
        v = t.get("chime") or {}
        sh = t.get("sheets") or {}
        lines = sorted({str(x.get("line")) for x in v.get("lines") or []})
        guide = t.get("guide")
        seen = (f"welcome {_yes(guide.get('welcomeSeen'))}, openers {', '.join(guide.get('openersSeen') or []) or '-'}"
                if guide else "-")
        out.append(f"| {_cell(t.get('label'), 50)} | {v.get('hand_overs', '-')} | {v.get('chimes', '-')} | "
                   f"{_yes(v.get('one_each'))} | {_yes(v.get('your_turn'))} ({_cell('; '.join(lines), 90)}) | "
                   f"{_yes(v.get('mic_open'))} | {len(sh.get('opener_on') or [])} | {len(sh.get('welcome_on') or [])} | "
                   f"{sh.get('most_at_once', '-')} | {seen} |")
    out.append("")
    for t in turns:
        v = t.get("chime") or {}
        if v.get("stray") or v.get("listening_without_mic") or (v.get("got") != v.get("want")):
            out += [f"### {t.get('label')}", "",
                    f"- chimes at the hand-overs {v.get('got')}, wanted {v.get('want')}",
                    f"- counted off a hand-over: `{json.dumps(v.get('stray'))[:400]}`",
                    f"- listening with the microphone shut: `{json.dumps(v.get('listening_without_mic'))[:400]}`", ""]
    return out


def report_markdown(legs, meta: dict, scan: dict, beats: list[dict] | None = None,
                    fits: list[dict] | None = None, turns: list[dict] | None = None) -> str:
    """The report: the head (shas, profile, the run's bundle), the table of legs, each leg's checks, then the beats."""
    out = [f"# Spec 157 / 158 -- the three views on the conversation, end to end (one run)", "",
           f"- keel-cloud `{meta.get('cloud')}` · keel-web `{meta.get('web')}` · keel-e2e-eval `{meta.get('eval')}`",
           f"- profile `{meta.get('profile')}` · started {meta.get('started')} · {meta.get('seconds', 0):g} s",
           f"- bundle `{meta.get('bundle')}`", f"- {scan_line(scan)}", "",
           "| Leg | What | Result | Time |", "|---|---|---|---|"]
    out += [leg_line(leg) for leg in legs]
    green = sum(1 for leg in legs if leg.status == "green")
    out += ["", f"**{green} of {len(legs)} legs green.**", ""]
    for leg in legs:
        out += [f"## {leg.id} -- {leg.title}", "", f"Result: **{leg.status}**" + (f" -- {leg.why}" if leg.why else ""), ""]
        for note in leg.notes:
            out.append(f"- note: {note}")
        for c in leg.checks:
            mark = "ok" if c.ok else "FAILED"
            where = f" (screen: {c.screen}; view: {c.view})"
            line = f"- [{mark}] {c.name}{where}"
            if not c.ok:
                line += f"\n  - got: `{json.dumps(c.detail, default=str)[:900]}`"
            out.append(line)
        out.append("")
    out += beats_markdown(beats)
    out += drawn_story_markdown(fits)
    out += turn_markdown(turns)
    return "\n".join(out).rstrip() + "\n"


def write_report(path: Path, legs, meta: dict, scan: dict, beats: list[dict] | None = None,
                 fits: list[dict] | None = None, turns: list[dict] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_markdown(legs, meta, scan, beats, fits, turns), encoding="utf-8")
    return path
