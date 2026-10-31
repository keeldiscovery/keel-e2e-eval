# Spec 114 -- The lock walk picks Yes or No on the pilot screen, and reads the window card once

keel-web 146 (merged 2026-10-31; its tasks.md): on `define/ready/pilot` (money in scope only; no pilot screen on PROBLEM)
the screen is two cards `[data-testid=pilot-yes]` / `[data-testid=pilot-no]` (`role=radio`, inside
`[data-testid=pilot-pick]`, both `aria-checked="false"` on open, including on a revisit), `[data-testid=before-continue]`
reads *Continue* and is **disabled** until a pick, then *Continue · Yes* / *Continue · No*; `[data-testid=pilot-first-step]`
reads *Your first step: {step}* where the money is in scope and the step is stored; no textbox, no checkbox; *No pilot*
on a new project sends `PUT /word` with `pilotEnabled: false`, *Yes* sends nothing (the stored default is true). **Any
walk that pressed plain Continue on this screen now fails**, so cycle 4 would stop at the lock on every money study.
Also keel-web 147 (queued): the context card's muted *Counting the last {window}.* line goes where the sentence carries
the window; `evals/corpus_scenario.py:677` and `tests/test_drifts_95_97_closed.py:134` pin it (103 FR-4 left them).

## Rules

- **FR-1 The pilot pick.** `harness/vectors_screens.py`'s ready step (`ready-pilot`): on the pilot screen the walk reads
  the quoted step (where drawn) and the two cards, asserts neither is checked and Continue is disabled, picks **Yes**
  (the corpus's `pilot_opt_in` people expect the pilot line at the end; spec 067 FR-6) -- or **No** where the entry's
  founder opts out, if the corpus records that -- and presses *Continue · Yes* / *· No*; records `pilot: {step, picked}`
  for the reader (the screen stays a founder screen of record, kind `ready-pilot`). The PUT is asserted on *No* only.
- **FR-2 The window line.** Where keel-web master carries 147 (read the page: the muted line absent when the sentence
  ends *We'll ask about the last …*), `evals/corpus_scenario.py` (~:677) and `tests/test_drifts_95_97_closed.py` (~:134)
  expect no *Counting the last …* line on the card and the line on an old sentence; where 147 is not yet merged the
  pins stand -- the builder reads keel-web master and says which.
- **FR-3 Tests.** `tests/test_lock_walk_pilot_114.py`: the cards' states on open, Continue disabled, the pick and the
  label, the PUT on No and none on Yes, the quoted step; the window-line pin both ways. `make unit` ZERO failed
  (master's counts as 106's tasks.md records them).

## Acceptance

`make unit` ZERO failed. Build right after 106, before 109: cycle 4 cannot run without it. One builder at a time in this
repo.
