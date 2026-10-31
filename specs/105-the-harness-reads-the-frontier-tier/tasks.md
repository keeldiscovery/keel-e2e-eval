# Tasks 105 -- The harness reads the frontier tier, the new prices, and screens the back-test and probe entries

Branch `105-the-harness-reads-the-frontier-tier` (worktree `wt/keel-e2e-eval-105`), off master `8221cf8` (104, 106,
107, 108 merged). Built by Claude on 2026-10-30. Read only: keel-cloud-docs at `4d790648` (169 merged:
`model-routing.json` v14, `ModelRouting.FALLBACK` / `standingTier`, `InferenceCharge.VERSION` 13, the probe
`canon/designs/measured-beliefs/probes/169-banking-gaming.yaml`) and its `specs/169-.../tasks.md` *keel-e2e-eval pins
that must move*, the checklist below. **No stack, no browser, no model, no paid call.** Nothing merged into master; the
branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `8147930` | FR-1: the fallback mirror in `instructions/models.py`; S-012's comment |
| `c284d12` | FR-2: `PRICE_VERSION` 12 -> 13 in the mirror and both fakes, the prose, the pins |
| `b0d570f` | FR-3: `instructions/screen_entries.py`, `instructions/run.py`, the probe mark, the Makefile's examples |
| the docs commit | this file and `AGENTS.md`'s spec-105 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| 104's tasks.md record, **master** (`92c0b75` + 104) against keel-cloud-docs past 169 | 4,093 | 1 | 53 |
| **branch at `b0d570f` (the last code; the docs commit adds none)** | **4,143** | **0** | **53** |

The one failure master carries -- `tests/test_credits_at_begin_088.py::test_the_mirror_is_keel_clouds_charge_table`,
`13 == 12` -- is FR-2's and is cleared. The +49 are `tests/test_frontier_tier_105.py` (4,094 + 49 = 4,143); none removed. Run from the worktree with
`stack.toml`'s `keel_cloud` at keel-cloud-docs `4d790648`, in 4 min 27 s.

## FR-1 -- the fallback mirror

- [x] T001 `instructions/models.py:69` `FALLBACK = {"frontier": "standard"}`, keel-cloud `ModelRouting.FALLBACK`.
- [x] T002 `ModelTable.standing_tier` (`:153`), keel-cloud `standingTier`: the class's own tier where the host's
  `hosts` row pins it, else `FALLBACK`'s rung where the row pins that, else `None` (no pin). Only `frontier` falls, and
  one rung: a `standard` class on a host with no `standard` row is still no pin.
- [x] T003 `resolve` (`:166`) reads the model at the standing tier; `resolve_effort` (`:185`) reads the effort **at the
  tier the model stands on** (the class's own tier when no model stands), exactly as `ModelRouting`'s constructor does
  (`effortsOfClass`: `standsOn == null ? tier : standsOn`) -- model and effort together. So on v14 codex / copilot
  frame jobs are `gpt-5.6-terra` at `medium`, claude's `claude-opus-5-5` at `medium`. `resolve_kind`,
  `resolve_screen`, `job_map`, `effort_job_map`, `stamp`, `models_used` and `efforts_used` follow through them.
- [x] T004 The table is the file as read: `hosts`, `efforts`, `classes` and `names_for` unchanged; no frontier row is
  invented (asserted).
- [x] T005 S-012's per-job model check (`evals/test_s012_journey_through_a_host.py`, `routing_table.resolve_screen`)
  follows unchanged; its comment says so. The bundle's *row for this host* stays the file's row.

## FR-2 -- the price version

- [x] T006 `PRICE_VERSION` 13: `harness/interview_charge.py:24`, `harness/interviewer_fake.py:40`,
  `harness/contacts_fake.py:40`, each with the prose beside it (what 13 moved: `PROBLEM_INTERPRET` 13 -> 26,
  `SOLUTION_MECHANISM` 14 -> 28; no row these modules mirror moved), and `interview_charge`'s module docstring and
  `row_faults` docstring. CM2, CM3, IM1 compare against `fake.PRICE_VERSION` and moved with it.
- [x] T007 Pins: `tests/test_credits_at_begin_088.py` (`:3` prose, `:53` renamed
  `test_both_fakes_carry_price_version_13`, `:95` `"price_version": 13`), and the mirror test now also holds what 13
  moved (`PROBLEM_INTERPRET` 26, `SOLUTION_MECHANISM` 28 on keel-cloud's table); `tests/test_interviewer_marks.py:834`
  `(13, 400, 2_000_000, 400)`.
- [x] T008 The S-012 journey's prose (`:35`, `:1244`): §6.3's five-participant figure (1,355) is the classic walk's,
  unmoved at 13. No corridor sum is mirrored; no gate check was added (it would be 300).

## FR-3 -- the screen reads back-test and probe entries

- [x] T009 `instructions/screen_entries.py` (new). `load` (`:263`): for a **screen needle** (`wanted`: neither empty,
  the full eval, nor a kind word) the back-test entries (`corpus.backtest_dir`, read through
  `corpus.load_file(..., backtest=True)` and its refusals) and probes (`probes_dir`, `load_probe`) **the needle names**
  (`names`: its first `/` segment is part of the id). Only those files are read (a file is `<id>.yaml`), so a golden
  screen never depends on an unrelated file; an id that is also a golden one refuses by name.
- [x] T010 `build_cases` (`:315`): a back-test entry's cases on `BACKTEST_SCREENS` -- `CONTEXT_INTERPRET`,
  `PROBLEM_INTERPRET`, `SOLUTION_MECHANISM`, built by the golden builders (`instructions/context.py`), ids
  `<id>/<SCREEN>/run<N>`; a probe's on the frame screens its `probes` list names. The needle is applied as `-k` applies
  it. Every extra case carries `meta["source"]` (`backtest` / `probe`); a probe case its plant (`meta["probe"]`).
- [x] T011 `instructions/run.py`: `_all_cases` (`:175`) appends the extras' cases after the golden ones; `_prepare`
  (`:264`) loads them beside the corpus and returns them; `deterministic` reads `_golden(cases)` (`:189`) only;
  `extras.verify_unchanged()` after the corpus's (`:544`); the console names what was read
  (`screened beside the golden corpus (spec 105): back-test entries ... · probes ...`).
- [x] T012 **The probe mark** (`screen_entries.probe_mark`, `run._score_probe` `:841`), read off the case's **first
  turn** (never a redraw), from the probe's own `first_turn`: `NEEDS_INPUT`, `questions` (1) question, that names the
  planted term (`term_pattern`: the words as typed, spaces or hyphens, the last word in any plain inflection --
  *loot boxes*, *respawn*), and offers `readings` (2) readings joined as alternatives (an *or*). A COMPLETED first
  turn is a fault named for what it did: *a COMPLETED statement / card that keeps / rewrites the planted term ...
  without asking*. The mark goes into the case's `diff.json` (`source`, `probe`, `failed`, `line`).
- [x] T013 **The records name the probe apart from the entries**: the scorecard's `screen_entries`
  (`{backtest: [{id, path, sha256}], probes: [{id, path, sha256, plants}]}`, dry and real) and `probes` (one mark a
  probe case, real runs). A probe moves no row of the marks file.
- [x] T014 `Makefile`: the instruction-screen examples name the back-test and probe needles; `run.py`'s `-k` help.

## FR-4 -- nothing else moves

- [x] T015 `K=frame` (a kind word), `K=PROBLEM_INTERPRET` (names no extra id) and the full eval (no needle) build
  exactly the cases they built (asserted). Routing v14 reaches the quality score names on its own
  (`quality/readers.py:172`); the synthetic `v13` fixtures in `tests/test_quality_0{78,79,81}.py` are untouched. The
  gallery, the marks (`MARKS_VERSION` unmoved), the corpus readers and every journey are untouched.

## FR-5 -- tests

- [x] T016 `tests/test_frontier_tier_105.py` (49): the fallback on a v14-shaped table with a frontier class and no
  host row (codex and copilot on their standard row, model and effort; stamp writes both), only frontier falls and
  one rung, the effort read where the model stands, a missing host, keel-cloud's live table, S-012 reading the
  resolver; the price version in the mirror, both fakes and their prose; the screen's case list with a back-test entry
  and a probe (what is read, the ids, the kinds, the seeds, the full eval / kind word / golden needle reading nothing
  extra, a broken unrelated file never read, a colliding id refused, a broken probe refused, the records, a file
  changed in flight); the coordinator's four needles on keel-cloud's live canon; the probe mark on a NEEDS_INPUT
  (held; missing term, missing readings, two questions) and on a card / a statement (keeps, rewrites); `_score_probe`
  on the run's own path; a dry screen of the probe end to end on fixtures.

## Where the spec and the code differ (the code's patterns followed)

- **`backtest-r19/` is keel-cloud's build output, not a source.** It is `BacktestCorpusTest`'s JSON
  (`build/backtest-r19/`); the source is `canon/designs/measured-beliefs/backtest/*.yaml` at revision 19, which the
  eval already reads (`corpus.load(..., backtest=True)`, `make backtest`). The screen reads that.
- **An extra entry joins only where the needle names it.** The spec says the screen takes the back-test corpus and
  probes *beside* the golden corpus; taken literally `K=PROBLEM_INTERPRET` would screen 7 + 28 + 1 entries and the
  full eval would start screening 28 back-test entries it has no marks for. A needle's first segment must be part of
  the extra's id; a short needle (`K=1`) names many back-test entries -- the dry run prints them and the cost first.
- **A back-test entry is screened on the three interpretation screens, not all eight.** It carries no golden
  expectations and keel-cloud's corpus tests write no facts for it, so `COMPARE`, the deterministic marks and the
  scored screens have nothing to hold it to. `K=08-fresco` is 3 screens x N; `K=08-fresco/PROBLEM_INTERPRET` the one.

## Not foreseen by the spec

- **The probe mark is mechanical.** *Offers two readings* is an *or* in the one question; *which* two (the gaming
  sense, the banking sense) is recorded beside the mark (`question`, `gaming_sense`, `banking_sense`) for a reader,
  not judged -- no judge is asked. *Names the term* accepts the term's plain inflections (*respawn* for *respawns*).
- **A screen's verdict stays `passed: false`.** As on any `K=frame` screen today, the interpretation screens are
  rendered and validated, never scored, so every mark is unmeasured and a real run exits 1. The probe's outcome is
  the scorecard's `probes`, the case's `diff.json` and the console line (*probe held* / *probe FAULT: ...*), not the
  exit code.
- **The register and the HTML report do not list the extras.** `register_blocks` walks the golden corpus; the
  extras' produced statements and cards are in their case directories (`envelope.json`, `diff.json`).
- **An effort follows its model, never the class.** keel-cloud's code reads the effort at the tier the model stands
  on, so a host that pins a frontier model with no frontier effort runs it at the CLI's default -- never at the
  standard row's effort (pinned by `test_the_effort_is_read_where_the_model_stands`).

## For the coordinator (paid, on the founder's word; never run by this build)

With `stack.toml`'s `keel_cloud` at keel-cloud-docs master (past 169) and Claude Code able to serve
`--model claude-opus-5-5`; `DRY=1` first costs nothing and prints each prompt:

```
make instruction-screen HOST=claude K=08-fresco/PROBLEM_INTERPRET N=3 MODELS=exported WHY=instruction:169
make instruction-screen HOST=claude K=08-fresco/SOLUTION_MECHANISM N=3 MODELS=exported WHY=instruction:169
make instruction-screen HOST=claude K=10-palus/PROBLEM_INTERPRET N=3 MODELS=exported WHY=instruction:169
make instruction-screen HOST=claude K=10-palus/SOLUTION_MECHANISM N=3 MODELS=exported WHY=instruction:169
make instruction-screen HOST=claude K=13-aircaps/PROBLEM_INTERPRET N=3 MODELS=exported WHY=instruction:169
make instruction-screen HOST=claude K=13-aircaps/SOLUTION_MECHANISM N=3 MODELS=exported WHY=instruction:169
make instruction-screen HOST=claude K=169-banking-gaming N=3 MODELS=exported WHY=instruction:169
```
