# Plan: the live journey under one questionnaire

**Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md) | **Branch**: `026-journey-one-questionnaire`

## 1. What moves, and what does not

One scenario file, three harness files, three documents. Nothing in `instructions/` moves:
`SCREEN_TO_CLASS` already carries `"QUESTIONS": "questions"` (spec 025 phase 6), so the journey's
new third job class is already covered by the model-routing assertion at the tail of the run and
this pass touches none of it — **checked, not assumed** (T004).

| File | What moves |
|---|---|
| `evals/test_s012_journey_through_a_host.py` | the chips assertion leaves `_read_the_lines`; a new `_the_questions_land` goes in between the third approval and People; the People step reads `questionsState`; three comments are corrected |
| `harness/refusals.py` | one new reader: the newest terminal failure on a **screen** (`QUESTIONS` has no stage) |
| `harness/agent_host.py` | `short_stops_at`'s sentence loses the word *questions* |
| `harness/browser.py` | one docstring: `ReviewCard.asked_first` names the block keel-web deleted |
| `tests/` | one new module, and two existing ones gain cases |
| `README.md`, `AGENTS.md` | one paragraph each |

## 2. Where the new step goes, and why exactly there

`_walk_stage_live` runs three times in a loop and each pass ends with `ReviewCard.continue_onward()`.
The `QUESTIONS` job fires on the approval that makes `Project.allFramedStagesApproved()` true — which
is **every** approval in this walk, because an unframed stage is not waited on (journeys §1.2: *"a
framed stage the founder has not written is skipped, not blocked on"*). So a job runs after the
first approval, and a second after the second, and a third after the third; each sees more beliefs
than the last and rewrites the questionnaire whole.

This pass waits **once**, after the loop, for two reasons and they pull the same way:

1. **Only the last one matters.** The questionnaire the strangers answer is the one standing after
   the last approval. Waiting after each would be waiting for two intermediate documents nobody is
   ever shown.
2. **It is where the founder waits.** keel-web 026 FR-017 locks People until `READY`; the founder's
   own next click after the third *Continue* is People. Putting the wait anywhere else would be the
   referee waiting somewhere a founder does not.

So: `for stage in STAGES: _walk_stage_live(...)` → `_the_questions_land(...)` → `People`.

## 3. The wait, in one shape

```
deadline = now + (keels_ai_job_wait_s if KEELS_AI else 420)
retried  = False
while now < deadline:
    state = overview["questionsState"]
    if state == "READY":            break
    if state == "FAILED" and not retried:
        POST /v2/projects/{id}/questionnaire/retry   # 202 {interactionId}
        retried = True
    elif state == "FAILED":         break            # a second one; fail with the wire's reason
    if KEELS_AI: _refuse_if_the_door_is_shut(...)    # spec 024 FR-010
    sleep 3s
```

**Three decisions inside that shape.**

- **`questionsState` absent is not `READY`.** A keel-cloud older than 048 sends no field at all, and
  keel-web falls back to `stages.every(approved)` (its `everyCardApproved`, FR-024). The referee does
  **not** copy that fallback: this repository floats at sibling HEADs by design (`AGENTS.md`), a
  staging twin that did not carry 048 would be the finding, and a referee that quietly passed on an
  absent field would hide it. An absent state is recorded and waited on, and the timeout names it.
- **One retry, and the second failure is keel-cloud's sentence.** `POST …/questionnaire/retry` is
  refused in every state but `FAILED` (422, rule `screen`), so there is nothing to guard: the only
  state it is sent in is the only state it is legal in.
- **The retry does not loosen the end-of-run accounting.** The failed `QUESTIONS` interaction stays
  on `/v2/inference-interactions`, and the *zero refusals, every job COMPLETED* step at the tail will
  name it. That is correct and deliberate (spec FR-020): the retry exists so the run says **why, at
  the moment it happened**, and still produces People, the readings and the brief as evidence —
  not so a red run reads green.

## 4. The moved assertion, read from both ends

`all(line["chips"])` was one read of one screen. It becomes two reads of two documents, and together
they say more than the one did:

- **the wire** — `GET /v2/projects/{id}/questionnaire`: every selection offers a pick list
  (`options` for `OPTIONS`, `buckets` for `BUCKETS`). This is the assertion itself, on the document
  that now owns it.
- **the screen** — the three approved cards, through `OpenedCard.strips()`, whose `read_line` is
  already read by that page object (`.strip__read`, keel-web 026 FR-020). At least one across the
  three. This is what proves the slice reached a founder rather than only a JSON reader.

**`occasion` is not asserted and cannot be.** The spec's own input asked for *"≥ 1 anchor with an
occasion"*; `QuestionnaireView`'s description says the opposite in as many words — *"`occasion` is
deliberately not here and is the only anchor field that is not — it is authoring metadata, stored on
the anchor, compared by `Q8`, never on `Form` and never shown"*. What is participant-visible is the
**section title** `FormComposer` renders the occasion as, and S-012 already asserts that: one section
per anchor block, and none of the three stage titles (spec 025 FR-021, the scenario's §2.1a step).
Recorded as Discovered **D-1** rather than silently dropped.

**`reads` is not on that wire either.** It is the model's own `QUESTIONS` answer — 0-based indices
into the context's `measurements[]` — which the server resolves into `Belief.selectionId` and
`Belief.readsBelief`. So *"selections whose `reads` resolve"* is asserted where the resolution is
visible: every `selectionId` a card names resolves to a selection on the one questionnaire (FR-012),
and every `readsBelief` names a stage and a line that exist (FR-013). Discovered **D-2**.

## 5. Test strategy — stackless, and honest about it

Nothing here can be proven green without a live host, so nothing here claims to be. The unit tests
do the two things that **are** stackless and that would have caught run 36862514753 in CI:

- **source tests**, the shape `tests/test_journey_through_a_host.py` already uses: the chips
  assertion is gone from `_read_the_lines`, the words that explain why are there, the new step is
  called between the loop and People, the ceiling is read off the host object rather than branched
  on, and the retry is sent exactly once.
- **markup tests**, the shape `tests/test_participant_sections_are_occasions.py` already uses:
  `ReviewLine`'s real markup with and without chips, and `ApprovedCard`'s real `.strip__read`,
  rendered into a Playwright page and read through the page objects, so *"`OpenedCard.strips()`
  already reads `read_line`"* is a measurement rather than a claim.

Plus pure-function tests for the new `refusals` reader.

## 6. Phases

1. **Read** — the designs, the two keel-cloud specs, keel-web 026, the openapi, keel-web's own
   markup, the red run. No file written.
2. **The review card** — FR-001 to FR-003, with its tests.
3. **The questions land** — FR-004 to FR-014, with its tests. The biggest commit.
4. **People** — FR-015 to FR-017, with its tests.
5. **The sweep** — FR-018 to FR-021, with its tests.
6. **The documents** — FR-022 to FR-024: the bundle's own sentence, `README.md`, `AGENTS.md`, and
   the next live run written down.

`make unit` green before every commit, and each phase's tests land in the commit of the phase they
certify (spec 025 D11's rule, kept).
