# Feature Specification: There is a door out, and the goodbye is proven at two seconds

**Feature Branch**: `011-keel-disconnect`

**Created**: 2026-09-09

**Status**: Implemented — S-001 and S-008 green against a live stack, runs of record named in
[tasks.md](tasks.md) and `README.md`.

**Input**: keel-cloud `canon/designs/keel-disconnect-design.md` (design of record, 2026-09-08),
§10 step 6: *"keel-e2e-eval, spec `011-keel-disconnect` — S-001's tail and `make down`. Last,
because it is the referee and needs 2, 4 and 5 standing. Its two-second `/v2/me` assertion is the
only place the goodbye is proven end to end; write it at two seconds from the start and let it be
red until step 4 lands, rather than writing it at thirty and never knowing."* The sections this
feature is a referee of are §3.2 (the four outcomes), §4 (the goodbye), §5.2 (the skill's second
script and its contract), §7 (invariants D1–D10, G1–G6, S1–S3) and §8.4 (this repo's own tests).

The siblings, read at these commits:

| Sibling | Branch | Commit | What this feature depends on |
|---|---|---|---|
| keel-runtime | `master` | `638c0dc` | spec 003: `keel disconnect` and its four outcomes. Spec 003 **second pass**: `_say_goodbye` is a real call now — `CloudClient.end_agent_session` exists, so the runtime's last act reaches keel-cloud. This is step 4, and this feature is the only place it is proven. |
| keel-connect-skill | `master` | `4eb0548` | spec 002: `scripts/keel_disconnect.py` and its six outcomes, `disconnected` among them. And the bundled runtime **refreshed to `638c0dc`** (`RUNTIME_VERSION` = `0.1.0+638c0dc`), which is what carried the goodbye onto the path a founder is on. |
| keel-cloud | `master` | `8acb805` | spec 033's goodbye endpoint and `agent_session.ended_at`; `keel.v2.connect.presence-threshold` = 90 s, which is the window the two-second bound exists to be nowhere near. |

## What changes, stated first

**The smoke could start a runtime and never stop one.** S-001 has opened §1.0 since spec 001 by
asserting that the landing reads *No agent connected*, connecting a runtime through
keel-connect-skill's own script, and asserting the landing reads *Agent connected*. It then walked
the rest of the journey and ended. The runtime it started was stopped, if at all, by `make down`
minutes later, and **nothing in this repository ever observed a founder leaving.**

Three things follow, and they are the whole feature.

1. **The way out obeys the way in's discipline.** `harness/connect.py` gains
   `stop_runtime_via_skill`, which shells keel-connect-skill's `scripts/keel_disconnect.py` and
   **never** `python3 -m keel_runtime disconnect` (§8.4, in as many words). It is deliberately not
   `stop_runtime`: that one is `make down`'s door and keeps the fallback a teardown needs.
2. **S-001 gains a tail**, and the fourth of its four assertions is the point of the whole spec:
   `GET /v2/me` reads `agent.connected` false **within two seconds** of the disconnect answering.
   keel-cloud derives that field from `last_seen_at` against a 90-second threshold, so only
   keel-runtime's last act can put a false there that fast. **This is the only place §4's goodbye
   is proven end to end**, in any of the four repositories.
3. **S-008's probe becomes an assertion.** It recorded `"path observed": "staleness"` and filed
   `runs/DRIFT.md` #47 rather than adapting around it. The bundled runtime has since been
   refreshed, so the path must now be `goodbye`, and #47 is RESOLVED citing the run.

## Clarifications

### Two functions for one verb — why not one? — **because they answer to different callers**

`stop_runtime` (spec 012 FR-003) prefers keel-connect-skill's script and **falls through** to the
bundled runtime's own `disconnect` when that script is absent, accepting both vocabularies
(`stopped`/`disconnected`, `timeout`/`did_not_stop`). That is right for `make down`: a teardown
that cannot tear a runtime down because a sibling moved leaves Postgres and two JVMs behind, and
`stopped` from one layer lower is still a runtime that is gone.

It is exactly wrong for S-001's tail. The tail exists to referee **keel-connect-skill's own
contract** — a script that is one of the four applications under referee — and `disconnected` is a
word only that script says. A tail that silently fell through to the runtime's own command would
go green while the thing it was written to prove was missing, which is the same failure spec 012
found and named (`runs/DRIFT.md` #48).

So: `stack.runtime.disconnect_via_skill_script` has no fallback and returns `None` rather than
guessing, `harness.connect.stop_runtime_via_skill` raises `DisconnectScriptMissing` on that
`None`, and `stack.runtime.disconnect` is unchanged for `make down`. One verb, two callers, and
the difference is written down in both docstrings.

### The design lists four assertions in an order this spec does not keep — **and says why**

§8.4 lists: (1) the outcome, (2) the heartbeat is gone, (3) the landing reads *No agent
connected*, (4) `/v2/me` within two seconds. The tail runs 1, 2, **4**, 3.

The bound is measured from the moment `disconnect` returned. Reloading the landing first is a real
browser navigation against a Vite dev server — hundreds of milliseconds at best — and would spend
the whole two-second budget before the first `/v2/me` call, leaving a bound that proves nothing.
Assertion 3 is a screen fact with no clock on it and reads identically half a second later. The
ordering is asserted in `tests/test_disconnect_tail.py` so it cannot drift back.

### `make down`'s outcome: asserted where? — **in the log, and in a stackless test**

Spec 012 already made `make down` disconnect and print the outcome. What this feature adds is that
the printed line is **checked**: `tests/test_disconnect_tail.py` runs `lifecycle.teardown` with a
fake `disconnect` and asserts the outcome *and the door that answered it* both reach stdout, and
that `did_not_stop` warns loudly while still stopping Postgres and the two JVMs. A teardown that
went quiet about which door answered would say nothing about whether the founder's own script was
ever exercised.

## User Scenarios & Testing

### US1 — the founder leaves, and Keel knows at once (P1)

A founder who has connected a runtime says "keel disconnect". The runtime goes; the machine says
so immediately; and the Keel it was talking to stops naming it as connected inside two seconds,
rather than waiting out a minute and a half.

**Acceptance** (`evals/test_s001_smoke.py`, the tail)

1. keel-connect-skill's `keel_disconnect.py` answers `disconnected`, carrying the pid it watched
   leave, with `via` naming that script.
2. `runs/.stack/keel-home/runtime.heartbeat.json` does not exist.
3. `GET /v2/me` reads `agent.connected` false within **two seconds** of (1).
4. The landing reads *No agent connected* — the same locator §1.0's opening step uses, so one run
   proves that line **both ways**.
5. A second disconnect answers `not_running` (D10).

### US2 — S-008 stops recording the debt and starts asserting the fix (P1)

**Acceptance** (`evals/test_s008_bundled_runtime.py` step 8)

1. `"path observed"` is `goodbye`, inside a window an eighth of keel-cloud's presence threshold.
2. **Local truth first** is still asserted either way (G3): `keel status` reads not-running the
   moment `disconnect` answered.
3. `runs/DRIFT.md` #47 is RESOLVED, citing both runs.

## Requirements

- **FR-001** `stack/runtime.py` gains `disconnect_via_skill_script` — keel-connect-skill's
  `scripts/keel_disconnect.py`, with this stack's own `--home`, a scrubbed environment
  (`AMBIENT_RUNTIME_VARS`, T-1 on the way out as well as the way in), and **no fallback**. It
  returns `None` when the script is absent or answers something unparseable. `disconnect` is
  rewritten in terms of it and behaves identically for `make down`.
- **FR-002** `stack/runtime.py` names the heartbeat where keel-runtime names it
  (`HEARTBEAT_FILENAME`, `heartbeat_path`), so a scenario can assert its absence rather than
  spelling the filename itself.
- **FR-003** `harness/connect.py` gains `stop_runtime_via_skill`: one recorded step, the outcome
  returned verbatim, `RuntimeError` for `did_not_stop`/`timeout` and for an outcome that disagrees
  with `status`, and `DisconnectScriptMissing` when the skill has no way out.
- **FR-004** S-001 ends with the five assertions of US1. The two-second bound is measured from the
  disconnect and spent before any page load.
- **FR-005** S-008 asserts `"path observed" == "goodbye"`.
- **FR-006** `runs/DRIFT.md` #47 is RESOLVED with both run bundles named.
- **FR-007** `make unit` grows, and the growth includes the ordering of the tail's own assertions,
  `make down`'s log line, and the two source properties no stackless test could otherwise hold.

## Success Criteria

- **SC-001** `make unit` green, up from 407 (landed at **425**).
- **SC-002** `make eval K=s001` green against a live stack, with the two-second bound held.
- **SC-003** `make eval K=s008` green with the goodbye path observed.
- **SC-004** `make down` prints a disconnect outcome and the door that answered it.
- **SC-005** Every cross-repo gap found is a `runs/DRIFT.md` entry with a bundle, never a
  workaround.

## What this feature deliberately does not do

- **It does not touch `stop_runtime`.** `make down` and S-002/S-005–S-007 keep the door that falls
  through, for the reason the clarification gives.
- **It does not make the landing distinguish a deliberate goodbye from a runtime that vanished.**
  Both read *No agent connected*, and keel-web's third label, *Agent lost*, stays the unreachable
  branch the design says it is (Appendix B) — that is a journeys question, not a wire one.
- **It does not add the packaging beds.** S-009, `make acceptance` and the four `dist/` trees are
  the skill design's step 10, spec `013-skill-distribution`.
