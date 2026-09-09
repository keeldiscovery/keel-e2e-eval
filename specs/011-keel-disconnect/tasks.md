# Tasks: There is a door out, and the goodbye is proven at two seconds

**Input**: [spec.md](spec.md) (FR-001..007, SC-001..005, the three clarifications) with
[plan.md](plan.md).

**The siblings, read at**: keel-cloud `8acb805`, keel-web `b0a5015`, keel-runtime `638c0dc`,
keel-connect-skill `4eb0548` — with the **bundled runtime `0.1.0+638c0dc`**, which is the whole
reason this feature could go green tonight (`runs/DRIFT.md` #47).

**Rules** (AGENTS.md): this repo owns no product code and never fixes the product — a cross-repo
finding is a `runs/DRIFT.md` entry with a bundle. `POLICY_VERSION` does not move: nothing in
`evals/policy.py` is touched. The scenarios stay deterministic and the two named LLM exceptions do
not change in number or in name.

---

## Phase 1: one verb, two callers

- [X] T001 `stack/runtime.py`: `disconnect_via_skill_script` (FR-001) — the founder's own door,
      with `--home`, a scrubbed environment and **no fallback**; `None` when the script is absent
      or unparseable. `disconnect` rewritten in terms of it, `make down`'s behaviour unchanged.
      `VIA_SKILL_SCRIPT` and `DisconnectScriptMissing` beside it.
- [X] T002 `stack/runtime.py`: `HEARTBEAT_FILENAME` and `heartbeat_path` (FR-002), named where
      keel-runtime's `heartbeat.py` names them.
- [X] T003 `harness/connect.py`: `stop_runtime_via_skill` (FR-003) — one recorded step carrying
      the `status` before and after, the outcome returned verbatim, `RuntimeError` on
      `did_not_stop` and on an outcome that disagrees with `status`. Its docstring carries the
      one-sentence difference from `stop_runtime`, which is untouched.

## Phase 2: the scenarios

- [X] T004 `evals/test_s001_smoke.py`: the tail (FR-004) — `disconnected` with its pid and its
      `via`, the heartbeat gone, `/v2/me` false inside two seconds measured from the disconnect,
      the landing reading *No agent connected* a second time, and a second disconnect answering
      `not_running`. The module docstring gains the paragraph that says why the bound is two.
- [X] T005 `evals/test_s008_bundled_runtime.py`: `assert path == "goodbye"` (FR-005), the
      staleness branch removed, and the docstring rewritten from *what this cannot prove tonight*
      to *what the fix made provable*.

## Phase 3: the stackless half

- [X] T006 `tests/test_disconnect_tail.py` — 18 tests: the script-only path's vocabulary, its
      scrubbed environment, its two `None` cases; that `make down`'s door still falls through
      while the tail's refuses; the tail's outcome, its two failure modes and its transcript
      entry; `heartbeat_path` on both profiles; `make down`'s log line **and** its loud warning
      that still tears the rest down; and five source properties — the tail never shells the
      runtime's own command, it asserts all four of the design's things, the bound is measured
      before any page load, the second call is `not_running`, and S-008 asserts the goodbye.
- [X] T007 `runs/DRIFT.md` **#47 RESOLVED** (FR-006), citing both runs of record, the commit in
      keel-connect-skill that closed it (`4eb0548`) and the 5 ms the smoke measured. The entry
      keeps its original text below the resolution, as this file's rule is.

## Phase 4: the runs of record

One stack session, `make up` → `make eval K=s001` → `make eval K=s008` → `make down`, on
keel-cloud `8acb805`, keel-web `b0a5015`, keel-runtime `638c0dc` and keel-connect-skill `4eb0548`,
with the bundled runtime `0.1.0+638c0dc`.

| Scenario | Run | Result |
|---|---|---|
| S-001 smoke | `20260909T052003Z-s001-smoke` | **PASSED, 5.0/5** — the tail green, `/v2/me` false **5 ms** after `disconnected` |
| S-008 bundled runtime | `20260909T052154Z-s008-bundled-runtime` | **PASSED, not scored** — `"path observed": "goodbye"` |

- [X] T008 `make unit` green: **407 → 425**.
- [X] T009 `make down` printed
      `[down] (eval) keel-runtime: not_running (via keel-connect-skill/scripts/keel_disconnect.py)`
      — the founder's own script answering the teardown, with the runtime already gone because
      S-008 had used the same door.
- [X] T010 `README.md` and `AGENTS.md` amended: the smoke's tail, the two-second bound, and the
      runs of record above.

## What is left undone, and where it goes

- **`make down` has never been observed answering `disconnected`.** After a clean run there is no
  runtime left for it to stop, so its honest outcome is `not_running` — which is the idempotent
  answer, through the founder's own script, and is what the log records. The `disconnected` path
  is exercised by S-001's and S-008's tails, several times a run.
- **The *Agent lost* label stays unreachable.** keel-web has a third label for an agent session
  that ended without a goodbye; nothing distinguishes it from *No agent connected* today, and the
  design says that is a journeys question rather than a wire one (Appendix B).
- **S-009 and the packaging beds** are spec `013-skill-distribution`, the skill design's step 10.
- **The instruction eval and S-004** were not run: neither is touched by this feature and both
  cost real money.
