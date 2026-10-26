# Tasks 071 -- Study scopes in the harness: ALL on every seed, two short journeys, the exporter's scope

Branch `071-study-scopes` off master `ec1293f` (worktree `wt/eval-071`). The product halves, read only: keel-cloud-docs
master `867b6465` (spec 133, contract 38: `scope` on the create request, `StudyScope`, `GateItem.counts`,
`Reveal.problem` / `Idea.problem`, `StandingsView.scope / question / ship / gateFact`, out-of-scope vectors absent) and
keel-web master `82a92f3` (specs 109 -- the choose screen, the badge, the corridor per scope, the four Overviews --, 110
and 111, the home). The design of record: keel-cloud-docs `canon/designs/study-scopes-design-2026-10-25.md` §5, §9,
§11, §15. The stack built from those checkouts (four symlinks beside the worktree, so `stack.toml`'s `../` paths name
the main checkouts; nothing written there), keel-runtime 0.8.0 bundled in keel-connect-skill `c677950`.

One commit per FR, in order, each gated on `.venv/bin/python -m pytest tests -q` green. No paid command, no key.

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `ec1293f` (before any change) | 3,175 | **6** | 53 |
| FR-1 `548040d` | 3,197 | 0 | 53 |
| FR-2 `289ba23` | 3,230 | 0 | 53 |
| FR-3 `4427e10` | 3,251 | 0 | 53 |
| FR-4 `911a287` | 3,257 | 0 | 53 |
| FR-5 `3b8b7a4` | 3,263 | 0 | 53 |
| FR-6 (this commit) | 3,265 | 0 | 53 |

Master's six reds were the siblings' moves, not this spec's (D-01).

## FR-1 -- ALL on every seed -- `548040d`

- [x] T001 `harness/browser.ScopeChoose` (keel-web 109's *For keel-e2e-eval* selectors: `[data-testid=scope-choose]`,
  `.scope-opt[data-pick]`, `scope-more`, `scope-plan[data-scope]` with its badge, pills, kind and length,
  `scope-continue`): `read()` and `choose(scope)` -- a card picked for a scope the web offers, nothing picked for ALL.
- [x] T002 `ScopeRewrite`: a one-shot `page.route` on `/v2/projects` alone (`is_projects_url`) that carries the next
  create request with `scope: ALL` (`with_scope`) and lets every other request fall back; `seen = {web, sent}`.
- [x] T003 `Landing.name_project(name, scope="ALL", seen=)` answers the choose screen between the name and the market;
  `preludes.create_project(..., scope=)`; `Journey.scope` (ALL) sent by `leg_project` and held by `_hold_the_scope`
  (the overview's and the list row's `scope`; under ALL the screen opened on the problem card, the page sent PROBLEM and
  the request went as ALL). S-010's and S-002's wire creates send `scope: ALL`.
- [x] T004 Unit `tests/test_study_scopes.py` (16): the request's body, the refusals, the five scopes, the rewrite's one
  shot, the held scope (and its three faults), every golden journey asking for ALL.
- [x] T005 Master's six reds put right (D-01). S-014 green on the local stack with FR-1 alone
  (`runs/20261026T025454Z-s014-green`).

## FR-2 -- S-015, the problem study -- `289ba23`

- [x] T010 `instructions/corpus.Entry.scope` (ALL; never read from a file -- REVISION stays 16).
- [x] T011 `harness/vectors_script`: `SCOPE_VECTORS`, `scope_of`, `scope_vectors`, `serves_gate`, `gate_counts`,
  `serves_part` (under ALL always True: `plan_keys` decides every part as it always has); `plan_keys` returns nothing
  for a part the scope does not serve and the gate alone where part 1 is the anchor; `calibration_jobs` over the
  scope's vectors; `respondent_jobs` none without a gate; `generate` writes the mechanism only where the idea card is,
  the faces only with the solution; `read_back(window=)` leaves out the window's clause as keel-cloud `ReadBack` does;
  no pilot opt-in in the problem study.
- [x] T012 `harness/vectors_screens`: `Corridor.context` with no window, `confirm_seed(vector, scope)` (the problem card
  goes on to the solution's seed where the problem is not calibrated), `idea_check(next_url=)`, `word_pilot_and_lock(
  pilot=)` (*1 of 2*, *2 of 2* in the problem study) and its 15 s wait for the button (a lock never offered returns
  `disabled`), `stage_exit` / `calibrates` / `step_of` (keel-web 109's `stageExitLabel`, `corridorStepsOf`),
  `Answers.scoped_overview`, the thank-you's pilot box read (`pilot_box`).
- [x] T013 `evals/corpus_scenario`: the legs read `j.scope` -- the context's window, the problem card's next step, the
  stage's exit label, step 5's counters (`before_counters`), the RESPONDENT_QUESTIONS count and the lock's lists over
  the scope's vectors, the whole study's report reads (`report_sheet`, `_too_few`, `_too_few_answered`) left to ALL;
  `leg_standings` split into `_await_standings` and `hold_standings`; `_drift_95_lock` (DRIFT #95).
- [x] T014 `evals/scope_journey.py`: `problem_entry` (01-countly, scope PROBLEM, `expected` its own problem standings and
  verdict), `record_of`, `leg_scoped_report` (the standings -- held to Countly's on the problem study -- the Overview as
  drawn, `scope-record.json`, `scope-marks.json`), `run`. `evals/test_s015_problem_only.py`.
- [x] T015 `evals/scope_marks.py` (SC1-SC7, `SCOPE_MARKS_VERSION` 1): the choose screen, the corridor's counts, the links,
  the interview, the standings, the decision by keel-cloud 133 FR-7's rule (`decision_by_rule`), the Overview.
- [x] T016 Unit: the golden walk unchanged under ALL, the problem seed, its expected walk, the decision rule, the marks on
  a stubbed walk and each mark's own fault; the scenario set is fifteen.

## FR-3 -- S-016, money alone -- `4427e10`

- [x] T020 `scope_journey.money_entry`: 01-countly on a B2B persona (`OWNER_ROLE`, title *Restaurant owner*), scope
  COMMERCIAL; Purchase friction added to the founder's calibration (`FRICTION`), Buyer and payer's belief in the owner's
  words; the ten owners (Countly's gate-yes people) on the decision-maker's link with their money picks (a time-only
  cost at revision 5's nominal $20 an hour) and two added answers each (`OWNER_PICKS`); `expected` empty (the verdict by
  the rule).
- [x] T021 `leg_idea_card` (*Your idea*, step 3 of 5: the solution's seed, its card, the idea card named and saved, on to
  who decides); `walk`'s money branch; `leg_persona` counts one respondent type on B2B money alone
  (`vs.primary_link`); `_hold_the_screens` holds the decision-maker's idea screen's `reveal-problem` line to the served
  `Idea.problem` on every decision-maker's link (ALL included); `problem_sentence` mirrors keel-cloud's
  `ProblemSentence`, and `scope_marks.sentence_faults` the spoken rules (one sentence, 6-20 words, no M5 word).
- [x] T022 DRIFT #96 (`_drift_96_window`, `DRIFT_96_WINDOW`) and #97 (`vs.chained_out_of_scope`, the two chained slices in
  `calibration_jobs`, `scope_journey.drift_97`); `_themes_on_return` bounded by the boxes the view serves.
  `evals/test_s016_money_only.py`; the scenario set is sixteen.
- [x] T023 Unit: the money seed, its expected walk, the problem-sentence mirror, the spoken rules, the money marks.

## FR-4 -- the back-test door takes `--scope` -- `911a287`

- [x] T030 `evals/backtest`: `SCOPE_VAR` (`KEEL_BACKTEST_SCOPE`), `SCOPES`, `scope()` (ALL unsaid; refused by name),
  `door_refusal` refusing an unknown scope on either door; `Backtest.scope`; `backtest.json`'s `scope`;
  `backtest.md` names it beside the stack where it is not ALL; `summary` reads it (ALL on a record from before);
  `rerun_row`'s Door cell `host · PROBLEM` where not ALL.
- [x] T031 `evals/run_backtest.py` hands `scope=backtest.scope()` to both doors; `Makefile` `backtest` passes `SCOPE=`;
  `scripts/backtest-host.sh --scope <scope>` / `--scope=` (refused by name before any `make`), passed on as `SCOPE=`.
- [x] T032 `corpus_scenario.run` walks a non-ALL back-test as a study of that scope (`scope_journey.walk`, `strict=False`,
  the marks as findings) and the whole study's legs exactly as before under ALL (one indent level in).
  `scope_journey.walk` and `scope_marks` cover the two solution studies (the gate's fact line, the Pilot tile alone or
  both, two cards) -- for a back-test under them; no journey walks them (judgement call 9).
- [x] T033 Unit: the scope's default and refusals, both doors' calls, the record, the markdown and the register row, the
  host runner's flag (a stubbed `make`).

## FR-5 -- the gallery export carries `scope` -- `3b8b7a4`

- [x] T040 `evals/gallery.prepare`: `scope` on every index row (beside `b2b`), the run's `backtest.json`'s, ALL where it
  carries none -- the fourteen; `attribution_reasons` refuses any other value. The manifest is unchanged.
- [x] T041 Unit `tests/test_gallery.py`: the row's keys, each of the five carried, an unknown scope refused (nothing
  written).

## FR-6 -- nothing else moves -- this commit

- [x] T050 `MARKS_VERSION` 20 and corpus `REVISION` 16 pinned (`test_marks_and_revision_do_not_move`); no corpus, registry,
  fixture or golden number moved. Under ALL the scripts of the seven golden entries, and for all 35 entries in keel-cloud's
  canon (the seven and the 28 back-test files) the people, founder inputs, read-back, calibration jobs, part-1 jobs and
  plan keys, are **byte-identical** to master's (`harness/vectors_script` of `ec1293f` and of this tree, dumped and
  compared out of tree).
- [x] T051 Two journey fixes the final runs found (D-04, D-05): the decision-maker's idea passage now opens with the
  problem's sentence under ALL as well (keel-cloud 133 T018 / judgement call 6 -- `interviewer_fake.solution_opening`,
  `interviewer_leg._framing_words`); step 5's counters kept in `Journey.changed`, not `j.screens` (S-007's page sweep
  reads every screen's text).
- [x] T052 AGENTS.md: the scenario set is sixteen, the study-scopes paragraph. DRIFT #95-#97 written. This file.

## The journeys (local stack, keel-cloud-docs `867b6465` + keel-web `82a92f3`, the scripted executor)

The stack was idle (`docker ps`: only an unrelated Testcontainers postgres on a random port); booted with `make up`,
the six journeys run one at a time with `make eval K=...`, torn down with `make down`. Runs of record (the final code:
this commit's tree before tasks.md, AGENTS.md and the DRIFT entries' run ids were written -- `versions.json` reads
`3b8b7a4`, dirty):

| Journey | Run | Result |
|---|---|---|
| S-006 | `runs/20261026T041505Z-s006-paidly` | **passed** (322 s) |
| S-007 | `runs/20261026T042028Z-s007-mulchrun` | **passed** (134 s) |
| S-005 | `runs/20261026T042243Z-s005-countly` | **passed** (292 s) |
| S-014 | `runs/20261026T042736Z-s014-green` | **passed** (135 s) |
| S-015 | `runs/20261026T042951Z-s015-problem-only` | **passed** (102 s), SC1-SC7 7 of 7 |
| S-016 | `runs/20261026T043134Z-s016-money-only` | **passed** (85 s), SC1-SC7 7 of 7 |

The first full pass on the FR-5 tree (`20261026T035542Z-s005-countly` passed, `...T040046Z-s006-paidly` failed on the
decision-maker's idea passage (D-04), `...T040338Z-s007-mulchrun` failed on the page sweep (D-05),
`...T040553Z-s014-green`, `...T040810Z-s015-problem-only` and `...T040952Z-s016-money-only` passed) is what T051 put
right. What the two new journeys read: S-015 -- Countly's four problem standings held, the verdict *Not yet* (Current
solution split them, 5 of 8), the Overview *Should you build it?*, one card, one piece, no tiles, tabs Overview and
Insights, no pilot box on any thank-you. S-016 -- the ten owners' six money lines all holding up on 10, *Build*, *Will
they pay?*, both tiles, the Pilot tab, the problem sentence *"Independent restaurant managers lose time whenever a
delivery does not match its invoice."* served and drawn on every owner's idea screen.

## Judgement calls

1. **ALL is carried, not chosen.** The web never offers ALL, so the harness walks the choose screen as it opens (the
   problem card, keel-web 109 judgement call 1) and rewrites the one create request's `scope` to ALL on the way out --
   the spec's *the walk sends `scope` in the create request as the web will*, with the harness's own value. The screen
   is still walked (and the request recorded: `{web: PROBLEM, sent: ALL}`) rather than the create done on the wire.
2. **The seeds derive, they are not written.** S-015 is 01-countly with `scope: PROBLEM` and nothing else; S-016 adds the
   B2B persona and the two B2B-only money rows a money-alone study on that persona needs (`OWNER_PICKS`, `FRICTION`),
   in the shapes 05-paidly records. The canon file is read and hashed as on every journey and never edited.
3. **S-015 holds Countly's own problem numbers; S-016 holds the rule.** The problem study asks Countly's people what the
   whole study asks them in part 1, gate counted, so its four standings and its verdict are the corpus's; money alone's
   owners are new answers on a new link, so no golden numbers are claimed -- the decision is held to 133 FR-7's rule
   over the served verdicts (SC6), every line called with its n on the wire.
4. **Kickers are the scope's.** The corridor's *Step k of n* is held to the scope's step count, case set aside (the
   capitals are CSS); the decision-maker's link keeps *The buying decision · k of 6* (133's *Part 1 of 1* is the
   person's link).
5. **The problem's sentence is mirrored and held strict.** `problem_sentence` cuts the problem card's statement as
   `ProblemSentence` does; on S-016 the served sentence equals it and passes the spoken rules (FR-3's *the harness's
   spoken mirrors apply to the reveal's sentence*). The decision-maker's idea screen is held to draw the served
   `Idea.problem` verbatim on every journey (ALL's decision-makers are served it too since 133).
6. **The marks are a journey ruler.** SC1-SC7 are `evals/scope_marks.py`'s, versioned apart (`SCOPE_MARKS_VERSION` 1) as
   the contacts, guide, interviewer and feedback marks are; `MARKS_VERSION` stays 20.
7. **THEMES on return are bounded by the boxes served.** keel-cloud 118 groups a held line's dissent box too; on S-016
   every money line holds and two carry boxes, and one regrouped when the founder came back -- the bound
   `len(failing)` would refuse that, so it is one a box the view serves (failing dimensions with them).
8. **The register's *stack column* is its Door column.** The register (`judgements/README.md`) has no Stack column; the
   Door column is where a row names the stack a run walked (KEEL / host), so a scoped run reads `host · PROBLEM` there;
   ALL rows are unchanged.
9. **A back-test under a scope walks the scoped legs, non-strict.** `--scope` is not only recorded: the entry is walked
   as that study (`scope_journey.walk`), the marks becoming findings as everything on a back-test does. The solution
   studies' branches (the solution's seed and calibration, the gate's fact line) are written from keel-web 109 and
   keel-cloud 133 but walked by no journey here; their first live walk is a back-test's.
10. **Product disagreements are stepped round by name, never fixed.** DRIFT #95 on the wire with the button's own body;
    #96 by holding the sentence over the window the page sent; #97 by scripting the jobs the cloud chains. Each step
    fails once the product is put right, and says what to drop.

## Discovered

- D-01 Master `ec1293f` was red on six unit tests the siblings moved: the gallery map's fourteen entries (ad56882 added
  14-21 and left four tests pinned at six -- the list, the clusters, the run count, and the keywords' case, which the
  export lower-cases; Lemma's YC page is `/companies/uselemma`; the eight carry no `statusToday` yet), keel-web
  110 / 111's guide clips (`home-intro`, `sample-question-solution` / `-money`, `report-read-<scope>`), and keel-web
  109's *1 question* heading (`ai_intro_heading`). Pinned to what they serve now, in FR-1's commit.
- D-02 The worktree's `stack.toml` paths are `../keel-cloud-docs` etc.; four symlinks in `wt/` name the main checkouts
  (outside every repository; nothing written to a sibling -- keel-web's only untracked entry is its own `.idea/`).
- D-03 DRIFT #95 / #96 / #97 (`runs/DRIFT.md`): keel-cloud's `PlanView.complete` is not scoped (both new journeys); keel-web
  sends the hidden recall window on money alone; keel-cloud's `ScreenChain` chains out-of-scope calibrations.
- D-04 keel-cloud 133 changed one served line under ALL, as its contract says: the decision-maker's SOLUTION passage now
  opens with `Idea.problem` before *Now the idea.* (S-006's interviewer leg failed on the stored clip's start until the
  expectation followed). Not a drift.
- D-05 S-007's page sweep reads every `j.screens` value's text; the step-5 counters list FR-2 put there drew none. Moved
  to `Journey.changed`.

## Left open

- The three DRIFTs' fixes are the products' (#95 keel-cloud, #96 keel-web, #97 keel-cloud); the harness's step-rounds
  name what to drop when each lands.
- No journey walks the solution or solution + money studies; `scope_journey.walk` and SC1-SC7 are ready for them (a
  seed and a test file each).
- A back-test under `--scope` has not been run (the paid commands are the founder's); its walk is unit-tested only.
