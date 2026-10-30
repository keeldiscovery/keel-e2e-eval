# Tasks 102 -- On a consumer entry's money study the person's body is answers alone

Branch `102-the-money-links-body` (worktree `wt/keel-e2e-eval-102`), off master `374694d` (the spec commit). Built by
Claude on 2026-10-30. Read only: the re-walk record `quality/cycles/20261030-35dfb74.md` and the 13-aircaps walk log
named in the spec. **No browser, no stack, no paid call**: the paid check (`make quality-walk ENTRIES=13-aircaps
SCOPES=COMMERCIAL DOOR=host`) is the coordinator's, on the founder's word. Nothing merged into master; the branch pushed
after every commit, never force-pushed.

| Commit | What |
|---|---|
| `caf5471` | FR-1..FR-4 and their 28 tests (the commit's subject runs into its body: a missing blank line, left as pushed) |
| `a280c71` | master's one failing test, not this spec's: the cycle's respondent screens name `condition` |
| the docs commit | this file, `AGENTS.md`'s spec-102 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| 101's tasks.md record (branch `b36f35f`) | 4,048 | 0 | 53 |
| **master `374694d`** (`083fc9a`'s score files fail `test_decided_before_087`, see below) | **4,047** | **1** | **53** |
| branch at `caf5471` (FR-1..FR-4) | 4,075 | 1 | 53 |
| **branch at `a280c71` (the last code; the docs commit adds none)** | **4,076** | **0** | **53** |

The +28 are `tests/test_money_links_body_102.py` (FR-1 13, the threading by scope 5 of them; FR-2 11; FR-3 1; FR-4 3). Master's row is the branch's at `caf5471` less the 28; the one failure was re-run
alone on a detached worktree at `374694d` and fails there the same.

## FR-1 -- the body

- [x] T001 `harness/vectors_script.py:1728` `PersonInputs.gate: bool = True` -- whether the study serves the gate; set by
  `person_inputs` (`:2913`, `gate=serves_gate(entry)`), so every caller of `response` is handed it with no new argument
  (the builder's pick of FR-1's two options: threaded from `person_inputs`). The default keeps every hand-built
  `PersonInputs` (S-016's owners, 076's outside decider, 077's chip person) on the gate, as today. `recency`, `story`
  and `anchor_chip` stay the file's record (`backtest.readings` prints them) and are never sent off the gate.
- [x] T002 `response` (`:1747`): off the gate and not `LINK_B2B`, an inside person's body is `{"answers": answers}`; the
  outside branch first and the B2B branch unchanged, every gated body unchanged.
- [x] T003 `ends_on_chip` (`:1768`): false off the gate -- no chip is asked, so none ends the interview.

## FR-2 -- no gate, no No

- [x] T004 `:1774` `NO_ANSWERS_OFF_THE_GATE`: `response` refuses a file gate No off the gate by name
  (`VectorsScriptError`: *the page asks them part 3 and the file has no answers for it; a revision would have to record
  their money picks ...*).
- [x] T005 `:1783` `not_walked_off_the_gate(person, interview)`: the reason a person is not walked off the gate (the gate
  No; FR-4's outside person), else None. `evals/corpus_scenario.py:2907` `_answer_one` asks it right after the served
  interview is read and, on a reason, appends one finding (`what` the reason, `person`, the served `kind` / `gate` /
  `condition`) and returns -- before any page is opened, so nothing is begun or posted.
- [x] T006 `walks_rungs` (`corpus_scenario.py:2977`): true for every inside person off the gate.
- Not touched, named: the spec's *gate-No path at `evals/corpus_scenario.py:2900`* is `harness/vectors_script.py`'s
  `moved_line_for_the_second_yes` (`if person.link != LINK_B2B and not person.recency`); off the gate the only people it
  would call a No are the ones FR-2 does not walk, so it stands. `follow_up_lines` reads `ends_on_chip` and so owes the
  file's chip person a line off the gate with no change of its own.

## FR-3 -- no story, no seam

- [x] T007 `corpus_scenario.py:3079` `_speak_for` returns None off the gate, so no seam is added and `_hold_the_box` is
  not run. `STORY_SPOKEN` untouched (it names golden entries only, all walked under ALL).

## FR-4 -- outside the segment

- [x] T008 `vectors_script.py:1779` `OUTSIDE_OFF_THE_GATE`, the spec's words exactly; `not_walked_off_the_gate` returns
  them for a person outside the segment off the gate **while the served interview carries no `condition`** -- once
  keel-cloud 166 / keel-web 145 serve it, the person is walked to the screener's exit (spec 101 FR-1's `first_screens`
  asks it first; `response` already sends `outsideSegment` alone), so nothing here has to be undone for spec 100.

## FR-5 -- tests (28)

`tests/test_money_links_body_102.py`: FULL off the gate (answers alone, story dropped; chip dropped, `ends_on_chip`
false), FULL on the gate (story, chip, No as today), `LINK_B2B` on and off the gate, outside on and off; 13-aircaps under
COMMERCIAL (20 people, none gated, 17 bodies of answers alone with no `recency` key, Harriet Coleman and Naomi Adler
among them, the three gate Noes refused by name); 13-aircaps under ALL as today; `person_inputs`' `gate` by scope (5);
`not_walked_off_the_gate` (8 cases); `_answer_one`'s source; follow-up lines off the gate; `_speak_for`; the outside
finding on 11-issen's Nikos Ferrante and the gate-No finding on Patrick Moran through `_answer_one` on a browser double
(no page opened); the five walked entries have nobody outside, 11-issen one.

## Beyond the spec: master's failing test -- `a280c71`

`tests/test_decided_before_087.py::test_the_screens_are_the_ones_the_cycle_scores` fails on master `374694d`: the four
COMMERCIAL r2 score files of `083fc9a` (08-fresco, 10-palus, 17-expanse, 21-codyco) carry the decision-maker's screener
as kind `condition` -- the walk's name for it (`vectors_screens.Interview._condition`), which `quality/readers.py`'s
catch-all keeps -- and `quality/decisions.py` `RESPONDENT_SCREENS` listed only `screener` (the gate's chip question).
`condition` is listed beside it and `quality/table.py` `fix_location` sends it where the screener question is fixed. No
rubric, mark or score moves.

## What the spec got wrong (or left loose)

1. **FR-2's *the corpus has none today* is wrong.** Every consumer back-test entry records gate Noes, and every one has
   no picks: 13-aircaps three (Patrick Moran, Lucia Ferraro, Desmond Hale), 09-karsa five, 11-issen, 23-taiga, 24-probo
   and the rest two or three. Refused at the walk's start (`person_inputs`), the refusal would have stopped all twelve
   consumer money studies before the first person -- the stop this spec exists to remove -- and FR-5's *20 bodies* could
   not hold. Built instead: `response` refuses them by name (the refusal, pure, as written), and the walk does not walk
   them and names each in one finding, as FR-4 does an outside person. **Consequence for the paid walk**: on 13-aircaps
   17 people answer of 20 invited, so `_await_standings` waits its full 60 s for an *answered == invited* that never
   comes, then reads (no failure), and the money lines' `n` is 17. Whether a gate No in the file should be walked on
   money alone at all (it would need the revision's money picks) is the corpus's question, not the harness's.
2. **The file's chip person** (one per consumer entry: Naomi Adler on 13-aircaps) is not refused: off the gate the chip
   is dropped and they answer part 3 on their file picks; a pick the file leaves out (Naomi's Ability to pay) takes the
   escape and is named, by the walk's existing unanswered path.
3. **The *gate-No path at `evals/corpus_scenario.py:2900`*** is in `harness/vectors_script.py` (see FR-2).

### Other places that assume a story on a non-B2B link (read, not changed)

- `evals/backtest.py:650` `watched_people`: the camera's PRIMARY person is the first with a gate yes, a story and no
  chip -- off the gate still a real person on the link (Harriet Coleman), so harmless.
- `evals/backtest.py:1472` `readings`: each row's `gate` / `story` / `chip` are the file's, printed as the file's; on
  money alone they describe nothing the page asked. A reader of `readings` should know.
- `evals/corpus_facts.py:211`: every file story registered as a fact (101 named it; unscored where never drawn).
- `evals/open_link_leg.py:101`, `evals/interviewer_leg.py:1394`: choose a person with a gate yes and a story -- golden
  journeys under ALL only.
- `evals/scope_marks.py` SC4 reads `idea` on a consumer money study (101's item 5, unchanged).
