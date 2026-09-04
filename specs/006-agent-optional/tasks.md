# Tasks: S-002, the agent-optional day

**Input**: [spec.md](spec.md). Rules as always: the referee owns no product code — over-gating
goes to `runs/DRIFT.md` with the screen and the wire side by side, never a harness workaround.
Runs on the **playground** profile. Gate: `make unit`, then `make eval K=s002 PROFILE=playground`.

- [x] T001 `harness/connect.py` (FR-002): `stop_runtime`, `reconnect`.
- [x] T002 `harness/browser.py` (FR-003): the landing's locked-reason reader, People's read-action
      state reader, and any step 3–8 gaps — added, never reshaped.
- [x] T003 `evals/preludes.py` (FR-004): `approved_project_with_one_read`, reusing S-001's own
      helpers where that is honest.
- [x] T004 `evals/test_s002_agent_optional.py` (FR-001): steps 1–8, the `§` citations, the three
      wire assertions.
- [x] T005 Run it: `make eval K=s002 PROFILE=playground` after an S-001 run, and from cold.
      Record what it finds. The spec's own prediction (People offers a read it cannot do) is a
      finding to confirm or refute, not an assumption to build around. **Confirmed both ways**:
      `runs/20260904T032807Z-s002-agent-optional/` (after S-001) and
      `runs/20260904T033552Z-s002-agent-optional/` (from cold) both fail at the same assertion,
      "§1.5/§1.6: the read action is disabled and states why, with no agent" -- US1 acceptance
      scenario 3 fails against the real product.
- [x] T006 `runs/DRIFT.md` for anything the product does wrong; `AGENTS.md`/`README.md` gain S-002.
      Three findings: #17 (blocking -- the predicted one, confirmed), #18 (non-blocking -- a stale
      reading-batch toast reappears on later People visits), #19 (non-blocking, worked around by
      logging out and back in -- a silently-reconnected runtime never rebinds an already-open keel
      session).
- [x] T007 Gate + commit in the house style with the trailers; no push. Report: the run id, the
      score, every DRIFT entry, and whether US1 scenario 3 passed or failed.
