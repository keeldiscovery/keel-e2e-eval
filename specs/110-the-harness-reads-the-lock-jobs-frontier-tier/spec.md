# Spec 110 -- The harness reads keel-cloud 170: price version 14, routing v15, the gate's No, the chips, the cost frame

keel-cloud 170 (merged 2026-10-30, cloud master `8c53497f`; its tasks.md lists every pin): `RESPONDENT_QUESTIONS` on the
frontier tier (routing v15, `classes.respondent = frontier`; 105's fallback mirror already resolves it), 35 -> 70 credits,
`InferenceCharge.VERSION` 14 (lock gate 70, or 470 with the recording); the gate's No label *I didn't get to* retired
(`OccasionStem.noLabel`; the page draws its own No, the voice says *Yes or no*); the story clip says *Or say: I can't
recall one particular {occasion}, or I'd rather not say.* with the served chips in order; the cost item's chips read
*None* and *I can't recall* (wire codes `NOTHING` / `DONT_KNOW` unchanged), the value box's spoken line names the label;
`WindowFrame.subjectLed` treats a clause opening *any* / *some* as its own subject; the 17 commercial-chain fixtures
refreshed; the probe `canon/designs/measured-beliefs/probes/170-judgement-verb.yaml` (job `RESPONDENT_PART1`).

## Rules

- **FR-1 `PRICE_VERSION` 13 -> 14** in `harness/interview_charge.py:24`, `harness/interviewer_fake.py:40`,
  `harness/contacts_fake.py:41`; `tests/test_frontier_tier_105.py:134-137`, `tests/test_credits_at_begin_088.py:53-54,
  :98`; the mirror test adds RESPONDENT_QUESTIONS 70. The IM1 fault seed of -35 (`test_interviewer_marks.py:462`) is
  still a fault (any non-price charge is).
- **FR-2 The gate's No and the chips.** `evals/corpus_scenario.py:3571-3577` reads the served `noLabel`: only *I didn't*
  (the want case) is served now; the gate-No check expects the page's own *No*. `instructions/spoken.py` S6 reads the
  registry escape *I can't recall* and its module note's item 2 is rewritten; the story-clip mirror says the two chips
  as served, in order; `instructions/wording.py` `gate()` mirrors `subjectLed` (*did any of the cash …*, never *did you
  any of the cash*).
- **FR-3 The cost frame mirrors.** `harness/vectors_script.py` `cost_how_line` / the respondent cost item mirror: the
  frame from the entry's typed `lossPhrase` where one exists (the three entries' lines as 170's tasks.md records them:
  Palus *your team* … interest missed; Expanse word for word; Codyco *what share of the reservation calls were lost*),
  the neutral verb by the unit otherwise; the chips *None* / *I can't recall*; the value box's spoken label.
- **FR-4 The screen reader.** `instructions/screen_entries.py` / `run.py`: `BACKTEST_SCREENS` gains `RESPONDENT_PART1`;
  `load_probe` accepts a respondent probe (`job_context`); `build_respondent` passes `problem` and `condition` (today it
  never did, so every past screen of this job wrote the gate from the circumstance); the probe mark for 170: the event
  carries no verdict word and keeps the object (the probe's expected wording).
- **FR-5 Tests.** The version pins; the gate-No read; the chip sentence; `subjectLed` in `wording.gate`; the cost frame on
  the three entries and on no `lossPhrase`; the screen's respondent case and probe. `make unit` ZERO failed (master's
  counts as 098's tasks.md records them).

## Acceptance

`make unit` ZERO failed. Build after 098, before 097; one builder at a time in this repo.
