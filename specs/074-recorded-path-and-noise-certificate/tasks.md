# Tasks 074 -- The harness follows keel-web 115 (one recorded path), and the noise-capture certificate

Branch `074-recorded-path-and-noise-certificate` off master `104aa11` (worktree `wt/eval-074`, `.git` a file). The
products, read only: keel-cloud-docs master `409d38d1` (136 the partial pick and the text-hearing fake transcriber,
137 the classifier's cap 400, 138 the public sample routes; contract 40; corpus revision 16) and keel-web master
`f0b78b2` (115 one recorded path, 116 the release after the last clip, 117 the occasion on the card, 118 Try one
heard, 119 *Hear it in a loud place*, 120 auto gain control named). The stack built from those checkouts through the
four symlinks beside the worktree (`wt/keel-cloud-docs`, `wt/keel-web`, `wt/keel-runtime`, `wt/keel-connect-skill`,
made 2026-10-25), keel-runtime 0.8.0 bundled in keel-connect-skill. No paid command was run, no key was present.

One commit per FR group: the spec `a49af38`; FR-1 `a4b169d`; FR-2 `314f3ca`; FR-3 `1ef8e83`; FR-4 (this file, the
docs). Each gated on `make unit` green.

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `104aa11` against keel-web `f0b78b2` (before any change) | 3,362 | **2** | 53 |
| FR-1 `a4b169d` | 3,368 | 0 | 53 |
| FR-2 `314f3ca` | 3,401 | 0 | 53 |
| FR-3 `1ef8e83` (and FR-4: docs only) | 3,436 | 0 | 53 |

Master's two reds were this spec's subject: the fixture-parity test (keel-web 115 removed `__speechError`,
`__speechEnd`, `__recognisers` and the recogniser fake) and `INTRO_TRANSCRIBED` (115's new line). The hand-off's 3,364 /
53 was master against keel-web before 115.

## FR-1 -- the AI walks drive the recorder -- `a4b169d`

- [x] T001 `harness/interviewer_screens.SPEECH_SEAM` restates keel-web 115 FR-5's `installFakeSpeech`: the fake recorder
  (`start(onLevel)` ticking ten a second, `stop()`, `cancel()`) and the always-granted microphone (level 0.12, counted).
  `__say(text, final=True)`: a final is pushed to the window's words and the level pulses at 0.3 for three ticks
  (`SAY_TICKS`), a non-final keeps the level up and the words provisional; the next `stop()` returns the finals joined,
  then the provisional words, as UTF-8 zero-padded to 20 KiB (`PADDED_BYTES`), base64, `audio/webm`; `stop()` and
  `cancel()` forget them. `__listening()` is the recorder running. The harness's own, as before: no `classify` or
  `answer` stand-in (spec 048 judgement call 1), `earcons: false`, the page's quiet and beat; stamps on
  `__recordStarts` / `__recordStops` / `__recordCancels` / `__levels`, and now `__soundAt` (the last loud tick) and
  `__micReleasedAt` (every release; `__micReleased` counts them).
- [x] T002 Gone: the recogniser's fake, `__speechError` / `__speechEnd` / `__recognisers` / `__speechStarts`,
  `Player.ear()` / `wait_ear` (now `recorder()` / `wait_listening(newer_than=)`), `recorder_seam` (now
  `follow_up_cap_seam(ms)`, the AI follow-up's cap alone). `Player.classified` keeps every read the page sends --
  `interview/answer`, the founder's `interviewer/answer`, and a `classify` should one ever go -- with the words its
  recording carried (`decode_said`, keel-cloud 136 FR-2's trim). `Player.say`'s look inside the quiet is `still` when
  the status reads *Recording your answer. Pause when you're done.* (`RECORDING`) and the heard line *Hearing you…*.
  `veto` is said as a final (the hold records too; an interim would hold the recording open). `INTRO_TRANSCRIBED` is
  115's line. `FLOW_TIMELINE` keeps every clip's `ended`.
- [x] T003 `text_seam` drives the same recorder by a level (`SpeakBox.speak` / `quiet`), so its recording is the zeros
  alone and keel-cloud 136's fake answers its `otherwise`, `FAKE_TRANSCRIPT` -- the old seam's 4 KiB of *a spoken
  answer* would have been heard as text by 136's fake (D-01).
- [x] T004 `evals/interviewer_leg.py`: every spoken answer is `how` RECORDED (`SPOKEN_HOW`); the AI link's reads are
  `interview/answer` (held: every one 200, at least one a spoken closed answer, no `classify`); the dry run reads its
  own `interviewer/answer` (never `classify`); the pilot ask is said like every window; the read-aloud step waits for no
  recogniser restart (the same recording runs through the quiet). The `not-allowed` leg goes: S-005's follow-up (`by`
  `said`) says the line into both windows -- by the pause, then by *Save and next* -- each written down at
  `maxSeconds` 120 and held to the line; S-006's (`sound`) makes a sound and leaves the second window silent to its cap.
  Every follow-up window draws no banner (115 FR-3).
- [x] T005 keel-web 117: `Corridor.context_occasion` reads the occasion through the card's *I'll ask about* line's
  *Change* (`context-occasion-change`): the field in the line's place (`[data-testid=context-occasion]`,
  `#context-occasion`), pre-filled, focused, its hint; Esc puts the line back, nothing edited or saved; no
  `.cfield--occasion` block. `corpus_scenario.occasion_faults` holds it; a card with no served stem (the scripted
  executor writes the plain noun, the shape before keel-cloud 120) draws no line, no *Change*, no field (117 J-4), and
  the noun is held on the confirmed view instead (`GET context` `occasion.noun` == the entry's). Edit's form draws no
  occasion block (`context_reopened`).
- [x] T006 keel-web 119: Send more's row is picked by its name (`.fmt__name`), since the AI interviewer's radio carries
  *Hear it* inside it (its press opens the popup and does not choose the row).
- [x] T007 Unit: `tests/test_interviewer_screens.py` rewritten for the recorder (the names a walk drives in both, the
  retired ones in neither; `__say`'s three constants and its code pieces against keel-web's fixture text; a real-page
  run of the seam: two finals and a provisional word recorded as 20 KiB whose words are all three, the next window the
  zeros, `__listening()` only while it runs, the mic counted); `test_follow_up_ladder.py`'s seam keys;
  `test_revision_16_walk.py`'s no-node read.

## FR-2 -- marks follow the screens -- `314f3ca`

- [x] T010 Re-pinned (`INTERVIEWER_MARKS_VERSION` 8 -> 9), each why naming this spec:
  - **IM9** (044 / 048): a spoken answer is RECORDED, the page's one path; one saying SPOKEN fails.
  - **IM19** (049, hears them out): the first words leave the window recording (*Recording your answer.*, *Hearing
    you…*), and the two finals are one recording, one `answer` read whose words are both.
  - **IM21** (050, the beat): nothing recorded inside it; the recogniser's starts are not read.
  - **IM25** (051, two minutes and four seconds): every follow-up window is recorded -- by the pause (4 s +- 500 ms
    after the last sound, nothing pressed), by *Save and next* (inside the gap, `ai-save` alone) or to the cap -- each
    with words written down once at `maxSeconds` 120; the browser path's kinds retire; the short form owes the pause and
    Save, the full leg the pause and the cap.
  None dropped. Read as before (the walk drives them through the recorder): IM5, IM14-IM18, IM20, IM22-IM24, IM26.
- [x] T011 keel-web 116 FR-1 (in the leg since FR-1's commit): `_mic_off_after_thanks` reads *Microphone off* once the
  done screen shows it and holds the release to the thank-you's end -- no release stamped while it plays, at least one
  at or after its `ended`, no recording begun after its `play` (under the dev build's StrictMode one release is stamped
  at load, keel-web 116 D-03, so the count is read for not moving).
- [x] T012 keel-web 116 FR-2: S-005 presses *End* in the follow-up's second hold (the take is already the follow-up's,
  so the response is unchanged); `_pilot_after_end` holds the pilot ask that follows (*Last question*) recording on the
  kept stream -- a recording begun after the press, `__micReleased` unmoved -- and the release after the thanks.
- [x] T013 Unit: `tests/test_recorded_path_074.py` (32) and `tests/test_interviewer_marks.py` (v9: the good record
  RECORDED, the hearing look recorded, the beat by recordings, the windows by the recorded kinds; IM9's SPOKEN fault,
  IM25's browser and late-Save faults).

## FR-3 -- `make noise-check` -- `1ef8e83`

- [x] T020 `evals/noise/` moved from keel-cloud `canon/designs/noise-capture-check-2026-10-26/` (the canon keeps its
  copies, README and results): `dataset.py` and `page_template.html` byte for byte; `pipeline.py` for Keel's path alone
  (the direct model and the suppressors stay in the canon); `synth.py` writing under the samples' root; `report.py` for
  one pass with the certificate.
- [x] T021 The product's calls: gpt-transcribe (`json`, `languages[]`, one `keywords[]` per label and the escape, the
  prompt) then `claude-haiku-4-5-20251001`, temperature 0, max_tokens 400 (keel-cloud 137), the system prompt the cloud
  checkout's own `classify-answer.md` (`stack.toml`'s `keel_cloud`), the user lines as `KeelsAiClassifier.userPrompt`;
  one retry on a reply that is not the JSON; a reply cut at `max_tokens` recorded (`cut`). Plain HTTPS through
  `requests` (already a dependency); the keys from `KEEL_OPENAI_API_KEY` / `KEEL_ANTHROPIC_API_KEY` into the headers
  alone, refused by name, never echoed.
- [x] T022 `norm_out` restates `Classification.validated()` after `KeelsAiClassifier.parse`: options by number (digits
  as text too), the escape where the item has one, single / gate the first of two, pick-N the first N, number in range,
  and keel-cloud 136 FR-1 (`partial_pick`; off is the read before 136). The story's WER without `jiwer`.
- [x] T023 Samples from `KEEL_NOISE_SAMPLES` (default the kept set, `~/Documents/projects/keel-noise-check-2026-10-26/
  audio`), the manifest the canon's `samples.json` ids in order; `synth.synthesize` only for what is absent (its heavy
  deps lazy, refused by name; a take padded and mixed once).
- [x] T024 `runs/<stamp>-noise-check/`: `results.jsonl`, `run.json`, `summary.json`, `noise-check.md` (the certificate
  line, the rooms table, every cell against the bar, the 0 dB cells outside it, the controls table, the misses with
  their transcripts), `page/index.html`, `register-row.md`, the row appended to `runs/noise-check-register.md`. The
  certificate: quiet closed 100%; every bed at 20 / 10 / 5 dB > 90%; confident wrong <= 2% and stories >= 90% in each
  of those cells (the quiet room's too) -- PASS, FAIL naming the first failing cell, or INCOMPLETE for a partial run;
  exit 0 on PASS only. `--only`, `--snrs`, `--limit`, `--resume`.
- [x] T025 `make noise-check` (`ONLY=`, `SNRS=`, `LIMIT=`, `RESUME=`), refusing without both keys; in no other target;
  no `test_*.py` under `evals/noise/`; nothing in the matrix. **Not run** (the founder runs it).
- [x] T026 Unit `tests/test_noise_check.py` (34): the canon's 1,260 `stt-none` rows scored offline -- PASS with 136's
  read (quiet 100%, the worst loud cell the café at 10 and 5 dB, 97.9%), 41 of 42 pick-two rows now right (the one
  left, `c5-onyx-cafe-0`, heard the babble and named no label), nothing else moved; the read off reproduces the canon's
  scoring row for row and FAILs on `clean` (95.8% < 100%); `validated()` case by case; the calls held to keel-cloud's
  source; the move; the manifest; the keys; the run folder's files; INCOMPLETE, a confident-wrong cell and a lost story
  named, 0 dB never gating.

## FR-4 -- nothing else moves -- this commit

- [x] T030 `MARKS_VERSION` 20 and corpus `REVISION` 16 unchanged; no corpus, registry, fixture or golden number moved;
  `GUIDE_MARKS_VERSION` 3, `CONTACTS_MARKS_VERSION` 2, `FEEDBACK_MARKS_VERSION` 1, `SCOPE_MARKS_VERSION` 2,
  `REPORT_MARKS_VERSION` 2 unchanged; `INTERVIEWER_MARKS_VERSION` 9 by FR-2. The other paid commands untouched.
- [x] T031 AGENTS.md: the spec 074 paragraph and the noise-check argued among the paid places; README: the command in
  *Run*. This file.

## The journeys (local stack, keel-cloud-docs `409d38d1` + keel-web `f0b78b2`, the scripted executor)

`docker ps` before `make up`: only `focused_robinson`. Booted once with `make up`, the journeys one at a time with
`make eval K=...`, torn down with `make down`. Runs of record on `1ef8e83` (FR-3; FR-4 is docs only):

| Journey | Run | Result |
|---|---|---|
| S-015 | `runs/20261027T083112Z-s015-problem-only` | **passed** (89 s), SC1-SC7 7 of 7 (v2) |
| S-016 | `runs/20261027T083241Z-s016-money-only` | **passed** (77 s), SC1-SC7 7 of 7 (v2) |
| S-005 | `runs/20261027T083358Z-s005-countly` | **passed** (310 s): IM 23 of 23 (v9; the follow-up by the pause then Save, End in its hold, the pilot ask recording after it); guide 17 of 17; report 5 of 5 |
| S-006 | `runs/20261027T083909Z-s006-paidly` | **passed** (330 s): IM 29 of 29 (v9; the sound window 4 s after the last sound, the silent one to the cap); guide 5 of 5; report 5 of 5; contacts 13 of 13 |
| S-007 | `runs/20261027T084440Z-s007-mulchrun` | **passed** (134 s): report 5 of 5 |
| S-014 | `runs/20261027T084654Z-s014-green` | **passed** (137 s): report 5 of 5 |

`versions.json` on every run: keel-cloud `409d38d1` (dirty by its own uncommitted canon `report.py` and `.idea/`, no
`src/` change), keel-web `f0b78b2` (dirty by its untracked `specs/121-example-one-study/` and `.idea/`), keel-e2e-eval
`1ef8e83` (dirty by this commit's docs alone), keel-runtime `3988131`.

Earlier runs on the FR-1 + FR-2 code: S-005 `20261027T075633Z` failed at the occasion (the scripted card has no stem,
D-02 -- fixed in FR-1), S-005 `20261027T075931Z` failed G4 once (D-03), S-006 `20261027T080530Z` passed (IM 29 of 29,
v9), S-005 `20261027T081105Z` passed (IM 23 of 23, v9).

## Discovered

- D-01 keel-cloud 136's `FakeTranscriber` hears any audio that is UTF-8 text of at most 4 KiB, so the text box's old
  seam recording (`'a spoken answer ' * 256`, exactly 4,096 bytes of text) would have been transcribed as itself, not as
  the stack's `FAKE_TRANSCRIPT` -- the box's appended story would have grown by 4 KB. Fixed in the harness (the zeros).
- D-02 S-005's first run on the 117 build failed at the occasion: the scripted executor's CONTEXT_INTERPRET writes the
  plain noun (the shape before keel-cloud 120), so the card serves no stem, and keel-web 117 then draws no *I'll ask
  about* line, no *Change* and no field (117 J-4) -- on the scripted journeys the occasion is on no screen at all. The
  harness holds that absence and the noun on the confirmed view; the open-and-Esc read runs where a stem is served (a
  back-test on Keel's AI), and is unit-tested on 117's markup in a real page.
- D-03 S-005 `20261027T075931Z` failed G4 once: the second replay of the welcome, sought to its end, was not seen to
  close within 5 s. Passed on the next two S-005 runs; no keel-web change touched the guide between 113 and 120. A
  flake of the guide's seam timing, not this spec's; not filed.
- D-04 With 136's read the café at 0 dB (outside the bar) reads more answers and some of them wrongly: on the canon's
  rows its confident-wrong goes from 10.4% to 12.5% while its closed-right goes from 70.8% to 72.9%. Reported in the
  certificate's tables; nothing gates on it.

## Where the spec and the code disagreed

- *REVISION 17*: `REVISION` is the corpus reader's revision, which must equal keel-cloud's corpus (`revision: 16` in
  every file at `409d38d1`); at 17 every corpus file is refused and no journey runs. Kept at 16; `MARKS_VERSION` stays
  20 (no instruction mark moved). The marks that moved are the interviewer ruler's (v9).
- *IM5 ... re-pinned where they counted the recorder's banner, the recogniser's restart or the probe*: IM5 reads the
  stored thanks clips' scripts and nothing of the answer path, so it is not re-pinned. Of the answer-path marks of
  048-050, IM9, IM19 and IM21 read the recogniser and moved; IM14-IM18, IM20 and IM22 did not. Of 051's, IM25 moved;
  IM23, IM24, IM26 and IM27 did not (the box was on the recorder since keel-web 076). 052 carries no speak-or-type mark.
  No mark counted the recorder's banner or the box's probe.
- *the founder's walk that edits the occasion on S-005 presses Change*: no walk ever edited the occasion, and the
  scripted card draws no *Change* (D-02). Every walk opens *Change* where it is drawn, reads the noun and puts the line
  back with Esc; nothing is edited.
- *the pilot ask after End is asserted to record*: no walk pressed *End* before a pilot ask. S-005 now presses it in
  the follow-up's second hold, where the take is already the follow-up's, so the response does not move.
- *A row in the gallery's register as the back-tests have (`make gallery`)*: the gallery exports example studies into
  keel-web's `public/sample/`, and the back-tests' register is keel-cloud's judgement register, read and never written
  here. The noise-check's row goes to its own register beside the runs (`runs/noise-check-register.md`, kept with the
  run folders) and into the run folder (`register-row.md`); no gallery export changed.
- *the canon keeps its README and results ... with a pointer here*: the canon is keel-cloud's and read-only here; the
  pointer is owed there (keel-cloud-docs `canon/designs/noise-capture-check-2026-10-26/README.md` naming
  keel-e2e-eval `evals/noise/` and `make noise-check`).
- *every journey that speaks ... green on staging after keel-web 115 and keel-cloud 136 are deployed*: not run (no
  staging, no deploy, no push from this builder); owed to the session.

## Judgement calls

- J-1 **No stack override was added.** The symlinks beside the worktree (`wt/keel-cloud-docs` -> the keel-cloud-docs
  checkout, and the other three) make `stack.toml`'s relative paths resolve from the worktree to the checkouts named in
  the hand-off; `load_config` resolved `keel_cloud` / `keel_web` to them and the runs' `versions.json` names their shas.
- J-2 **The text box's recording is the zeros alone** (D-01), keel-web 115's fixture's own output for a window in which
  nothing was said, so the box's take still appends the stack's `FAKE_TRANSCRIPT`.
- J-3 **The veto is a final**: with the recogniser gone, an interim keeps the level up and the hold's recording open.
- J-4 **The certificate's confident-wrong and stories' limits apply to the quiet room too** (closed 100% already
  implies no confident wrong there); a partial run is INCOMPLETE, never PASS.
- J-5 **The two vendors are called over plain HTTPS** (`requests`), the bodies the product's SDK calls send, so the paid
  command adds no dependency; synthesizing absent samples needs numpy, scipy and soundfile, refused by name.
- J-6 **The canon's `synth.py` seeded each bed with `hash(name)`**, which Python randomizes per process; the moved copy
  uses a stable CRC of the name, and its mix never pads or re-mixes a take that is already there.
- J-7 keel-web 116 FR-3 (*Hear Livia* only while the mic is live): the walks tap `intro-hear` only on the
  Let-them-choose intro (IM29), which keeps its button; nothing moved. keel-web 118 (Try one heard) and 120 (auto gain
  control) meet no walk.

## Left open

- `make noise-check` on the founder's word: its certificate, run folder and register row.
- The six remote journeys on staging once keel-cloud 136 + keel-web 115-120 are deployed there.
- The canon's pointer to `evals/noise/` (keel-cloud).
- No DRIFT written.
