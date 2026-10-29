# Tasks 087 -- Decided before: the founder's decisions recorded, a decided weak row snoozed, not advised again

Branch `087-decided-before` (worktree `wt/eval-087`, `.git` a file), off master `44037fc` (specs 085-089 spec-only on
top of 084's `851f9db` + `5da2837`). Read only: keel-cloud-docs (live `ad5f6441`, and an exported snapshot at
`f48f256e` for the gate, below), keel-web `039435d`. `REVISION` 17, `MARKS_VERSION` 21, `INTERVIEWER_MARKS_VERSION`
12, `RUBRIC_VERSION` 2 unchanged. **No paid call**: no walk, no reader, no adviser call; the only cycle commands run
were `make quality-advise ... DRY=1` and `make quality-walk DRY=1`. Nothing merged or deployed; every commit pushed
to the branch.

| Commit | What |
|---|---|
| `6c69a90` | FR-1: `quality/decisions.py` (the reader and validator of `quality/decisions.toml`), the FR-1 tests |
| `86c75e2` | FR-2 + FR-3 + FR-4: the match and the snooze (`quality/decisions.py`), `quality/cycle.py` (record, walk, advise, advice page, `reopens`), `quality/readers/adviser.md` (`{{declined}}`, `reopens`), `tests/test_decided_before_087.py`, the no-decisions fixture in 079's and 081's tests |
| this commit | FR-5: `quality/CYCLE.md` (step 2, step 3, the coordinator's duty, a rule that does not move), `AGENTS.md` (the 087 paragraph), the Makefile's `quality-advise` comment, the runbook test, this file |

## Unit

The live keel-cloud-docs checkout (`ad5f6441`) is at corpus revision 19 (keel-cloud 158-160 merged), and master's
harness still reads revision 17 (spec 089 is spec-only): on it master is not green. The gate was therefore run twice
on each tree -- against the live checkout, and against keel-cloud-docs `f48f256e` (084's read-only sha) exported by
`git archive` into a scratch folder and named in `stack.toml` for the run only (restored after; never committed).

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `44037fc`, keel-cloud-docs `f48f256e` snapshot | 3,662 | 0 | 0 | 61 |
| **branch, keel-cloud-docs `f48f256e` snapshot** | **3,694** | **0** | **0** | **61** |
| master `44037fc`, live keel-cloud-docs `ad5f6441` | 3,398 | 79 | 40 | 206 |
| branch, live keel-cloud-docs `ad5f6441` | 3,430 | 79 | 40 | 206 |

The 32 new tests are `tests/test_decided_before_087.py`; 079's and 081's tests hold at their counts. Against 084's
recorded 3,670 / 0 / 53: the snapshot has no `.git`, so the tests that read keel-cloud's git history skip (8 more
skipped, 8 fewer passed) -- the same on master and branch. The live run's 79 failed and 40 errors are the corpus
revision (`CorpusError: ... revision is 19; this eval reads revision 17 only`), the same set on master and branch (diffed by node id);
none is in the quality cycle.

## FR-1 -- the record

- [x] T001 `quality/decisions.py` `load` reads `quality/decisions.toml`: every `[[decision]]` has `id`, `cycle` (a
  cycle id), `proposals` (advice numbers), `row` (exactly scope, audience, dimension, screen; each a string, a list,
  or `*` alone), `fix` (string, list or `*`), `decision` (taken | declined | held), `until` (spec-merged | never | a
  cycle id), `why`; `spec` required on taken; `merged` (a sha) allowed on a spec-merged entry only; an unknown field,
  a reused id or a top-level table other than `decision` is refused. Every refusal names the entry and the field.
- [x] T002 The row's scope is one of `quality.cycle.SCOPES`, its audience one of `rubric.AUDIENCES`, its screen one of
  `decisions.SCREENS` (the founder flow's kinds, the stranger's, and `insights`), its dimension `-`, `*` or a
  `<scope>.<name>` key.
- [x] T003 Pinned: the file of record parses (20 entries, D-2026-10-29-01 to -20, each naming a committed cycle
  record, none `merged` yet); `SCREENS` covers every kind the committed score files (and 079's fixtures) carry and
  table.py's founder files; fourteen shapes refused by name; no file is no decision. **The file of record was not
  changed**: every field already had the spelling FR-1 reads.

## FR-2 -- the snooze

- [x] T004 `row_matches`: scope, audience, dimension, screen (= the row's `kind`); `*` any, a list a set, `-` only a
  row with no dimension.
- [x] T005 `fix_matches` (the matching rule): `*` any; else one of the decision's `fix` values, case and spacing aside,
  (a) equals the row's fix category, or (b) is `dimension-registry.json` on a `registry row`, or (c) occurs whole in
  the row's fix place (not inside a longer name: `questions.md` does not match `respondent-questions.md`). A free
  label (*a third persona option*) matches no fix location the cycle writes, so it snoozes nothing.
- [x] T006 `active`: `never` always; a cycle id while the record's name sorts at or before it (records sort by name,
  the date then the build, as `previous_record` does); `spec-merged` until the entry carries `merged`.
- [x] T007 `compose` (the record) splits the weak rows: the snoozed ones under `## Decided before (N) -- snoozed by
  quality/decisions.toml (spec 087), not sent to the adviser`, one line each (the row, then per decision its id, word,
  spec on taken, how long it holds, its why); `## Weak rows (M: K to advise, N decided before)` lists the rest; the
  advise line counts K. `weak_rows` in the data block stays every weak row (the measurement); `decided_before` is
  added only when non-empty, so a record with nothing decided is 079's to the byte (pinned against 079's fixture).
- [x] T008 `make quality-walk` loads the decisions after its preflight and refuses a bad file before any paid step;
  its dry run says how many it holds.
- [x] T009 `make quality-advise` sends only the open rows; when every weak row is decided it prints the list and
  `every one decided before ... nothing to advise, no call made` and writes nothing.
- [x] T010 Pinned on 079's fixture cycle: `never` snoozes, lists, sends nothing; a cycle id through that cycle
  snoozes and an earlier one does not; `spec-merged` snoozes until `merged` is written, then the row is advised and
  not listed; a decision on another row or with a free-label fix snoozes nothing.

## FR-3 -- the adviser knows

- [x] T011 `adviser.md` gains `## What the founder has already said no to` (`{{declined}}`): each active declined
  decision whose `row` matches the row (a `*` row every row), whatever its `fix`, with its row, what was proposed
  and his why in full; *(The founder has declined nothing on this row.)* otherwise. A section *What the founder has
  declined stays declined* asks the adviser to name any it goes against in `reopens`.
- [x] T012 `parse_advice` reads `reopens` (a list of ids): required when the prompt quoted a declined decision,
  `[]` when absent otherwise (an answer of 079's shape). `reopened` refuses a proposal naming one -- recorded by row
  as **Refused -- not a proposal** (spec 087 FR-3), naming the decision and its why, the refused text kept, as 081
  FR-6 records a special case.
- [x] T013 Pinned: the prompt carries the declined whys on the row (a `*` one and the row's own) and not another
  row's, a taken one's or an ended one's; a proposal that reopens one is refused naming it; an answer without
  `reopens` when one was quoted is *No proposal*.

## FR-4 -- the advice page

- [x] T014 `render_advice` counts only the advised rows (`N weak row(s) ...`, then `K more decided before, listed at
  the end (spec 087): not advised`), and lists the snoozed rows at the end under `## Decided before (K)`, one line
  each, before the data block (`decided_before` in it). A taken decision whose spec has merged no longer snoozes, so
  its row was advised and is not listed. Pinned with a second weak row at the gate, one advised and one snoozed.

## FR-5 -- the runbook

- [x] T015 `quality/CYCLE.md`: the file in the opening list; *What has the founder already decided?* in the four
  questions' table; step 2 *Decided before* (the file's fields, the match, the until, the listing, the refusals);
  step 3 *Decided before* (not sent, listed at the end, the declined whys, `reopens`), its cost per row not decided,
  and **the coordinator's duty**: after every walk-through, add the founder's decisions before the next advise;
  after every merge of a spec a decision names, write `merged = "<sha>"`; *Rules that do not move*: a decided row is
  not advised again while its decision holds, reopened by editing the file.
- [x] T016 `AGENTS.md`: the 087 paragraph after 084's. The Makefile's `quality-advise` comment names the snooze.

## The acceptance

| Command | Result |
|---|---|
| `make unit` (snapshot) | **3,694 passed, 0 failed, 61 skipped** (185 s; master 3,662 / 0 / 61: +32, the new file) |
| `make quality-advise CYCLE=quality/cycles/20261028-f48f256.md DRY=1` | exit 0; **62 of 62 weak rows under `## Decided before (62)`**, nothing sent, nothing written: D-05 (the registry rows) 25, D-08 (the page's own words) 12, D-19 (the respondent files and the follow-up ladder) 9, D-02 (solution-mechanism.md) 7, D-01 (context-interpret.md) 6, D-03 (problem-interpret.md) 5, D-04, D-06, D-07 one each beside another -- 67 decisions named on 62 rows (five rows under two) |
| `make quality-walk DRY=1 ENTRIES=21-codyco SCOPES=PROBLEM WHY="dry"` | the plan, and `decisions: 20 in quality/decisions.toml (spec 087)` |

Pinned in `test_the_dry_advise_on_cycle_f48f256_snoozes_every_weak_row_and_sends_nothing`: the 62 listed rows are the
advice page's 62 in its order, and every one is snoozed by a decision whose `proposals` names its advice number.

## Judgement calls

1. **The matching rule for `fix`** (T005): the decisions name a fix as a file (`context-interpret.md`) or a phrase
   (*the page's own words*, *the follow-up ladder*) where table.py names a category and a longer place; the rule is
   the category, or the value whole inside the place, plus one alias, `dimension-registry.json` = category `registry
   row` (the file every registry row lives in). The file of record was left as written.
2. **`screen` is the row's kind** (`q`, `check`, `item`, `gate` ...), as the cycle's row key prints it; `SCREENS` is a
   constant in `quality/decisions.py`, held by a test to every kind the committed score files carry -- a new screen
   kind is added there in the spec that adds it.
3. **One commit for FR-2, FR-3 and FR-4**: all three are the same few functions of `quality/cycle.py` (compose,
   advise, render_advice, the prompt); FR-1 stands alone.
4. **A row several decisions match** is listed once, with every matching decision on its line.
5. **The record keeps `weak_rows` whole** (every weak row, the measurement) and adds `decided_before`; only the
   rendered *Weak rows* list and the advise count drop the snoozed rows. With nothing decided, the record is 079's
   to the byte.
6. **`reopens` is the adviser's own word**, as `persona_aware` is 081's: the harness cannot tell mechanically that a
   proposal contradicts a free-text why, so the adviser names the ids, and the harness refuses whatever it names. It
   is required only when a declined decision was quoted, so 079's answers still read.
7. **A cycle-id `until` compares by record name** (`<=`), the order `previous_record` uses.
8. **No decisions file is no decision** (the cycle as before 087); a malformed one refuses.
9. **When every weak row is decided, a non-dry advise writes nothing**, rather than an advice page of only *Decided
   before* lines: it would overwrite `quality/cycles/20261028-f48f256-advice.md`, the record the decisions cite.
10. **079's and 081's tests read no decisions** (an autouse fixture pointing `cycle.DECISIONS` at a missing file):
    their fixture's one weak row is a registry row, which D-05 (`*`, `dimension-registry.json`) would snooze.
11. **The worktree's `.venv`** is a directory (ignored) whose `python` and `lib` are the main checkout's: running with
    `PY=` pointing elsewhere breaks `test_door_keel_is_spec_062_byte_for_byte...` (it compares `make -n` output).

## What did not hold

- **The gate is not green on the live keel-cloud-docs checkout**, master or branch: corpus revision 19 against
  master's harness at 17 (spec 089, spec-only on master, is the fix). The counts above are against the `f48f256e`
  snapshot; the live failures are the same on both trees.
- **D-05 snoozes more than its twenty proposals.** Its row is `*` everywhere and its fix the registry, so it snoozes
  every registry-row weak row until keel-cloud 152 merges -- including the two follow-up ladder rows (also D-19's),
  49 (also D-06, declined) and **53 (D-07, held through `20261028-f48f256` only: "the row competes again next
  cycle")**, which stays snoozed by D-05 until `merged` is written on D-05. Not changed: narrowing D-05's row is a
  change to the decision, the founder's to make.
- **D-04 (the no-number rule) reaches COMMERCIAL only**: its row names scope COMMERCIAL, so on a later cycle the
  PROBLEM and SOLUTION problem-seed rows' adviser is not told it (FR-3 quotes declined decisions whose row matches).
  Widening it to `*` is the founder's word.
- **The free-label decisions snooze nothing by themselves** (D-09 to -18 and D-20 name product asks, not fix
  locations): their rows are snoozed by the broader taken decisions beside them (D-05, D-08, D-19); once those merge,
  only the declined ones still act -- through the adviser's prompt, not the snooze.
