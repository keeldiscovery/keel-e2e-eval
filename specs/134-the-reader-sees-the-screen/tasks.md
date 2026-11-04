# Tasks 134 -- The reader judges what the screen showed; the corpus rungs fit the card

Branch `spec-134`, off `60d6147` (the spec and its two amendments), in the worktree
`/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-134` (`.git` a file). Built 2026-11-04 (ET) against keel-cloud-docs
master `c456c0b3` (back-test corpus revision 23) and keel-web master `7509a44b`. Not merged; nothing paid (no walk, no
reader, no `claude -p`); no corpus revision, contract, rubric, card or `MARKS_VERSION` moved.

| Commit | What |
|---|---|
| `7240328` | plan.md; the gate at the base (two pins of `test_decided_before_087` re-pinned, see Deviations) |
| `829d889` | FR-1 to FR-3 and `tests/test_reader_sees_screen_134.py` (11) |
| this commit | FR-4's review (`corpus-rewording.md`), these tasks |

## FR-1 The read-back is the screen's

- [x] T001 `evals/backtest.read_back`: on an Answer and a Check screen (`SCREEN_DRAWN_BELIEF`) no wire `belief`; the
  read-back carries `belief line on screen` where drawn and `keel will test` / `bar` from `test_after` or `test`. On a
  Choose and a `q` screen the wire's belief stays. Held by test: the timed belief (*... within about 4 weeks ...*) never
  reaches an Answer or Check read-back; a Check takes the box after the edit.

## FR-2 Rows are rows

- [x] T002 `harness/vectors_screens`: `LIST_ROW` (`.listcheck ul.listrows li.listrow:not(.listrow--note)`) and
  `LIST_FOUNDER_NOTE` (keel-web 168's `li.listrow--note` / `list-founder-note`); `_list_rows` reads rows by `LIST_ROW` and
  the note as `note` (the founder note and the `.listcheck__note` line, joined; `founder_note` and `guidance` apart).
- [x] T003 `evals/backtest.READ_JS`: rows skip `li.listrow--note`; `note` is the list of guidance lines (the founder note,
  every `.listcheck__note`); `founder_screens` carries `note`.
- [x] T004 `quality/readers.founder_screens`: the note handed to the reader under the rows, labelled
  (`NOTE_LABEL`, *Under the list (Keel's guidance, not a row)*), never among them.

## FR-3 The Check screen is judged after the founder's edit

- [x] T005 `vectors_screens.Corridor.list_check`: the step is named for what it does (*founder checks Keel's list for
  {key}, types their own rows into it and saves it* where the walk types); the docstring says the edit, the second read
  and the second shot; after an edit (`after` read) the screen is shot again (`_reshot`).
- [x] T006 `evals/backtest.Camera.after_edit`: the Check screen's founder record taken again after the edit
  (`founder-NN-check-<key>-after-edit.png`, the same number), its `file`, `rows`, `note`, `keel_test`, `text`, `url` moved
  to that read, Keel's first draw kept under `before_edit`, `edited` set; `founder_screens` carries `edited` and
  `before_edit`.
- [x] T007 `evals/backtest.check_did` (the spec's `founder_did`: `founder_answer`'s `check` branch): *typed {n} of their
  own rungs over Keel's draft, then saved*; rungs typed into new rows and Importance's own further difficulties said too;
  *saved as Keel drafted it* (`CHECK_AS_DRAFTED`) only where nothing was typed.
- [x] T008 `quality/readers`: an edited Check screen's rows are named the founder's (`ROWS_EDITED`, *Rows, as the founder
  left them (they typed their own over Keel's draft, then saved)*).

## FR-4 The corpus rows fit the card (all fourteen)

- [x] T009 `specs/134-the-reader-sees-the-screen/corpus-rewording.md`: the fourteen gallery entries read row by row
  against the cards, Table 1 (entry · dimension · field in the yaml · before · after · rule, 128 rows), the beliefs that
  quote a moved row, the shape changes (splits, drops, a moved pick), the rows judged to fit, and Table 2 (the eval files
  that quote a moved row). Per the coordinator's correction no YAML, fixture or pin moved on this branch.

Every reworded row, with the rule it broke (the rules' words: `corpus-rewording.md`, *How to read it*):

**08-fresco**

- Importance: *Keeping the job on schedule* -> *Planning tomorrow's work and crews* (imp-moment)
- Importance: *Getting subs to show up and finish* -> *Lining up subs to show up tomorrow* (imp-moment, imp-cause)
- Importance: *Keeping the site safe* -> *Following up on safety issues from the walk* (imp-moment)
- Current solution: *Log done on site* -> *Done on site, no time after the walk* (cs-measure)
- Current solution: *Finished at home or the next morning* -> *Took the rest of the evening* (cs-joined, cs-measure)
- Current solution: *Never got written up properly* -> *Never got written up that day* (cs-fail, cs-measure)
- Compatibility: *The job kept its logs in Procore or ACC* -> *could stop to film and talk on the walk* (cmp-settled, cmp-core, cmp-subject)
- Purchase friction: *A trial on one live job* -> *(dropped)* (pf-offer)
- Purchase friction: *A security review* -> *A security review of the site videos* (pf-object)

**09-karsa**

- Importance: *Keeping up with rising bills* -> *Deciding how much to keep back for bills* (imp-moment)
- Importance: *Earning more each month* -> *Getting the leftover rupees to earn something* (imp-moment, imp-backwards)
- Importance: *Paying for things abroad* -> *Getting dollars together for a payment abroad* (imp-moment)
- Current solution: *Bought dollars at a fair rate, no hassle* -> *Bought dollars at the fair rate* (cs-joined, cs-measure)
- Current solution: *Got some after trying several places* -> *Paid well over the rate* (cs-measure)
- Current solution: *Paid a big premium or took a risk* -> *Paid a big premium on every dollar* (cs-joined)
- Current solution: *Could not get dollars and kept rupees* -> *Could not get any dollars* (cs-joined)
- Adoption friction: *Upload an ID card and a photo of payment* -> *Upload a photo of each payment* (af-one, af-ground)

**10-palus**

- Current solution: *Earned a good rate with no effort* -> *Earned a market rate after fees* (cs-joined, cs-measure)
- Current solution: *Earned a fair rate, a little upkeep* -> *Earned a bit under market after fees* (cs-joined, cs-measure)
- Current solution: *Earned a low rate, never revisited* -> *Earned well under market after fees* (cs-joined, cs-measure)
- Current solution: *Earned little after fees and effort* -> *Earned next to nothing after fees* (cs-joined, cs-measure)
- Compatibility: *Their bank could link through Plaid* -> *could keep their current bank while the reserve sat elsewhere* (cmp-settled, cmp-core, cmp-subject)
- Compatibility: *They could wait two days for their cash* -> *could wait one to two business days for their cash* (cmp-clipped)
- Compatibility: *Their policy allowed bonds beyond Treasuries* -> *had a cash policy that allowed bonds beyond Treasuries* (cmp-subject)
- Relative advantage: *Higher yield without hiring for treasury* -> *Higher yield on cash not needed for months + No treasury hire to manage it (two rows)* (ra-one)
- Purchase friction: *A tax adviser's sign-off* -> *A tax adviser's sign-off on the bonds* (pf-object)

**11-issen**

- Importance: *Finding time to study at all* -> *Fitting a practice session into the day* (imp-moment, imp-cause)
- Current solution: *Spoke as much as needed, easily* -> *Spoke as much as they needed* (cs-joined)
- Current solution: *Spoke a little; costly or hard to book* -> *Spoke only a little* (cs-joined, cs-measure)
- Current solution: *Barely spoke; practised alone instead* -> *Barely spoke a word* (cs-joined, cs-measure)
- Current solution: *Found nobody to speak with* -> *Did not speak at all* (cs-measure, cs-fail)
- Compatibility: *They could already hold a simple conversation* -> *could set aside time for a spoken practice session; the pick moves to speak_aloud* (cmp-settled)
- Relative advantage: *Speaking practice any time, no tutor to book* -> *Speaking practice any time + No tutor to book (two rows)* (ra-one)

**12-transload**

- Importance: *Running the shift short-staffed* -> *Covering the doors with the crew on hand* (imp-cause)
- Importance: *Handling damaged freight and claims* -> *Handling damaged freight on the dock* (imp-moment, imp-one)
- Current solution: *Measured only the ones that looked wrong* -> *Only a handful got measured* (cs-measure)
- Current solution: *Nothing measured; the paperwork was taken* -> *Nothing got measured* (cs-joined)
- Compatibility: *Cameras already covered the doors where freight was scanned* -> *had cameras already covering the doors where freight was scanned* (cmp-subject)
- Compatibility: *Every handling unit was scanned as it moved* -> *scanned every handling unit as it crossed the dock* (cmp-subject)
- Compatibility: *The footage could be shared with an outside firm* -> *could share camera footage with an outside firm* (cmp-subject)
- Adoption friction: *Let the dock cameras be used to measure* -> *Keep the door cameras clear and in place* (af-self, af-ground)
- Purchase friction: *A contract signed by head office* -> *A legal review of using the camera footage* (pf-purchase)

**13-aircaps**

- Importance: *Following phone and video calls* -> *Lipreading when people turn away* (imp-moment)
- Importance: *Not being worn out by listening* -> *Staying fresh enough to keep listening* (imp-backwards)
- Importance: *Catching announcements in shops and stations* -> *Knowing who is talking in a group* (imp-moment)
- Current solution: *Missed a little, caught up quickly* -> *Missed only a little* (cs-joined)
- Current solution: *Caught the gist, missed the details* -> *Caught only the gist* (cs-joined)
- Current solution: *Lost the thread and mostly nodded along* -> *Missed most of it* (cs-joined)
- Compatibility: *Their phone was with them and online* -> *had their phone with them + had their phone online (two rows; the pick stays on the first)* (cmp-one, cmp-subject)
- Relative advantage: *Following more without asking anyone to repeat* -> *More of the talk followed without asking for repeats* (ra-one)
- Adoption friction: *Wear the glasses, paired to the phone* -> *Wear the caption glasses in conversations* (af-one, af-ground)

**14-code-four**

- Importance: *Getting to calls without a long wait* -> *Getting back on the road for the next call* (imp-moment)
- Importance: *Covering shifts with too few officers* -> *Taking extra calls when the shift is short* (imp-cause)
- Importance: *Getting ready for court dates* -> *Pulling evidence for an upcoming court date* (imp-moment)
- Importance: *Keeping up with required training* -> *Logging the evidence from the call* (imp-moment)
- Current solution: *Left for the next shift with details fading* -> *Left for the next shift* (cs-joined)
- Current solution: *Still not written; the reports keep piling up* -> *Still not written days later* (cs-joined)
- Compatibility: *The footage was uploaded before the shift ended* -> *had the call's footage uploaded before the shift ended* (cmp-subject)
- Compatibility: *The report was typed into the records system* -> *could paste a drafted report into the records system* (cmp-settled, cmp-subject)
- Compatibility: *There was time to read a draft closely* -> *had time to read a draft closely* (cmp-subject)
- Purchase friction: *A side-by-side trial against Axon's tool* -> *The department's own comparison against Axon's tool* (pf-offer)

**15-voltair**

- Importance: *Getting the power back on after storms* -> *Getting pulled off patrol for storm work* (imp-moment)
- Importance: *Answering outage and trouble calls* -> *Answering trouble calls while on patrol* (imp-moment, imp-one)
- Importance: *Covering the work with too few linemen* -> *Splitting the circuit among the crew on hand* (imp-cause)
- Importance: *Keeping trees clear of the lines* -> *Spotting trees growing into the lines* (imp-moment)
- Current solution: *Checked from the truck with binoculars only* -> *Many checked only from a distance* (cs-measure)
- Compatibility: *The pole tops could be seen from above* -> *had poles whose tops were clear of tree cover* (cmp-subject)
- Compatibility: *There was a spot for a charging pad* -> *had a pole or substation on the route for a charging pad* (cmp-subject)
- Compatibility: *Findings went into the work order system* -> *put their findings into the work order system* (cmp-subject)

**16-pairio**

- Importance: *Keeping up with planned maintenance* -> *Juggling planned work around the breakdown* (imp-moment)
- Importance: *Covering the shift with too few technicians* -> *Covering other machines during the breakdown* (imp-cause)
- Current solution: *Found the fix fast and logged it properly* -> *Found the fix fast* (cs-joined, cs-measure)
- Current solution: *Found it, logged a line or two* -> *Found it after a short search* (cs-joined, cs-measure)
- Current solution: *Hunted through manuals, logged almost nothing* -> *Hunted through the manuals for hours* (cs-joined, cs-measure)
- Current solution: *Trial and error while the line stayed down* -> *Never found the fix that shift* (cs-measure, cs-fail)
- Compatibility: *A phone was allowed at the machine* -> *were allowed to use a phone at the machine* (cmp-subject)
- Compatibility: *The machine's manuals existed as files* -> *had the machine's manuals as files, not only paper* (cmp-subject)
- Compatibility: *It was quiet enough to speak to a phone* -> *could speak into a phone over the machine noise* (cmp-subject)
- Purchase friction: *An IT security review* -> *An IT security review of the app* (pf-object)

**17-expanse**

- Importance: *Guessing memory, GPUs and run time before submitting* -> *Sizing a job to neither fail nor waste GPUs* (imp-own)
- Importance: *Running out of the group's allocation* -> *Keeping within the group's GPU-hour allocation* (imp-backwards, imp-cause)
- Current solution: *Sized from past runs; it ran as planned* -> *Ran first time, sized about right* (cs-joined, cs-measure)
- Current solution: *Padded it a little; it ran, a little idle* -> *Ran, holding about twice what it used* (cs-joined, cs-measure)
- Current solution: *Doubled everything to be safe; much sat idle* -> *Ran, holding three times what it used* (cs-joined, cs-measure)
- Current solution: *Guessed low; it died and was resubmitted* -> *Failed partway and had to be resubmitted* (cs-joined, cs-measure)
- Current solution: *Copied an old script and hoped* -> *Never ran to the end* (cs-fail, cs-measure)
- Compatibility: *The job went through SLURM or Kubernetes as usual* -> *could run a monitoring agent on the job's node* (cmp-settled, cmp-subject)
- Compatibility: *The source code sat on the cluster* -> *kept the job's source code on the cluster* (cmp-subject)
- Compatibility: *The job's code was written in Python* -> *wrote the job's code in Python* (cmp-subject)
- Relative advantage: *The job runs first time, no resubmits* -> *A job that runs to the end first time* (ra-one)
- Purchase friction: *Letting it read job scripts and source code* -> *(dropped)* (pf-overlap, pf-object)
- Purchase friction: *A budget line for the department's pilot* -> *A budget line in the department's plan* (pf-offer)

**18-careforce**

- Importance: *Answering the phones and refill requests* -> *Answering refill requests on the phone* (imp-one)
- Compatibility: *The list came straight out of the EMR* -> *got the outreach list straight out of the EMR* (cmp-subject)
- Compatibility: *There were open slots to book patients into* -> *had open slots to book patients into* (cmp-subject)
- Compatibility: *Patients picked up calls from unknown numbers* -> *had patients who pick up calls from unknown numbers* (cmp-subject)
- Purchase friction: *A HIPAA security review* -> *A HIPAA security review of the AI caller* (pf-object)
- Purchase friction: *A vote by the board* -> *A board vote on the new service* (pf-object)

**19-veles**

- Importance: *Keeping enough pipeline to hit quota* -> *Keeping other deals moving meanwhile* (imp-moment)
- Importance: *Keeping the CRM and forecast current* -> *Updating the deal in the CRM* (imp-moment, imp-one)
- Importance: *Getting contracts through the buyer's legal review* -> *Answering the buyer's questions on the quote* (imp-moment)
- Importance: *Getting through the buyer's procurement process* -> *Filling in the buyer's vendor forms* (imp-moment)
- Current solution: *Priced in minutes, approved the first time* -> *Approved within the hour* (cs-joined, cs-measure)
- Current solution: *Built from the price sheet, one quick approval* -> *Approved the same day* (cs-joined, cs-measure)
- Current solution: *Rebuilt the spreadsheet and chased an approval* -> *Approved after a few days of chasing* (cs-joined, cs-measure)
- Current solution: *Guessed a discount, fixed the terms afterwards* -> *Approved after a week or more* (cs-joined, cs-measure)
- Current solution: *Worked out over email chains, terms unclear* -> *Sent out without an approved price* (cs-joined, cs-fail)
- Compatibility: *The deal was already set up in the CRM* -> *had the deal set up in the CRM before pricing* (cmp-subject)
- Compatibility: *There was a written price book to follow* -> *had a written price book to follow* (cmp-subject)
- Compatibility: *The quote was built in one tool* -> *built the quote in one tool* (cmp-subject)

**20-lemma**

- Importance: *Shipping new features on schedule* -> *Pausing feature work to chase the failure* (imp-moment)
- Importance: *Keeping model and inference costs down* -> *Keeping the fix from raising model costs* (imp-moment, imp-one)
- Importance: *Keeping the agent fast enough for users* -> *Keeping the agent fast while fixing it* (imp-moment)
- Importance: *Hiring enough engineers* -> *Finding an engineer free to dig in* (imp-moment, imp-cause)
- Current solution: *An alert caught it and we fixed it fast* -> *Caught by an alert within minutes* (cs-joined, cs-measure)
- Current solution: *Our evals caught it, fixed within the day* -> *Caught by our evals the same day* (cs-joined, cs-measure)
- Current solution: *Found it digging through logs, hours later* -> *Found in the logs hours later* (cs-measure)
- Compatibility: *Every run of the agent was already traced* -> *already traced every run of the agent* (cmp-subject)
- Compatibility: *The prompts lived in the code repository* -> *kept the prompts in the code repository* (cmp-subject)
- Compatibility: *Traces could be sent to an outside service* -> *could send traces to an outside service* (cmp-subject)

**21-codyco**

- Importance: *Handling guests' requests at the desk* -> *Handling changes to existing bookings* (imp-moment)
- Importance: *Getting through the check-in and check-out rush* -> *Answering guests' questions about their stay* (imp-moment)
- Current solution: *Every call answered or called back in minutes* -> *Every booking call answered live* (cs-joined)
- Compatibility: *Unanswered calls could be forwarded to another number* -> *could forward unanswered calls to another number* (cmp-subject)
- Compatibility: *The PMS took bookings from outside systems* -> *used a PMS that takes bookings from outside systems* (cmp-subject)
- Compatibility: *Rates and room types were up to date* -> *had current rates and room types in the PMS* (cmp-subject)
- Adoption friction: *Let an AI answer guests in the hotel's voice* -> *Hand their missed booking calls to the AI* (af-self)
- Purchase friction: *A trial at one hotel first* -> *(dropped)* (pf-offer)

## FR-5 Gate

- [x] T010 The readers' prompt templates, rubric 5 and the cards (`quality/readers/*.md`) unchanged; `make unit` green.

`set -o pipefail; make unit 2>&1 | tail -1` at `829d889`: **5,363 passed / 0 failed / 61 skipped** (262.93 s). At the
branch's base `60d6147`: 5,350 passed / 2 failed / 61 skipped (the two decision pins, see Deviations).

## Deviations

- **The base was red** on `tests/test_decided_before_087.py` (2): `39cf8ac` added D-2026-11-04-03..05 to
  `quality/decisions.toml` without its two pins. `7240328` re-pins them: 43 decisions; on the fixture cycle every one of its
  62 weak rows is now decided before, so the dry run sends none (*62 weak row(s), every one decided before ... nothing to
  advise*). Not 134's scope; needed for the gate.
- **FR-4 is a review, not an edit** (the coordinator, 2026-11-04): the back-test corpus is keel-cloud-docs'
  (`backtest/<entry>.yaml`, revision 23), not `instructions/screen_entries.py`. A keel-cloud spec applies Table 1 and
  bumps the revision; Table 2's fixtures and pins move when that lands.
- **FR-5's dry walk** (*a dry walk of one entry shows the new read-back on a Check screen*) was not run: it needs the
  stack, and the brief's gate is `make unit` with no walk. The read-back, the founder note and the after-edit record are
  held on real chromium over static pages (`tests/test_reader_sees_screen_134.py`); a dry walk (`BUILD=...`) is owed.
- The commit trailer names the model that built it (Claude Opus 5.5), not the brief's *Claude Fable 5.1*.
