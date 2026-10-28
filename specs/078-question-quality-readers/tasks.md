# Tasks 078 -- The question-quality readers: a versioned rubric, committed scores, a baseline

Branch `078-question-quality-readers` off master `852ec86` (the spec), worktree `wt/eval-078` (`.git` a file). The design
of record, read only: keel-cloud-docs `canon/designs/question-quality-rubric-2026-10-28.md` (at `6e1f76e0`). Built with
the coordinator's three decisions and the founder's two additions of 2026-10-28, each amended into `spec.md` first:
the `claude` CLI door (no key), `score_pct` and the 90% bar, the bounded context, the scope carried, the Insights
grouping (§G). `MARKS_VERSION` 20 -> **21**; `RUBRIC_VERSION` **1**; `REVISION` 16, `INTERVIEWER_MARKS_VERSION` 12,
`REPORT_MARKS_VERSION` 3 unchanged. Nothing merged, pushed or deployed.

| Commit | What |
|---|---|
| `fb0f796` | spec amended: the CLI door, `score_pct` / the 90% bar, the bounded context |
| `ff6a35f` | spec amended: the scope carried (FR-4 / FR-5 / FR-6) |
| `0d14dd9` | spec amended: the Insights grouping, §G |
| `580791f` | FR-1 / FR-7: `quality/RUBRIC.md`, `quality/rubric.py`, `read` in the marks, `MARKS_VERSION` 21, the pins moved |
| `debe4d7` | FR-2 - FR-6: the reader prompts, `readers.toml`, `readers.py`, `table.py`, the make targets, `tests/test_quality_078.py` |
| `a1c8fe7` | AGENTS.md, README, the empty `quality/TABLE.md` |
| this commit | this file, and four more `MARKS_VERSION == 20` pins the full suite found |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `852ec86` (the hand-off's figure, and `fb0f796` re-run here) | 3,543 | 0 | 55 |
| this commit | 3,590 | 1 | 53 |

The +46: 43 in `tests/test_quality_078.py`, three in the moved files (two v21 calls tests in `test_instruction_marks.py`,
a v20 bundle re-scored in `test_instruction_rescore.py`). **The one failure and the two fewer skips are not this
branch's**: keel-cloud-docs' `build/brief-facts/` was rewritten at 08:35 today by another hand (01-countly.json's mtime),
after master's 3,543 / 55 was measured here, so `cloud_facts_at_104` stops skipping two tests: one passes, and
`test_report_marks::test_keel_clouds_facts_draw_the_corpus_overview_on_all_seven_entries` reads 48 of 49 (the
COMMERCIAL panel's lead). The same test on master `852ec86`'s own tree (`git archive`, the same venv) fails the same
way, 48 == 49; no file this branch touches is read by it.

## FR-1 -- the rubric is a file, and it has a version -- `580791f`, `0d14dd9`

- [x] T001 `quality/RUBRIC.md`: R1-R5 with the design's 0/1/2 anchors word for word (a test reads them against the
  design when the sibling checkout is there), the instead line, the two booleans (code's: `out_of_place` = R1 0,
  `looks_stupid` = R2 or R4 0), the three whole-flow questions, `score_pct` / `flagged_pct` / the 90% bar, the weak rule,
  the verdict against the baseline, the version log. The parts the readers are sent sit between markers
  (`prompt`, `prompt-g`), so the criteria have one source.
- [x] T002 §G (the founder's second addition): G1 / G2 with their anchors; G2 is 2 by default without a junk answer.
- [x] T003 `quality/rubric.py`: `RUBRIC_VERSION = 1` (held equal to RUBRIC.md's own line), the parse into the prompt,
  the score shape (`SCORE_KEYS`, `INSIGHT_KEYS`), the answer parse (0/1/2; R4 `null` only where nothing is offered),
  `summaries` with the insight readings folded into the respondent's and the overall `score_pct`, `aggregate` refusing
  two rubric versions, `validate_file` (the round-trip).

## FR-2 / FR-3 -- the readers are files; what is read -- `debe4d7`

- [x] T004 `quality/readers/founder.md`, `respondent.md`: screen, whole-flow and (respondent) insights prompts between
  markers; `{{...}}` filled in one pass by the runner; one JSON object asked back, no fence, no response contract.
- [x] T005 `quality/readers.toml`: `claude-opus-5-5`, `medium`, `anthropic`, `claude CLI`. The argv is
  `instructions/judge.py`'s `_ARGV` + `--model` + `--effort` (the CLI 2.1.312 accepts `--effort medium`; the smoke's
  `modelUsage` names `claude-opus-5-5`); `judge_env` strips the effort knobs; cwd is the run folder.
- [x] T006 What is read: every founder screen of `backtest.json` in order (kicker, question, hint, options, rows, chips,
  what Keel wrote, what was typed); every served respondent screen per link from `respondents[link].drawn` -- the
  screener its own screen, the gate with its story prompt and the AI link's spoken line, each item (the price with its
  up-front ladder from `served` and its plan), the idea / reveal cards, the follow-up. Earlier screens as kicker +
  question only; the scored screen in full.
- [x] T007 The personas: the founder-reader the `.sources.md` whole; the respondent-reader the person the walk took on
  the link (the first the entry names for it), their line from the sources (a bullet, else the paragraph naming
  them), the role (`PRACTITIONER` / `BUYER`), the decision-maker's title, and the entry's `context` fields.
- [x] T008 §G: one call per follow-up line of two answers or more, read from `brief.insights` (groups, `quotes`,
  `rawQuotes`), on the link its dimension was asked on, skipped while `themes_settled` says it is still grouping.

## FR-4 -- `make read-screens` (paid) -- `debe4d7`

- [x] T009 Refusals, each one sentence and exit 2: no `RUN`, a bundle without `backtest.json`, no founder screen, a
  missing `claude` binary, a failed one-word probe. No key is read (a test holds the source to it).
- [x] T010 The score file `quality/scores/<entry>/<yyyymmdd>-<scope>-r1-<cloud7>-v<routing>-<reader>.json`: the header
  (entry, scope, bundle, cloud / web sha, routing version read with `git show` at the bundle's cloud commit, rubric
  version, reader, cost, probe cost, seconds, calls, the entry yaml's sha and whether it matches the bundle's), the
  summaries, the flow answers, `insights` / `insights_note`, the screens, `unread` and `read_fraction`. Its path is
  printed. Every prompt and answer under `runs/<stamp>-read-<entry>/calls/`.
- [x] T011 `DRY=1` prints every prompt, writes them under the run folder, calls nothing, writes no score. `LIMIT=n` /
  `ONLY=text` make a partial run whose `score.json` stays in the run folder (never `quality/scores/`).

## FR-5 / FR-6 -- the table and the baseline -- `debe4d7`

- [x] T012 `quality/table.py` / `make read-table`: the head (overall, per audience, per scope, against 90%), rows per
  (scope, dimension, audience, kind) with the five means, 0s, entries with a 0, instead lines and the §1 fix location,
  weak rows marked and listed; the Insights rows per (scope, dimension); the trend per (entry, scope), last three files,
  ↑ ↓ =. Another rubric version set aside by name; a partial file refused.
- [x] T013 `BASELINE=1`: like with like (the baseline's studies only), each row's deltas, the verdict better / same /
  worse; refused without a baseline or at another rubric version. `--cut-baseline` (no make target: the founder's word)
  archives the old baseline under `quality/baselines/<date>.md`.

## FR-7 -- the rubric is a mark -- `580791f`

- [x] T014 `MARKS_VERSION` 21, calls 121-123: `read_rows()` fills every scorecard's `read` block (dry and real) from the
  latest score file per corpus entry at the current `RUBRIC_VERSION`; *not measured* otherwise; never in `ROWS`,
  `DEFAULTS` or `passed`. `marks.toml`'s v21 header and `[read]` table. `rescore.py` `OLDEST` stays 20.

## FR-8 -- nothing else moves

- [x] T015 No gate names the readers (a test holds `eval`, `eval-live`, `unit`, `sample`, `instruction-eval` and the
  matrix to it); `quality/` has no `test_*.py`; the back-test walk, the golden corpus, the journeys, the noise check and
  the routing table untouched. AGENTS.md names the readers as a widening of the instruction eval's place.

## Every pin moved

| Pin | Was | Now | Why |
|---|---|---|---|
| `test_instruction_marks` version, calls | 20; 1-90, 110-120 | 21; 1-90, 110-123 (+2 v21 tests) | FR-7 |
| `test_instruction_rescore` refusal words, OLDEST | *re-scored at v20*; `OLDEST == 20 == MARKS_VERSION` | *at v21*; `OLDEST == 20`, version 21 (+ a v20 bundle re-scores) | call 123 |
| `test_backtest`, `test_founder_walk_076`, `test_follow_ups_075`, `test_sample_export`, `test_recorded_path_074`, `test_study_scopes`, `test_guide_marks` | `MARKS_VERSION == 20` | `== 21` | FR-7 |

## The gate

| Run | Result |
|---|---|
| `make unit` at this commit | 3,590 passed / 1 failed / 53 skipped (master 3,543 / 55; the failure is sibling drift, above, and fails on master's tree too) |
| `make read-screens DRY=1 RUN=<keel-e2e-eval>/runs/20261024T184654Z-backtest-21-codyco` | 63 prompts printed (41 founder screens, 17 respondent screens, 3 whole-flow, 2 insight lines), no call, no score; output under `runs/dry-21-codyco/` (ignored) |
| the smoke, `make read-screens RUN=<same> LIMIT=1 ONLY=problem.prevalence` | 2 screens scored (founder `q-problem.prevalence`, respondent PRIMARY `gate`), 0 unread, `score_pct` 80.0, flagged 0; 3 CLI calls (the probe + 2), $0.1688 list-price equivalent on the founder's plan, 22.4 s; `score.json` in `runs/smoke-21-codyco/` only |

## Not to be scored (the coordinator, for the founder, 2026-10-28)

**The thirteen bundles of 2026-10-24 (entries 08-21) are NOT to be scored**: they were walked before the screener, at
scope ALL. The smoke's two calls on 21-codyco's bundle are a smoke only; its partial `score.json` never reaches
`quality/scores/`. The first scoring run is the coordinator's, on bundles walked on the current build, per scope.

## What did not hold

- *The refusal "without the reader's key"* (FR-4 as first written) is replaced by the coordinator's decision 1: the
  CLI door, refused on a missing binary or a failed probe.
- *The probe is a third call*: the smoke spent three calls, not two -- the probe the refusal rule needs (one word,
  $0.036).
- *The Insights grouping* is not in `themes_settled` (it carries counts); it is read from `brief.insights`.
- *The thirteen recorded bundles* are not the calibration set FR-6 named (see above); no baseline is cut.
- *`make unit` is not fully green* on today's siblings: one report-marks test fails on keel-cloud-docs' rebuilt
  `build/brief-facts/` (48 of 49), on master's tree as on this branch -- not this spec's to fix.

## Judgement calls

- J-1 **The booleans are code's**, derived from the scores, so a reader can never flag a screen its own scores clear.
- J-2 **R4 is `null`** on a screen with nothing to pick (a card, a text box), and `score_pct` counts only given scores;
  the parse refuses a `null` R4 where options are shown.
- J-3 **Partial runs never write under `quality/scores/`**: a smoke or a slice is evidence, not a score of record.
- J-4 **`read` is reported, never gating**: a score file judges a back-test bundle's served words, an instruction-eval
  run judges the instructions on the golden corpus; gating one by the other would fail every run without a file.
- J-5 **§G stays `RUBRIC_VERSION` 1**: it arrived before any score file existed, so no score of two rubrics can mix.
- J-6 **The readers widen the instruction eval's LLM place** in AGENTS.md (the judge's door, a ruler), so the count
  stays four, as the back-test widened S-012's.
- J-7 **The routing version** is read from keel-cloud's `model-routing.json` at the bundle's own cloud commit (`git
  show`, read only), `NA` when it cannot be; the entry yaml read today is checked against the bundle's sha256 and the
  match recorded rather than refused.
