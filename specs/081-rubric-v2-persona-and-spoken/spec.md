# Spec 081 -- Rubric version 2: plain to this person, and said aloud

The founder, 2026-10-28, on the readers (spec 078): *"what we should look at is not only the project context but the
location and the persona -- if a question says nautical miles and the person is a mariner, that's perfectly fine; what
is the likelihood that a person in that industry, in that what / where / when, will understand. And the rubric should
check whether our questions and options are AI-avatar friendly; we have guidelines."* Design of record: keel-cloud-docs
`canon/designs/question-quality-rubric-2026-10-28.md` §3 as amended today (R2 rewritten, R6 added, the generating-side
note). No score file is committed yet, so the version moves before the first cycle and nothing is re-scored. Build
after 079 (merged) -- the first cycle must run at RUBRIC_VERSION 2.

## Rules

- **FR-1 `RUBRIC_VERSION` 1 → 2**, and `quality/RUBRIC.md` says what changed and why (078 FR-1's rule): R2's anchors
  rewritten, R6 added. A score file at version 1 is refused by the table by name (none exists; the fixtures move to 2).
- **FR-2 R2 is judged from inside the persona.** The anchors: 2 *yes, in their own words*; 1 *needs a second read, or
  one word they would not use*; 0 *confusing, double-barrelled, or words of another trade*. The reader prompt says in
  so many words that the yardstick is this person -- their trade, their place, their time of life -- never the general
  public: the trade's own words are plain to them, a word from outside the trade is not however common elsewhere. Both
  readers carry it (the founder's trade for the founder-reader).
- **FR-3 The persona is handed before any screen.** Both prompts open with the persona block: for the respondent-reader
  the person the walk took on that link (078 judgement call 6) plus the project's what / where / when as the context
  fields say it (actor, actor_plural, job, circumstance, segment, window, the market's country); for the founder-reader
  the entry's sources and the same context. The block is recorded in the score file's header once, not per screen.
- **FR-4 R6, said aloud.** A sixth criterion on every respondent screen (one wording serves the phone and the AI
  interviewer, so no screen is exempt): the reader is handed the question, the options and the escape as the avatar
  would say them, and keel-cloud `canon/designs/spoken-questions-guidelines.md` §2, §3 and §5 pasted by the runner
  (one source, read from the cloud checkout at the bundle's sha where it exists, else the checkout's), and answers
  whether this person would hear it once and answer. Anchors: 2 *says well: short, one question, the options spoken
  as a list a person can hold*; 1 *one option or clause is a mouthful, a number or symbol that does not say well*;
  0 *cannot be said: a parenthesis, a slash, an abbreviation only the eye reads, two questions in one breath*. R6 is
  scored into the respondent audience's score_pct like the others, with its own `spoken_pct` beside; `looks_stupid`
  gains R6 = 0. The founder-reader has no R6.
- **FR-5 The table.** One more mean column (R6) on respondent rows, `spoken_pct` in the head beside `insights_pct`; the
  weak rule unchanged; the fix location for an R6 zero is *the registry row's wording or the spoken transform* (design
  §1), and for an R2 zero *the registry row, or the instruction gains the trade's words* (the generating-side note).
- **FR-6 The adviser never proposes a special case.** (The founder, 2026-10-28: *"the fix should not be 'let me add
  this if-else in the instruction set'; the main fix should be: is it persona aware?"*) `quality/readers/adviser.md`
  carries the rule (design §5a): a proposal that adds a condition on an industry, a role, a country or a product is
  wrong; the proposal is that the writer is handed the persona and writes in that person's words for every trade at
  once. The adviser's JSON gains `persona_aware: true|false` and the runner refuses to write a proposal with it false
  (it records the refusal in the advice file by row, so the founder sees that a special case was the model's first
  idea and was not taken). A unit test holds a fixture proposal with an *if the people are ...* clause refused.
- **FR-7 Nothing else moves.** R1, R3, R4, R5, G1, G2, the whole-flow questions, the readers' model and door, the
  cycle's commands, `MARKS_VERSION` 21 (the `read` mark reads whatever version the score file says).

## Acceptance

`make unit` green but for the known revision-17 red (master `f111489`: 3,627 / 1 / 53, the one red closed by spec
080): the prompt carries the persona block and the three guideline sections; R6 parsed, folded, refused when missing
on a respondent screen and refused when present on a founder screen; the version refusal; the fixtures at 2.
`make read-screens DRY=1` on the 21-codyco bundle prints the persona block once and R6 in every respondent prompt.
No paid call. tasks.md in 079's shape.
