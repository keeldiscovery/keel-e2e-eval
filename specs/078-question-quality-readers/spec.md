# Spec 078 -- The question-quality readers: a versioned rubric, committed scores, a baseline

The founder, 2026-10-28: two readers score every question a founder and a stranger are served; the rubric and the
reader prompts live in the repository, versioned, never thrown away; every score is committed so the quality can be
watched improving; the first full run is the baseline the future is measured against -- when an instruction changes,
when a registry row changes, when a model is upgraded. Design of record: keel-cloud-docs
`canon/designs/question-quality-rubric-2026-10-28.md` (the five criteria, the two readers, the fix ladder) and
`canon/testing-pyramid.md` (where this sits among the unit tests, the journeys and the instruction eval). PROPOSED and
approved in outline; every scoring run is paid and runs only on the founder's word. Build on his word.

## Rules

- **FR-1 The rubric is a file, and it has a version.** `quality/RUBRIC.md`: the five criteria (R1 fits here, R2 plain,
  R3 about their life, R4 the options, R5 the founder's words kept / nothing leaks), the 0-1-2 anchors, the two
  booleans (`out_of_place`, `looks_stupid`), the *instead* line, the three whole-flow questions, and the weak rule (a
  0 on the same criterion in two of five entries, or a mean under 1.5). `quality/rubric.py` carries
  `RUBRIC_VERSION = 1` and the JSON shape of one score; a change to a criterion, an anchor or the weak rule bumps the
  version, and the file says what changed and why (the pattern of `MARKS_VERSION`). Scores of two rubric versions are
  never averaged.
- **FR-2 The readers are files too.** `quality/readers/founder.md` and `quality/readers/respondent.md`: the two
  prompts, each with its persona hand-off (the founder-reader: the entry's `.sources.md`; the respondent-reader: the
  link's `{actor, actor_plural, job, circumstance, segment, window}` and one named person from the sources), the
  rubric pasted by the runner from `RUBRIC.md` (one source of the criteria), the screens-so-far context, and the one
  JSON object asked back. The reader model and effort are pinned in `quality/readers.toml` (`model`, `effort`,
  `vendor`), recorded in every score file; the default is Opus 5.5 at medium. The readers follow `instructions/judge.py`'s
  rules: bounded, one screen per call, cached within a run, every prompt and answer recorded, never the executor, never
  a nonce fence or a response contract.
- **FR-3 What is read.** A back-test bundle's `backtest.json` (spec 062 FR-4): every founder screen in order and every
  served respondent screen per link, as text. The readers never drive the UI and never see the screenshots. The
  founder-reader reads the founder screens; the respondent-reader reads each link's screens (part 1, part 2, the
  commercial link; the AI link's spoken form as the player serves it, read as said). One call per screen, the earlier
  screens of the same walk as context.
- **FR-4 `make read-screens RUN=<bundle>` (paid).** Refuses without the reader's key in the shell (named by vendor, as
  `make backtest` names Keel's), never in `make eval`, `make unit`, the matrix or a checker. Writes
  `quality/scores/<entry>/<yyyymmdd>-r<RUBRIC_VERSION>-<cloud-sha7>-<routing-version>-<reader-model>.json`: one object
  per screen (`screen`, `audience`, `link`, `dimension`, `kind`, `r1..r5`, the five whys, `out_of_place`,
  `looks_stupid`, `instead`), the three whole-flow answers per audience, and a header (entry, bundle run id, the cloud
  sha and web sha the bundle was walked on, the product's routing table version, `RUBRIC_VERSION`, the reader's
  model/effort, cost, time). **The file is committed** (the run folder stays ignored, as every run is): the scores are
  the record, the bundle is the evidence.
- **FR-5 `make read-table` (free).** From every committed score file under `quality/scores/`, `quality/TABLE.md`: one
  row per (dimension, audience, screen kind) over the latest score of each entry at the current rubric version -- the
  five means, the count of 0s, the entries that gave them, the *instead* lines, and the fix location by the design's
  §1 (registry row / shared file / code transform / no model). Weak rows marked. A second table per entry over time
  (the last three score files) so the trend is visible: ↑ ↓ = beside each mean. Regenerated and committed with every
  score file.
- **FR-6 The baseline.** `quality/BASELINE.md`: the first full run over the five entries the founder names (the
  thirteen recorded bundles 08-21 are scored first, free of product cost, to calibrate the rubric against his eye on
  five screens before the baseline is cut). It names the score files that make it, the cloud sha, the routing version,
  the rubric version, the reader, and the five means per row. A later run compares against it by `make read-table
  BASELINE=1`: each row's delta, and a verdict line -- **better / same / worse** by the weak rule and the means (a
  row that was weak and is not, or the reverse). A model upgrade's run, an instruction's run and a registry row's run
  are all compared the same way; a new baseline is cut only on the founder's word (`BASELINE.md` rewritten, the old
  one kept under `quality/baselines/<date>.md`).
- **FR-7 The rubric is a mark.** `read` joins `instructions/marks.toml` as a mark kind beside `no_leak`, scored from a
  committed score file rather than a run, so `instruction-eval`'s scorecard can show the five means and the flagged
  count when a score file for its entry exists at the current rubric version; *not measured* otherwise (the dry run's
  rule). `MARKS_VERSION` 20 → 21.
- **FR-8 Nothing else moves.** The back-test walk (spec 062), the instruction eval's writer-side marks, the golden
  corpus (`REVISION` 16), the journeys, the noise check, the model routing table; no reader call from any gate.

## Acceptance

`make unit` green (master `f46c1e8`: 3,543 / 55): the rubric file parses into the prompt; a score file round-trips
its shape; the table and the baseline delta are computed from fixture score files (`tests/fixtures/quality/`, two
entries, two rubric versions, one mixed -- refused); the refusals (no key, no RUN, a bundle without `backtest.json`,
a score at another rubric version). `make read-screens --dry-run RUN=<bundle>` prints every prompt and writes no
score. The first paid run, on the founder's word, over the thirteen recorded bundles; he reads five screens' scores
against his own eye before the baseline run. tasks.md in 077's shape. The score files, `TABLE.md` and `BASELINE.md`
are committed on eval master, never pushed without his word.

## Judgement calls, for the founder to overturn

1. Scores live in keel-e2e-eval under `quality/`, beside the harness that writes them -- not in keel-cloud, whose
   instructions they judge, so a cloud commit never carries a verdict on itself.
2. The reader is Opus 5.5 at medium; a stronger reader than the Sonnet-medium writer, the same vendor.
3. One respondent persona per link (the first role the sources name); a second persona is a flag, not the default.
4. The score file name carries the cloud sha, the routing version and the reader model, so a diff of two files says
   which of the three moved.

## Amended at build (the coordinator, 2026-10-28) -- three decisions added to the rules above

1. **The reader runs through the `claude` CLI exactly as `instructions/judge.py` does**, with
   `--model claude-opus-5-5` -- `claude -p --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence
   --max-turns 1 --output-format json`, plus `--model` and `--effort` -- **not an API key**. FR-4's refusal is read so:
   `make read-screens` refuses when the `claude` binary is missing or `claude -p` cannot answer a one-word probe, never on
   a key, and no key is read, named or passed. `quality/readers.toml` pins `model = "claude-opus-5-5"`,
   `effort = "medium"` (passed as `--effort medium`, which the CLI accepts), `vendor = "anthropic"`, `door = "claude
   CLI"`; the effort knobs of the environment are stripped as the judge strips them (`judge_env`).
2. **The score as one number.** Beside the five means, every score file and `TABLE.md` carry `score_pct` = (the sum of
   every r1..r5 given over the file's screens) / (2 x the count of those scores) x 100, per audience and overall, and
   `flagged_pct` = the screens with any 0 / the screens x 100. `TABLE.md`'s head says the overall `score_pct` over the
   latest file of every entry, and the bar the founder named: **90% is the bar** before the remaining entries are
   walked. The weak rule stays as FR-1 has it.
3. **The reader's context is bounded.** The earlier screens of the same walk go in as one compact list (kicker and
   question only), never their options, so a call stays small; the screen being scored goes in full.
