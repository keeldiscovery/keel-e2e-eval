# Feature Specification: the short journey, a golden founder, and the cell sets that pay for themselves

**Feature Branch**: `short-journey`

**Created**: 2026-09-11

**Status**: Implemented, **never run live**. `make unit` **821 → 911**, green. `actionlint` (1.7.12,
with shellcheck) is clean. **Nothing here spent a model request, ran a stack or touched AWS.**
`make eval-live` is still the founder's own command to type, and the merge that lands this carries
`[skip e2e]` so that the four new per-change cells are the founder's to start rather than this
change's to start for them. What this specification changes is **what a qualifying change buys,
whose founder it buys it as, and who gets told when it goes red.**

**Input**: the founder's decisions of 2026-09-11, in conversation, after the first cloud runs of
spec 020. Five of them, and the first is the one the rest follow from:

> *"Per change runs only S-012, but a short journey: the host leg plus the first model job — the
> PROBLEM frame's confirmation card landing — then disconnect. Full journey stays for nightly and
> weekly."*

And, on the sets:

> *"per_change = macOS and Windows × both hosts, 4 cells, Python 3.13, legs short. nightly = those
> 4 with the full journey plus Windows × both hosts on Python 3.9. weekly = all 18. Ubuntu leaves
> per_change and nightly — fewer than 5% of founders — and stays weekly."*

And, on the founder who walks it:

> *"S-012's founder comes from the golden corpus, not the payroll fixture."*

The siblings, read at these commits:

| Sibling | What this feature depends on |
|---|---|
| keel-cloud | `canon/designs/e2e-matrix-design.md` §5 (the matrix and its three schedules — **amended here**, see *Deviations*), §6.2 (`[skip e2e]`), §6.4 (where a verdict is recorded), §10 (what a cell costs), §14 decisions 4, 6, 11 and 12. And `canon/designs/measured-beliefs/corpus/` — the seven frozen golden entries, `03-lullaby` by default. |
| keel-runtime | nothing new. |
| keel-web | nothing new. |
| keel-connect-skill | nothing new; the plugin still comes from the public marketplace. |
| this repository | spec 019's `KEEL_JOURNEY_HOST` and `harness/agent_host.py`; spec 020's `matrix/cells.toml`, `matrix/cells.py` and `.github/workflows/matrix.yml`; spec 010's `harness/corpus_script.py`, which is **reused rather than copied**. |

## What changes, stated first

| File | What it is |
|---|---|
| `harness/agent_host.py` | Two more journey axes beside the host: `journey_legs()`/`LEGS`/`UnknownLegs` (`KEEL_JOURNEY_LEGS`) and `journey_entry()` (`KEEL_JOURNEY_ENTRY`). `bundle_slug(host, legs)` suffixes **only** the short one. |
| `evals/test_s012_journey_through_a_host.py` | The founder and the one person come from the corpus, through `harness/corpus_script.py`. `_land_the_card` is split out of `_walk_stage_live` and is where the short journey stops. The payroll fixture is gone from this module. |
| `harness/evidence.py` | `write_block(run_dir, name, record)`; `write_host` is now one line of it. The scenario writes a `journey` block: entry, its sha256, the title, the person, the legs. |
| `matrix/cells.toml` | **The new sets.** Four cells per change, six nightly, eighteen weekly, and a `legs` field. |
| `matrix/cells.py` | `Cell.legs`, defaulting to `full`; refused by name when it is neither; emitted in `as_dict` and shown by `make matrix-check`; **six new coverage rules** (below). |
| `matrix/notify.py` | **New.** Whether a run should open, comment on or close the `Matrix is red` issue, and with what body. It decides; it never acts and never reaches the network. |
| `.github/workflows/matrix.yml` | `[skip e2e]` honoured on this repository's own push; `KEEL_JOURNEY_LEGS` exported from the cell; keel-cloud's corpus directory sparse-checked-out for the cells that read it; and the `summary` job's issue, with `issues: write` scoped to that job alone. |
| `Makefile` | `eval-live` gains `LEGS=` and `ENTRY=`. |
| `tests/test_matrix_cells.py` | The coverage rules rewritten to the new sets; the `legs` field. |
| `tests/test_journey_through_a_host.py` | The two new axes, the shared card assertion, the corpus founder and the corpus person. |
| `tests/test_matrix_notify.py`, `tests/test_matrix_workflow.py` | **New.** The issue's four branches and two edge cases (32); the workflow's skip matcher, **run under bash** (23). |
| `README.md` | The commands, the env vars, the sets. |

### Why the journey got shorter, in one paragraph

A full journey is about **thirteen premium requests** or **`$1.50`** of API a cell, and the
per-change set runs on every merge to five repositories. What actually breaks when an operating
system, a Python or a host CLI moves is the **first half**: the marketplace install into a fresh
host home, the three words, the device flow, the executor the skill chose, and one model job coming
back in the right shape. The three stages, the person, the reading and the brief break when
*keel-cloud* moves — and keel-cloud moving is what the nightly is for. So a merge buys the part a
merge can break, four cells of it, and the night buys the whole thing on the same four cells plus
the floor. Nothing is measured less often than daily; one thing is measured more cheaply per merge.

### The six coverage rules, written down

`matrix/cells.py::coverage_problems` enforces these, `make matrix-check` runs it, the workflow's
`select` job runs it, and `tests/test_matrix_cells.py` holds the **real file** to them. They replace
§5.2's three.

1. **`per_change` is macOS and Windows, each host, once.** Four cells. Ubuntu is not in it.
2. **`per_change` runs the current Python** (the last value of the axis) on every cell.
3. **`per_change` runs the short journey, and runs S-012 alone.** A full journey or a corpus
   scenario in the cheap set is the cheap set stopping being cheap.
4. **`nightly` runs every `per_change` combination again at full length.** This is the rule the
   short journey rests on: what a merge measures in part, the night measures whole, on the same
   cell, within the day.
5. **`nightly` spends the 3.9 floor** (the first value of the axis) and **neither cheap set names
   an Ubuntu cell**. spec 004's floor moved from per-change to nightly; it was not dropped.
6. **`weekly` is the full product of the axes**, eighteen cells, **every one of them full length.**

### The founder is a corpus founder now

S-012 borrowed `evals/payroll_exceptions.yaml` — the *smoke's* fixture — for a project name, three
statements and a person's name. That was never wrong, and it is no longer right: the corpus is the
set this repository measures the product's judgement against everywhere else, and a journey that
walks a founder nobody else walks is a journey whose inputs no other run shares.

`KEEL_JOURNEY_ENTRY`, default `03-lullaby`, and everything it gives comes through
`harness/corpus_script.py`:

- `founder_inputs(entry)` → the project name (the entry's title), the market, and the three
  statements **verbatim**. It already refuses an entry with a missing statement, by name.
- `person_inputs(entry)[0]` → the entry's first person, their story text per anchor they wrote
  under, and their picks. It already refuses a person offered an anchor their role is not asked.

Reused, not copied: a second reader here would be a second chance to be wrong about the three
places the corpus and the wire disagree.

**What it does not change is the model's half.** On a live run the beliefs, the roles, the anchors
and the pick lists are the host model's own, invented from the founder's three statements. So the
person's stories go into the anchors the model wrote, **in order**; their picks are used wherever
the model's own option list happens to offer them, and the page's first option is taken where it
does not. Which of the two happened is **recorded in the bundle and asserted nowhere** — spec 016
FR-007 stands, whole.

## User scenarios

### A merge lands, and four cells spend two model jobs each

`select` reads `cells.toml`, picks `per_change`, and hands the workflow four cells: macOS and
Windows, Claude and Copilot, Python 3.13, `legs: short`. Each installs the plugin from the public
marketplace into a fresh host home, says *"keel connect"*, is approved at `/connect`, proves the
runtime is on its own host's executor by flag, creates *Lullaby — what the cry means* on the GB
market, types the entry's PROBLEM statement, and gets one confirmation card back with a non-empty
claim. Then the wire is asked whether anything was refused and whether every job completed, the
spend is written down, and the skill's own door out is used. Four bundles named
`s012-journey-<host>-short`.

### The founder types `[skip e2e]` and merges to this repository

`select` runs, reads the head commit's message out of the environment, matches the four words
literally, writes one line to the summary saying it was read, and stops. Until today the four
**senders** honoured those words and the **receiver** did not, so the same commit skipped the matrix
when it landed in keel-cloud and ran it when it landed here.

### A Windows cell goes red at 03:07 and the founder is asleep

The `summary` job collects the rows, sees a verdict that is not `PASSED`, finds no open issue
titled `Matrix is red`, and opens one — labelled `matrix`, carrying the run's own table and a link
to the run. The next night it is still red: the same issue gets another comment, not a second issue.
On Thursday everything passes: the issue gets *green again* and is closed. **It is information, not
a trigger** (M8, decision 12): nothing deploys, nothing rolls back.

### A run where the cells never started

The deploy failed, so no cell produced a row. The issue is **not** closed and none is opened: a run
that measured nothing is never green, and a deploy failure is not a red matrix.

## Requirements

- **FR-001 One scenario, three axes.** `KEEL_JOURNEY_HOST`, `KEEL_JOURNEY_LEGS` and
  `KEEL_JOURNEY_ENTRY`, all read once at import, all set by `make eval-live`. The first two refuse
  an unknown value **by name**; the third is refused by the corpus reader, with the ids there
  actually are.
- **FR-002 The short journey asserts exactly what the full one asserts up to its stopping point,
  and nothing else.** Held by `_land_the_card` being one function called from two places, not by
  two blocks that agree today. **Nothing new is asserted from the model's prose.**
- **FR-003 The full journey does not move.** Same legs, same order, same shapes, same wire, same
  bundle name (`s012-journey-<host>`, no suffix). `LEGS` defaults to `full`.
- **FR-004 Both lengths leave the same way**: no refusals, every job `COMPLETED`, the spend written
  down, and the skill's own `keel disconnect`. A short run is a shorter journey, never a laxer one.
- **FR-005 The founder and the one person are the corpus's**, through `harness/corpus_script.py`
  and no second reader. A corpus this run cannot reach is a **named failure**, never a fallback to
  another founder.
- **FR-006 The entry id, its sha256 and the legs are in the bundle** — `versions.json`'s `journey`
  block, and `facts.json` as strings the scorer skips and a reader does not.
- **FR-007 `legs` is a cell's field, optional, defaulting to `full`**, and is **not** part of a
  cell's id. The same cell short in `per_change` and full in `nightly` is one runner job in two
  sets, and a cell's id is still the founder it registers with the twin's picker.
- **FR-008 The sets meet the six rules above**, checked by `make matrix-check` on the Mac, by
  `select` on a runner, and by `make unit` against the real file.
- **FR-009 The receiver honours `[skip e2e]`** on its own `push`, read out of the environment and
  matched literally (`grep -qF`), on the `push` event only, with one line of summary saying so.
- **FR-010 One issue, four verbs, and a decision nothing can hide.** `matrix/notify.py` decides;
  the workflow does `gh issue list|create|comment|close` with no branches of its own; `issues:
  write` is scoped to the `summary` job, which restates `contents: read` because a job-level block
  replaces the workflow's.
- **FR-011 A run that produced no rows says nothing at all** — it neither opens an issue nor closes
  one. A cell job that *failed outright* wrote no row either, and that one counts as red.
- **FR-012 Nothing here is a trigger.** No deploy, no rollback, no production, and no issue opened
  by anything but a cell's own verdict. `KEEL_STAGING_ENABLED` remains the master switch, and the
  `[skip e2e]` on this change's own merge is the first use of FR-009.

## What is deliberately not built

- **No `LEGS=medium`, and no per-stage selector.** Two lengths, and the short one's stopping point
  is the founder's sentence, not a parameter.
- **No second scenario.** `KEEL_JOURNEY_LEGS` is a mode of S-012, as the founder asked; a
  `test_s013_short_journey.py` would be a second thing to keep in step with the first.
- **No corpus copy in this repository.** The corpus is keel-cloud's, read-only, hashed on the way
  in. A cell reaches it by a sparse checkout of one directory with a read-only token.
- **No change to the payroll fixture**, which is still the smoke's, still edited by this repository,
  and still what S-001 and the scenarios that use it use.
- **No issue per cell, no issue per run, no dashboard, no badge.** One issue, reused.
- **No `[skip e2e]` on `workflow_dispatch` or `schedule`.** A hand dispatch is the founder asking
  for it now; a schedule has no commit of its own.
- **No paid run.** Every command below is the founder's to type.

## Deviations from the design, and why

1. **§5.2's three schedules are replaced, not reconciled.** The design's table reads *"6 / 6 / 18,
   each OS once per host, nightly Ubuntu only"*; the founder's decision of 2026-09-11 reads
   *"4 / 6 / 18, Ubuntu weekly only, per-change short"*. The design says the sets are
   **[overrulable]** (decision 4: *"the founder can promote nightly to eighteen the day the numbers
   stop mattering"*), and this is that overrule going the other way. **keel-cloud's design has not
   been edited by this repository** — it is that repository's document — so the amended rules are
   written down here, in `matrix/cells.toml`'s header, and in `matrix/cells.py::coverage_problems`'
   own docstring, and the design's §5.2 is the stale paragraph until keel-cloud amends it.
2. **A cell now checks out keel-cloud's corpus directory.** Not in the design, and not in spec 020,
   which said *"the two private siblings are not needed here"*. They were not, until S-012's founder
   became a corpus founder and the nightly cell's S-005/6/7 needed the same directory — that one was
   a latent hole in spec 020, never run. It is a **sparse** checkout of
   `canon/designs/measured-beliefs/corpus` with the existing read-only `KEEL_SIBLINGS_TOKEN`, about
   60 kB, and a cell without the token warns loudly and then fails by name.
3. **The issue is a fourth place a verdict is recorded**, where §6.4 names three. The three it names
   are all places a founder has to go and look at; the founder asked to be told instead.
