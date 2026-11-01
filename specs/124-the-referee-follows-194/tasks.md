# Tasks 124 -- The referee follows keel-cloud 194 (the condition's clip)

Branch `123-the-referee-follows-193` (the one branch for 123-125; worktree `wt/keel-e2e-eval-123`), on spec 123's commit
`f054170`. Built by a builder (Claude, on the coordinator's brief) on 2026-11-01. Read only: keel-cloud-docs master
`2d848360` (194's tasks.md, `ClipKind`, `PassageComposer` -- `CHECKED_COMMERCIAL_ROUTE`, `CHECKS`, `YES_OR_NO`,
`conditionOf`, `condition`, `checks`, `compose`'s placement --, `canon/openapi-v2.yaml` at contract 57). **No stack, no
model, no paid call, no key read.** Nothing merged; the branch pushed after the spec's commit.

## FR-1 -- the condition's clip (`harness/interviewer_fake.py`)

- [x] T001 `KINDS` gains `CONDITION`, last, as `ClipKind` declares it (spoken, not in `UNSPOKEN`).
- [x] T002 `condition_clip(question)` = the question as served + *Yes or no.* (`PassageComposer.condition`), None where
  none; `condition_of(interview)` = a gated link's `gate.condition`, else `Interview.condition`
  (`PassageComposer.conditionOf`). The fake's length rule (`fake_seconds`) reads the clip as any other.

## FR-2 -- the walks that read the clips (`evals/interviewer_leg.py`, `evals/interviewer_marks.py`)

- [x] T003 The leg records each role's `condition` place (`_condition_place`: `gate` -- said after the problem passage,
  before the gate's ITEM -- or `idea` -- after the OPENING, before the idea) and the clip's words.
- [x] T004 IM3 (`spoken_order` / `_expected_kinds`) expects `CONDITION` there; a role whose set holds no CONDITION clip
  (a lock from before 194) is held to the order without it -- never refused for it.
- [x] T005 The framing step (`_framing_words`) holds the CONDITION clip's words whole, and reads a recording from before
  194 in 101's words (`with_condition=False`).
- [x] T006 `instructions/spoken.py` enumerates no clip kind, so nothing there moved (the spec named it in case).

## FR-3 -- the passages' words

- [x] T007 `problem_passage(topic, items, gated=True)`: *That's the problem. Take a moment with it. First a quick check
  or two that this is for you. Then I'll ask you {items} questions about it.* -- the items alone (the gate no longer
  counted); `checks(0)` the first sentence alone; an ungated part 1 keeps today's sentence.
- [x] T008 `opening(first, commercial_link, checked=True)`: *First a quick check that this is for you. Then the idea, and a
  few questions on the money side.* where the condition comes before the idea (the decision-maker's with a written one,
  money alone's person); the idea's close unchanged.
- [x] T009 `before_101`'s close reads past the checks sentence (the backfill stand-in still seeds 101's old words).

| Clip | Was (pinned here) | Now (`PassageComposer` at `2d848360`) |
|---|---|---|
| PROBLEM, gated (payroll practitioner, three items) | *... Take a moment with it. Then I'll ask you four questions about it.* | *... Take a moment with it. First a quick check or two that this is for you. Then I'll ask you three questions about it.* |
| OPENING, a condition before the idea | *... First the idea, then a few questions on the money side. ...* | *... First a quick check that this is for you. Then the idea, and a few questions on the money side. ...* |
| CONDITION | -- | *Do you run payroll for at least 50 employees? Yes or no.* |

## FR-4 -- contract 57

- [x] T010 The eval keeps no contract snapshot (56 moved nothing the harness reads, spec 119 T015; the tests read
  keel-cloud's `canon/openapi-v2.yaml` with `>=` pins). 57 is pinned the same way: `x-keel-contract` at least 57 and
  `InterviewerPlayer.clips.condition` present and optional.

## Tests

- New `tests/test_condition_clip_124.py` (13): 194's constants read from `PassageComposer.java` (concatenated constants
  joined); the clip, the checks and the checked opening in 194's *As composed* words; `condition_of` / `_condition_place`;
  `CONDITION` last in `ClipKind`; IM3 with the clip before the gate and before the idea, and a set from before 194 held
  without it; the framing words on a gated link, an old recording and the decision-maker's; `before_101` past the checks;
  contract 57.
- `tests/test_interviewer_marks.py::test_the_kinds_are_keel_clouds_own` (red since 194) passes unmoved.
- Re-pinned: `tests/test_follow_up_ladder.py::test_the_fakes_follow_up_lines` -- FOLLOW_UP is no longer the last kind;
  CONDITION follows it, as in `ClipKind`.

## Gate

`set -o pipefail; make unit` against keel-cloud-docs `2d848360` and keel-web `2b84758`, 16:55:32-16:59:29 ET:

`2 failed, 4899 passed, 54 skipped in 236.93s (0:03:56)`

One of the two was `test_follow_up_ladder::test_the_fakes_follow_up_lines` (its *FOLLOW_UP is last* pin), re-pinned in
this commit (the file alone: 61 passed). The other is spec 125's (`test_read_back_mirror_085::test_the_draw_mirror_reads_the_clouds_sources`, 195's
`droppedAsSpelt`); 125's tasks.md carries the zero.

## Not foreseen

1. **No contract snapshot to move** -- "the way 56 did" was nothing in the eval (no field read moved); 57 is pinned as a
   read of the cloud's yaml.
2. **The coordinator's decision of 2026-11-01** (194's tasks.md): the checks sentence is in the OPENING where the
   condition comes before the idea, never in the idea's close; the mirror follows the code as built, not 194's first
   letter.
3. **Money alone's person link** (FULL, no gate) also takes the checked opening (`checkedFirst` is *no gate and a
   condition*, whatever the kind), so `opening(..., checked=True)` reads it with `commercial_link` False.

## Owed elsewhere

- keel-cloud: nothing.
- keel-web: 160 plays the clip and counts it (spec 125 FR-2 follows it here).
- Staging: a re-lock (or a new lock) records the clip; a lock from before 194 is walked and scored without it.
