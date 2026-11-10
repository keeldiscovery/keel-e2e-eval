"""Spec 151 FR-5 Stack 3, `audio_direct`: the model listens, no transcript. `gpt-audio-mini` through Chat Completions
is given each turn's audio (an `input_audio` part, 16-bit PCM wav cut from the rendered track) and the questionnaire,
on `instructions/copilot-audio.md`, and returns the same JSON as the other two. There is no text level."""

from __future__ import annotations

import base64

from evals.copilot.stacks import base

AUDIO_MODEL = "gpt-audio-mini"
#: The methodology page's figure (OpenAI's pricing page, 2026-11-10): $10 a million audio tokens in. Its text-token
#: rates are not on the page: counted, priced at 0, owed.
AUDIO_USD_IN_PER_M = 10.0


def audio_body(system: str, user: str, wav: bytes) -> dict:
    return {"model": AUDIO_MODEL, "modalities": ["text"],
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": [
                             {"type": "text", "text": user},
                             {"type": "input_audio", "input_audio": {"data": base64.b64encode(wav).decode("ascii"),
                                                                     "format": "wav"}}]}]}


def reply_text(reply: dict) -> str:
    try:
        content = reply["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ""
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return content or ""


def audio_usage(reply: dict) -> dict:
    u = (reply or {}).get("usage") or {}
    audio_in = int(((u.get("prompt_tokens_details") or {}).get("audio_tokens")) or 0)
    return {"audio_tokens_in": audio_in, "audio_text_in": max(0, int(u.get("prompt_tokens") or 0) - audio_in),
            "audio_text_out": int(u.get("completion_tokens") or 0)}


class AudioDirect(base.Stack):
    number = 3
    name = "audio_direct"
    levels = ("audio",)
    instruction_file = "copilot-audio.md"

    def run(self, script, q, clients, *, level, audio_dir=None, clocks=None):
        if level != "audio":
            raise SystemExit("copilot-bench refuses: Stack 3 (audio_direct) has no text level")
        system = base.instruction(self.instruction_file)
        items = {it["id"]: it for it in q["items"]}
        current, state, events = None, "listening", []
        from evals.noise.pipeline import parse                                # noqa: PLC0415
        for i, turn in enumerate(script["turns"]):
            wav = base.cut_wav(base.track_of(audio_dir, turn["who"]), clocks[i]["start"], clocks[i]["end"])
            user = "\n".join([base.questionnaire_block(q), ""] + base.status_lines(current, state)
                             + [f"Track: {base.SPEAKER[turn['who']]}"])
            reply, c_ms = clients.audio_chat(audio_body(system, user, wav))
            ev = base.event_from(parse(reply_text(reply)), turn=i, who=turn["who"], items=items, current=current,
                                 state=state)
            wait = min(base.TURN_END_HOLD, float(turn.get("silence_after") or 0) or base.TURN_END_HOLD)
            ev.update(heard=None, parts={"wait": wait, "transcribe": 0.0, "classify": c_ms / 1000},
                      usage=audio_usage(reply))
            ev["t_emitted"] = round(sum(ev["parts"].values()), 3)
            events.append(ev)
            current, state = base.advance(ev, current), ev["state"]
        return events
