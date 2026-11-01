# Tasks 126 -- The founder types like a person (typos on the quality walk, and the leak check)

Branch `126-the-founder-types-like-a-person` (worktree `wt/keel-e2e-eval-126`), on the spec's commit `2a0b3a2`. Built by
a builder (Claude, on the coordinator's brief) on 2026-11-01. Read only: keel-cloud-docs master `2d848360` (the
back-test entries, through `harness/vectors_script`) and keel-web `2b84758` (its sha in the DRY plan). **No stack, no
model, no paid call, no key read.** Nothing merged; the branch pushed after each commit.

## FR-1 -- the typist

- [x] T001 New `harness/typist.py`: `typos(text, seed, *, keep, avoid) -> (typed, [Typo(meant, typed, kind)])`.
  Deterministic from `seed` (`"<entry id>:<field>"`): every choice is a sha256 of the seed, the word's place and the
  word (no `random`, so no Python version moves it). `owed(text)`: one typo about every twelve words
  (`int(n / 12 + 0.5)`), at least one from four words, none under four.
- [x] T002 The kinds (`edits(word)`, the first letter never touched): `transposed` (two adjacent inner letters, *every*
  -> *evrey*), `dropped` (an inner letter, *without* -> *withot*, *errors* -> *erros*), `doubled` (a consonant,
  *running* -> *runnning*), `ie/ei` (the only typo of a word that has the pair, *receive* -> *recieve*). One edit a
  word; every typo is optimal-string-alignment 1 from its word and `spelling.same_word` it (spec 125's port of keel-cloud
  195's `Spelling`), so the product's own rule reads it as the word meant.
- [x] T003 The rules (`typeable`): only `[a-z]{5,}` -- never a capitalised word, a word with a digit (*€5,000*,
  *53-room*), a word with an apostrophe or hyphen (*hotel's*, *seven-figure*), a currency or a unit (`UNITS`), a word
  under five letters, or a word of `kept_words(entry)`. **The corpus records no `product_words` or brand list**
  (`instructions/corpus.py` has none; *product words* in `no_leak` are the mechanism's own vocabulary), so the kept words
  are the idea name the founder types (`founder_idea_name`), the offer name (`interpretations.offer_name`) and the short
  name (`solution_mechanism.short_name`). Beside them `avoided_words(entry)`: a typed form is never a word of the entry's
  own yaml, nor of the text itself (it would read as that word, and a leak of it would be no leak). Punctuation and
  spacing kept.

## FR-2 -- where the founder types

- [x] T004 `typist.type_founder(entry, founder)`: `FounderInputs`' `actor`, `job`, `circumstance`, `segment`,
  `problem_seed`, `solution_seed` typed; the project name, idea name, decider, calibration answers, window and hourly rate
  as recorded. Every typo `{field, meant, typed, kind}`.
- [x] T005 Wired into the quality walk only. `quality/cycle.py walk --typos on|off` (default on; `make quality-walk
  TYPOS=0` passes `--typos off`); `plan_steps(..., typos=True)` adds `TYPOS=1` to each `make backtest`; the Makefile
  passes it on as `KEEL_BACKTEST_TYPOS` (`backtest.typos()`: `1`/`on`, `0`/`off`/unsaid, anything else refused by name
  through `door_refusal`); `run_backtest.py` hands it to `Backtest(typos=...)`; `corpus_scenario.run` types the founder
  only when `backtest.typos is True`. `backtest.json` and `inputs.json` carry `typos` only when one was typed.
- [x] T006 `DRY=1` prints every field as it will be typed, each typo marked `typed[meant]` (`typist.dry_lines`,
  `cycle.typed_fields`); an entry it cannot read is said, never refused.
- [x] T007 `make gallery` reads `inputs.json`'s founder through `typist.as_meant` (see *Not foreseen* 2): unchanged where
  no `typos` is recorded.

## FR-3 -- the leak check

- [x] T008 `typist.served_texts(bundle)`: every served text `backtest.json` already captures, in the walk's order -- the
  founder's screens less what he typed on them (`answer`), each link's served interview (condition, idea, gate, items
  with their spoken forms, reveal) and drawn screens, the screens after the answers, the report (`brief`). No new
  navigation.
- [x] T009 `typist.walked(bundle, typed)`: the typos on the fields the walk reached (the founder's `context`,
  `problem-seed`, `solution-seed` screens recorded) -- a PROBLEM study never types the solution seed.
- [x] T010 `typist.leaks(bundle, typed)`: each typed form searched as a whole word, case-insensitively; a hit is
  `{screen, field, meant, typed, text}` (the sentence around it), one a screen and sentence; the word spelt right is
  not reported. `leak_line`: *typo leak: "withot" (meant "without") reached the PROBLEM question "..."*.
- [x] T011 `cycle.walk_one`: after the readers, the score file gains `typos` and `typo_leaks` -- only when the walk typed
  one, so a score file of a walk with none is the readers' byte for byte. Never a stop, never a retype.
- [x] T012 The record: `_head_of` adds `typos`, `typo_fields`, `typo_leaks` only when a file carries typos; the head
  says `  - typos: N typed on M fields; K leaked (spec 126)`; `## Typo leaks (spec 126)` lists each study (*N typos
  typed on M fields; none leaked*) and a defect line a leak under it. A record of walks with none renders as before.
- [x] T013 FR-4: the founder-reader still has the entry's `.sources.md`; no reader prompt, `RUBRIC_VERSION` or
  `MARKS_VERSION` moved. `quality/CYCLE.md` and the Makefile say the typist; the AGENTS.md paragraph.

| Where | Was | Now |
|---|---|---|
| `make quality-walk` | each back-test `... DOOR= PEOPLE=7` | `... DOOR= PEOPLE=7 TYPOS=1` (`TYPOS=0`: as before) |
| the founder's problem seed on the walk | the entry's sentence as recorded | typed with ~1 typo a 12 words |
| `make backtest`, the journeys, `make gallery` | -- | unchanged (no `TYPOS`, no `typos` key) |
| a score file | the readers' | `+ typos`, `+ typo_leaks` when typos were typed |
| the cycle head | score_pct, walks, second asks | `+ typos: N typed on M fields; K leaked` when typed |

## Tests

- New `tests/test_typist_126.py` (35): determinism; the six kinds' examples (*recieve*, *beleive*, *withot*, *erros*,
  *runnning*, *evrey*) and that every edit keeps the first letter, is one edit and `same_word`; the rate; the rules
  (names, numbers, *hotel's*, units, kept words; the typed text untyped back is the text); `avoid`; every back-test entry
  at `2d848360` typed by the rules (skipped without the sibling); only the six fields typed; the marked DRY line; the env
  var and its refusal; the walk's argv with and without; the DRY output on and off; the 21-codyco DRY lines; **the leak
  check on the recorded 21-codyco PROBLEM walk** (`tests/fixtures/typist/backtest-21-codyco-PROBLEM.json`, cycle 6's
  `20261101T111212Z` bundle trimmed to its served parts): clean, the founder's own answer never a leak, a typed form in a
  served question a leak in the founder's words, whole words only, a PROBLEM study's solution seed; `as_meant`; the score
  file written only with typos; the record's head and section only with typos; `_head_of`'s counts.
- Re-pinned: `tests/test_backtest_host.py::test_the_runner_reads_the_door_and_the_keel_door_still_refuses_on_a_missing_key`
  (the KEEL door's `Backtest(...)` now carries `typos=backtest.typos()`).

## Gate

`set -o pipefail; make unit 2>&1 | tail -1` on the committed tree (`d9015ba`, the build commit) against keel-cloud-docs
`2d848360` and keel-web `2b84758`, 18:45:49-18:49:56 ET (exit 0):

`4952 passed, 54 skipped in 246.84s (0:04:06)` -- **0 failed, 0 errors** (master `2a0b3a2`: 4,917 passed / 54 skipped;
+35, all in `tests/test_typist_126.py`).

The run before it (18:40:42-18:44:52 ET) failed one test, the re-pin above: `1 failed, 4951 passed, 54 skipped`.

## The DRY run (21-codyco, PROBLEM)

`make quality-walk DRY=1 ENTRIES=21-codyco SCOPES=PROBLEM WHY="dry"` from the worktree (calls nothing):

```
quality-walk DRY RUN -- nothing runs, nothing is written. WHY: dry
keel-cloud ../keel-cloud-docs at 2d84836 (master); keel-web ../keel-web at 2b84758; DOOR=keel
studies: 1 (21-codyco x PROBLEM); reader claude-opus-5-5 (medium); the bar 90%; 7 people a study on the person's own link, the decision-makers whole (spec 106)
  a paid walk would refuse: KEEL_ANTHROPIC_API_KEY is not set in this shell -- DOOR=keel answers every job on Keel's AI (spec 062 FR-2); or walk DOOR=host on the founder's own Claude Code
    1. down
    2. backtest ENTRY=21-codyco SCOPE=PROBLEM DOOR=keel PEOPLE=7 TYPOS=1   > runs/quality-walk/20261101T234633Z-20261101-2d84836/21-codyco-PROBLEM.backtest.log
    3. read-screens RUN=<bundle> OUT=runs/quality-walk/20261101T234633Z-20261101-2d84836/read-21-codyco-PROBLEM   > runs/quality-walk/20261101T234633Z-20261101-2d84836/21-codyco-PROBLEM.read.log
    4. read-table BASELINE=1 CYCLE=quality/cycles/20261101-2d84836.md
typos: on (spec 126; TYPOS=0 turns them off) -- the founder's fields and seeds as he will type them, each typo marked typed[meant]:
  21-codyco:
    actor (0 typos): reservation agent
    job (1 typo): turn everry[every] guest who calls into a booking
    circumstance (2 typos): bokoing[booking] calls come in on every shift, after hours, at peak and on holidays, and not every one gets answeed[answered]
    segment (1 typo): reservation agenst[agents] at hotel groups in Germany that run a central reservations office or call center
    problem_seed (7 typos): Hotel grous[groups] miss aboutt[about] 5% of their reservation calls even with a central reservations office or a call center: after hours, during peak hours, on holidays. Every call that rigns[rings] out is a booking that goes to an online travel agenccy[agency] or a competitor, a seven-figure roundingg[rounding] error for a mid-sized grroup[group]; we started Codyco after a friend told us how much mnoey[money] he was losing from missed calls, and one 53-room hotel made €5,000 in extra bookings in its first 4 weeks with us.
    solution_seed (4 typos): An AI reservation agent: the hotel forwards the calls nobody picks up to Codyco, which answers in the hotel's voice, answers the guest's questions, takes the pyment[payment] and writes the confirmed bokoing[booking] staight[straight] into the PMS (OPERA Cloud, Sihot, Apaleo), handding[handing] a call to the desk by rules the hotel sets.
decisions: 25 in quality/decisions.toml (spec 087) -- a weak row one covers is listed under Decided before, not advised
then the record: quality/cycles/20261101-2d84836.md (and TABLE.md's head); commit both with the score files
```

(The PROBLEM walk types the four fields and the problem seed; the solution seed is printed but `walked` leaves its
typos out of the score file, since no solution-seed screen is reached.)

## Not foreseen

1. **`_head_of` iterated the keys of `latest`** (a dict keyed `<entry> · <scope>`), so spec 122's `asked_again` /
   `unread` were always 0 and the second-ask line never printed. Fixed in passing (`latest.values()`); the typo counts
   read the same way. No committed record changes (records render from their data blocks).
2. **The gallery reads the founder's typed words.** `quality-accept` builds the gallery from the cycle's bundles, and the
   gallery's problem sentence and keywords come from `inputs.json`'s founder -- with typos on, the homepage would show
   them. `gallery.read_run` now reads it through `typist.as_meant` (the typos put back), unchanged where none was typed.
3. **The back-test bundle records no AI interviewer clip or passage** (the walk takes the text link; no recorded bundle
   carries one). The leak check reads every served item's `spoken` block (the words the voice says) and whatever else
   the bundle captures; a clip's words are read the day a bundle records them.
4. **The context fields are stored as typed.** The walk still asserts keel-cloud stores the four fields as the founder
   typed them (`fields.get(key) == value`, against the typed founder). If keel-cloud ever corrects the stored fields, that
   step stops the walk -- a contract question for keel-cloud, not a leak.
5. **Words the founder repeats can carry the same typo** (*bokoing* in the circumstance and the solution seed): each
   field is seeded on its own, and the same word at the same place gives the same edit.

## Owed elsewhere

- keel-cloud: every typo leak cycle 7 records is its defect (an instruction or a code check that carried the founder's
  spelling into a served text), never a reason to retype.
- The corpus (keel-cloud-docs): optionally a `product_words` / brand list per entry, which `kept_words` would read beside
  the names.
- The coordinator: cycle 7 on the five catalog entries runs with typos on by default; the record names every typo and
  every leak.
