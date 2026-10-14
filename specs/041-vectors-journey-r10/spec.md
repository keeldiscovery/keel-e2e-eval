# Spec 041 -- the vectors journey on corpus r10 and the redesigned screens

Spec 11 of keel-cloud `canon/designs/redesign-plan-2026-10-14.md`, **its journey half** (spec 040 was the marks half;
its *Follow-ups* section "The later journey spec" is this spec's task list). Sibling of keel-cloud-docs master `7b151f9`
(087 / 088 / 089: vectors only, registry 4, all thirteen decide, corpus revision 10, contract 13, routing v11 with
`asked: light`, charge 7, document 20) and keel-web master `844ea36` (062 classic gone, 063 the founder's one dimension a
screen, 064 the stranger's screens on contract 13, and 065 -- merged while this spec was in flight, on top of `c499bf7`
-- the brief in two pages and the overview's pilot tile). No
MARKS_VERSION or POLICY_VERSION moves, spec 040's marks are untouched, **no model is called and no money is spent**;
the proof is the local stack.

## What the journeys do now

- FR-001 **One function per leg** (`evals/corpus_scenario.py`), 039's shape: `leg_project`, `leg_context` (the entry's
  window, at least two units -- 01 `{4, WEEKS}`, 05 `{3, MONTHS}`, 07 `{2, WEEKS}`), `leg_interpret_problem`,
  `leg_calibrate(PROBLEM)`, `leg_interpret_solution` (the seed, the mechanism card, and **the idea as the solution's
  first question**: S2's three lines read and saved untouched -- Save is the approval), `leg_calibrate(SOLUTION)`,
  `leg_persona`, `leg_calibrate(COMMERCIAL)`, `leg_lock` (step 5's two screens, *Lock and write the questions*),
  `leg_invite`, `leg_interview`, `leg_standings`, `leg_brief`. S-012's leg two calls the same functions, `strict=False`.
- FR-002 **`leg_calibrate`, one dimension a screen** (keel-web 063): Prevalence, Frequency, the cost and the price on
  one screen each; every list dimension's *Answer* (the founder's words typed, Continue -> `POST
  calibration/{vector}/draft`), *Check and save* (waited out while Keel drafts; the drafted list read and saved untouched)
  and, where the list picks, *Choose* (none pre-picked; the entry's own item picked). Asserted: every screen's *Stage · k
  of n* (Problem 4, Solution 4, Commercial 6 on B2B / 5 on B2C), its n dots with the k-th hollow (a question's Answer /
  Check / Choose share it) and the side nav locked with no link; the stage's last primary names the next stage
  (*Save and continue to the solution*, *Continue to paying*, *Save and continue to Before people see it*); every drafted
  list is the entry's own (Importance's own item locked *yours* first, Current solution's phrase and five outcomes,
  Commitment's step, Buyer and payer's roles with *Nobody else* left to Choose); the *Keel will test* box reads the
  entry's `belief_sentence` (Check on the four Keel-set dimensions, Choose on the four picked, the pending line before the
  pick); on the wire every list is stored as saved -- code's positional codes, the stranger's `asked` faces, the
  `pickedIndex`, the phrase -- and the review is complete with every belief the entry's (LEFT_OUT where unsure). **The
  DRIFT #74 wire step is gone** (nothing is left to send).
- FR-003 **The script answers contract 13** (`harness/vectors_script.py`): `CALIBRATION_QUESTIONS` -- Prevalence's
  `event` and five fifths, a `list {items[{label, asked?}], phrase?}` per list dimension (the entry's own list), key and
  note only on Frequency, the cost and the price -- **one entry a vector and one more per list dimension the founder
  answers**, in the corridor's order (`calibration_jobs`), because the redraft runs the same screen on the same key set;
  `RESPONDENT_QUESTIONS` `{key}` per planned key and the gate's `{key, event}` (E1-E4); `ASKED` the corpus's own faces per
  Compatibility / Adoption friction list; `BRIEF` the headline and three answers, each citing its stage's deciding
  dimension (`broke` where it broke), no tests, no quotes. The ladder / rank / chip readers, `RESPONDENT_ESCAPES`,
  `FIXED_LABELS` beyond Prevalence, `purchase_friction_labels`, `commitment_labels`, `importance_labels` and `slug` are
  deleted.
- FR-004 **Typed inputs in contract 13's shapes**: a list dimension's Answer words, its saved list as keel-web posts it
  (labels, untouched faces, `pickedIndex`, phrase; no codes) and its picked item; each person's picks on the wire's own
  codes (`wire_code`: `own` / `rival_n`, `outcome_n`, `benefit_n`; the registry's fixed answers unchanged), two codes on
  Importance, the escape as `chip`, "nothing" as `costTotal {AMOUNT, 0}`, the gate's story chip CANT_RECALL.
- FR-005 **`leg_interview`** (keel-web 064): each person in their own browser context; held **to the wire on every
  journey** -- the decision-maker's link opens with the idea's three lines under the served kicker (D9); the gate's
  story chip is *I can't recall one particular {occasion}* alone; every item draws its served kicker, stem (Price's anchor
  aside), options as rows, *Pick two.* on Importance and ONE escape, its served label, after the control and before the
  buttons (none on Commitment) -- and **to the corpus** on the scripted ones: the body the page POSTs equals the person's
  own answers. The founder reads after each person.
- FR-006 **`leg_standings`**: every `expected.standings` row -- status, drift, `n`, the interval counts, every
  `optionCounts` code mapped onto the wire's -- and every `expected.vector_verdicts` verdict, the worst of its dimensions
  (D3); the board's pills, bands, belief tile and download; each stage page's rows and headline, the B2B decider banner,
  and **one row's per-person list** (the deciding dimension opened: every person's name and `readAs` the wire's).
- FR-007 **`leg_brief`, on the wire** (`GET standings`): the scripted headline and three answers (`fallbackUsed`
  false); a card per calibrated dimension equal to `instructions/brief_facts.py`'s reading of the entry (key, name,
  number, line, status, the verdict half of `statusWords`; spec 040's DRY proved that reading equal to keel-cloud's
  `BriefFactsCorpusTest`, 94/94); `broke` per stage; the pilot `{optedIn, finished, percent, perLink}` on the brief and
  on `StandingsView` (the overview's tile's read). Then **keel-web 065's pages, held to that wire on every journey**:
  page one (`/p/{id}/brief`) -- the decision, the headline, each stage's served answer (`.bans`), each stage's served
  cards word for word in order (name, number, line, status words), each card linking to its block, four tiles the
  fourth the pilot (*k of n · p%* over the per-link line, equal to both `facts.pilot` and `StandingsView.pilot`), the
  next tests with their chips, the footer, and none of *deal-breaker*, *Where they differ*, *Inferred from*; page two
  (`/p/{id}/brief/breakdown`) -- one block per card in its order with the card's own name, status words, number and
  line, *What broke* on `broke.key`'s block alone, the way back; the download's tab (`/p/{id}/print`) -- page one again.
  The board's third tile (`.tile--pilot`) is held to `StandingsView.pilot` in `leg_standings`.
- FR-008 **Extras** -- S-005: one respondent type, every part on one link; Existing sacrifice one under the floor of 5
  and *Too few to call* on the wire and the commercial page; the window is four weeks, Frequency is on the founder's
  screen (*4 weeks*), asked of everyone, and holds up (n 8). S-006: twelve translators FULL on parts 1-2 with a gate,
  eight decision-makers COMMERCIAL_LINK on part 3 with none; each decision-maker's first screen the idea under its served
  kicker, Ability to pay and Purchase friction asked of them; every translator's item kicker counts *of 2*; the commercial
  vector counted over the eight; the banner names the typed role; floor 5 everywhere and every asked dimension above it;
  twenty asked and twenty answered. S-007: US / TX / en-US; every amount in dollars and no £, €, GBP or EUR on any page
  read; *No price yet* leaves Price and Ability to pay out (amber) and the commercial vector is still called, on
  Purchase friction's split.
- FR-009 **Product defects** go to `runs/DRIFT.md` with a number (#78-#81), and the journey steps round each in a step
  named for the entry.

## Results

- `make unit`: **1,846 passed / 53 skipped** (before: 1,818 / 77). The 24 call-89 skips are gone (23 in
  `tests/test_vectors_journey.py`, rewritten for r10 -- 36 tests now -- and 1 in `tests/test_journey_through_a_host.py`);
  the 53 left are 039's r2-shape skips.
- `COMPOSE_PROJECT_NAME=keel-e2e-eval make up` then `make eval K="s005 or s006 or s007"`: **3 passed**, twice, against
  keel-cloud-docs `7b151f9` + keel-web `844ea36` (local stack; the same env var on `make eval`, whose Postgres gate asks
  Compose by project name); before 065 landed, once against `c499bf7` with the printed brief read on 064's page. No
  model, no money.

## Disagreements between corpus r10 and the wire (reported, the corpus not edited)

- D-1 **Frequency on Paidly's and Mulch Run's windows.** r10 keeps Frequency on the founder's own "out of N" (spec 040
  call 78): Paidly *4 to 7 invoices out of 7* over `{3, MONTHS}`, Mulch Run *4 to 6 working days out of 7* over
  `{2, WEEKS}`; keel-cloud counts it on 0..the window's count, so neither the founder's range nor the picks fit, the
  founder leaves it out and the journeys assert LEFT_OUT (and the brief's Frequency card *you weren't sure, so it was
  left out*) where the corpus and keel-cloud's own corpus test read HOLDING_UP. **Countly's `{4, WEEKS}` carries its
  *1 to 3 weeks out of 4*: asked, HOLDING_UP, as the corpus says** (039's D-1 and D-2 for Countly are gone with D13).
- D-2 **List codes.** r10's founder lists keep revision 9's slugs (`matching_deliveries`, `works_well`,
  `shorter_time`); keel-cloud codes every list item by its place (087 call 2: `own`, `rival_1`.., `outcome_1`..,
  `benefit_1`..). A pick is sent, and an `optionCounts` row compared, on the wire's code by the item's place in the
  entry's list (`vectors_script.wire_code`, `on_the_wire`).
- D-3 **Cost totals' period** (039's D-3, kept): r10 records every Existing sacrifice pick `period: quarter`; keel-cloud
  asks over the founder's period (a month on all three) and the journey re-expresses each amount by keel-cloud's
  `Period` days. "Nothing" (`{nothing: true}`) is typed as the number 0, an amount (D8); Paidly's two decision-makers who
  lost nothing read the same (the card's *£58.33* holds).
- D-4 **The story chip.** r10's `05-paidly` Xavier Dubois records `chip: rather_not_say`; contract 13's gate story has
  one chip, CANT_RECALL (keel-cloud 088). He taps *I can't recall one particular invoice*; GUESSED either way, no
  reading, no counted standing moves.
- D-5 **The persona's role.** r10's B2B persona is `decision_maker: {role: agency}` (`owner` on Mulch Run), an id whose
  `roles` label is *Agency project managers* (*Crew owners*), and its Buyer-and-payer belief reads *The agency decides,
  and nobody else has to agree.* -- keel-cloud 087's reading of the role word. Typed as the label, keel-cloud's
  `BeliefSentence.the` keeps a capitalised word as a name: *Agency project managers decides, ...*. The founder types the
  role word (call 93), and the banner and the commercial link's role card carry it.
- D-6 **Words r10 does not record**, composed by the referee (`vectors_script.COMPOSED`): the idea's three lines (from
  the mechanism, as 039); Prevalence's clause and its five fifths' labels; each list dimension's Answer words (call 91);
  the gate's clause -- *have a time when {circumstance}*, or the referee's shorter clause where that frames past E4's 20
  words (Paidly *wait to be paid for an invoice an agency had approved*, Mulch Run *fetch mulch from the supply yard for
  a job*; call 95); the BRIEF reading.
- D-7 **The hourly rate** (039's D-8, kept): Paidly 20 GBP, Mulch Run 25 USD against keel-cloud's market default; set on
  the wire after the commercial stage, then the page reloaded (call 101).
- D-8 **Paidly's two mechanism terms** padded to keel-cloud's three from the short name (039, kept).

## Judgement calls

Numbered on from 90 (the last one spec 040 used); each is the simplest reading that keeps `make unit` and the three
journeys green where the inputs are silent.

91. **The Answer words are the list's own labels**, joined with *;*, as many whole ones as fit 25 words (Current
    solution's phrase first; Buyer and payer with nobody else to agree, *Nobody*). r10 records the list the Answer was
    drafted from, not the Answer; the scripted draft is the entry's list whatever the words, and the words carry every
    digit the list does (L3).
92. **Every list dimension is answered in words**, so each is redrafted exactly once, and the script's
    CALIBRATION_QUESTIONS entries are `calibration_jobs`: the slice on each seed, then one redraft per list dimension in
    the slice's order (a dimension left out is not drafted). keel-web's *empty box over a saved list* path is never taken.
93. **The B2B persona's role is the corpus's `decision_maker.role` word** (*agency*, *owner*), not the role's label (D-5);
    S-006's banner extra follows the typed role.
94. **Every list is saved untouched**, so code vouches for every face and no ASKED job runs; the script still carries
    one ASKED entry per Compatibility / Adoption friction list (every index, the corpus's face), and the unit tests hold
    those to K1-K6's shape.
95. **The gate's clause** is *have a time when {circumstance}* where that frames within E4's 20 words (Countly, 03, 06),
    else the referee's clause in `GATE_EVENTS` (02, 04, 05, 07); both held to E1-E4 and R4 in the unit tests.
96. **Choose picks the entry's `pickedIndex`**; on a live journey the model's item at that index, clamped to its list.
97. **The brief's cards are held to `instructions/brief_facts.py`'s reading** of the entry -- the repository's own,
    proved equal to keel-cloud's `BriefFactsCorpusTest` by spec 040's DRY -- with D-1's Frequency read as left out; the
    pilot to its `pilot_for`. (The scratchpad copies of keel-cloud's JSON are a reference, not a fixture.)
98. **The referee's brief** is one sentence a part: the headline (*Scripted by the referee ... not written by a model.*,
    citing the problem's deciding dimension) and *On {stage}, {Name} is what broke, so it is what to change ...* /
    *... decides the reading ...*, citing the deciding dimension (B7: what broke cited where it broke); no tests, no
    quotes, no digit, no name.
99. **The *Keel will test* box is held where it says something**: on Check for the four dimensions whose bar Keel sets,
    on Choose (after the pick) for the four that pick; Choose's box before the pick reads *Pick one and the test appears
    here.* Buyer and payer's is held but for its first letter (DRIFT #79).
100. **The review is not walked** (keel-web 063 call 7 took it out of the walk); it is asserted on the wire -- complete,
     every row's belief the corpus's `belief_sentence` (every dimension now: each r10 belief is code's template over the
     saved list, so there is no multi-tick sentence to excuse, 039's D-7 is gone).
101. **The hourly rate goes on the wire after the commercial stage and the page is reloaded**: the write moves the
     revision under step 5, whose lock would otherwise post the revision it read (409).
102. **One row a stage page has its per-person list read**: the vector's deciding dimension (else the first row with
     people), each person's name and `readAs` held to the wire's row.
103. **"Nothing" is typed as 0 in the amount mode** (the page's first mode; keel-web 064 call 9).
104. **The pilot box is ticked for every person the entry records `pilot_opt_in`** (on all three entries, gate-yes
     people), on the done screen.
105. **The respondent screens are held to the wire on every journey, live ones too** -- they are code's words, never a
     model's -- and only the body is held to the corpus.
106. **A transient product state is stepped round once, never more**: S2's empty lines reloaded once (#78), a 409 on a
     corridor write pressed again once after the page's poll (#80), a FAILED questions state read again once (#81); a
     second failure fails the journey.
107. **065's pages are held to the wire, not to the corpus**: the corpus is already held on the wire one step before
     (cards, broke, pilot), so the pages read the served facts and reading word for word -- on S-012 too. Words are read
     as the DOM carries them (`text_content`), never as the CSS capitalises them.
108. **Page one's tiles**: four, the fourth the pilot; the three verdict tiles are counted, not re-worded (the board and
     the stage pages already hold the verdict words).
109. **Page two's blocks are compared on what a card says** (name, status words, *number line*, *What broke* present or
     not); the row body inside each block is the stage page's own component, which `leg_standings` already reads.

## Follow-ups

- **keel-web**: #78 (S2's stale idea), #79 (Buyer and payer's preview capital), #80's silent 409.
- **keel-cloud**: #80 and #81 (two reads, not one snapshot); #79's served template head.
- **The next corpus revision** (spec 040's, plus): Paidly's and Mulch Run's Frequency on their own windows (D-1); the
  persona's role word beside its label (D-5); Xavier Dubois's story chip (D-4).
- **The remote run against the staging twin** (not run here): `PROFILE=remote` with `KEEL_REMOTE_WEB_URL` (and
  `KEEL_REMOTE_GATE_USER` / `KEEL_REMOTE_GATE_PASSWORD` for the stub issuer's gate, from the session's own secret store),
  against a twin deployed at keel-cloud-docs `7b151f9` (or later) and keel-web `844ea36` (or later) with
  `KEEL_VECTORS_ENABLED=true`; `make up PROFILE=remote` (three checks), `make eval K="s005 or s006 or s007"
  PROFILE=remote`, `make down PROFILE=remote`. The runtime runs here on the scripted executor against the twin's cloud;
  no model, no money.
