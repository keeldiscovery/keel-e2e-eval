# Tasks 103 -- The harness reads the window as its own sentence

Branch `103-the-window-sentence-in-the-mirror` (worktree `wt/keel-e2e-eval-103`), off master `a2c76e0` (the spec commit).
Built by Claude on 2026-10-30. Read only: keel-cloud-docs' `specs/168-the-window-is-its-own-sentence/tasks.md` and
`ReadBack.java` at `9ba42382`. **No browser, no stack, no paid call.** Nothing merged into master; the branch pushed after
every commit, never force-pushed.

| Commit | What |
|---|---|
| `2381123` | FR-1 (the mirror) and FR-2 (the pins, each with why), and the `ReadBack.java` source pin |
| `5dfe693` | FR-3 (the money-alone check) and its new test; the two other vacuous *counting* checks |
| `1f38236` | master's other failing test, not this spec's: keel-cloud 166's reworded `Interview.condition` description |
| the docs commit | this file, `AGENTS.md`'s spec-103 paragraph and its `:505` prose |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| 102's tasks.md record (master `374694d`+102) | 4,076 | 0 | 53 |
| **master `a2c76e0`** against the sibling keel-cloud-docs at `9ba42382`+ (`test_the_sentence_mirror_reads_the_clouds_read_back`, T007; `test_the_screener_screen_is_first_...`, below) | **4,074** | **2** | **53** |
| branch at `5dfe693` (FR-1..FR-3) | 4,076 | 1 | 53 |
| **branch at `1f38236` (the last code; the docs commit adds none)** | **4,077** | **0** | **53** |

Master's row was run on a detached worktree at `a2c76e0` against the sibling at `bf073aad`. The +1 is `test_drifts_95_97_closed.py::test_a_live_models_money_alone_sentence_is_held_to_no_window_sentence` (FR-3).
The sibling keel-cloud-docs main checkout (read through `../keel-cloud-docs`) moved during the build, from `9ba42382`
(168) to `372dd0cf` and `bf073aad` (spec 169, instruction text only); the counts above were read on it as it stood.

## FR-1 -- the mirror

- [x] T001 `harness/vectors_script.py:475` `sentence`: `out + "." + (f" We'll ask about the last
  {window_words(window)}." if window else "")` -- the job closes with its full stop, the window a third sentence; no
  window (none stored, or `read_back`'s scope rule, spec 135) the two sentences byte for byte. `window_words` stays
  *7 nights* (keel-web's `RECALL_WINDOW_WORDS`), so *the last* is the mirror's own, where 168 has it in
  `RecallWindow.words()` -- the same sentence served.
- [x] T002 The docstring (`:457-468`) and `read_back`'s comment (`:484`) say the new shape.

## FR-2 -- the pins, re-pinned with why (168)

- [x] T003 `tests/test_read_back_mirror_085.py`: `FRESCO_SENTENCE` (:30), Lullaby (:65, :74), 13-aircaps (:86), Palus
  (:209), each test's docstring (or the constant's comment) naming 168.
- [x] T004 `tests/test_drawn_screener_seams_077.py`: 07-mulchrun (:67-68), the payroll and translator sentences (:104,
  :107).
- [x] T005 `tests/test_vectors_journey.py`: 07-mulchrun (:630-631), 01-countly (:634).
- [x] T006 `tests/test_drifts_95_97_closed.py:171` and `tests/test_study_scopes.py:168`: `.endswith(". We'll ask about
  the last 4 weeks.")`.
- [x] T007 **Not in the spec's list:** `test_read_back_mirror_085.py::test_the_sentence_mirror_reads_the_clouds_read_back`
  holds the mirror's joins to `ReadBack.java` through the sibling path, and pinned 149's line ending `.append(they(what));`.
  168 made it `.append(they(what)).append('.');`, so the test **failed on master** once the sibling was at `9ba42382`.
  Re-pinned to the new line, plus the window line `out.append(" We'll ask about ").append(window.words()).append('.');`
  and no *, counting* in `sentence`'s body -- the mirror's FR-1 is now held to the cloud's source.

## FR-3 -- the money-alone check

- [x] T008 `evals/corpus_scenario.py:340` (`_drift_96_guard`, the non-strict branch, a host's live model):
  `"we'll ask about" not in drawn.lower()`, with a one-line why. The leg's step title (`:385-387`) says the new shape.
- [x] T009 New `test_a_live_models_money_alone_sentence_is_held_to_no_window_sentence`: on a non-strict journey a
  windowless sentence passes and the windowed read-back fails (the old check let it pass).
- [x] T010 **Not in the spec's list, the same vacuity:** `test_drifts_95_97_closed.py:130` (the money-alone test's
  `"counting" not in understands`) and `test_study_scopes.py:243` (`"counting" not in read_back(seed, window=False)`)
  now ask for no *we'll ask about*.

## FR-4 -- not here

- [x] T011 Untouched: `evals/corpus_scenario.py:679` (*Counting the last {window}.*, the web's muted line) and
  `tests/test_drifts_95_97_closed.py:150` (the card's window line case) -- keel-web 147's. History untouched: old specs,
  `runs/DRIFT.md`, `quality/` (scores, cycles, `decisions.toml`'s D-2026-10-30-03 quotes the old tail as the decision's
  why), the gallery fixtures.

## FR-5 -- fresh projects

- [x] T012 A project confirmed before 168 keeps the old sentence in its stored `understands` (keel-cloud stores it at the
  confirm, `ContextSlots.understands`; never recomposed on read). The quality walk and every journey make fresh
  projects, so nothing is owed; a hand check on an older staging project would see *, counting ...* until its context is
  re-confirmed.

## Beyond the spec: master's other failing test -- `1f38236`

`tests/test_founder_walk_076.py::test_the_screener_screen_is_first_and_the_idea_after_it` pinned *"Spec 145 (FR-4,
contract 43): COMMERCIAL_LINK only -- the screener, asked before `idea`"* in `canon/openapi-v2.yaml`; keel-cloud 166 FR-4
(`c2437f90`, contract 49, no bump) reworded it *"... on COMMERCIAL_LINK -- the screener ..."* and added the no-gate FULL
link. Re-pinned to the new words; what the test holds did not move. Whatever eval spec mirrors 166 (the condition on a
money-alone FULL link, 102 FR-4's hand-off) may want to pin the new sentence too.
