"""Spec 151 FR-7 / FR-9: the fake transports -- `DRY=1` and the tests run every stack through these, with no key and no
call. `FakeClients` answers each request with the next canned event (the script's own truth unless told otherwise),
hears each turn as its script words, and opens a fake Realtime transport that speaks the transcription protocol."""

from __future__ import annotations

import json
from collections import deque

from evals.copilot.stacks.base import canned_events


class FakeRealtime:
    """A Realtime transcription socket: `session.update` and `append` are recorded, every `commit` is answered with a
    `completed` event carrying the next transcript."""

    def __init__(self, transcripts: deque):
        self.transcripts, self.sent, self.inbox, self.closed = transcripts, [], deque(), False

    def send(self, raw: str):
        event = json.loads(raw)
        self.sent.append(event)
        if event["type"] == "input_audio_buffer.commit":
            text = self.transcripts.popleft() if self.transcripts else ""
            self.inbox.append(json.dumps({"type": "conversation.item.input_audio_transcription.delta", "delta": text}))
            self.inbox.append(json.dumps({"type": "conversation.item.input_audio_transcription.completed",
                                          "item_id": f"item_{len(self.sent)}", "transcript": text}))

    def recv(self):
        return self.inbox.popleft() if self.inbox else None

    def close(self):
        self.closed = True


class FakeClients:
    """One script's fake vendor. `events` default to the script's canned events (a perfect box); `heard` default to the
    script's words, per speaker track for the live transcriber."""

    def __init__(self, script: dict, *, events: list | None = None, heard: list | None = None, classify_ms: int = 400,
                 transcribe_ms: int = 300, usage: dict | None = None, audio_usage: dict | None = None):
        evs = events if events is not None else canned_events(script)
        self.replies = deque({k: e.get(k) for k in ("q", "verdict", "option", "tier", "state")} for e in evs)
        texts = heard if heard is not None else [t["text"] for t in script["turns"]]
        self.heard = deque(texts)
        self.by_track = {"founder": deque(), "them": deque()}
        for t, text in zip(script["turns"], texts, strict=True):
            self.by_track[t["who"]].append(text)
        self.classify_ms, self.transcribe_ms = classify_ms, transcribe_ms
        self.usage = usage or {"input_tokens": 0, "output_tokens": 0}
        self.audio_usage = audio_usage or {}
        self.requests, self.sockets = [], []

    def _next(self) -> str:
        return json.dumps(self.replies.popleft() if self.replies else {})

    def messages(self, body: dict):
        self.requests.append(body)
        return {"content": [{"type": "thinking", "thinking": ""}, {"type": "text", "text": self._next()}],
                "usage": dict(self.usage), "stop_reason": "end_turn"}, self.classify_ms

    def transcribe(self, wav: bytes, *, keywords: list, prompt: str):
        self.requests.append({"transcribe": len(wav), "keywords": keywords, "prompt": prompt})
        return (self.heard.popleft() if self.heard else ""), self.transcribe_ms, len(wav) / 48_000

    def audio_chat(self, body: dict):
        self.requests.append(body)
        return {"choices": [{"message": {"content": self._next()}}], "usage": dict(self.audio_usage)}, self.classify_ms

    def realtime(self):
        who = "founder" if not self.sockets else "them"
        sock = FakeRealtime(self.by_track[who])
        self.sockets.append(sock)
        return sock
