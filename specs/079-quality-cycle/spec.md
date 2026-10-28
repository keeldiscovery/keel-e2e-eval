# Spec 079 -- The quality cycle: one kick-off, a comparison, an adviser, a rerun, an acceptance that becomes the homepage

The founder, 2026-10-28: *"When I say kick off the instruction set -- a costly one, maybe every week or whenever a key
change happens -- we run it, compare the score with the previous one, have an AI model infer what should be changed,
rerun it, and once we are satisfied that output becomes the homepage examples. Seamlessly. It should not come from
your memory: the framework should support all this."* This spec makes the cycle a set of commands and committed files
in this repository, so a session with no memory of today runs it by reading `quality/CYCLE.md`. It builds on spec 078
(the readers, the score files, TABLE.md, BASELINE.md) and spec 063 (`make gallery`). Build on the founder's word, after
078 is merged. Every walk and every reader call is paid and runs only on his kick-off.

## Rules

- **FR-1 The runbook is a file.** `quality/CYCLE.md`: the cycle's six steps below, each with its exact command, what it
  costs, what it writes, and what the founder decides at it. `AGENTS.md` points at it under *The quality cycle*. A
  session that is told *kick off the instruction set* reads this file and nothing else; the file says so in its first
  line.
- **FR-2 Step 1, the kick-off: `make quality-walk ENTRIES=<ids> [BUILD=<cloud7>]` (paid).** Walks each named entry on
  the local stack with `make backtest ENTRY=` (spec 062, Keel's AI through the key in the shell, or `DOOR=host`), on
  the keel-cloud and keel-web checkouts as they stand (their shas recorded), then runs `make read-screens` over each
  new bundle (spec 078), and ends with `make read-table BASELINE=1`. Refuses without the key, without ENTRIES, or with
  a dirty keel-cloud checkout (a sha must name what was measured). Writes a cycle record
  `quality/cycles/<yyyymmdd>-<cloud7>.md`: the entries, the bundles, the score files, the table's head (score_pct per
  audience and overall), the cost and the time, and the comparison with the baseline (better / same / worse per row, FR-6
  of 078). The record is committed with the score files.
- **FR-3 Step 2, the comparison, is what the founder reads.** `TABLE.md`'s head after a walk carries three lines:
  *this cycle* (score_pct, flagged_pct), *the baseline* (the same), *the bar* (90%). Below, the weak rows with their
  fix location (the design's §1), and the rows that moved since the baseline with their *instead* lines. Nothing
  else is needed to decide whether to advise, rerun or accept.
- **FR-4 Step 3, the adviser: `make quality-advise CYCLE=<record>` (paid, one call per weak row).** An AI reader --
  the same bounded shape as the readers, `claude -p --model claude-opus-5-5`, `quality/readers/adviser.md` -- is handed
  one weak row at a time: the criterion that failed, the screens that failed it with their whys and *instead* lines,
  the fix location, and **the current text at that location** (the registry row's `founder` or `respondent` guidance, or
  the named section of the instruction file, read from the keel-cloud checkout). It answers with one proposed edit:
  the new text, three sentences of why, and which rung of the ladder it is (words / effort / split). The proposals are
  written to `quality/cycles/<record>-advice.md`, committed, **never applied**: the founder reads them and says which
  to take; a taken proposal becomes a keel-cloud spec (a registry row or an instruction file, with the spoken-form
  acceptance line where a respondent wording moves) built and merged like any other.
- **FR-5 Step 4, the rerun.** After the keel-cloud change is merged, `make quality-walk` again on the same ENTRIES: a
  new cycle record, compared against the baseline AND against the previous cycle (the record names both deltas). The
  loop is steps 2-4 until the founder is satisfied, or the table says the bar is met.
- **FR-6 Step 5, the acceptance: `make quality-accept CYCLE=<record>` (free).** On the founder's word only. Rewrites
  `quality/BASELINE.md` from that cycle's score files (the old baseline kept under `quality/baselines/<date>.md`), and
  runs `make gallery` from that cycle's bundles with `--scores quality/scores` (spec 063 amended here: a bundle whose
  latest score file at the current rubric version has a flagged screen, or a score_pct under the bar, is refused by name,
  and the gallery is built from the rest) into keel-web's `public/sample`. It prints what changed in the snapshot (the
  slugs refreshed, the slugs added and still missing a `gallery_names.toml` row or a cover) and the sentence the keel-web
  refresh spec starts from. The keel-web side -- the snapshot commit, the example frames re-pinned, the deploy -- is a
  keel-web spec per acceptance, light gate; `CYCLE.md` names its shape so it is never invented.
- **FR-7 Step 6, the cadence.** `CYCLE.md` says when a cycle is due: a registry or instruction change merged in
  keel-cloud, a routing table or model change, or a week since the last record -- and that none of these runs anything by
  itself: the founder kicks off. The cycle record's header carries *why this cycle* in his words.
- **FR-8 Everything on disk, nothing in anyone's memory.** The entries to walk by default (`quality/cycle.toml`:
  `entries = [...]`, the five of the baseline, then every entry 08-27 as they pass), the bar, the reader and adviser
  models, the rubric version, the gallery's refusal rule: all in files under `quality/`, all committed, all read by
  the commands. A session can answer *what is the current score, what changed, what is proposed, what is on the
  homepage* from `TABLE.md`, the latest cycle record, its advice file and `BASELINE.md`.
- **FR-9 Nothing else moves.** The journeys, the unit gates, the golden corpus, the noise check; no command of this
  spec runs from `make eval`, `make unit`, the matrix or a checker.

## Acceptance

`make unit` green (master at 078's merge): the cycle record is composed from fixture score files and a fixture
baseline; the adviser's prompt is built from a fixture weak row and a fixture registry row (dry run prints it, no
call); `quality-accept` refuses a cycle with a failing bundle by name and builds the gallery from the rest (fixture run
folders, as 063's tests do); the refusals (no key, no ENTRIES, dirty checkout, unknown CYCLE). `CYCLE.md` read by a
fresh reader (the coordinator) answers the four questions of FR-8 without the repository's history. tasks.md in
078's shape. The first real cycle on the founder's kick-off.

## Judgement calls, for the founder to overturn

1. The adviser proposes and never applies: a wording change in keel-cloud is a spec, with its gate, even when the
   adviser wrote the words.
2. One adviser call per weak row, not one for the whole table: a small prompt with the current text in it gives a
   concrete edit; a table-wide prompt gives an essay.
3. The bar (90%) and the weak rule live in `quality/cycle.toml`, changed by commit, so a record always names the bar
   it was held to.
4. `quality-accept` is free and local; the keel-web deploy stays a separate, explicit step with its own gate.
