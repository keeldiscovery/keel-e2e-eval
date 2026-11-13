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

## What was built, per FR

- [x] **FR-0 owed since 245 / 186.** `quality/readers/dimensions.md` copied byte for byte from `e4497962`'s
  `dimension-cards.md` (`4dc14231...`); the pin chain moved (`CARDS_SHA256_141` = 245's, 243's `94fd69c0...` the step
  before; 149's test holds either). `harness/vectors_script.py`: `drafted_list` writes no `asked` / `only_if` on
  Compatibility and Adoption friction (the corpus face still read for the row's `kind`; L4 still refuses a face-less corpus
  row); `asked_result` answers **every index** of the saved list (a row with no corpus face answered with its label).
  `harness/vectors_screens.py`: each Check row carries `reword` (owed False); `list_choose` reads the asked line
  (`_choose_asked_line`: `choose-asked` with lead and question, `choose-asked-as-written`, or `choose-asked-writing` waited
  out at 2 s polls to a 90 s cap, `waited_s` kept). `evals/corpus_scenario.py`: `choose_faults` holds the line on the two
  asked lists; the framing step faults a reword line on any Check; `_asked_log_note` reads keel-cloud's *asked after the
  read-back* lines for the project on the solution stage (a note). `stack/cloud_log.py` (new): the stack's `cloud.log`
  read by prefix with its `key=value` fields (`LINES`: the eleven lines 245 / 247 / 248 / 250 write), `None` on the remote
  profile.
- [x] **FR-1 the lock and the two gates.** `interviewer_leg._lock_body` (`_lock_switch` kept as its name): the body is
  `{expectedRevision}` alone, no switch, no carousel, no price word on the lock screen (kept as IM2's L1). The walk's lock
  step (`_keels_door_l1` / `_own_door_l1`) holds 187's one screen on both doors: *Lock your answers*, the one line, *Lock
  and write the questions*, the body's keys. `harness/interviewer_fake.py`: `PRICE_VERSION` 17, `CREDITS` = `RECORD_PRICE`
  1,500 (`COST_MICRO_USD` 7,500,000), `CHANGE_PRICE` 0, `PROJECT` 1,000, `GRANT` 2,500, `PRICES`, `NOT_SET_UP`,
  `view_of(list, role)`, `record_route` / `try_route`, the log prefixes, `INSUFFICIENT_PROJECT` and the two remedies.
  `harness/interview_charge.py`: version 17 -- `PROJECT_PRICE` / `NEW_PROJECT_PRICE` 1,000 (`NEW_PROJECT_PRICE_V15` 298
  kept), `INTERVIEW_CREDITS` 0 with `written_at_begin()` False (`INTERVIEW_CREDITS_V16` 30 the shape of record;
  `charged_once` names any row as the fault), `INACTIVE_RETIRED`, `project_key` / `project_rows` / `project_row_faults` /
  `bought_once` / `moves_balance`, `project_credits` 1,000 flat from 17 (`FIVE_PARTICIPANTS` 1,000; the Makefile,
  `matrix/cells.toml` and the matrix test say so). `stack/ledger.GRANT_CREDITS` and `agent_host.KEELS_AI_GRANT` 2,500.
  `interviewer_leg._two_gates` (local profile): a second project bought through `POST /v2/projects` is one SPEND `PROJECT`
  of 1,000 at 17 (`bought_once`), the balance 0 after (2,500 - 1,500 - 1,000), the `project bought:` line; a text link on
  the journey's project served with the owner at 0 (state OPEN, nothing INACTIVE); on B2B the other kind's New-link rows
  read *Set up first* with the on-card line, then that kind set up for nothing (*Already paid*, *Record {Face}*, 202, no
  row, READY); the balance stood in at 900 and `POST /v2/projects` refused **422** `INSUFFICIENT_CREDITS_FOR_NEW_PROJECT`
  `required` 1000 with the sentence, nothing made, the `credits refused:` line; the balance back to 0. `_begin` /
  `_begun_on_screen`: 204 and **no** row, the balance unmoved. The closing sweep: no INTERVIEW row anywhere, nothing but
  PROJECT, the recording's pair and the stand-ins moves the balance. `open_link_leg`: strangers A and B begin with no row;
  `ledger_faults` owes none; `the_ledger` says so.
- [x] **FR-2 Sent as three tabs.** `harness/interviews_screens.py`: `SENT_TAB` / `SENT_PANEL` with `calls`, 187's label
  (`SENT_TABS_LABEL`; 136's kept as `_136`), the leads, the three buttons, the New-link popup's ids and words;
  `tabs()` reads the three tabs with `aria-controls` and the open panel (its lead, its button, its empty line);
  `open_new_link(project, kind_label, mode)` presses New link / New group link, the kind row when drawn
  (`send-kind-{roleId}` off the card's `data-role`), and reads the format rows as served (`_new_link_formats`:
  checked, disabled, the greyed word, `format-status`, the on-card line); `send_someone` is the one screen -- *Their
  name*, the format, *Make {first}'s link* -> `POST invitations/batch`, `link-made`, Done (the record keeps `press`,
  `ready`, `popup`); `send_group` the group's screen -- *Name this group*, the cap line, the format, *Make the link* ->
  `POST groups`, `group-link-made`; `formats_for` reads and cancels. `make_new_link` (the row's *New link, {name}*)
  unchanged. The search box from six rows stays `links_reading`'s (`LINKS_SEARCH_FROM`); the Calls table's own is read in
  the calls leg. G15's register read is inside the panel (`[role=tabpanel]`).
- [x] **FR-3 the interviewer per kind.** `harness/interviewer_screens.Persona`: `card(label)` (`data-interviewer`,
  `kind-asks`, the primary's id / words / enabled, `kind-progress` with its bar and words, `kind-failure`),
  `wait_card_state`, `set_up(label, face, hear_s)` through `set-up-interviewer` -> `set-up-interviewer-popup` (kicker,
  title, the carousel, `set-up-cost[data-paid]`, *Not now*, *Record {Face} · 1,500 credits*) -> `POST
  interviewer/kinds/{roleId}/record`; the persona line, its popup, Send more's rows, the band's Hear and L1's carousel
  removed with their doors (`line`, `wait_state`, `record`, `formats_now`, `hear_band`, `l1_again`); 187's words as
  constants (`setup_interviewer`, `record_face`, `kind_asks`, `kind_recording`, `persona_progress`, ...).
  `evals/interviewer_leg.py` restructured: `_own_ai` reads the list (200, every kind NOT_SET_UP, `recordingOpen` false) and
  is refused a set-up and an AI link (422 NEEDS_CREDITS); `_first_set_up` (the faces at 1,500 / not paid / open, FACE_UNKNOWN
  on the kind's route, the card's button words, the face step's words, 202, -1,500, `recordingPaid` true, the two log
  lines); `_ready` per kind (`view_of`, no `changePrice`, the `interviewer ready:` line); `_sent_after_set_up` (the card
  READY: *{Face} asks*, *Try it yourself* lit, no band); `_screens_recording` / `_screens_ready` on the card and New
  link's rows (full leg); `_the_recording` merges `lock.recordings` per kind (`stack/ledger.recordings` /
  `recording_of`, document 38), `try/{roleId}` for a set-up kind alone (409 NOT_READY recorded otherwise);
  `_retired_doors` names the change, the low balance and the inactive link. `evals/interviewer_marks.py` **v18**: IM2
  on 247 / 250's screens (L1 no price at all; S1 / S2 own one *Set up the AI interviewer · N once* at the served
  `recordPrice`; S3 owns *Set up first · N once*, no credits note), `ALLOWED_PRICE_KEYS` widened, `served_prices` reads
  `recordPrice`; `RETIRED` = IM10, IM11, IM30 (never measured, the reason on the card); `SHORT_FORM` without IM30.
- [x] **FR-4 (the 248 half) + FR-5.** `evals/calls_leg.py` (new), on S-005 after the interviewer leg: the Calls tab
  empty (*Calls with me · 0*, the lead, Plan a call enabled, *No calls planned.*); `plan_a_call` (the one screen, the
  kind row on two kinds, 201 CallRow: PLANNED, NONE, `typedName`, `signInUrl`, `copilotPath`, the Done screen, the
  `call planned:` line); `read_the_row` (status word, name, *You wrote {typed}*, *Start the call*); `start_sheet`
  (the three steps, 1 and 3 pressed green, the link drawn or copied); `sign_the_person_in` (the CALL token's
  CALL_ARRIVAL -- the notice with the founder's first name, Continue with Google, no Begin, nothing of the questionnaire;
  the stub picker by the registered identity; CALL_SIGNED_IN; the row GOOGLE with Google's name, `nameDiffers`, the
  `call signed in:` line); `walk_the_card` headless (FR-5: `FAKE_MEDIA` -- two silent `AudioContext` tracks, two
  microphones by label, a `documentPictureInPicture` object so the check passes; the mic picked `mic-two` and remembered
  across a reload (`keel-copilot-mic`); Start -> `POST start` 200 ON_CALL; `_walk_filings` by the card's buttons --
  the intro's →, the gate's Yes and the STORY stretch stopped, `opt-1` / a typed 3 on a number, the ladder's second
  step, the follow-up stretch stopped, the reveal's →, the pilot -- with one undo (Z) on the second filing;
  `_walk_closing` opens and stops OWN_QUESTIONS and THEIR_QUESTIONS; End -> the upload kept off the wire: one multipart,
  parts `founder` / `them` / `keys`, files `founder.wav` / `them.wav` / `keys.json`; Float drawn, never pressed, the card
  never floating). A second call typed as the person's own first name: `nameDiffers` false, no *You wrote*. The
  register after: every call drawn, the search box from six rows.
- [x] **FR-6.** `REVIEW_CONTRACT` 65 -> **69** (`TODO(249)`: 70); the price pins 15 -> 17; the screen-response contract
  pins read 25 or 26 (245 moved it); `tests/test_cloud_245_250_248_web_186_190_mirror_154.py` (88): the digest, the
  charge table and the grant, the contract and the routes, the project row and the leg's gates, every selector the
  harness presses in keel-web's source, the words, the card's three parts, the FIRST_PERSON wiring.
- [x] **FR-7 the `FIRST_PERSON` kind.** `instructions/contract.py` `SCREEN_FIRST_PERSON`, `FIRST_PERSON_FIELD`,
  `FIRST_PERSON_CONTRACT` (COMPLETED alone, one string field, 200 characters); `instruction.STEMS["FIRST_PERSON"]`
  `first-person`; `prompts.KINDS` + the case `<entry>/FIRST_PERSON/run<N>` built where the entry's mechanism carries
  `idea_belief` (`context.build_first_person`: `idea_belief` / `idea_what` / `idea_how`); `run.KIND_WORDS["first_person"]`
  (and `first-person`), `SCREENS` + FIRST_PERSON so its instruction is read, `_score` holds the one field to
  `context.first_person_faults` (F1 empty, F2 over 200, F3 third person, F4 not opening *I believe it would*, F5 a
  plural first person) -- reported in the line, never a mark; the cloud's validator is never asked for it (no
  InferenceScreen). **Never run.** `make instruction-screen HOST=claude K=<entry>/FIRST_PERSON N=3
  WHY=instruction:first-person.md` is the founder's door.
- [x] **FR-8 nothing else.** No stack, `score.py`, bench or prototype change.

## Commits

| Commit | What |
|---|---|
| (this) | tasks.md, the plan |

## Counts

(filled at the end: `make unit`, the journeys on the fakes.)

## Judgement calls

1. **The fakes were broken before this spec, three times over, and the walk says so now.** The scripted executor
   matches a screen by its exact context key set, from keel-cloud's own `context-keys.json` export -- and since
   keel-cloud 229 (Importance's draft is handed `problem_clause`), 228 (Current solution's draft is handed
   `answer_parts`) and 226 (W-rung refuses a corpus rung once, so a redraft is handed `repair`) three key sets the
   export does not name reach the runtime. No scripted journey had run since 2026-10-30 (the cycles walk the real
   model), so nothing saw it. `vectors_script.context_keys_for` now writes the three as screens of their own
   (`CALIBRATION_QUESTIONS+problem_clause`, `+answer_parts`, and each `+repair`) and `generate` files each job under
   the set it will be matched through (`calibration_screen_of`, `study_holds_went_wrong`), the redraft answered
   with the same corpus result (keel-cloud's wording rules note a second refusal and serve the row as drafted). Not in
   the spec's text; FR-0's *the walk keeps walking* could not hold without it.
2. **The marks are v18.** IM10 (the change of face), IM11 (its refusal at a low balance) and IM30 (the band's Hear)
   are retired -- the product has no door for them (keel-cloud 247 FR-1 / FR-6, keel-web 187) -- never measured, the
   reason on the card; IM2 holds L1 to no price word at all and Sent's cards / New link's rows to 187's own priced
   words at the served `recordPrice`. The spec names no marks version; the change is the honest one.
3. **The full leg (S-006) is restructured but not walked.** The short form (S-005) was walked on the fakes; the
   B2B steps (`_screens_recording`, `_screens_ready`, the second kind's free set-up in `_two_gates`, `_choice_link`,
   `_recorded_link`, `_retry`) are written on 247 / 250's shapes and read by the unit suite only. Time.
4. **The card's upload is asserted off the wire, not by its answer.** keel-cloud 249's record route is not on
   `e4497962`, so `POST calls/{id}/record` answers 404 and the card draws its failure line; the leg keeps the
   request (three parts, the file names, the multipart type) and records the phase, asserting nothing of the answer
   (`TODO(249)`).
5. **Float in headless.** The browser check needs `documentPictureInPicture` to exist, so the fake defines one whose
   `requestWindow` refuses; the Float button is asserted drawn and the card never floating, and it is never pressed --
   the spec's *absent or disabled, never failed* read as *never floating, never failed*.
6. **The card runs in the founder's own context**, a new page with the fake sources installed by `add_init_script`
   -- never a cookie set by hand (`tests/test_stub_oidc.py` refuses any login bypass, and it caught the first draft).
7. **The person signs in on the stub issuer by the harness's own registry identity** (`register_stranger`, as the
   group link's strangers), typed once as a nickname (*You wrote*) and once as their own first name (`nameDiffers`
   false). Two calls, so the second stays PLANNED and unverified for 249's n line.
8. **Pins moved with the cloud, not only with the spec**: `ScreenResponseContracts.CONTRACT_VERSION` 26 (245),
   `SCHEMA_VERSION` 39 (248), `AnsweredRows(..., ReviewDto asked)` (245), every job row priced 0 at 17 -- each old test
   reads its version of record or a later one, named.
9. **Retired by name, kept as the record**: `tests/test_im2_staging_switch_094.py` (the lock's switch), 090's two
   tests on Send more's way and L1's 130 title, 091's five IM2 tests on L1's credits sentence, 150's `SEND_WHO`
   ways, the Persona's `line` / `record` / `formats_now` / `hear_band` / `l1_again`.
10. **Nothing paid, nothing on host claude.** The FIRST_PERSON kind is wired and tested by the unit suite's case
    builder alone; no instruction screen ran.

## TODO(249)

- FR-4: the fake call record (`fixtures/calls/`), the upload's 202, the row to ANSWERED, the filed answers, the story
  RECORDED, one follow-up, two notes, `heard` on item 1, the 30 line, the n line's `unverified`.
- FR-6: the contract digest at 70.
