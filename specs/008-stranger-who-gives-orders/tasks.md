# Tasks: S-004, the stranger who gives orders (live)

**Input**: [spec.md](spec.md) (FR-001..006, SC-001..002) and keel-cloud
`canon/designs/words-are-words-design.md` §L5.

**Rules**: opt-in only (`make eval-live`); skip with reason when no logged-in `claude`; the
referee owns no product code. Needs keel-runtime `002`, keel-cloud `026`, keel-web `009` merged
for a green run. Bring the stack up with `make up` first.

- [ ] T001 `harness/connect.py`: `executor=`, `env_extra=` (FR-001).
- [ ] T002 `harness/canary.py` + `tests/test_canary.py` (FR-002).
- [ ] T003 `Makefile` `eval-live`, `pytest.ini` marker, `make eval` deselects `live` (FR-004).
- [ ] T004 `evals/test_s004_stranger_who_gives_orders.py` (FR-003).
- [ ] T005 First live run on the merged stack; DRIFT entries; cost recorded (FR-005, SC-001).
- [ ] T006 README (FR-006); `make unit` green; commit with the trailers; no push.

## Discovered

(Record here anything the run taught that the spec did not know.)
