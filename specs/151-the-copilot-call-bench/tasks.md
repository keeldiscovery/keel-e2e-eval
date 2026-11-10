# Tasks 151 -- The copilot call bench

Branch `spec-151`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-151` (`.git` a file, asserted first),
cut at `430eadf` (the spec). Built by a builder (Claude Opus 5.5) on 2026-11-10 ET. Nothing paid: no key read or looked
for, no model called, no audio rendered, no stack, no cycle. Not merged; master untouched; every commit pushed as it
landed. Plan: `plan.md`. Read only: the main checkout's `runs/20261109T195556Z-backtest-08-fresco/backtest.json` (the
fixture's source; nothing else copied) and keel-cloud-docs' `classify-answer.md` (for the tiers' words).

| Commit | What |
|---|---|
| `34ea98a` | plan.md and tasks.md before code |
| `555e19f` | FR-1..FR-3: questionnaire + fixture, catalogue, plans, writer + fake writer |
| `bd51d9b` | FR-4..FR-7: renderer, three stacks + fakes, three instructions, bars, scorer, sheets/page, `make copilot-bench` |
| `e127dda` | FR-8/FR-9: AGENTS.md paragraph, `tests/test_copilot_bench.py` (74), R1's duplicate dropped (608) |
| (this) | tasks.md |

## What was built, per FR

- [x] **FR-1** `evals/copilot/questionnaire.py`; `evals/copilot/fixtures/questionnaire-08-fresco.json` written from the
  bundle. **The bundle serves one link (COMMERCIAL_B2B, scope COMMERCIAL), not three**: the fixture carries its six items
  (q1 value_box -> number in hours; q2 price_ladder, q3 single_choice, q4/q6 fixed_four, q5 duration_bands -> single).
  The extractor takes every link a bundle serves, its gate (-> `gate`, Yes/No) and story prompt (-> `free`) included,
  proven on a two-link fragment (`tests/fixtures/copilot/backtest-fragment.json`). Controls mapped beyond the spec's two:
  `cost_total` -> number; `single_choice`, `fixed_three`, `fixed_four`, `scale_four`, `duration_bands`,
  `benefit_with_advantages` -> single; `pick_two`, `pick_one_then_one` -> multi pick 2; an unknown control is refused.
- [x] **FR-2** `catalogue.py`: the 18 founder habits and 9 respondent behaviours, verdicts, tiers, states; each kind's
  item kinds, first round, verdict / tier, state after, `offers_options`; `expected_tier` (a story prompt or a changed
  meaning caps an answer at *likely*); `validate()` = the form + clocks + round length + every turn's kind rule + every
  planned kind present.
- [x] **FR-3** `plan.py` (R1 608 = every applicable item x habit x behaviour, cap 700 with a seeded draw; R2 200, R3 120,
  R4 12, seeded); `writer.py` (Sonnet 5.5, `instructions/script-writer.md`, rewrite once with the faults, the first reply
  passed back unchanged, then drop + count; `FakeWriter` composes every round's entries from templates and all pass the
  same rules); `sample_markdown` (`SAMPLE=20`).
- [x] **FR-4** `render.py`: `synth.tts` per turn (founder card-reading instruction / the noise check's), one timeline,
  16-bit PCM tracks, `turns.json` clocks, the bed on at most a tenth of R3.
- [x] **FR-5** `stacks/` (turn_by_turn, running_state with `LiveTranscriber`, audio_direct), `clients.py` (the only
  network code), `fakes.py`; instructions `copilot-match.md`, `copilot-state.md`, `copilot-audio.md`.
- [x] **FR-6** `bars.py`, `score.py` (A--G, certificate, costs), `report.py` (sheets, page, register).
- [x] **FR-7** `bench.py` + `make copilot-bench` (refuses without ROUND/LEVEL; without both keys unless DRY).
- [x] **FR-8** AGENTS.md: one paragraph after the noise-capture certificate's; "four named places" unchanged.
- [x] **FR-9** `tests/test_copilot_bench.py`, 74 tests, no key, no call (requests.post and the socket refused in the DRY
  tests).
- [x] **FR-10** nothing else moved (the noise check imported, never edited).

## Judgement calls

1. Truth form + one optional turn key `kind` (A's confusion matrix by habit kind needs it). Respondent answers carry
   `verdict: null`; a follow-up reply `follow_up`; a counter-question or second voice `nothing`.
2. `any_order` is shown by the order asked, not by one turn (`SCRIPT_KINDS`).
3. R1's `clarifying` habit is not its own axis: every counter-question script carries the clarifying line (614 -> 608).
4. **E.unsure** reads unsure calls on the answers the script says were readable: the catalogue writes unclear answers
   on purpose (about a fifth of R1), so a perfect box would fail the 10% bar on the raw rate; the raw rate is in the
   sheet. E.honest with no unsure call is met vacuously.
5. Rounds gate: R1 A, B, E, G; R2/R3 + C, D; R4 + F. Outside its round a cell is *not applicable*.
6. `SAMPLE=` stops after scripts + sample.md; DRY appends no register row; a paid run exits 0 when one stack PASSes.
7. The live socket is fed as fast as it is read (not at speaking pace); `parts.transcribe` is commit -> transcript.

## Mechanical rules (FR-3 acceptance)

Rule on the words: verbatim (= stem), light_reword / story_prompt (not the stem -- weak), options_own_words (no label),
options_reordered_or_missing (not all labels in Keel's order), preface (ends with the stem after 3+ words), restart (a
break), clarifying (follows a counter-question on its item), follow_up (after the answer), follow_ups_in_a_row (2+),
own_note (no q), any_order, went_back, answered_for_them, back_channel (no `?`, no q), straight (<= 15 words, reads),
story_first (>= 20 words, reads), late_negation (a correction in the last two thirds), number_for_yes_no (a number),
different_question (unclear), counter_question (ends `?`), interrupted (ends `--`), two_voices (beside a respondent
turn, reads nothing). **No rule on the words**: meaning_changed (only "not the stem"), stacked, leading, hedged --
meaning, not form; their verdict / tier is checked and the reviewer reads the sample.

## Gate

`make unit`, whole and unpiped, against keel-cloud-docs master `37cac581` (spec 244 landed there during the build:
contract 65, document 37) and keel-web at its head:

- Before (`430eadf`, the spec only): **3 failed, 5793 passed, 81 skipped in 338.78s**, exit 2.
- After (`e127dda`, the last code): **3 failed, 5867 passed, 81 skipped in 320.04s**, exit 2 -- the same three, all
  sibling pins on keel-cloud 244 and none of this spec's: `test_cloud_233_mirror_144::test_the_contract_is_63`
  (65 != 64), `test_cloud_243_web_184_mirror_149::test_the_contract_is_64_and_the_screen_contract_25`,
  `test_sharing_130::test_document_version_36` (37). Tests +74 (`tests/test_copilot_bench.py`), 0 new failures.
- `tests/test_copilot_bench.py` alone: 74 passed in 1.2 s.
- `make copilot-bench ROUND=1 LEVEL=text DRY=1` with neither key in the shell: exit 0, three scripts kept,
  `runs/20261110T210048Z-copilot-bench-r1-text/` (sample.md, sheet.md, page/ ...); each stack INCOMPLETE (three scripts
  leave A.options_own_words and A.meaning_changed unmeasured), A/B 100%. Without DRY and without keys: refused, exit 2.
- Lint: the repo has no lint target; `ruff check --isolated --line-length 120 --select F,B,E,W` on `evals/copilot` and
  the test file: clean (ruff installed into the worktree's venv for the check only).

## Owed (a later spec or the first paid run)

- The Realtime transcription session shape (`session.update` type transcription, `audio.input.format`,
  `turn_detection: null`, the `completed` event) and gpt-audio-mini's chat body are written from the vendors' documented
  shapes and pinned only by fakes: the first R1 audio run is their check. `keywords` are not sent to the live model
  (no documented field; the stems go in its prompt). `websockets`, numpy and soundfile are not in `requirements.txt`.
- gpt-audio-mini's text-token rates are not on the page: counted, priced 0.
- The bundle serves one link: a three-link fixture needs a FULL back-test bundle (any entry, `QUESTIONNAIRE=`).
- The page's Baseline (embedding similarity) and the Spread (three trials a call) are not built.
- keel-cloud-docs master moved to spec 244 (contract 65, document 37) during this build: the three mirror pins in the
  gate fail at the floating head and are another spec's (FR-10).
