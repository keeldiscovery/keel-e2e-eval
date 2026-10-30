# Spec 101 -- The money study's people: the person's link opens with the idea card, and a B2B money study has only the decision-maker's link

Cycle 3's two remaining stops (both also cycle 2's), diagnosed 2026-10-30 from the walk's logs
(`runs/quality-walk/20261030T135615Z-20261030-fcec453/`):

1. **13-aircaps · COMMERCIAL** (`runs/20261030T152257Z-backtest-13-aircaps`, step *Harriet Coleman answers the interview,
   screen by screen*): on a money-only study the person's link (kind FULL, no gate) opens with the idea card -- the
   intro says *First, an idea, in three lines. Then a few questions on the money side.* -- but
   `harness/vectors_screens.py:2345-2347` walks the idea only `if interview.kind == "COMMERCIAL_LINK" and
   interview.idea`, so the walker goes straight to `_items` and waits 20 s for a question heading (`h1.iv-q`) that is
   not there.
2. **17-expanse · COMMERCIAL** (`runs/20261030T155319Z-backtest-17-expanse`, `KeyError: 'PRIMARY'` at
   `evals/corpus_scenario.py:2595`, outside a step): on a money-only study of a B2B entry the Sent register serves one
   kind only, the decision-maker's (`kinds: [COMMERCIAL_B2B "Operator"]`; keel-cloud 133: the person's own link is not
   offered where the money is the whole study and someone else decides), but the leg sends every corpus person on
   `labels[kind]` with `kind = PRIMARY` for the people who are not deciders. 08-fresco, 10-palus and 21-codyco money
   studies (B2B entries) stop the same way once 096 carries them past the cost step and the lock.

## Rules

- **FR-1 The idea card where it is served first.** The walker runs `_idea()` whenever the served interview carries
  `idea` **and no gate** (the money study's person link, kind FULL), as it does on a COMMERCIAL_LINK; a FULL link with a
  gate is unchanged (its idea comes after the gate, inside the parts as today). After keel-cloud 166 / keel-web 145 the
  same link also carries `condition`: the walker asks it before the idea whenever `interview.condition` is served,
  whatever the kind (spec 100 holds the inside/outside walk; here only the order).
- **FR-2 A B2B money study sends the deciders alone.** In `leg_people_and_links` (or wherever `:2595` lives), where the
  register serves no `PRIMARY` kind, the PRIMARY people are **not sent**: the step records them as *not on this study
  (money alone on a B2B entry: the decision-maker's link only, keel-cloud 133)*, the standings and the brief
  assertions read the deciders' answers only (the money items are theirs), and `PICKS_NEEDED` / the counts expect the
  deciders' number. A money-only study on a B2C entry (13-aircaps) sends every person on the one FULL link as today.
  A register with both kinds is unchanged.
- **FR-3 Nothing else moves.** The SOLUTION and PROBLEM walks, the decision-maker's screener leg (076), the marks.

## Acceptance

`make unit` green with ZERO failed (master's counts as 096's tasks.md records them: 4,003 / 0 / 53); unit tests on the
idea-first decision (kind × gate × idea) and on the people-to-send selection from a register with one kind and with
two. Then, on the local stack at keel-cloud 165 or later, `make quality-walk ENTRIES=08-fresco,13-aircaps,17-expanse
SCOPES=COMMERCIAL DOOR=host` and `ENTRIES=10-palus,21-codyco SCOPES=SOLUTION,COMMERCIAL DOOR=host` reach the end of
every walk (the coordinator runs them, paid, on the founder's word of 2026-10-30: *"wait for the entire eval study to
complete"*). Build on the founder's word, now, before the re-walk; one builder at a time.
