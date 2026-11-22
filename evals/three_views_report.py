"""Spec 157 FR-3: the one run's report -- `runs/157/<cloud sha>-<web sha>/report.md`, every leg with every named check,
a failure naming its screen and its view, and the stack's log scan (no HeyGen, no OpenAI, no Anthropic host contacted).
Spec 158 FR-6: *The beats* -- every conversation the founder's legs told, beat by beat: the question Keel asked, how
much was said, what Keel read back, the red crosses (or the ticks and crosses), the orb's states and where it went.

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


def report_markdown(legs, meta: dict, scan: dict, beats: list[dict] | None = None) -> str:
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
    return "\n".join(out).rstrip() + "\n"


def write_report(path: Path, legs, meta: dict, scan: dict, beats: list[dict] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_markdown(legs, meta, scan, beats), encoding="utf-8")
    return path
