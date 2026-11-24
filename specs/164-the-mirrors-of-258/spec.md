# Spec 164 -- The mirrors of keel-web 258: the stranger-side reads of spec 161 moved to the screens 258 drew

Spec 161 was built beside keel-web 257 and before keel-web 258 merged (keel-web master `5a23ccf0`, then `1fdea165`
with the follow-up wait), so its stranger-side legs read the card and the pages as they were. The run of record of
2026-11-24 (`runs/157/6a50f661-0fab7131/20261124T203757Z`) failed the problem copilot leg on the card's walked record
(the card read at step `?` with the intro's words) and the orb and avatar legs on the No-sayer's why (a web race, fixed
in keel-web `1fdea165`: the on-the-spot follow-up waits for the route, `FOLLOW_UP_WAIT_MS`). This spec moves every
mirror keel-web 258's `tasks.md` lists under *Eval mirrors to move* (ten items, file and line) and re-runs the legs.
Nothing paid.

## Rules

- **FR-1 The ten mirrors.** Each item of keel-web `specs/258-the-four-questions-on-the-link/tasks.md` §*Eval mirrors
  to move* is applied as written: 1 the `pending_258` film-first branch retired; 2 `.rp-tookby` -> `insights-capped`;
  3 `report_marks` `capped` in place of `took_by`; 4 the Frequency chart's `data-chart="frequency"`, the five bands,
  the `data-for` pair and the caption; 5 the breakdown's bands cell, no Current solution row; 6 the card's Frequency
  bubbles as digits 1..5; 7 the card walk: two follow-ups a call, Frequency's `also` on Never, the gate's `followUp`
  opening the why on a No with only Importance after; 8 `interviewer_fake.owed` on `recency`; 9 the ways panel's
  DOM; 10 the nesting on `defined`, `calibrating`, `calibrated`.
- **FR-2 The card's walked record.** `harness/three_surfaces.py` / `calls_leg.py`: the card's step is read from the
  card's own passage kind and item (`gate`, `item`, `followUp`, `pilot`), never from its position, so the walked record's
  step 1 is the gate with *Did this happen to you?* and its two options; the one-script check passes against the orb
  and the face on the served and the walked records alike.
- **FR-3 The run.** `make unit` green with no new red; one local run of `make e2e-157 PROFILE=eval` on the stack
  (keel-cloud-docs at `8fc10e71`, the problem batch's commit, checked out detached by the integrator or by you in a
  temporary worktree the stack points at; keel-web `1fdea165`) with the problem legs green (orb, avatar, copilot) and
  every other leg as 161's run 4 had it; the bundle named in `tasks.md`. A red that is the product's goes to
  `runs/DRIFT.md`, never patched around.

## Acceptance
- `make unit` green; the problem legs green on the local run; `tasks.md` with the commits, the run and the judgement
  calls.
