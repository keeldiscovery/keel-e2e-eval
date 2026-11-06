# Tasks 142 -- The harness mirrors keel-cloud specs 230 and 231

Branch `spec-142`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-142` (`.git` a file), off master
`80826fc`. Against keel-cloud-docs master `1bbe210e` (231 at `21b896f9`, 230 merged on top); no keel-cloud checkout
edited. Nothing paid; no stack, no model, no key, no walk; the unit suite only. Not merged; master untouched. The corpus
yaml, `quality/decisions.toml`, the readers' rubric and `RUBRIC_VERSION` untouched.

| Commit | What |
|---|---|
| `590eaa7` | plan.md; FR-1 the digest, FR-2 E8's tail, FR-3's one moved pin |
| (this) | tasks.md: the gate |

- [x] T001 FR-1 the reader digest. `quality/readers/dimensions.md` copied byte for byte from keel-cloud-docs `1bbe210e`
  `src/main/resources/keel/dimension-cards.md`, sha256 `06fcd867112e8fc285e9361061895018fe4739597f33f638bb97481e25f74a53`
  (= `RespondentReview.CARDS_SHA256`; the Prevalence card's amendment, 231). `CARDS_SHA256_141` in
  `tests/test_cloud_219_228_mirror_141.py` moved from `2ddae90c...` to `06fcd867...`; it is the one constant the 213
  and 216 pins read for the current copy, so no other pin moved (`2ddae90c` left only in spec 141's tasks.md, history).
- [x] T002 FR-2 E8 (231). `instructions/wording.py`: `left_standing(unit)` mirrors `WindowFrame.leftStanding`;
  `packed_fault`'s state-word sentence now says *on a given {unit} or not* (was *day*) and ends on the tail; the
  head-verb sentence ends on it too. The cause, judgement, *still have* and verdict sentences unchanged, as in the
  cloud. Pins moved as `PrevalenceEventIsAMomentTest` moved: `test_a_head_verb_of_state_is_refused` (+ the tail),
  `test_the_unit_is_the_windows_and_have_is_read_whole` (*on a given working day;* inside, the tail at the end).
  Grep of `harness`, `instructions`, `tests`, `evals`, `quality`: no pin expects an E8 to end `RESULT_INVALID`, so none
  moved to the note.
- [x] T003 FR-3 230, checked and found already true. `evals/corpus_scenario._choose_label` / `keel_left_out` (104 FR-1,
  108 FR-2) read the founder's typed rows on the drafted list and stop by name where one is missing; the Answer's
  redraft is awaited by `_wait_calibration`, which reads `state == FAILED` and retries through `_retried`
  (`/calibration/{vector}/retry`, spec 062) while the journey has retries -- the Palus path. Nothing new read. One pin
  moved: `tests/test_cloud_212_mirror_136.py::test_the_instructions_say_what_the_mirrors_hold` read settled_by's three
  values in founder-lists.md, which 230 FR-4 cut as a restatement (the schema's enum); it now reads them off
  `SavedList.SETTLED_BY` and the instruction's settled_by line (*one at least `nobody`*).
- [x] T004 FR-4 the gate.

## Gate

`set -o pipefail; make unit 2>&1 | tail -1`:

- Before (master `80826fc` against keel-cloud-docs `1bbe210e`): **6 failed, 5597 passed, 81 skipped in 323.76s** --
  `test_cloud_211_mirror_133::test_nothing_else_in_the_cards_moved_and_the_clouds_copy_is_owed`,
  `test_cloud_212_mirror_136::test_the_cards_carry_the_one_clause_lines_under_prevalence_and_frequency`,
  `test_cloud_212_mirror_136::test_the_instructions_say_what_the_mirrors_hold`,
  `test_cloud_213_mirror_137::test_the_cards_are_the_vendored_copy_at_the_clouds_digest`,
  `test_cloud_216_mirror_139::test_the_cards_are_the_vendored_copy_at_216s_digest`,
  `test_cloud_219_228_mirror_141::test_the_reader_digest_is_the_clouds_vendored_cards`.
- After (`590eaa7`): **5603 passed, 81 skipped in 309.89s (0:05:09), 0 failed.** No new tests (pins moved in place).

## Judgement calls

- The spec named three red tests; six were red (the 212 cards-lines test and the 216 digest pin read the same cards;
  the 212 instructions test met 230 FR-4's cut). All six back to green, nothing else red.
- `left_standing` is a public helper so the pins quote it, as the cloud's tests quote `WindowFrame.leftStanding`.

## Left open

- None in the harness. The cloud's own open item (231: E7, E9 and E2's length still refuse past the repair turn) is
  the cloud's; no harness pin reads it.
