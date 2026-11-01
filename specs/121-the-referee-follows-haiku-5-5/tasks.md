# Tasks 121 -- the referee follows the light tier to Claude Haiku 5.5

Built 2026-11-01 on branch `121-the-referee-follows-haiku-5-5` (worktree `wt/keel-e2e-eval-121`, `.git` a file, its own
`make venv`), off master `ea2a287` plus the spec commit `edb3c92`. Source of truth, read only: keel-cloud 190 on its
branch `190-the-light-tier-on-haiku-5-5` (worktree `wt/keel-cloud-docs-190`, head `ddb691f0`, not on master yet):
its `tasks.md` (the three requests, both rate cards, the HOLD table, *owed to keel-e2e-eval*), `model-routing.json`
v16, `InferenceCharge.java` (VERSION 15), `CreditPolicy.java` (298), `KeelsAiClassifier.java`, `InterviewerConfig.java`
and `build/haiku-5-5-requests.txt`. The worktree agrees with its tasks.md everywhere this spec reads it. keel-cloud-docs
master `cbc3ef8f` differs from 190's base `2e99c4f8` by one file (`specs/191-.../spec.md`), so the 190 worktree is
190-merged for every file this repo reads. **No model, no paid command, no key**: `make unit` only. Nothing merged into
master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `192590e` | FR-1: routing v16 mirrored -- docstrings, every fixture's light id, the 029 screen pin, S-012's comment; `tests/test_haiku_5_5_121.py` (v16) |
| `cf480c4` | FR-2: the noise check's classifier request (`request_body`, `answer_text`), the Makefile comment, `test_noise_check`'s pin, 121's request tests |
| `b2268f1` | FR-3: price version 15, the light prices and the New-project gate 298 mirrored, the pins re-pinned |
| the docs commit | this file and `AGENTS.md`'s spec-121 paragraph |

## Unit (the gate)

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| base `edb3c92` (master + the spec) against keel-cloud-docs `cbc3ef8f`, keel-web `f02595c` (08:23:13-08:27:20 ET) | 4,868 | 0 | 0 | 53 |
| branch at `b2268f1` against keel-cloud-docs `cbc3ef8f` (before 190), keel-web `f02595c` (08:37:11-08:41:19 ET) | 4,882 | 1 | 0 | 57 |
| branch at `b2268f1` against **keel-cloud-docs-190 `ddb691f0`**, keel-web `f02595c` (08:32:54-08:36:54 ET) | 4,887 | 0 | 0 | 53 |
| **the final tree (this commit) against keel-cloud-docs-190 `ddb691f0`**, keel-web `f02595c` (`set -o pipefail; make unit 2>&1 \| tail -3`, 08:42:39-08:46:36 ET, exit 0) | **4,887** | **0** | **0** | **53** |

The run against 190 points `stack.toml`'s `keel_cloud` at `../keel-cloud-docs-190` for the run only, restored after
(never committed). Against `cbc3ef8f` the one failure is `test_credits_at_begin_088::test_the_mirror_is_keel_clouds_charge_table`
(InferenceCharge.VERSION 14 there, 15 here) and the four extra skips are 121's own, by name, on a checkout before 190
(the live table v15, no `haiku-5-5-requests.txt`, the classifier still on temperature 0, the enum at 14): they clear
when 190 merges. +19 tests, all in `tests/test_haiku_5_5_121.py`.

## FR-1 -- routing v16 -- `192590e`

- [x] T001 `instructions/models.py` `resolve` / `resolve_effort` read the table as the file: nothing to change in code.
  On v16 a claude light case (`context`, `reading`, `asked`; `example_match` is dormant) resolves `claude-haiku-5-5` at
  `low` and `stamp` writes it `effort: {claude: low}`; Codex and Copilot light cases (`gpt-5.6-luna`) carry none. The
  three docstrings (`resolve_effort`, `efforts_used`, `stamp`) and `prompts.Case.effort`'s note and the Makefile's
  MODELS paragraph said a light case carries no effort because `effort` errors on Haiku 4.5; they say v6-v15 / v16 now.
  The reader never read `sampling`; a v15 table carrying it still parses (tested).
- [x] T002 Every fixture's light id `claude-haiku-4-5-20251001` -> `claude-haiku-5-5` (`test_instruction_models.py`:
  V6, V8_TABLE, v11, the runtime-kwarg test; `test_frontier_tier_105.py` V14; `test_backtest_host.py`'s
  `claude-haiku-4-5`). The runtime-kwarg test gains a v16 reading (`effort: low` reaches keel-runtime's
  `_model_kwarg`); the no-effort case stays as the v6-v15 shape.
- [x] T003 `specs/029-.../contracts/models-screen.json`: light `claude-haiku-5-5`, `efforts.claude.light` `low`, the
  `_comment` says why; still refused for naming no `asked` (call 84).
- [x] T004 S-012's per-job model check (`resolve_screen` on keel-cloud's own table) needs no change; its comment says
  v16's light jobs request `claude-haiku-5-5`, read off the table.

## FR-2 -- the noise check's classifier -- `cf480c4`

- [x] T005 `evals/noise/pipeline.py`: `CLASSIFY_MODEL = "claude-haiku-5-5"`, `CLASSIFY_EFFORT = "low"`,
  `MAX_TOKENS = 1_024`, `THINKING = {"type": "adaptive"}`; `TEMPERATURE` removed. `request_body` is the request as
  mirrored:

  ```json
  { "model": "claude-haiku-5-5", "max_tokens": 1024, "system": "<classify-answer.md>",
    "messages": [ { "role": "user", "content": "<KeelsAiClassifier.userPrompt's lines>" } ],
    "thinking": { "type": "adaptive" }, "output_config": { "effort": "low" } }
  ```

  -- 190's classifier record key for key (texts elided as its record elides them): no `temperature`, `top_p`, `top_k`
  or `budget_tokens`, one user message, no prefill. `answer_text` joins every `text` block by type (190's `textOf`),
  so a reply opening with a thinking block is read past it; a refusal has no text (unparsed, then retried once, as
  before). The run record's `classify` says `thinking` and `effort` for `temperature`. The cost line is Haiku 5.5's
  first card, $0.10 / $0.50 a MTok (a classify prompt is ~2 KB, far under the 100K card).
- [x] T006 The Makefile's `noise-check` comment (:132) says the 5.5 request; `evals/test_classifier_live.py`'s docstring
  says the light tier is Haiku 5.5 at low.
- [x] T007 `test_noise_check.test_the_classifier_is_called_as_keel_cloud_calls_it` reads 190's classifier source (no
  `.temperature(`, `ThinkingConfigAdaptive`, `OutputConfig.Effort.of(effort)`, the cap `1_024`), `InterviewerConfig`'s
  `routing.effortsAt("light")`, and the model and effort off keel-cloud's own routing table; skipped by name on a
  checkout before 190.

## FR-3 -- price version 15 -- `b2268f1`

- [x] T008 `PRICE_VERSION` 14 -> **15** in `harness/interview_charge.py`, `harness/interviewer_fake.py` and
  `harness/contacts_fake.py` (CM2 / CM3 / IM marks and the Begin row read it), each with its line of why.
- [x] T009 `interview_charge.py`: the module note and the gate note say 15 and **298** (was 300); `LIGHT_PRICES`
  `{CONTEXT_INTERPRET: 1, ASKED: 1}` (`LIGHT_PRICES_V14` 3 / 3 kept for the record), `FRAME_PRICES`,
  `CALIBRATION_QUESTIONS_CREDITS` and `NEW_PROJECT_PRICE` summed as `CreditPolicy` sums it, pinned against the enum at
  version 15 (skipped by name before it). The Begin row's `price_version` in `row_faults`'s note follows.
- [x] T010 Re-pinned at 15 with why: `test_credits_at_begin_088` (both fakes, the Begin row fixture),
  `test_frontier_tier_105` (the mirror and both fakes), `test_interviewer_marks` (charge v9's line). S-012's two price
  prose passages name 15.

## FR-4 -- the cache fields

- [x] T011 No cost note in this repo reads keel-cloud's settled log line: `evals/backtest.py`'s cost section reads the
  wire's `actual_cost_micro_usd` (and, on the host door, the CLI's own envelope usage, which already carries
  `cache_read_input_tokens` / `cache_creation_input_tokens`); `quality/cycle.py` sums the bundles' USD. So the light
  classes' `cache_read=` on the Keel door is **the coordinator's log check** (190: Haiku 5.5 caches from 512 tokens).

## FR-5 -- nothing else moved

Contract 56, corpus revision 22, `MARKS_VERSION` 24 (and every other marks version) stand. No mark summed the
context's or asked's 3 credits.

## Every mirror moved, with its source in keel-cloud 190

| Mirror here | Source line in keel-cloud 190 (`ddb691f0`) |
|---|---|
| fixtures' light id, the 029 pin, the v16 test table | `model-routing.json`: `"light": "claude-haiku-5-5"` (hosts.claude), `"light": "low"` (efforts.claude), no `sampling` |
| `pipeline.CLASSIFY_MODEL` / `CLASSIFY_EFFORT` | `InterviewerConfig.java:157` `routing.effortsAt("light")`; the routing row above |
| `pipeline.MAX_TOKENS = 1_024` | `KeelsAiClassifier.java:82` `static final long MAX_TOKENS = 1_024;` |
| `pipeline.THINKING`, `output_config` | `KeelsAiClassifier.params`: `.thinking(ThinkingConfigAdaptive.builder().build())`, `.outputConfig(... Effort.of(effort))` |
| no `temperature` | `KeelsAiClassifier` javadoc: *temperature 0 is gone -- Haiku 5.5 refuses any non-default temperature* |
| `pipeline.answer_text` | `KeelsAiClassifier.textOf(Message)` |
| `pipeline.request_body`'s shape | `build/haiku-5-5-requests.txt`, *the classifier (classify-answer.md)* |
| `pipeline.HAIKU_USD_IN / OUT` 0.10 / 0.50 | `ModelRates.HAIKU_5_5` first card (190 tasks FR-2's table) |
| `PRICE_VERSION = 15` | `InferenceCharge.java:272` `public static final int VERSION = 15;` |
| `LIGHT_PRICES` 1 / 1 | `InferenceCharge.java:122` `CONTEXT_INTERPRET (1, 579, ...)`, `:177` `ASKED (1, 663, ...)` |
| `NEW_PROJECT_PRICE = 298` | `CreditPolicy.java:45` (summed from the enum; its javadoc *1 + 26 + 28 + 3 × 81 = 298*) |

## What the spec did not foresee, and what was decided

1. **The resolver needed no change.** It reads `hosts` and `efforts` generically, so v16 moved behaviour (a claude
   light case now carries `effort: low`) without moving code; FR-1 is the prose, the fixtures and the tests.
2. **"Every fixture's light id moves" includes snapshot tables** (V6, V8, v11, V14), whose version and shape are what
   their tests read. Decided: the id moves in all of them (the shape -- no light effort -- stays theirs), and V8's
   comment says the id is today's; a grep test holds that no test or fixture names the old id but 121's own v15 table.
3. **The noise page template still says *Claude Haiku 4.5 at temperature 0*.** `evals/noise/page_template.html` is
   held byte-equal to keel-cloud's canon copy (`noise-capture-check-2026-10-26/page_template.html`), which is read
   only here. Left as it is; owed to keel-cloud's canon (below). The run record (`run.json`) says the 5.5 request.
4. **The effort as a constant or read from the table.** The product reads `routing.effortsAt("light")` at start; the
   pipeline keeps `CLASSIFY_MODEL` / `CLASSIFY_EFFORT` constants (the spec names the constant) and the test holds both
   to keel-cloud's own routing table, so a v17 that moves the light row fails `make unit`, not the paid run.
5. **No ledger mirror of the light charges existed** (no mark or walk sums CONTEXT_INTERPRET or ASKED). Decided: a
   small record-and-pin mirror in `interview_charge.py` (`LIGHT_PRICES`, `NEW_PROJECT_PRICE`) held to the enum, read by
   nothing at walk time -- so the next re-pricing fails a test instead of passing silently.
6. **The gate's sibling.** keel-cloud 190 is not on master; the gate ran against its worktree (`stack.toml` pointed
   there for the run only, never committed). Master `cbc3ef8f` carries only 191's spec.md beyond 190's base, so this is
   190-merged for every file read. Against master the branch fails the price version alone (expected until the merge).
7. **The classifier's 4 s budget and thinking latency** are not mirrored by the pipeline (its HTTP timeout is 30 s, as
   before); the paid run's latency column measures it.
8. **Commit attribution** follows the brief's `Claude Fable 5.1` trailer.

## Owed elsewhere (not touched here)

- **keel-cloud canon** (`canon/designs/noise-capture-check-2026-10-26/page_template.html`): *Claude Haiku 4.5 at
  temperature 0* -> the 5.5 request; then copy it here byte for byte (the move test holds the two equal).
- **The coordinator**: merge keel-cloud 190 and this branch together (against master before 190 this branch fails the
  price-version pin); the light classes' `cache_read=` in keel-cloud's settled log; the next quality cycle on the five
  catalog entries is the switch's run of record (cycle 6: 85.4%). `make noise-check` on Haiku 5.5 is paid and the
  founder's word (the 2026-10-26 certificate was Haiku 4.5's).
- **keel-web**: nothing.
