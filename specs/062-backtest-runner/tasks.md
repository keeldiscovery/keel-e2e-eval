# Tasks 062

Built against keel-cloud-docs master `bf0e20d`, keel-web `9f3845a` (the main checkout's HEAD when the run took it),
corpus revision 12, `MARKS_VERSION` 20 (unchanged).

- [x] T001 FR-1 `instructions/corpus.py`: `backtest_dir`, `BACKTEST_KEYS`, `load(keel_cloud, *, registry=None,
  directory=None, backtest=False)` and `load_file(..., backtest=False)`; `_check_backtest` -- `expected` absent or empty,
  `idea_name` a string of one to five words, `sources` ignored -- before every refusal a golden file gets; `Entry` gains
  `idea_name` and `backtest`. An empty or absent back-test directory is an empty corpus.
- [x] T002 FR-1 `harness/vectors_script.py`: `load` / `entry_for(..., backtest=True)`; `founder_idea_name` falls back to
  the entry's `idea_name` after `IDEA_NAMES`.
- [x] T003 FR-1 `tests/test_backtest.py` (22): every file in keel-cloud's back-test directory loads in back-test mode
  (bound to the registry slice, and through `founder_inputs` / `person_inputs`); `tests/fixtures/backtest/99-broken.yaml`
  refused with the golden sentence; the three differences; golden refuses the two keys; `entry_for`; the refusal
  sentence; fake-for; the ungated export; the markdown; FR-5's walls.
- [x] T004 FR-2 `make backtest ENTRY=<id>` (Makefile, refusal sentences, `evals/run_backtest.py`), the founder
  registered on the local stub at run time and signed up through `/signup` (`evals/backtest.Backtest.sign_in`).
- [x] T005 FR-3 `corpus_scenario.run(..., backtest=)`: strict=False, Keel's door, the camera hooks
  (`Corridor.camera`, `Interview.camera`, `Interviews.camera`, `create_project(camera=)`), the ungated export
  (`export_sample(..., gated=False)`) into `runs/<run>/export/`.
- [x] T006 FR-4 `backtest.md` / `backtest.json` (`evals/backtest.transcript`, `markdown`), written in `run()`'s
  `finally` whatever the walk reached.
- [x] T007 FR-5 Makefile header and AGENTS.md (S-012's paragraph: the back-test as the fourth paid command, with the
  measured cost); no mark, step or version moved.
- [x] T008 Acceptance 1 and 2 (below); `backtest/README.md` (five lines, untracked in keel-cloud-docs).

## Judgement calls

1. **The target brings its own stack up and down** (FR-2's builder's call). `evals/run_backtest.py` overrides the
   `stack` fixture: it refuses a stack already answering (its keel-cloud was booted without this shell's key, and the
   key reaches keel-cloud only through `stack/cloud.py`'s `dict(os.environ)` at boot), boots one, tears it down. So
   the key lives in exactly one process tree for the run's length.
2. **The founder is registered at run time, not added to the stub's built-ins.** The local stub's `POST /identities` is
   ungated, so `Backtest.identity` registers `backtest` (sub `cell-backtest`, *Backtest Founder*,
   `backtest@keel-backtest.test`); a 409 on the same stub reuses it. The picker every other scenario sees is unchanged.
   Before signing up, the run holds keel-cloud's log to *Keel's AI is ON* and the email outside the effective
   `KEEL_VENDORS_FAKE_FOR` (`in_fake_for` mirrors keel-cloud's `FakeFor`).
3. **The runner is `evals/run_backtest.py`, not a `test_*.py`**, so no directory run (`make eval`, `make eval-live`,
   `make unit`) collects it and `tests/test_scenario_set.py`'s fourteen are untouched; it is `live`-marked anyway.
4. **The back-test widens S-012's named LLM place rather than adding a fifth** (AGENTS.md's count stays four): the
   same founder journey, on the same Keel's-AI door, locally.
5. **Golden entries now refuse `idea_name` / `sources` by name.** Before, the loader ignored unknown keys, so "accepts
   the two keys" meant nothing unless golden mode refused them; no golden file carries either.
6. **The sample export moves `runs/<run>/export/` to FR-3's snapshot; the contract export goes to
   `runs/<run>/contract-export/` on this run alone** (both wrote `manifest.json`). Golden runs are unchanged.
7. **Keel's door in the corridor legs.** `Journey.keels_door` (False everywhere else): L1 is held to its three
   counters and title only (the carousel and *Lock and record the interviewer* recorded; the lock records Livia, fake
   renders, 400 credits), and the greyed-formats assertion of leg_invite is skipped (Text is still pressed and held).
8. **The guide's welcome is waited for 30 s and skipped** (`Backtest.pass_welcome`), not judged: on a fresh vite the
   sheet's lazy chunk landed after `MarketStep.start`'s 5 s pass in dry run 1 and covered the context step's Save.
9. **The guide and feedback marks are not scored on the back-test** (they are S-005/6/7's regressions, and FM1 would
   fail a run on the model's words); `leg_welcome`, the script and the runtime are not run; every other leg is.
10. **Legs are timed by laps** (`run()` calls each leg exactly as before -- the source-shape tests read those lines --
    and a no-op `_no_lap` elsewhere); `leg_report` and `leg_one_currency` share one lap, the "teaching" lap is the
    30 s welcome wait.
11. **A refused model result is a finding, retried as the founder's screen would** (after the first two paid runs, see
    Measured): `Journey.retries` (0 everywhere else; `RETRIES` 3 here) lets `_wait_calibration` and the lock's
    questionnaire wait `POST .../retry` and reload; `Corridor.seed(resend=)` sends the seed again when the chat reopens
    its composer; a failed reading batch or THEMES job is recorded, not asserted. All land in `findings`.
12. **Screens go to `runs/<run>/screens/`**, apart from the harness's numbered `screenshots/`; the send screen is shot
    once (its first opening), not twenty times; the respondent camera watches the first gate-yes person with a typed
    story on the primary link and the first decision-maker. keel-web's corridor scrolls inside its card, so a
    "full-page" shot is the viewport there; the transcript carries the screen's whole text read beside it.
13. **Acceptance 2 ran the authored `08-fresco`** (all six authored entries 08-13 loaded cleanly in back-test mode, so no
    smoke copy was made); B2B, so both links and the decision-maker's screens are exercised. The README was still
    written (five lines) since the directory had none.
14. **Two zero-spend dry runs with an invalid key** (`EXECUTOR_AUTH_FAILED`, $0) proved the boot, the door, the camera,
    the transcript-on-failure and the teardown before any paid run.
15. **`stack.toml`'s four `[paths]` lines read `../../…` under `git update-index --skip-worktree` for the build**, as 061
    did, and were put back byte for byte (sha256 `f6986f68…`), flag cleared.

## Entries refused

None: `08-fresco`, `09-karsa`, `10-palus`, `11-issen`, `12-transload`, `13-aircaps` all load in back-test mode (bound
to the registry slice) and through the harness readers.

## DRIFT (product findings, not fixed here)

- **keel-web, Keel's door: the seed chat's failure line says *Your AI's answer came back in a shape this step can't
  use, so nothing was saved. Start the step again.*** to a founder on Keel's AI (paid run 2), where AGENTS.md's spec 024
  rule is *Keel*, never *your AI*.
- **Keel's AI refused itself twice in three paid runs on `08-fresco`**: run 1, PROBLEM's CALIBRATION_QUESTIONS
  `RESULT_INVALID` (`result.questions[2].list.items[0].label: L2: an item is 1 to 9 words; 'Logging site walk photos and
  notes into an accurate record' is 10`); run 2, PROBLEM_INTERPRET answered but the step could not apply it. Run 3
  needed no retry. Both are the back-test doing its job; neither is a harness fault.

## Measured (2026-10-22)

**`make unit`** (`PY=` the main checkout's venv): **2,964 passed / 53 skipped** before, **2,986 / 53** after (+22,
`tests/test_backtest.py`).

**Paid runs** (key read into the one command's environment from `/keel/staging/anthropic-api-key`; never printed or
written; `grep -r sk-ant runs/` empty):
1. `runs/20261022T143840Z-backtest-08-fresco` -- stopped at PROBLEM's calibration (RESULT_INVALID above), 3 jobs,
   **$0.1236**. Fixed: retries (call 11).
2. `runs/20261022T145304Z-backtest-08-fresco` -- stopped at the problem seed (the step refused the answer), 2 jobs,
   **$0.0631**. Fixed: resend (call 11).
3. **`runs/20261022T151435Z-backtest-08-fresco` -- 1 passed in 394 s** (wall 380 s; interviews 179 s), 30 jobs,
   **$0.5021** (CALIBRATION_QUESTIONS 11 $0.3023, INTERPRET 13 $0.1112, SOLUTION_MECHANISM $0.032, CONTEXT_INTERPRET
   $0.0234, PROBLEM_INTERPRET $0.0204, RESPONDENT_QUESTIONS $0.0128, THEMES 2 still open at the transcript); models
   `claude-sonnet-5-5` and `claude-haiku-4-5-20251001`, host `api`; credits 2,500 -> 801. Screenshots: **40 founder,
   10 + 10 respondent** (primary, decision-maker). Decision **NOT_YET** (MEDIUM, smallest group 7); PROBLEM and SOLUTION
   *People disagree*, COMMERCIAL *Not holding up*; pilot 6 of 20 (30%); price $250 a month (6 of 8). Readings: the
   model's anchoring equals the file's on all 18 people the file anchors. Export: 36 files, 195,607 bytes, names kept
   20 of 20. Total spent across the three: **$0.69**.
