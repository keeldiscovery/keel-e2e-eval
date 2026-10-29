# Spec 087 -- Decided before: the founder's decisions are recorded, and a weak row he has already decided is snoozed, not advised again

The founder, 2026-10-29, after deciding every proposal of the second cycle's advice one by one: *"all the decisions we
made should be recorded so that the next time the cycle runs we don't show the same things and have to go through the
decision again ... whatever the agent found and we decided not to go ahead should be recorded, so that it's kind of
snoozed next time."*

Today the cycle (spec 079, `quality/cycle.py`, `quality/CYCLE.md`) scores every screen, lists every weak row, and the
adviser writes one proposal per weak row, every cycle, with no memory of what the founder said about the same row last
time. The record of 2026-10-29 lives only in this spec's companion file, written by hand.

## Rules

- **FR-1 The record.** `quality/decisions.toml`, one `[[decision]]` per decision: `id`, `cycle` (the record it was
  decided on), `proposals` (the advice numbers), `row` (scope, audience, dimension, screen; each a string, a list, or
  `*`), `fix` (the fix location as the cycle names it, or a free label for a product ask; a string, a list or `*`),
  `decision` (`taken` | `declined` | `held`), `spec` (the specs it became, free text, on `taken`), `until`
  (`spec-merged` | `never` | a cycle id), `why` (the founder's reason, in his words where he gave them). The file of
  record ships with this spec, holding the nineteen decisions of 2026-10-29. `make unit` refuses a file whose entry
  lacks a field, whose `decision` or `until` is not one of the three, or whose `row` names a scope, audience or screen
  the cycle does not score.
- **FR-2 The snooze.** When the cycle writes its record (step 2) and when the adviser runs (step 3), each weak row is
  matched against every decision whose `row` and `fix` match it (`*` and lists as sets; `dimension` `-` matches a row
  with none). A matched row is **snoozed** while the decision's `until` holds: `never` always; a cycle id through that
  cycle; `spec-merged` until the coordinator marks the decision merged (`merged = "<cloud or web sha>"` on the entry,
  written when the spec lands, so the next cycle measures the fix and the row competes again). A snoozed row is listed
  in the record under a new heading **Decided before**, with the decision's id, its word (`taken`/`declined`/`held`), its
  `why` and, on `taken`, its `spec`; it is not sent to the adviser and not counted in the advice's weak-row total. A
  weak row that matches no decision is advised as today.
- **FR-3 The adviser knows.** The adviser's prompt gains the declined decisions whose `row` is `*` or matches the row
  (their `why` in full) as *the founder has already said no to*, so a proposal on a neighbouring row does not reopen
  what was declined (the no-number rule; the short name for strangers; the shared decider; the occasion as a noun).
  A proposal that contradicts one is refused by the harness the way 081 FR-6 refuses a special case, naming the
  decision.
- **FR-4 The advice page.** The advice record lists the snoozed rows at its end under *Decided before*, one line each,
  so the founder sees what was not advised and why; the taken ones whose spec has merged since are not listed (they
  competed).
- **FR-5 The runbook.** `quality/CYCLE.md` gains the file and the rule in step 2 and step 3, and the coordinator's duty:
  after every merge of a spec a decision names, write `merged` on the entry; after every walk-through with the founder,
  add his decisions before the next advise.

## Acceptance

`make unit` green with ZERO failed (master's counts as the last spec's tasks.md records them): a unit test per `until`
kind on a fake record (snoozed, listed, not advised; a `spec-merged` entry with `merged` set competes again); one that
the adviser's prompt carries the declined `why`s; one that the file of record parses and every entry's `row` names
scored scopes and screens; `make quality-advise ... DRY=1` on `quality/cycles/20261028-f48f256.md` shows every weak row
of that cycle snoozed under a decision of 2026-10-29 (the whole page was decided) and sends nothing. Build on the
founder's word, given 2026-10-29.
