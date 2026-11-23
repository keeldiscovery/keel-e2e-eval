# Spec 160 -- Both interviewers, the same walk: the pared-down player on the orb and the face

keel-web 256 (merged 3b19090c, 2026-11-23) pared the respondent player down: one first screen with one button (the mic
test becomes Start; no mic = a hard block), the film with two icon buttons and *Begin the interview*, the replay mark in
place of *Say it again*, the speaker (orb or face) large with the question's words lit while it speaks and small while it
listens, and a green tick on the last page. The founder's rule (2026-11-23): "test for both the interviewers and ensure
that it is in sync". Spec 159's walks read the old screens; this spec moves them and adds the sync check.

## Rules

- **FR-1 The mirrors move.** Every read keel-web 256 lists under *Eval mirrors to move* in its `tasks.md`
  (`specs/256-the-player-pared-down/tasks.md` in keel-web, lines 188-217) moves: `start-talking` -> `ai-start`;
  `ai-mic-fallback` and its line -> `ai-mic-block` and *This interview needs your microphone.*; the intro heading
  *{founder} has {n} questions for you.*; the orb's name and the not-a-person line on both speakers; the facts become
  chips (*About N minutes*, *Microphone needed*, *Sound on*); the transcriber and microphone lines inside the closed
  `ai-intro-answers`; `ai-story-orb` gone; the chip *{name} · AI interviewer* in `ai-caption` / `ai-facecol`;
  `ai-story-go-on` -> wait for `ai-film-begin` and press it; `ai-film-pause` / `ai-film-again` / `ai-film-board`;
  `filmOrb` always false; the done page's title *Done. Your answers have gone to {founder}.* over `ai-done-tick`;
  `ai-again` -> `ai-replay`; `data-layer="full"` / `ai-still` -> `ai-facecol[data-size]`. `interviewer_screens.py`,
  `interviewer_leg.py`, `three_views_strangers.py`, `story_screens.py` and their unit mirrors (`tests/`) follow.
- **FR-2 The refused mic is a block.** Spec 159 FR-3's refused-mic link (walked by taps to its end) becomes: the mic
  refused -> `ai-mic-block` with its line, no `ai-start`, no stage, no question ever drawn; *Test your mic* retried after
  the seam allows the mic -> `ai-start` appears. One link per study, both speakers.
- **FR-3 The same walk on both speakers.** For each study, the orb link and the face link are walked through the same
  states in the same order and the walk records, per step, the state word, the speaker's size (`large` while it
  asks, `small` once the sheet opens), the ids present, and the words lit while it speaks. The check: the two records
  are equal step for step except the speaker's name and the face's own clip routes. Where the pared-down player is in
  one state on the orb and another on the face, the leg fails by name and says which step. The same-words check of
  159 FR-2 (the opening and one item say the same words, by clip key) stays.
- **FR-4 The film.** On both speakers: no orb and no face above the board; `ai-film-pause` flips and holds the drawing;
  `ai-film-again` restarts; a tap on `ai-film-board` shows the lines and a second tap hides them; the film's end draws
  `ai-film-begin` and nothing plays until it is pressed; after the press the opening clip plays and the speaker is
  drawn. The founder's own story player (`define/story`) is unchanged: 158's checks on it stay as they are.
- **FR-5 The replay mark.** On one item per link, `ai-replay` is pressed: the item's clip plays again (the orb: the
  same `/v2/clips/{id}`; the face: her clip) and the window reopens; `ai-again` is nowhere.
- **FR-6 The last page.** `ai-done-tick` present, the title as served, *Microphone off*, *What is Keel?*; the served
  thanks sentence is not drawn (keel-web 256 judgement call).
- **FR-7 Untouched.** The copilot legs; the founder's legs (FR-1a-d); the ledger checks (nothing bought); the charge
  checks; `PROFILE=remote` untouched.
- **FR-8 Report and DRIFT.** The report's *The orb* section becomes *The two speakers*: one row per study per speaker
  with the state sequence, the sizes, and the same-walk verdict. Every web finding goes to `runs/DRIFT.md` with the
  usual shape. Contract 84 unchanged.

## Acceptance

`make unit` with no new red; a local `make e2e-157 PROFILE=eval` against the sibling main checkouts keel-cloud-docs
`8bd57d6f` and keel-web `3b19090c` (or later) with every 160 check held or a DRIFT entry naming the web defect; the
founder's legs and the copilot legs unchanged and green; nothing paid (FakeSpeech, the fake avatar, the fake
transcriber). The run on merged masters is the integrator's run of record.
