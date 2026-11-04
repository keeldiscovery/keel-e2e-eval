# Spec 133 -- The harness mirrors keel-cloud 211 and keel-web 171

keel-cloud 211 (cycle 10's code-side defects) and keel-web 171 (the context intro counts the screen it heads; done on
master 6b7a8bd). Their tasks.md list what this harness owes. Builds on 131, 132.

## Rules

- **FR-1 Rules by name.** `L33` (a Buyer and payer row for a role the founder never typed) and `L34` (a priced
  Commitment step without a free smaller step) in `LOCK_NOTES` and `score.py` where L-rules are named; `X8` now
  refuses a single dropped founder word (once, then noted).
- **FR-2 The fake writer's rows.** Priced Commitment rows (pay, paid pilot, order) in `vectors_script.py` and the
  scripted writer carry a free smaller step with its reason; Buyer and payer rows are roles the corpus Answer typed;
  the context result keeps every founder word of WHAT and WHEN.
- **FR-3 Pins.** The Commitment Answer question *What's the first real step you'd want them to take, and what would
  it cost them?*; Purchase friction's untimed belief (*… within the time you'll set, or not need it.*) on Check
  before a time; Prevalence's founder question with the whole segment, core and condition (Lullaby: *… under six
  months in the US*); the *who answers* label as the whole typed title, with *, with {co-decider} agreeing* once
  Buyer and payer is saved (never the bare last word); Relative advantage's *Keel will test* line with every kept
  benefit joined by *and*; the typist fixture's intro *Four short answers, a phrase each.* (171; done on master).
- **FR-4 The Commitment card's good example** (Fresco's paid pilot with no smaller step) contradicts the card's own
  rule and 211 FR-6: the example gains the free smaller step; the card's rule lines do not move; keel-cloud's vendored
  copy and `CARDS_SHA256` move in the same commit **only if** the cloud's copy is updated (not here: note it as owed).
- **FR-5** `make unit` green; nothing paid.
