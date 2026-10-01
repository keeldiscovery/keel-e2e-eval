# Tasks: the live journey under one questionnaire

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `026-journey-one-questionnaire`

`make unit`: **green at every commit on this branch.** Baseline at `a7d1d72`, before a line was
written: **1,217 passed** (Discovered **D-0**).

**Tests first, within each phase.** Each phase's own tests are written before the code that turns
them green and land in the same commit (spec 025 D11's rule, kept). **No test is deleted**, and no
assertion is removed — each one either stands where it stood or stands somewhere else with the
reason above it.

**Nothing below spends a model call.** The only paid thing this branch produces is the command in
spec.md's *The next live run*, and it is the founder's to type.

## Phase 1 — read before writing anything

- [X] **T001** keel-cloud `canon/designs/one-occasion-once-design.md` §1–§6A — the rule, the three
      options and why (c), the participant's page, the data model, `Q8`, the cross-stage half.
- [X] **T002** keel-cloud `specs/048-lines-then-questions/` and `specs/049-one-occasion-once/`
      (spec, tasks, Discovered) — the `QUESTIONS` screen, `questionsState`, the retry endpoint, the
      invite gate, `earlier_lines`, `reads`, `readsBelief`, the bare ids.
- [X] **T003** keel-web `specs/026-one-occasion/spec.md` **and keel-web's own markup** —
      `StageRoute.tsx`, `ReviewLine.tsx`, `SideNav.tsx`, `translate.ts`, `PeopleRoute.tsx`. The
      markup is what a page object reads, and reading only the prose is how a referee writes an
      assertion against a screen that does not exist (**D-3**, **D-4**).
- [X] **T004** this repository's own blast radius: `instructions/models.py::SCREEN_TO_CLASS`
      (already carries `QUESTIONS` — spec 025 phase 6, so the tail's model-routing assertion covers
      the new job and **nothing here touches it**), `harness/refusals.py` (stage-keyed — **D-5**),
      `harness/browser.py`'s `ReviewCard`/`OpenedCard`/`People`/`Shell`/`ParticipantPage`,
      `evals/preludes.py::walk_stage` (asserts no chips — out of scope and said so), `matrix/`.
- [X] **T005** keel-cloud `canon/journeys.md` §1.2–§1.5 — the journey of record.
- [X] **T006** the red run: matrix hand dispatch **36862514753**, staging **782a01a**, failing at
      `evals/test_s012_journey_through_a_host.py:492` in under two minutes.

## Phase 2 — the review card asks for what a review card can have (FR-001 … FR-003)

- [X] **T010** `tests/test_journey_one_questionnaire.py` (new): the chips assertion is gone from
      `_read_the_lines`; the three that remain are still there verbatim; the comment that replaced it
      names 048, keel-web 026 FR-012 and run 36862514753; `_read_the_lines` still records the chip
      counts so the bundle keeps the number it stopped asserting.
- [X] **T011** `evals/test_s012_journey_through_a_host.py::_read_the_lines`: delete nothing, assert
      three of the four, and write the reason where the fourth stood, pointing at the step FR-010
      moves it to.

## Phase 3 — the questions land (FR-004 … FR-014)

- [X] **T012** `harness/refusals.py`: `latest_failure_on_screen(get_json, project_id, screen)` —
      the newest terminal failure on a **screen**, for the two screens that carry no stage
      (`QUESTIONS`, `BRIEF`). `latest_failure` keeps its exact behaviour and both read one private
      helper, so the two readings of *terminal* cannot drift (**D-5**).
- [X] **T013** `tests/test_journey_one_questionnaire.py`: the new reader, against hand-built rows —
      a `QUESTIONS` row with a null `stage` is found by screen and **not** found by
      `latest_failure` at any stage, which is the blindness the function exists to end.
- [X] **T014** `evals/test_s012_journey_through_a_host.py`: `QUESTIONS_WAIT_S`, the module constant,
      read off `AgentHost.keels_ai_job_wait_s` on the Keel door and 420 s elsewhere, with the
      arithmetic written down (PT300S + two minutes).
- [X] **T015** `_the_questions_land(...)`: the poll, the one retry, the failure sentence, and the
      four assertions (the wire's questionnaire; the pick lists; the ids; the per-stage slice and its
      `readsBelief`), plus the screen read through `OpenedCard.strips()`.
- [X] **T016** `tests/test_journey_one_questionnaire.py`: the step is called once, between the stage
      loop and People, on the full journey only; the ceiling is read off the host object and not
      branched on by name; the retry is sent to the right path and sent once.
- [X] **T017** `tests/test_review_card_chips_markup.py` (new): keel-web's real `ReviewLine` markup
      with and without a selection, and `ApprovedCard`'s real `.strip__read`, through `ReviewCard`
      and `OpenedCard`. Proves `lines()[i]["chips"] == []` on a card with no questionnaire and that
      `strips()[i]["read_line"]` is already the slice's founder-facing end.

## Phase 4 — People unlocks on the state the product unlocks on (FR-015 … FR-017)

- [ ] **T018** `tests/test_journey_one_questionnaire.py`: the People step names `questionsState`,
      still asserts all three approvals, and records `people_locked_reason()`.
- [ ] **T019** `evals/test_s012_journey_through_a_host.py`: the People step, rewritten to assert
      both facts in one step with keel-web's own sentence in the evidence.

## Phase 5 — the sweep (FR-018 … FR-021)

- [ ] **T020** `_invite_one_live`'s minutes comment — keel-web 026 FR-004 puts *About N minutes* on
      the participant page for the first time. The **assertion** does not move (**D-7**).
- [ ] **T021** `harness/agent_host.py::short_stops_at` and the scenario's own short-journey note:
      the short run buys the framing and its lines, **not** its questions (**D-8**).
- [ ] **T022** the end-of-run accounting step's comment: a `QUESTIONS` retry shows up there, and why
      that is right.
- [ ] **T023** `harness/browser.py::ReviewCard.asked_first` — a dated note naming keel-web 026
      FR-011, which deleted the block it reads. **Not fixed here** (**D-6**).
- [ ] **T024** `tests/test_journey_through_a_host.py`: the short journey's own sentence, asserted
      against the new wording.

## Phase 6 — the documents, and the run the founder types (FR-022 … FR-024)

- [ ] **T025** the bundle's `journey` block says the full journey waits for the one questionnaire.
- [ ] **T026** `README.md`'s S-012 section and `AGENTS.md`'s third named place: one sentence each.
- [ ] **T027** spec.md's *The next live run* — the dispatch inputs, the Mac command, the bundle
      name, and why there is no `WHY` on it. **Written, never typed.**

## Discovered

A ledger of what the work found that the documents did not say, in the order it was found. Each
entry names where it was found and what was done about it.

- **D-0 — the baseline.** `make unit` at `a7d1d72`, before a line was written: **1,217 passed in
  142.75s**. Recorded so every later number on this branch has something to be compared with.

- **D-1 — `occasion` is deliberately not on the questionnaire wire, so it cannot be asserted
  there.** The brief for this spec asked for *"≥ 1 anchor with an occasion"*. keel-cloud
  `canon/openapi-v2.yaml`'s `QuestionnaireView` says the opposite in as many words: *"`occasion` is
  deliberately not here and is the only anchor field that is not — it is authoring metadata, stored
  on the anchor, compared by `Q8`, never on `Form` and never shown"* (design §6). What a participant
  sees of the occasion is the **section title** `FormComposer` renders it as, and S-012 already
  asserts exactly that, in its §2.1a step: one section title per anchor block, and none of the three
  titles a *stage* used to draw (spec 025 FR-021). **So the occasion assertion is not added and the
  one that already exists is named as the place it lives.** Asserting an absent field would have
  gone red on a correct product.

- **D-2 — `reads` is not on that wire either; what resolves is `selectionId` and `readsBelief`.**
  `reads` is the model's own `QUESTIONS` answer — 0-based indices into the context's
  `measurements[]` — which keel-cloud resolves server-side, writing the derived `selectionId` onto
  every belief that reads it (049 FR-013) and `readsBelief` beside it. Nothing named `reads` ever
  reaches a founder. **So *"selections whose `reads` resolve"* is asserted as the two things that
  are readable**: every `selectionId` a stage card names resolves to a selection on the project's one
  questionnaire (FR-012), and every `readsBelief` names one of the three stages and an integer
  `line` that is some belief's own `number` on that stage's card (FR-013).

- **D-3 — the chips are not on the approved card either, so the moved assertion could not simply
  move to the other card.** The brief said *"asserts the stage cards carry their slice of the one
  questionnaire **with chips**"*. Read in keel-web: `Chips` is rendered by `ReviewLine` and
  `ReviewLine` is used by `DraftReview` alone (`StageRoute.tsx:372,384`). The **approved** card
  (`StageRoute.tsx:570` onward) draws `div.strip` rows whose questionnaire slot is
  `span.strip__read` — *"Asked: …"*, *"Same pick list as line 4"*, *"Measured with the problem's
  line 3"* (keel-web 026 FR-020). And the review card is drawn **before** approval, which is before
  the questionnaire exists. **So in the journey of record chips render on no card at all**, and the
  assertion lands in two places instead: the pick lists on the wire (FR-010), and `strip__read` on
  the three approved cards (FR-014). `OpenedCard.strips()` already reads `read_line` off
  `.strip__read` — written for spec 030 and load-bearing for the first time here.

- **D-4 — …except on a `SOLUTION` or `COMMERCIAL` review card, where a chip is 049 working.** A
  `QUESTIONS` job runs after **every** approval, not only the third: `allFramedStagesApproved()` is
  true once the one framed stage is approved, because an unframed stage is skipped and not waited on
  (journeys §1.2). So by the time the `SOLUTION` card is reviewed, `PROBLEM`'s selections exist — and
  049 FR-013 writes the referent's `selectionId` onto a belief that `reads` an earlier stage's
  measurement. Such a line renders chips on a card whose own stage is unapproved. **So the absence
  of chips is recorded and never asserted** (FR-003): asserting it would fail precisely the run that
  proves the cross-stage half works.

- **D-5 — `harness/refusals.py` is stage-keyed and `QUESTIONS` has no stage.** `latest_failure`
  filters `row.get("stage") == stage`, and `InferenceScreen.QUESTIONS` carries none (nor does
  `BRIEF`). Asked about a failed `QUESTIONS` job it answers `None` — *"nothing happened"* about a
  wire that knows exactly what did, which is `runs/DRIFT.md` #37's shape one axis over. Answered with
  `latest_failure_on_screen`, sharing one private *newest terminal row* helper with `latest_failure`
  so the two readings of *terminal* cannot drift (FR-021).

- **D-6 — keel-web 026 FR-011 deleted the block `ReviewCard.asked_first()` reads, and three places
  in this repository still require it. Not fixed here, named here.** The *What they'll be asked
  first* `<dl className="qa">` is gone from `StageRoute.tsx` (with `REVIEW_ASKED_FIRST_HEADING`,
  `REVIEW_ONE_STORY_TERM`, `REVIEW_THEN_TERM`, `reviewThenLine` and `REVIEW_ASKED_FIRST_HINT`),
  because a stage no longer owns a questionnaire and the block had nothing to draw. So
  `ReviewCard.asked_first()` now returns `""` for ever, and:
  - `evals/test_s001_smoke.py:664-667` asserts it non-empty and containing *story* and *pick*;
  - `evals/corpus_scenario.py:336-340` asserts the same, for all six scripted scenarios;
  - `harness/rubric.py:207-220`'s **ORI-U4** scores it, and `tests/test_policy_v8.py:144`
    seeds its absence as a failure.

  **S-012 asserts none of this** — it only captures the block as evidence — so this spec's own
  scenario is unaffected. Fixing it means deciding what ORI-U4 measures now that the founder reads
  the questions on the People page instead (journeys §1.2: *"they see them in full on the preview of
  what the person being interviewed actually receives"*; keel-web 026 FR-014's *Read the questions*),
  which is a rubric question and belongs to its own spec. `ReviewCard.asked_first`'s docstring now
  carries a dated note so the next reader finds this entry instead of the empty string.

- **D-7 — `minutes` is on the participant page now, and the scenario's comment said it never
  was.** `_invite_one_live` carried *"`minutes` is rendered in exactly one place in the whole
  product — `SendPopup`'s *About N minutes* line, never on the participant's page
  (`one-occasion-once-design.md` §4)"*. That was true when it was written and §4 named it as a drift
  — *"`journeys.md` §2.1's mock shows *About 15 minutes* on the stranger's first screen and the page
  does not show it. That is a separate drift, named here and not fixed here."* keel-web **026
  FR-004 fixed it**: `ParticipantRoute.tsx` renders `PARTICIPANT_MINUTES(form.minutes)` under the
  consent line. **The comment is corrected; the assertion is not touched** — it counts *About N
  minutes* lines in the founder's **preview** string, which is still exactly one, and `N ≥ 10` is
  still `FormComposer`'s floor.

- **D-8 — the short journey does not buy the questions, and two sentences said it did.**
  `harness/agent_host.py::short_stops_at` and the scenario's own `spec 021` note both describe the
  short Keel's-AI run as buying *"the problem framed and the lines **and questions** keel-cloud
  chained off it (PROBLEM_FRAME + PROBLEM_ASSUMPTIONS)"*. Since 048 the assumptions job writes no
  questionnaire, and the `QUESTIONS` job fires on the **approval** — which `_read_the_lines`
  deliberately never makes, since it returns the card un-approved. Both sentences corrected; the
  screens named in the same breath (`PROBLEM_FRAME + PROBLEM_ASSUMPTIONS`) were already right and
  are what made the error visible.

- **D-9 — a `QUESTIONS` retry still goes red at the tail, and that is the design.** The retry
  (FR-006) does not remove the first attempt's failed interaction from
  `GET /v2/inference-interactions`, so the *zero refusals, every job COMPLETED* step at the end of
  leg two will name it. Deliberate, and the same posture `_land_the_card`'s benign follow-ups
  already take: the journey goes on so that People, the readings and the brief are all in the bundle
  as evidence, and the accounting then says what failed. The retry's value is that the failure is
  reported **where it happened, with keel-cloud's own reason**, instead of as a 420-second silence.
  The step's comment now says so.

- **D-11 — the comment that replaced the assertion *is* the assertion, as far as a grep is
  concerned.** The first run of `tests/test_journey_one_questionnaire.py` went red on its own first
  test: the long comment above the step quotes `assert all(line.get("chips") for line in lines)` so
  a reader can see what left, and a source test that greps the raw function body reads that
  quotation as the assertion still standing. Answered with `_code_of`, which drops `#` lines before
  the check -- and the test now asserts **both** halves: the assertion is gone from the code, and
  the quotation is still in the comment. A rule this repository was going to need again: every
  moved assertion on this branch leaves its own text behind on purpose.

- **D-12 — a fixture whose point is an absent node pays Playwright's thirty-second auto-wait for
  every one of them.** `tests/test_review_card_chips_markup.py` ran for **over eight minutes** and
  had to be killed: the page objects read optional nodes through `_safe_text` (a belief with no
  `p.you-said`, a strip with no `.strip__read`), `_safe_text` swallows the timeout, and the timeout
  is 30 s each by default. *Absent* is exactly what these fixtures are about, so the cost is
  structural rather than incidental. Answered with one named constant,
  `_ABSENT_IS_THE_POINT_MS = 250`, on the page: thirty-three seconds became under ten, and a quarter
  of a second is far longer than a `set_content` page ever needs. Worth the ledger entry because the
  next markup test written here will meet it on its first run.

- **D-13 — a stale `questionsState` still reads `FAILED` for a second or two after the retry is
  accepted, so *retry once* cannot be written as a flag.** `POST …/questionnaire/retry` answers 202
  with an `interactionId` and the new job starts asynchronously; the very next poll can still read
  `FAILED` from the attempt that was just retried. A naive `if retried: break` would therefore
  report *the retry failed too* without the retry having run at all. The wait compares the newest
  `QUESTIONS` failure's own `interaction_id` against the one it retried, and treats `FAILED` as
  terminal only when it belongs to a **different** attempt.

- **D-10 — `instructions/models.py` needed nothing.** `SCREEN_TO_CLASS` has carried
  `"QUESTIONS": "questions"` since spec 025 phase 6, and `REPORTED_CLASSES` carries `questions`, so
  the tail's *every job requested the model the cloud's table names for its class* assertion already
  covers the journey's new third job class on a routing runtime. Checked at T004 and recorded, so
  the next reader does not check it twice.
