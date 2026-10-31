# Tasks 106 -- The gallery holds three studies per example, each from its own walk, with seven people

Branch `106-the-gallery-holds-three-studies-per-example` (worktree `wt/keel-e2e-eval-106`, its own `make venv`), off
master `9f06e2f` (113's docs; 4,543 / 0 / 56). Built by Claude on 2026-10-30/31. Read only: keel-cloud-docs master
`1acc3791` (the back-test entries in `canon/designs/measured-beliefs/backtest/`, `FounderViewAssembler.status`),
keel-web master `98607db` (`src/lib/examples.ts`, `public/sample/index.json`: fourteen one-study rows, each with keel-web's
own `title` and `image`; `specs/151-three-study-pills-each-its-own-study/spec.md`). **No stack, no model, no paid call, no
walk, no `make gallery` into keel-web** -- every export here wrote under a test's `tmp_path`. Nothing merged into
master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `e7a616f` | FR-2: the walk sends seven people a study (`cycle.toml` `people = 7`, `PEOPLE=`, `study_people` narrowed) |
| `ff37fe7` | FR-1 / FR-2 / FR-3 / FR-4: three studies per example, the number in words, the gallery's own last score as the gate, provenance per study; 063's and 079's tests moved, CYCLE.md |
| `99e0f58` | FR-5: `tests/test_gallery_106.py`'s export half (42 tests in all) |
| the docs commit | this file and `AGENTS.md`'s spec-106 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| master `9f06e2f` against keel-cloud-docs `1acc3791`, keel-web `98607db` (this worktree, before any change) | 4,543 | 0 | 56 |
| **branch at `99e0f58` (the last code; the docs commit adds none), keel-cloud-docs `1acc3791`, keel-web `23c7596`** | **4,582** | **0** | **56** |

+39: `tests/test_gallery_106.py`'s 42, less three in `tests/test_gallery.py` (46 -> 43: the twenty-people refusal
retired, spec 071's five per-scope rows become one row test and three another-scope refusals);
`tests/test_quality_cycle_079.py` keeps its 38 (two acceptance tests and the scope-order test rewritten, none
added or removed). 4,543 - 3 + 42 = 4,582. keel-web moved from `98607db` to `23c7596` (146) between the two
runs; no failure came from it or from any other spec.

## The checklist

- [x] T001 **FR-1 three studies per example** (`evals/gallery.py`). `STUDIES` = `problem`, `solution`, `money`;
  `STUDY_SCOPE` = PROBLEM, SOLUTION, COMMERCIAL (`Run.scope`, `Run.study`). `export` groups the runs by entry and study
  (`_grouped`) and refuses a set that is not three studies per known entry, each once; `prepare` builds a `Slug` of three
  `Study`s (`prepare_study`: withheld reads, `interview.json`, the manifest, the figures), writes `OUT/<slug>/<study>/`
  (the 060 file set, `interview.json`, `manifest.json` each), and the index row: the problem study's fields at the top
  as before (`TOP_STUDY`; `scope` reads PROBLEM; `interview.links` the problem study's), then `studies: {problem,
  solution, money}`, each `{decision, howSure, pilot, price, answered, invited}` (`STUDY_FIGURES`). `three_studies` --
  `make gallery`'s and `make quality-accept`'s pre-filter -- sets aside by name a run of another scope (ALL,
  SOLUTION_COMMERCIAL), an entry given a study twice, an entry lacking one (*... never a partial one; nothing is written
  for it*), and the rest are written. `one_per_entry`, `--scope-order`, `cycle.toml`'s `scope_order` retired;
  `newest_runs` is the newest finished run of each study per entry, `(runs, one reason per entry lacking a study)`.
- [x] T002 **FR-2 seven people** (`quality/cycle.toml` `[cycle] people = 7`, held by `load_config`: a whole number from 1).
  `make quality-walk PEOPLE=<n>` (`--people`, `resolve_people`) overrides it; `plan_steps(..., people)` puts `PEOPLE=7`
  on every `make backtest`; `make backtest PEOPLE=` is `KEEL_BACKTEST_PEOPLE` (`backtest.people`, refused by name in
  `door_refusal`), `Backtest.people`, `backtest.json`'s `people` where set; `corpus_scenario.run` narrows the entry
  (`Entry.people_cap`) before `person_inputs`. `vectors_script.study_people`: with a cap, the first n of the people the
  scope sends on the person's own (FULL) link, in corpus order; the decision-makers never narrowed. `not_on_study` names
  the people past the cap with their own reason (`NOT_ON_STUDY["PAST_THE_CAP"]`), after the scope's; `capped`;
  `not_on_this_study` records them in one step. The cycle record carries `people` and the rerun line `PEOPLE=` only when
  the walk capped (a 079 record reads as it did: the fixture record is byte for byte).
- [x] T003 **FR-2 the number in words.** `DISCLAIMER` (`evals/gallery.py`) is *A simulated study inspired by {name} (Y
  Combinator {batch}): {people}, all simulated. The founder's answers, the people and everything they said are
  fictional, ...*; `people_words(invited, answered)` -- *seven people answered*, *one person answered*, *six of the seven
  people invited answered*, *none of the seven ...* -- `number_words` one to twenty (keel-web's `COUNT_WORDS`), digits
  past. `invited` is `participants` (the register's rows, `gallery.py:517` as was), `answered` the rows whose `status` is
  ANSWERED (keel-cloud `FounderViewAssembler.status`). Each study's manifest says its own; the row says the problem
  study's. `PARTICIPANTS` (twenty) and *the run invited N people; the disclaimer says twenty* are gone; the check
  refuses a manifest whose disclaimer is not its own study's sentence, and a study that invited nobody.
- [x] T004 **FR-3 the gate is the gallery's own last score.** `score_gate`: no score file at the current rubric version,
  or a flagged screen, refuses the study by name (079 FR-6 kept; `refuse_flagged` stays a parameter, never a flag);
  `bar_pct` (`--bar`) is off by default. `cycle_score` reads the runs' latest score files together as the cycle record's
  head does (`table.head`); `last_accepted` is the newest `provenance-*.json` that records `accepted.score_pct`; `gate`
  refuses below it (*the cycle's score_pct X% is below the gallery's last accepted Y% (cycle C, provenance-T.json) -- not
  promoted ...; nothing is written*), passes equal or above whatever the 90% bar says, passes the first acceptance and
  one recorded at another rubric version (never compared, said). `promote` is the one path (`make gallery` with
  `--scores`, `make quality-accept`): the readers' refusals said, the gate, three studies per entry, `export` with
  `accepted = {cycle, score_pct, rubric_version}`. `make quality-accept` holds the gate **before** it cuts the baseline
  (a refused cycle cuts nothing, writes nothing; exit 1) and calls `promote` with the scores alone (no bar);
  `--keep-flagged` / `--keep-under-bar` retired; `cycle.toml`'s `[gallery]` knobs retired and refused should one come
  back. `cycle.toml`'s 90% bar is untouched (the product's, the cycle record's).
- [x] T005 **FR-4 provenance and privacy as today.** `runs/gallery/provenance-<exportedAt>.json` is `{exportedAt,
  accepted, examples: [{slug, entry, cycle, studies: {problem|solution|money: {scope, run, cloud, web}}, renamed}]}`,
  outside OUT; the needles are every study's entry id and run name; the grep covers every study's bytes; *Simulated*,
  `inspiredBy` and the attribution on the row and all three manifests (the example's own attribution alike in all).
- [x] T006 **FR-5 tests** (`tests/test_gallery_106.py`, 42): the seven-people walk on the five cycle entries (B2B
  problem / solution the first seven; the B2B money study's deciders whole; 13-aircaps' first seven on its one link;
  ALL capping the person's link; no cap as before; the reasons; downstream names nobody past the cap; `PEOPLE=` refused
  by name; the runner, the journey and the Makefile carry it; `cycle.toml` and the record); three studies from one
  cycle's bundles; the row's `studies`; the refusal on a missing study; twice and another scope; the disclaimer's
  number; the gate (first, lower, equal, above, over the studies, flagged, `--bar`, another rubric version, pre-106
  files); `make quality-accept` end to end (three studies built, keel-web's keys and cover kept, the score recorded, the
  next lower cycle refused before the cut, an equal one passing); `--scores` alone; provenance per study.
- [x] T007 **063's and 079's tests moved, each change said.** `tests/test_gallery.py` exports the run of record as three
  studies (`three_studies`) and reads `OUT/fresco/<study>/`; the twenty-people refusal is retired (a comment says
  where it went); spec 071's per-scope row is the problem study's PROBLEM and another scope is refused.
  `tests/test_quality_cycle_079.py`: the settings (`[gallery]` empty, `people` 7); the fixture cycle's acceptance cuts
  the baseline and, neither entry whole, leaves the gallery (the build is 106's); the scope-order test retired into
  *refuses by name and retires the scope order*. `tests/test_backtest_host.py`'s runner pin re-pinned with why.
- [x] T008 **Docs.** `quality/CYCLE.md` steps 1 (seven people) and 5 (the gate first, three studies, the provenance as
  the gate's memory); the Makefile's `gallery`, `backtest`, `quality-walk` and `quality-accept` comments; the module
  docstrings (`evals/gallery.py`, `quality/cycle.py`, `evals/run_backtest.py`); `instructions/gallery_names.toml`'s
  header (the disclaimer is not a row's to write).
- [ ] Cycle 4 (`make quality-walk`, paid) and its `make quality-accept` into keel-web: **not run** -- the founder's word.

## Cycle 4's export, exactly

From the **main checkout** (`~/Documents/projects/keel-e2e-eval`, whose `runs/` holds the bundles and whose
`runs/gallery/` is the gate's memory), after the walk wrote `quality/cycles/<yyyymmdd>-<cloud7>.md`:

```
make quality-accept CYCLE=quality/cycles/<yyyymmdd>-<cloud7>.md
```

It passes `--scores` alone (`quality/scores`, no bar). Cycle 4 is the **first acceptance**: the four provenance files
under `runs/gallery/` today (2026-10-22 to 2026-10-24) are 063's lists and record no score, so the gate says *no
accepted score yet: the first acceptance passes* and records cycle 4's score_pct for cycle 5. A rehearsal that writes
nothing into keel-web or `quality/`: `make quality-accept CYCLE=<record> OUT=<scratch>/sample QUALITY_OUT=<scratch>/quality
PROVENANCE_DIR=<scratch>/prov`. The walk itself (paid, not this spec's): `make quality-walk ENTRIES=default
WHY="<his words>"` (DOOR=host for his plan) -- seven people a study by `cycle.toml`.

## What keel-web 151 reads

- `public/sample/index.json` `{generatedAt, count, examples}`; each row as before (its top-level `decision`, `howSure`,
  `pilot`, `price`, `assumptions`, `disclaimer`, `interview.links`, `scope` = the **problem** study's), plus `studies:
  {problem, solution, money}`, each `{decision, howSure, pilot: {optedIn, finished, percent} | null, price: {edgeSaid,
  chose, n} | null, answered, invited}` in that order. `title`, `image` and `tests` are kept from the snapshot's row.
- `public/sample/<slug>/<problem|solution|money>/<path>.json` -- `overview`, `plan`, `standings`, `roles`, `people`,
  `readings`, `readings/<batch>`, `invitations`, `invitations/<id>`, `interview`, `manifest` (the study's own disclaimer:
  *seven people answered, all simulated*; a B2B money study *eight ...*). No file at the slug's root but `cover.jpg`: the
  one-study layout's files are gone (the slug's folder is replaced whole), so the snapshot lands with 151.

## Where the spec and the code differ (the code's patterns followed)

- **The disclaimer's text is not in `instructions/gallery_names.toml`** (FR-2: *its disclaimer text moves*): it has
  always been `evals/gallery.py`'s `DISCLAIMER`, filled from the map's `inspired_by`. It moved there; the map's header
  says so and writes none.
- **`answered` beside `invited`.** FR-2 has the check read the study's `invited` and the sentence say *... people
  answered*. Both are read: where everyone invited answered (every study of the five cycle entries' first seven, and every
  decision-maker) the sentence is the spec's; where fewer did (a gate No on money alone is walked nowhere, spec 102) it says *six of the seven people
  invited answered*, never a number that is not so.
- **The gate's memory is the provenance file**, as FR-3 says, and so is per machine (`runs/` is ignored): accept on the
  checkout that ran the last one. `make quality-accept` holds the gate before it cuts the baseline -- a cycle below the
  gallery's last score is *not promoted* (the founder's word), so it is not the baseline either and the two never part;
  079's order stays for every other refusal (the baseline cut, the gallery left as it is). `make gallery --scores` run
  by hand records its score too: it is the gallery's own last score whichever command promoted it.
- **The cycle's score_pct** is the cycle record's head (re-read from its score files) in `make quality-accept`, and the
  runs' latest score files read together in `make gallery --scores` -- the same arithmetic (`table.head`).
- **The kept keys** (`title`, `image`, `tests`, keel-web 103 / 104 / 107) and `cover.jpg` are not in the spec; see below.
- **`refuse_flagged`** stays a parameter of `score_gate` (079's tests use it) but nothing passes `False`: no command
  line flag, no `cycle.toml` knob.

## What the spec did not foresee

1. **The B2B money studies send eight, not seven.** *On a B2B money study its deciders (seven today)*: the canon has
   eight decision-makers on 08-fresco, 10-palus and 21-codyco and seven on 17-expanse. FR-5's *deciders untouched* is
   built, so those three money studies invite eight and their disclaimer says *eight people answered*. Capping the
   deciders at seven too is one line in `study_people`, the founder's call.
2. **With a flagged screen refusing its study and an example being three studies, few entries survive.** Cycle 3
   (`20261030-fcec453`, 84.9%) had a flagged screen in at least one study of 10-palus, 13-aircaps, 17-expanse and
   21-codyco: read through 106's gate it would publish **Fresco alone**; cycle 1 (`20261028-f48f256`) **Codyco alone**.
   If cycle 4 is like them, the homepage holds one or two examples. FR-3 keeps the flag (*never published*); whether a
   flagged screen should drop the screen, the study or the example is the founder's word.
3. **Nine examples leave the index.** The cycle walks five entries; keel-web's index has fourteen. The export writes the
   index from the cycle's examples, so the other nine leave it (their folders stay under `public/sample/` until keel-web
   removes them). `make quality-accept` now says which (*left out of the index*), and the keel-web sentence counts them.
4. **063 never kept keel-web's own row keys.** The snapshot's rows carry `title` (107) and `image` (103) that keel-web
   wrote by hand; a re-export dropped both (079's acceptance kept only the cover file). The export now keeps `title`,
   `image` and `tests` on a refreshed row, and the slug's `cover.jpg` (moved from `quality/cycle.py` into the export).
5. **The first seven include gate Noes.** *The first seven eligible in corpus order* is built as `study_people`'s list
   narrowed, no skipping: 08-fresco's seventh (Jolene Pruitt) and 17-expanse's (Ingrid) answer the gate No, so those
   problem and solution studies read six stories of seven; every money study's seven answer.
6. **The provenance file changed shape** (a list -> `{exportedAt, accepted, examples}`). Nothing reads it but
   `last_accepted`, which reads a pre-106 list as no score: cycle 4 is the first acceptance on the main checkout.
7. **`scripts/backtest-host.sh` has no `--people`**: the walk calls `make backtest` itself, so nothing needed it.
8. **Two exports in one second share a provenance file name** (`exportedAt` is to the second; 063's, unchanged): the
   later overwrites the earlier, and `last_accepted` reads the later -- harmless for the gate, named here.
