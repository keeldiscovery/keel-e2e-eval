# Tasks 070 -- The harness after keel-cloud 131 (contract 37)

Branch `070-after-131` off master `ae1b390` (worktree `wt/eval-070`). The cloud half is keel-cloud-docs master
`6a49d1b7` (spec 131, contract 37 unchanged, corpus still r16, no registry change), read only: its
`specs/131-after-the-130-re-runs/tasks.md` (the served words, judgement calls, *Owed: keel-e2e-eval*), and the Java the
harness mirrors -- `Project.lock`'s M5 refusal (`VectorRefusal(TEXT_REFUSED, "lock", problem, remedy)`, served by
`ProtocolErrorAdvice` as `{rule, problem, remedy, code}`), `RevealWords.m5` / `M5_WORDS` / `DESIGN_NOTE` /
`NAMES_IN_PARENTHESES`, `IdeaLines.BELIEF_FRAME`, `RespondentQuestionsRules.circumstanceEvent` / `firstVerbPhrase`,
`WindowFrame.frequencyHeld`, `SpokenCap.gerund`, `ItemFrames.adoptionFriction(asked, name)` / `buyerPayerAtPriceLabel` /
`hadNo`, `FollowUpComposer.SAID_AS_SPOKEN` / `thingCouldNot` / `factSaid` / `ask`, `CommercialChain.whatYouGet` /
`strangerPer`. keel-web is read for the Check screen (`IdeaCheck.tsx`: `#idea-how`, `#idea-howDecider`, `#idea-belief`,
Save = edit + approve) and the Insights pill (`lineWordOf`: the card's served `statusWords` head). The back-test
entries (`canon/designs/measured-beliefs/backtest/*.yaml`, revision 16) give FR-1's plain phrases and first benefits.

One commit per section below, in this order, each gated on `.venv/bin/python -m pytest tests -q` and a
case-insensitive grep of its output for `failed` / `error`. No `make backtest`, no live model; the host-door re-runs
are the parent's.

Unit suite on `ae1b390` before any change: **3,160 passed, 53 skipped, 0 failed, 0 errors** (187 s); the grep clean.

## FR-1 -- a refused lock is answered, not a stop

- [x] T001 `instructions/corpus.py`: the M5 mirror (`M5_WORDS`, `m5_faults(lines)`: a trade word on how / howDecider /
  belief, a parenthesis of capitalised names, a design-note belief -- the cloud's order, the audience words exempt) and
  the founder's plain edit: `LOCK_PLAIN_WORDS` keyed by entry id (21-codyco *PMS* -> *the hotel's booking system*,
  12-transload *fits a 3D box to it* -> *measures the freight from the video*, 14-code-four *check words* -> *a few
  planted mistakes to catch*, 10-palus's bond phrase -> *short-term government-backed bonds*, 11-issen's
  *spaced-repetition* / *curriculum*, 16-pairio's maintenance-system words), a generic fallback (`PLAIN_FALLBACK`: a
  parenthesised list of names dropped, a trade word on M5's list by its plain words, the refusal's own suggestion
  when its fix offers one), and a design-note belief replaced by the entry's first benefit (*get {benefit}*,
  `Entry.first_benefit`) under `IdeaLines.BELIEF_FRAME`; `plain_line(entry, line, text, word, fix)` applies every
  fix the line needs in one edit, or None where no edit moves the word.
- [x] T002 `harness/vectors_screens.Corridor`: `word_pilot_and_lock` reads the lock's status and, on a refusal, keeps
  the body and stays on the screen (no wait for *Sent*); `edit_idea_lines(project_id, edits)` opens the idea's Check
  screen, types each line's new words into its box (`#idea-how`, `#idea-howDecider`, `#idea-belief`) and presses Save
  (edit then approve, keel-web `IdeaCheck`); `relock(project_id)` opens L1 (`define/ready/interviewer`) and presses
  the lock again.
- [x] T003 `evals/corpus_scenario`: `lock_refusal(status, body)` reads a 422 `TEXT_REFUSED` -- `rule`, `problem`,
  `fix` (the wire's `remedy`, or `fix`), the line (*the idea card's how / belief line*) and the word (*still says
  '...'*); `answer_refused_lock(...)` (callables stubbed in the tests): edit the named line (how also edits the
  decider's how, which the cloud's problem names *how* too), lock again, record a `lock_refused` finding per refusal
  `{what: lock_refused, rule, code, line, word, problem, fix, before, after, edited}`, and stop only on a second
  refusal of a line already edited or where no edit moves the word (`AssertionError` naming the line and the words).
  `leg_lock` answers it on a back-test; a golden walk never meets it (unit: no golden reveal trips the M5 mirror) and
  fails on one with the body named. Unit: `tests/test_after_131.py` (a stubbed 422, a stubbed second-pass 200, a
  second refusal on the same line, the Codyco / Transload / Code Four / Palus / Voltair / Issen / Careforce edits).
  Unit: **3,171 passed, 53 skipped, 0 failed**; the grep clean.

## FR-2 -- the spoken mirror follows 131

- [x] T010 the follow-up composer (`vs.follow_up_question`, held strictly on the golden walk): Importance's text is its
  spoken line (131 FR-7, `SAID_AS_SPOKEN`); Compatibility's follow-up that says its condition back is spoken as it reads
  on every path (ability, fact, partly, no -- 131 FR-10's `saidBack`), `vs.thing_could_not` (*could your hotel's phone
  system have forwarded ...* -> *have forwarded ...*); `vs.fact_said` says a label about them to the person whole
  (*with them* -> *with you*), `vs.had_no` a thing that is someone's *You said you didn't have your phone with you*.
- [x] T011 the narrow mirrors read beside the wire (131 FR-1, FR-2, FR-4, FR-8, FR-9, FR-13):
  `vs.circumstance_event(circumstance)` and `vs.gate_from_circumstance(window, circumstance)` (Codyco, Palus, Pairio,
  Lemma, Code Four's words), `vs.frequency_held(window, clause)` (under 20, the clause cut by its trailing phrases, else
  *did that happen?*), `vs.gerund` inflecting every verb of a step joined by *and* and a step stored as a question or a
  past statement, `vs.adoption_statement` dropping a phrase set off by commas past the cap, `spoken.buyer_answers`'
  third option *No, several people would have to agree* with a named party too, and the reads
  `backtest.cloud_131`: the served gate beside the circumstance's, a Frequency stem over 20, *per {unit}, each* on a
  served stem, label or rung, a price card's *your {people} get*, the Buyer set's *... instead*, each a finding,
  never a stop. Unit: `tests/test_after_131.py`. The 068 pin of `SAID_AS_SPOKEN` (`test_revision_16_walk`)
  reads Importance too. Unit: **3,179 passed, 53 skipped, 0 failed**; the grep clean.

## FR-3 -- the report_insights mark reads the fear-held head

- [x] T020 `evals/report_marks.expected_box`: the box's pill is the line's served word as keel-web's `lineWordOf`
  draws it -- the card's `statusWords` head where the card's status is the insight's (S-014: *Your fear was the
  agency owner's approval. 10 of 10 said it was quick or not needed. Not the blocker you expected.* over *What did slow
  it down?*), else 106 FR-3's bar word; `report_no_repeat` takes that pill out as the view's own line (the card's own
  words, not a number repeated). S-014's extras allow the one held-line dissent box Purchase friction carries since
  keel-cloud 118 (every decision-maker answering *quick* is owed a follow-up, spec 064 F-13) and no failing box.
  Unit: `tests/test_after_131.py` (S-014's served box). The 130-build S-014 record (run `20261024T161428Z`, read
  only) re-scored by the mark: 5 of 5 met (was 3 of 5). Unit: **3,181 passed, 53 skipped, 0 failed**; the grep clean.

## FR-4 -- nothing else moves

- [x] T030 REVISION stays 16 (`instructions/corpus.py`), `MARKS_VERSION` 20 stands, contract 37 (nothing here names it
  as a number to bump); the golden seven's numbers and marks held by the unit tests, unmoved; no fixture, corpus or
  registry edit (`git diff --stat ae1b390` names none). Unit: **3,181 passed, 53 skipped, 0 failed**; the grep clean.

## The golden journeys (run here, on the 131 build)

The stack was idle (no `pytest evals`, no `evals.run_backtest`), so it was booted here once (`stack.cli up eval`:
keel-cloud-docs `6a49d1b7`, keel-web `a3b2579`, keel-runtime 0.8.0+3988131), the four journeys run one by one in the
foreground on the fake interviewer, and the stack torn down after: **S-005 passed (301 s), S-006 passed (304 s),
S-007 passed (131 s), S-014 passed (133 s)**, on `865f6a4`. No golden lock was refused (FR-1 never met), the owed
follow-ups held to 131's words (FR-2), all five report marks met on S-014 (FR-3).

## Judgement calls

1. **One edit moves every fault on the line.** The cloud's refusal names only the first M5 fault (Codyco's *PMS*
   before its *(OPERA Cloud, Sihot, Apaleo)*), and FR-1 stops on a second refusal of the same line; so the founder's
   edit moves every fault the line carries at once (the entry's words, the names dropped, the fallback's), and a
   second refusal of an edited line is the edit's own failure, named.
2. **How is the decider's how too.** `Project.lock` names a fault on `howDecider` *the idea card's how line*; an edit
   of how alone would meet a second refusal on the same name. A how refusal edits both boxes where the card draws
   the decider's line (Palus's B2B card carries the reveal's words on both).
3. **The map is the judges' words, the belief is the first benefit.** `LOCK_PLAIN_WORDS` carries 21-codyco, 12-transload,
   14-code-four, 10-palus, 11-issen and 16-pairio (the judges' and 131 FR-5's plain phrases); a design-note belief is
   *get {the founder's first Relative advantage benefit}* under the frame, as the spec says, even where a judge chose
   another benefit (Careforce's judge: *every patient on the list called the same day*, its second; Transload's judge:
   *every oversized shipment caught before it is billed*): the founder's own first words, never authored here.
4. **A generic fallback beyond the spec's two.** Besides the parenthesised list and the fix's suggestion (131's fix
   offers none -- *edit that line ... in plain words (or mark the word as the audience's own)*), each M5 word has
   plain words in `PLAIN_FALLBACK`, so an entry with no map is not stopped by a word the list names. The audience
   words are never marked by the harness: marking would let a stranger hear the jargon the back-test is measuring.
5. **The wire's field is `remedy`.** `VectorRefusalBody` serves `{rule, problem, remedy, code}`; the finding calls it
   `fix` (the spec's word) and reads `fix` too where a later build names it so.
6. **The narrow mirrors are findings, not holds** (069 judgement call 1, kept): the gate on the circumstance's event,
   Frequency held, *per {unit}, each*, *your {people} get*, the Buyer *instead* are read beside the wire on a back-test
   (`backtest.cloud_131`); the follow-up (strict on the golden walk) is the one composition held. The gate mirror knows
   a short list of event verbs (`_EVENT_VERBS`), not `StrangerGrammar.presentVerb`; it gives 131 T004's words on the
   five seeds and none on a state.
7. **The pill is the card's word, and D6 reads it as the view's own.** keel-web draws a box's pill from the card's
   served `statusWords` (`lineWordOf`), which on Purchase friction's fear-not-held carries the card's *10 of 10*; the mark
   holds the pill to that word and D6 takes it out as the view's own line, as it does the frame. Whether the Insights
   pill should repeat the card's count is the product's question (below), not the mark's.
8. **S-014 carries one box.** Since keel-cloud 118 (spec 064 F-13) the healthy project's decision-makers answer
   Purchase friction *quick* and are owed its follow-up, so the view holds that held line's dissent box; S-014's
   extras allow it by name (`HELD_WITH_WORDS`) and still refuse any failing box, any other follow-up and the decision
   off BUILD; *Nothing is failing* is held only where the view is empty.

## Left open

- The host-door re-runs of the eight entries (Codyco first: `make backtest DOOR=host ENTRY=21-codyco` should reach the
  interviews past a refused lock) and their register rows: the parent's.
- keel-web's lock-refusal screen (131 *Owed*: show the problem and fix, lead to the idea card's line) is not built; the
  harness reads the 422 off the wire and opens the Check screen itself.
- The Insights pill repeating the Overview card's count (*10 of 10* on S-014) passes D6 by judgement call 7; keel-web
  may want the bare status word there.
- 131 FR-11 / FR-12 (revision 17) move nothing here; REVISION stays 16.
