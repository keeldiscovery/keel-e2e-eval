# Implementation Plan: There is a door out, and the goodbye is proven at two seconds

**Branch**: `011-keel-disconnect` | **Date**: 2026-09-09 | **Spec**: [spec.md](./spec.md)

**Input**: [spec.md](./spec.md), keel-cloud `canon/designs/keel-disconnect-design.md` (§3.2, §4,
§5.2, §7, §8.4, §10 step 6) with `canon/designs/keel-skill-design.md` §11, and the two sibling
contracts this feature calls across: keel-connect-skill
`specs/002-keel-disconnect/contracts/skill-disconnect-output.md` (six outcomes) and keel-runtime
`specs/003-keel-disconnect/contracts/disconnect-cli-output.md` (four).

**On the artefact set.** `spec.md` + `plan.md` + `tasks.md`, the shape specs 004–008 and 012 use.
This feature adds one function to two modules, a tail to one scenario, one assertion to another,
and one stackless test file. It moves no versioned constant — `POLICY_VERSION` does not move,
because nothing about *scoring* changed. It needs no `research.md` (the two contracts are read,
not researched), no `data-model.md` (it introduces no data), and no `contracts/` of its own (it is
a **consumer** of two contracts that live in the repos that own them).

## Summary

Give the smoke an ending. S-001 already opens §1.0 by connecting a runtime through
keel-connect-skill's own script; it now closes §1.0 by stopping one through that skill's *other*
script, and asserts the four things §8.4 lists — the outcome, the absent heartbeat, the landing
line proven for the second time in one run, and `GET /v2/me` going false inside two seconds. That
last bound is the only end-to-end proof of the goodbye anywhere in the four repositories, and it
was written at two seconds from the start precisely so it could not pass without one.

**Technical approach**: split the verb, not the module. `stack.runtime.disconnect` keeps its
fallback for `make down`; a new `disconnect_via_skill_script` beneath it has none, and
`harness.connect.stop_runtime_via_skill` is the recorded-step wrapper the scenario calls. Nothing
else in the repo changes behaviour.

## Technical Context

**Language/Version**: Python 3.11+, as `stack/`, `harness/` and `evals/` already are.

**Dependencies**: unchanged. No new package, nothing new in `requirements.txt`.

**Testing**: `make unit` for everything stackless, `make eval K=s001|s008` for the live legs.

**Constraints**: this repo owns no product code, never writes to a sibling repository, and reports
cross-repo gaps as `runs/DRIFT.md` entries with a bundle.

## The four changes, and why each is where it is

### 1. `stack/runtime.py` — one verb, two callers

`disconnect_via_skill_script` is the extraction, not a new mechanism: it is the block `disconnect`
already had, lifted out and given a name, so the caller that must not fall through can reach it
without reaching the fallback. `disconnect` is now three lines: call it, return the answer if
there is one, otherwise the bundled runtime's own command. Both docstrings say which caller each
is for, because that is the only thing about the pair anyone will need to know later.

`HEARTBEAT_FILENAME` / `heartbeat_path` go here rather than in the scenario for the usual reason:
a scenario that spelled `runtime.heartbeat.json` itself would be a fifth place that name lives.

### 2. `harness/connect.py` — the way out, under the way in's rule

The module's opening rule is that this harness never shells `python3 -m keel_runtime` itself.
`stop_runtime_via_skill` is that rule applied to the disconnect, and §8.4 names the function. It
records one step with the `status` before and after around the outcome, so the transcript shows
the runtime that was there, what was said to it, and that it went.

### 3. `evals/test_s001_smoke.py` — the tail

Placed after the §1.10 download and before the corpus-hash bookkeeping step, so the journey reads
in order and the last thing the run does is still verify nothing moved underneath it. The
ordering deviation (4 before 3) is argued in the spec's clarification and asserted in the tests.

### 4. `evals/test_s008_bundled_runtime.py` — the probe becomes an assertion

One `if path == "staleness":` branch out, one `assert path == "goodbye"` in, and the module
docstring rewritten from *what this cannot prove tonight* to *what the fix made provable*. The
DRIFT entry it cites is amended in the same commit, and a stackless test holds the two to each
other so neither can quietly revert.

## Risks, and what each is worth

- **The two-second bound is a real clock on a real machine.** It passed at **5 ms** on the run of
  record, three orders of magnitude inside the budget, because the goodbye is a single bounded HTTP
  call the runtime makes before exiting (G2: one call, 2 s timeout, no retry). A bound this far
  from its limit is not flaky; a bound that started failing would mean the goodbye stopped
  happening, which is exactly what it is for.
- **S-001 now ends with no runtime running.** Every other scenario already starts one and handles
  all three connect outcomes (`authorization_started`, `connected`, `already_connected`), so
  `make eval-all` is unaffected — checked by reading each caller, not assumed.
- **A future keel-connect-skill without `keel_disconnect.py`** would fail S-001 loudly rather than
  silently falling through. That is the intended behaviour and the reason the two functions exist.
