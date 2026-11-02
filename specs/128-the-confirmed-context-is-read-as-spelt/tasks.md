# Tasks 128 -- The confirmed context is read as spelt

Branch `spec-128` (worktree `wt/keel-e2e-eval-128`) on master `8ee0bb1`. Built by a builder (Claude, on the
coordinator's brief) on 2026-11-02. **No stack, no model, no paid call, no key read.** Nothing merged; the branch pushed
after each commit.

## FR-1 -- held as spelt

- [x] T001 `harness/typist.py`: `as_spelt`, `spelt_faults` through `instructions.spelling.same_word`.
- [x] T002 `evals/corpus_scenario.py` `leg_context`, the confirmed step: the four fields held as spelt (was
  `fields.get(key) == value`); the confirmed occasion against the card's field held as spelt (was `!=`).
- [x] T003 `evals/corpus_scenario.py` `context_reopened`: Edit's filled form held as spelt, its key set whole (was
  `edited.get("fields") == founder.context_fields`).

## FR-2 -- what is recorded

- [x] T004 `typist.respelled`; the confirmed step's seen carries `respelled`, and `j.changed["context_wire"]` too.
  `typist.leaks` unchanged.

## FR-3 -- typos off

- [x] T005 Equal text is held as spelt; no existing test re-pinned.

## FR-4 -- tests

- [x] T006 `tests/test_spelt_context_128.py`: one corrected typo passes, a swapped word fails, a dropped word fails, the
  exact text passes, `respelled` carries the corrected pair; cycle 8's 08-fresco served fields pass against its typed
  ones; the two steps' sources hold through `spelt_faults`.
- [x] T007 `make unit` green.
