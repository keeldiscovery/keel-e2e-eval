# Tasks 081 -- Rubric version 2: plain to this person, and said aloud

Branch `080-corpus-revision-17` (one worktree for 080 then 081, `wt/eval-080`, `.git` a file), on top of 080's four
commits off master `fc7cad5`. The designs of record, read only, keel-cloud-docs master `88bfce8d`:
`canon/designs/question-quality-rubric-2026-10-28.md` §3 as amended (R2 rewritten, R6, the persona block, the
generating-side note) and §5a (*the fix is persona awareness, never a special case*), and
`canon/designs/spoken-questions-guidelines.md` §2, §3, §5 (pasted by the runner, never copied here). `RUBRIC_VERSION`
1 -> 2; `MARKS_VERSION` 21 and `REVISION` 17 (080) unchanged. **No paid call**: no reader, no adviser, no back-test.
No score file of record existed, so nothing is re-scored. Nothing merged, pushed or deployed.

| Commit | What |
|---|---|
| `07e3b30` | FR-1 / FR-2 / FR-4: `quality/rubric.py`, `quality/RUBRIC.md` |
| `c63bdba` | FR-3 / FR-4: `quality/readers.py`, `quality/readers/founder.md`, `respondent.md` |
| `fabefdc` | FR-5: `quality/table.py`, `quality/TABLE.md` |
| `bf76b73` | FR-6: `quality/readers/adviser.md`, `quality/cycle.py` |
| `e063b28` | the fixtures at version 2, `tests/test_quality_081.py` (24), 078 / 079's pins, README, AGENTS |
| this commit | this file |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| 080's last commit `15efaa7` | 3,630 | 1 | 53 |
| `e063b28` and this commit | 3,655 | 0 | 53 |

080's one red (`test_quality_078::test_the_rubric_parses_into_five_criteria_...`: the design's R2 anchors rewritten for
version 2) is closed here -- that test is now `..._six_criteria_...`. The +25 passed are `tests/test_quality_081.py`'s 24 and that one red, now green.

## FR-1 -- the version

- [x] T001 `quality/rubric.py`: `RUBRIC_VERSION = 2`; `RETIRED = {1: ...}` -- `validate_file` refuses a file at a
  retired version **by name** (*x.json is at rubric version 1, before spec 081 ... refused*), and `table.load_scores`
  turns that into a `TableRefused` naming the path (`make read-table` exits 2). A file at another, unretired version
  (the fixtures' 3) is still set aside as 078 did, its header checked alone.
- [x] T002 `quality/RUBRIC.md`: **RUBRIC_VERSION 2** at its head and a *Versions* entry 2 saying what changed and why
  (R2's anchors and why version 1's read a trade's own word as jargon; the persona block; R6 and why; the v1 refusal).

## FR-2 -- R2 from inside the persona

- [x] T003 R2 is *Plain to this person* with the design's anchors word for word (*yes, in their own words* / *needs a
  second read, or one word they would not use* / *confusing, double-barrelled, or words of another trade*), held to the
  design by the 078 test as amended. The shared prompt part opens with *the yardstick is this person, never the general
  public* (the trade's words plain to the trade; a word of another trade is not, however common elsewhere), and each
  reader's own task paragraph says it again in the second person (the founder's trade for the founder-reader).

## FR-3 -- the persona block before any screen

- [x] T004 Every prompt of both readers (screen, whole flow, grouping) **opens** with `## Who you are` and the block:
  the founder-reader's is the sources whole and the project's what / where / when (`founder_persona`); the
  respondent-reader's the person on the link, their sources line, role, title on the commercial link and the same
  context (`persona`). `context_lines` is the context fields 081 names: actor, actor_plural, job, circumstance,
  segment, the window, and the market's country (with its region) -- the country is new; the others were 078's.
- [x] T005 The score file's header records the blocks **once** (`persona: {founder, respondent: {link: block}}`) beside
  `spoken_guidelines: {source, sections, sha256}`; no screen carries them. Both are required of a version-2 file.

## FR-4 -- R6, said aloud

- [x] T006 R6 lives in its own `prompt-r6` part of RUBRIC.md (the design's row word for word), pasted only into the
  respondent screen prompt beside keel-cloud's guidelines §2, §3 and §5 (`spoken_guidelines`: `git show
  <bundle sha>:canon/designs/spoken-questions-guidelines.md` in the configured cloud checkout where that commit carries
  it, else the checkout's file; a missing section refused by number).
- [x] T007 Every respondent screen carries *Said aloud by the AI interviewer*: the served spoken form where the bundle
  records one (the gate), else the guidelines' §3 template filled from the screen (`spoken_template`: the stem, *I'll
  read N options[; pick two].*, *a; b; or c.*, *Or say {escape}.*; the price's plan as *Then: ...*; a card read whole).
  No respondent screen is exempt.
- [x] T008 `parse_answer(..., audience=)`: a respondent answer without `r6` refused, a founder answer with one
  refused; `validate_file` the same on a stored screen. `score_pct` sums r1..r6 (`None` R4 / R6 in neither sum);
  `spoken_pct` per audience (`None` for the founder) and overall; `looks_stupid` gains R6 = 0; `flagged` reads R6.
- [x] T009 The dry run prints each persona block and the guidelines **once**, then every prompt with them named in place
  (`[the PRIMARY persona block, printed above]`); the prompt files it writes carry them whole.

## FR-5 -- the table

- [x] T010 An R6 mean column on every row (– on a founder row), `spoken_pct` beside `insights_pct` on the head's
  respondent line, a spoken % column in the trend, R6 in the baseline's rows and the comparison's deltas; the weak rule
  unchanged (R6 is a criterion under it). A row weak on R6 or R2 carries `fix.also` (`CRITERION_FIX`): R6 *the
  registry row's wording or the spoken transform*; R2 *the registry row, or the instruction gains the trade's words: the
  writer handed the persona, never a condition on one trade* -- shown in the fix column, the weak rows and the
  adviser's location. `quality/TABLE.md` rebuilt (no score file yet).

## FR-6 -- the adviser never proposes a special case

- [x] T011 `quality/readers/adviser.md`: the rule (design §5a) in the prompt and `persona_aware: true | false` in the
  JSON. `cycle.parse_advice` requires it (a boolean); `cycle.special_case` refuses a proposal marked false **or** whose
  text opens a condition on who the people are, their trade, country or product (*if / when / where / unless* + the
  people, a placeholder such as `{actor_plural}`, industry, trade, role, country, market, product, sector + a verb) --
  whatever the flag says. A refused proposal is written to the advice file under its row as **Refused -- not a
  proposal**, with the refused text in a fold and the reason in the data block; it is never under *The proposed text*.

## FR-7 -- nothing else moves

- [x] T012 R1, R3, R4, R5, G1, G2, the whole-flow questions, the readers' model and door, the cycle's commands, the
  bar and the weak rule, `MARKS_VERSION` 21 (`read` reads whatever version the file says: a v1 file is *not measured:
  rubric version [1], not 2*).

## The fixtures, moved to 2

Every score fixture (`tests/fixtures/quality/scores/`, `cycle/scores/`) r1 -> r2: `rubric_version` 2, R6 2 on each
respondent screen and `None` on founder screens, the header's `persona` and `spoken_guidelines`, the summaries
recomputed; bb-beta's other-version file 2 -> 3 (still set aside). The fixture cycle's baseline was re-cut and both
records recomposed by `compose` -- the R6 2s move the numbers: 08-fresco PROBLEM 86.7% -> 88.2%, the cycle 95.0% ->
95.6% (delta to the previous -13.3 -> -11.8), the walk test's record 93.3% -> 94.1%; the 078 table 90.0% -> 91.2%,
aa-alpha's trend 87.5 -> 88.9. `tests/fixtures/quality/keel-cloud/` carries a six-section guidelines file so no unit
test reads the sibling checkout for them.

## The acceptance

| Command | Result |
|---|---|
| `make unit` | **3,655 passed, 0 failed, 53 skipped** (183 s) |
| `make read-screens DRY=1 RUN=.../runs/20261024T184654Z-backtest-21-codyco` | 63 prompts (58 screens, 3 whole-flow, 2 insight lines), no call; each persona block printed once (*Your name is Lena Hoffmann.* 1, *Stefanie Wagner* 1, the founder's sources 1); R6 and a said-aloud line in all 17 respondent screen prompts, in none of the 41 founder prompts; the guidelines read at the bundle's `6a49d1b7` |
| `make quality-advise DRY=1 CYCLE=tests/fixtures/quality/cycle/cycles/20261101-abcdef1.md` | one prompt (the fixture's weak row), *The fix is persona awareness, never a special case* and `"persona_aware": true \| false` in it, the R2 fix line in its location; no call |

## Judgement calls

1. **R6 in its own prompt part, not the shared table.** The founder-reader has no R6; one shared table would have
   handed it a criterion it must not score. `criteria()` reads both parts and returns the six in order.
2. **The dry run names the blocks in place.** *Prints the persona block once* is read literally: the stdout carries
   each block (and the guidelines) once at its head, and every prompt names them where they sit; the files written
   are the prompts whole, as they would be sent -- each call is a fresh `claude -p`, so every prompt must carry them.
3. **The §3 template where the bundle has no spoken form.** 21-codyco's items record none (only the gate does); FR-4
   asks for the screen *as the avatar would say it*, so the runner fills the guidelines' own template and says so in
   the line, never pretending it was served.
4. **The special case is caught by code as well as by the flag.** FR-6 names the flag; a model can mark a conditional
   `true`, so `special_case` also reads the text (a narrow pattern: a condition word, then who the people are or
   their trade / country / product, then a verb). The founder's own example and three like it are refused; *in the
   words of {actor_plural}* is not.
5. **Version 1 refused, other versions still set aside.** FR-1 says refused by name; 078's set-aside of *another*
   version stays for any version not retired, so a later bump does not need this code to move.
6. **The fixtures' R6 is 2 everywhere.** It keeps each fixture's story (the same weak rows, the same flags); the R6
   zeros are the new tests' own, built in a temporary dir.
7. **`git show` at the bundle's sha reads the configured checkout** (`stack.toml`'s keel-cloud), not the path
   `versions.json` names: both are keel-cloud-docs here, and the configured one is what every other reader uses.

## What did not hold

- Nothing of the acceptance; the README's paragraph on the readers and one AGENTS.md word (*five means*) moved with
  it, beyond the spec's list.
