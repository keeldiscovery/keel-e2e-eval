# Spec 044 -- contract 16 and the AI interviewer journey

The keel-e2e-eval half of keel-cloud 094 (*The pre-rendered AI interviewer*: contract 16, `InferenceCharge` 9, document
22) and keel-web 069. Inputs: 094's *What keel-e2e-eval must do*, `canon/designs/ai-interviewer-prerendered-2026-10-15.md`
(the spoken order, decisions 1-10), and 069's page objects. The stack runs keel-cloud's **fake renders** (a 1-second
mp4 per clip, 3 s virtual delay) and the **fake transcriber**; **no vendor is called and no money is spent**; the one
live render test lives in keel-cloud and is not run here.

## What moves

- FR-001 **Contract 16 and charge v9 where this eval reads them.** `price_version` 9 on every HOLD read by
  `stack/ledger.py`; the register's `formatUsed`; `LockBody.interviewer`; the new refusal codes in `harness/`. Routing
  and `MARKS_VERSION` unchanged (the instruction eval's ruler measures the questions, not the recording).
- FR-002 **The interviewer leg** (`evals/interviewer_leg.py::leg_interviewer`), on **S-006** (`05-paidly`, B2B) after the
  contacts leg, and the short form on S-005 (B2C), on the wire and through the screens:
  1. the lock is sent with `interviewer: {face: TITO}` (the screen: L1's carousel, Tito tapped, "Lock and record the
     interviewer"); the receipt carries `interviewer.status RECORDING`; the ledger holds **one** `INTERVIEWER_RECORDING`
     HOLD + SPEND pair of 400 beside the lock's jobs; no price word on L1 (page object asserts the absence);
  2. the walkthrough's frame 2 names Tito (first visit) and is skipped on the second founder (S-010 stand-in);
  3. Sent's persona line reads RECORDING with a progress "k of N"; "Try it yourself" is disabled; `POST invitations
     {format: AI_INTERVIEWER}` is **409 `INTERVIEWER_NOT_READY`**; a TEXT link is made;
  4. the fake completes: `GET interviewer` READY within 30 s; the line reads "Recorded today at …" with "Change who
     asks · 400 AI credits"; **the clips**: per role, kinds in the order OPENING, PROBLEM, ITEM…, SOLUTION, ITEM…,
     COMMERCIAL, ITEM…, PILOT, THANKS; the SOLUTION script contains the idea's name, its claim and its belief line; no
     clip's script contains the founder's `word.pitch`; the DIDNT_CATCH clip exists once per role;
  5. `GET interviewer/try/{roleId}` serves the Interview with `interviewer` and `tryRun`; the dry-run page plays the
     opening (the fake clip) and End; **no row moved**: no invitation, no response, no pilot, no ledger entry;
  6. an AI_INTERVIEWER link is made; the stranger's `GET interview` carries `interviewer` with clip URLs that answer
     **206 to a Range request** and 404 for a clip of another project; the page answers all seven kinds through the
     speech seam (`window.__keelSpeech`), including one miss ("31" on 0-30 -> the didn't-catch clip, then "two"), one
     ordinal, one "all of them", one typed field value (Amount 200), and the pilot Yes on the sheet; `POST response`
     carries `heard` / `how` on every answer and `format AI_INTERVIEWER`; the register's row shows `formatUsed`;
  7. a CHOICE link: the intro offers both; "Answer in writing" posts `format TEXT`;
  8. the founder changes the face to JUDY: the ledger gains an `INTERVIEWER_CHANGE` 400 pair; the line returns to
     RECORDING then READY with Judy; at a balance below 400 the change is **422 `INSUFFICIENT_CREDITS_FOR_INTERVIEWER`**
     and the popup shows the server's words;
  9. a seeded fail-once clip (the fake's seam) is retried by the recorder and READY still arrives; the retry wrote no
     ledger row.
- FR-003 **Marks** (`evals/interviewer_marks.py`, IM1-IM12: one recording pair per lock, no price on L1/S1/S2/S3, the
  spoken order, the solution passage's three facts, no spoken founder's word, pilot last AND asked on every AI interview with its Yes landing in the overview's pilot count, Range served, the dry run
  wrote nothing, heard on every spoken answer, the change pair, the refusal at a low balance, the retry free).
  Unmeasured never passes.

## Judgement calls

1. The speech seam is the only way the eval "talks"; it is a test-build seam in keel-web, asserted absent from a
   production build by one check.
2. The fake's 3 s delay is enough to see RECORDING on the screen; the poll is 10 s, so the leg waits up to 30 s.
3. The B2C short form (S-005) asserts the lock pair, READY and one AI link; the B2B form carries the rest.

## Inputs as built

keel-cloud-docs master **`a0b3759`** (094 merged at `78c90b6` -- contract 16, `InferenceCharge` 9, document 22 -- then
095, *read on arrival*, the 095 worktree's `ee86d1e`, the same code; `./gradlew check` 1,568 tests, 0 failures, run on an
export of it) and keel-web master **`d23895f`** (069 merged, branch head `df6841f`). The stack runs keel-cloud's fakes
(renderer 3 s, poll 10 s -- not sped up) and serves keel-web with `vite --mode test`.

## Judgement calls (implementation)

148 on are this spec's (129-147 are spec 043's). Each is the simplest reading that keeps the journeys green where the
inputs are silent, and each can be reversed alone.

148. **The interviewer is recorded after the lock, on Keel's door, through `POST interviewer/face`.** The journeys'
     founder is on their own AI (the scripted runtime), and contract 16 records nothing for an own-AI lock; on Keel's
     door the lock's RESPONDENT_QUESTIONS job goes to Keel's own AI, which has no key on this stack, so no Keel's-door
     lock reaches READY. So `leg_lock` holds the own-AI L1 (one line, *Lock and approve*, no carousel, no `interviewer`
     on the receipt) and the leg stands the founder on Keel's door (spec 043's stand-in, keyed `e2e-eval:044:`) and
     records Tito the way contract 16 gives a locked project with none -- NOT_RECORDED, *Record the interviewer*, the
     popup, *Record Tito* -- which keel-cloud charges as `INTERVIEWER_RECORDING` (its call 19). Reversed in a `finally`.
149. **The founder's word is written after the lock** (`PUT word`, legal after the lock; the incentive and the pilot
     kept as stored): no corpus founder writes one, and IM5 needs a word to hold unspoken. One fixed sentence, composed.
150. **The stranger's walk waits for its answer's response**, not the request leaving the browser: the last
     decision-maker's done screen has no heading of its own, so the walk returned with the POST in flight and S-006's
     standings read 7 of 8 once. The walk now asserts 200/201 (043 call 147's shape, for the answers).
151. **The journeys' reading step is door-aware** (keel-cloud 095): on Keel's door nothing is pressed, the newest batch
     and any after it end DONE, a founder's `POST readings` is 409 `READING_IN_PROGRESS` / `NOTHING_TO_READ` (named in
     `rule`, not `code`); on their own AI with the agent connected before the answers nothing reads on arrival (095 call
     14), so S-005 / 006 / 007 keep asking on the wire -- which is the coordinator's own-door rule. No journey here runs
     on Keel's door; the branch is there for one that will.
152. **The leg leaves nothing unread.** Its answers are read on arrival on Keel's keyless door and fail; 095 FR-D then
     reads them at the next agent connect -- S-007's runtime, on S-007's script, which spent S-007's readings on them
     and moved S-007's standings (found once). So the leg answers as the *last* readable corpus person (the scripted
     executor repeats its last INTERPRET entry once spent) and, back on the own door with S-006's runtime connected,
     reads what is left (`POST readings`, DONE, then 409 `NOTHING_TO_READ`).
153. **The stack serves keel-web in test mode** (`mode` in `stack/vite.eval.config.ts`, `EVAL_WEB_MODE` overrides), as
     keel-web's own e2e does, for the one seam; nothing else in keel-web reads the mode. The production build's
     absence of the seam is held by one check on keel-web's source (`tests/test_interviewer_screens.py`): every read of
     `window.__keelSpeech` sits under `import.meta.env.MODE === "test"`.
154. **The Let-them-choose link's intro is held on screen and its answer in writing goes on the wire**: *Answer in
     writing* is the text player, which every journey walks already, and the eval's text page object starts from the
     text link's own *Begin*.
155. **The short form answers its AI link too** (judgement call 3, widened): the consumer link carries the cost total, so
     S-005 is where the field is typed (*Amount*, 30) and the price band said; S-005 owes IM1, 3-7, 9 and 13.
156. **The answers are the corpus person's, said the way a person would**: the gate aloud, the story typed, the first
     single choice by ordinal, the first number a miss (*31*, outside every range here -- the didn't-catch clip, *"A
     number from 0 to 3, please."*) then the number in words, pick-two tapped, the advantages *all of them* when they are
     all the person's, the rest by their options' own words, a cost total typed into the field, the pilot ask tapped
     Yes. The page's one `POST response` is held to the person's closed answers item by item.
157. **The dry run stops at End** (keel-web 069 FR-007: stoppable at any point; on a try run End ends with *Nothing was
     stored.* and asks no pilot): the opening plays on the one `<video>`, one answer aloud, End. The founder's route is
     loaded again after *Try it yourself* so the seam's init script runs.
158. **Frame 2 is held on a replay**: W1 first plays at `leg_invite`, on the own door before anything is recorded (068's
     wording minus the credit words); after READY the leg presses *How it works* and holds frame 2 *Tito asks your
     questions*. W1's once-per-account rule stays `leg_invite`'s (043 call 141); no S-010 stand-in was built.
159. **L1's no-price rule is held on L1 revisited on Keel's door after the lock** (the carousel, disabled), the only
     Keel's-door L1 this stack can draw; it checks Judy while Tito asks (DRIFT #87, stepped round).
160. **IM7's "another project" is another role's clip** on S-006 (an unknown id on S-005): the respondent's route serves
     only the link's role's clips (keel-cloud call 29), and no second project has a recording in the same run.
161. **IM3 reads keel-cloud's order as composed**: the gate first in part 1 with its story prompt as its follow-up, the
     commercial link opening on the idea (SOLUTION, no items) before the money side, DIDNT_CATCH once a role, last.
162. **IM4 holds the solution passage to the three lines' words** (the name whole, 80% of the claim's and the benefit's
     content words): keel-cloud reads the reveal's lines as written (*"Imagine {name}. {how} {belief}"*, its call 10),
     not FR-B's template.
163. **IM9 is *heard on every spoken answer*** (FR-003's words): a value typed into a field carries none (DRIFT #89).
164. **IM13 is born here** (the coordinator's ledger mark after 095): every reading or brief HOLD of the leg says why --
     `read-on-arrival:<invitationId>`, `brief:after-batch`, `retry:<n>:<parent>` -- at most three attempts a reading.
     `INTERVIEWER_MARKS_VERSION` stays 1: no run scored it before.
165. **IM12 is unmeasured, never passed** (DRIFT #86): the fake's fail-once is Java-only; nothing is faked.
166. **Contract 16 where the contacts leg reads it**: the AI interviewer on a project with no recording is 409
     `INTERVIEWER_NOT_READY` (CM12) and every HOLD is `price_version` 9 (CM2 / CM3) -- `CONTACTS_MARKS_VERSION` 2;
     Send more's rows are *Text only* and the greyed words `recording` / `not recorded` / `needs Keel's credits`.
167. **keel-cloud's clips live under the stack's own `runs/.stack/clips-<profile>`** (`KEEL_CLIPS_DIR`): the default
     `./data/clips` is relative to keel-cloud's checkout.
168. **A link made after an arrival reading is made twice when the first is refused** 409 `concurrency` (DRIFT #88),
     in a step named for the entry; Send more is pressed for the format it is asked for (069 checks the AI interviewer
     first once recorded).
169. **`MARKS_VERSION` stays 19** and routing is unchanged (FR-001): no model turn moved.

## Results

- T001 baseline, nothing changed: `make unit` **1,912 passed / 53 skipped**; S-005 / 006 / 007 **3 passed** (391 s) vs
  keel-cloud-docs `47dd816` + keel-web `df2e97a`.
- The wire phase vs `78c90b6` (094) + keel-web `df2e97a`: 3 passed (458 s); vs `a0b3759` (095) + `df2e97a`: 3 passed
  (419 s).
- **Runs of record**, keel-cloud-docs **`a0b3759`** + keel-web **`d23895f`**, `make down` then a fresh database each:
  **3 passed** (498 s; bundles `runs/20261015T2309*` to `runs/20261015T2315*`) and **3 passed** (506 s;
  `runs/20261015T2318*` to `runs/20261015T2324*`). Interviewer marks **12 of 12** on S-006 (IM12 unmeasured) and **8 of 8**
  on S-005 each time; the contacts marks 13 of 13 and 1 of 1; DRIFT #85's, #87's and #88's steps firing on every S-006.
  The first recording READY in 9-12 s, the change in 12 s, on the fake's 3 s and the 10 s poll.
- `make unit` **2,035 passed / 53 skipped**.

## DRIFT

- **#84 RESOLVED** by keel-cloud 095 for Keel's door (`a0b3759`); the own door keeps asking for readings (095 call 14).
- **#85** keel-cloud: the batch refuses an own-AI founder's AI link 409 `INTERVIEWER_NOT_READY`, not 422
  `INTERVIEWER_NEEDS_CREDITS`.
- **#86** keel-cloud: the fake renderer's fail-once is Java-only; step 9 / IM12 cannot be driven.
- **#87** keel-web: L1 revisited after the lock checks Judy while Tito asks.
- **#88** keel-web with keel-cloud 095: a link made after an arrival reading is refused 409 `concurrency`, the server's
  words in the popup.
- **#89** keel-web: a value typed into the field carries no `heard`.
