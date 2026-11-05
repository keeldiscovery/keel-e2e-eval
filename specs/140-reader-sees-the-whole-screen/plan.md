# Plan 140 -- The reader sees the whole screen

Branch `spec-140` (worktree `/Users/athulrajeev/Documents/projects/wt/eval-140`, `.git` a file), off the spec's commit
on master `a619c72`. Read only: keel-web master `ec99fa93` (`src/components/calibration/ListQuestion.tsx`: the Choose
radio's `data-suggested` and `aria-describedby` -> `choose-{dimension}-why-{i}` (`calib__suggest`, `calib__suggest-k`,
`calib__suggest-why`), the Check row's `check-suggestion`, Commitment's one-step block (`listcheck__field`,
`commitment-note`, `commitment-smaller-step`, `commitment-smaller-step-add`, `commitment-answers` /
`commitment-answer`); `src/lib/translate.ts` for the words; `src/lib/founderLists.ts` `draftBody`), and the recorded
bundles of cycle 14 under `keel-e2e-eval/runs/` (copied, trimmed, into `tests/fixtures/spec140/`). No stack, no model,
no walk, no paid call, no key read; the unit suite only. No rubric, reader-instruction or `RUBRIC_VERSION` change.

| FR | Where |
|---|---|
| FR-1 | `evals/backtest.py` `READ_JS` (`choices`: every radio / checkbox option with `suggested` and `why`, the why read off the element `aria-describedby` names whose id carries `-why-`); `founder_screens` carries `choices`, `suggested`, `commitment` into the bundle; `quality/readers.py` `suggestion_said` (one function: *{label} -- Keel's suggestion: {why}*) used by the *Options:* and *Rows:* lines and the compact line. |
| FR-2 | `READ_JS` `commitment`: the step box (`step`), the smaller-step box with its frame (`smaller`: before / value / after) or its absence (`smaller: null`, `smaller_add` where the add button is drawn), the answers in order, the note; `AFTER_EDIT_FIELDS` keeps them on an edited Check; `quality/readers.py` `_commitment_lines`. |
| FR-3 | `harness/vectors_screens.py` `Corridor._press_primary`: the URL wait runs to `60 s * patience` (the seed's budget, 660 s on a back-test), the 409 second press kept; past 10 s the Save's seconds are noted in the transcript (`founder's Save took N s ...`) and kept in `Corridor.slow_saves`; the network settles after the move (`networkidle`, bounded, never fatal). |
| FR-4 | `stack/processes.py` `wait_or_restart` (one restart on a 500 or a timeout, said on stdout -- the walk log -- then the gate again, then `HealthGateTimeout`); `stack/web.py` `up` uses it, and a web that answers but not 200 on its own pid is restarted the same once. `quality/cycle.py`: `VITE_TIMEOUT` counted in `runs/.stack/web.log`'s bytes written during each walk (`Study.vite_timeouts`), summed into the head (`vite_timeouts`) and said beside the typos line. |
| FR-4b | `harness/vectors_screens.py` `sent_how` (the draft body's `how`, absent where the page sent none); `list_answer` keeps `seen["sent_how"]` when present; `evals/corpus_scenario.answer_boxes_faults` reads `answer` + `how` against the two boxes where `how` is present, the joined text where absent; `evals/backtest.py`'s answer record names `sent how`. |
| FR-5 | `tests/test_reader_sees_the_whole_screen_140.py` + `tests/fixtures/spec140/` (the six recorded screens and the suggestion words as the screenshots draw them). |
