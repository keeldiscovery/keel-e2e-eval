# Tasks 148 -- The harness mirrors round A: keel-cloud 238 to 241 and keel-web 183

Branch `148-the-harness-mirrors-round-a`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-148` (`.git`
a file, asserted first), cut at master `00625f6`. Built by a builder (Claude Opus 5.5) on 2026-11-09 ET. Read only:
keel-cloud-docs master **`155eaca9`** (238, 239, 240, 241 merged: the final cloud sha of the round) and keel-web master
**`36d069ed`** (183 merged). Nothing paid: no stack, no model, no key, no walk, no journey, no cycle -- the unit suite
only. Not merged; master untouched; every commit pushed as it landed. The corpus yaml, `quality/decisions.toml`, the
readers' prompts and rubric and `RUBRIC_VERSION` untouched.

**Contracts**: `x-keel-contract` 63 and `CONTRACT_VERSION` 25, unchanged (nothing in the round moved a shape).
**Digest**: `CARDS_SHA256` **before `42fa94dd18d99c3800e507c2225d4e5244d8654425f3287447389ce56c15c0e1`** (237), through
238's `d764f34fd23127c001ac61f1cfddbedc1adf7ce9ec520144765161cfceaa81d2` and 239's
`94f9edc648dd57e76df30d788e7fff86f8cf5fc1ef7f785e36d71574eaf809a7` (240 moved no card), **after
`78bd11674018b1e2644b2de99256e1fe3c2c781e0f6fca7cefab68fe98e86307`** (241) = `RespondentReview.CARDS_SHA256` at
`155eaca9`. **Instruction bytes at `155eaca9`** (pinned, `INSTRUCTION_BYTES`): `respondent-questions.md` 9,957 (238:
9,952; 239: 9,957; under 170's 9,969), `problem-interpret.md` 15,391, `solution-mechanism.md` 8,747.

| Commit | What |
|---|---|
| `6b192d3` | FR-1 the cards' byte copy; the digest pin chain moved |
| `2ce81bd` | FR-2 (238) the gate: E7's three refusals, E9's fourth, E8's blame and verdicts; the named stop; the notes |
| `504966f` | FR-3 (239) Existing sacrifice: LossNotDone, the line's base, the unit, the part-3 job, the Check's note |
| `d910eed` | FR-4 (240) the reveal heard once: M8 over the reveal, the M8 note's path, the scripted lines redrafted |
| `4fdbf0e` | FR-5 (241) Ability to pay's two labels |
| `5fae998` | FR-6 (web 183) the window question: the typed when, the WHO's first comma, the note hook, 2 of 2's read-back |
| `10c52ec` | FR-7 the record: round A cited; `gate_refusals` / `stop_rule` in `backtest.json`; the gate line |
| (this) | tasks.md |

## What was built, per FR

- [x] **FR-1 the digest** (`6b192d3`). `quality/readers/dimensions.md` copied byte for byte from `155eaca9`'s
  `dimension-cards.md` (238: Prevalence §2, *The act that hurts, read against the segment*; 239: Existing sacrifice §2,
  §6; 241: Ability to pay §2, §5, §6). `CARDS_SHA256_141` (the one constant the 211-237 pins read) moved in place; 147's
  digest pin holds 237's as one it may have been (as 147 did 235's). `tests/test_cloud_238_241_mirror_148.py` pins
  `CARDS_SHA256_238` / `_239` / `_241` (four distinct digests in the chain) and each spec's card words.
- [x] **FR-2 the gate (238)** (`2ce81bd`).
  - `instructions/wording.py`: `routine_fault(event, routine, went_wrong, actor_plural, circumstance=None, seed=None)`
    -- 212's test, then **the segment** (FR-1; an event turning on a negation skipped), then on an event E8 does not
    fault **the hurt's kind** (FR-3) and, with the seed in hand, **a new word** (`new_word`, `new_word_fault`; `E8_OWN`
    never a new word); `no_sayer_fault`'s fourth test (FR-2, `hurt_words`, negated or not); `packed_fault`'s blame at the
    head (`BLAME_HEADS`, `FAIL_FORMS`, `blame_head`, `blame_fault`) after the judgement test; `VERDICT_WORDS` +
    *less than it could*, *more than it should*; `HURT_SENTENCE`, `ROUTINE_TEST`, `NO_SAYER_TEST` built on it. Checked
    word for word against `TheGateAsksTheActThatHurtsTest` (the florist, the print shop, the choir, the bakery, the milk,
    Lullaby). `instructions/score.py`'s `act_that_hurts` hands E7 the circumstance (and a seed, where in hand).
  - The walk: `corpus_scenario.gate_refusal(said, vector)` names each E7 / E9 `RESULT_INVALID` by rule and refusal
    (`GATE_REFUSALS`: *the segment*, *the hurt's kind dropped*, *a word the founder never gave*, *the routine*, *the
    no-sayer names no word of the hurt*, *... set apart by the routine*, *... outside the segment*, *... missing*, *what
    might have been*) on its `result.questions[N]` path -- the project step's seed refusal (`wordTheFounderGave`) reads
    the same; `_retried`'s finding carries `rule` / `refusal` / `spec`; past the retries `_wait_calibration` stops with
    *... FAILED -- stopped by E7 (the segment, keel-cloud 238 FR-1) past the repair turn: ...*;
    `Journey.gate_refusals`. E8 (blame, the two verdicts) is never a gate refusal: `LOCK_NOTES` gains **E7** (a named
    stop) and **E8** (*served with the note past the repair turn, never a stop*), E9's meaning names 238 FR-2.
  - The mirror's own test that a served gate is never the routine: `wording.inside_the_segment` / `gate_clause` --
    `backtest.cloud_131` adds `gate_in_the_segment`, a finding *the served gate asks what every one of them does in the
    segment -- its words all the circumstance's (keel-cloud 238 FR-1)*, never a stop; every golden scripted gate is
    never inside its segment (pinned).
  - Fixtures (the harness's, the corpus untouched): Countly's, Linerly's and Mulchrun's scripted no-sayers gain the
    hurt's word (*..., so no stock was recounted*, *..., so no time was lost*, *..., so nobody waited*); the Lullaby
    draft in `test_instruction_score` carries Lullaby's own routine / went_wrong / no-sayer (it carried the keys
    fixture's). Pins moved as 238 moved them: 216's agent example (*an agent whose booking calls never rang out*), 224's
    *fail to* example (*had the log fail to save*), 141's Codyco clause (*had a booking call ring out unanswered*), 216's
    `NO_SAYER_TEST` source pin, 131's back-test gate test (131's circumstance gate is a 238 finding now).
- [x] **FR-3 Existing sacrifice (239)** (`504966f`).
  - `harness/vectors_script.py`: `LossNotDone` mirrored -- `banned_word` (`loss_word` + `NEUTRAL_PHRASES`), the plain
    not-done (`_not_done_rungs`: *un-* + participle, the card's four banned verbs with their own object), the founder's
    line said to the person (`_as_typed_rungs`, `_seen_go`), `loss_not_done` -> `(stem, as_typed)`;
    `_rate_stem` -> `(served, wanted, share, measure, as_typed, per)`, `wanted` decided on the served stem
    (`says_a_neutral_verb`), the fallback where wanted or a banned word; the place rung gone; `asked_base` / `line_base`
    / `base_note`; `per_unit` in the ladder, the clause's frames and the B2B label; `check_note`, `sacrifice_note`
    (`VectorsController.sacrificeNote`'s join), `framed_per`; the hours path *did ... not get*; `loss_clause_question`
    refuses any banned word.
  - `respondent_jobs` gains `(3, link)` on a no-gate scope where the clause is wanted (`part_three_writes`: the chain,
    the item would carry a neutral verb, part 3 asks something on its link -- the decision-maker's on B2B);
    `respondent_result` carries part 3's `loss_clause` there (part 1's only where the gate is served); `loss_clause_wanted`
    on `asked_base`.
  - The walk: `_lock_lands` names the part-3 job (*part 3, the Existing sacrifice item's clause on a study with no part
    1*) and expects one interactionId; a served banned verb is `SACRIFICE_BANNED` (*FAULT: ...*), a finding never a
    stop; after the lock the COMMERCIAL view's Existing sacrifice `note` is `SACRIFICE_NOTE` (`sacrifice_note_finding`,
    `as_typed` / `base` flags). Every corpus and back-test entry's chain item, and every fallback rung on it, says no
    banned word (pinned).
  - Pins moved as 239 moved them (`CostQuestionInTheirWordsTest`, `SacrificeItemNamesTheLossTest`,
    `TheQuestionScreensDefectsTest`): 110's frames (cash decision, reservation shift, quote, conversation, billing,
    shipment, the no-line cases, the sale's line, the GPU label), 110's three entries, 141's five entries. The
    seventeen worked cases (`test_the_mirror_is_keel_clouds_seventeen_worked_cases`, red at the base) green again.
- [x] **FR-4 the reveal (240)** (`d910eed`).
  - `harness/vectors_script.py`: `said_twice` (`IdeaLines.saidTwice`: names, joined words, two plain words in a row,
    the what line's kind; the belief's frame not counted; a word inside a longer thing not named apart), `kind_of`,
    `what_is`, `card_line`, `IDEA_SMALL_WORDS`, `CLOSES_THE_PHRASE`; `m8_breaches` (each how voice, the line's path, the
    cloud's words). Checked against 240's two reveals (Sproutcap, Shelfwise) and the cloud's breach text.
  - `evals/backtest.py`: `LOCK_NOTES["M8"]` is 240's (*a name, noun or phrase heard twice across the reveal*);
    `m8_heard_again` reads `M8: 'X'[, 'Y'] (is|are) heard again in the (what line|how line|belief)` and the breach
    note's own path (`result.idea_what` / `result.short_name`, `result.idea_how.primary` / `.decider`,
    `result.idea_belief`) into the lock note's `heard_again`; 207's old words read by name only, as before.
  - The walk: `reveal_heard_once` reads the served idea check (the typed name, what it is, the how, the belief) for M8
    and for a dropped hedge (`belief_hedge_dropped`: where the seed says *target* / *aim* / *expect* / *estimate*, the
    belief opens *would* + that verb, never *would earn*) -- `M8_SERVED` / `HEDGE_SERVED` findings, never a stop.
  - The scripted reveals redrafted heard once (a fixture change, no corpus answer moved): `idea_lines` takes the first
    how form (whole; without its output; without its trigger; the mechanism alone) and belief (on the circumstance;
    `BELIEF_POINTS_BACK`, *make a real difference to all of that.*) that says nothing twice beside the suggested what
    line. Moved: Compliancelog (how without its output, the belief points back), Lullaby (how without its trigger: its
    *reason* is the what line's kind), Paidly (how without *within seven days*), Repeatline (how without *the request
    filed*). Countly, Linerly and Mulchrun compose as before.
- [x] **FR-5 Ability to pay (241)** (`4fdbf0e`). `test_dimension_cards_131`'s served options read *Charged back to
  whoever uses it* and *New money from outside, such as a grant*; the new file pins the registry's five labels under
  their codes and order, no label naming a team, site, department or branch, `BUDGET_SUPPORTS` unmoved. No other
  mirror carries a label.
- [x] **FR-6 the window question (web 183)** (`5fae998`). `vectors_screens.typed_when_clause_of`, `window_people_of`,
  `window_label_of` (the read's occasion clause -> its *When* clause -> the typed when -> *the last time it happened*),
  checked case for case against `window-names-the-moment-183.test.tsx` and the web's owed Codyco example (its typos
  the persona file's). `corpus_scenario.window_page_faults(page, window, typed)`: on the walk's 2 of 2 the heading is
  the typed when's -- a fault naming *keel-web 183 FR-1* where it reads *the last time it happened* over a typed when,
  or parts from the mirror. `SACRIFICE_NOTE_TESTID` (`[data-testid=sacrifice-note]`) read on the cost screen before it
  is touched (`sacrifice_note` on the screen record). `read_back("context-window")` hands no summary
  (`CONTEXT_WINDOW_NO_SUMMARY`) and the *Keel understands* sentence apart as `next_screen_understands`.
- [x] **FR-7 the record** (`10c52ec`). `backtest.json` always carries `gate_refusals` (empty where none: its presence
  marks a 148 bundle) and `stop_rule` where the walk stopped on one; `backtest.md` says *stopped by E7 (the segment,
  keel-cloud 238 FR-1) on PROBLEM* beside the failed step. `quality/cycle.py`: `Study.gate_refused` / `stop_rule`
  (`study_gate`); the review line cites `ROUND_A_CITED` (*spec 209, keel-cloud 232, 233, 235, 236, 237, 238, 239, 240,
  241*) on a record of 148's walks; `gate_line`: *the gate (keel-cloud 238, 239, 240, 241: the round's mirrors, spec
  148): n E7 / E9 refusals of Keel's AI over m walks ...; stopped by rule on k: {entry} · {scope} E7 (the segment, ...)*.
  A record before 148 reads as 147 wrote it (pinned).
- [x] **FR-8 tests** -- below.

## Gate

`make unit` (the worktree's `.venv` a symlink to the main checkout's venv, ignored by git)
against keel-cloud-docs `155eaca9`, keel-web `36d069ed`:

- Before (`00625f6`): **12 failed, 5731 passed, 81 skipped in 327.14s** -- the eight digest pins (211, 212's cards line,
  213, 216, 219-228, 232, 233, 235, 237), 216's `NO_SAYER_TEST` source pin, 224's verdict list, and the seventeen
  worked cases (`test_lock_frontier_110`, 239's moved fixtures).
- After (`10c52ec`, the last code; this commit adds tasks.md only): **5783 passed, 81 skipped in 311.98s (0:05:11), 0 failed**, 2026-11-09 13:12 ET -- the twelve back to green, nothing else red. (A run with `PY=` overridden on the make line fails `test_backtest_host`'s byte-for-byte dry run of `make backtest`: the override reaches the nested make; an artifact of the invocation, green under plain `make unit`.)
- +40 tests (5743 -> 5783): `tests/test_cloud_238_241_mirror_148.py` (35 functions, 40 cases with the parametrised refusals).
  Pins moved in place, none weakened: `CARDS_SHA256_141`; 147's digest pin; 216's agent example and E9 source pin; 141's
  verdict map (*fail to*, the two new words), Codyco's clause and the five entries' items; 110's frames, labels and
  three entries; 131's Ability to pay options; 131's back-test gate test (a 238 finding added); 097's read-back.
- `tests/test_reader_sees_the_whole_screen_140.py::test_a_save_past_the_budget_still_stops_the_walk` failed once in a
  loaded full run during the build and passed alone (a timing test; nothing of 148 touches it) -- watch it.

## Judgement calls

1. **Commit trailers** name the model that built them (*Claude Opus 5.5*, the session's attribution), not the brief's
   *Claude Fable 5.1* -- 147's precedent.
2. **The fallback no-sayer stays** (`NO_SAYER_ANY`, *one of them for whom it went right that time*): it names no word
   of the hurt, so 238's E9 refuses it -- but only on a back-test entry's scripted Prevalence, which no scripted journey
   walks (the cycle runs Keel's model). The test names that refusal instead of asserting a pass.
3. **Lullaby's scripted clause draws E7's new word *work* at the project step** (*had to work out why their baby was
   crying*: *work* is in the founder's typed job, *work out what the baby needs*, which is none of 238's four sources --
   its judgement call 5; the corpus seed says *can't tell what the cry means*). Left as the cloud's `VectorFixtures`
   words (216 judgement call 8) and pinned: no scripted journey walks Lullaby (S-012 is the host's model). Owed to
   keel-cloud as an open question (below).
4. **E7 / E9 are a named stop by their words**, not by a new wire field: `gate_refusal` reads the refused interaction's
   `status: path: why` (`RESULT_INVALID` only); the walk's behaviour is as before (retry while retries last, then the
   step fails) -- the stop now names the rule, and the bundle records each refusal.
5. **The served gate's segment test is FR-1's alone** (`inside_the_segment`): the routine is not in a served gate's
   hand, so the back-test reads the served clause against the context's circumstance only -- a finding.
6. **The part-3 job's `condition` is not scripted**: the person's link keeps spec 166's screener (the job's chip held,
   else code's); the script sends none, so code's stands as before. No golden entry (all off the chain) starts a part-3
   job, so S-016's scripted money-only walks are unchanged; on the back-test entries under money alone Palus, Codyco,
   Veles (decision-maker's link), AirCaps and Taiga (the person's) start one.
7. **The served banned verb is a FAULT finding, not a stop** (the brief's *as a fault, not a stop*); the drift finding
   against the mirror stays beside it.
8. **The scripted reveal ladder** (FR-4) is the harness's, persona-free: forms of the corpus's own four mechanism
   fields and the cloud's own pointer (*all of that*) -- the first heard once is taken, so an entry already heard once is
   composed byte for byte as before.
9. **The hedge check is the walk's, not code's** (240 judgement call 1: code cannot read a hedge): four English verbs of
   aim, read only where the founder's seed says one; a finding.
10. **2 of 2's read-back** (FR-6) hands the readers no summary and the card's sentence labelled as the next screen's,
    rather than nothing: the readers lose no evidence, and nothing is scored as drawn on 2 of 2 that is not.
11. **The window heading is held exactly to the mirror on a first pass** (`window_page_faults` with the typed fields):
    strict journeys assert it, the back-test records it as a finding.

## What the cycle runner should expect (the next paid cycle, the founder's word)

- **New stop names**: a walk refused past its retries on the gate fails at the PROBLEM calibration with *... FAILED --
  stopped by E7 (the segment | the hurt's kind dropped | a word the founder never gave | the routine, keel-cloud
  238 / 212) past the repair turn* or *stopped by E9 (the no-sayer names no word of the hurt, keel-cloud 238 FR-2 | ...)*;
  `backtest.json` `stop_rule`, `backtest.md` *stopped by E7 ...*, the record's gate line names the walk.
- **New findings** (never a stop): retried refusals carry `rule` / `refusal`; lock notes *E7 on CALIBRATION_QUESTIONS*,
  *E8 on CALIBRATION_QUESTIONS* (blame: *let*, *allowed*, *failed to*; *less than it could*, *more than it should*),
  *M8 on SOLUTION_MECHANISM* with `heard_again` (words, line, path); *the served gate asks what every one of them does
  in the segment* (`gate_in_the_segment`); *FAULT: Existing sacrifice: the served item says ...*; *Existing sacrifice:
  the Check's note ...* (as typed / the base); *the idea's reveal says a thing twice* and *the belief drops the
  founder's hedge*; on 2 of 2 a window heading that parts from the typed when.
- **The part-3 job on money-only studies**: a COMMERCIAL walk of Palus, Codyco, Veles, AirCaps or Taiga now starts ONE
  `RESPONDENT_QUESTIONS` job (part 3; 70 credits held, the questions WRITING until it lands) where it started none; the
  lock step's receipt expects one interactionId. Expanse's (a line code reads whole) starts none.
- The served Existing sacrifice items move (no neutral verb, the typed unit on B2B: *... per hotel did not get
  answered?*, *... per company was yield you gave up?* with the Check's note, *... per cluster sat idle?*); the
  cost-item DRIFT finding compares against the mirror with no clause, so a writer's clause served will read as drift
  beside it (as before 148).
- The record's review line cites *keel-cloud 232, 233, 235, 236, 237, 238, 239, 240, 241* and a gate line follows it.

## Open

1. **keel-cloud 238 and the founder's job** (judgement call 3): `newWord` counts `went_wrong`, the routine, the
   circumstance and the seed, never the founder's typed job -- the golden Lullaby's *work out* is refused as a word the
   founder never gave though the founder typed it. A keel-cloud question for the founder; no fixture moved here.
2. The cycle (paid, the founder's word): BUILD = keel-cloud `155eaca9` / keel-web `36d069ed`, *Why* naming 238-241 and
   183 against cycle 18 (`quality/cycles/20261108-7662026.md`); the switch as the founder orders it.
3. No keel-cloud defect filed from this spec: no walk ran.

## Read

- keel-cloud-docs `155eaca9`: `specs/238..241/tasks.md` (the owed sections), `dimension-cards.md`,
  `RespondentReview.CARDS_SHA256`, `WindowFrame.java`, `ScreenResultApplier.java` (`actThatHurts`,
  `wordTheFounderGave`, M8), `TheGateAsksTheActThatHurtsTest`, `PrevalenceEventIsAMomentTest`, `LossNotDone.java`,
  `LossClause.java`, `CommercialChain.java`, `EvidencePlan.java`, `RespondentQuestionsRules.java`,
  `VectorsController.sacrificeNote`, `ExistingSacrificeNamesTheThingTest`, the moved cost pins, `IdeaLines.java`,
  `IdeaName.named`, `VectorFixtures`, the three instruction files, `canon/designs/spoken-questions-guidelines.md` §23,
  the registry.
- keel-web `36d069ed`: `specs/183-the-window-question-names-the-moment/tasks.md`, `src/lib/contextReach.ts`,
  `src/components/calibration/CalibrationPage.tsx`, `tests/unit/window-names-the-moment-183.test.tsx`.
