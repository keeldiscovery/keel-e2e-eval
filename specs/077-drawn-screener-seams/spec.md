# Spec 077 -- The harness follows keel-cloud 146 (the drawn screener's seams)

The thorough pass of 2026-10-28 ran the six remote journeys against staging `3b25264` + `b50eb04`: five green, S-007
red at *the context is confirmed on the wire* (`corpus_scenario.py` ~412). keel-cloud 145 FR-4a draws the screener's
condition from the founder's WHICH PEOPLE on every confirm; on 07-mulchrun (*landscaping crew leads in the Dallas-Fort
Worth suburbs, spring season*, market US) it drew *are based in the Dallas* (cut at the hyphen) and the sentence came
back *..., who are based in the Dallas, when ...* -- the qualifier the core already keeps, said twice. DRIFT #99 (076)
is the same doubling on the decision-maker's chip. keel-cloud 146 (`specs/146-drawn-screener-seams`) closes both and
145's owed *when while*; this spec moves the harness with it. Contract stays 43; keel-web needs nothing.

## Rules

- **FR-1 07-mulchrun carries a code-drawn screener.** The cloud now draws *are based in the Dallas-Fort Worth suburbs*
  from the founder's words (146 FR-1), so every FULL link of S-007 serves the gate chip *Are you based in the
  Dallas-Fort Worth suburbs?* (YES inside) although the scripted CONTEXT_INTERPRET writes no condition. `SEGMENTS`
  (`harness/vectors_script.py`) gains 07's row -- the core as the card shows it (*Landscaping crew leads in the
  Dallas-Fort Worth suburbs, spring season*), that condition, that question, YES -- or the harness reads the chip off
  the wire where a row would mis-state what the fake writes; either way the walked people answer it and are counted
  inside, and S-007's confirm step holds: the sentence after confirm is the card's, word for word (146 FR-2).
- **FR-2 `read_back` says a qualifier once.** The mirror of `ReadBack.sentence` adds *, who {condition}* only where
  the core does not already carry the condition's qualifier (146 FR-2's rule: the core keeps the drawn part, or
  names its content words and numbers). 05-paidly's line is unchanged (*Freelance translators in the US, who work
  mostly for agencies, when ...*: the core lost it); 07's gains no clause. `segment_line` follows the same rule.
- **FR-3 `decider_chip` names the people once.** The mirror of the third-person chip (146 FR-3) puts the people's head
  before *you decide for*: `actor_plural` with its qualifier cut where one is found (*who ...*, *in {Place}*, an
  amount) and a word precedes it; whole where it carries none; *the people* where the clause would say what
  `actor_plural` says. S-006's decision-makers are served *Do the people you decide for work mostly for agencies?*
  (DRIFT #99 closed -- mark it closed in `runs/DRIFT.md`); the S-006 assertion that the question starts *Do the* and
  carries *you decide for* holds as written.
- **FR-4 "when" once.** Where the harness composes or pins a line that puts *when* before a circumstance (the
  understands sentence, the role's default line, the interview's topic line if any mark reads it), a circumstance that
  opens with *while*, *when*, *whenever*, *during* or *as* takes no second *when* (146 FR-4, 145 FR-3's five words).
  No corpus entry's circumstance opens with one today; the mirror still holds the rule, pinned by a unit test.
- **FR-5 Nothing else moves.** Marks versions stay (interviewer 12, report 3) unless a mark's pinned wording moves;
  REVISION stays 16 (146 lists any golden row whose sentence moved for the founder's revision 17 -- read its
  tasks.md and mirror nothing from it); no paid command; the noise check, back-tests and judge untouched.

## Acceptance

`make unit` green (master `ad540c3`: 3,528 passed / 55 skipped). Light gate: S-006 and S-007 on the local stack
against keel-cloud-docs master at 146's merge (the coordinator names the sha) and keel-web master `b50eb04`; S-005 as
the smoke if time allows. Remote six after the deploy are the coordinator's. tasks.md in 076's shape: tasks per FR,
every pin moved with why, the gate record, DRIFT #99's closure, what did not hold.
