"""Spec 151 FR-5 / FR-7: the paid transports, behind one small interface so every stack runs on a fake in the tests.

`Clients` is what a stack and the writer call:

* `messages(body) -> (reply, ms)` -- Anthropic's Messages API (Haiku 5.5 for the stacks, Sonnet 5.5 for the writer);
* `transcribe(wav, *, keywords, prompt) -> (text, ms, seconds)` -- OpenAI gpt-transcribe, as `OpenAiTranscriber` calls
  it (`evals.noise.pipeline`: `response_format=json`, `languages[]`, one `keywords[]` a hint, the prompt);
* `audio_chat(body) -> (reply, ms)` -- OpenAI's Chat Completions with an `input_audio` part (gpt-audio-mini);
* `realtime() -> transport` -- a Realtime websocket for gpt-live-transcribe (`send(str)`, `recv() -> str`,
  `close()`), used only by `stacks.running_state.LiveTranscriber`.

The keys come from the shell (`KEEL_OPENAI_API_KEY`, `KEEL_ANTHROPIC_API_KEY`) into the request headers alone -- never
logged, echoed or written; `keys_from` refuses by the variable's name. `HttpClients` is the only class that touches the
network, and it is built only by `bench.run` when both keys are present and `DRY` is not set.
"""

from __future__ import annotations

import os
import time

from evals.noise.pipeline import ANTHROPIC_KEY_VAR, OPENAI_KEY_VAR

MESSAGES_URL = "https://api.anthropic.com/v1/messages"
TRANSCRIBE_URL = "https://api.openai.com/v1/audio/transcriptions"
CHAT_URL = "https://api.openai.com/v1/chat/completions"
REALTIME_URL = "wss://api.openai.com/v1/realtime?intent=transcription"


def keys_from(env=None) -> dict:
    """The two keys from the shell, or a refusal that names the variable -- never the value."""
    env = os.environ if env is None else env
    keys = {"openai": (env.get(OPENAI_KEY_VAR) or "").strip(), "anthropic": (env.get(ANTHROPIC_KEY_VAR) or "").strip()}
    absent = [n for n, v in ((OPENAI_KEY_VAR, keys["openai"]), (ANTHROPIC_KEY_VAR, keys["anthropic"])) if not v]
    if absent:
        raise SystemExit("copilot-bench refuses: " + " and ".join(absent) + " not set in this shell -- the bench calls "
                         "Sonnet 5.5 (the writer), Haiku 5.5, gpt-transcribe, gpt-live-transcribe, gpt-audio-mini and "
                         "gpt-4o-mini-tts; the keys are read into the request headers alone, never logged, echoed or "
                         "written (DRY=1 needs neither)")
    return keys


class HttpClients:
    """The real transports. Three tries on a 429, a 5xx or a broken connection, as the noise check."""

    def __init__(self, keys: dict, *, timeout: int = 60):
        self.keys, self.timeout = keys, timeout

    def _post(self, url, *, headers, json=None, data=None, files=None, timeout=None):
        import requests                                                       # noqa: PLC0415

        response = None
        for _ in range(3):
            try:
                response = requests.post(url, headers=headers, json=json, data=data, files=files,
                                         timeout=timeout or self.timeout)
            except requests.RequestException:
                time.sleep(1.0)
                continue
            if response.status_code == 429 or response.status_code >= 500:
                time.sleep(1.0)
                continue
            break
        return response

    def messages(self, body: dict) -> tuple:
        headers = {"x-api-key": self.keys["anthropic"], "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}
        started = time.time()
        r = self._post(MESSAGES_URL, headers=headers, json=body, timeout=600 if body.get("max_tokens", 0) > 16_000
                       else self.timeout)
        ms = int((time.time() - started) * 1000)
        if r is None or r.status_code != 200:
            return {"error": None if r is None else r.status_code, "content": []}, ms
        return r.json(), ms

    def transcribe(self, wav: bytes, *, keywords: list[str], prompt: str, lang: str = "en") -> tuple:
        from evals.noise.pipeline import TRANSCRIBE_MODEL                     # noqa: PLC0415

        data = [("model", TRANSCRIBE_MODEL), ("response_format", "json"), ("languages[]", lang)]
        data += [("keywords[]", k) for k in keywords] + [("prompt", prompt)]
        started = time.time()
        r = self._post(TRANSCRIBE_URL, headers={"Authorization": "Bearer " + self.keys["openai"]}, data=data,
                       files={"file": ("turn.wav", wav, "audio/wav")})
        ms = int((time.time() - started) * 1000)
        if r is None or r.status_code != 200:
            return "", ms, 0.0
        body = r.json()
        return (body.get("text") or "").strip(), ms, float((body.get("usage") or {}).get("seconds", 0) or 0)

    def audio_chat(self, body: dict) -> tuple:
        started = time.time()
        r = self._post(CHAT_URL, headers={"Authorization": "Bearer " + self.keys["openai"],
                                          "content-type": "application/json"}, json=body)
        ms = int((time.time() - started) * 1000)
        if r is None or r.status_code != 200:
            return {"error": None if r is None else r.status_code}, ms
        return r.json(), ms

    def realtime(self):
        try:
            from websockets.sync.client import connect                        # noqa: PLC0415
        except ImportError as missing:
            raise SystemExit("copilot-bench refuses: Stack 2 at the audio level needs the websockets package "
                             "(.venv/bin/pip install websockets)") from missing
        ws = connect(REALTIME_URL, additional_headers={"Authorization": "Bearer " + self.keys["openai"]},
                     open_timeout=20, max_size=None)
        return ws                                                             # send(str), recv() -> str, close()
