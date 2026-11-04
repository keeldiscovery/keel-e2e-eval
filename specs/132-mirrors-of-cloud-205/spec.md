# Spec 132 -- The harness mirrors keel-cloud 205

keel-cloud 205 (master 5b8f0fc9): the founder's lists fit the dimension cards. Its tasks.md lists what this harness
owes. Builds on 129, 130, 131.

## Rules

- **FR-1 L32 by name.** `evals/backtest.LOCK_NOTES` and `instructions/score.py` name L32 (a Purchase friction step
  that is the founder's own trial, pilot, guarantee, onboarding or money-back offer is refused once, then noted).
- **FR-2 The fake writer and the walker's rows.** `vectors_script.py`'s Purchase friction rows that carry the founder's
  trial or pilot are expected refused once, then noted, as the cloud now does; the scripted founder-lists writer does
  the same.
- **FR-3 The walker's Buyer and payer pick.** On a Buyer and payer Choose the walker picks the role the corpus Answer
  names, never *Nobody else* (Palus: the board), unless the Answer names nobody.
- **FR-4 The cards' Open points 205 settled** are moved out of *Open* in `quality/readers/dimensions.md` into the
  card's lines, word for word as the registry now says: ability to pay's escape; adoption friction's condition;
  purchase friction's b2b_only; commitment's soft yes and its drift template without *now*; prevalence's and
  frequency's wording notes. No other card line moves; the card tests (131 FR-1b) re-pin to the registry.
- **FR-5 Pins.** Commitment's drift template and the two moved Answer questions (Purchase friction: *What must the
  buyer's own side clear before they pay?*; Commitment: *What's the first real step you'd want them to take, and where
  would any money go?*) wherever this harness pins them. `make unit` green.

## Amended for keel-cloud 206 (master b177a4bd)

- **FR-6 More rules by name.** `E9` (a gate clause of *could/would/should have* refused once, then noted), `K10` (a
  compatibility clause with a bare verb after the auxiliary, or *had* before a possessive) and the draft-side `K8`
  (an adoption friction item without its condition) are reported by name where L-rules are.
- **FR-7 The fake writer's adoption friction rows** carry an `only_if` condition tied to the step's risk, so the
  scripted founder does not spend a repair turn per item.
- **FR-8 The walker types the Purchase friction time** from the corpus entry (the step's own time), never leaves the
  box empty; where the corpus has none, it picks *I'm not sure*.
- **FR-9 Pins.** The new Existing sacrifice stems (*what percent of …*, *go without*, *fell through*; never *miss*)
  and Commitment's first label *Yes, I would* wherever pinned; the `vs_screens` mirror of the window label's third
  clause (*the last time {circumstance}*, keel-web 166) and of Purchase friction's held Choose (`keeltest-waiting`, no
  `.keeltest__b` before a time).

## Amended for keel-web 168 (master after bdb63e72)

- **FR-10 The walker on the moved founder screens.** Buyer and payer's Choose has two options at most: *Nobody else*
  and one option holding every role joined with *and*; the walker picks by index (1 for the roles, 0 for nobody),
  never by a role's label; a list holding only *Nobody else* has no radiogroup and is confirmed as a statement. The
  `chain-share-RECOVERED` price shape is absent on a fresh study. The `vs_screens` constants
  `IMPORTANCE_ANSWER_HINT`, `COMPATIBILITY_ANSWER_HINT`, `CURRENT_SOLUTION_HOW_HINT`,
  `PURCHASE_FRICTION_CHOOSE_BAR_UNDATED` and `CHAIN_BASE_HELP` take the new words (keel-web
  specs/168-founder-screens-owed-by-cloud-205/tasks.md lists them); the Purchase friction bar with no time reads
  *Holds if no more than 1 in 3 say it would take a long time.*
