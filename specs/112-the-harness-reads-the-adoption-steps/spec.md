# Spec 112 -- The harness reads keel-cloud 171: the adoption frame, the marked suggestion, the founder's efforts in the screen

keel-cloud 171 (merged 2026-10-30; its tasks.md lists every pin): adoption friction's rows are the founder's efforts in
their order; one suggested step may follow, last, `suggested: true` with its why, never counted toward the 1 to 4 and
never the default belief (`SavedList.tested()` takes the first non-suggested row); the stranger's frame is **To use
{name}, you'd {step}. Would you do that, or not?** (or *To use it, …*), the clause cap now 10 words with the existing
fallbacks; a stored clause naming the idea where the founder's row does not is said with *it*; the writers say *it* and
never add the idea's name; `L5` allows one suggestion with a why (two refused, a missing why a repair), `L1` counts only
the founder's efforts.

## Rules

- **FR-1 The frame mirrors.** `instructions/spoken.py` `ADOPTION_ASK`, `_WOULD_DO` (~:418), `adoption_frame` (~:447-474),
  `framed` (~:491): the new frame around the whole step, clause at most 10, the fallbacks as the cloud's (drop a phrase
  set off by commas, then the question part, then *it*; past that the founder's row in the frame); `harness/vectors_script.py`
  `adoption_statement` (~:2714) and `gerund` (~:2655) -> the served *To use {name}…* with the *it* swap;
  `instructions/context.py:416` (the asked job's frame) and `tests/test_instruction_context.py:237`;
  `instructions/marks.py:1157` (v22 item 126) says the new frame; `tests/fixtures/gallery/expected-interview-fresco.json:139`.
- **FR-2 The suggestion.** `instructions/score.py` `SUGGESTED_ON` (~:293) gains `solution.adoption_friction` (and
  `tests/test_phrase_is_the_peoples_093.py:108`); the `L5` message (~:403) names Adoption friction, a missing why is a
  breach; `L1`'s `_draft_count` (~:326, :365) excludes the one suggested step. `evals/corpus_scenario.py` `keel_added`
  (~:1744) reads `suggested: true` on adoption rows instead of diffing labels (104's finding becomes *Keel suggested:
  '…' -- why*); `_choose_label` (~:1706) never lands on a suggested row unless the entry picked it.
- **FR-3 The founder-lists screen reads the entry's Answer.** `instructions/screen_entries.py` / `run.py`: a back-test
  entry's `CALIBRATION_<VECTOR>` case hands the writer the entry's typed Answer for the dimension (today `answers` is
  always empty, so the founder's efforts never reach the writer and 171's FR-6 screens prove nothing); the probe mark
  for 171: the founder's efforts first and as typed, at most one `suggested` row, last, with a why, no brand in any
  `asked`. The cases: `K=21-codyco/CALIBRATION_SOLUTION`, `17-expanse`, `08-fresco`.
- **FR-4 Tests re-pinned with why:** `tests/test_after_130.py:85-89, 188, 202`, `tests/test_after_131.py:389-402`,
  `tests/test_phrase_is_the_peoples_093.py:135-144, 171`, `tests/test_instruction_spoken.py:380`.
- **FR-5 Tests.** `tests/test_adoption_steps_112.py`: the frame named and unnamed, at and over the cap with each
  fallback; the *it* swap; `keel_added` on a suggested row; `_choose_label` skipping a suggested row; the screen case
  with an Answer. `make unit` ZERO failed (master's counts as 097's tasks.md records them).

## Acceptance

`make unit` ZERO failed. Build after 097, before 100; one builder at a time in this repo.

## Addendum 2026-10-30 -- keel-cloud 172's pins (merged after 171; small, taken here or by the next eval builder)

- `instructions/spoken.py:181` `served_escape` (and `item_escape` :169): Current solution's escape is read from the
  SERVED item (`{code, label}`), *I can't recall* (`cant_recall`, spoken *Or say you can't recall.*) where the list's
  `handed_off` call was false, *Someone else did it* otherwise -- the call never reaches the founder wire.
- Walks send the code served (a `someone_else_checks` where the served escape is `cant_recall` is refused *not this
  question's way out*); `tests/test_follow_up_ladder.py:172` and `tests/fixtures/corpus/10-fixture-b2b.yaml:212,381` stand
  for lists with no call. No price/contract pin moves.
- `tests/fixtures/gallery/expected-interview-fresco.json:78` is stale either way; re-record after the next screen.
