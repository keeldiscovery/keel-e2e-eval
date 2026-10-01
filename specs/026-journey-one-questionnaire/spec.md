# Feature Specification: the live journey under one questionnaire — the review card stops asking for chips, and the questions are waited for where they are actually written

**Feature Branch**: `026-journey-one-questionnaire`

**Created**: 2026-10-01

**Status**: **Draft for implementation.** Nothing here spends anything. The one paid thing this
spec produces is a *command* — the founder's next live S-012 run — and it is written down in
*The next live run* below rather than typed by this pass.

**Input**: the designs and specs of record, read in full —

- keel-cloud [`canon/designs/one-occasion-once-design.md`](../../../keel-cloud/canon/designs/one-occasion-once-design.md)
  — **§1** (the one sentence), **§2** (the live form and its five anchors for two occasions),
  **§3.4** (option (c): one questionnaire, written by a call that sees all of it, and *what it
  changes about when the questionnaire exists*), **§4** (what the participant sees; sections by
  occasion; the minutes estimate and the correction that `minutes` is not on the participant page),
  **§5** (the data model: `AnchorRef`/`SelectionRef` lose the stage, `qualified()` goes, `Q7`
  becomes project-wide), **§6** (`occasion` and `Q8`), **§6A** (duplicate lines across stages:
  `earlier_lines`, `reads`, one control, one answer against two lines).
- keel-cloud [`canon/designs/assumptions-step-design.md`](../../../keel-cloud/canon/designs/assumptions-step-design.md)
  §6 and §9 — the `QUESTIONS` call, its Haiku tier, its cost and its measured ~18 s.
- keel-cloud [`specs/048-lines-then-questions/spec.md`](../../../keel-cloud/specs/048-lines-then-questions/spec.md)
  and its `tasks.md` Discovered — the `QUESTIONS` screen, `Overview.questionsState`,
  `GET /v2/projects/{id}/questionnaire`, `POST /v2/projects/{id}/questionnaire/retry`, the invite
  gate, and FR-003: **a stage is approved on its lines**.
- keel-cloud [`specs/049-one-occasion-once/spec.md`](../../../keel-cloud/specs/049-one-occasion-once/spec.md)
  and its `tasks.md` Discovered — sections by occasion, `earlier_lines`, `reads`, `Belief.readsBelief`,
  and the bare anchor and selection ids.
- keel-web [`specs/026-one-occasion/spec.md`](../../../keel-web/specs/026-one-occasion/spec.md) —
  FR-011 (*What they'll be asked first* **deleted**, not emptied), FR-012
  (`QUESTIONS_NOT_WRITTEN_YET`, once per card, never an empty pick list), FR-017/FR-018 (the invite
  gate is `Overview.questionsState`, read and not recomputed; the locked reason), FR-019 (the one
  retry control, in the side nav and nowhere else), FR-020 (the three readings of `strip__read`),
  FR-004 (the participant page draws *About N minutes* for the first time).
- keel-cloud `canon/openapi-v2.yaml` at this checkout — `Overview.questionsState`,
  `QuestionnaireState`, `QuestionnaireView`, `Questionnaire`, `Selection`, `Belief.selectionId`,
  `Belief.readsBelief`, `StageCard.questionnaire`, `GET /v2/projects/{id}/stages/{stage}`.
- keel-cloud `canon/journeys.md` **§1.2–§1.5** — the journey of record: the three cards and their
  two actions, *"They see them in full on the preview of what the person being interviewed actually
  receives"*, approval as the moment the questions stop being editable, People reachable only once
  every framed bet is approved, and the waiting list.
- keel-web `src/routes/founder/StageRoute.tsx`, `src/components/review/ReviewLine.tsx`,
  `src/components/SideNav.tsx`, `src/lib/translate.ts`, `src/routes/founder/PeopleRoute.tsx` — read
  at this checkout, because what a page object reads is markup and a spec that quoted only prose
  would be guessing at it.
- this repository at `master` `a7d1d72`: `evals/test_s012_journey_through_a_host.py` whole,
  `evals/preludes.py`, `harness/browser.py` (`ReviewCard`, `OpenedCard`, `People`, `Shell`,
  `ParticipantPage`), `harness/keel_host.py`, `harness/agent_host.py`, `harness/refusals.py`,
  `instructions/models.py`, `matrix/cells.toml`, `Makefile`, `AGENTS.md`, `README.md`, and
  `specs/025-one-occasion-marks/` as the shape this repeats.
- **the red run**: matrix hand dispatch **36862514753**, on staging **782a01a** — the first run on
  the new build — which failed in **under two minutes** at
  `evals/test_s012_journey_through_a_host.py:492`:
  `AssertionError: a PROBLEM line offers no pick list at all: ["Crying they couldn't read, recently", …]`.
- `.specify/memory/constitution.md` — still an unfilled template at `a7d1d72`, every principle
  `[PRINCIPLE_N_NAME]`. Recorded because a spec that claims to have been checked against a
  constitution should say when there is nothing to check against. `AGENTS.md` is this repository's
  governing document and is what this spec is written to.

## The one sentence

**The live journey stops asking a review card for pick lists it cannot have, waits for
`Overview.questionsState == READY` where the one questionnaire is actually written — after the last
framed stage is approved — and makes the pick-list assertion there instead, against the project's
one questionnaire and against the slice each approved card carries; People's unlock is read off the
same state rather than recomputed from the approvals.**

## Why this exists

Until keel-cloud spec 048 a stage **could not be approved without its own questionnaire**:
`ScreenResultApplier.confirmCommand` ran `frame → introduceRoles → introduceAssumptions → approve`
in one apply, and `introduceAssumptions` took a questionnaire. So *lines approved* and *questions
exist* were one event, and every review card a founder ever read had pick lists under its lines.
S-012 asserted that, correctly, for as long as it was true:

```python
assert all(line.get("chips") for line in lines), (
    f"a {stage} line offers no pick list at all: ...")
```

048 splits that one moment into two. `introduceAssumptions` takes beliefs, roles and rationales;
`writeQuestionnaire(Questionnaire)` is a separate command that **one `QUESTIONS` call** applies, and
that call runs when `Project.allFramedStagesApproved()` becomes true — which is **strictly after**
every review card is read. keel-web 026 FR-012 draws the only sane consequence: `ReviewLine` renders
`Chips` as `{selection ? <Chips …/> : null}`, and a card on which no line resolves a control says so
**once**, in `QUESTIONS_NOT_WRITTEN_YET`, instead of drawing three empty pick lists.

So the assertion at line 492 is now asserting that a screen shows something the product is designed
not to show it. Run 36862514753 is what that costs: a whole staging deploy, a whole host leg, two
model jobs, and a red verdict ninety seconds in on the *first* card of three.

**Nothing below deletes an assertion.** *Every line offers a pick list* is still the thing worth
knowing; it has moved to the one place where it is true and where it can be read from both ends —
the project's one questionnaire on the wire, and the slice each approved card carries on the screen.

## What this pass does not do

- It does not touch `evals/preludes.py::walk_stage` or the six scripted scenarios. They run against
  a scripted executor whose script `harness/corpus_script.py` already writes the 048 way (spec 025
  phase 8), and none of them asserts chips on a review card.
- It does not fix **D-6** below — `ReviewCard.asked_first()` reads a block keel-web 026 FR-011
  deleted, and `evals/test_s001_smoke.py`, `evals/corpus_scenario.py` and `harness/rubric.py`'s
  ORI-U4 still require it. That is a real, named, scored breakage and it is **S-001's and the
  rubric's**, not S-012's; it is recorded with its line numbers and left for its own spec rather
  than half-fixed here.
- It spends nothing. No `make eval-live`, no `make instruction-eval`, no browser against staging.

## Requirements

### The review card

- **FR-001** — the per-stage review assertion (`_read_the_lines`) MUST require, exactly as before,
  that the card rendered **lines**, that **every line is numbered**, and that at least one rule line
  **names a deal-breaker**. None of those three moved and none of them is weakened.
- **FR-002** — it MUST NOT require chips on that card. The reason MUST stand above the place the
  assertion stood, naming keel-cloud 048 (the questionnaire is the project's and is written after
  the last approval), keel-web 026 FR-012 (`ReviewLine` draws no empty `Chips`), and run
  36862514753.
- **FR-003** — chips on a review card MUST be **recorded**, never required and never refused. A
  `SOLUTION` or `COMMERCIAL` line may legitimately carry one before its own stage is approved: 049
  FR-013 writes the referent's `selectionId` onto every belief that `reads` an earlier stage's
  measurement, so a line reading `PROBLEM`'s line 3 owns a control the `PROBLEM` approval already
  wrote. Asserting the absence would fail exactly the run that proves 049 works.

### The questions land

- **FR-004** — after the **third** approval and **before** People, the journey MUST wait for the
  project's one questionnaire, by polling `GET /v2/projects/{id}/overview` for `questionsState`.
  `READY` ends the wait. The poll interval is 3 s — the same interval the *What this says* wait
  already uses — so the wire is asked about twenty times a minute's wait, not once.
- **FR-005** — the ceiling MUST be **420 s** on the three CLI doors and the Keel door's own
  `keels_ai_job_wait_s` (**660 s**) behind the Google door. 420 is keel-cloud's own `QUESTIONS`
  abandonment (PT300S) plus two minutes of queue, hand-off and poll slack; a Haiku 4.5 `QUESTIONS`
  job is estimated at ~18 s (assumptions-step-design §6.4) and measured at one to three minutes on
  a live host, so the ceiling is roughly three times the worst measurement rather than a guess.
  The Keel door's number is read off `AgentHost.keels_ai_job_wait_s`, exactly as the review-card and
  BRIEF waits already read it, and never written as an `if HOST == "keel"` beside this wait.
- **FR-006** — `FAILED` MUST be retried **exactly once**, through
  `POST /v2/projects/{id}/questionnaire/retry`, in a step of its own that records the 202's
  `interactionId`. A second `FAILED`, or a `FAILED` still standing at the deadline, MUST fail the
  run **with keel-cloud's own reason** — the `QUESTIONS` interaction's `refusal`, `detail`,
  `diagnostic` and job `error` — never with *"nothing happened within 420 s"*.
- **FR-007** — on the Keel door the wait MUST ask the wire whether the door is bolted on every
  poll, through the existing `_refuse_if_the_door_is_shut`, for spec 024 FR-010's reason: a
  `KEEL_AI_DISABLED` answer comes back before a socket is opened, and a run that sat out 660 s for
  it would be reporting the referee's patience instead of the product's sentence.
- **FR-008** — a timeout MUST name the **last state seen** (`NOT_STARTED`, `WRITING` or `FAILED`)
  and the `QUESTIONS` interaction's own status. `NOT_STARTED` at the deadline means the approval did
  not start a job at all, which is a different fault from one that ran and gave up, and the two must
  not read the same.

### What the questions have to be

- **FR-009** — `GET /v2/projects/{id}/questionnaire` MUST answer `state: "READY"` with **at least
  one anchor**, every anchor carrying a non-blank `id` and a non-blank `prompt`.
- **FR-010** — **every selection on it MUST offer a pick list.** This is FR-002's assertion, moved:
  an `OPTIONS` selection carries a non-empty `options`, a `BUCKETS` selection a non-empty `buckets`.
  The *words* are the model's and nothing asserts them (spec 016 FR-007); what is asserted is that a
  control a stranger will be shown offers something to pick.
- **FR-011** — **the ids are the project's.** Anchor ids MUST be unique across the whole
  questionnaire and selection ids MUST be unique across the whole questionnaire — `Q7` is
  project-wide since 048, where it used to be per stage. No anchor and no selection may carry a
  `stage` key: 049 reduced `AnchorRef`/`SelectionRef` to a bare id and deleted `qualified()`, and an
  id that still named a stage would mean the wire had not moved.
- **FR-012** — **each stage card MUST carry its slice.** For every stage,
  `GET /v2/projects/{id}/stages/{stage}` MUST answer a card whose every belief `selectionId`, where
  present, **resolves** to a selection on the project's one questionnaire, and whose own
  `questionnaire.anchors` are a subset, by id, of the project's. At least one belief across the
  three cards MUST resolve one — a questionnaire no line reads is a questionnaire written about
  nothing.
- **FR-013** — **`reads` MUST resolve.** Where a belief carries `readsBelief`, its `stage` MUST be
  one of the three and its `line` MUST be an integer that names a belief's own `number` on that
  stage's card. This is the founder-visible end of 049 §6A.5: *"measured with the problem's line
  3"* has to point at a row the founder can count to.
- **FR-014** — on the screen, the three approved cards MUST between them render at least one
  `strip__read` line — keel-web 026 FR-020's slot, which says `Asked: "…"`, *Same pick list as line
  N* or *Measured with the problem's line 3*. The **sentence** is never asserted (FR-007); its
  presence is what proves the slice reached the founder and not only the wire.

### People

- **FR-015** — the People unlock step MUST be a wait for **`questionsState == READY`**, not for the
  approvals alone. keel-web 026 FR-017 reads the same state (`gateOpen = questionsState === "READY"`)
  and `Project.invite` enforces the same gate (`rule: "questionnaire"`), so the referee reading the
  approvals would be the one party in the system computing it a fourth way.
- **FR-016** — the old reading is **kept, not replaced**: all three stages MUST still read
  `approved: true` on the overview at that moment. Both facts are asserted, in the same step,
  because *approved and still locked* and *unlocked while unapproved* are two different faults and a
  single assertion could not tell them apart.
- **FR-017** — when People is locked the step MUST record `Shell.people_locked_reason()`, so a
  failure carries keel-web's own sentence (*"Writing the questions for your lines. People opens when
  they land."* / *"We couldn't write the questions for your lines."*) rather than a boolean.

### The sweep

- **FR-018** — `_invite_one_live`'s comment claiming `minutes` is *"never on the participant's
  page"* MUST be corrected: keel-web 026 FR-004 renders `About N minutes` under the consent line for
  the first time. The **assertion** — exactly one *About N minutes* line in the **founder's
  preview**, with `N ≥ 10` — is untouched and still right: it reads the preview string, not the
  participant page.
- **FR-019** — the short journey's two sentences claiming it buys *"the lines and questions
  keel-cloud chained off"* the framing MUST be corrected, in `harness/agent_host.py::short_stops_at`
  and in the scenario's own note. Since 048 the assumptions job writes no questionnaire and the
  `QUESTIONS` job fires on the **approval**, which the short run deliberately never makes.
- **FR-020** — the end-of-run accounting step (*zero refusals, every job COMPLETED*) MUST say, in
  its comment, that a `QUESTIONS` retry shows up there as a failed job. It is not loosened: a
  journey whose questions failed once is a journey with a failed job in it, and the retry exists so
  the run reports *why, where it happened* and still produces the rest of the evidence before the
  accounting names it.
- **FR-021** — `harness/refusals.py` MUST gain a way to ask for the newest terminal failure on a
  **screen** rather than on a stage. `QUESTIONS` and `BRIEF` carry no stage, so `latest_failure`
  (which matches `row["stage"] == stage`) is structurally blind to them and would answer `None`
  about a wire that knows exactly what went wrong — `runs/DRIFT.md` #37's shape, one axis over.

### The bundle and the next run

- **FR-022** — the bundle name does **not** move. `runs/<stamp>-s012-journey-<host>[-short]` means
  what it meant; this spec changes what the full journey asserts, not which run it is, and a reader
  comparing today's bundle with last week's must not have to translate a name.
- **FR-023** — the bundle MUST record, in its `journey` block, that the full journey now waits for
  the one questionnaire, so a reader of a green bundle can tell a run that waited for `READY` from
  one taken before this spec.
- **FR-024** — the founder's next live run MUST be written down here, with its dispatch inputs, and
  nothing in this pass may type it.

## The next live run

**It costs model spend and it is the founder's to type.** S-012 is a live scenario: `AGENTS.md`'s
third named LLM place.

**The matrix hand dispatch** — the same shape as run 36862514753, which is the run this spec exists
to turn green:

| input | value | why |
|---|---|---|
| `set` | `per_change` | the one macOS Claude cell, whole (`matrix/cells.toml`'s `per_change`) |
| `cells` | `macos-latest-claude-py3.13` | the cell 36862514753 ran, so the two runs are one measurement |
| `scenarios` | `s012` | the journey alone, no corpus riders — the change is the journey's |
| `deploy` | `true` | staging must carry 048 **and** 049 and keel-web 026 |
| `wipe` | `true` | the run's founders are this run's |
| `stop_twin` | `false` | the founder keeps the twin up for manual testing (2026-09-29/30) |

**The same thing from a Mac**, against the twin, when the founder would rather watch it:

```sh
make up PROFILE=remote
make eval-live K=s012 HOST=claude LEGS=full PROFILE=remote ENTRY=03-lullaby PEOPLE=5
```

**The bundle**: `runs/<stamp>-s012-journey-claude/` — unchanged (FR-022).

**There is no `WHY` on this command, and that is not an oversight.** `WHY=` is
`instructions/why.py`'s gate and it belongs to `make instruction-eval` / `make instruction-screen`
alone — the run that scores keel-cloud's prose against the frozen corpus and whose five named
events (`instruction:`, `prompt:`, `contract:`, `new-model:`, `marks:`) decide whether a screen or a
full run is earned. **S-012 is gated by the matrix, not by `WHY`**: `matrix/cells.py` decides what a
qualifying change buys, and a hand dispatch is the founder deciding. Inventing a sixth `WHY` event
for the journey would be adding a gate to a place the design does not have one, so this spec names
the gate that does apply instead. **This change earns no instruction-eval run at all**: it moves no
instruction, no prompt, no contract, no model and no `MARKS_VERSION`, so the standing gate's run of
record `20261001T043420Z-instructions` still stands at `MARKS_VERSION` 8 and nothing here may spend
against it.

## Success criteria

- **SC-001** — `make unit` green at every commit on this branch; no test deleted.
- **SC-002** — no assertion that stood at `a7d1d72` is gone. Each one either stands where it stood,
  or stands somewhere else with the reason written above it.
- **SC-003** — the review-card step makes three assertions where it made four, and the fourth is
  findable from the comment that replaced it.
- **SC-004** — a reader of the new step can say, without opening keel-cloud, what state the wait is
  waiting for, how long it waits, what it does when it fails, and what it asserts when it lands.
- **SC-005** — nothing in this pass spends a model call.
