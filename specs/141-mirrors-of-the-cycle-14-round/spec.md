# Spec 141 -- The harness mirrors keel-cloud's cycle 14 round

keel-cloud specs 219, 220, 221, 222, 223, 224, 225, 226, 227 and 228 (the cycle 14 round; the founder's word 2026-11-05)
moved frames, caps, rules and the dimension cards. The harness pins several of them and reads the cards as its reader
digest; nine tests on master went red the moment keel-cloud master moved (spec 140's gate names them: the three
cards-digest pins of the 211/213/216 mirrors, `cloud_198_mirror_130`'s soft yes, `corpus_r19`, two in
`instruction_spoken`, `lock_frontier_110`, `money_cards_redrawn_118`). This spec brings every mirror to the cloud as
merged and must land before cycle 15 walks on it.

## Rules

- **FR-1 The reader digest.** `quality/readers/dimensions.md` is a byte copy of keel-cloud master's
  `src/main/resources/keel/dimension-cards.md` at the sha tasks.md names; its sha256 equals keel-cloud's
  `CARDS_SHA256`. One task, run last, once every cloud spec of the round is merged.
- **FR-2 Relative advantage (219).** `instructions/spoken.py` `advantage_stem` / `hard_case`: the anchor is *Think of
  {hard_case}.* first where the study holds one (*the last time …* said *the most recent time …*), then 214's stem
  anchor, then 198's at-stake; `instructions/corpus.py` `ADVANTAGE_BELIEF_TEMPLATE` / `advantage_belief` take
  `{hard_case_theirs}` where the study holds one; `harness/vectors_script.py`: the scripted PROBLEM_INTERPRET result
  may carry the six clause fields and the Prevalence results the two hard cases; the gate of a study without the
  problem's questions reads the card's clause where the card writes one.
- **FR-3 Price (220).** No frame pin moves (none quotes it); `instructions/chain.py` `price_belief` already names the
  idea. A test that the walked Price question names the idea on a study that holds a name.
- **FR-4 Commitment (221).** `instructions/spoken.py` `STEP_OPTION_MAX_WORDS` 9 → 11; `first_yes` cuts at 9;
  `_second_step` holds the smaller step to 11 less the frame and says a verb-first step in its -ing form;
  `commitment_answers` mirrors `restatesTheStep` with the act; `instructions/step_cost.py` mirrors `DATA_ACTS`;
  `instructions/marks.py`'s revision-16 note on the two cut golden options is retired (Lullaby's Yes whole);
  `tests/test_instruction_spoken.py` pins move to the whole step.
- **FR-5 Prevalence (224).** `instructions/wording.py` `packed_fault` mirrors the head state verbs and the fourteen
  verdict words (the instruction's list, matched in every tense; *have to* at the head allowed, as keel-cloud read it);
  `harness/vectors_script.py` `PROBLEM_CLAUSES["06-repeatline"]` reworded off *by hand* (the harness's own fixture,
  not the corpus); `tests/test_cloud_212_mirror_136.py` green.
- **FR-6 Current solution (226, 228).** `evals/corpus_scenario.py` reads `lineAfter` beside `line`; the walk leaves
  the line where it is drawn; the golden fake writer's Countly and Linerly ladders take one W-rung repair turn, then
  serve unchanged -- any count of repair turns or notes allows it; `instructions/brief_facts.py` `current_solution_bar`
  stands.
- **FR-7 Existing sacrifice (222, 227).** `instructions/chain.py` `cost_said` / `cost_belief`: the count frame
  (*about {n} {measure} per {unit} a {period}*, no *of {base}*, never %), the typed unit kept beside a percent of a
  named base, the consumer unit unless it is the people's own noun; `evals/corpus_scenario.py` `chain_words_owed` and
  `chain.py` `equation_per_drawn` no longer ban *per {unit}* beside a percent; the stranger's item mirror takes the
  writer's `loss_clause` where the scripted result carries one, else code's reading (the neutral verbs stay as the
  fallback).
- **FR-8 Importance and Compatibility (223, 225).** The mirrors of the own row (code's noun phrase from the clause
  where the study holds one), the Compatibility row `kind` and the permission frame (*Yes, easily · Yes, with some
  steps · Only with help or approval · No*), the settled note and the rivals' notes as served fields the walk reads and
  leaves alone; tasks.md names each pin from the three specs' tasks.md "owed" sections.
- **FR-9 Gate.** `make unit` green with no failures (the nine back to green, nothing else red); the mirror tests of
  each spec named in tasks.md; the contract export and the instruction mirrors regenerated the way the repo does it.
  No paid runs, no model calls, no corpus change, RUBRIC_VERSION stands.

## Out of scope

The reader's rubric; the card tiers (meaning|shape); the Buyer and payer joined row.
