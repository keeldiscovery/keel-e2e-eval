# Tasks 154 -- The walk and the fakes follow Sent's three tabs and the calls

Branch `spec-154`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-154` (`.git` a file, asserted first),
cut at master `acd4c25`. Built by a builder (Claude Fable 5.1) on 2026-11-13 ET, from 02:02 ET. Read only: keel-cloud-docs
master **`e4497962`** (245 / 247 / 250 / 248 merged; contract **69**; `canon/openapi-v2.yaml`; `InferenceCharge.VERSION`
**17**; `dimension-cards.md` at `4dc14231...`) and keel-web master **`697a7a2b`** (186 / 187 / 188 / 189 / 190 merged).
Nothing paid: no host, no instruction screen, no cycle -- the unit suite and the journeys on the fakes (the scripted
runtime, the fake renderer, the fake transcriber), the stack pointed at the two masters above through an **uncommitted**
`stack.toml` (absolute paths; the repo has no override, and the worktree's `../` would resolve to other worktrees). Not
merged; master untouched; every commit pushed as it landed.

**Scope of this pass** (the coordinator's brief): FR-0, FR-1, FR-2, FR-3, FR-5, the part of FR-4 that keel-cloud 248
allows (plan, sign in, PLANNED / ON_CALL, *You wrote*), FR-7 as *the `FIRST_PERSON` kind added to `instructions/run.py`,
never run*. **Left as TODO until cloud 249 merges (contract 70)**: FR-4's upload / digest assertions and FR-6's contract-70
digest -- marked `TODO(249)` below and in the code.

## Plan, per FR

- [ ] **FR-0 owed since 245 / 186.** `quality/readers/dimensions.md` copied byte for byte from `e4497962`'s
  `dimension-cards.md` (`4dc14231...`; 243's `94fd69c0...` the step before); the pin chain moved; a new mirror test
  `tests/test_cloud_245_250_248_web_186_190_mirror_154.py`. `harness/vectors_script.py`: `drafted_list` writes no `asked`
  / `only_if` (the Compatibility `kind` still read off the corpus face, never sent); `asked_result` answers every index of
  the saved list. `harness/vectors_screens.py`: the Check's rows read with no reword line (`reword` counted, owed 0);
  `list_choose` waits for `choose-asked-writing` to leave (2 s polls, 90 s cap, then one GET of the calibration) and
  reads `choose-asked` / `choose-asked-as-written` (`asked_line`). `evals/corpus_scenario.py`: `choose_faults` holds the
  line on the two asked lists; the Check holds no reword line. `stack/cloud_log.py`: the stack's `cloud.log` read for the
  new lines (*asked after the read-back*, *interviewer set up / ready*, *project / interviewer bought*, *credits
  refused*, *call planned / signed in / started*, *first-person written*), a note step on the local profile.
- [ ] **FR-1 the lock and the two gates.** `interviewer_leg._lock_switch` -> the body is `{expectedRevision}` alone (no
  `interviewer`, no `recordOnSend`); `InterviewerFaces` read with no `recordOnSend` / `preselected` / `changePrice`.
  `harness/interviewer_fake.py`: `PRICE_VERSION` 17, `CREDITS` 1,500 (`RECORD_PRICE`), `PROJECT` 1,000, the change at 0.
  `harness/interview_charge.py`: version 17 -- `NEW_PROJECT_PRICE` 1,000 (`PROJECT`, one SPEND written whole), Begin
  writes **no** row (`INTERVIEW` 0, nothing written), no INACTIVE link. The leg's credit steps on Keel's door (the
  stand-in grant 2,500): 1,500 at the first kind's set-up, nothing at the second; a second project bought through the
  API is one SPEND `PROJECT` v17 of 1,000 leaving 0; a link served with the owner at 0; the balance stood at 900 and New
  project refused **422** `INSUFFICIENT_CREDITS_FOR_NEW_PROJECT` `required` 1000; nothing at Begin.
- [ ] **FR-2 Sent as three tabs.** `harness/interviews_screens.py`: `SENT_TAB` gains `calls`, the panels
  `sent-panel-{name,group,calls}`; `send_someone` through **New link** (`new-link` on By name, `new-link-popup`,
  `send-kind-{roleId}` when two kinds, `#send-name`, `send-format-*`, `send-make`, `link-made`); `send_group` through
  **New group link** (`new-group-link`, `#send-group-name`, `group-link-made`); the search box from six rows asserted
  in `links_reading` as before (`LINKS_SEARCH_FROM`). G15's register read inside `[role=tabpanel]`.
- [ ] **FR-3 the interviewer per kind.** `interviewer_fake`: `GET interviewer` a list (`view_of(list, role_id)`),
  `NOT_SET_UP`, the `kinds/{roleId}/record` route, `try/{roleId}`. `harness/interviewer_screens.Persona`: `card(label)`
  (`data-interviewer`, `kind-asks`, `kind-progress`), `set_up(label, face)` through `set-up-interviewer` ->
  `set-up-interviewer-popup` -> `set-up-record`. `evals/interviewer_leg.py` restructured on 247: the own-AI read is a
  200 list (the AI link still 422 NEEDS_CREDITS); the first set-up from the card (the face step, the 1,500 line, 202),
  the card's progress words, READY on the fake renderer (`interviewer ready:`), `recordingPaid` true after; an AI link for
  the set-up kind; the other kind's AI row greyed *Set up first* in New link (B2B); `try/{roleId}` for the set-up kind
  only. Retired by name (their doors are gone from the product): the persona line and its band (IM30), *Change who
  asks* (IM10, IM11), the inactive link, L1's carousel.
- [ ] **FR-4 (the 248 half) + FR-5.** `evals/calls_leg.py`: Plan a call through `plan-call` (the kind row on two kinds,
  the name, `plan-call-press`, `plan-call-done`); the row `call-row[data-status=PLANNED]`; `call-start` ->
  `start-call-sheet` (steps 1 and 3; the copilot opened by the harness itself); the person signs in through the stub
  issuer on the CALL token (`call-arrival` -> `arrival-google` -> the picker -> `call-signed-in`); the row's identity
  GOOGLE and *You wrote {typed}* where the names differ; the card walk headless: fake `mediaDevices` (two silent tracks,
  two microphones) and a fake `documentPictureInPicture` so the browser check passes; the mic picked by name and
  remembered across a reload; Start (ON_CALL on the wire); six filings with one undo; the STORY, FOLLOW_UP,
  OWN_QUESTIONS and THEIR_QUESTIONS stretches; End -> the upload hits `POST calls/{id}/record` with three parts
  `founder` / `them` / `keys`. Float: drawn, never pressed, never floating (`floating` absent). On S-005 after the
  interviewer leg. `TODO(249)`: 202, the row to ANSWERED, the digest, the n line, *heard*, the 30 line.
- [ ] **FR-6.** `vectors_screens.REVIEW_CONTRACT` 65 -> **69** (`TODO(249)`: 70); the price pins 15 -> 17 in the unit
  suite; `make unit` green.
- [ ] **FR-7 the `FIRST_PERSON` kind.** `instructions/contract.py` `SCREEN_FIRST_PERSON`; `instruction.STEMS`
  `first-person`; `prompts.KINDS` + the case (`<entry>/FIRST_PERSON/run<N>`, context `idea_belief` / `idea_what` /
  `idea_how` from the entry's mechanism); `run.KIND_WORDS["first_person"]`; `validate` batches it as CONTEXT's shape
  (`InferenceScreen.FIRST_PERSON`, unmeasured by name where the validator does not take it); never run.
- [ ] **FR-8 nothing else.** No stack, `score.py`, bench or prototype change.

## Commits

| Commit | What |
|---|---|
| (this) | tasks.md, the plan |

## Counts

(filled at the end: `make unit`, the journeys on the fakes.)

## Judgement calls

(filled as they are made.)

## TODO(249)

- FR-4: the fake call record (`fixtures/calls/`), the upload's 202, the row to ANSWERED, the filed answers, the story
  RECORDED, one follow-up, two notes, `heard` on item 1, the 30 line, the n line's `unverified`.
- FR-6: the contract digest at 70.
