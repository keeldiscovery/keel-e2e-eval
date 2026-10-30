# Tasks 093 -- The harness mirrors keel-cloud 161: the bare phrase, the follow-up rung, the stale L1 and L5 restatements (with 163's frame and K3 on the framed line)

Built on the same branch as spec 090, after it: `090-and-093-the-screens-as-drawn` (worktree `wt/eval-090`), off master
`242f289`. Built by Claude Opus 5.5 on 2026-10-30 (commits carry the hand-off's `Claude Fable 5.1` trailer). Read only:
keel-cloud-docs master **`a396fe9f`** (161 merged at `b009fac8`, 163 at `a396fe9f`; contract 48; corpus revision 19) --
`ItemFrames.bare` / `said` / `oneAct` / `adoptionFriction`, `SpokenCap.leadingClause` / `present`,
`StrangerGrammar.wouldDo` / `secondPerson`, `AskedRules.fault` / `framed`, `ScreenResultApplier`'s `L1` and `L5`,
`FollowUpComposer`'s `{phrase}`, the registry of record; 161's and 163's tasks.md (their pins for this repository). Inputs
besides: the spec of record (FR-1 to FR-6, not edited); the two founder-lists screens' bundles
(`runs/20261029T193750Z-instructions`, `runs/20261030T111940Z-instructions`, copied into the worktree's ignored `runs/`
and re-scored there, never in the main checkout). **No paid call**: the re-scores ran `--no-judge`; the screen ran
`DRY=1`. Nothing merged or deployed; the branch pushed after every commit.

| Commit | What |
|---|---|
| `3734bb4` | FR-1: the scripted phrase bare |
| `9b295a2` | FR-2: the rung |
| `67d6e9b` | FR-3: L1 in 161's words, L5 admits Compatibility; `MARKS_VERSION` 21 -> 22 |
| `fd51cd4` | FR-4: the adoption-friction frame is `ItemFrames`' |
| `1083f7a` | FR-5: K3 judges the framed line |
| the docs commit | this file, 090's, `AGENTS.md`'s spec-090 and spec-093 paragraphs |

## Unit (the gate)

`make unit`, against the live checkouts (keel-cloud-docs `a396fe9f`, keel-web `02b952c`):

| | passed | failed | skipped |
|---|---|---|---|
| master `242f289` | 3,773 | 3 | 55 |
| branch at 093 FR-3 (`67d6e9b`) | 3,841 | 0 | 53 |
| **branch, final tree (the docs commit; 093 FR-5 `1083f7a` the last code)** | **3,855** | **0** | **53** |

`make instruction-screen K=03-lullaby/CALIBRATION DRY=1 WHY=instruction:founder-lists.md`, master (`git archive
242f289`, run beside the worktree and removed) and branch: the same **9 cases** (9 calibration, N=3; the one listed case
`03-lullaby/CALIBRATION_PROBLEM/run1 (CALIBRATION_QUESTIONS)`), the same `spoken 15 of 15`, `facts 14 of 14`, `overview 7
of 7`, the same denominators (calibration 11, validity 11, no_leak sweep A 3); nothing called, nothing spent. The only
difference is `marks_version` 21 -> 22 in the dry run's verdict (the printed JSON schema's key order differs between the
two runs: the exporter's, not this spec's).

## The re-score (the acceptance)

`python -m instructions.rescore runs/<id> --no-judge` on copies of the two bundles; faults by rule on the calibration
screens (the PROBLEM and SOLUTION runs of 03-lullaby):

| Bundle | Recorded (v21) | Re-scored at v21 on this branch before FR-3 | **Re-scored at v22 (final)** | option_validity v21 -> v22 |
|---|---|---|---|---|
| `20261030T111940Z` (the screen after keel-cloud 161 / 163) | L1 x3 (Importance), **L5 x3** (Compatibility), **K3 x2** (Adoption friction) | the same | **L1 x3 (Importance) only** | 25/33 (75.8 %) -> **30/33 (90.9 %)** |
| `20261029T193750Z` (the screen of 2026-10-29, before 161) | L1 x3 (Importance), **L5 x3** (Compatibility), K2 x2 + K3 x2 (Compatibility), **K2 x1** (Adoption friction) | the same | L1 x3 (Importance), **L1 x3 (Current solution: *your way of ...*)**, K2 x2 + K3 x2 (Compatibility); **no L5, no Adoption K2** | 26/33 -> 24/33 |

- **The L5 faults on 03-lullaby's SOLUTION runs are gone** on both bundles (FR-3; the spec's acceptance names the
  2026-10-29 bundle: *no L5 fault on `solution.compatibility`* -- met).
- **The K3 faults are gone** (*open the app before picking the baby up*, *open it near the cot when the crying starts*:
  FR-5) and the 2026-10-29 Adoption friction K2 (*would you ... while your baby cried*, 21 words by the harness's old
  frame, 20 by the cloud's) is gone (FR-4).
- **The Importance L1s remain** (*problem.importance takes ...*: spec 091's, the draft list's minimum -- not this spec's).
- The 2026-10-29 bundle gains three Current solution L1s: that run was written by `founder-lists.md` before 161, whose
  drafts still opened on *your way of* -- what 161's `L1` now refuses. The 2026-10-30 run (after 161) has none.
- The 2026-10-29 Compatibility K2 / K3 faults remain: 161 FR-3's subject (the instruction), not a restatement here.

## FR-1 -- the scripted phrase is bare -- `3734bb4`

- [x] T001 `harness/vectors_script.py`: `YOUR_WAY_OF`, `bare_phrase` (`ItemFrames.bare`), `one_act` (`ItemFrames.oneAct`,
  128 FR-16), `said_phrase` (`ItemFrames.said`). `drafted_list` writes `bare_phrase(corpus phrase)` (918-920: was the
  corpus's *your way of ...* as the draft's), so no scripted PROBLEM draft earns 161's `L1`; `saved_list`'s phrase is
  bare too (the founder saves the draft as drawn; the strict *stored as saved* check compares the wire to it);
  `evals/corpus_scenario._corpus_list` (what the Check screen draws) likewise. The corpus is not edited.
- [x] T002 `tests/test_phrase_is_the_peoples_093.py` FR-1 (the helper, *said*, every golden entry's draft and saved
  phrase bare, the corpus still *your way of*).

| File | Old | New | Why |
|---|---|---|---|
| `harness/vectors_script.py` `drafted_list` (918-920) | `draft["phrase"] = saved["phrase"]` | `bare_phrase(saved["phrase"])` | 161 FR-1, its pin |
| `harness/vectors_script.py` `saved_list` | the corpus phrase | `bare_phrase(...)` | the founder saves the bare draft |
| `evals/corpus_scenario.py` `_corpus_list` | the corpus phrase | `vs.bare_phrase(...)` | the Check screen draws the draft |
| `tests/fixtures/registry/slice.yaml` (163-167) | guidance *a second-person phrase for today's way*; option rule *A second-person phrase ('your way of checking for errors') ...* | 161's: *the act itself, a bare gerund phrase in the people's own words (never 'your way of')*; *The act today's way is, as a bare gerund phrase ... never opening on 'your way of', never a bare 'it' ...* | the registry mirror says 161 |
| `tests/test_instruction_spoken.py` (186-188, 216-217) | *How did your way of finding them go?* | *How did finding them go?* | 161's pin |
| `tests/test_controls_089.py` (322) | *How did your way of working out what the baby needed go?* in the registry | `How did {said_phrase(...)} go?` in it, and no *How did your way of* | 161 T005 |
| `tests/test_vectors_journey.py` `test_the_drafted_lists_keep_keel_clouds_rules` | `draft["phrase"].startswith("your ")` | the phrase is its own `bare_phrase`, never *your way of* | 161 L1 |

Not moved (161's pins call them stored data, valid and read bare): `tests/test_instruction_corpus_r11.py:68`,
`tests/test_instruction_context.py:165` -- the corpus records *your way of ...* and these read the record.
(`tests/v9_fixtures.py:154` is `GOOD_LISTS`, a *draft* that must meet every L rule: moved in FR-3, T009.)

## FR-2 -- the rung -- `9b295a2`

- [x] T003 `harness/interviewer_fake.py` `LADDER` (271-272): Current solution's text and spoken *You said {phrase} works
  for you. What keeps it working?* (was *You said your way of {job} works. ...*); `FILL_DEFAULTS["{phrase}"]` *the way you
  do it* (the composer's); `LADDER_SHA` `1cf2ebc3` -> `b009fac8` (161's merge).
- [x] T004 `harness/vectors_script.lock_values`: `{phrase}` on the Current solution rung, `said_phrase` of the locked
  phrase (`FollowUpComposer.lockValues`); `job_gerund`'s docstring (2283) says `{job}` is Relative advantage's now.
- [x] T005 Tests: `test_follow_up_ladder.py` (286: the default line *You said the way you do it works for you. ...*);
  `test_follow_ups_075.py` (122: Paidly's filled line *You said getting an approved invoice paid works for you. ...*,
  from the phrase, not the job gerund); `test_phrase_is_the_peoples_093.py` FR-2 (the rung, 161's Lullaby example).
- [x] T006 **The ladder's registry tests ran again.** `test_follow_up_ladder._registry_at_154` skipped every test that
  holds `LADDER` to the registry when the Current solution rung lacked `{job}` -- true of every 161 registry, so
  `test_the_ladder_is_the_registrys_own` and `test_each_texts_placeholders_are_the_registrys_and_fill_knows_them`
  were silently skipped on master against the live checkout. The detector reads `{job}` or `{phrase}`, and
  `SPOKEN_PLACEHOLDERS` carries `{phrase}`: both run and pass (`LADDER` equals 161's registry).

## FR-3 -- L1 and L5 say the cloud's -- `67d6e9b`

- [x] T007 `instructions/score.py` `list_faults`: `L1` (305-307) in 161's words -- a blank phrase *L1: Current solution
  carries the phrase today's way is asked by, the act in the people's words ('checking for errors')* (was *... the
  second-person phrase ... ('your way of ...')*), and a drafted phrase opening on *your way of* *L1: '<phrase>' opens on
  'your way of'; write the act alone, in the people's words ('<bare>')*; `L5` (330-332) admits one `suggested` on
  `SUGGESTED_ON` = Purchase friction and Compatibility, never elsewhere (*... on Purchase friction (a step it adds) and
  Compatibility (the condition most likely to be missing) only*, the cloud's words).
- [x] T008 **`MARKS_VERSION` 21 -> 22** (`instructions/marks.py`): the v22 paragraph; calls 124 (L1, L5), 125 (`OLDEST`
  stays 20: a v20 or v21 bundle re-scores at v22), 126 (FR-4 / FR-5); `instructions/marks.toml`'s v22 header. No number in
  `[marks]` moved.
- [x] T009 Fixtures and pins: `tests/v9_fixtures.GOOD_LISTS`' phrase *finding them* (a draft that meets every L rule);
  `test_instruction_score.py` (the blank-phrase words; a phrase in Keel's words is an `L1`; L5's red cases now a
  suggested Adoption effort and two suggested conditions; one suggested condition passes; the corpus-as-a-draft test
  drafts the phrase bare); `test_instruction_report.py` (*phrase: finding them*); every `MARKS_VERSION == 21` pin moved
  to 22 with why (`test_backtest`, `test_follow_ups_075`, `test_founder_walk_076`, `test_guide_marks`,
  `test_instruction_marks` -- the version, the calls 110-126, the marks file's v22 header --, `test_instruction_rescore`
  -- *cannot be re-scored at v22*, a v20 bundle re-scored at v22 --, `test_quality_081`, `test_recorded_path_074`,
  `test_sample_export`, `test_study_scopes`).

## FR-4 -- the adoption-friction frame is the cloud's -- `fd51cd4`

- [x] T010 `instructions/spoken.py` `framed` (402-407) on Adoption friction is `adoption_frame(asked)`,
  `ItemFrames.adoptionFriction` as `AskedRules.framed` reads it: a clause opening on *would / will / could / can / do
  you* (`questionPart`) is said *You'd ...*, a leading clause (`SpokenCap.leadingClause`, 132) said after it in the
  present while the whole fits 20, else the step alone; any other clause in the second person
  (`StrangerGrammar.secondPerson`), *you had to / have to / need to / needed to* as *you would have to / need to*
  (`wouldDo`), capitalised; then *Would you do that, or not?* (`ADOPTION_ASK`). 163's 12-word clause rule is the
  registry's option rule, read there, never restated.
- [x] T011 Tests: 163's slip (*would you hold your phone near the crib for ten seconds while your baby cried*) frames to
  20 words as code reads it (the harness read 21) and passes K2; 163's worked example 15; a leading clause; *had to*; one
  word more still K2.

## FR-5 -- K3 reads the framed line -- `1083f7a`

- [x] T012 `instructions/spoken.py` `face_faults`: on Adoption friction, K3 reads the clause as framed (the line before
  *Would you do that, or not?*): it passes when it says *you / your*, or when it opens on no subject other than the
  stranger (a base-form clause: the frame's *Would you* is its subject); a clause opening on a third-person subject
  (`THIRD_PERSON_OPENERS`: *the, a, an, this, that, these, those, it, its, he, she, ... someone, nobody, there, my, our,
  I, we*) faults, naming its framed words. Compatibility's K3 is unchanged.
- [x] T013 Tests: the 2026-10-30 screen's two clauses pass; *they'd clip ...* passes; *the cry ...*, *the room ...*,
  *it listens ...* fault; Compatibility's *did the phone sit within reach* still faults.

## FR-6 -- nothing else moves

The corpus (revision 19), the frames handed to the model (`context.asked_frame`), 089 / 090's frames, the marks beyond
L1 / L5 / K2 / K3's Adoption friction reading, the readers: untouched.

## Judgement calls

1. **`saved_list` and the Check screen's corpus list say the phrase bare too.** FR-1 names the scripted draft; the
   founder saves the draft as drawn, so the strict *stored as saved* and *drawn as drafted* checks would otherwise
   compare a bare wire phrase with *your way of*. The founder's typed Answer (`answer_text`) keeps the corpus's words: it
   is what a founder types, and 161 makes the model strip it.
2. **`MARKS_VERSION` moved (21 -> 22)**: `option_validity`'s reading moved both ways (a suggested Compatibility
   condition is met; a phrase in Keel's words is an L1; Adoption friction's K2 / K3 read the cloud's frame). One bump
   carries FR-3 to FR-5 (calls 124-126); `OLDEST` stays 20 because every rule reads the draft the bundle holds.
3. **`suggested_why` is not restated.** The cloud's L5 also notes a Compatibility suggestion without `suggested_why`; that
   is a note (a breach past the repair turn), not a refusal, and FR-3 names only the admission.
4. **K3 lives in `instructions/spoken.face_faults`**, not `instructions/validate.py` (the spec's name): `validate.py`
   carries no K3; `face_faults` is the one K3 the founder-lists screen and the ASKED screen score with.
5. **A third-person subject is read off the clause's first word** (`THIRD_PERSON_OPENERS`): grammar only, no trade
   words. A capitalised first word is not taken as a name (a model's clause opens lower-case; a name would open
   capitalised and pass -- named, not guarded).
6. **The cloud's past-tense turn is not restated** (*you wore* -> *you'd wear*, `was` -> `is` beyond the leading clause):
   it moves no word, so K2 counts the same, and K3 reads *you* either way.
7. **The ladder's skip detector was fixed** (FR-2, T006): it was silently skipping two registry tests on every 161
   checkout; making them run is how FR-2's rung is held to the registry.

## What did not hold

- **`make eval K=s005` on the stack** (no `L1` note in the journey) is the coordinator's after the merge.
- **The 2026-10-29 bundle reads worse at v22** (26/33 -> 24/33): it was written before 161, and its three Current
  solution drafts open on *your way of* -- the cloud's L1 now, the harness's too.
- **Importance's L1 (the draft list's minimum)** remains on both bundles: spec 091's.
