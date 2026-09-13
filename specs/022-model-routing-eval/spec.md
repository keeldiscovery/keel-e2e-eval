# Feature: the eval pins models the way the cloud pins them — `--models`

**Branch**: `model-routing` · **Created**: 2026-09-13 · **Status**: built, unmeasured (no run of
record has used it yet)

**Input**: keel-cloud `canon/designs/model-routing-design.md` (design of record, 2026-09-12,
amended 2026-09-13) — §4 the table, §5 the wire, §6 *no founder's pin*, §7 the process rule, §10
step 3, which is this repository's:

> **keel-e2e-eval**: `--models <file>` for `instructions.run`, written into each case's job
> `model` map (replacing the `KEEL_<HOST>_MODEL` environment the runner sets today); per-class
> pins in the report and the verdict (`models_used` per class), the screen target likewise;
> S-012 asserts the job log's `model_requested` equals the exported table's entry for the cell's
> host.

The siblings this half was written against, and what it assumes of the halves still landing:

| Sibling | What this feature depends on | Landed? |
|---|---|---|
| keel-cloud | `src/main/resources/keel/model-routing.json` (design §4, `hosts`/`classes`/`_tiers`, tiers exactly `light`, `standard`, `frontier`); `ScreenContractTool` exporting it as `model-routing.json` beside the three contract files; `InferenceScreen.jobClass()` mapping the ten screens to the five classes as `instructions/models.py::SCREEN_TO_CLASS` does | design §10 step 1, in flight |
| keel-runtime | 0.5.0 reads `request_payload["model"][<host>]` and passes it as its CLI's model flag; writes `model_requested`/`model_used`/`retried_unpinned` on the job's `envelope.json` or an `execution.json` beside it; drops the `KEEL_<HOST>_MODEL` variables, flags and config keys | design §10 step 2, in flight |

## What changes, stated first

1. **`instructions/models.py`** (new): reads the table in the design's §4 shape and refuses
   anything else — an unknown tier, an unknown class, a class this eval measures with no tier, a
   malformed `_tiers`. `resolve(host, class)` walks class → tier → the host's row; a missing host
   or tier is `None`, the CLI's default, never a failure. `stamp(cases, table, host)` puts the
   wire's **sixth key** on each case after its prompt is rendered:
   `case.payload["model"] = {<host>: <model>}` — exactly what `InferenceJobService` will send.
2. **`instructions.run --models FILE|exported`**: `FILE` is a table of one's own (candidates to
   screen); `exported` is the table keel-cloud's own exporter wrote beside the contracts, so a run
   of record can say it measured the cloud's table and nothing else. Refused beside any
   `KEEL_<HOST>_MODEL` in the environment: a run pins one way. `make instruction-eval` and
   `make instruction-screen` take `MODELS=…`.
3. **The bundle**: `verdict.json` gains `models_used` (`{assumptions, reading, brief}`, `null`
   where the host ran the class on its default; `null` altogether on a single-model run);
   `scorecard.json`'s `model` block gains `models_used` and `models_source`; `manifest.json`'s
   `model` gains `per_class` and `table`; each case's `envelope.json` gains `model_requested`.
   `report.html` names the per-class pins where it used to name one or none. `pinned_model` is
   untouched, so every run of record so far reads exactly as it did and `rescore.py` needs no
   change.
4. **The exported contract's optional fourth file**: `instructions/contract.py` reads
   `model-routing.json` beside `manifest.json` when it is there and carries it as
   `ExportedContract.model_routing` (`None` on an older export). keel-cloud's own
   `contracts/exported-contract-format.md` (spec 029) is where the file is specified; it is that
   repository's to amend, and this one reads what it finds.
5. **S-012** (`evals/test_s012_journey_through_a_host.py`): on a bundled runtime of 0.5.0 or
   newer with a keel-cloud checkout that carries the table, every job the cloud reports an
   interaction for must have requested **exactly** the model the table names for the cell's host
   and that job's class — `None` where the table has no entry, which is every job while the table
   ships empty. On an older runtime, or a checkout with no table, the step is a **note that says
   which**, never a pass. The referee also stops recording a `KEEL_<HOST>_MODEL` pin on a runtime
   that no longer reads one.
6. **An older runtime still gets the pin, its way**: keel-runtime below 0.5.0 ignores the job key
   and reads `self.model` on its executor when it builds the argv, so on such a runtime — asked of
   `keel_runtime.__version__`, never assumed — the per-case value is put there one case at a time
   (`apply_fallback`). A 0.5.0 runtime is left alone: the key is its only source of truth.

## Clarifications

### Why the payload key and not the environment? — **because that is the run the table claims**

The certificate a table row rests on (design §7) is a run through the path a founder's job takes.
The environment was keel-runtime 0.4.0's way in, one model for a whole process; the design removes
it, and an eval that kept using it would certify something no founder's runtime does.

### The table ships empty. What does `--models exported` measure then? — **the default, and says so**

Every class resolves to `None`; every case is sent without the key; `models_used` is three
`null`s. That is the same measurement as today's unpinned run, recorded as such. A row enters the
table only after a run of record with the candidate in a file of one's own.

### Per-class pins and the marks — **unchanged, MARKS_VERSION 6**

Nothing in the rubric moves. A `light` model on the readings is judged by the same anchoring mark
as any other; a `standard` model on the assumptions by the same recall and refusal marks. Which
model answered which class is a fact the bundle records, not a lever on the marks.

## Requirements

- **FR-001** `--models` reads the design's §4 shape whole; the three tiers `light`, `standard`,
  `frontier` and the five classes are the only names accepted; `_tiers` is tolerated when it is
  the ladder and refused when it is not.
- **FR-002** The pin is `request_payload["model"] = {<host>: <model>}`, sixth after the five keys
  `buildRequestPayload` writes, stamped after the prompt is rendered and never in it.
- **FR-003** A host or tier the table does not name pins nothing and is recorded as `null`.
- **FR-004** `--models` beside a legacy `KEEL_<HOST>_MODEL` is a refusal to start naming the
  variable; a bad table refuses before the pre-flight and before the lock.
- **FR-005** `verdict.json` carries `models_used`; the scorecard's model block, the manifest and
  each case envelope carry the same facts; `pinned_model` and every existing field are unchanged.
- **FR-006** `ExportedContract.model_routing` is the fourth file when present and `None` when not;
  `--models exported` refuses when it is `None`.
- **FR-007** S-012 asserts `model_requested == table entry` per job on a routing runtime with a
  table, and notes why not otherwise.
- **FR-008** On a runtime older than 0.5.0 the per-case pin lands on `executor.model`; on 0.5.0 it
  does not.

## Success criteria

- **SC-001** `tests/test_instruction_models.py` green, and every earlier instruction-eval test
  green with one deliberate change: the manifest's `model` object has two more keys.
- **SC-002** A screen with a candidates file — `make instruction-screen HOST=codex MODELS=<file>`
  — produces a bundle whose `verdict.json` names the per-class pins and whose case envelopes each
  carry `model_requested`. *(Not yet run: a Copilot screen held the lock while this was built.)*
- **SC-003** Once keel-cloud exports the table, `make instruction-eval HOST=<host> MODELS=exported`
  is the run of record the landing page may cite for that host's row.

## Tests

`tests/test_instruction_models.py` — the resolver (class → tier → model; missing host; missing
tier; the empty table), the file's edges, `--models`/legacy-pin exclusion, `exported` with and
without the fourth file, the sixth key's placement and the prompt's innocence, the runtime-version
fallback, the model block, the manifest, the report and the case envelope, the job-directory
reader S-012 uses, and the Makefile's threading. The manifest test in
`tests/test_instruction_host.py` is amended for the two new keys.
