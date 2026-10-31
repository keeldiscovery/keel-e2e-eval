# Tasks 115 -- The harness reads keel-cloud 174: the seven template and frame rules

Branch `115-the-harness-reads-the-seven-templates` (worktree `wt/keel-e2e-eval-115`, its own `make venv`), off master
`6549dfb` (115's FR-0 added to the spec; 4,604 passed / 6 failed / 5 errors / 54 skipped against keel-cloud-docs
`e68c0de4`, 114's tasks.md records the same). Built by Claude on 2026-10-31. Read only: keel-cloud-docs master --
`e68c0de4` (174 merged) when the build started, **`ab5b15ef` (177 merged) by the time it ended** --
`VectorCorpusFixture.spec174Reads`, `WindowFrame`, `SpokenForm.countAnswerLine`, `ItemFrames` (`compatibilityLabel`,
`fact`, `FACT_LABELS`), `FollowUpComposer` (`lockFact`, `onlyIfSaidBack`), `SavedList.ONLY_IF`,
`src/main/resources/keel/dimension-registry.json`, `FrequencyKeepsItsUnitTest`, 174's tasks.md (its *keel-e2e-eval pins
that must move* is the checklist below); keel-web master -- `d6dc5a9` (147) then **`7ac4d71` (148 merged)**. **No
stack, no model, no walk, no paid call.** Nothing merged into master; the branch pushed after every commit, never
force-pushed.

| Commit | What |
|---|---|
| `0652ff0` | FR-0: `corpus.spec174_escape` / `recorded_escape_is` (rules R and A), the walk's chip read through it, `served_escape_picks` sends Purchase friction's served code |
| `9c6cb74` | FR-1: the slice, invariant 4 on the decider template, `corpus.spec174_reads` and `engine_belief`, the Importance box, the money seed, the fact four, `spoken.is_fact`, the fact said back; re-pins |
| `0bfdcde` | FR-2: `window_first` / `counted_in` / `short_unit`, `frequency_held` with the unit kept, `count_answer_line`, `wording.frequency_respondent`; re-pins |
| `71bf41b` | FR-3: `interviewer_fake.only_if_said_back` beside the ladder, read by `follow_up_question` |
| `fcea01a` | FR-5: `tests/test_seven_templates_115.py` (76); the 110 record stand-in confined to its item; the record's tests skip by name with no brief facts |
| the docs commit | this file and `AGENTS.md`'s spec-115 paragraph |

## Unit (the gate)

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `6549dfb` against keel-cloud-docs `e68c0de4`, keel-web `d6dc5a9` (this worktree, before any change) | 4,604 | 6 | 5 | 54 |
| **branch at `fcea01a` (the last code; the docs commit adds none), keel-cloud-docs `ab5b15ef`, keel-web `7ac4d71`** | **4,682** | **0** | **0** | **63** |

+76 tests, all `tests/test_seven_templates_115.py` (4,604 + 6 + 5 + 54 + 76 = 4,745 = 4,682 + 63). **All eleven of
master's red are cleared**: `test_corpus_r11_shape.py::test_the_corpus_reads_the_same_through_the_exported_registry` and
`test_lock_frontier_110.py`'s three cost-item cases pass; `test_lock_frontier_110.py`'s two record tests and
`test_instruction_spoken.py`'s five pass against a fresh record (read from a scratch copy of keel-cloud-docs' 00:55
`build/spoken-corpus.txt` with an empty brief-facts beside it) and **skip by name** in the checkout as it stands, which
has no `build/brief-facts` (*not foreseen* 5). The 63 skipped are the 53 revision-2 readers master skips
(`test_corpus_script`, `test_s004_live_choices`, `test_policy_v8`) and ten on the missing brief facts: the record's
seven, `test_instruction_brief_facts.py`'s two, `test_corpus_r19.py`'s Lullaby guard. `make unit` was also green at
`fcea01a` (4,682 / 0 / 0 / 63) before the docs commit; the docs commit's run is the same.

## The checklist (keel-cloud 174's *keel-e2e-eval pins that must move*)

- [x] T001 **FR-0 the escape, one rule** (`instructions/corpus.py`). `SPEC174_ESCAPES = {commercial.purchase_friction:
  {cant_recall: cant_tell}}` and `spec174_escape(key, recorded)` (case kept: the walk's `CANT_RECALL` reads
  `CANT_TELL`); `recorded_escape_is(key, recorded, escape)` -- the same code, or the code the rule reads it as -- holds
  rule R (`_check_row`, a row's escape) and rule A (`_check_pick`, a chip). Revision 19 records `cant_recall` on that row
  in 19 entries (05-paidly, 06-repeatline, 07-mulchrun and 16 back-tests) and on Transload's one chip; nothing is
  rewritten, and a recorded `cant_tell` under a registry before 174 is still refused. The module docstring says so
  (*Revision 19 read through keel-cloud 174*, before 173's paragraph).
- [x] T002 **FR-0 the walk sends the code served** (`harness/vectors_script.py`): `_pick` reads a chip through the rule
  (Transload's Ray Castellano carries `CANT_TELL`); `served_escape_picks` -- 172's Current solution re-expression --
  takes Purchase friction too (`PURCHASE_FRICTION_ESCAPES`, `FRICTION_SENT_AS_SERVED`): a build before 174 serving
  `CANT_RECALL` gets that code, named as a finding; a 174 build moves nothing. `corpus_scenario._answer_one` records the
  escape served of the dimension each note names.
- [x] T003 **The registry slice** (FR-1, `tests/fixtures/registry/slice.yaml`, the header says so): Frequency's founder
  guidance (*... did a typical {actor} ...?*, `:61`'s row), Importance's (`:126`), Compatibility's (`:212`) and Purchase
  friction's (`:593`) belief templates, Purchase friction's escape `cant_tell` / *I can't tell* (`:607`) and its option
  rule (it quoted *I can't recall*), Commitment's `belief_template_decider` (`:645`) -- each the export's, byte for byte;
  nothing else re-exported (spec 040's hand-sized slice). `instructions/registry.py` invariant 4 holds the decider
  template to one `{value}`, as `DimensionRegistry` does.
- [x] T004 **The belief mirrors** (FR-1, `instructions/corpus.py`): `COMMITMENT_DECIDER_TEMPLATE`,
  `FRICTION_BELIEF_TEMPLATE`, `COMPATIBILITY_BELIEF_TEMPLATE`, `IMPORTANCE_BELIEF_TEMPLATE` (the export's), `belief_the`
  (`BeliefSentence.the`, not chain's `the_role`: an acronym-led role takes *the*, a capitalised name is kept) and
  **`spec174_reads(entry, key)`**, the cloud's `VectorCorpusFixture.spec174Reads` after 173's rule: *Most {people} would
  {step} now.* -> *In most cases the {role} would {step} now.* where the decision-maker is someone else (the persona's
  `decision_maker.role`); *Of these {n}, {item} is one of the two that {people} would most like made easier when {c}.*
  -> *{People} have {n} things that are hard when {c}. {Item} is one of the two they would most like made easier.*; *For
  most, {c}.* -> *For most {actor_plural}, {c}.*; *{step} slows the purchase most.* -> *{step} can slow or stop the
  purchase.*; anything else as 173 reads it. `engine_belief` reads every row through it, so the Keel-will-test box and
  the review rows (`corpus_scenario`, 113's two) hold the wire to 174's words. `instructions/corpus.py:26-28` and
  `instructions/marks.py:152-154` are revision 18's account, kept as history; the 174 reading is a paragraph before
  each (*v24 stands*).
- [x] T005 **The Importance box** (FR-1, `evals/corpus_scenario.py`; the spec's `:2111-2112` is `:2134`ff on this
  branch): `_hold_importance_check` reads the count off 174's first sentence (`importance_count` /
  `importance_count_words`: *have {n} things that are hard*), not *Of these {n},*; `_importance_needs_three` asserts
  the own item and two saved read *have three things that are hard* and compares the own list saved again with
  `engine_belief`, not the raw record (a third journey comparison through the rule).
- [x] T006 **`evals/scope_journey.py:80`, `:88`**: the money seed's Purchase friction belief *Setting it up with the POS
  provider can slow or stop the purchase.* and its escape `cant_tell` (the harness's own seed, the registry's words).
- [x] T007 **The fact four** (FR-1, `instructions/spoken.py:80`, `:139`, `:245`): `FACT_ANSWERS` is the registry's four
  (174 FR-3: *Yes, easily · Yes, with some steps · Only with help or approval · No*); `FACT_ANSWERS_128` keeps 128's
  *Yes · Mostly · Partly · No* for items a lock stored before 174, and `served_labels` reads both. `is_fact(asked, label)`
  ports `ItemFrames.fact(asked, label)` (`permission`, `head_verb`, `past_fact`, `condition_fact`; `PERMISSION_WORDS`,
  `FACT_HEADS`, `MODALS` held to `ItemFrames.java`).
- [x] T008 **The fact said back** (FR-1; the spec lists `harness/vectors_script.py:2608` under FR-2, `:2691` on this
  master): `follow_up_question` reads a fact by its tested condition (`spoken.is_fact`, the lock's `ItemFrames.fact`) as
  well as by a stored *Partly*; `fact_said_back` -- *You said no to this: {fact}.*, the registry's third said as picked
  (*You said only with help or approval: your phone was within reach of the cot. What got in the way?*), a stored
  *Partly* 128's *You said only partly to this:*; the have-fact on *No* of a fact either way.
- [x] T009 **The frequency frames** (FR-2, `harness/vectors_script.py:311-315`): `counted_in` (*on* a day or a night,
  *in* a week or a month), `short_unit` (a two-word unit's last word), `window_first`, `frequency_served` on it;
  `frequency_served_before174` and `frequency_unit_dropped` read the retired frames (160-173's *on how many {unit in
  full}*, 160's *on how many did*) on stored items. **`frequency_held`** (`:3132-3142`, `:3228` now): the unit-dropped step is gone;
  past the cap the clause is cut by its trailing phrases, else *... did that happen?*, the unit said (the grammar check
  is not mirrored, as before). `instructions/wording.py:213` (`frequency_respondent`) the same frame (the spec lists it
  under FR-1; it is one rule with `window_first`, so it moved with FR-2).
- [x] T010 **The spoken range** (FR-2): `spoken.count_answer_line` (`SpokenForm.countAnswerLine`: *Say a number from 1 to
  N.* past five steps, *A number from 1 to N.* at five or fewer); `tests/test_instruction_spoken.py:168` and
  `tests/test_controls_089.py:113` re-pinned. No spoken rule checks a number's answer line beyond its full stop (S8), so
  no mark moved.
- [x] T011 **`tests/test_after_131.py:383`** re-pinned with why: Fresco's *on how many days* (the two-word unit said once),
  the recount clause cut by its trailing phrase (*... the stock by hand?*), never the unit dropped.
- [x] T012 **The only-if follow-up** (FR-3): `harness/interviewer_fake.py`, beside the ladder -- `ONLY_IF`
  (`SavedList.ONLY_IF`), `ONLY_IF_ASK` (*What would have to happen for that to be true?*), `ONLY_IF_ASK_BEFORE_174` (155's
  *What would that need to look like?*), `only_if_said_back`. `follow_up_question` reads it where the cloud composes it:
  Adoption friction's conditional yes served *Only if {condition}* is said back whole, on the second stem, spoken as it
  reads; the registry's fixed *Yes, if it was clearly worth it* keeps the also stem.
- [x] T013 **The gallery fixtures stay** (FR-4): `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/` (*slows the
  purchase most*, *For most, on their last day, ...*) and `expected-interview-fresco.json` are untouched; a test reads
  Fresco's recorded beliefs in their frame and through the one rule in 174's words. The sample and corpus-shaped
  fixtures (`sample/s006-reads.json`, `corpus/09-fixture.yaml`, `10-fixture-b2b.yaml`, `backtest/99-broken.yaml`) record
  the older words the same way and are read through the rules.
- [x] T014 **Re-pinned with why** (each comment says *spec 115 ... re-pin*): `test_advantage_belief_113` (the golden
  record's standing row is Current solution's now -- 174 moved Importance; `engine_belief` compared three times);
  `test_corpus_r11_shape` (rules R and A through `recorded_escape_is`); `test_instruction_spoken` (Lullaby's fact four
  by the record's age, the registry's Lullaby block now the registry's four, the range line);
  `test_lock_frontier_110` (*in how many months*; the record stand-in moves Purchase friction's escape lines, inside
  their item); `test_instruction_window_frame` (*in how many weeks*); `test_controls_089` (the range line, `windowFirst`
  read off `WindowFrame.java`); `test_after_131` (T011).
- [x] T015 **Tests** (FR-5, `tests/test_seven_templates_115.py`, 76).
- [x] **`MARKS_VERSION` 24 stands**, no `PRICE_VERSION` / contract pin moves (contract 49): no mark scores a belief
  sentence, `spoken_form` reads the escape the registry names, and no rule moved.
- [ ] The founder's Frequency frame (*did a typical {actor}*): **no walk expects the founder's Frequency question** (the
  cloud composes it in code from the model's clause), so it lives in the slice's guidance alone; no mirror was added.

## Where the spec and the code differ (the code's patterns followed)

- **Line numbers moved**: `corpus_scenario.py:2111-2112` is `:2134`ff (`_hold_importance_check`) and `:2218`ff
  (`_importance_needs_three`), `vectors_script.py:2608` is `:2691`, `:3132-3142` is `:3228`ff on this branch.
- **`wording.py:213`** is listed under FR-1 and moved with FR-2's commit: it is `window_first`'s frame.
- **The fact said back** is listed under FR-2 (`:2608`) and is 174's FR-3 (Compatibility); it moved with FR-1's fact four.
- **The rule reads at the checks and at the walk's reading**, never at the reader's load: `Entry` keeps the record as
  written (`compare.build_input` sends the escapes as recorded, as the cloud's own fixture does), the pattern 173's
  `spec173_reads` set; the walk reads its chip through the rule in `_pick`, and `served_escape_picks` sends the served
  code, the 172 pattern.
- **`recorded_escape_is` is tolerant of both registries** (RECORDED_CONTROLS's pattern): the slice and the export read
  the same record, before or after 174.

## What the spec did not foresee

1. **The journeys compared the raw record three times, not two.** `_importance_needs_three` held the own list saved again
   to the corpus's `belief_sentence`; with 174's Importance served every strict journey would fail it. It reads
   `engine_belief` now (T005).
2. **The fact four needed a port of `ItemFrames.fact`.** Since 174 a fact is served the registry's four, so no *Partly*
   says an item is a fact: the follow-up's fact said back reads the tested condition (`spoken.is_fact`, T007, T008).
3. **The harness never composed the only-if line** (174's *not foreseen* 11): `follow_up_question` gave the also stem for
   a served *Only if ...* since keel-cloud 155. It is mirrored and read now (T012).
4. **Back-test founders' beliefs are not 152's sentences** (*Most are open to ...*, *When ..., X is one of the two
   difficulties ... out of five.*), so 174's rules leave them as recorded -- as the cloud's own rule does; their walks are
   not strict, so a mismatch is a finding.
5. **keel-cloud-docs' main checkout lost `build/brief-facts` mid-build**: a Gradle run of `SpokenGuidelinesCorpusTest`
   alone at 00:55 ET (after 177 merged) rewrote `build/spoken-corpus.txt` in 174's words and left no brief facts, so
   `cloud_corpus.read` refused and the record's seven tests errored. They skip by name now
   (`v9_fixtures.skip_without_brief_facts`), as they do with no record. Read against a scratch copy of that fresh record
   (an empty brief-facts beside it), every one of 115's record pins holds; **one test does not, and it is not 174's**:
   `test_instruction_spoken.py::test_the_corpus_record_keeps_every_rule_and_nothing_is_known_apart` expects 109 of 109,
   and a record written after keel-cloud 171 scores 104 of 109 -- the five golden Adoption friction `K2`s spec 112
   recorded (its tasks.md, *104 of 109*). It was hidden by the before-170 skip on the old record and will fail once the
   coordinator reruns both corpus tests in keel-cloud-docs. Left alone (spec 112's / keel-cloud 171's).
6. **keel-cloud 177 and keel-web 148 merged during the build**; no new failure came from either.
