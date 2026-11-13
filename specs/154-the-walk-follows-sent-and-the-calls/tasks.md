# Tasks 154 -- The walk and the fakes follow Sent's three tabs and the calls

Branch `spec-154`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-154` (`.git` a file, asserted first),
cut at master `acd4c25`. Built by a builder (Claude Fable 5.1) on 2026-11-13 ET, from 02:02 ET. Read only: keel-cloud-docs
master **`e4497962`** (245 / 247 / 250 / 248 merged; contract **69**; `canon/openapi-v2.yaml`; `InferenceCharge.VERSION`
**17**; `dimension-cards.md` at `4dc14231...`) and keel-web master **`697a7a2b`** (186 / 187 / 188 / 189 / 190 merged).
Nothing paid: no host, no instruction screen, no cycle -- the unit suite and the journeys on the fakes (the scripted
runtime, the fake renderer, the fake transcriber), the stack pointed at the two masters above through an **uncommitted**
`stack.toml` (absolute paths; the repo has no override, and the worktree's `../` would resolve to other worktrees). Not
merged; master untouched; every commit pushed as it landed.

**Two passes** (the coordinator's brief): the first on keel-cloud-docs `e4497962` (contract 69) -- FR-0, FR-1, FR-2,
FR-3, FR-5, the part of FR-4 that keel-cloud 248 allows, FR-7 as *the `FIRST_PERSON` kind added, never run*; the second
on **`dfdad66a`** (249 merged: contract **70**, document **40**) -- FR-4's upload / digest assertions and FR-6's digest at
70. The stack ran against the two main checkouts throughout (the playground profile; the cloud restarted on `dfdad66a`
for the second pass).

**Third pass (2026-11-13, 06:50 -- 09:40 ET, a second builder after the first hit its usage limit).** Finished the
uncommitted gate fixes, then walked S-005 on the fakes until it reached the calls leg. Mid-pass the coordinator moved
the cloud to **keel-cloud-docs `34735d05`** (251 merged: **contract 71**, the 1,000 written at a project's FIRST LOCK,
reason `project:lock`; creation writes no row and is never refused); the gate's last runs are on `34735d05`. keel-web
master moved under the walk too (`697a7a2b` -> `aa8b49c6` contract 70 vendored -> `7fefa951` integration -> `965ad85a`,
191's first commits); vite served the checkout live, so each run read keel-web master as it stood. **The S-005 scripted
walk had not reached the commercial review since 2026-10-30** (the first pass's runs stopped at step 125 at best, so
"S-005 walked on the fakes" above meant its first half): this pass found and fixed the drift between there and the
calls leg -- every fix below is a reading of what the product serves now, none moves a product rule:

- FR-0: the Choose's 90 s asked-line ceiling is spent only on the two asked lists (it was waited on every Choose, the
  unit fixtures too); a Choose with no line and no question on the wire is a finding, not a fault (on `dfdad66a`
  Adoption friction's asked job starts at the Choose's Save, confirmed in the database: its ASKED job is created at the
  Continue); the stored lists are read once the asked jobs landed (`_wait_asked_faces`: no open step, every asked row
  faced).
- The corpus reader mirrors keel-cloud **188 FR-2** (`spec188Reads`, the step under 199's): the record's *the payer*
  read as the deciders' own plural (*The problem already costs independent restaurant managers ...*).
- The follow-ups: `{solution_name}` is the idea's name alone off **185 FR-2**'s reveal (*Imagine {name}, {what it is}.*);
  Adoption friction's conditional yes is followed up in the registry's words (**184 FR-7** retired 174's said-back).
- The report marks (v3, unchanged): a quote's side `NOT_COUNTED` (**180**, contract 50); each Insights box's served
  `statusLine` / `countLine` are its own words (keel-web **155 FR-7**), not repeated Overview numbers.
- The interviewer leg: `GET interviewer` kept as the list it is (the wire helper handed `{}`); the kind card's
  *{Face} asks* and the call row's *You wrote {typed}* read without the separator keel-web draws inside the span; the
  log lines read with a short wait (`cloud_log.wait_lines`: the cloud's stdout reaches `cloud.log` in chunks); IM3 reads
  the price ladder's `#under` / `#over` clips as the item's own; the AI person's second follow-up is the earliest other
  one-of rung where the last item is already the only rung owed.
- **FR-1 on 251**: the leg's second project is created for nothing (201, no PROJECT row, no `project bought:` line,
  balance unmoved), its uncalibrated lock answers its own refusal first and writes nothing; at 900 New project is 201
  with no row and no `credits refused:` line; the closing sweep owes NO PROJECT row; `PROJECT_REASON` `project:lock`
  (`project:new` kept as 250's). **Not walked on the fakes: the lock's own SPEND of 1,000 and its 422 at 900** -- the
  journey's project locks on its own AI before Keel's door, and a second project would have to be calibrated whole to
  reach a lock that reads the balance (domain refusals answer first, 251 judgement call 3). Said plainly; owed.
- FR-6: `REVIEW_CONTRACT` **71**, `CONTRACT_SHA256_71` `f5a078b1...` (`canon/openapi-v2.yaml` at `34735d05`), 70's sha
  kept; the web's vendored copy pinned by version (70 at `aa8b49c6`: `a6de15c4...`, its body = cloud's 70; 71 once
  vendored: its body = cloud's 71).

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
- [x] **FR-4 + FR-5.** `evals/calls_leg.py` (new), on S-005 after the interviewer leg: the Calls tab
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
  parts `founder` / `them` / `keys`, files `founder.wav` / `them.wav` / `keys.json`, answered **200** with the row;
  `wait_digested` reads the row ENDED then ANSWERED (the digest's thread), the card's phase `done`, the `call ended` /
  `call digested` / `call counted` lines; Float drawn, never pressed, the card never floating). The n line after it:
  `people.unverified` 0 (its person signed in). **The second pass (keel-cloud 249)**: a second call, typed as the
  person's own first name and **never signed in**, started on the wire and uploaded the **fake call record**
  (`evals/call_record.py`, `fixtures/calls/`): two 16 kHz mono 16-bit WAVs and the key log built off the served script
  -- the gate's Yes with its STORY stretch, six items filed (option 1 each, a typed 3 on a number item), the third undone
  and filed again, the FOLLOW_UP stretch after the item whose `against` names the filed option, the pilot's Yes, the
  OWN_QUESTIONS and THEIR_QUESTIONS stretches, End; the founder's track silent with a tone at every filing, the
  person's with the words the stack's fake transcriber hears (keel-cloud 136 FR-2: audio that is text) at each window
  the digest cuts -- the story, the follow-up, each voice's note, and **option 3's label at item 1's pick-check window**,
  so the fake classifier names option 3 where option 1 was filed. `upload_fixture_record` (200, ENDED, then ANSWERED);
  `the_digest`: the detail (format CALL, `callId`, identity NONE, six answers TAPPED each with its `at`, `heard` on item
  1 = option 3's label, the story as heard, one follow-up with its words, two notes OWN / THEIR with both voices), the
  timeline (the filings kept after the undo in time order, the four stretch kinds, two notes, `heard`), Hear the call
  (`audio/them` 206 to a Range of 100 bytes, `audio/founder` 200 whole with `Accept-Ranges` and the fixture's exact
  length, another track word 404), NO INTERVIEW ledger row and nothing that moves the balance (keel-cloud 250 over the
  spec's "30 line"), and `people.unverified` **1** with the call inside `answered`. The register after: every call
  drawn, the search box from six rows.
- [x] **FR-6.** `REVIEW_CONTRACT` 65 -> **70** (69 in the first pass); the vendored contract pinned by its sha256
  (`CONTRACT_SHA256_70` = `8f218c42...`, `canon/openapi-v2.yaml` at `dfdad66a`), the document version 40; the price
  pins 15 -> 17; the screen-response contract pins read 25 or 26 (245 moved it); `SCHEMA_VERSION` read as 37 or later;
  `tests/test_cloud_245_250_248_web_186_190_mirror_154.py` (89): the digest, the charge table and the grant, the
  contract, its sha, the routes (the kinds', the calls', the record's, the digest's, the timeline's, the audio's), the
  project row and the leg's gates, every selector the harness presses in keel-web's source, the words, the card's three
  parts, the fake call record's shape, the FIRST_PERSON wiring. The web digest waits for the coordinator's sha (keel-web
  master `697a7a2b` re-vendors 70 once more).
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
| `ec4a189` | Spec 154: tasks.md, the plan |
| `68e77e5` | Spec 154 FR-0 / FR-1 / FR-6 / FR-7: the cards at 4dc14231, price version 17 and the two gates in the fakes, no asked/only_if on the drafts, the Check without a reword line, Choose through choose-asked, Sent's three tabs and New link in the page object, the kind card and its face st... |
| `457a001` | Spec 154 FR-1 / FR-3 / FR-4 / FR-5: the interviewer leg on 247 / 250 (the lock body alone, the card's face step, READY per kind, the two gates, Begin writes no row, the retired doors named), the calls leg (plan, the row, the Start sheet, the person's sign-in on the stub issuer, the... |
| `cc9313e` | Spec 154: the calls leg on S-005, the asked-after-the-read-back log note, the open-link journey on the kind's route with no row at Begin, tasks.md drafted |
| `3eb181f` | Spec 154 FR-0: the scripted executor's key sets for Importance's draft (problem_clause, keel-cloud 229), Current solution's (answer_parts, 228) and each redraft (repair); the card walked in the founder's own context; the unit suite's remaining pins moved |
| `a9aa0ac` | Spec 154 FR-0: the ASKED stub answers the Importance probe's two jobs, every faced row's condition and the asked ladder's repair turn; tasks.md judgement calls |
| `0b5e43f` | Spec 154 FR-0: the Adoption friction face cut to K2's frame where the corpus's does not fit; the Importance probe waits for its asked jobs between saves |
| `9d2f81b` | Spec 154 second pass (keel-cloud 249, contract 70): the fake call record and its fixtures, the card's upload digested to ANSWERED, the fixture call's detail / timeline / audio / ledger / unverified assertions, the Choose line's one GET and reload, the digest pins at 70 |
| `1336c74` | Spec 154 FR-0: the Choose line's ceiling spent only on the two asked lists; the line read into the step's record; a Choose with no line and no question on the wire filed as a finding, not a fault |
| `5eb95eb` | Spec 154 FR-0: spec 130's ASKED-result test reads every Adoption friction row with its condition (the step's own where the entry records none) |
| `050b9ca` | Spec 154 FR-6: the mirror test and S-005 name keel-cloud-docs dfdad66a and contract 70; the TODO(249) notes retired |
| `002689b` | Spec 154 FR-0: the stored lists are read once the asked jobs the stage's Saves started have landed |
| `0bf833f` | Spec 154: the corpus reader mirrors keel-cloud 188 FR-2 -- the record's *the payer* read as the deciders' own plural (spec188Reads, the step under 199's) |
| `d0a98a3` | Spec 154 FR-2: the invite leg's greyed-format check skips New link's line under the rows (`_on_card`), as the interviewer leg does |
| `496cdba` | Spec 154: the follow-up's {solution_name} is the idea's name alone off keel-cloud 185's reveal (*Imagine {name}, {what it is}.*), as FollowUpComposer says ideaName |
| `6def1eb` | Spec 154: Adoption friction's conditional yes is followed up in the registry's own words (keel-cloud 184 FR-7 retired 174's said-back) |
| `3d30936` | Spec 154: the report marks read keel-cloud 180's quote side NOT_COUNTED and keel-web 155 FR-7's box head (statusLine, countLine) as the box's own words |
| `85860a1` | Spec 154 FR-3: the interviewer leg's wire helper keeps `GET interviewer`'s list (keel-cloud 247 FR-5) -- it handed the leg {} -- and the recording read takes the primary kind's view off it |
| `39f096c` | Spec 154: the legs read keel-cloud's log lines with a short wait (cloud_log.wait_lines) -- the cloud's stdout reaches the log in chunks, and S-005 read *credits refused:* empty in the second it was written |
| `2794d90` | Spec 154 FR-3: the kind card's *{Face} asks* is read without the separator keel-web 187 draws inside its span |
| `cb3c853` | Spec 154 FR-3: the AI link's person meets two follow-ups where the last item is already the one rung owed -- the latest other served rung answered against, one tap |
| `4169d6d` | Spec 154 FR-3: the AI person's second follow-up is the earliest other one-of rung (the later plain questions stay for the way back); IM3 reads the price ladder's second-step clips (`#under` / `#over`) as the item's own |
| `914c22a` | Spec 154 FR-1 / FR-6 on keel-cloud 251 (contract 71): New project writes no row and is never refused; the leg's second project is created free, its uncalibrated lock answers its own refusal and writes nothing; 900 creates; the closing sweep owes no PROJECT row; the row's reason pro... |
| `a7e0813` | Spec 154 FR-1: the 900 step proves the project made by the 201's id, not by a count of `/v2/me/projects` (which the leg reads empty) |
| `f99b59d` | Spec 154 FR-4: the call row's *You wrote {typed}* is read without the separator keel-web 189 draws inside its span |
| (this) | tasks.md: the third pass, the counts, what remains |

## Counts

Third pass, 2026-11-13 ET, the stack (playground profile) on the two main checkouts through the uncommitted
`stack.toml`; the unit suite needs no stack.

- **`make unit`** (`.venv/bin/python -m pytest tests -q -rs`), 09:07 ET at `a7e0813` + the mirror test's web pin:
  **1 failed, 5,918 passed, 124 skipped** in 361 s. The one failure is environmental and not this spec's:
  `tests/test_copilot_bench.py::test_tts_retries_a_read_timeout` imports numpy, which `requirements.txt` does not carry
  (spec 151's tasks.md says so). The skips: 12 retired by spec 154 by name, the rest the long-standing ones (the corpus
  past revision 2, the live-only, a thin stub). The first run of the pass (06:51 ET) failed one more,
  `test_cloud_198_mirror_130::test_the_scripted_asked_result_writes_condition_and_never_only_if` (the first pass's
  every-row condition, its pin moved: `5eb95eb`), and ran slow (every Choose fixture waited the 90 s ceiling: `1336c74`).
- **S-005 on the fakes** (`make eval K=s005 PROFILE=playground`), sixteen runs 07:19 -- 09:25 ET, `make down` / `make
  up` before each; each fix above is the reading one run stopped on. The last full run on the committed code
  (`20261113T135724Z-s005-countly`, cloud `34735d05`, web master as served at 08:57) walked **386 of its steps green and
  stopped at step 387, the interviewer marks: 21 of 22 met, IM16 owed** (below). A probe run with IM16 tolerated
  (an uncommitted edit, reverted; never committed) went on: the calls leg walked **Sent's Calls tab, Plan a call (201,
  PLANNED), the row, the Start sheet, the person's CALL_ARRIVAL and sign-in on the stub issuer** green, and stopped where
  the copilot card never drew (below). The two gates on 251 (`914c22a`, `a7e0813`) walked green in those runs.
- **S-006 and S-017 not walked in this pass** (time); the three remote journeys on staging are the coordinator's.


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

## Left for the coordinator

Said plainly -- **S-005 is not green yet**; it stops at two places this pass did not finish:

1. **IM16 (the way back) is owed on S-005's AI link.** The walk tries Back on a plain one-of question whose answer owes
   no follow-up and that has another answer owing none. On `34735d05` the AI link's reader (01-countly) has none
   left: Relative advantage (the only item with a safe other answer) carries the read-aloud step
   (`_read_aloud_item`, spec 049 call 1), Compatibility's *Yes, most of the time* owes its #also and its other answers
   all owe, Adoption friction's other answers all owe (its *Only if ...* is a #also), Buyer and payer is the lock's
   rung. Fix owed: move the read-aloud step off the one item that can carry Back, or choose the AI link's reader by a
   Back spot. Not a product fault.
2. **FR-4 / FR-5 on the fakes: the copilot card never draws.** `GET calls/{id}/script` keeps `firstPersonPending`:
   keel-cloud logs *first-person owed: ... not written reason=own-ai* (the eval founder is back on their own AI after
   the interviewer leg's restore), and keel-web 188 holds the writing line and draws no card until the first-person line
   lands. So the card walk (Start, the six filings, End, the three-part upload, ENDED -> ANSWERED) and the fixture call's
   digest (the filed answers, the story, one follow-up, two notes, `heard` on item 1, no INTERVIEW row, `unverified` 0
   then 1) were **not re-confirmed against `dfdad66a` / `34735d05` on the fakes in this pass** -- the assertions are in
   `evals/calls_leg.py` and the unit suite holds their shapes against cloud 249's contract, but no run reached them.
   Fix owed: walk the calls leg on Keel's door (the stand-in, as the interviewer leg does) or have the scripted runtime
   answer the first-person job, then re-run.
3. **251 at the lock, not walked**: the SPEND of 1,000 (`project:lock`) at the first lock, and the 422
   `INSUFFICIENT_CREDITS_FOR_NEW_PROJECT` at 900 at the lock -- S-005's project locks on its own AI before Keel's door;
   walking it needs the stand-in grant before the lock (or a second project calibrated whole).
4. **The web digest**: the mirror test pins keel-web's vendored contract by version -- at keel-web master `851ca8c2`
   (and `aa8b49c6` .. `965ad85a`) it is still **70** (`a6de15c4...`, its body = cloud's 70 byte for byte); once the
   contract-71 vendoring lands, the test asserts its body = cloud's 71 (`f5a078b1...`). Pin the final web sha in
   `WEB_MASTER_70` / a 71 constant when it arrives.
5. `stack.toml` is **uncommitted** (absolute paths to the main checkouts; the repo documents no override).
