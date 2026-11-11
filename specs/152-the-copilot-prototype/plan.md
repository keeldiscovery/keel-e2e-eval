# Plan 152 -- The copilot prototype

**Branch** `spec-152` | **Worktree** `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-152` | **Spec** `spec.md` beside this
file | **Design of record** the UX page of 2026-11-11 (`copilot-ux-from-the-bench.html`, artifact LDexgdh49E9oAzpQZ27nGz v1).

## Summary

Stack 1 of the bench, live: a stdlib `ThreadingHTTPServer` on 127.0.0.1 that serves one vanilla page and, per turn the
page cuts, calls exactly what `TurnByTurn.run` calls (`transcribe` with `base.keywords` and `TRANSCRIBE_PROMPT`, then
`haiku_body(instruction('copilot-match.md'), match_prompt(...))`, `read_reply`, `event_from`, `advance`) and keeps the
founder's filings (box, keys, notes) as the server's record. The page cuts turns on two sources (microphone = founder,
shared Meet tab = respondent; or one microphone and `T` in rehearsal), posts each as a 16-bit mono WAV, and draws the
UX page's card (Now / Heard / Filed / keys) in a Document Picture-in-Picture window. Every turn, event, key and the
session's counts are logged to `runs/<ts>-copilot-prototype/` in the bench's event shape. Nothing in `stacks/`,
`score.py`, `bench.py`, `catalogue.py` or `instructions/` moves.

## Technical context

- Python 3.12 (the repo's `.venv`), stdlib only on the server (`http.server`, `wave`, `threading`, `json`); the vendor
  calls go through `evals.copilot.clients.HttpClients` (already `requests`). No new dependency.
- The page: one HTML, one JS, one CSS, Chrome desktop (Document PiP needs Chrome 116+). Web Audio: an `AnalyserNode`
  per source for the level, a `ScriptProcessorNode` for the samples (no worklet module, so the page references only its
  three files), `AudioContext({sampleRate: 24000})`.
- Tests: `tests/test_copilot_prototype.py`, pytest only, the server on an ephemeral port against `FakeClients`; the
  page's JavaScript read as text.

## Layout

```text
evals/copilot/prototype/
  __init__.py
  server.py       FR-1 Session (the record, the keys, the ordering) + Handler + main() (refusal, URL, run folder)
  copilot.html    FR-2/FR-3 the page: sources, rehearsal, Float, the card host, the turn log
  copilot.js      FR-2/FR-3 turn cutting, WAV encoding, posting, the card's states, the keys, PiP
  copilot.css     FR-3 the UX page's tokens and card classes (.cp .h .q .frame .heard .filed .opts .foot ...)
  frames.json     FR-3 frame pills by item id (data: window, unit, anchor)
tests/test_copilot_prototype.py   FR-5
Makefile          make copilot-prototype [PORT=] [QUESTIONNAIRE=]
AGENTS.md         FR-6 one paragraph under the bench's
```

## Decisions

1. **Turn transport.** `POST /turn?who=founder|them&seq=n&started_at=s&ended_at=s&mode=share|rehearsal` with the WAV as
   the body (`audio/wav`); wall clocks are epoch seconds from the page (the bench's clocks are seconds). The server
   checks the WAV is 16-bit mono and writes it as `turns/<seq>-<who>.wav` before any call.
2. **The page's data.** The page needs the questionnaire, the frames and the record: one more GET under the static
   route, `GET /copilot.json` (items, frames, constants, the card). Still no templating: the HTML is a plain file.
3. **Ordering.** Each request runs in its own thread. Transcription runs at once (it needs only the current question
   for `keywords`); the classify step waits for every turn that arrived earlier (either side) to finish, **or to have
   been running 20 s**, then reads `current`/`state` and applies `advance` under one lock. So turns are classified in
   arrival order per side (and across sides, which keeps `current` right when the respondent answers before the
   founder's question has been read), and a hung turn never blocks the next one past 20 s; it still completes and is
   recorded when it does.
4. **A key beats a late reply.** If the founder filed a turn's question by key (`seq_of_turn`) while it was stuck, the
   late event is recorded (`superseded: true`) but does not overwrite the founder's filing.
5. **Empty transcript.** An empty transcript is not sent to the classifier (it could only guess at `They said: ""`): the
   event carries `heard: ""`, the question at arrival, no verdict; on the respondent's side it is the "heard nothing"
   hand-over with the options numbered. Logged with `parts.classify: 0`.
6. **What files where.** A respondent event with an option and tier sure/likely is filed by the box; unsure (or
   `{"unclear": true}`, or an unparsed reply) is a hand-over, filed by nothing until a key; `follow_up` / `nothing` on
   the respondent's line is kept as a note under the question. A founder `follow_up` or `own_note` is "your own
   question, kept as a note under Qn" (the question current, or before Q1). `meaning_changed` flags the current
   question with the frame pills absent from the heard words (token match, case and punctuation ignored); `F` clears it.
7. **Keys on the server.** `1`-`6` pick (a multi item toggles picks up to its `pick`), `0` escape, `X` note (the Filed
   row's reply kept as a note; if the Now card is flagged and nothing is filed under it yet, the next reply to it is
   kept as a note), `F`, `Z` (a history stack: every filing, box or key, and every X note is undoable), `→`/`Space`,
   `←`, `P`. `R` (ask again: the spoken form, large), `T` (rehearsal side) and `Esc` (float / return) are the page's;
   the page posts them too so `keys.jsonl` holds every key pressed (`applied: "page"`).
8. **Done.** When every item is filed (box or key) or kept as a note by `X`, or the model says `done`.
9. **`shown_at`.** The server stamps `wall.shown_at` when it sends the reply (same machine as the page); the page sends
   its own measured `shown` times back on its next request and they replace the server's.
10. **Log rewrite.** `events.jsonl` and `session.json` are rewritten whole (tmp + rename) on each change so a late
    `shown_at` lands on its event; `keys.jsonl` is appended.
11. **Refusal.** `make copilot-prototype` refuses in one line, exit 2, when either key is absent; `server.main` does the
    same itself via `clients.keys_from` (the message names the variables, never a value).

## Gate

`tests/test_copilot_prototype.py` and `tests/test_copilot_bench.py` green; the new Python byte-compiles; `make -n
copilot-prototype` shows the command. Nothing paid, no vendor called, no key looked for.
