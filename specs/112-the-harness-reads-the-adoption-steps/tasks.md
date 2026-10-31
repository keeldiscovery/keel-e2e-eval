# Tasks 112 -- The harness reads keel-cloud 171: the adoption frame, the marked suggestion, the founder's efforts in the screen

Branch `112-the-harness-reads-the-adoption-steps` (worktree `wt/keel-e2e-eval-112`, its own `make venv`), off master
`0ee35ef` (097's docs). Built by Claude on 2026-10-30. Read only: keel-cloud-docs at `f4ca175f` (171 merged:
`ItemFrames`, `SpokenCap`, `StrangerGrammar`, `SavedList`, `ScreenResultApplier`, `RespondentItems`, `AskedRules`,
`ScreenContextBuilder`, 171's tests and tasks.md), later at `84b80d86` (172 merged) for the final gate; keel-web at
`1d83a28`, later `a83d846` (144). **No stack, no model, no paid call, no screen run.** Nothing merged into master;
the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `c42c98c` | FR-1: the frame -- `spoken.step` / `to_use` / `says_it` / `adoption_friction` / `adoption_frame`, `asked_frame`, `adoption_statement`, call 126 |
| `b1eeb31` | FR-2: `SUGGESTED_ON`, `L5`, `L1`; `keel_added` off the flag, `_choose_label`; call 124 |
| `7684946` | FR-3: the back-test redrafts with the typed Answer, the 171 mark |
| `21599bb` | FR-5: `tests/test_adoption_steps_112.py` (54) |
| `2db52a8` | `MARKS_VERSION` 23 -> 24, calls 129-130 (not in the spec; see below -- droppable on its own) |
| the docs commit | this file and `AGENTS.md`'s spec-112 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| master `0ee35ef` against keel-cloud-docs `f4ca175f`, keel-web `1d83a28` (this worktree, before any change) | 4,327 | 0 | 56 |
| **branch at `2db52a8` (the last code; the docs commit adds none), keel-cloud-docs `84b80d86`, keel-web `a83d846`** | **4,383** | **0** | **56** |

+56 passed: `tests/test_adoption_steps_112.py`'s 54 and two more parameters of 093's frame test (171's 10- and
11-word pins). None removed. Master had **no** failure against 171: every eval pin of 171's list is a mirror of the
old frame, not a read of keel-cloud, so nothing went red until the mirror moved -- the re-pins below are this spec's
own. No failure came from keel-cloud 172 or keel-web 144 (merged while this was built).

## The checklist (keel-cloud 171's *eval pins to move*)

- [x] T001 **The frame mirror** (FR-1, `instructions/spoken.py`): `SpokenCap.step` ported (`step`: a leading *would
  you* / *you'd* / *you would* / *you had to* / *have to* / *need to* dropped, a past or a participle in base form via
  `StrangerGrammar.baseOfPast` / `baseOfPastLoose` and 171's `BE_DO_HAVE` / `PARTICIPLES`, 132's leading clause moved
  to the end in the present, a clause's own *to ..., you'd* purpose dropped, later pasts after *you* / *and* in the
  present); `ItemFrames.toUse`, `questionPart`, `saysIt` (the *it* / *its* swap, only a capitalised name, never where
  the founder's row carries it) and `fitted`'s give-way (whole, then without a comma phrase, then a question's step;
  named, then *it*). `ADOPTION_ASK` stays the question; `_WOULD_DO` (123's *you would have to*) is gone.
  `adoption_frame` is `ItemFrames.adoptionFrame` (what `K2` measures: the whole step, no give-way); `framed` follows.
  `ADOPTION_CLAUSE_MAX_WORDS` = 10 recorded, never a fault (the registry's option rule, as 163's 12 was).
- [x] T002 **The served statement mirror** (FR-1, `harness/vectors_script.py`): `adoption_statement(asked, name,
  label=None)` is the lock's composition then its hold -- `spoken.adoption_friction(asked, name, label or "")`, then
  past 20 words the founder's row in the same frame (named, *it* where the name takes it past 20), then the plain
  *Would it fit the way you do things, or not?* (`ADOPTION_PLAIN`). No name is now *To use it* (was None). `gerund`
  stays for the follow-up rungs (171 FR-7), its docstring says it is no longer the frame's.
  `evals/backtest.cloud_130` hands it the tested row's label; `_tested_item` reads `SavedList.firstTyped()`.
- [x] T003 **The asked job's frame** (FR-1): `context.asked_frame` -> *To use it, you'd {asked}. Would you do that, or
  not?*; `tests/test_instruction_context.py:237` re-pinned.
- [x] T004 **`L5` and `L1`** (FR-2, `instructions/score.py`): `SUGGESTED_ON` gains `solution.adoption_friction`; the
  `L5` message is 171's; a suggested Adoption friction item with no `suggested_why` is an `L5` fault; `L1` counts the
  items less the one suggested (*... besides the one suggested step*).
- [x] T005 **104's *Keel added*** (FR-2, `evals/corpus_scenario.py`): `keel_added` on Adoption friction reads the
  served `suggested: true` rows (`keel_suggested`, the wire's `suggestedWhy`); the finding is *Adoption friction: Keel
  suggested: '...' -- why*. `_choose_label` never lands on a suggested row unless the entry's typed pick is that row
  word for word (a label on both is the founder's row); spec 108's near rows and `keel_left_out` read the founder's
  rows alone (`_founders_rows`).
- [x] T006 **The founder-lists screen reads the entry's Answer** (FR-3, `instructions/screen_entries.py`,
  `instructions/run.py`): `BACKTEST_SCREENS` gains `CALIBRATION_QUESTIONS`; `backtest_calibration_cases` builds, for a
  named back-test entry, one redraft a typed list dimension -- `redraft_context`: the seed-time job with `dimensions`
  cut to the one and `answers` `{key: the walk's typed words}` (`vectors_script.calibration_answers`' `text`), as
  `ScreenContextBuilder` builds a redraft. Adoption friction's carries the 171 row (`meta["steps"]`: the typed efforts,
  `brand_names` -- the title's name, the short name, the offer's name). `steps_mark` holds the first turn: COMPLETED,
  the founder's efforts first and as typed, no other unmarked row, at most one `suggested` row, last, with a why, no
  brand in any `asked`; each clause's words recorded for a reader. `run._score_probe` marks it (`state.probes`, the
  diff's `probe`, the console's *171 held*).
- [x] T007 **Tests re-pinned with why** (FR-4): `test_after_130.py` (the named statement, the long one now the plain
  frame / the founder's row, the cloud_130 mirror), `test_after_131.py` (`test_the_adoption_frame_whole`: base form;
  Fresco, Lemma and Pairio give way to the founder's row, as keel-cloud's own re-pins), `test_phrase_is_the_peoples_093.py`
  (L5 admits Adoption friction, a missing why faults; the frame pins and 163's slip -- now 23 words, a `K2`),
  `test_instruction_spoken.py:380`, `test_instruction_context.py:237`. Beyond the spec's list:
  `test_instruction_score.py` (Lullaby's 12-word corpus face is now a `K2`), `test_lock_frontier_110.py` (the 170
  record: five golden faces now `K2`s, 104 of 109; `BACKTEST_SCREENS` ends respondent, calibration),
  `test_frontier_tier_105.py` (a back-test needle builds the redrafts after the four), `test_choose_by_label_104.py`
  (the generic *Keel added* test held on Compatibility; 21-codyco's pre-171 rows carry no flag -- named *drafted
  unmarked*), and the `MARKS_VERSION` pins (below).
- [x] T008 **Tests** (FR-5, `tests/test_adoption_steps_112.py`, 54): the frame named and unnamed, fifteen stored
  shapes in base form, at and over the cap with each fallback, past them all the founder's row and the plain frame;
  the *it* swap; `K2` at 10 and 11; the served stem against the row; the gallery line (below); `L1` / `L5` on one, two
  and a why-less suggestion; `keel_added` on a suggested row, a reworded row never Keel's, an unmarked one named apart;
  `_choose_label` skipping a suggested row; the default belief; the screen on 21-codyco, 17-expanse and 08-fresco with
  their Answers and the validator's batch; the 171 mark held and each fault; the run marking a redraft.
- [ ] `make instruction-screen HOST=claude K=21-codyco/CALIBRATION_SOLUTION/ADOPTION_FRICTION N=3 WHY=instruction:171`
  (and 17-expanse, 08-fresco): **not run** -- paid, the founder's word; the coordinator's.

## Where the spec and the code differ (the code's patterns followed)

- **`MARKS_VERSION`**: the spec names call 126's wording only. FR-1 and FR-2 move `option_validity` both ways (an
  11-word face is now a `K2`; a marked step with its why is now valid, one without an `L5`), and the repo's rule
  (`marks.toml`'s header, 093 and 091) is that a moved reading moves the version -- else a v23 scorecard re-scored at
  v23 changes silently. So **23 -> 24**, calls 129-130 (`OLDEST` stays 20), calls 124 and 126 amended to point at 129,
  every `== 23` pin moved. Its own commit (`2db52a8`): drop it and the rest stands at v23.
- **`_draft_count` (~:326)**: it sees no items, so `L1`'s exclusion of the suggested step is in `list_faults`, where
  the items are counted.
- **The gallery fixture (`expected-interview-fresco.json:139`)** is not changed: it pins what the 2026-10-22 run of
  record *served* (`evals/gallery.py` exports a run's questions verbatim), and a project locked before 171 keeps its
  stored question (171 T014). Rewriting the pin would fail the export test; rewriting the run would fabricate a
  recording. The test instead holds the recorded line and the mirror's new frame for the same row (*To use Fresco,
  you'd take short videos and talk over them on walks.*). The gallery exports no draft lists, so 171's *a gallery
  draft with `suggested: true`* has no place to go.
- **One case a dimension**: keel-cloud redrafts one list at a time, so a back-test entry's redraft is
  `<id>/CALIBRATION_<VECTOR>/<DIMENSION>/run<N>`, every list it typed. `K=21-codyco/CALIBRATION_SOLUTION` therefore
  runs Compatibility, Relative advantage and Adoption friction (9 calls at N=3); `.../ADOPTION_FRICTION` the one (3).
- **`keel_added` "instead of diffing labels"**: on Adoption friction it reads the flag alone. A drafted row neither
  typed, near a typed one, nor marked (what 171 FR-1 says the writer never drafts) is still named, apart (*Keel added,
  unmarked*), so the regression 104 caught is not lost.
- **`L5`'s why**: a missing `suggested_why` faults on Adoption friction (171's breach) but not on Compatibility, where
  call 124 left it a note; the cloud breaches both.
- **The grammar check** (`StrangerGrammar.fault`) beside the cap is not mirrored, as before 171: where it moves a
  served stem the mirror differs and `cloud_130` writes a finding, never a stop.
- **`_THIRD_TO_SECOND`** turned *them* (093's mirror); `StrangerGrammar.THIRD` never does (*talk over them*). Corrected.
- **`K3` on Adoption friction** reads the step after the frame's *you'd* (the frame always says *you'd* now, so the
  whole line would never fault); the third-person-subject rule stands.

## What the spec did not foresee

1. **The golden corpus is past the new frame's room**: five of its seven Adoption friction faces (01-countly,
   02-compliancelog, 03-lullaby, 04-linerly, 06-repeatline -- 11 or 12 words, written to 163's 12) are now `K2`s.
   `spoken_form` at zero spend reads **104 of 109** (was 109), and Lullaby's own lists no longer score clean as a draft
   (one `K2`). 171 did not move the corpus (its *not foreseen* 1 says so for stored rows); a corpus revision with
   10-word faces is keel-cloud's to make. Not softened here.
2. **`answers` was `{}` on every screen** -- so 171's FR-6 screens could not have measured *the founder's efforts first*
   before this; now they can, on back-test entries only (the golden corpus records no Answer text, so its seed-time
   job is unchanged).
3. **The brand list** is the entry's title before the dash plus its short and offer names; 21-codyco's short name
   (*missed calls booked by AI*) is a description, so an `asked` clause repeating it word for word faults too.
4. keel-cloud-docs (172) and keel-web (144) merged during the build; the gate was re-run against them, green.
