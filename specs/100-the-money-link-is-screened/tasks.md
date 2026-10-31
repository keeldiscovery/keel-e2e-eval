# Tasks 100 -- The money link is screened (and spec 112's addendum: keel-cloud 172's pins)

Branch `100-the-money-link-is-screened` (worktree `wt/keel-e2e-eval-100`, its own `make venv`), off master `88c603d`
(112's docs; 4,383 / 0 / 56). Built by Claude on 2026-10-30. Read only: keel-cloud-docs master (166 and 172 merged;
`1acc3791` with 173 by the end), its `specs/166-.../tasks.md` (the wire) and `specs/172-.../tasks.md`; keel-web master
`a83d846` (144) and the **unmerged** branch `145-the-money-links-screener` (`879ac42`). **No stack, no browser run, no
model, no paid call**: `make eval K=s016` / `K=s006` are the coordinator's. Nothing merged into master; the branch pushed
after every commit, never force-pushed.

**keel-web 145 was not merged** when this was built (keel-web master's head is 144). Built against the wire of 166's
tasks.md and 145's branch as it stands: the text page asks the money link's screener on the same screen as the
decision-maker's (`[data-testid=condition-screen]`, `h1.iv-q`, a radiogroup named by the question, Yes / No, no kicker, no
Back), the reveal after it inside (*Part 1 of 1 · An idea to consider*), and outside the exit (*That's it.*, the page's
own thank-you) with `{outsideSegment: true, answers: []}`; the AI flow asks it on a `kind: "condition"` step. If 145
merges with other ids, `harness/vectors_screens.py` `Interview._condition` is the one place to move.

| Commit | What |
|---|---|
| `08ec703` | FR-2: the walk asks the money link's screener wherever served; the outside counted apart (harness + `corpus_scenario`) |
| `42ac150` | FR-1, FR-3: S-016's consumer leg (ten inside, one outside), `leg_money_screener`; SC8 and SC4 on the FULL link, `SCOPE_MARKS_VERSION` 3 |
| `c3b40bf` | `tests/test_money_link_screener_100.py` (67) |
| `fafd2a1` | spec 112's addendum: Current solution's escape off the served item; the walk sends the code served; `tests/test_current_solution_escape_172.py` (31) |
| the docs commit | this file, `AGENTS.md`'s spec-100 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| master `88c603d` (112's tasks.md; keel-cloud-docs `84b80d86`) | 4,383 | 0 | 56 |
| branch at `c3b40bf` (Job 1), keel-cloud-docs `1acc3791` (173 merged during the build) | 4,449 | 1 | 56 |
| **branch at `fafd2a1` (the last code; the docs commit adds none), keel-cloud-docs `1acc3791`, keel-web `a83d846`** | **4,480** | **1** | **56** |

+98 tests in all: `tests/test_money_link_screener_100.py`'s 67 and `tests/test_current_solution_escape_172.py`'s 31
(4,383 + 98 = 4,480 passed + 1 failed); none removed. **The one failure is not this spec's**: keel-cloud **173**
(`f9314999`, merged into keel-cloud-docs master while this was built) moved `ScaleFour.FRAME` to *... have made your last
{occasion} go better for you, or not?*, and `tests/test_controls_089.py::test_the_question_is_scale_fours_and_the_plain_frame_past_the_cap`
reads that Java source against `vectors_script.BENEFIT_FRAME` (*... have made it go better ...*). Neither file is touched
here; it fails the same on master's code against today's keel-cloud-docs. Left for keel-cloud 173's eval pins.

## Job 1 -- spec 100

### FR-1 -- S-016 opens the consumer money link: one walked outside, the rest inside

- [x] T001 `evals/scope_journey.py` `consumer_money_entry`: 01-countly on its own persona (`SAME_PERSON`, as the file
  records) under `scope: COMMERCIAL` -- the people's one FULL link, no gate. The people: Countly's ten with a delivery in
  the window (inside, `condition: YES`, their commercial picks alone; a gate No has no money answers off the gate, spec
  102 FR-2) and **`OUTSIDE_PERSON` (*Ilse Brandvold*)**, `condition: NO`, last. Refused for any other entry, for a B2B
  seed, and where `vs.money_condition` serves nothing. Countly's context condition is the scripted one (`SEGMENTS`:
  *run one or two sites*), so the served screener is *Do you run one or two sites?*
- [x] T002 `harness/vectors_script.py` `chip_from` mirrors keel-cloud `RespondentQuestionsRules.chipFrom` (the clause
  *are/is/am ...* -> *Are you ...?*, else *Do you ...?*, held to 20 words, else none: E7); `decider_chip`'s clause is
  factored out to `_condition_clause`, its output unchanged. `money_condition(entry)`: `{question, inCodes: [YES]}` on a
  consumer study that serves no gate, None elsewhere (the gate's chip; the B2B decision-maker's `decider_condition`).
  Part 3 is code's at the lock and money alone has no RESPONDENT_QUESTIONS job (`respondent_jobs`), so `chipFrom`'s is
  what is served.
- [x] T003 `scope_journey.leg_money_screener` (after `leg_interview`, consumer COMMERCIAL only) holds
  `money_link_faults` over every person walked: the served link FULL, no gate, `reveal.afterPart` 0, `condition` the
  mirror's, `first_screens` `["condition", "reveal"]`; inside the screener then the reveal and a body of the answers alone
  (102); outside the screener alone, `{outsideSegment: true, answers: []}` 201, the exit, no pilot box. Strict on S-016
  (and `outside == [OUTSIDE_PERSON]`), a finding on a back-test; a person not walked (102) is skipped.
- [x] T004 Counted apart: `corpus_scenario.hold_outside_apart` (from `scope_journey.leg_scoped_report`, every scope,
  after `_await_standings`) holds `outside_apart_faults` -- `StandingsView.outsideSegment` is the number walked outside,
  `people.answered` leaves them out, their People row (`GET people`) carries `outsideSegment: true` and nobody else's
  does, the Pilot tile's served `perLink[PRIMARY].notCounted` says *N outside who the study is for*, and Sent's row draws
  keel-web's `OUTSIDE_SEGMENT_MARK` (*outside the people you described*) under the outside name and not under an inside
  one (`interviews_screens.Interviews.outside_mark`). Strict an assertion, a back-test a finding.
- [x] T005 `evals/test_s016_money_only.py` gains `test_s016_money_only_consumer` (slug `s016-money-consumer`) beside the
  B2B leg, which is unchanged; `make eval K=s016` runs both.
- [x] T006 The AI door: `evals/interviewer_leg.py` `_Walk.screener` is `screener_of` on a FULL link (the gate's chip, or
  the money link's own `condition`), none on the decision-maker's (keel-web 145 FR-3 keeps its AI walk), and the walk
  answers it where the sheet asks it. No AI-door journey walks money alone today, so nothing runs it yet.

### FR-2 -- the walk's money studies

- [x] T007 `vectors_screens.screener_of` mirrors keel-web `conditionOf`. `corpus_scenario._answer_one`'s spec 067 FR-6
  fallback (an outside person on a page that serves no chip is walked inside, named) read `gate.condition` alone, so on
  the money link -- which serves the screener at the top level -- 11-issen's Nikos Ferrante would have been walked
  **inside**: it reads `screener_of` now, and he answers it outside. `not_walked_off_the_gate` already walked an outside
  person once `condition` is served (102 T008); its words (`OUTSIDE_OFF_THE_GATE`) now say why a money link still serves
  none (a project locked before 166, or a condition past 20 words), one 102 pin moved with them.
- [x] T008 `condition_screen_faults` holds the money link too (`_hold_the_screens` calls it wherever no gate is served):
  the screen after the screener inside is `first_screens`' next -- the decision-maker's idea, the money link's reveal.
- [x] T009 `_await_standings` settles at `answered + outsideSegment == invited` (166 FR-3: the outside are never in
  `people.answered`), so a study with someone outside no longer waits its 60 s.
- [x] Inside for every scripted person: already so (`Interview._condition` answers `inCodes[0]` for anyone in the
  segment); the corpus's people are inside by construction.

### FR-3 -- marks: `SCOPE_MARKS_VERSION` 2 -> 3

- [x] T010 **SC8 *the money link screens***: on money alone's FULL links `condition` is the mirror's (none where the
  context carries none), no gate, the first screen drawn the screener (or the reveal with none), an outside person drew
  the screener alone; where a gate is served the link's own `condition` is absent; B2B money alone (no person's link)
  is met with its why. `record_of` carries `screens`, `outside`, `money_condition`.
- [x] T011 **SC4 reads the FULL link's `reveal`** where it read `idea` (101's *what the spec got wrong* 5: only the
  decision-maker's link serves `idea`), and holds no outside person to the card they never reach. Without it the
  consumer S-016 could not be strict.
- [x] Pins moved: `test_study_scopes` (7 -> 8 marks, v3), `test_founder_feedback_073` (v3). `MARKS_VERSION` (24) does not
  move: the scope marks are their own ruler.

### FR-4 -- nothing else moves

S-015 (its gate's chip; SC8 only checks no top-level `condition` beside it), S-016's B2B leg, the decision-maker's
screener legs (`leg_outside_decider` unchanged; `condition_screen_faults` gives the same answer on a COMMERCIAL_LINK,
pinned), the instruction screens, the corpus.

## Job 2 -- spec 112's addendum (keel-cloud 172's pins)

- [x] T012 `instructions/spoken.py`: `handed_off_of(served)` reads the list writer's call off the SERVED item's escape
  (`{code, label}`, the escape alone, or its code / label): False where it is `cant_recall` / *I can't recall*, True for
  another, None where nothing is served. `item_escape` / `served_escape` take `served=` and on Current solution return
  `CANT_RECALL_ESCAPE` (*I can't recall*, said *Or say you can't recall.* through `said`) where the call was false, the
  registry's *Someone else did it* otherwise -- **with nothing served, a list with no call** (every caller before this, so
  every pin stands). No other dimension reads `served`. S6 hands the composed item's own label, so the record may carry
  either way out, each with its own spoken line.
- [x] T013 The walk sends the code served: `vectors_script.served_escape_picks` re-expresses a person's Current solution
  escape (`SOMEONE_ELSE_CHECKS` / `CANT_RECALL`) to the served item's code, each named (`ESCAPE_SENT_AS_SERVED`);
  `_answer_one` runs it before the items are held, so the strict *unoffered* check and the body agree with the page.
- [x] The pins of lists with no call stand and are held: `tests/test_follow_up_ladder.py:172` (`SOMEONE_ELSE_CHECKS`
  apart), `tests/fixtures/corpus/10-fixture-b2b.yaml:212,381` (`someone_else_checks`, no `handed_off`). No price or
  contract pin moves.
- [ ] `tests/fixtures/gallery/expected-interview-fresco.json:78` (*Someone else does the checking*): stale either way, as
  the addendum says; not touched (the gallery pins a recorded run) -- re-record after the next screen.

## What the spec did not foresee

1. **S-016 had no person's link to screen.** S-016 is Countly *B2B* money alone, where keel-cloud 133 FR-4 issues the
   decision-maker's link only, and 166 serves the person's screener on a **consumer** money link alone (166 *not
   foreseen* 3). FR-1's *one inside, one outside* needs a second, consumer project: built as S-016's second test on
   Countly's own persona, ten inside (the entry's own, so the standings mean something) and one outside -- the B2B leg
   untouched.
2. **FR-1's *the six money questions*** are four on Countly's consumer link (Existing sacrifice, Price, Buyer and payer,
   Commitment: `plan_keys(seed, 3, PRIMARY)`; Purchase friction is B2B only, and Countly's consumer plan asks no Ability
   to pay); the leg holds what is served, not a count.
3. **The outside body is `{outsideSegment: true, answers: []}`**, not `{outsideSegment: true}` alone: keel-web 145 (as
   127 and 096) sends the empty list, the cloud reads it as none (166's *anything beside it* is a 422 for a non-empty
   answer), and the harness has always expected it (`PersonInputs.response`). Held as the page sends it.
4. **The Pilot tile draws no `notCounted`**: keel-web's `pilotTileLine` reads the per-link counts alone, so *counted
   apart on the Pilot tile* is held on the wire (`StandingsView.pilot.perLink[].notCounted`); the drawn words for an
   outside person are Sent's `OUTSIDE_SEGMENT_MARK` (and the answers popup's), which the leg reads.
5. **SC4 had to move with SC8** (FR-3 named one row): on a consumer money study it read `idea`, which the FULL link never
   serves, so every consumer money walk recorded a false SC4 (101's debt).
6. **The 067 FR-6 fallback would have walked the outside person inside** on every back-test with a condition under
   COMMERCIAL (11-issen); FR-2 needed that one line as much as the new code.
7. **keel-cloud 173 merged into keel-cloud-docs master mid-build** and broke one eval pin (above); not this spec's.
8. **Unrun**: no `make eval` was run (the brief forbids the stack). The consumer leg is held on doubles only:
   `_answer_one` walks the outside person to the exit strictly on a fake page, and the seed's bodies and the marks are
   pure; the browser walk of the ten inside on a real page is `make eval K=s016`'s, on keel-web 145.
