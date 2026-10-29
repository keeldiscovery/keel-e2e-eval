# Tasks 086 -- The harness reads corpus revision 18 and the follow-ups that name the thing

Branch `086-revision-18-and-the-gate` (worktree `wt/eval-086`, `.git` a file), off master `31c1dd8` (085 merged). Read
only: keel-cloud-docs -- the live checkout at `ad5f6441` (corpus revision 19, one past this spec) and two snapshots
exported by `git archive` into a scratch folder and named in `stack.toml` for the run only (restored after; never
committed): **`21395ab0`** (152's merge, the sha this spec's gate names) and **`1602f8b4`** (153's last docs commit:
152 + 154 + 153, still revision 18, before 155). `REVISION` 17 -> 18; `MARKS_VERSION` 21 and `RUBRIC_VERSION` 2
unchanged; `INTERVIEWER_MARKS_VERSION` 12 -> 13 (FR-5). **No paid call**: no walk, no reader, no adviser call, no
model, no `make eval`. Nothing merged or deployed; every commit pushed to the branch.

Built in one step: 154 had merged (`ba71504a`) and 153 too (`1602f8b4`) when this was built, so FR-5 went with the rest.

| Commit | What |
|---|---|
| `efb436f` | FR-1: `REVISION = 18`, the notes, `_REVISION_OF[17]`, the three fixtures, the refusal table, the version pins; `test_corpus_r17.py` renamed to `test_corpus_r18.py`, content unchanged (080's way) |
| `01267f6` | FR-2: rule D18 (`tests/test_corpus_r18.py`), D17 and D16 kept as records; the reader's rule C on 152's rate belief |
| `6f7e296` | FR-3: the pins that quote revision 18's moved words |
| `6c36650` | FR-5: the follow-ups name the thing (keel-cloud 154) |
| this commit | this file, `AGENTS.md`'s spec-086 paragraph |

FR-4 is **struck** (below); FR-6 needed no commit (below).

## Unit

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `31c1dd8`, keel-cloud-docs `21395ab0` snapshot | 3,448 | 75 | 40 | 207 |
| **branch, keel-cloud-docs `21395ab0` snapshot** | **3,709** | **0** | **0** | **64** |
| branch at FR-3 (`6f7e296`), `21395ab0` snapshot | 3,711 | 0 | 0 | 61 |
| branch at FR-3 (`6f7e296`), `1602f8b4` snapshot | 3,708 | 3 | 0 | 61 |
| **branch, keel-cloud-docs `1602f8b4` snapshot (153 + 154)** | **3,712** | **0** | **0** | **61** |
| master `31c1dd8`, live keel-cloud-docs `ad5f6441` | 3,444 | 79 | 40 | 207 |
| branch, live keel-cloud-docs `ad5f6441` | 3,448 | 78 | 40 | 207 |

On `21395ab0` master refuses every canon file (*revision is 18; this eval reads revision 17 only*) -- its 75 failures
and 40 errors are that refusal plus the pins that quote revision 17's words. **The branch is green on both snapshots.**
On `21395ab0` three more skip than on `1602f8b4`: the follow-up ladder's three reads of keel-cloud's registry and
composer, which skip by name there (*keel-cloud predates spec 154*) because that snapshot serves the old rows
(judgement call 1). The three that fail at FR-3 on `1602f8b4` are exactly those, before FR-5 moved the ladder. +1 on
`1602f8b4` against FR-3 is IM27's new mutation (a clip in the registry's bare words).

**On the live checkout** (revision 19) the branch's 78 failed and 40 errors are the same set as master's but for the
rename (`test_corpus_r17.py` -> `test_corpus_r18.py`, eleven node ids each side) and master's two extra (the ladder's
placeholder and defaults reads, red on master because 154 had merged; green on the branch). Every error and 72 of the
failures are `CorpusError: ... revision is 19; this eval reads revision 18 only`. The other six are all **spec 089's**
(revision 19, the three moved controls, the frames):

- `test_backtest.py:76` and `test_corpus_r18.py:135` / `:160` / `:276` -- revision 19 itself: D18 sees canon at 19
  beside the r17 record, 159 reworded decision sentences in `expected`, and `check_corpus_r18.py` refuses an r19 file;
- `test_follow_up_ladder.py:69` -- 159's Relative advantage scale: the registry's rung is now against `no_difference`,
  `worse` and reads *... wouldn't make much difference on your last {occasion}. What would make {job} better for you,
  if anything?*;
- `test_interviewer_marks.py:915` -- 158's ITEM_MORE clip *And one more?* (the harness's `ONE_MORE` still *And which
  one more?*).

## FR-1 -- revision 18 -- `efb436f`

- [x] T001 `instructions/corpus.py`: `REVISION = 18`; a *Revision 18 read* paragraph (152, the seven templates and the
  Prevalence phrases, the rate cost's belief, no standing moved) above revision 17's, which is kept; `_REVISION_OF[17]`
  names revision 17 as *MARKS_VERSION 21's corpus before keel-cloud 152 (the belief sentences of seven templates and
  the prevalence phrases in revision 17's words, ...)*, so a file at 17 is refused by name.
- [x] T002 The three fixtures (`tests/fixtures/corpus/09-fixture.yaml`, `10-fixture-b2b.yaml`,
  `tests/fixtures/backtest/99-broken.yaml`) at revision 18, their revision line alone. 080 made no `*-r17` fixture, so
  there is no `*-r18` one to make; their invented belief sentences are not read against the templates (the reader has
  no rule B) and stay.
- [x] T003 `tests/test_instruction_corpus_r11.py`'s refusal table reads *this eval reads revision 18 only* and gains
  revision 17; `REVISION == 18` in `test_follow_ups_075`, `test_founder_walk_076` (twice), `test_recorded_path_074`,
  `test_study_scopes`.

## FR-2 -- rule D18 -- `01267f6`

- [x] T004 `tests/test_corpus_r18.py` **D18**: the 35 canon entries beside keel-cloud's `corpus-r17/` and
  `backtest-r17/`; every leaf difference the revision line (17 -> 18), or on a golden entry one of 152's eight fields
  (`founder_calibration.<row>.belief_sentence` of Prevalence, Importance, Current solution, Compatibility, Relative
  advantage and Commitment; `belief_phrase` of Prevalence and Relative advantage -- `check_corpus_r18.py`'s
  `R18_GOLDEN`), strings both sides, all eight moved on each of the seven (56); or on a back-test entry the cost's
  `belief_sentence`, on exactly the eleven rate entries (09, 10, 12, 13, 17, 18, 19, 20, 21, 23, 26). 35 + 56 + 11
  differences, nothing else. The header is a YAML comment, so the parsed diff holds no trace of it.
- [x] T005 A second test: every entry's `expected` is revision 17's whole (no standing, drift, inside, n, median or
  verdict), and the new words are the templates' (Prevalence's phrase one of *Under 2 in 10 ... At least 8 in 10* and
  the sentence opening on it; *given them ...*; *Most ... would ... now.*; *... still falls short.*; *For most, ...*;
  *Of these ...*; the rate belief *The problem already costs the payer about ...: ...*).
- [x] T006 **D17 kept as the record**, mirror against mirror (`corpus-r16/` + `backtest-r16/` beside `corpus-r17/` +
  `backtest-r17/`), with its row's n and option counts; **D16** as 080 kept it. The cloud's `check_corpus_r18.py` OK on
  all 35; all 35 load at 18 (the 28 in back-test mode); r17's 03-lullaby refused by name. Rule Q and the rest of the
  file as they were.
- [x] T007 The reader's rule C (`instructions/chain.py` `cost_belief`, `CommercialChain.costBelief`): RATE reads *The
  problem already costs the payer about {figure} of {base} {per}: {loss}.* -- without it the eleven rate entries are
  refused at load. The answer-box test's revision-14 12-transload carries the record's rate belief so the read reaches
  the Answer box.

## FR-3 -- the pins -- `6f7e296`

- [x] T008 `instructions/marks.py`'s header: a *Corpus revision 18* paragraph above 17's -- the belief words moved, no
  standing; **v21 stands** (no mark scores a belief sentence: `compare_correctness` reports it, never marks it; `no_leak`
  reads the founder's `belief_phrase` as data under the same rule); the seven r18 files by sha256 (canon bytes at
  `21395ab0`, equal to `corpus-r18/`, unchanged through `1602f8b4`). `instructions/marks.toml`'s comment names
  revision 18 (no key moved).
- [x] T009 The pins, listed below with why.

**The marks digests** (revision 18, keel-cloud-docs `21395ab0`):

| File | sha256 |
|---|---|
| `01-countly.yaml` | `84e305923f67b9760f4f8b68f793490cfa5327b508f1860e8b45288d8875c499` |
| `02-compliancelog.yaml` | `3c8d964502cf413eace932a82bf8ea28bec13679957d31627f771010016084a2` |
| `03-lullaby.yaml` | `8b55d8e43bd6f5642a8019ea92f381f8398bca9610e808a8c2fbfcad9490f0ca` |
| `04-linerly.yaml` | `6d3dd62fb68f09a0c67bb3319fb3241fdaf7fe88f24bf2d51cccaee7bc830830` |
| `05-paidly.yaml` | `0d6f8a0a66ca7d2061487ac5046c95da797c4ba8c68f72eaa32ad67ff70e80e4` |
| `06-repeatline.yaml` | `5658999231d463408f7e4f8ff4abc476914a4e7203c799655e2c9cbfd9fe0a7b` |
| `07-mulchrun.yaml` | `9da91df12ef3a0f9a4eb8490216ddfe6ccc11c1d2f3b652d1b03fe6310b3d0f4` |

## FR-4 -- the gate without chips -- **struck**

keel-cloud 153 as merged (`2306e26a`, FR-2 amended 2026-10-29: the founder, *"put the chips back"*) serves the gate's
two chips as spec 123 FR-3 did -- they were only ever drawn with the story box after a Yes. So no gate pin moves:
`harness/vectors_screens.py`'s `GATE_RATHER_NOT_SAY`, `browser.py`'s CANT_RECALL / RATHER_NOT_SAY presses and the
journeys that press a chip stay as they are; 153's tasks.md says the same (*no eval or web pin moves for the chips*).
The branch is green on `1602f8b4`, which carries 153.

## FR-5 -- the follow-ups name the thing (keel-cloud 154) -- `6c36650`

- [x] T010 `harness/interviewer_fake.py`: `LADDER_SHA` `f280c5ae` -> `9f78b765`; `LADDER`'s nine rungs and `ALSO`'s three
  second stems at 154's text and spoken words (the headings, `against` sets and `ALSO`'s headings unchanged, as 154
  left them); `FILL_DEFAULTS` gains `{job}` *doing this*, `{solution_name}` *it*, `{step}` *that step*, and `{effort}`
  reads *doing that*; `WORTH_MORE` *What would make it worth more to you?*; `NO_NAME`, `named`, `would_not_pay_text`
  (*You said you wouldn't pay for {name}. What would change your mind?*), `price_said_back(question, band, name)`;
  `spoken_filled` (`FollowUpComposer.spoken`).
- [x] T011 `harness/vectors_script.py`: `job_gerund` (`SpokenCap.jobGerund`, `OBJECT_OPENERS`); `lock_values`
  (`FollowUpComposer.lockValues`: `{occasion}`, `{job}`, `{solution_name}`, and per rung `{founder_item}`, `{effort}`
  and `{step}` as -ing phrases, `{smaller_step}`); `follow_up_clip` (`FollowUpComposer.clip`). `follow_up_question`
  fills the lock's words on every rung and either stem, serves the said-as-spoken text and the spoken line filled, and
  names the idea in Relative advantage's *worse*, Buyer and payer asked about this purchase (*Who would have to agree
  to {name}, and what would they need to see?*), Price's said-back and would-not-pay, and Purchase friction asked about
  this purchase (*What would take the time in buying {name}?* / *What would slow down buying {name}, if anything?*).
- [x] T012 `evals/interviewer_leg.py`: each role's FOLLOW_UP clips are held to `One more thing.` + the filled words
  (`said`, from `vs.follow_up_clip`), and the served `followUps[].spoken` to the same words. `evals/interviewer_marks.py`
  IM27 reads the leg's `said` (a record without it reads the registry's line, as before): **`INTERVIEWER_MARKS_VERSION`
  12 -> 13** (judgement call 3).
- [x] T013 The pins, below. The spoken line on the AI link is the filled one wherever the walk composes it
  (`follow_up_plan` -> `follow_up_question`), so the six journeys' follow-up screens and clips move with the mirror.

## FR-6 -- decided before

- [x] T014 `quality/decisions.toml` D-2026-10-29-05 carries `merged = "21395ab0"` and D-2026-10-29-19 `merged =
  "078fe157"` (155's last docs commit, which carries 153, 154 and 155, the three specs D-19 names) -- both written on
  master at `c474dfe`; confirmed, no edit. 087's tests read the file's shape and pass on every tree above.

## Every pin moved

| Pin | Was | Now | Why |
|---|---|---|---|
| `test_corpus_r17.py` (renamed `test_corpus_r18.py`) | D17 against canon | D18 against canon; D17 and D16 mirror against mirror | FR-2 |
| `test_instruction_corpus_r11` refusal table | *reads revision 17 only* | *reads revision 18 only*, revision 17 refused by name | FR-1 |
| `REVISION == 17` (`test_follow_ups_075`, `test_founder_walk_076` x2, `test_recorded_path_074`, `test_study_scopes`) | 17 | 18 | FR-1 |
| `test_corpus_r11_shape` (two tests) | revision 17 | revision 18 | FR-1 |
| `test_instruction_marks::test_the_header_names_the_seven_r17_digests_...` | r17 digests at `88bfce8d` | `..._r18_digests_...`: the seven at `21395ab0`, *v21 stands* | the canon bytes moved |
| `test_instruction_report::test_the_calibration_block_...` | Lullaby's Prevalence phrase *Most*, sentence *Most of these parents* | *6 to 7 in 10*, *6 to 7 in 10 of these parents* | 152's Prevalence phrases |
| `instructions/registry.py` invariant 4 + `tests/fixtures/registry/slice.yaml` | `{value}` never on Relative advantage's template | `{value}` once on every template; the slice's five moved templates in 152's words | 152 `invariant4Templates`; on `21395ab0` the registry of record failed the old invariant 4, so the spoken-guard test skipped |
| `harness/vectors_script.PREVALENCE_OPTIONS` | *Only a few ... Nearly all* | *Under 2 in 10 ... At least 8 in 10* | 152's option rule; every corpus entry's chosen phrase is its bin's |
| `evals/corpus_scenario._hold_importance_check` / `_importance_needs_three` | *out of {n}.* at the sentence's end | *Of these {n},* at its start | 152's Importance template (S-005/006/007 read it on the Check screen and on the wire) |
| `instructions/brief_facts.DECISION_CHANGE["07-mulchrun"]` | *against your nearly all.* | *against your at least 8 in 10.* | 152's `DecisionChangeCorpusTest` |
| `test_follow_up_ladder` (ladder, placeholders, defaults, fill, script) | 118-era rungs, a spoken line with no brace, `Map.of` defaults | 154's rungs, spoken lines holding only the project's words (`SPOKEN_PLACEHOLDERS`), `ALSO` held to the registry, `Map.ofEntries` defaults with `NO_NAME`, `WORTH_MORE`; skip by name before 154 | FR-5 |
| `test_after_130` (price said back, owed price) | *... worth more?*, *it*, *for this. What would change that?* | *... worth more to you?*, the idea named (Lullaby's *a suggested reason for crying*), *What would change your mind?* | 154 FR-2 |
| `test_after_131::test_importances_follow_up_text_is_its_spoken_line` | *You put other difficulties ahead of this one. ...* | *You did not pick {the own item} as one to make easier. What made the others more pressing for you?* | 154 |
| `test_revision_16_walk` (RA spoken, Paidly's owed RA) | *You said it would not have made much difference. What would have?* | the template; *You said invoice payout service would have made no difference. What would make getting paid for finished work in time to cover the month better?* | 154 |
| `test_follow_ups_075::test_the_plan_composes_...` | the raw spoken line | the filled one (Paidly's job) | 154 |
| `test_interviewer_marks` (IM27 fixture, version) | clips in the registry's words; v12 | clips in filled words with `said`; a bare-words clip fails IM27; v13 | FR-5 |
| `INTERVIEWER_MARKS_VERSION == 12` (`test_interviewer_marks`, `test_recorded_path_074`, `test_founder_walk_076`) | 12 | 13 | FR-5 |

**Not moved, with why:** the brief-facts compare (`build/brief-facts/` is a Gradle output, absent from a `git archive`
snapshot, so those two tests skip there; 152 left the brief's card lines alone); the zero-spend compare and the
corpus overview (green on both snapshots); `quality/RUBRIC.md` (no anchor quotes a template; `RUBRIC_VERSION` 2); the
readers' prompts; the eval's own invented fixtures' belief sentences; the follow-up headings (154 left them); the
gallery's Fresco expected interview and `test_gallery.py:381` (*What would you start with instead?*) and its
*Nearly all* / *Most are open to* assumptions, and `tests/fixtures/sample/s006-reads.json` -- recorded runs of
2026-10-22, as 085 left them (rewriting them would falsify the record); `test_follow_ups_075`'s screen-walk question and
`test_interviewer_marks`'s `RA_TEXT` (any served string; they test the page walk and the marks, not the words).

## Acceptance

- [x] `make unit` on the `21395ab0` snapshot: 0 failed (and on `1602f8b4`, which carries 153 and 154).
- [x] `tests/test_corpus_r18.py` on keel-cloud at 152's merge or later: green on both snapshots (the live checkout is at
  revision 19: spec 089's).
- [ ] `make eval K=s005`, `K=s006`, `K=s007` on the local stack at a cloud sha carrying 153 and 154 and web master:
  **left for the coordinator** (the stack is down; starting it, and any journey, is the coordinator's).

## Judgement calls

1. **The ladder's registry reads skip by name before 154.** The gate's snapshot (`21395ab0`) predates 154, so the
   three tests that read keel-cloud's registry rows and composer source could not pass on it with 154's ladder; they
   skip (*keel-cloud predates spec 154*), as `_registry` already skipped a keel-cloud before 103, and the gate was run
   on `1602f8b4` too, where they run and pass. Every harness-only follow-up test runs on both.
2. **`1602f8b4` as the second snapshot**, not the live checkout or 155's `078fe157`: it is the last revision-18 commit
   carrying 152 + 153 + 154 and nothing of 155 (which this spec does not name; its registry change is guidance only and
   its said-back is code's) or 158-160.
3. **`INTERVIEWER_MARKS_VERSION` 12 -> 13.** IM27 now reads the clip words the leg records (filled from the project)
   rather than the registry's bare line -- a mark reading its record differently, the module's own rule for a bump, as
   144's lead-in moved it to 11.
4. **`MARKS_VERSION` 21 stands.** No mark scores a belief sentence; `no_leak` sweeps the founder's `belief_phrase` in the
   respondent stems by the same rule whatever the phrase says.
5. **Rule C moved in FR-2, invariant 4 in FR-3.** The reader cannot load the eleven rate back-tests without 152's rate
   belief, so it rides with D18; invariant 4 and the slice are a pin on the registry, so they ride with FR-3.
6. **The slice fixture's five moved templates in 152's words**, not only Relative advantage's that invariant 4 needed:
   the slice says it is the registry's words; nothing else in it was re-exported (its Importance read *out of five*
   before and was already stale).
7. **The harness's Prevalence defaults** take 152's capitalised phrases (152's judgement call 8), so a scripted draft
   and the recorded phrase never differ.
8. **`{founder_item}` in the clip** reads the served label where the walk has it and the saved list's own item
   otherwise (the try read gives no token to look the option up by); the served label is the founder's own words (R2).
9. **`{job}` is the entry's context job** (`_ctx(entry)["job"]`, as the read-back reads it): 03-lullaby's is *work out
   what the baby needs and settle them*, so the harness says *... and settling them* where 154's tasks.md (on 149's
   slots) says *settling the baby*.
10. **The harness's `gerund` stays 131's narrow mirror** (no 132 leading clause, a short verb list); `job_gerund` is
    built on it. Every corpus job reads as 154's examples do.

## What did not hold

- `make eval K=s005` / `s006` / `s007`: not run (the stack was down; the coordinator's).
- The live checkout is not green: revision 19 and keel-cloud 158-160 are spec 089's (the six named above, the rest the
  revision refusal).
- The brief-facts compare could not run on either snapshot (no `build/brief-facts/` in a `git archive`); it is not a
  revision-18 pin (152 moved no card line).
