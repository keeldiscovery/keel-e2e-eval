"""Spec 152 FR-1 / FR-4: the copilot prototype's server -- Stack 1 of the bench, live, behind a local page.

A `ThreadingHTTPServer` on 127.0.0.1 (default port 8765, `PORT=`) that the founder opens in Chrome during a real call.
It is an eval-repo tool, not product code: no sign-in, no project, nothing in keel-cloud or keel-web.

Routes:

* `GET /` -- the page (`copilot.html`), and beside it `/copilot.js`, `/copilot.css` (plain files from this folder, no
  templating) and `/copilot.json`: the questionnaire's items, the frame pills (`frames.json`), the page's constants and
  the card as the server holds it.
* `POST /turn?who=founder|them&seq=<n>&started_at=<s>&ended_at=<s>&mode=share|rehearsal` -- one turn the page cut, the
  body a 16-bit mono WAV (`Content-Type: audio/wav`, the page's sample rate in its header). The wall clocks are epoch
  seconds from the page. Optional `shown=<seq>:<s>,<seq>:<s>` carries back when the page drew earlier replies. The turn
  is written to `turns/<seq>-<who>.wav`, transcribed with `clients.transcribe(wav, keywords=base.keywords(q, current),
  prompt=turn_by_turn.TRANSCRIBE_PROMPT)`, classified with `base.haiku_body(instruction('copilot-match.md'),
  turn_by_turn.match_prompt(q, current, state, who, heard))`, read through `base.read_reply` / `base.event_from`, and
  `current` / `state` advance with `base.advance` exactly as `TurnByTurn.run` does. The reply is the event (`q, verdict,
  option, tier, state, heard, reply, parts{wait, queue, transcribe, classify}, seq, who`) with the Filed row it makes
  and the card.
* `POST /key` -- `{"key", "seq_of_turn": n | null, "at": s}`: the founder's filing on the server's record (`1`-`6` an
  option, `0` the escape, `X` a note, `F` clear the frame flag, `Z` undo, `ArrowRight`/`Space` next unanswered,
  `ArrowLeft` previous, `P` listening on/off; `R`, `T`, `Escape` are the page's own and are only logged). The reply is
  the card.

Order: each request runs on its own thread. Transcription starts at once; the classify step waits for every turn that
arrived earlier (either side) to finish or to have been running `GIVE_UP_S` (20 s), so turns are read in arrival order
and a hung vendor call never holds the next turn past 20 s. The hung turn still completes and is recorded when it does;
it moves nothing a later turn has already moved, and a filing the founder made by key for it stands.

An empty transcript is not sent to the classifier: the event says `heard: ""` and, on the respondent's side, the card
hands the question over ("heard nothing", the options numbered).

The log is `runs/<stamp>-copilot-prototype/`: `turns/<seq>-<who>.wav`, `events.jsonl` (the bench's event shape plus
`heard`, `reply`, `parts`, `seq`, `who`, `wall{ended_at, shown_at}`), `keys.jsonl` and `session.json`. No `register`.

Keys come from `clients.keys_from(os.environ)` (`KEEL_OPENAI_API_KEY`, `KEEL_ANTHROPIC_API_KEY`) into the request
headers alone; the server refuses to start without both and never writes a key anywhere.

  PYTHONPATH=. .venv/bin/python -m evals.copilot.prototype.server [--port 8765] [--questionnaire <fixture>]
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import threading
import time
import wave
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from evals.copilot import clients as clients_mod
from evals.copilot import questionnaire as qmod
from evals.copilot.stacks import base, turn_by_turn
from evals.noise.pipeline import ANTHROPIC_KEY_VAR, OPENAI_KEY_VAR

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
RUNS_DIR = REPO_ROOT / "runs"
FRAMES = HERE / "frames.json"
INSTRUCTION = "copilot-match.md"
HOST = "127.0.0.1"
DEFAULT_PORT = 8765
#: The UX page's rule 5: after 5 s the Filed row says carry on; after 20 s the founder files it by hand.
STILL_WORKING_S = 5.0
GIVE_UP_S = 20.0
#: Five minutes with no turn on either source: the card shows the pause.
SILENCE_PAUSE_S = 300.0
#: The page's turn cutting: open after 150 ms above the threshold, close after `base.TURN_END_HOLD` below it, drop
#: anything shorter than 0.4 s.
TURN_OPEN_S, TURN_MIN_S = 0.15, 0.4
STATIC = {"/": ("copilot.html", "text/html; charset=utf-8"),
          "/copilot.html": ("copilot.html", "text/html; charset=utf-8"),
          "/copilot.js": ("copilot.js", "text/javascript; charset=utf-8"),
          "/copilot.css": ("copilot.css", "text/css; charset=utf-8")}
SIDES = ("founder", "them")
MODES = ("share", "rehearsal")
SERVER_KEYS = ("1", "2", "3", "4", "5", "6", "0", "X", "F", "Z", "ArrowRight", "Space", "ArrowLeft", "P")
PAGE_KEYS = ("R", "T", "Escape")
OWN_VERDICTS = ("follow_up", "own_note")
#: Words a frame pill can lose without losing its meaning (the token match ignores them).
SOFT_WORDS = frozenset("a an the it that this of to you your just".split())


class BadTurn(ValueError):
    pass


# ------------------------------------------------------------------------------------------------ small reads

def wav_info(wav: bytes) -> dict:
    """The WAV's shape, refused unless it is 16-bit mono PCM: `{rate, frames, seconds}`."""
    try:
        with wave.open(io.BytesIO(wav), "rb") as w:
            channels, width, rate, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
    except (wave.Error, EOFError) as bad:
        raise BadTurn(f"the body is not a WAV ({bad})") from bad
    if channels != 1 or width != 2:
        raise BadTurn(f"the WAV must be 16-bit mono (got {channels} channel(s), {8 * width}-bit)")
    return {"rate": rate, "frames": frames, "seconds": round(frames / rate, 3) if rate else 0.0}


def tokens(text: str) -> list[str]:
    """Lower-case words, `$` and thousands commas dropped, so "$800" and "800" are one word."""
    text = (text or "").lower().replace("$", "").replace(",", "")
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)


def frame_of(frames: dict, item_id: str | None) -> list[str]:
    f = frames.get(item_id) if item_id else None
    if not f:
        return []
    if isinstance(f, list):
        return [str(p) for p in f]
    return [str(p) for part in ("window", "unit", "anchor") for p in (f.get(part) or [])]


def missing_pills(pills: list[str], heard: str) -> list[str]:
    """The pills whose words are not all in what was heard (soft words ignored)."""
    said = set(tokens(heard))
    out = []
    for pill in pills:
        need = [t for t in tokens(pill) if t not in SOFT_WORDS] or tokens(pill)
        if not all(t in said for t in need):
            out.append(pill)
    return out


def answer_label(item: dict, option: dict | None) -> str | None:
    """What the Filed row says the answer is."""
    if not option:
        return None
    if option.get("unclear"):
        return "I did not catch that"
    if option.get("escape"):
        return item.get("escape") or "escape"
    if "value" in option:
        unit = item.get("unit")
        return f"{option['value']} {unit}" if unit else str(option["value"])
    if "text" in option:
        return option["text"]
    opts = item.get("options") or []
    return "; ".join(opts[n - 1] for n in option.get("picks") or [] if 0 < n <= len(opts)) or None


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _write_json(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _write_jsonl(path: Path, rows: list) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    os.replace(tmp, path)


def load_frames(path: Path = FRAMES) -> dict:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return raw.get("items") or {}


# ------------------------------------------------------------------------------------------------ the session

class Session:
    """The server's record of one hand call: the box's `current` / `state`, the filings (by the box, by key, as notes),
    the founder's own notes, the frame flags, the undo history, and the run folder they are written to."""

    def __init__(self, q: dict, clients, run_dir: Path, *, frames: dict | None = None, give_up_s: float = GIVE_UP_S,
                 mode: str = "share"):
        self.q, self.clients, self.run_dir = q, clients, Path(run_dir)
        self.items = {it["id"]: it for it in q["items"]}
        self.order = [it["id"] for it in q["items"]]
        self.frames = load_frames() if frames is None else frames
        self.system = base.instruction(INSTRUCTION)
        self.give_up_s = give_up_s
        self.mode = mode
        self.current: str | None = None
        self.state = "listening"
        self.listening = True
        self.model_done = False
        self.filings: dict[str, dict] = {}
        self.history: list[dict] = []
        self.notes: list[dict] = []
        self.flags: dict[str, list[str]] = {}
        self.note_next: set[str] = set()
        self.filed_row: dict | None = None
        self.heard_row: dict | None = None
        self.turns: dict[int, dict] = {}
        self.keyed_seqs: set[int] = set()
        self.events: list[dict] = []
        self.keys = 0
        self.rev = 0
        self.started = now_iso()
        self._cv = threading.Condition()
        self._io = threading.Lock()
        self._arrivals = 0
        self._applied_max = -1
        self._pending: dict[int, float] = {}
        (self.run_dir / "turns").mkdir(parents=True, exist_ok=True)
        self._write_session()

    # -------------------------------------------------------------------------------------------- turns

    def turn(self, *, who: str, seq: int, wav: bytes, started_at: float | None = None, ended_at: float | None = None,
             mode: str | None = None, shown: dict | None = None) -> dict:
        if who not in SIDES:
            raise BadTurn(f"who must be one of {', '.join(SIDES)}")
        info = wav_info(wav)
        if shown:
            self.shown(shown)
        with self._cv:
            if seq in self.turns:
                raise BadTurn(f"turn {seq} was already posted")
            if mode in MODES:
                self.mode = mode
            idx = self._arrivals
            self._arrivals += 1
            self._pending[idx] = time.monotonic()
            self.turns[seq] = {"who": who, "q_at": self.current, "idx": idx, "done": False}
            keywords = base.keywords(self.q, self.current)
        (self.run_dir / "turns" / f"{seq}-{who}.wav").write_bytes(wav)
        try:
            return self._run(idx, who=who, seq=seq, wav=wav, keywords=keywords, info=info, started_at=started_at,
                             ended_at=ended_at)
        finally:
            with self._cv:
                self._pending.pop(idx, None)
                self._cv.notify_all()

    def _wait_turn(self, idx: int) -> float:
        """Block until every earlier turn is done or has been running `give_up_s`; the seconds waited."""
        start = time.monotonic()
        while True:
            now = time.monotonic()
            blockers = [s for i, s in self._pending.items() if i < idx and now - s < self.give_up_s]
            if not blockers:
                return time.monotonic() - start
            self._cv.wait(timeout=max(0.01, min(self.give_up_s - (now - s) for s in blockers)))

    def _run(self, idx, *, who, seq, wav, keywords, info, started_at, ended_at) -> dict:
        usage = {}
        heard, t_ms, secs = self.clients.transcribe(wav, keywords=keywords, prompt=turn_by_turn.TRANSCRIBE_PROMPT)
        heard = (heard or "").strip()
        usage["transcribe_s"] = secs or info["seconds"]
        with self._cv:
            queue_s = self._wait_turn(idx)
            current, state = self.current, self.state
        c_ms, parsed = 0, None
        if heard:
            reply, c_ms = self.clients.messages(base.haiku_body(
                self.system, turn_by_turn.match_prompt(self.q, current, state, who, heard)))
            usage.update(base.haiku_usage(reply))
            parsed = base.read_reply(reply)
        ev = base.event_from(parsed, turn=idx, who=who, items=self.items, current=current, state=state)
        if not heard:
            ev.update(q=current, tier="unsure" if who == "them" else None)
        ev.update(heard=heard, parts={"wait": base.TURN_END_HOLD, "queue": round(queue_s, 3),
                                      "transcribe": t_ms / 1000, "classify": c_ms / 1000}, usage=usage)
        ev["t_emitted"] = round(sum(ev["parts"].values()), 3)
        ev.update(seq=seq, who=who, wall={"started_at": started_at, "ended_at": ended_at, "shown_at": None},
                  audio={"file": f"turns/{seq}-{who}.wav", **info})
        with self._cv:
            late = self._applied_max > idx
            self._applied_max = max(self._applied_max, idx)
            row = self._apply(ev, current=current, late=late)
            self.rev += 1
            ev["late"] = late
            ev["superseded"] = bool(row.get("superseded"))
            self.turns[seq].update(done=True, q=ev["q"] or current)
            ev["wall"]["shown_at"] = round(time.time(), 3)
            self.events.append(ev)
            out = dict(ev, filed_row=self._row_view(row), card=self.card())
        self._write_events()
        self._write_session()
        return out

    def _apply(self, ev: dict, *, current: str | None, late: bool) -> dict:
        """The event on the record: what moves, what files, the Filed row it makes."""
        who, seq, heard, verdict = ev["who"], ev["seq"], ev["heard"], ev["verdict"]
        q = ev["q"] or current
        self.heard_row = {"who": who, "heard": heard, "seq": seq}
        if not late:
            if ev.get("state") == "done":
                self.model_done = True
            before = self.current
            self.current = base.advance(ev, self.current)
            self.state = ev["state"]
            if self.current != before:
                self.note_next.discard(before)
        if who == "founder":
            if not heard:
                return {"kind": "heard_nothing", "who": who, "seq": seq, "q": q}
            if verdict == "meaning_changed" and ev["q"]:
                miss = missing_pills(frame_of(self.frames, ev["q"]), heard)
                self.flags[ev["q"]] = miss
                ev["frame_missing"] = miss
            elif verdict in ("as_written", "same_meaning", "options_own_words", "stacked", "leading") and ev["q"]:
                self.flags.pop(ev["q"], None)
            if verdict in OWN_VERDICTS:
                under = ev["q"] or current
                self.notes.append({"kind": "own_question", "under": under, "seq": seq, "heard": heard})
                row = {"kind": "own_question", "who": who, "seq": seq, "q": under}
                self.filed_row = row
                return row
            return {"kind": "founder", "who": who, "seq": seq, "q": ev["q"], "verdict": verdict}
        # the respondent
        if seq in self.keyed_seqs:
            return {"kind": "keyed", "seq": seq, "q": q, "superseded": True}
        if not heard:
            row = {"kind": "heard_nothing", "who": who, "seq": seq, "q": q}
        elif verdict in ("follow_up", "nothing"):
            self.notes.append({"kind": "reply" if verdict == "follow_up" else "not_an_answer", "under": q,
                               "seq": seq, "heard": heard})
            row = {"kind": "note", "who": who, "seq": seq, "q": q, "verdict": verdict}
        elif q in self.note_next:
            self.note_next.discard(q)
            self._file(q, {"by": "note", "option": None, "tier": None, "seq": seq, "heard": heard})
            row = {"kind": "kept_note", "who": who, "seq": seq, "q": q}
        elif q and ev["option"] is None and self.items[q]["kind"] == "free" and ev.get("parsed"):
            tier = ev["tier"] or "likely"
            self._file(q, {"by": "box", "option": {"text": heard}, "tier": tier, "seq": seq, "heard": heard})
            row = {"kind": tier, "who": who, "seq": seq, "q": q}
        elif q and ev["option"] and not ev["option"].get("unclear") and ev["tier"] in ("sure", "likely", None):
            tier = ev["tier"] or "likely"
            self._file(q, {"by": "box", "option": ev["option"], "tier": tier, "seq": seq, "heard": heard})
            row = {"kind": tier, "who": who, "seq": seq, "q": q}
        else:
            row = {"kind": "unsure", "who": who, "seq": seq, "q": q}
        self.filed_row = row
        return row

    def _file(self, q: str, filing: dict) -> None:
        filing = dict(filing, frame=frame_of(self.frames, q), frame_missing=list(self.flags.get(q) or []),
                      label=answer_label(self.items[q], filing.get("option")) if filing.get("option") else None)
        self.history.append({"q": q, "prev": self.filings.get(q), "row": self.filed_row})
        self.filings[q] = filing

    def shown(self, shown: dict) -> None:
        """The page's own clocks for when it drew replies: `{seq: epoch seconds}`."""
        with self._cv:
            changed = False
            for ev in self.events:
                s = shown.get(ev["seq"])
                if s is not None:
                    ev["wall"]["shown_at"] = s
                    changed = True
        if changed:
            self._write_events()

    # -------------------------------------------------------------------------------------------- keys

    def key(self, *, key: str, seq_of_turn: int | None = None, at: float | None = None,
            shown: dict | None = None, resume: bool = False) -> dict:
        """One key. `resume` is `P` pressed on the five-minute pause: the page stops showing it, listening stays on."""
        if shown:
            self.shown(shown)
        key = {" ": "Space", "x": "X", "f": "F", "z": "Z", "p": "P", "r": "R", "t": "T", "Esc": "Escape",
               "→": "ArrowRight", "←": "ArrowLeft"}.get(key, key)
        with self._cv:
            if key in PAGE_KEYS or (key == "P" and resume and self.listening):
                applied, message = "page", ("resumed after the silence" if key == "P" else None)
            elif key not in SERVER_KEYS:
                applied, message = False, f"{key!r} is not a copilot key"
            else:
                applied, message = self._key(key, seq_of_turn)
            self.keys += 1
            self.rev += 1
            row = {"key": key, "seq_of_turn": seq_of_turn, "at": at, "received_at": round(time.time(), 3),
                   "applied": applied, "message": message, "current": self.current,
                   "filed_q": (self.filed_row or {}).get("q")}
            card = self.card()
        with self._io:
            with (self.run_dir / "keys.jsonl").open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        self._write_session()
        return {"applied": applied, "message": message, "card": card}

    def _target(self, seq_of_turn: int | None) -> tuple[str | None, int | None]:
        if seq_of_turn is not None and seq_of_turn in self.turns:
            t = self.turns[seq_of_turn]
            return (t.get("q") or t["q_at"]), seq_of_turn
        row = self.filed_row or {}
        if row.get("q"):
            return row["q"], row.get("seq")
        return self.current, None

    def _key(self, key: str, seq_of_turn: int | None) -> tuple[bool, str | None]:
        if key == "P":
            self.listening = not self.listening
            return True, "listening" if self.listening else "paused"
        if key in ("ArrowRight", "Space"):
            nxt = self._next_unanswered()
            if nxt is None:
                return False, "every question is filed"
            self._move(nxt)
            return True, None
        if key == "ArrowLeft":
            i = self.order.index(self.current) if self.current in self.order else 0
            if i == 0:
                return False, "already on the first question"
            self._move(self.order[i - 1])
            return True, None
        if key == "F":
            if self.current not in self.flags:
                return False, "the Now card is not flagged"
            self.flags.pop(self.current)
            return True, None
        if key == "Z":
            if not self.history:
                return False, "nothing to undo"
            h = self.history.pop()
            if h["prev"] is None:
                self.filings.pop(h["q"], None)
            else:
                self.filings[h["q"]] = h["prev"]
            self.filed_row = {"kind": "undone", "q": h["q"], "seq": (h["prev"] or {}).get("seq")}
            return True, None
        if key == "X" and self.current in self.flags and self.current not in self.filings and \
                (self.filed_row or {}).get("q") != self.current:
            self.note_next.add(self.current)
            return True, f"the next reply to {self.current} is kept as a note"
        q, seq = self._target(seq_of_turn)
        if q is None:
            return False, "no question to file under"
        item = self.items[q]
        if key == "X":
            heard = self._heard_of(seq)
            self._file(q, {"by": "note", "option": None, "tier": None, "seq": seq, "heard": heard,
                           "verdict": "nothing"})
            self._keyed(seq)
            self.filed_row = {"kind": "kept_note", "q": q, "seq": seq}
            return True, None
        if key == "0":
            if not item.get("escape"):
                return False, f"{q} has no escape"
            option = {"escape": True}
        else:
            n = int(key)
            opts = item.get("options") or []
            if not opts:
                return False, f"{q} takes a {item['kind']}; X keeps the reply as a note"
            if n > len(opts):
                return False, f"{q} has no option {n}"
            option = {"picks": [n]}
            prev = self.filings.get(q) or {}
            if item["kind"] == "multi" and prev.get("by") == "key" and (prev.get("option") or {}).get("picks"):
                picks = list(prev["option"]["picks"])
                picks = [p for p in picks if p != n] if n in picks else (picks + [n])[-int(item.get("pick") or 2):]
                option = {"picks": sorted(picks)} if picks else {"unclear": True}
        self._file(q, {"by": "key", "option": option, "tier": None, "seq": seq, "heard": self._heard_of(seq)})
        self._keyed(seq)
        self.filed_row = {"kind": "keyed", "q": q, "seq": seq}
        return True, None

    def _keyed(self, seq: int | None) -> None:
        if seq is not None and seq in self.turns and not self.turns[seq]["done"]:
            self.keyed_seqs.add(seq)

    def _heard_of(self, seq: int | None) -> str | None:
        for ev in reversed(self.events):
            if ev["seq"] == seq:
                return ev["heard"]
        return None

    def _move(self, q: str) -> None:
        self.current, self.state = q, ("answered" if q in self.filings else "listening")

    def _next_unanswered(self) -> str | None:
        i = self.order.index(self.current) if self.current in self.order else -1
        for qid in self.order[i + 1:] + self.order[:max(i, 0)]:
            if qid not in self.filings:
                return qid
        return None

    # -------------------------------------------------------------------------------------------- views

    def done(self) -> bool:
        return self.model_done or all(qid in self.filings for qid in self.order)

    def counts(self) -> dict:
        by = [f["by"] for f in self.filings.values()]
        return {"filed_by_box": by.count("box"), "filed_by_key": by.count("key"), "filed_as_notes": by.count("note"),
                "own_notes": len(self.notes), "items": len(self.order)}

    def _row_view(self, row: dict | None) -> dict | None:
        """A Filed row with the filing it shows, when it shows one."""
        if not row:
            return None
        row = dict(row)
        if row.get("q") in self.filings and row["kind"] in ("sure", "likely", "keyed", "kept_note"):
            row["filing"] = self.filings[row["q"]]
        return row

    def card(self) -> dict:
        """What the card shows, as the server holds it."""
        row = self._row_view(self.filed_row)
        return {"rev": self.rev, "current": self.current, "n": (self.order.index(self.current) + 1) if self.current else 0,
                "N": len(self.order), "state": self.state, "listening": self.listening, "done": self.done(),
                "flags": dict(self.flags), "note_next": sorted(self.note_next), "filed_row": row,
                "heard_row": self.heard_row, "filings": dict(self.filings), "counts": self.counts(),
                "frames": {qid: frame_of(self.frames, qid) for qid in self.order}}

    def page_data(self) -> dict:
        items = [{k: it.get(k) for k in ("id", "kind", "question", "options", "escape", "spoken", "unit", "pick")}
                 for it in self.q["items"]]
        with self._cv:
            card = self.card()
        return {"questionnaire": self.q.get("path"), "items": items, "card": card, "run": self.run_dir.name,
                "constants": {"turn_open_s": TURN_OPEN_S, "turn_end_hold_s": base.TURN_END_HOLD,
                              "turn_min_s": TURN_MIN_S, "still_working_s": STILL_WORKING_S,
                              "give_up_s": GIVE_UP_S, "silence_pause_s": SILENCE_PAUSE_S, "sample_rate": 24000}}

    # -------------------------------------------------------------------------------------------- the log

    def _write_events(self) -> None:
        with self._cv:
            rows = [dict(e) for e in self.events]
        with self._io:
            _write_jsonl(self.run_dir / "events.jsonl", rows)

    def _write_session(self, *, ended: str | None = None) -> None:
        with self._cv:
            body = {"spec": "152", "questionnaire": self.q.get("path"), "mode": self.mode, "started": self.started,
                    "ended": ended or now_iso(), "turns": len(self.events), "keys": self.keys, **self.counts(),
                    "items": {qid: {k: f.get(k) for k in ("by", "label", "option", "tier", "seq", "frame_missing")}
                              for qid, f in self.filings.items()},
                    "notes": list(self.notes), "current": self.current, "done": self.done()}
        with self._io:
            _write_json(self.run_dir / "session.json", body)

    def close(self) -> None:
        self._write_events()
        self._write_session(ended=now_iso())


# ------------------------------------------------------------------------------------------------ HTTP

def _shown_from(raw: str | None) -> dict:
    out = {}
    for part in (raw or "").split(","):
        if ":" in part:
            s, t = part.split(":", 1)
            try:
                out[int(s)] = float(t)
            except ValueError:
                continue
    return out


def _num(v: str | None) -> float | None:
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


class Handler(BaseHTTPRequestHandler):
    session: Session = None  # set by make_server
    server_version = "keel-copilot-prototype"

    def log_message(self, fmt, *args):     # quiet: the run folder is the log
        return

    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj) -> None:
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json")

    def _foreign(self) -> bool:
        """A POST from another site's page (a browser sends its Origin) is refused: only this page files."""
        origin = self.headers.get("Origin")
        if not origin:
            return False
        host = urlparse(origin).hostname
        return host not in ("127.0.0.1", "localhost")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/copilot.json":
            return self._json(200, self.session.page_data())
        if path in STATIC:
            name, ctype = STATIC[path]
            return self._send(200, (HERE / name).read_bytes(), ctype)
        return self._json(404, {"error": f"no {path}"})

    def do_POST(self):
        url = urlparse(self.path)
        if self._foreign():
            return self._json(403, {"error": "only the copilot page may post"})
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try:
            if url.path == "/turn":
                a = {k: v[-1] for k, v in parse_qs(url.query).items()}
                if "seq" not in a:
                    raise BadTurn("seq is required")
                out = self.session.turn(who=a.get("who", ""), seq=int(a["seq"]), wav=body,
                                        started_at=_num(a.get("started_at")), ended_at=_num(a.get("ended_at")),
                                        mode=a.get("mode"), shown=_shown_from(a.get("shown")))
                return self._json(200, out)
            if url.path == "/key":
                k = json.loads(body or b"{}")
                seq = k.get("seq_of_turn")
                shown = {int(s): float(t) for s, t in (k.get("shown") or {}).items()}
                out = self.session.key(key=str(k.get("key") or ""), seq_of_turn=int(seq) if seq is not None else None,
                                       at=_num(k.get("at")), shown=shown, resume=bool(k.get("resume")))
                return self._json(200, out)
        except (BadTurn, ValueError) as bad:
            return self._json(400, {"error": str(bad)})
        except Exception as broke:                                          # noqa: BLE001 -- the page files it by key
            return self._json(500, {"error": type(broke).__name__})
        return self._json(404, {"error": f"no {url.path}"})


def make_server(session: Session, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    handler = type("CopilotHandler", (Handler,), {"session": session})
    httpd = ThreadingHTTPServer((HOST, port), handler)
    httpd.daemon_threads = True
    return httpd


def absent_keys(env) -> list[str]:
    return [n for n in (OPENAI_KEY_VAR, ANTHROPIC_KEY_VAR) if not (env.get(n) or "").strip()]


def main(argv: list[str] | None = None, env=None) -> int:
    env = os.environ if env is None else env
    ap = argparse.ArgumentParser(prog="python -m evals.copilot.prototype.server", description=__doc__.split("\n\n")[0])
    ap.add_argument("--port", type=int, default=int(env.get("PORT") or DEFAULT_PORT))
    ap.add_argument("--questionnaire", default=None, help="a questionnaire fixture (default the committed one)")
    ap.add_argument("--runs-dir", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    try:
        keys = clients_mod.keys_from(env)
    except SystemExit:
        print("copilot-prototype refuses: " + " and ".join(absent_keys(env)) + " not set in this shell -- the "
              "prototype calls gpt-transcribe and Haiku 5.5 on every turn; the keys go into the request headers "
              "alone, never logged, echoed or written", file=sys.stderr)
        return 2
    q = qmod.load(a.questionnaire)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(a.runs_dir or RUNS_DIR) / f"{stamp}-copilot-prototype"
    session = Session(q, clients_mod.HttpClients(keys), run_dir)
    try:
        httpd = make_server(session, a.port)
    except OSError as busy:
        print(f"copilot-prototype refuses: port {a.port} on {HOST} is not free ({busy.strerror}); PORT= another",
              file=sys.stderr)
        return 2
    print(f"copilot-prototype: http://{HOST}:{a.port}/  (open it in Chrome)")
    print(f"  questionnaire {q['path']} · {len(q['items'])} items · log {run_dir} · Ctrl-C ends the session")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        session.close()
        c = session.counts()
        print(f"copilot-prototype: ended · {len(session.events)} turns · {c['filed_by_box']} filed by the box, "
              f"{c['filed_by_key']} by key, {c['filed_as_notes']} as notes · {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
