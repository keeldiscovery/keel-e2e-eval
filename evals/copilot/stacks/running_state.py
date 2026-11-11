"""Spec 151 FR-5 Stack 2, `running_state`: live transcription and a running call state. `gpt-live-transcribe` over the
Realtime websocket on both tracks, the client committing each turn at the script's turn end (no server-side turn
detection), then Haiku 5.5 on `instructions/copilot-state.md` holding the questionnaire and a window of the transcript
so far (`WINDOW_TURNS`, default 12) at every turn end. At the text level the script's words are the transcript.

`LiveTranscriber` speaks the Realtime transcription protocol over any transport with `send(str)` / `recv() -> str` /
`close()`; the tests and `DRY=1` hand it a fake, and the real websocket (`clients.HttpClients.realtime`) is opened only
with a key. The audio is fed as fast as it is read, not at the speaking pace, so a 30-minute call is not 30 minutes of
wall clock; `parts.transcribe` is the commit-to-transcript time, which is the latency the live model adds.
"""

from __future__ import annotations

import base64
import json
import os
import time

from evals.copilot.stacks import base

LIVE_MODEL = "gpt-live-transcribe"
WINDOW_TURNS_DEFAULT = 12
CHUNK_SECONDS = 0.1
LIVE_PROMPT = "A video call: a founder asking survey questions in their own words, and the respondent answering."


def _closed_exceptions() -> tuple:
    try:
        from websockets.exceptions import ConnectionClosed                    # noqa: PLC0415
    except ImportError:
        return ()
    return (ConnectionClosed,)


def window_turns(env=None) -> int:
    env = os.environ if env is None else env
    raw = (env.get("WINDOW_TURNS") or "").strip()
    return int(raw) if raw.isdigit() and int(raw) > 0 else WINDOW_TURNS_DEFAULT


def session_update(*, prompt: str = LIVE_PROMPT, lang: str = "en", rate: int = 24_000) -> dict:
    """A transcription session: 16-bit PCM in, gpt-live-transcribe, no turn detection (the client commits)."""
    return {"type": "session.update",
            "session": {"type": "transcription",
                        "audio": {"input": {"format": {"type": "audio/pcm", "rate": rate},
                                            "transcription": {"model": LIVE_MODEL, "prompt": prompt, "language": lang},
                                            "turn_detection": None}}}}


class LiveTranscriber:
    """One track's live session. `say(pcm)` appends the turn's audio in chunks, commits, and returns `(text, ms)`, the
    ms from the commit to the completed transcript."""

    COMPLETED = "conversation.item.input_audio_transcription.completed"
    FAILED = ("error", "conversation.item.input_audio_transcription.failed")

    def __init__(self, transport, *, prompt: str = LIVE_PROMPT, rate: int = 24_000, width: int = 2, reopen=None):
        self.transport, self.rate, self.width, self.prompt, self.reopen = transport, rate, width, prompt, reopen
        self.transport.send(json.dumps(session_update(prompt=prompt, rate=rate)))
        self.seconds = 0.0
        self.reopened = 0

    def say(self, pcm: bytes, *, timeout: float = 30.0) -> tuple[str, int]:
        """One turn; a socket that drops mid-turn (a keepalive timeout, a closed connection) is reopened once and the
        turn sent again, when a `reopen` factory was given."""
        try:
            return self._say(pcm, timeout=timeout)
        except (ConnectionError, OSError, TimeoutError, *_closed_exceptions()):
            if self.reopen is None:
                raise
            self.close()
            self.transport = self.reopen()
            self.transport.send(json.dumps(session_update(prompt=self.prompt, rate=self.rate)))
            self.reopened += 1
            return self._say(pcm, timeout=timeout)

    def _say(self, pcm: bytes, *, timeout: float) -> tuple[str, int]:
        step = int(self.rate * CHUNK_SECONDS) * self.width
        for i in range(0, len(pcm), step):
            self.transport.send(json.dumps({"type": "input_audio_buffer.append",
                                            "audio": base64.b64encode(pcm[i:i + step]).decode("ascii")}))
        self.seconds += len(pcm) / (self.rate * self.width)
        self.transport.send(json.dumps({"type": "input_audio_buffer.commit"}))
        started = time.time()
        while time.time() - started < timeout:
            raw = self.transport.recv()
            if raw is None:
                break
            event = json.loads(raw)
            if event.get("type") == self.COMPLETED:
                return (event.get("transcript") or "").strip(), int((time.time() - started) * 1000)
            if event.get("type") in self.FAILED:
                break
        return "", int((time.time() - started) * 1000)

    def close(self):
        try:
            self.transport.close()
        except Exception:  # noqa: BLE001 - a closed socket is closed
            pass


def state_prompt(q: dict, current: str | None, state: str, lines: list[tuple[str, str]]) -> str:
    out = [base.questionnaire_block(q), ""] + base.status_lines(current, state)
    out += ["", "Transcript so far (newest last):"]
    out += [f"{base.SPEAKER[who]}: {text.strip()}" for who, text in lines]
    return "\n".join(out)


class RunningState(base.Stack):
    number = 2
    name = "running_state"
    levels = ("text", "audio")
    instruction_file = "copilot-state.md"

    def __init__(self, window: int | None = None):
        self.window = window or window_turns()

    def run(self, script, q, clients, *, level, audio_dir=None, clocks=None):
        system = base.instruction(self.instruction_file)
        items = {it["id"]: it for it in q["items"]}
        live = {}
        if level == "audio":
            live = {who: LiveTranscriber(clients.realtime(), reopen=clients.realtime) for who in ("founder", "them")}
        current, state, events, said = None, "listening", [], []
        try:
            for i, turn in enumerate(script["turns"]):
                usage, t_ms = {}, 0
                heard = turn["text"]
                if level == "audio":
                    frames, _rate, _w = base.cut(base.track_of(audio_dir, turn["who"]), clocks[i]["start"],
                                                 clocks[i]["end"])
                    heard, t_ms = live[turn["who"]].say(frames)
                    usage["live_s"] = clocks[i]["end"] - clocks[i]["start"]
                said.append((turn["who"], heard))
                user = state_prompt(q, current, state, said[-self.window:])
                reply, c_ms = clients.messages(base.haiku_body(system, user))
                usage.update(base.haiku_usage(reply))
                ev = base.event_from(base.read_reply(reply), turn=i, who=turn["who"], items=items, current=current,
                                     state=state)
                ev.update(heard=heard, parts={"wait": 0.0, "transcribe": t_ms / 1000, "classify": c_ms / 1000},
                          usage=usage)
                ev["t_emitted"] = round(sum(ev["parts"].values()), 3)
                events.append(ev)
                current, state = base.advance(ev, current), ev["state"]
        finally:
            for t in live.values():
                t.close()
        return events
