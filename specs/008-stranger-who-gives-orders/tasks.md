# Tasks: S-004, the stranger who gives orders (live)

**Input**: [spec.md](spec.md) (FR-001..006, SC-001..002) and keel-cloud
`canon/designs/words-are-words-design.md` §L5.

**Rules**: opt-in only (`make eval-live`); skip with reason when no logged-in `claude`; the
referee owns no product code. Needs keel-runtime `002`, keel-cloud `026`, keel-web `009` merged
for a green run. Bring the stack up with `make up` first.

- [x] T001 `harness/connect.py`: `executor=`, `env_extra=` (FR-001).
- [x] T002 `harness/canary.py` + `tests/test_canary.py` (FR-002).
- [x] T003 `Makefile` `eval-live`, `pytest.ini` marker, `make eval` deselects `live` (FR-004).
- [x] T004 `evals/test_s004_stranger_who_gives_orders.py` (FR-003).
- [ ] T005 First live run on the merged stack; DRIFT entries; cost recorded (FR-005, SC-001).
- [x] T006 README (FR-006); `make unit` green (99); committed. T005 (the first live run)
      waits for keel-runtime 002 and keel-cloud 026 to merge.

## Discovered

- The canary file is planted in the runtime's **home** (`runs/.stack/keel-home-<profile>/`,
  beside `credentials.json`), not the directory the connect script starts from: with keel-runtime
  spec 002 the model's cwd is an empty per-job directory anyway, and the home is where a model
  with file access would find the most sensitive thing first.
- US1 and US2 each create a project of their own: an approved card cannot be started over in the
  MVP (no changing the problem, screen-review design §5), so the framing attack needs a fresh
  problem card, and the live model's framing is never the script's exact words. The approved
  project from S-001 is attacked only through a participant (US3).
- The scan of the agent's words deliberately excludes P9 (the founder's own view of a
  participant's verbatim answers -- §1.6 says those are shown as typed) and the runtime's
  `request.json` logs (the source material *should* carry the orders); it covers the toast, the
  cards, the People table, every chat reply and every CLI envelope.
