# Spec 140 -- The reader sees the whole screen

Cycle 14 (quality/cycles/20261105-04d95c2.md, -2, -3; the founder's word 2026-11-05 09:00 ET: "all your
recommendations look good … go ahead"): six points, plus three under Compatibility, were lost because the reader was
told less than the screen shows -- a harness capture gap, not the product. Three walks also stopped early for reasons
the harness owns.

1. **Choose screens: Keel's suggestion unseen.** keel-web's `ListQuestion.tsx` marks the suggested radio on a Choose
   screen `data-suggested="true"` with its why under it (`aria-describedby` → `choose-{dimension}-why-{i}`, spec 097
   FR-4). `evals/backtest.py`'s capture reads suggested rows as `li.listrow--suggested` with `[data-testid=check-suggestion]`
   (Check lists, spec 139 FR-3) and `options(...)` as `[role=radio]` labels alone, so the reader's *Options:* carries no
   suggestion tag and no why. Five screens scored R7 1 for "no suggested row with a reason" while the screenshot shows
   both (08-fresco choose-compatibility, 10-palus, 13-aircaps, 21-codyco choose-compatibility; 13-aircaps
   choose-adoption_friction).
2. **The Commitment check: the step unseen.** The capture carries the two word counters (*7 / 9 words.*, *6 / 9
   words.*) and the *Keel will test* box, not the step box, the smaller-step box (`[data-testid=commitment-smaller-step]`,
   its *Yes, after … first* frame) or the *What strangers can answer* chips (`[data-testid=commitment-answers]`
   `commitment-answer`). 13-aircaps check-commitment was scored blind ("I can't read it to check").
3. **The Save wait.** `harness/vectors_screens.py` `_press_primary` waits 10 s for the URL to change; 17-expanse
   SOLUTION's idea Save ran a calibration refuse-and-repair (L29, ~17 s) and the walk stopped. The wait must cover a
   repair turn.
4. **The Vite hang.** The local dev server degraded from 00:06 ET (58 "transport invoke timed out after 60000ms" in
   runs/.stack/web.log) and both remaining 21-codyco walks stopped (a web health 500, a seed page that never drew).
   The cause is unknown; the stack must notice and restart web once before giving a walk up.

## Rules

- **FR-1 The Choose screen's suggestion.** The capture reads, for every `[role=radio]` option, whether it is Keel's
  suggestion (`data-suggested`) and its why (the element `aria-describedby` names, the `choose-…-why-…` one); the
  reader's *Options:* line for that row reads *{label} -- Keel's suggestion: {why}*, in both the founder-reader's full
  text and the compact one. A Check list's suggested row (spec 139 FR-3) reads the same words, one function.
- **FR-2 The Commitment check.** The capture carries the step box as drawn, the smaller-step box with its frame
  (*Yes, after {smaller step} first*) or its absence, and the strangers' answer chips in order; the reader's text names
  them (*Your step, as strangers hear it: …*, *Or a smaller step first: …* or *no smaller step*, *What strangers can
  answer: …*). The counters stay as guidance.
- **FR-3 The Save wait.** `_press_primary` waits for the network to settle and the URL to move, up to the walk's step
  budget (the same budget `seed` uses, 660 s), never a fixed 10 s; the step's note says how long the Save took when it
  passed 10 s, so a slow writer shows in the record without stopping the walk.
- **FR-4 The web health.** `stack/processes.py`'s health gate on keel-web, on a 500 or a timeout, restarts web once and
  waits again before raising; the walk log says so. The Vite "transport invoke timed out" line in web.log, seen during
  a walk, is counted in the cycle record's head beside the typos line.
- **FR-4b The Current solution draft's two fields.** keel-cloud 228 / keel-web 177: the page sends the Answer screen's
  two boxes as `answer` and `how` (the second `""` when empty). The browser-walk check in `evals/corpus_scenario.py`
  ("the draft's one Answer", ~L2061) reads the draft body's `answer` against `join_answer(what, how)` and would fault on
  every Current solution walk once 177 ships: it reads `answer` + `how` where `how` is present, the joined text where it
  is absent. The API path, which sends `answer` alone, keeps working through 191's split. This lands BEFORE any cycle on
  a web build at or after 177.
- **FR-5 Tests.** FR-1 and FR-2 on a recorded bundle (a fixture page per shape); FR-3 with a fake page that moves after
  15 s; FR-4 with a fake health endpoint that 500s once. `make unit` green, counts in tasks.md. The five screens above,
  re-read from their recorded bundles with the new capture, are listed in tasks.md with what the reader now sees (no
  model call: the text alone).
- **FR-6 Rubric.** No rubric or reader-instruction change; RUBRIC_VERSION stands, so cycle 15 compares with 14.

## Out of scope

The reader digest `quality/readers/dimensions.md` (it follows keel-cloud's cards when 219-227 land, their own task);
the Buyer and payer joined row.
