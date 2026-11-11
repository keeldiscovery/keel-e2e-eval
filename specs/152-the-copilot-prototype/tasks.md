# Tasks 152 -- The copilot prototype

Branch `spec-152`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-152` (`.git` a file, asserted first),
cut at `c86bd08` (the spec). Built by a builder (Claude Opus 5.5) on 2026-11-11 ET, while the bench's paid audio run
went on from the main checkout (untouched). Nothing paid: no key read or looked for, no vendor called; the server is
exercised on `FakeClients`, and the page was driven once end to end in Node against a fake-client server (a stub DOM and
Web Audio, synthetic levels; a scratch harness, not committed). Not merged; master untouched; every commit pushed as it
landed. Plan: `plan.md`.

| Commit | What |
|---|---|
| `79343c6` | plan.md and tasks.md before code |
| `cddc6f1` | FR-1/FR-4: the server (Stack 1 live, the record, the keys, the order, the run folder) and `frames.json` |
| `e2ef594` | FR-1: `make copilot-prototype` (one-line refusal, exit 2); the Filed row carries its filing |
| `9cfa856` | FR-2/FR-3/FR-5: the page (sources, rehearsal, cutting, WAV, the card's states, keys, Float) and the tests |
| `c1eba6e` | FR-6: AGENTS.md paragraph |
| (this) | tasks.md closed |

- [x] T1 plan.md and tasks.md before code
- [x] T2 FR-1 `evals/copilot/prototype/server.py`: `Session` (turn, keys, ordering, record), `Handler` (GET the three
  files + `/copilot.json`, POST `/turn`, POST `/key`), `main` (refusal, URL, run folder). Turn transport: the WAV as
  the body, `?who=&seq=&started_at=&ended_at=&mode=` (documented in the module docstring).
- [x] T3 FR-4 the log: `turns/<seq>-<who>.wav`, `events.jsonl` (bench shape + `heard`, `reply`, `parts`, `seq`, `who`,
  `wall{started_at, ended_at, shown_at}`, plus `audio`, `late`, `superseded`), `keys.jsonl`, `session.json`
  (questionnaire, mode, started, ended, `filed_by_box` / `filed_by_key` / `filed_as_notes`, own notes, items, notes).
- [x] T4 FR-3 `frames.json`: window / unit / anchor for q1-q6, keyed by the fixture's ids.
- [x] T5 FR-2/FR-3 `copilot.html`, `copilot.js`, `copilot.css` (the UX page's tokens and card classes, no web fonts).
- [x] T6 FR-1 `make copilot-prototype [PORT=] [QUESTIONNAIRE=]`.
- [x] T7 FR-5 `tests/test_copilot_prototype.py` (26 tests).
- [x] T8 FR-6 AGENTS.md paragraph under the bench's.
- [x] T9 tasks.md closed.

## Judgement calls (see plan.md "Decisions")

1. **A fourth GET.** The page needs the questionnaire, the frames and the record without templating, so the static
   route also serves `GET /copilot.json`. `frames.json` itself is not served as a file.
2. **Cross-side order.** The classify step waits for every earlier turn of *either* side (capped at 20 s a turn), not
   only its own side's: a respondent's quick answer must be read against the question the founder just asked.
   Transcription runs at once, in parallel.
3. **Empty transcript not classified** (heard nothing; on the respondent's side the hand-over with the options).
4. **A key beats a late reply** for the same turn (`superseded: true` on the event); a late turn moves nothing a later
   turn already moved (`late: true`).
5. **`X` on a flagged Now card** with nothing filed under it arms "keep the next reply as a note" (the UX page's
   "X will keep the reply as a note"); otherwise `X` keeps the Filed row's reply as a note.
6. **`P` on the five-minute pause** clears the pause and keeps listening (`resume`), rather than toggling listening off.
7. **`R`, `T`, `Esc`** are the page's; they are posted too so `keys.jsonl` holds every key pressed (`applied: "page"`).
8. **Turn side in rehearsal** is fixed when the turn opens (press `T` before speaking as the other side).
9. **Posts are not serialised by the page.** Each turn is posted the moment it is cut; the in-flight turns are kept in
   seq order on the page and the server holds the order (so a hung post never holds the next one back).
10. **Origin check.** A POST carrying another site's `Origin` is refused (403), so only the page files.

## Not done, and why

- **"Two questions in one breath: the second queued."** Stack 1's instruction returns only the first question's id for a
  `stacked` verdict; the second cannot be known without changing `instructions/copilot-match.md`, which FR-7 forbids.
  The card shows the first; the founder moves on with `→` or by asking the second again.
- **Not run in Chrome by the builder.** The page's JavaScript was syntax-checked and driven in Node with stubs
  (turn cutting, posting, the Filed row sure / likely / by you / undone / own question / heard nothing / working / 5 s / 20 s / late, the keys,
  the pause; Done is covered by the unit tests only); Document PiP, `getUserMedia` / `getDisplayMedia` and focus across windows are for the founder's hand test.
