"""Spec 151 FR-5: what the three stacks share -- the questionnaire block every prompt carries, the Haiku request in the
noise pipeline's shape, the read of a reply into an event (`norm_out` reused on an answer), the turn audio cut from a
rendered track (stdlib `wave`: the tracks are 16-bit PCM), and the canned events `DRY=1` scores."""

from __future__ import annotations

import io
import wave
from pathlib import Path

from evals.copilot import catalogue as cat
from evals.copilot.questionnaire import labels, noise_item
from evals.noise.pipeline import CLASSIFY_EFFORT, CLASSIFY_MODEL, MAX_TOKENS, THINKING, answer_text, norm_out, parse

HERE = Path(__file__).resolve().parents[1]
INSTRUCTIONS = HERE / "instructions"
#: The browser's own silence detection stands in for a turn's end: the hold before a turn is declared over.
TURN_END_HOLD = 0.7
#: Haiku 5.5's list prices (as `evals.noise.pipeline`), $ a million tokens.
HAIKU_USD_IN, HAIKU_USD_OUT = 0.10, 0.50
SPEAKER = {"founder": "founder", "them": "respondent"}


def instruction(name: str) -> str:
    text = (INSTRUCTIONS / name).read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"copilot-bench refuses: {name} is blank")
    return text


def questionnaire_block(q: dict) -> str:
    lines = ["Questionnaire:"]
    for it in q["items"]:
        sp = it.get("spoken") or {}
        kind = {"gate": "yes or no", "single": "one of the options", "number": "a number",
                "free": "free text"}.get(it["kind"], f"{it.get('pick') or 'any'} of the options")
        said = f"{sp['anchor']} {sp.get('stem')}" if sp.get("anchor") else sp.get("stem") or it["question"]
        lines.append(f"{it['id']} ({kind}{', in ' + str(it['unit']) if it.get('unit') else ''}): {said}")
        for n, o in enumerate(it.get("options") or [], 1):
            lines.append(f"  {n}. {o}")
        if it.get("escape"):
            lines.append(f'  escape: "{it["escape"]}"')
    return "\n".join(lines)


def status_lines(current: str | None, state: str) -> list[str]:
    return [f"Current question: {current or 'none yet'}", f"Box state before this turn: {state}"]


def haiku_body(system: str, user: str) -> dict:
    """The noise pipeline's request: Haiku 5.5, max_tokens 1,024, adaptive thinking at effort medium, no temperature."""
    return {"model": CLASSIFY_MODEL, "max_tokens": MAX_TOKENS, "system": system,
            "messages": [{"role": "user", "content": user}], "thinking": dict(THINKING),
            "output_config": {"effort": CLASSIFY_EFFORT}}


def haiku_usage(reply: dict) -> dict:
    u = (reply or {}).get("usage") or {}
    return {"haiku_in": int(u.get("input_tokens") or 0), "haiku_out": int(u.get("output_tokens") or 0)}


def read_reply(reply: dict) -> dict | None:
    return parse(answer_text(reply or {}))


def event_from(parsed: dict | None, *, turn: int, who: str, items: dict, current: str | None, state: str) -> dict:
    """A model's JSON as an event: an unknown id, verdict, tier or state is dropped (null); a founder turn carries no
    answer; a respondent turn carries no founder verdict (a question verdict, an own note or a back-channel echoed onto
    the respondent's line is dropped and the option read); an answer is read through `norm_out` against its item, as
    `Classification.validated()` reads it. The model's JSON stays on the event as `reply`, for the audit."""
    p = parsed if isinstance(parsed, dict) else {}
    q = p.get("q") if p.get("q") in items else None
    verdict = p.get("verdict") if p.get("verdict") in cat.VERDICTS else None
    if who == "them" and verdict in cat.FOUNDER_VERDICTS:
        verdict = None          # a respondent asks no Keel question: a verdict echoed from the founder's line is noise
    tier = p.get("tier")
    tier = cat.CONFIDENCE_TIER.get(tier, tier) if tier is not None else None
    tier = tier if tier in cat.TIERS else None
    new_state = p.get("state") if p.get("state") in cat.STATES else state
    option = None
    if who == "them" and verdict is None and q and items[q]["kind"] in cat.CLOSED and p.get("option") is not None:
        option = {k: v for k, v in norm_out(noise_item(items[q]), p["option"]).items() if not k.startswith("_")}
        if option.get("unclear"):
            tier = "unsure"
    if who == "founder":
        tier = None
    return {"turn": turn, "q": q, "verdict": verdict, "option": option, "tier": tier, "state": new_state,
            "parsed": parsed is not None, "reply": parsed if isinstance(parsed, dict) else None}


def advance(ev: dict, current: str | None) -> str | None:
    """The question the box holds after an event: the founder's newest question, else unchanged."""
    if ev.get("verdict") in cat.QUESTION_VERDICTS and ev.get("q"):
        return ev["q"]
    return current


def keywords(q: dict, current: str | None) -> list[str]:
    """`keywords[]` for the transcriber: the current item's labels and every item's spoken stem."""
    items = {it["id"]: it for it in q["items"]}
    out = labels(items[current]) if current in items else []
    for it in q["items"]:
        stem = (it.get("spoken") or {}).get("stem") or it["question"]
        if stem not in out:
            out.append(stem)
    return out


# ------------------------------------------------------------------------------------------------ the audio

def cut(track: Path, start: float, end: float) -> tuple[bytes, int, int]:
    """The PCM frames of `track` from `start` to `end` seconds: `(frames, rate, sample width)`."""
    with wave.open(str(track), "rb") as w:
        rate, width = w.getframerate(), w.getsampwidth()
        w.setpos(max(0, min(w.getnframes(), int(start * rate))))
        frames = w.readframes(max(0, int((end - start) * rate)))
    return frames, rate, width


def cut_wav(track: Path, start: float, end: float) -> bytes:
    frames, rate, width = cut(track, start, end)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(width)
        w.setframerate(rate)
        w.writeframes(frames)
    return buf.getvalue()


def track_of(audio_dir: Path, who: str) -> Path:
    return Path(audio_dir) / ("founder.wav" if who == "founder" else "them.wav")


# ------------------------------------------------------------------------------------------------ the stack

class Stack:
    number = 0
    name = "stack"
    levels = ("text", "audio")

    def run(self, script: dict, q: dict, clients, *, level: str, audio_dir: Path | None = None,
            clocks: list | None = None) -> list[dict]:
        raise NotImplementedError


def canned_events(script: dict, *, question_s: float = 0.6, answer_s: float = 0.9) -> list[dict]:
    """The events a perfect box would emit, from the script's truth -- what `DRY=1` scores (and what the fake clients
    answer)."""
    out = []
    for i, t in enumerate(script["turns"]):
        tr = t["truth"]
        secs = question_s if t["who"] == "founder" else answer_s
        out.append({"turn": i, "q": tr.get("q"), "verdict": tr.get("verdict"), "option": tr.get("option"),
                    "tier": tr.get("tier"), "state": tr.get("state_after"), "parsed": True, "t_emitted": secs,
                    "parts": {"wait": 0.0, "transcribe": 0.0, "classify": secs}, "usage": {}})
    return out
