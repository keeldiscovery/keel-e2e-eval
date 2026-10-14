# Spec 040 -- marks for the October redesign (marks v18)

Spec 11 of keel-cloud `canon/designs/redesign-plan-2026-10-14.md`, **its marks half**; the one input is
`canon/designs/design-2026-10-14.md` (§9 row "11 eval": *marks v-next: spoken-form checks on every corpus item, coverage
over 13 with no weight, the brief answers; DRY compare equal; certificate on the founder's word only*), with
`canon/designs/spoken-questions-guidelines.md` (§2-§5 the rules, §8 the marks) and the keel-e2e-eval follow-ups of
keel-cloud 087, 088 and 089. Sibling of keel-cloud-docs master `7b151f9` (087, 088, 089 merged: registry `VERSION` 4,
project document 20, `CONTRACT_VERSION` 13, routing table v11, `InferenceCharge` 7, corpus revision 10). The journey half
-- re-pointing the browser page objects, the legs and S-012 at the redesigned founder and respondent screens -- is a later
spec, once keel-web's specs 7, 8 and 10 land. **No model is called and no money is spent here; there is no run of record
and no certificate until the founder says so.**

## Requirements

- FR-001 **`MARKS_VERSION` 17 -> 18** (`instructions/marks.py`, `marks.toml`), judgement calls 77-90 below, numbered on
  from 76. Ten marks: `dimension_coverage`, `option_validity`, `no_leak`, `anchoring_accuracy` (0.90),
  `compare_correctness`, the rule-refusal rate (<= 0.02), `shape_refusals` (0), **`brief_answers`** (was
  `brief_paragraphs`), and two born here, **`spoken_form`** and **`brief_facts`** (1.00 each).
- FR-002 **Registry 4, all thirteen decide** (call 77): `instructions/registry.py` reads keel-cloud 087's registry --
  no `weight`, the seven founder lists' `founder.saves`, one `respondent.escape {code, label, counts}`, the fixed
  answers with their `supports` / `conditional` -- and checks 087's eight invariants (plus invariant 0: a registry
  still carrying `weight`, `respondent.chips` / `codes` / `asked_in_v1`, `common.chips` / `something_else` or
  `answers.status_vocabulary` is refused by name). `DEAL_BREAKERS`, `RESPONDENT_ESCAPES`, `FIXED_RESPONDENT_CODES`,
  `CODE_WRITTEN_RESPONDENT_CONTROLS` and `names_the_offer` are deleted. `RecallWindow` refuses a count below 2 and has
  no `CYCLES` / `SHIFTS` / `LAST_CYCLE` (D13).
- FR-003 **Corpus revision 10 only** (call 78): `instructions/corpus.py` refuses revision 9 by name and checks
  `sim/check_corpus_r10.py`'s shape half (S, W, L, R, A; r9's P, K, D, U, O) -- the recount stays the engine's.
  The unit fixtures (`tests/fixtures/corpus/09-fixture.yaml`, `10-fixture-b2b.yaml`) are revision 10, their `expected`
  the engine's own output, and `check_corpus_r10.py` prints OK for both.
- FR-004 **Contract 13 mirrored** (calls 83-85): `CALIBRATION_QUESTIONS` (`founder-lists.md`; context gains `answers`,
  each list dimension's `saves`, no `weight`; result a `list` per list dimension), `RESPONDENT_QUESTIONS` (item `{key,
  event?}`; no `founder_options`; items carry `escape`), the new **`ASKED`** screen (`asked.md`; context `dimension,
  context, market, items`; result `items[{index, asked}]`; `K1`-`K6`; job class `asked` on routing v11's `light`; the
  validator's ASKED case), and `BRIEF` (result `{headline, problem.answer, solution.answer, commercial.answer,
  next.tests, quotes}` under `B7`). Eight screens; `instructions/models.py` knows the `asked` class;
  `harness/vectors_script.context_keys_for` reads the eight-screen export.
- FR-005 **Spoken-form marks on every corpus item** (calls 79-81; guidelines §8): `instructions/cloud_corpus.py` runs
  keel-cloud's `SpokenGuidelinesCorpusTest` and `BriefFactsCorpusTest` once (`./gradlew test --rerun --tests ...`,
  zero spend) and reads `build/spoken-corpus.txt` and `build/brief-facts/<entry>.json` into the bundle
  (`cloud-corpus/`); `instructions/spoken.py` holds every composed item to `S1`-`S10` and every corpus `asked` face to
  `K2`-`K6`.
- FR-006 **Brief marks** (call 82): `brief_answers` is a case meeting seven marks restating keel-cloud 089's
  `BriefReading.check` (`shape`, `length`, `cites`, `broke`, `numbers`, `quotes`, `bans`), proved equal to the real
  validator; `brief_facts` is one check a card and one the pilot, keel-cloud's against `instructions/brief_facts.py`'s
  reading of the corpus. A `BRIEF` case is handed keel-cloud's own facts for its entry (call 84).
- FR-007 **Marks over thirteen, no weight** (calls 77, 78, 82): coverage over the vector's answered slice, the plan and
  the indices handed; a stage's verdict the worst of its dimensions (the engine's, `compare_correctness`); the brief's
  decision over every dimension; Purchase friction's turned reading and Buyer and payer's "Nobody else" are the engine's
  and the corpus's (the reader checks only their shapes); no guessed flag; one escape an item; no one-unit window.
- FR-008 **DRY compare equal**: `make instruction-eval DRY=1` against `7b151f9` measures `compare_correctness`,
  `spoken_form` and `brief_facts` for real and every model mark unmeasured (`passed: false` by construction).
- FR-009 **`rescore.py` refuses every bundle below 18** (call 88), v17 by name.
- FR-010 **Dead code deleted**: weight tiers, DEAL_BREAKERS, `ROUGH_GUESS` / `rough`, *Something else*, `RATHER_NOT_SAY`
  on items, the model-written option and distractor checks, W3 / W7 / W8 on question text, call 56's reported wording
  counts (`wording.reported`, `long_options`, `report.wording_html`), the one-unit window (`frames_frequency`,
  `vectors_script.one_unit_window`, the `CYCLES` / `SHIFTS` words), `brief_paragraphs` and the brief's tiles /
  conclusion / infer / sharpest / `next.sentence`, `context.founder_option_codes` / `founder_option_labels`, the old
  brief figures (`observed_of`, `cost_figure`, `price_figure`, `ability_figure`, `brief_dimension`, `vectors_for`).
- FR-011 **DRIFT**: #74 closed by D13 (by construction; not yet observed live); #76 (keel-cloud's validator reports an
  `L` refusal as shape) and #77 (five corpus wording items) recorded.

## Results

- `make unit`: **1,818 passed / 77 skipped** (against keel-cloud-docs `7b151f9`; before this spec the same checkout gave
  1,608 passed / 31 failed / 119 skipped, and 039 recorded 1,705 / 53 against `b8a4eed`). The 77 skips: 53 are 039's
  (the r2-shape readers of `tests/test_corpus_script.py`, `test_s004_live_choices.py`, `test_policy_v8.py`, spec 029
  O-1) and 24 are call 89's (23 in `tests/test_vectors_journey.py`, 1 in `tests/test_journey_through_a_host.py`). The
  former r9 canon skips (`CANON_NOT_R7`) are gone: the canon tests run at r10.
- `make instruction-eval DRY=1` against keel-cloud-docs `7b151f9` (`runs/20261014T034458Z-instructions`, gitignored):
  `compare_correctness` **108 of 108** (15 x 4 B2C + 16 x 3 B2B), `spoken_form` **104 of 104** (74 composed items + 35
  faces, 5 known apart), `brief_facts` **94 of 94** (cards + pilot; only spec 082's insight words reported), every
  model mark unmeasured, `passed: false`. 447 model cases at N=3 (149 at N=1): 63 interpretation, 63 calibration, 42
  asked, 63 respondent, 195 interpret, 21 brief; denominators per N: coverage 80 + 81 + 35, option_validity 122,
  no_leak 35 sweeps. The eval's own estimate for the full run: $17.88.

## Judgement calls

Numbered on from 76 (the last one 038 used); each is written out in full in `instructions/marks.py`'s docstring, where
the rubric's calls live, and summarised here.

77. **Registry 4, all thirteen decide.** The registry is read with no weight; the removed registry-3 keys are refused
    by name (invariant 0), never ignored; the eight invariants are 087's (FR-002).
78. **Corpus revision 10, shape half only.** The reader refuses any other revision by name and checks the shape rules
    of `check_corpus_r10.py` against the registry (a list's `saves`, a row's control / codes / escape, a pick's code);
    the recount is the engine's. Drifts are `both | none | stronger | short`; `deciding` is any dimension of its
    vector, `null` exactly when `NOT_TESTED`. Frequency's pick is held to the founder's own "out of N" (not the
    window's count: 05-paidly asks "invoices out of 7" over a 3-month window, as the checker does).
79. **`spoken_form` reads keel-cloud's composed record, not a copy of the renderer.** The eval runs keel-cloud's own
    corpus test and checks the record's shape against §2-§5 (`S1`-`S10`); the two unchanged frames (Existing
    sacrifice, Relative advantage) are held to **25 words until the founder decides** (keel-cloud 088 call 12: four
    corpus items run 21-24). `spoken-corpus.txt`'s option lists are parsed with the labels the item can carry, so a
    comma inside a label stays one option.
80. **The three-word option floor binds the founder's words only** (Importance's and Current solution's five); the
    registry's fixed answers and Price's bands are the record (keel-cloud 088 call 14).
81. **Five corpus wording items are known, named and out of the denominator** (`spoken.KNOWN`, DRIFT #77): 06's
    Commitment step and four Compatibility faces with no *you* -- 01's (088 named it), and 02's, 03's and 07's, which
    this mark found beside it. A known item no longer found is a fault, so the ledger shrinks with the corpus.
82. **The brief is answered, and its facts are compared.** `brief_answers` (seven marks) replaces `brief_paragraphs`;
    `brief_facts` marks the cards (key, name, number, line, status, the verdict half of `statusWords`) and the pilot,
    and reports the insight half, the decision, the vector words, `broke` and `notAsked` (all equal on r10).
83. **The respondent job writes the gate's clause and nothing else.** Coverage is every planned `{key}`; validity the
    gate alone (E1-E4); `no_leak` sweeps A and B over that clause; anything else written is not read. W3 / W7 / W8 and
    call 56's wording counts retire here (no model question text exists).
84. **Eight screens; `ASKED` is a subject; `BRIEF` gets keel-cloud's facts.** One ASKED case a saved Compatibility and
    Adoption friction list an entry, handed the corpus's labels; K1 is coverage, K2-K6 validity. A BRIEF case's facts
    are keel-cloud's own (`BriefFactsCorpusTest`) where the run has them, else this repository's reading (the unit
    fixtures); its meta says which.
85. **The founder-lists job is marked by code, a drafted face to the K rules too.** Stricter than the aggregate's L4
    (words and no `?`), because a face the founder keeps is never re-phrased and reaches a stranger as drafted (088
    FR-003's vouching).
86. **An `L` refusal is a rule** (DRIFT #76): the validator's rule-id pattern lacks `L`, so a shape refusal whose reason
    opens `L<n>: ` is read as rule `L<n>` until keel-cloud adds the letter.
87. **`ASKED` is redrawn once, like the question screens** (call 41); the ladder's second rung (one turn on
    `standard`) is a routing step this eval does not model.
88. **`rescore.py` refuses every bundle below 18**, v17 by name.
89. **The journey's corpus-reading unit tests skip by name at revision 10.** `harness/vectors_script.py`'s results and
    typed inputs still write revision 9's shapes; re-pointing them is the later journey spec's. What reads the export
    (the keys table) reads the new shape now, and the one-unit branches are deleted (S-005's spec-078 step inverted to
    D13's) -- nothing else in `evals/` or the page objects is touched.
90. **`BRIEF` is read as taken by the call that judges it.** keel-cloud 086 removed the validator's last
    `InferenceScreen.BRIEF` reference, so `validate.shapes_taken` read BRIEF as not taken (a real run would have left
    BRIEF's refusal rate unmeasured); `BriefReading.check(` is now a marker beside the constant.

Smaller readings, recorded beside the calls they belong to: W9 (no money) is asked of every calibration entry the
model writes, Frequency / Price / Existing sacrifice included, as keel-cloud's `refuseMoney` reads every entry (call
85); a list's `founder_phrase` in the BRIEF context's `beliefs` is the list's own phrase (Current solution) else the
tested item's label (call 84); an entry keel-cloud composed no item for is one unit of `spoken_form`, never clean
(call 79); `MODELS=` refuses a pin file that names no `asked` class, so spec 029's frozen
`contracts/models-screen.json` no longer loads (call 84).

## Follow-ups

### The next corpus revision (not edited here: the plan allows one corpus revision and 087 spent it)

- `06-repeatline` Commitment step *introduce you to the practice's IT supplier* composes *would you introduce you to the
  practice's IT supplier, or not?* (`S10`) -- reword the step in the stranger's base form (e.g. *introduce us to your IT
  supplier* said as the founder's ask, or *put us in touch with your IT supplier*).
- `01-countly` Compatibility face *did the invoice come with the delivery itself* has no *you* (`K3`); so do
  `02-compliancelog`'s *was every completion already recorded in the learning system*, `03-lullaby`'s *was the room quiet
  enough for a phone to hear the cry* and `07-mulchrun`'s *was there room at the curb of that job for a mulch drop* --
  this mark found the last three beside the one keel-cloud 088 saw. When the revision lands, strike them from
  `spoken.KNOWN` (the mark fails until it is struck).

### keel-cloud

- Add `L` to `ScreenContractTool.VECTOR_RULE` (DRIFT #76), then delete `validate._reclassified`.
- Write the composed wording as JSON beside `spoken-corpus.txt` (a contract, not a reader's text).
- Open for the founder (088 call 12): shorten Existing sacrifice's and Relative advantage's frames, or bound their
  slots; `spoken.LONG_FRAMES` then goes and `S1` holds every stem to 20.

### The later journey spec (once keel-web specs 7, 8 and 10 land)

- `harness/vectors_script.py`: answer `CALIBRATION_QUESTIONS` with `list` drafts from each entry's founder lists,
  `RESPONDENT_QUESTIONS` with `{key, event}`, `ASKED` with the corpus's own faces, `BRIEF` with headline + three answers
  (citing `broke`); type the founder's Answer / Check / Choose screens (lists, the picked index, Importance's own +
  four rivals, Current solution's phrase, Commitment's one step) and each person's picks as revision 10 records them
  (two codes on Importance, the fixed answers, `{chip: <escape>}`, the commercial link's idea screen first).
- `harness/vectors_screens.py` / `harness/browser.py` page objects: the 22 new founder screens (one dimension a screen,
  counters and dots, the locked side nav, Choose radios), the respondent screens of §5.1 (pick two, fixed four / three,
  one escape, no removed chip), the brief's two pages (cards, the pilot tile, the breakdown) and the overview's third
  tile.
- `evals/corpus_scenario.py`: the legs above; the `leg_calibrate` DRIFT #74 wire step goes (nothing left to send);
  S-005's Frequency is now asked on Countly's {4, WEEKS}; un-skip `tests/test_vectors_journey.py` and the one
  `tests/test_journey_through_a_host.py` test (call 89).
- S-012: leg two on the same legs, `strict=False`; the Keel door unchanged.

### Runs that spend money -- the founder's to say yes to (none run here)

At the eval's own estimate of about $0.04 a case (the v9 run of record was $19.75 for 414 cases), on Claude with
`MODELS=exported`:

- `make instruction-screen HOST=claude WHY=instruction:asked.md K=asked N=3 MODELS=exported` -- the 14 ASKED cases x 3
  on the `light` tier: **about $1-3** (the design says "about $3"); before routing v11's `asked: light` row is trusted.
- `make instruction-screen HOST=claude WHY=instruction:respondent-questions.md K=respondent N=3 MODELS=exported` --
  21 cases x 3: **about $2.50** (E4 is new).
- `make instruction-screen HOST=claude WHY=instruction:brief.md K=brief N=3 MODELS=exported` -- 7 cases x 3: **about
  $1-2** (`brief.md` rewritten by 089, unscreened).
- `make instruction-screen HOST=claude WHY=instruction:founder-lists.md K=calibration N=3 MODELS=exported` -- 21 cases x
  3: **about $2.50-3** (new instruction, unscreened).
- The certificate: `make instruction-eval HOST=claude WHY=marks:18 MODELS=exported` -- 149 model cases x 3 = 447:
  **about $18-22 and 2.5-3 h**, on the founder's word only.
