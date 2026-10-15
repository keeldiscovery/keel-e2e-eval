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
  spoken order, the solution passage's three facts, no spoken founder's word, pilot last, Range served, the dry run
  wrote nothing, heard on every spoken answer, the change pair, the refusal at a low balance, the retry free).
  Unmeasured never passes.

## Judgement calls

1. The speech seam is the only way the eval "talks"; it is a test-build seam in keel-web, asserted absent from a
   production build by one check.
2. The fake's 3 s delay is enough to see RECORDING on the screen; the poll is 10 s, so the leg waits up to 30 s.
3. The B2C short form (S-005) asserts the lock pair, READY and one AI link; the B2B form carries the rest.
