# Spec 119 -- The harness walks cycle 5's studies to the end, and the reader hears what the voice says

Cycle 5 (2026-11-01, `quality/cycles/20261101-e65afec.md`) stopped nine of fifteen walks early. Six stops were the
harness's own mirrors lagging keel-cloud 180-186 and keel-web 155-157 (three of them, the lock step's title, fixed
mid-cycle at `a1b92a3`); two were keel-cloud's (spec 187 FR-1); one was test data (187 FR-4a). And the respondent-reader
scored Price's spoken form from the written list because the bundle recorded no spoken form for it (118 FR-4c(a) did not
reach the text link). These are harness defects: the referee owns no product code, and a mirror that lags is the
referee's fault. Builds on 118. keel-cloud 187 (contract 56, corpus revision 22) and keel-web 158 first.

## Rules

- **FR-1 The idea's line.** The respondent's idea card and the reveal carry keel-cloud 185's served line *Imagine
  {name}, {what}.* (`served.idea.what` on the interview is that line); the check holds that the line names the idea
  (`name` in it) and that the drawn card opens with the served line -- never *Imagine {name}.* alone (10-palus and
  13-aircaps COMMERCIAL stopped on Sofia Marchetti and Harriet Coleman for this).
- **FR-2 Ability to pay's written question.** keel-cloud 181 serves the item's `question` as the one spoken sentence
  (*Think of the price you just gave. …*) and the written per-person question on `askedAfter.answers[].question` (*You
  said about {band}. …*); the page draws the written one. *Every screen draws what the wire served* compares the drawn
  question with the written one for the person's Price answer (17-expanse COMMERCIAL stopped on Gregory Lindqvist).
- **FR-3 The Choose pick on Purchase friction.** The founder's time is typed for every B2B entry from corpus revision 22
  (`duration`), the Continue waits for it, and the pick is read back as before (21-codyco COMMERCIAL stuck on Choose);
  the reader's screen description of Choose carries the time box, its hint and the 157 bar, so the founder-reader scores
  what is there (its R2 = 0 said *no number box*).
- **FR-4 The reader hears the voice on every item, on either link.** The walk records the served `spoken` of every
  respondent item from the interview wire into the bundle (anchor, stem, count line, options line, escape line, and the
  `under` / `over` second-step lines of Price and the duration bands) whichever link the person walks, and the reader's
  `{{screen}}` carries it as 118 FR-4c(a) intended; the sentence *the bundle records no spoken form for it* is never
  written for an item that serves one. A test on a recorded bundle.
- **FR-5 The spoken guard.** Ability to pay's escape of record is the registry export's (`cant_say`, *I can't say*,
  keel-cloud 181), read from the bundle's `contract-export/dimension-registry.json`, never a pinned table (S6 flagged every
  B2B money study); Price's first step on a percent ladder (*Under a quarter of a percent; a quarter to under half a
  percent; half a percent or more; or you wouldn't pay for this.*) is clean under S8 when it is §3's four options in
  order ending *; or z.*; the duration bands' two steps are read as Price's (keel-cloud 187 FR-3): S3 counts the first
  step's four, S7 the count line it serves.
- **FR-6 Corpus revision 22.** `corpus_reader` reads 22 (every B2B entry's `duration`, every entry's
  `current_solution.today`); r21 retires as r20 did; `answer_text` types `current_solution.today` into the Answer's first
  box and the rungs into the second (184 FR-8b(a)); the AI walk answers the duration bands in two steps (keel-web 158);
  contract 56.
- **FR-8 The idea step's waiting state is not a screen.** On 10-palus SOLUTION the walk captured the idea step twice
  while the mechanism job was still running (the kicker and the what-box hint, no text; recorded as
  `failed-solution-calibration`) and the founder-reader scored both (R1 = 0, R2 = 0: *repeats the kicker and hint of
  screen 10 with no text*). The walk waits for the served `what` / `how` / `belief` before it captures the idea step,
  captures it once, and names a calibration that truly failed by its served reason; a waiting state is never a scored
  screen. A test on the recorded bundle.
- **FR-7 Tests.** Each mirror pinned with why; the four stops replayed on fixtures; FR-8 on the Palus bundle; `make unit`
  ZERO failed.

## Acceptance

`make unit` green against keel-cloud 187 and keel-web 158 merged. The next cycle's fifteen walks reach their end or stop
on a fault that is the product's, named. The matrix's s012 red on the Insights view (a Commitment box's served group
not drawn) is owed to this spec's successor if it is the harness's; the coordinator settles which from the cycle's
bundles.
