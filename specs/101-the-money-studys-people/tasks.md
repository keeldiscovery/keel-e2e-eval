# Tasks 101 -- The money study's people: the person's link opens with the idea card, and a B2B money study has only the decision-maker's link

Branch `101-the-money-studys-people` (worktree `wt/keel-e2e-eval-101`), off master `705c7a5` (the spec commit). Built by
Claude Opus 5.5 on 2026-10-30. Read only: keel-cloud master `35dfb74f` (`InterviewComposer.java`: the money study's
person link, `StudyScope.servesGate`, `Invitation.awaitsReading`), keel-web `466178a` (`interviewAnswers.ts`
`screensOf`) and its spec 145, and the two bundles named in the spec from the main checkout's `runs/` (nothing under
`runs/` touched). **No browser, no stack, no paid call**: the two `make quality-walk` runs of the acceptance are the
coordinator's, after the merge. Nothing merged into master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `6304f1c` | FR-1: the money study's person link opens with the idea card, the screener first wherever it is served, and nobody is read on money alone |
| `b36f35f` | FR-2: a B2B money study sends the decision-makers alone, the PRIMARY people recorded as not on this study |
| the docs commit | this file, `AGENTS.md`'s spec-101 paragraph |

## Unit (the gate)

`make unit` on the live checkouts (keel-cloud-docs as configured, the back-test files read from
`canon/designs/measured-beliefs/backtest/`):

| | passed | failed | skipped |
|---|---|---|---|
| 096's tasks.md record (master `18f30c3`) | 4,003 | 0 | 53 |
| **master `705c7a5`, re-measured** | **4,003** | **0** | **53** |
| branch at FR-1 (`6304f1c`) | 4,030 | 0 | 53 |
| **branch at FR-2 (`b36f35f`, the last code; the docs commit adds none)** | **4,048** | **0** | **53** |

The +45 are this spec's: `tests/test_money_study_people_101.py` (45: FR-1 27, FR-2 18); 082's
`test_08_fresco_under_all_and_commercial_is_every_person_in_the_file` was re-pinned in place (renamed
`..._under_all_is_every_person_in_the_file`, money alone now the deciders), so it adds none.

## FR-1 -- the idea card where it is served first -- `6304f1c`

Stop: `runs/20261030T152257Z-backtest-13-aircaps` (COMMERCIAL), seq 115 -- `waiting for locator("h1.iv-q")`, 20 s. The
failure's `page.html` is the card: kicker *Part 1 of 1 · An idea to consider*, `reveal-problem`, `.iv-card`, the bridge
*The next questions are on the money side.*, Continue; seq 113 recorded `kind: FULL` with part 3's five items.

- [x] T001 `harness/vectors_screens.py:2255` `first_screens(interview)`: keel-web `screensOf`'s head off the served
  interview -- `condition` wherever `Interview.condition` is served (any kind), `idea` on a COMMERCIAL_LINK, `gate` on a
  FULL link with one, `reveal` where a FULL link's reveal precedes its first served part.
- [x] T002 `:2284` `reveal_opens(reveal, part, *, revealed)`: before `part` when not walked yet and `part >
  reveal.afterPart` (money alone's `afterPart` 0 before part 3; the first part after an unserved one, as keel-web).
- [x] T003 `Interview.walk` (`:2387-2394`, was master `:2346-2351`): the screener and the decision-maker's idea read off
  `first_screens` -- the screener on any kind (keel-cloud 166 / keel-web 145, not built yet: walked as soon as served).
- [x] T004 `Interview._items` (`:2740-2746`): before each part, `reveal_opens` walks the card with `_idea(screen=
  "reveal")`; the after-part reveal (`:2816-2818`) is unchanged but for `not revealed`. `_idea` (`:2575`) takes the
  screen's name (keel-web's: `reveal` on a FULL link) and records kicker, card, question, problem as before.
- [x] T005 Beyond the spec, the next stop on the same walk: `harness/vectors_script.py:1383` `read_owed(entry, name)` --
  readable **and** the study serves the gate. `evals/corpus_scenario.py` `_read` (`:3697`, was master `:3659`'s
  `readable_people`) asks it. On money alone no gate is served, no story typed, keel-cloud's `Invitation.awaitsReading`
  is false, and the own-door path's `POST readings` is refused `NOTHING_TO_READ` until its 45 s assert -- 13-aircaps has
  sixteen readable people in the file, so the walk would have stopped at Harriet Coleman's reading.
- [x] T006 Tests (27): the aircaps shape; kind × gate × idea × reveal (COMMERCIAL_LINK with / without idea, FULL money
  alone, FULL with a gate and the reveal after part 1, the problem study, `idea` on a FULL link not walked); the screener
  first on all three shapes and a gate's own screener left to the gate; `reveal_opens` (8 cases); `_items` on a page
  double (money alone's card once before part 3, the solution's reveal after part 1 as before, none on the
  decision-maker's link); `walk` reads `first_screens`; `read_owed` per scope and the `_read` source.

## FR-2 -- a B2B money study sends the deciders alone -- `b36f35f`

Stop: `runs/quality-walk/20261030T135615Z-20261030-fcec453/17-expanse-COMMERCIAL.backtest.log:90-125` -- `KeyError:
'PRIMARY'` at master `corpus_scenario.py:2670` (`labels[kind]`), `labels = {'COMMERCIAL_B2B': 'Operator'}`.

- [x] T007 `harness/vectors_script.py:2820` `DECIDERS_ONLY_SCOPES = ("COMMERCIAL",)`, `:2823` `NOT_ON_STUDY` (the two
  reasons), `study_people` (`:2829`): under COMMERCIAL on a B2B entry the B2B people alone; on a B2C entry everyone;
  082's PROBLEM / SOLUTION rule and SOLUTION_COMMERCIAL / ALL unchanged. `:2843` `not_on_study(entry)` -> (names left
  out in corpus order, why).
- [x] T008 `evals/corpus_scenario.py:2718` `link_kind`, `:2723` `people_to_send(people, kinds)` -> (sent, unserved), pure;
  `:2731` `not_on_this_study(j, labels)`: on money alone where people are left out, one founder step *13 of the entry's
  people not on this study (money alone on a B2B entry: the decision-maker's link only (keel-cloud 133)) ...* recording
  them beside the register's kinds; a person whose kind the register does not serve fails that step by name (never a
  KeyError). No step where nothing is left out on money alone (ALL, SOLUTION_COMMERCIAL, 082's PROBLEM / SOLUTION, B2C).
- [x] T009 `leg_invite` (`:2648`, `:2673`): sends `not_on_this_study`'s list; `labels[kind]` reached only for a served kind.
- [x] T010 `tests/test_backtest_scope_082.py`: 082's *money alone sends every person* re-pinned to the deciders.
- [x] T011 Tests (18): 17-expanse COMMERCIAL is its 7 deciders (13 left out, Priyanka Raghunathan among them, the
  reason); 08-fresco, 10-palus, 21-codyco the same, ALL / SOLUTION_COMMERCIAL everyone; 13-aircaps COMMERCIAL everyone;
  082's reason kept; follow-up lines and `inputs.json` name no left-out person; `people_to_send` on a register with one
  kind and two (and one FULL kind, B2C); `not_on_this_study` on a step double (the record, the old stop as a named
  fault, no new step on the other scopes); `leg_invite`'s source.

### The downstream consumers, and what each reads now

Everything below reads `j.people` (= `vs.person_inputs(entry)`, built from `study_people` after the scope is set in
`corpus_scenario.run` and `scope_journey.run`), so the deciders alone on a B2B money study with no code of its own:

- `vs.person_inputs` -> `follow_up_lines` (pooled over the deciders), `inputs.json` (`write_generated`, the quality
  readers' respondent side), `vs.generate`'s THEMES screen (`walked_follow_ups`, strict journeys only).
- `leg_invite`: the send loop, *every corpus person has a link of their own* (links == `len(j.people)`, the register's
  order); `scope_journey.one_kind` (already the deciders' one kind, keel-cloud 139).
- `leg_interview` -> `_answer_one` (the COMMERCIAL_LINK interview each), `_read` (deciders are never readable),
  `junk_follow_ups`, `hold_the_chip_people`, the pilot's `opted_in`.
- `scope_journey.record_of` `"people": len(j.people)` -> `scope_marks.sc3` (`links == people`, kinds `{COMMERCIAL_LINK}`
  by `links_of("COMMERCIAL", b2b=True)`, which already said so).
- `_await_standings` and the standings / SC5-SC7 read the wire (invited, answered), not a count of the file.
- `backtest.readings(j)`, `backtest.watched_people(j.people)` (the camera).

Not touched, named: `PICKS_NEEDED` (`corpus_scenario.py`, `{"pick_one_then_one": 2}`) counts a control's option picks,
not people; `gallery.attribution_reasons` refuses a run that invited other than `PARTICIPANTS` (20) -- a B2B money
study invites its deciders (7 on 17-expanse), as 082's PROBLEM / SOLUTION walks already invite 12 or 13; the disclaimer
is the founder's fixed sentence, so a scoped run's gallery export is a decision for him, not this spec;
`corpus_facts.vectors_facts_for` registers every file story as a fact (unscored on a page that never draws it, as on
082's walks).

## FR-3 -- nothing else moves

The SOLUTION and PROBLEM walks (no step added, 082's people), the decision-maker's screener leg (076: the same
`_condition`, now reached through `first_screens`), the gate, the after-part reveal, the marks (`MARKS_VERSION`,
`SCOPE_MARKS_VERSION` 2), the corpus, the scenario set.

## What the spec got wrong (or left loose)

1. **FR-1's field is `reveal`, not `idea`.** keel-cloud `InterviewComposer` serves `idea` on a COMMERCIAL_LINK alone; on
   the money study's person link (kind FULL, no gate) the card is `reveal` with `afterPart` 0 (spec 133 FR-4), and
   keel-web `screensOf` draws it as the `reveal` screen before the first part after it. A walker running `_idea()` on
   `interview.idea` there would never have fired. Built on the served shape; the screen is recorded as `reveal`.
2. **The spec's stop was not the walk's last on 13-aircaps.** After the card, `_read` would have waited on a reading for
   each of the sixteen people whose file has a story; money alone types none (T005).
3. **FR-2 is a study rule, not a register read.** The register's kinds are keel-cloud 133's rule; the people are decided
   before the walk (`study_people`, as 082 did for PROBLEM / SOLUTION) so `inputs.json`, the follow-up lines and the
   readers agree with the leg; the register is held to it at send time (a mismatch is a named fault, not a quiet drop).
   082's test that money alone sends everyone had to move.
4. **`PICKS_NEEDED`** in the hand-off names an option-pick count, not a count of people; nothing to change there.
5. **SC4 on a B2C money study reads `idea`** (`scope_marks.sc4`'s COMMERCIAL branch: the problem's sentence and the idea
   screen), which a FULL link does not serve -- 13-aircaps' walk will record SC4 findings (non-strict) though the page is
   right. The marks are FR-3's to keep; a scope-marks spec owes `reveal` on the FULL link (SCOPE_MARKS_VERSION 3).

## Judgement calls

1. **The screener before the idea on any kind** is walked whenever `Interview.condition` is served, though keel-web 145 /
   keel-cloud 166 are not built: a FULL link with a gate never carries it, so nothing served today moves.
2. **`idea` on a FULL link is not walked** -- keel-web draws the idea screen on a COMMERCIAL_LINK alone.
3. **One step, only on money alone**, records the people left out, so 082's walks gain no step (FR-3).
4. **The opening reveal's record carries `problem`** (as the decision-maker's idea does); the after-part reveal's shape is
   unchanged.
