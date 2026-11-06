# Plan 142 -- The harness mirrors keel-cloud specs 230 and 231

Branch `spec-142` (worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-142`, `.git` a file), off master
`80826fc`. Read only: keel-cloud-docs master `1bbe210e` (231 at `21b896f9`, 230 merged on top); each spec's tasks.md
"Owed" section is the list of record. No stack, no model, no walk, no paid call, no key; the unit suite only. The corpus
yaml, `quality/decisions.toml`, the readers' rubric and `RUBRIC_VERSION` untouched.

## Where each FR lands

| FR | Where |
|---|---|
| FR-1 the digest | `quality/readers/dimensions.md` = keel-cloud's `src/main/resources/keel/dimension-cards.md` byte for byte (`06fcd867...`); `tests/test_cloud_219_228_mirror_141.py` `CARDS_SHA256_141` moves (the 213 and 216 pins read it). |
| FR-2 E8 (231) | `instructions/wording.py`: `left_standing(unit)` (`WindowFrame.leftStanding`); `packed_fault`'s state-word sentence says the window's unit and ends on the tail, the head-verb sentence ends on it too. Pins in `test_cloud_219_228_mirror_141.py` (`test_a_head_verb_of_state_is_refused`, `test_the_unit_is_the_windows_and_have_is_read_whole`) move as `PrevalenceEventIsAMomentTest` did. Grep: no harness pin expects an E8 to end `RESULT_INVALID`. |
| FR-3 230 | Read only: `evals/corpus_scenario._choose_label` / `keel_left_out` (104 FR-1, 108 FR-2) read the typed rows on the drafted list; the Answer's redraft is awaited by `_wait_calibration`, which reads FAILED and retries through `_retried` (062). One pin moves: `test_cloud_212_mirror_136.py::test_the_instructions_say_what_the_mirrors_hold` read settled_by's three values in founder-lists.md, which 230 FR-4 cut as a restatement -- the values are now read off `SavedList.SETTLED_BY`. |
| FR-4 the gate | `set -o pipefail; make unit 2>&1 \| tail -1`, counts in tasks.md. |
