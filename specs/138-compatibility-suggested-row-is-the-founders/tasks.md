# Tasks 138 -- Compatibility's suggested row is the founder's own

Branch `spec-138`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-138` (`.git` a file). Nothing paid.

- [x] T001 FR-1 `_founders_rows` gated on Adoption and Purchase friction.
- [x] T002 FR-2 `keel_added` folds the founder's rows; the false *Keel added* on a capitalised typed row goes.
- [x] T003 FR-3 `_choose_label`'s suggested skip gated the same way.
- [x] T004 FR-4 the tests (Palus' cycle 13 shape on Compatibility and on Adoption friction; `keel_added`).
- [x] T005 FR-5 `make unit` green; the gate's counts here: `5442 passed, 85 skipped in 260.01s (0:04:20)` (2026-11-04 16:33 ET), zero failed, on keel-cloud-docs master 7972c12a and keel-web master 4ccfc81 -- each the named master (e3e22a8d, d5b117c) plus one spec-docs-only commit (cloud 216, web 175: `specs/` alone, no source moved). Base master 11aa155 was red on two `test_decided_before_087` pins (D-2026-11-04-03..05 marked merged without the pins that count them), re-pinned here (the first gate with 138 in, before that re-pin: 5440 passed / 2 failed / 85 skipped). +9 tests in `tests/test_spec_138_compat_suggested.py`; `tests/test_choose_by_label_104.py` 21-codyco compatibility `keel_added` re-pinned to one row (FR-2: two of its three rows are the founder's reworded).
