# Spec 046 -- The founder's staging feedback of 2026-10-16: marks and journeys

The eval half of keel-cloud 097 (contract 17) and keel-web 070. The stack runs the fakes; no model, no vendor, no money.

## What moves

- FR-001 Contract 17 where the eval reads it: `Interview.language`, `InterviewerFace.pronoun`, the two refusals, the batch
  route's 422 (DRIFT #85 closed); `price_version` unchanged.
- FR-002 **Marks** (`evals/feedback_marks.py`, FM1-FM6, unmeasured never passes): FM1 no calibration list item names a
  role or person the founder did not name (the role-word list of 097 against the corpus person's seed, Answer and
  persona roles); FM2 the Importance list is the own item plus exactly the difficulties the corpus Answer named; FM3
  Keel's base query carries no industry; FM4 the idea's name equals the corpus seed's product name when it has one,
  else the Check screen demanded one and the journey typed it; FM5 an AI-interviewer answer advances without a
  "Next question" step (no `thinking` phase longer than 1 s between a resolved answer and the next clip's `play`);
  FM6 a typed field answer carries `heard`.
- FR-003 **Journeys**: the Importance Check screen with two others (and once with one, asserting the one-more ask);
  the idea Check screen's name field; the persona step without the link; the pick page's select-all; no Copy button;
  the AI leg's flow without the Next-question taps; the batch route's 422 on own-AI.
- FR-004 **DRIFT**: #85, #87, #88, #89 closed with the shas; anything new recorded.

## Judgement calls

1. FM1's role-word list is copied from 097 so both sides refuse the same words.

## Inputs as built

keel-cloud-docs master **`3002978`** (097 merged; exported to the scratchpad and served from there, the same tree as the
097 worktree's `8060a7e`; contract 17, `CONTRACT_VERSION` 17, document 23) and keel-web master **`752e873`** (070 merged,
branch head `7d72b3a`), served `--mode test` for the speech seam (spec 044 call 153). The wire half was built against
keel-web 070's worktree at `785cc52` / `f52fed3`. No model, no vendor, no money; the local profile only.

## Judgement calls (implementation)

173 on are this spec's (148-169 are 044's, 170-172 045's). Each is the simplest reading that keeps the journeys green
where the inputs are silent, and each can be reversed alone.

173. **FM1's role words are read from keel-cloud's own export** (`common.role_words` in the run's `export/`, 097 call 9),
     and restated once in `harness/vectors_script.py` (`ROLE_WORDS`, `role_pattern`) for the script's first drafts; a
     unit test holds the two equal and ports 097's `RoleWordsTest` cases. The founder's own words FM1 admits are the four
     context fields, the two seeds, the persona's roles (the actor, the decider) and **that dimension's Answer** --
     narrower than `L6`'s allow-list (which also takes the confirmed mechanism card and every saved list, 097 call 6):
     the eval holds the words the founder typed. Every drafted list is read off `GET calibration` -- the slice's first
     draft and the redraft from the Answer -- 14 to 16 lists a journey.
174. **Importance's first draft is the own item alone, and its Answer names the others alone** (097 call 10): the own
     item is the problem itself, code's, locked first, so the composed Answer (r11 records no Answer) is the other
     difficulties' labels; FM2 reads the redraft against exactly those.
175. **A first draft leaves out an item naming a role the founder has not yet written** (`vs.first_draft`): `L6` reads
     every draft, and before the Answer the founder's words hold no *owner* or *finance* -- 05-paidly's Purchase friction
     drafts *A security review* alone and the agency owner and finance arrive with the Answer's redraft (found on the
     wire run: COMMERCIAL's first draft refused, the repair turn unanswerable). An item is dropped, never replaced; a
     list left empty is refused by name.
176. **Every founder names the idea** (097 F7, call 14): no r11 solution seed yields a name (`vs.seed_idea_name` restates
     `IdeaName.fromSeed` and a test says so of all seven), so S-005 and S-007 type the entry's short name on S2 and
     S-006 its own *Invoice payout service* (spec 042 call 117 kept). Before typing, the wire is held to the refusal:
     `what` null, approve and an empty name 422 `IDEA_NAME_REQUIRED`, nothing written. `NAME_ON_THE_WIRE` (a `PUT idea`
     before S2) was the stand-in until keel-web 070's S2 and is off.
177. **The Check screen with two others, and once with one, keeps the corpus's lists** (FR-003): 01-countly's Answer
     names one other difficulty (*yours + 1*, the one-more ask, Save refused 422 `ONE_MORE_NEEDED`, a line opened), and
     05-paidly's two (*yours + 2*, no ask, Save on); the founder types the rest of their own list on the Check screen,
     so the list saved -- and every stranger's pick -- is the corpus's five (`IMPORTANCE_NAMED`, COMPOSED). FM2 counts
     the typed rows as the founder's: saved = Keel's redraft + what was typed.
178. **Own + 2 is saved on the wire** (`_importance_needs_three`, every journey, after the PROBLEM stage): own + 1 is 422
     `ONE_MORE_NEEDED` (*name one more difficulty*) and moves no revision; own + 2 is 200 and its belief reads *out of
     three*; the founder's own list is saved again (*out of five*, the corpus sentence) and the page reloaded. No screen
     saves a list of three, because no corpus list is three.
179. **FM3 is owed on S-006 alone**, the one journey that opens Contacts (on Keel's door, spec 043's stand-in): every
     kind's base query carries an empty `categories`. S-005 and S-007 leave it unmeasured.
180. **FM4's demand is the wire's refusals plus, when S2 is walked unnamed, the screen's** (the empty box, its
     placeholder, Save off); FM4 fails a served name, an unrefused approve, a name over five words or a stored name that
     is not the one typed.
181. **FM5 reads a timeline the page keeps itself** (`interviewer_screens.FLOW_TIMELINE`, an init script beside the
     speech seam): every `data-phase` of `ai-stage`, every `play` of the stage's video and every press of `ai-next` with
     its words. A *thinking* span is timed from its start to the next clip's `play`; a span ended by a press (*Finish* on
     the pilot ask, which 070 keeps) is not the flow's. Owed on S-005 and S-006 (the two AI links). Measured spans are
     ~500 ms (keel-web's `ADVANCE_MS`).
182. **FM6 is owed where a field was typed** -- S-005's cost total (*Amount*); S-006's AI person is asked no field, so it
     is unmeasured there. IM9 is left as spec 044 wrote it (*heard on every spoken answer*); `INTERVIEWER_MARKS_VERSION`
     stays 1.
183. **DRIFT #85, #87, #88 are asserts now**: the own-AI batch 422 `INTERVIEWER_NEEDS_CREDITS`; L1 after the lock ticks
     the recorded Tito; a Send-more link refused 409 `concurrency` is retried by keel-web itself (the page object keeps
     every batch response of the one press, and the step holds the retry to 201 with no server sentence drawn). #89 is
     FM6. #86 stands (IM12 unmeasured).
184. **The pick page's tools are held on S-006's first page of names**: *Select all* ticks the 25 and the button reads
     *Save 25 picked ... · 300 credits*, *Clear* unticks them (*Save 0 ... · 0 credits*, off); a page of 25 draws no
     pager (the pager needs more than 25 waiting, which no fake search here fetches); C3 draws no *Copy as a new
     dataset*.
185. **F8 is held on the mechanism card** (the link lived there, not on the persona step): its text carries neither *Someone
     else would use it* nor *Who would use it instead?*.
186. **`FEEDBACK_MARKS_VERSION` 1, and `MARKS_VERSION` stays 19**: 097 moved `founder-lists.md` (the list rule) and the
     mechanism contract (`idea_what` gone) -- a subject change, which earns a screen on the founder's word
     (`WHY=instruction:founder-lists.md`), not a ruler change; nothing here runs the instruction eval.

## Results

- T001 baseline vs `3002978` + keel-web 070 at `785cc52`, nothing changed: `make unit` 2,032 passed / 57 skipped; S-005 /
  006 / 007 all failed at PROBLEM's first calibration draft (097 call 10; the repair turn the script cannot answer) --
  before any approve. With the first drafts fixed, every journey met IDEA_NAME_REQUIRED at S2, as foretold.
- The wire half vs `3002978` + keel-web `f52fed3`: S-007 passed; S-005 / S-006 passed every leg up to the AI interviewer's
  stage (070 F1 had removed *Next question*). The screen half vs the same: 3 passed (553 s).
- **Runs of record**, keel-cloud-docs **`3002978`** + keel-web master **`752e873`** (branch head `7d72b3a`), eval
  `5e027f6`, `make down` then a fresh database each: **3 passed** (498 s; bundles `runs/20261016T0357*` to
  `runs/20261016T0403*`) and **3 passed** (512 s; `runs/20261016T0406*` to `runs/20261016T0412*`). Feedback marks: S-005 5 of
  5 (FM3 unmeasured), S-006 5 of 5 (FM6 unmeasured), S-007 3 of 3 (FM3, FM5, FM6 unmeasured) each time; FM5's thinking
  spans 502-511 ms. Interviewer marks 12 of 12 on S-006 (IM12 unmeasured, DRIFT #86) and 8 of 8 on S-005; contacts marks
  13 of 13. The batch's 409 `concurrency` behind an arrival reading met keel-web's silent retry once on each S-006 run.
- `make unit`: **2,074 passed / 57 skipped** (2,032 / 57 at T001: 36 feedback-mark tests, four more vectors-journey
  tests, the rest the page objects' new calls).

## DRIFT

- **#85 RESOLVED** by keel-cloud 097 (`3002978`); **#87, #88, #89 RESOLVED** by keel-web 070 (`752e873`, branch head
  `7d72b3a`). #86 stands.
- **#90 new** (keel-cloud, one field wide): before the founder names the idea, `GET idea` serves `what` null and
  `shortName` the mechanism card's model-written short name.
