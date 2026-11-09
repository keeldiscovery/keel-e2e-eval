# The dimension cards (spec 131 FR-1, FR-1a, FR-1b, FR-1c)

**The corpus writer's law** (spec 135 FR-3, keel-cloud 215): the back-test entries these cards are read against are
written under keel-cloud's `canon/designs/measured-beliefs/backtest/CONSTITUTION.md` (the founder's document of
2026-11-04) -- the seed, what the founder types at each stage held to these cards, the people, the sources file, the
gate before an entry enters the gallery (section 9) and what moves when a card changes (section 10). A card here says
what a screen's options must do; the constitution says how a corpus row is written so they can.

The founder, 2026-11-03: *"our agent should be dimension aware ... is this question valid -- do the options meet the
criteria for that dimension, including the option?"*; and at 08:50 ET: *"spend a good amount of time for how each
dimension would look like, and how the options should look like, how much of them should be for and how much should be
against, and ensure that that's foolproof."*

**What a card is.** One card per dimension of keel-cloud's registry, thirteen, in the registry's order (four of the
problem, three of the solution, six of the money). Each card says, in plain words and for the founder's screens and the
stranger's item of that dimension alike, in this order: what the dimension measures; the shape its options must have;
which answers count for the belief the screen tests, which against, and which count for nobody; the escape; a good and a
bad example; the pitfalls the readers have already seen. Where the registry and a spec disagree, or the sources leave a
point unsettled, the card says so under **Open**; a reader never scores an Open point as a fault of the screen.

**How the readers use it.** `quality/readers.py` sends the screen's card -- the text between its two `card:` markers,
nothing above the first marker -- to the founder-reader and to the respondent-reader after the persona and before the
screen, on every screen whose dimension is set (answer, check, choose, q, the stranger's item and the gate, the card
after the answers); a screen with no dimension (context, idea, send) gets none (FR-2). The reader scores R7, *fits the
dimension*, from the card, asking its questions in order (FR-1c): **the measure** -- is every option on the one measure
the card names?; **the shape** -- the count, the order, the first and the last, the founder's own row; **the balance** --
could the belief ever be supported by these options? could it ever be refuted?; **the escape** -- there where the card
requires one, absent where the card forbids one. 2 all met; 1 one rule bent; 0 a rule broken: a scale where every option
counts one way, a scale with no working rung, an item whose options cannot answer the belief, a missing escape the card
requires (FR-3). On the card after the answers, the same For / Against / Neither is the yardstick for the card's rule
line, its strip and its count line. The card never replaces the persona: whether the words are plain is still judged
from inside the person (R2). The card says what the options must do, never which trade's words they use, and no rule on
it depends on who the people are (the founder's rule of 2026-10-28: persona-aware, never a special case).

**Held to the registry by test.** The source of truth is keel-cloud's registry,
`canon/designs/vectors/dimension-registry.yaml` (master `09d0784f`, specs 203 and 204 in), and the compare rules' code
(`domain/vectors/Compare.java`, with `CommercialChain`, `PurchaseFriction`, `WorkingRung`, `SavedList`, `ItemFrames`).
Every card opens on a **Registry** line and carries the registry's codes in backticks on its **Fixed answers**, **For**,
**Against**, **Neither** and **Escape** lines. A test reads those lines against the registry row -- `meaning` word for
word, the founder `control`, the counts and order of `option_rule` and `fixed_answers`, `answers.compare_rule`,
`supports`, `escape` and `left_out` -- and a card that drifts from its row fails `make unit` (FR-1b). When the registry
moves, the card moves in the same commit.

**The words every card uses.**

- *The belief*: the sentence the founder checked on the way in. The strangers' answers are counted for or against it.
- *For* and *against*: for or against **the founder's belief** -- never "for the product", never "for today's way". A
  conditional yes is a yes: it counts for, drawn lighter and split in the count line (spec 180: there is no neutral).
- *Neither*: counted for nobody -- the item's escape (always apart, but for Importance's *None of these*, which counts
  against); a guess (an answer with no story behind it); a person never asked (a No at the gate answers nothing more; on
  Ability to pay, everyone below the founder's price); and the whole dimension when the founder chose *I'm not sure*:
  left out, asked of nobody, and the brief says it is untested.
- *The floor*: 5 counted people (Prevalence: 5 gate answers). Fewer is *Too few to call*.
- *The bar*: at least 2 in 3 of the counted for is *Holding up*; 1 in 3 or fewer *Not holding up*; between, *People
  disagree* -- said *Did not hold* on the five lines whose bar the founder saw as a limit (*no more than 1 in 3 say
  ...*): Compatibility, Relative advantage, Adoption friction, Purchase friction, Commitment. Prevalence alone reads a
  share of Yes against the founder's band.
- *Healthy*: at least one option can count for the belief and at least one against it -- else the belief can never be
  supported, or never refuted, and the screen tests nothing.
- Where someone else decides to pay (a business study), the money items are asked on the decision-maker's own link,
  with no gate; the problem and solution items on the people's link, after a Yes at the gate.

---

<!-- card:problem.prevalence:begin -->
### Prevalence · `problem.prevalence`

**Registry:** PROBLEM, order 1 · founder `single_choice` (no *I'm not sure*) · stranger `gate_yes_no` (part 1, the gate)
· compare `proportion_from_gate`, supporting side `more` · escape none · floor 5 gate answers.
**Screens:** the founder's question (q) · the stranger's gate · the card after the answers.

#### 1. What it measures

How many of the people you are studying had the problem in the period you chose.

#### 2. The options' shape

- **The founder's question** is code's frame around the founder's problem: *In {window}, how many out of 10
  {actor_plural} {event}?* -- the people as the founder named the segment, every qualifier kept; the event the costly
  thing that goes wrong (the wrong outcome, the lost time, the money given up), never only the circumstance every member
  of the segment is in; one act in the tense of the window, no two conditions, no cause or result packed in, nothing the
  person does not see; a standing state asked as the moment inside the window where it shows, so *at least once* fits.
- **Exactly five options, code's, in this order, on one measure (a share out of 10), no gaps and no shared edges:**
  *Fewer than 2 in 10* (`p_0_20`) · *2 or 3 in 10* (`p_20_40`) · *4 or 5 in 10* (`p_40_60`) · *6 or 7 in 10*
  (`p_60_80`) · *8 or more in 10* (`p_80_100`). The first is the lowest share, the last the highest.
- Each option's belief phrase is the same share, never stretched: *Under 2 in 10 · 2 to 3 in 10 · 4 to 5 in 10 · 6 to 7
  in 10 · At least 8 in 10* -- never *nearly all*, *most*, *a few*. Keel adds no option and no *I'm not sure*.
- **The stranger's gate**: *In {window}, did you {the founder's problem, said to them}?* -- the problem the founder
  counted, never the circumstance; never names the idea. **Fixed answers, in order:** `yes` *Yes* · `no` *No*. The stem
  must name the window and the problem as one act the person did or met, so a person without the problem can truly say
  No and a person with it Yes. A Yes opens the story; a No ends the interview, and the person is still counted.
- **One clause (keel-cloud 212).** The strangers' event is the founder's clause, by code: the gate and the Frequency
  item carry the founder's Prevalence event, turned to the second person by code, never a second writer's. The founder's
  writer writes it from `went_wrong` (the one part of the problem a person with it had to do or put up with), beside
  `routine` (what every one of the people does whether or not the problem struck): the act that hurts, at most 9 words,
  8 on a working-days window: 20 spoken words minus the strangers' frame -- never the routine, a lasting state, a
  judgement, or a cause or result packed in. A thing left standing is asked as what it did or cost them inside one
  {unit}, never where it sat (keel-cloud 231). Code holds the clause, one repair turn each: then the routine (`E7`) and
  a clause over the cap (`E2`) are refused; a lasting state, a judgement, a cause or a verdict (`E8`) is served as
  written with a note -- never a refusal at confirm.
- **The No-sayer (keel-cloud 216).** The writer shows the test in `no_sayer` -- one of the people who did the day's
  work in the window and truly answers No to the event, and what was different for them -- and code refuses one set
  apart by the routine or outside the segment (`E9`): if every one of them would say Yes, it is the routine; write the
  part that hurt instead -- the thing that failed, was lost, came back wrong, sat idle or had to be done twice.
- **The act that hurts, read against the segment (keel-cloud 238).** `E7` also refuses an event every word of which is
  the segment line's (`circumstance`) or the routine's -- what every one of them does whether or not the problem struck;
  one that carries none of `went_wrong`'s own words (the kind of thing that went wrong, dropped); and one with a word
  the founder never gave (in none of `went_wrong`, the routine, the circumstance or the founder's problem: a setting or
  a kind added). `E9` also refuses a no-sayer who names none of `went_wrong`'s own words: their No is a word of the hurt,
  denied or not. `E8` also reads *less than it could* and *more than it should* as verdicts, and *let*, *allowed* or
  *failed to* at the head as blame: what happened to them is said with its subject first (*had the call ring out*),
  never as their choice (*let the call ring out*). Each refusal names the words and says the test above.

- **Settled by keel-cloud 205 (the registry's note):** 2026-11-03, spec 205 (FR-4; the dimension card's Open point): the
  founder's question screen carries belief_template as it stands ('... had this at least once in {window}'); the card
  after the answers names the gate's own clause, never 'had this' (spec 184 FR-1; code, on the card only). Both stand;
  nothing here moves.

#### 3. For, against, neither

- **For:** `yes` -- they had the problem in the window.
- **Against:** `no` -- they did not. A No is counted: it is in the share.
- **Neither:** nobody at the gate. There is no escape. Every gate answer counts, a Yes with no story behind it
  included (the gate is explicit). People on the decision-maker's link are not asked the gate and are not counted here.
- **The bar:** the share of Yes against the founder's band -- at the band's low edge or above holds (above the band:
  *more than you think*); below the low edge does not hold; there is no *People disagree* on this line. In people: the
  low edge of the band times the people counted (*at least 8 in 10* of 7 is 6; *6 or 7 in 10* of 7 is 5). Floor 5.
- **Balance:** two answers, one each way; the founder's band sets the bar. The lowest band, *Fewer than 2 in 10*, has a
  low edge of 0, so any share holds it: that belief can only be supported, never refuted. Every other band can be
  refuted.
- **Healthy:** Yes and No both possible and both true of someone -- the stem asks the founder's problem, not a thing
  everyone in the segment does. A gate on the circumstance (every member says Yes) leaves No to nobody: the belief is
  tested against nothing, R7 0.

#### 4. The escape

**Escape:** none, on both screens. The founder's question offers no *I'm not sure* (the gate is the denominator; a study
with no gate has none), and nothing on that screen may promise one. The gate is two answers, no escape: an escape there
would take people out of the share. The chips a reader may meet beside the gate (*I can't recall one particular ...*,
*I'd rather not say*) belong to the story box after a Yes (keel-web hides them on a No; the founder's decision
D-2026-10-29-20) -- they are not the gate's escape and not a fault of this card. Left out: unreachable (*I'm not sure*
is never offered).

#### 5. A good example and a bad example

- **Good (R7 2)** -- Fresco, construction superintendents, the last 5 working days. Founder: *In the last 5 working
  days, how many out of 10 construction superintendents on commercial jobs typed up the daily log after their site
  walks?* -- the five code labels; the founder picks *8 or more in 10*; the belief *At least 8 in 10 of these
  construction superintendents on commercial jobs had this at least once in the last 5 working days.* Gate: *In the last
  5 working days, did you type up the daily log after your site walks?* *Yes · No.* A super whose log was done on the
  walk says No (against); one who typed it up in the trailer says Yes (for).
- **Bad (R7 0)** -- the same study, the gate asked of the circumstance: *In the last 5 working days, did you log
  site-walk photos and notes?* *Yes · No.* **What breaks it:** *log site-walk photos and notes* is what every working
  superintendent does, not the problem the founder counted -- everyone says Yes, No has no one, and *at least 8 in 10*
  can never be refuted (registry decision 26).

#### 6. Pitfalls the readers have seen

- Two facts packed into one count (a missed call *and* a lost guest; a chore and its result), or a cost or duration the
  founder never typed (cycle 8, proposal 44; cycle 7, 45).
- The gate drifting from the founder's problem: the condition that made it a problem dropped, a hint at another way
  (*by hand*, *stay*, *your bank's treasury product* copied from the instruction's example), so the struggling person's
  true answer is missing (cycle 7, 45 and 65; cycle 8, 49 and 68).
- The question screen's intro promising an *I'm not sure* the row does not offer (cycle 7, 41); the card after the
  answers re-banding or stretching the founder's band (*6 to 7 in 10* where they typed another; *nearly all*) (cycle 7,
  40; cycle 8, 43).

#### Open

- **Not settled.** A founder who picks *Fewer than 2 in 10* holds a belief no answer can refute (code: the share is
  always at or above 0). FR-1c asks *could it ever be refuted?*; whether R7 reads that founder's pick as a broken rule,
  when the screen's own options are sound, is not settled by the sources.
<!-- card:problem.prevalence:end -->

---

<!-- card:problem.frequency:begin -->
### Frequency · `problem.frequency`

**Registry:** PROBLEM, order 2 · founder `numeric_interval` (*I'm not sure* allowed) · stranger `segmented_1_to_n` (part
1) · compare `interval_contains_median`, supporting side `more` · escape `cant_recall` · floor 5.
**Screens:** the founder's question (q) · the stranger's item · the card after the answers.

#### 1. What it measures

How often someone who has the problem runs into it.

#### 2. The options' shape

- **The founder's question** is code's: *On how many of {window} did a typical {actor} {event}?* -- the window
  first, then one act that happened on a given unit or did not, in the simple past (no state, cause or result, nothing
  the person does not see), named as the people name it; the question last. **No options:** a two-handle range from 0
  to the window's count, in whole units of the window (*4 to 7 nights out of 7*; *2 to 3 months out of 3*). The belief:
  *{actor_plural} face this on {value}.*
- **The stranger's item** is code's: *On how many of {window} did you {event}?* -- the count of units it happened on,
  not the number of times; the unit said once, in the window phrase (keel-cloud 216: never *on how many did you*, never
  the unit said again, *in the last 3 months, in how many months*). **One measure: units of the window.**
  **The options:** one button per unit, *1* first, the window's count last (*1 · 2 · 3 · 4 · 5 · 6 · 7*) when the count
  is at most 7; a number box of at least 1 for a longer window. Never a 0 (a Yes at the gate means at least one), never
  the founder's range, never bands. Spoken past five steps: *Say a number from 1 to {N}.* Then the one escape.
- **One clause (keel-cloud 212).** The strangers' event is the founder's clause, by code: the founder's Frequency
  question and the stranger's item ask the founder's Prevalence event, the stranger's turned to the second person by
  code -- the same act, so a count of the strangers' units reads against the founder's range; the clause is at most 9
  words, 8 on a working-days window: 20 spoken words minus the strangers' frame.

- **Settled by keel-cloud 205 (the registry's note):** 2026-11-03, spec 205 (FR-4; the dimension card's Open point): the
  founder's question screen carries belief_template as it stands ('{actor_plural} face this on {value}.'); the card
  after the answers names the question's own clause, never 'face this' (spec 184 FR-2; code, on the card only). The
  event the question asks is Prevalence's clause (WindowFrame.frequencyFounder), so the event's rules live in
  Prevalence's guidance. Nothing here moves.

#### 3. For, against, neither

- **For:** a count at the founder's low or above -- inside the founder's range, or above it (*more often than you
  think*).
- **Against:** a count below the founder's low.
- **Neither:** `cant_recall` *I can't recall* (apart); a guess; anyone who said No at the gate (never asked); a story
  chip that ended the interview.
- **The bar:** at least 2 in 3 at the founder's low or above holds; 1 in 3 or fewer fails; between, people disagree. The
  middle answer is reported. Floor 5.
- **Balance:** the founder's low splits the buttons -- *1* up to one under the low count against, the low up to the
  window's count for. With *4 to 7 nights out of 7*: 1, 2, 3 against; 4, 5, 6, 7 for.
- **Healthy:** the founder's low is at least 2, so at least one button can count against. A range that starts at 0 or 1
  makes every button count for: the belief can never be refuted -- every option counts one way, R7 0 by FR-1c. The
  question says the unit once, in the window phrase: *On how many of the last 3 months did you ...?*, never *In the
  last 3 months, in how many months ...* -- a word shorter than that, so the event keeps its 9 words (8 on working
  days) under the 20-word cap.

#### 4. The escape

**Escape:** `cant_recall` *I can't recall*, apart -- must be on the item, and only it. Never a *0* or *None* button in
its place: a person past a Yes at the gate has at least one. The founder's side: *I'm not sure* is allowed and leaves
the dimension out (asked of nobody; the brief says untested).

#### 5. A good example and a bad example

- **Good (R7 2)** -- Lullaby. Founder: *On how many of the last 7 nights did a typical parent have to work out why
  their baby was crying?* -- range *4 to 7 nights out of 7*; belief *Parents of babies under six months face this on 4
  to 7 nights out of 7.* Stranger: *On how many of the last 7 nights did you have to work out why your baby was
  crying?* *1 · 2 · 3 · 4 · 5 · 6 · 7 · I can't recall.* For: 4 to 7; against: 1 to 3.
- **Bad (R7 0)** -- Palus, cycle 4 (spec 174 FR-5): *In the last 3 months, on how many did you leave raised cash sitting
  in your bank's money market fund?* *1 · 2 · 3 · I can't recall.* **What breaks it:** *on how many did you* drops the
  unit, so *1*, *2* and *3* measure nothing the founder's *2 to 3 months out of 3* can be read against; and *leave ...
  sitting* is a standing state, not an act that happened on a given month.

#### 6. Pitfalls the readers have seen

- The window's unit said twice (*in the last 3 months, in how many months*) or dropped past the spoken cap (*on how many
  did you*) (cycle 8, proposal 47; spec 174 FR-5).
- A lasting state (money left sitting, an agent failing) counted by day or month, so the person cannot tell what counts;
  the thing named in words other than the trade's (cycle 8, 47).
- The founder's question packing two conditions, a cause or a result into the event, or asking about an outcome the
  person never sees (*guests booking elsewhere*) (cycle 8, 39).

#### Open

- **Spec 131 vs registry.** FR-1a sketches Frequency's options as *the window's units as bands*; the registry serves one
  button per unit from 1 to the window's count (a number box past 7) and the founder a range -- there are no bands. The
  card follows the registry.
- **Not settled.** The registry's option rule lets the founder set a range from 0; this card scores a range starting
  at 0 or 1 R7 0 by FR-1c's own words, but whether the founder's question should refuse such a range is not settled.
<!-- card:problem.frequency:end -->

---

<!-- card:problem.importance:begin -->
### Importance · `problem.importance`

**Registry:** PROBLEM, order 3 · founder `rival_list` (saves 2 to 5, own first, 9 words; *I'm not sure* allowed) ·
stranger `pick_one_then_one` (part 1) · compare `share_in_picks` · escape `none_of_these`, counts against · floor 5.
**Screens:** the founder's Answer and Check · the stranger's item · the card after the answers.

#### 1. What it measures

How much they want this problem made easier, next to the other things that are hard for them.

#### 2. The options' shape

- **The founder's list** (code `own` first, then `rival_1` to `rival_4`): the founder's own difficulty -- the problem
  itself, locked, **first** -- then the other difficulties the founder named, **one to four, in their words; Keel adds
  none**. Save needs three in all (the own item and two), because the stranger picks two.
- The own item is the founder's problem whole: their verb and the when or where they named, both halves of a pair kept,
  never narrowed to one part, never the circumstance said again. The own row is the hurt Prevalence tests
  (keel-cloud 216, `L37b`): `went_wrong` said as the difficulty, on its verb, never the circumstance or the whole job
  (*Typing up the log after the walk*, not *Getting the day into the log*). **Keel's own row is the writer's act from
  the study's problem clause** (keel-cloud 229): the act these people do or put up with at that moment, as a
  difficulty a stranger would want made easier (*Picking up booking calls before they ring out*; *Sizing a job's
  memory so it never runs out*), held by code -- **A1** a word of the clause beyond the people's and the occasion's,
  **A2** an *-ing* act, never what befell them (*Losing ...*, *Having ...*, *Being ...*), **A3** not the job or the
  circumstance said again, **A4** at most 9 words, no idea name, no number the founder did not write; a breach: one
  repair turn, then **code's phrase** (keel-cloud 223: `went_wrong` as a noun phrase, its verb in the *-ing* form, at
  most 9 words, else cut by its trailing phrase -- *Losing site notes before writing the daily log*); the writer's own
  row only where the study holds no clause, or neither fits. Each other row: a difficulty these same people meet
  themselves, in their own part of the work, at that moment -- never another role's, setting's or channel's; it keeps
  its aim (never a look-alike chore); at most 9 words; no two overlap, none a part or a cause of another; never a wish,
  a fix or a product; no number the founder did not write.
- **The notes under the rows** (keel-cloud 223), never a refusal -- the founder's words are saved and the belief carries
  them: where the founder rewords the own row into the job or the circumstance said again, the Check notes it, *This
  reads as what every one of them does. Strangers pick what hurts; name the part that goes wrong.*; on Save, the review
  reads the rivals back (the review switch on) and a rival that is a part, a cause or a means of the own row, in another
  channel or outside the moment the circumstance names, or one difficulty with another row, carries one sentence of
  why, in the people's words. **The review may change such a rival** (keel-cloud 232, 235): a part, a cause or a means
  of the own row, or one difficulty with another row, is **put aside, never reworded** (*Choosing a seat where they can
  see every face* is how they follow the talk: reworded, it lands on a piece of the own row); a rival in another channel
  or outside the moment is reworded only where its aim survives as a **different** difficulty these same people meet
  themselves at that moment, in their own part of the work, at most 9 words (*Answering group requests that come by
  email* -> *Taking group enquiries over the phone*), held by code to the rules for the rows above -- it keeps a word of
  the founder's row and borrows no word of the own row the founder's row did not have, else it is put aside; where no
  such reading exists, put aside -- never the own row, never under three rows. The Check says what Keel changed in one
  line, the founder's words stay under the row behind **Put back**, and nothing they typed is lost; a change code
  refuses under the floor is the note alone.
- The belief: *{actor_plural} have {list_size} things that are hard when {circumstance}. {value} is one of the two they
  would most like made easier.* Keel's bar is fixed: one of their two.
- **The stranger's item:** *Think of your last {occasion}. Which one of these would you most like made easier?*, then,
  with the list in place and the pick marked, *And one more?* **One measure: which they would most like made easier.**
  The options are the founder's list reworded into the people's words, shuffled per study, **the own item never first**
  and never missing; each a task the person does, opening on their own verb in the same *-ing* shape, one thing (no
  list, slash or bracket inside), none the whole job, none holding another. A row that is someone else's job is
  dropped; at least three stay. Never names the idea.

#### 3. For, against, neither

- **For:** the founder's own difficulty (`own`) among the person's picks -- first or second; *Nothing else* after
  picking it first counts too (the first pick alone, counted as one pick).
- **Against:** two other rows picked and the own item left out; one other row and then *Nothing else*;
  `none_of_these` *None of these* -- the one escape on any card that counts against.
- **Neither:** a guess; a No at the gate (never asked); a story chip that ended the interview.
- **The bar:** holds if at least 2 in 3 put it in their two. Floor 5.
- **Balance:** each person is for or against; the own item is one row among three to five, so most picks can land
  either way.
- **Healthy:** the own item is on the stranger's list (else nothing can count for: R7 0), and there are at least two
  other rows (so a person can fill both picks without it).

#### 4. The escape

**Escape:** `none_of_these` *None of these*, at the first ask only, and it counts **against**. At the second ask
`nothing_else` *Nothing else* takes its place -- not an escape: the first pick stands alone. *None of these* must be at
the first ask and must not be at the second. The founder's side: *I'm not sure* leaves the dimension out.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Lullaby. Founder's list: *Knowing what the cry means* (own, first, locked) · *Getting the baby back
  down after a feed* · *Getting back to sleep yourself* · *Keeping track of the night's feeds*; belief *Parents of
  babies under six months have four things that are hard when the baby cries in the night. Knowing what the cry means is
  one of the two they would most like made easier.* Stranger: *Think of your last night. Which one of these would you
  most like made easier?* *Getting the baby back down after a feed · Working out what the cry means · Getting back to
  sleep yourself · Keeping track of the night's feeds · None of these* -- then *And one more?* with *Nothing else*. For:
  any two holding *Working out what the cry means*; against: two others, or *None of these*.
- **Bad (R7 0)** -- Codyco, reservation agents, the own item lost on the way to the stranger: *Think of your last shift.
  Which one of these would you most like made easier?* *Handling guests' requests at the desk · Keeping rates right on
  every channel · Answering booking emails and group requests · Getting through the check-in rush · None of these.*
  **What breaks it:** the founder's own *Answering every booking call before it rings out* is not among the options --
  nothing can count for the belief, which can only be refuted.

#### 6. Pitfalls the readers have seen

- The own row losing the founder's verb or moment, or swollen into the whole job; rivals drifting to a look-alike chore
  or to another role's or channel's work (front-desk rows for a central reservations office; phone calls for
  face-to-face talk) (cycle 7, proposal 38; cycle 8, 41).
- Options written as bad outcomes that read backwards after *made easier* (*losing the thread*, *calls that ring out*,
  *cash earning little*), a cause or cost as a row (*too few linemen*), or one option swallowing another (cycle 7, 44;
  cycle 8, 48).
- The own item missing from the list (09-karsa, 20-lemma) (cycle 8, 41 and 48).
<!-- card:problem.importance:end -->

---

<!-- card:problem.current_solution_satisfaction:begin -->
### Current solution · `problem.current_solution_satisfaction`

**Registry:** PROBLEM, order 4 · founder `scale_lines` (saves exactly 5, 9 words, a phrase; *I'm not sure* allowed) ·
stranger `single_choice_5` (part 1) · compare `below_line` · escape `someone_else_checks` (or `cant_recall`, by the act),
apart · floor 5.
**Screens:** the founder's Answer (two boxes) and Check · the stranger's item · the card after the answers.

#### 1. What it measures

How well the way they handle it today gets the job done.

#### 2. The options' shape

- **The founder's Answer** has two boxes, each at most 25 words: the first, what they do today (the act and its means:
  tools, habits, workarounds); the second, how it goes (the founder's own rungs, and where *good enough* ends).
- **The Check screen:** the act as a bare gerund phrase in the people's own words (*working out what the baby needed*;
  never opening on *your way of*, never a bare *it*), and **exactly five outcomes, best to worst** (codes `outcome_1` to
  `outcome_5`), each at most 9 words (a founder's rung too, said in fewer of their words), parallel, one clause saying
  how it turned out.
- **One measure:** every rung is a step on the one scale of the cost the founder's Answer names -- time, money, how
  often, quality -- never a stand-in (when the log was finished, yield alone). **Keel's rungs stay on the founder's
  measure** (spec 226): each is the founder's act going worse on it, never another place, another act or an outcome in
  place of the measure (*The cash sat in checking earning nothing* under four rungs of yield after fees; *Failed
  partway and had to be resubmitted* under three of idle reservation; *Calls that rang out were simply lost* under four
  of who was called back). A rung is the outcome alone, never the outcome and its cost at once (*It settled my doubt
  but took substantial effort*), unless the founder's measure is that cost. Code reads Keel's rungs (`W-rung`, one
  repair turn, then noted): no noun after *the* or a possessive that the founder's rungs and the act do not say; every
  word the founder's three or more rungs all share; no *but* / *though* clause naming effort, time or money where the
  founder's rungs grade none.
- **The first rung is today's way getting the job done** -- the founder's where the Answer names one; else Keel's,
  written above theirs and tagged as Keel's until the founder saves; never a less bad shortfall (spec 203). **The last
  rung is today's way failing outright** (it never got done). Between: the founder's own rungs word for word in the
  order typed, then Keel's worse ones to five. Each shortfall named has its own worse rung; one rung is the usual case;
  no rung joins two states with *and* or *or*; no two overlap; no true answer left out.
- **The line** sits under the last founder rung the Answer calls acceptable (under the first by default; after 2 where
  the Answer types none) and **always under a working rung**: never above the first rung (the Save refuses it), never
  under a shortfall rung (code raises it). So 1 to 4 rungs sit above it. **The founder places it** (spec 226): the Check
  carries the line as a control, drawn where the draft put it, movable to under the first to the fourth rung -- under
  the last rung that still counts as today's way working (`lineAfter`, 0 to 3); a line placed under a shortfall rung is
  refused with the reason. The bar names the rung just above the line by its exact words on the final list: *Holds if at
  least 2 in 3 land below '{rung}'.* -- and the card after the answers and the brief name the rung the founder chose.
  The founder rewords and moves the line; the order is fixed.
- **The notes** (spec 226): on Save, the review reads the five rungs back for one measure and may draw one sentence
  under a rung that grades something else (*this rung grades whether the job ran, not how much it held*). **The review
  rewrites the five as one scale** (specs 232, 235): the measure is the first rung's; where any other rung grades
  something else, every rung that must move is rewritten so the five are one ladder on that measure, best to worst,
  each rung a distinct step on it (a time, an amount, a share, a count) -- never a condition or the reason it went that
  way (*Called back once other calls cleared* says why a call waited, not when it was called back) -- at most 9 words,
  the last today's way failing outright on it (*Never called back*, never *simply lost*). Code holds the ladder whole or
  not at all (`W-rung`, the rules above, no condition clause, distinct from both neighbours); on code's refusal the
  review is asked once more for the whole ladder, inside the Save's hold, else the rungs stay the founder's with the
  notes alone. The first rung, the order, the five and the line never move. The Check says *Keel rewrote the scale so
  every answer is a step in {measure}.* (the measure in the people's words; else what Keel changed in one line), the
  founder's words stay under the rung behind **Put back**.
- The belief: *For most {actor_plural}, {value} still falls short.* -- {value} the act.
- **The stranger's item:** *Think of the last {occasion}. How did {the act} go?* -- one act, the step that hurts, on that
  one occasion (it may ask what it cost: how long, how much). The options are the five saved rungs **in order**, the
  working one first, each answering that exact question, no method, no two both true; the true answer of anyone who did
  it is always one of the five. Then the one escape. Never names the idea.

#### 3. For, against, neither

The belief tested is *today's way still falls short*. So:

- **For the belief:** every rung **below** the line -- today's way fell short (`outcome_3` to `outcome_5` on a line
  after 2).
- **Against the belief:** every rung **above** the line -- the first, and any other above it: today's way did the job
  (`outcome_1` and `outcome_2` on a line after 2). In today's way's own terms these are the answers *for today's way*.
- **Neither:** the escape (`someone_else_checks` *Someone else did it*, or `cant_recall` *I can't recall*), apart; a
  guess; a No at the gate; a story chip that ended the interview.
- **The bar:** holds if at least 2 in 3 land below the rung just above the line. Floor 5.
- **Balance:** 1 to 4 rungs against (above the line), the rest for (below it) -- most often 1 or 2 against, 3 or 4 for.
- **Healthy:** at least one rung above the line reads as today's way working, and at least one below it falls short.
  A scale of five shortfalls is R7 0 wherever its line sits: the rung above the line is a shortfall counted as if
  today's way had worked, nothing can truly count for today's way, a person whose last time went fine has no answer, and
  the belief is tested against nothing. Code reads a rung as a shortfall by its words -- *inconsistent*, *uneven*,
  *unsupported*, *too weak*, *never enough*, *not enough*, *fail* / *fails* / *failed* / *failing* / *failure*, *fell* /
  *falls short*, *not good enough*, *didn't work* / *did not work*, *doesn't work*, *never worked*, *cost them money* --
  unless the word before it negates it
  (*nothing*, *no*, *none*, *never*, *without*, *nobody*). A shortfall in other words (*took three tries*) is not seen by
  code: the reader must see it.

#### 4. The escape

**Escape:** exactly one, apart. `someone_else_checks` *Someone else did it* (code writes it to the occasion: *Someone
else did it that night*) where the act could have been handed off; `cant_recall` *I can't recall* where it could not
(following a conversation, sizing a job you submit yourself) -- the list writer's `handed_off`, *Someone else did it*
where unwritten. Must be there; never both. The founder's side: *I'm not sure* leaves the dimension out.

#### 5. A good example and a bad example

- **Bad (R7 0)** -- the angel-group screening study on staging, 2026-11-03 (spec 203). The act: *screening startup decks
  before the committee meets.* The five: *Inconsistent* · ┄ line ┄ · *Too uneven* · *Unsupported* · *Too weak* · *Never
  enough*; the bar *Holds if at least 2 in 3 land below 'Inconsistent'*; the stranger's item serves the same five, then
  *Someone else did it*. **What breaks it:** *Inconsistent*, *too uneven*, *unsupported*, *too weak*, *never enough* --
  every rung is a shortfall, no rung where today's way works; *Inconsistent*, above the line, is counted against the
  belief as if it had worked, so nothing can truly count for today's way and *still falls short* is tested against
  nothing. (keel-cloud's `TheScaleHasAWorkingRungTest` rebuilds the same shape in full rungs: *Inconsistent evidence
  across the decks · Unsupported claims reached the committee · Evidence too weak to decide on · Never enough evidence
  to decide · The screening failed outright*, the line under the first.)
- **Good (R7 2)** -- the same study redrawn as spec 203 has it: *Evidence was clear enough to decide* (Keel's, tagged
  until saved) · ┄ line ┄ · *Inconsistent evidence across the decks* · *Unsupported claims reached the committee* ·
  *Evidence too weak to decide on* · *Never enough evidence to decide*; the bar *Holds if at least 2 in 3 land below
  'Evidence was clear enough to decide'*. For: rungs 2 to 5; against: rung 1. Lullaby's scale passes as it is: *Knew
  what the baby needed straight away · Got it right after one wrong guess* · ┄ line ┄ · *It took a few tries to find it
  · Tried everything before anything worked · Nothing worked; the baby settled alone* -- for 3 to 5, against 1 and 2.

#### 6. Pitfalls the readers have seen

- **No rung where today's way works** -- five shortfalls, the first counted against the belief as if it worked. On
  cycle 8 all fourteen Check screens scored R4 1 or 2 for overlap and coverage, and no reader named it (spec 131's
  reason; keel-cloud 203).
- The bar naming a rung that is not on the final list (ten of fourteen in cycle 8); rungs grading a stand-in (when the
  log was finished, yield alone) instead of the cost the Answer names; joined *or* / *and* rungs; the usual case, or a
  common true answer (someone else did it, another tool), missing (cycle 7, proposal 35; cycle 8, 36).
- On the item, a stem asking one act and options measuring another -- 08-fresco: the stem asked how the photo upload
  went, the options were about the log (R4 0); a stem pasting two acts, a tool list or a segment label (cycle 7, 43;
  cycle 8, 46).

#### Open

- **Spec 131 vs registry.** FR-1a's sketch, *for: the first rung and the ones above the founder's line; against: every
  rung below it*, counts for and against **today's way**. The registry's rule (`below_line`) and its belief (*{value}
  still falls short*) count the rungs below the line **for the founder's belief** and the rungs above it against. The
  card states both and the test reads the registry's.
- **Spec 203 FR-3 vs code.** FR-3 says the served card never counts a shortfall rung as for today's way; a list saved
  before 203 whose first rung is a shortfall keeps its line under that rung (`SavedList.lineAfter` is never above the
  first; 203's tasks.md, *not done as written*), so on such a list the shortfall still counts against the belief. Re-
  saving it is refused until the first rung is reworded.
<!-- card:problem.current_solution_satisfaction:end -->

---

<!-- card:solution.compatibility:begin -->
### Compatibility · `solution.compatibility`

**Registry:** SOLUTION, order 1 · founder `item_list` (saves 2 to 4, 16 words, picked, with `asked`; *I'm not sure*
allowed) · stranger `fixed_four` (part 2, after the reveal) · compare `fixed_last_two_against` · supports `yes_easily`,
`yes_with_steps` · escape `cant_tell` · floor 5.
**Screens:** the founder's Answer, Check and Choose · the stranger's item · the card after the answers.

#### 1. What it measures

How well your idea fits the way they already work: their tools, their routines, their habits.

#### 2. The options' shape

- **The founder's list:** 2 to 4 conditions the idea must meet, each at most 16 words, a verb phrase with no subject of
  its own (it reads whole after *Most {actor_plural}*), each with its stranger's clause (`asked`: second person, framed
  by code to at most 20 words, no question mark). Each is one whole act with one thing to weigh -- a clear yes or no for
  every usual way of doing the job (two things joined are two conditions); none already true of everyone the study is
  about, by the founder's segment or by the usual way of doing the job; none narrower than the part of the mechanism it
  tests; the step the idea depends on most never missing; no two about the same thing; no number the founder did not
  write. Keel marks one suggested (the one most likely missing, the one that costs the stranger most) with why; on
  Choose (*Which of these is most likely to be missing?*) the founder picks the one to test. Belief: *Most
  {actor_plural} {value}.*
  **Each row's kind** (spec 225): the writer writes `kind` on every row -- **ability** (the person could do it
  themselves), **fact** (true of them or not) or **permission** (someone else allows it or sets it up for them) --
  from the row's words and the context, beside `settled_by`; code holds it: a row whose words name an allower or a
  sign-off is a permission; a row opening on *could* with no allower is an ability unless the writer says why not; a
  row with no kind (saved before, or reworded since) takes the word test. **The suggestion is never settled:** Keel's
  suggested row is held to the same `settled_by` test as the founder's -- settled, it is refused once and then dropped,
  and no other is suggested in its place. **The review may change a condition that breaks this card** (keel-cloud
  233, 236, the review switch on): on Save of the Check, before the pick, it reads the conditions back -- **every row
  is read, Keel's included** (its drafted rows and its suggestion, as the founder's) -- a permission someone else
  holds, typed as an ability, is rewritten so the words say so, with a permission code reads (*could forward
  unanswered calls to another number* -> *were allowed to have unanswered calls forwarded to another number*), the kind
  following the words; a line that is no condition (a wish, a benefit, a feature or a step of the idea) is rewritten
  into the condition behind it, else put aside. **A rewrite faces the settled test too:** where all but every one of
  them has what it says, the row is put aside instead. **Two rows about one thing are one, by meaning:** two rows about
  the same integration, tool or step -- the narrower is put aside, its why naming the row that covers it. Code holds
  every change to the rules above (16 words, the kind by its words, no two alike, never the idea's name), never under
  two rows. The Check says what Keel changed in one line, the words it changed stay under the row behind **Put back**
  (Keel's as served), nothing is lost; a change code refuses is the note alone. **The suggestion moves when put
  aside:** where the review puts the suggested row aside, or no suggested row is kept, it may suggest the step of the
  mechanism no kept row tests, in row shape, with its why; code adds it at the end as the suggested row, held to the
  rules above against every kept row, never beside a kept suggestion nor past four rows, and Choose offers it as
  Keel's suggestion. **A settled row is put aside, not noted:** a condition all but every one of the segment already has is put aside, its why saying what
  settles it (*Most of your segment already has this ...*), behind **Put back**; with the review off, a row the writer
  marks settled carries that sentence as a note under it, never a refusal, and the founder may pick it.
- **The stranger's item:** *On your last {occasion},* the picked condition asked as a question (*could you have ...?*,
  *was ...?*). **Fixed answers, in order** (`yes_easily` · `yes_with_steps` · `only_with_help` · `no`), worded by the
  row's kind, the codes fixed:
  - a **permission** (allowed, approval, sign-off, or an act someone else does for them): *Yes, easily · Yes, with some
    steps · Only with help or approval · No*; **the permission stem is the passive whichever way the row is written**:
    where the act is done for the person -- a could-row (*could you have forwarded ...*) or an allowed-to row (*were you
    allowed to have unanswered calls forwarded ...*) alike -- the stem is in the passive, by code from the asked face
    (*Think of your last booking call. Could unanswered calls have been forwarded to another number?*); a permission
    the person would exercise themselves (*were allowed to upload the data to an outside tool*) keeps the face as
    written;
  - an **ability** (could, able): *Yes, easily · Yes, most of the time · Only sometimes · No*;
  - a **fact** (where something is, what they have): **three** -- *Yes · Yes, with some steps · No*; `only_with_help`
    is never served on a fact.
  Then *I can't tell*. **One measure:** could they have, on that occasion.

#### 3. For, against, neither

- **For:** `yes_easily` (*Yes, easily* / *Yes*) and `yes_with_steps` (*Yes, with some steps* / *Yes, most of the
  time*) -- the conditional yes counts for, drawn lighter, split in the count line.
- **Against:** `only_with_help` (*Only with help or approval* / *Only sometimes*) and `no` (*No*).
- **Neither:** `cant_tell` *I can't tell* (apart); a guess; a No at the gate.
- **The bar:** holds if no more than 1 in 3 answer the last two (at least 2 in 3 for); past it *Did not hold*. Floor 5.
- **Balance:** 2 for, 2 against (a fact: 2 for, 1 against).
- **Healthy:** the asked condition is true for some of these people and false for others. A condition the segment
  already settles (everyone says Yes) can never be refuted: R7 0. A clause that is not one whole act leaves the options
  no true answer.

#### 4. The escape

**Escape:** `cant_tell` *I can't tell*, apart -- must be on the item, and only it. The founder's side: *I'm not sure*
leaves the dimension out.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Fresco, an ability: belief *Most construction superintendents on commercial jobs could talk over
  the noise on site.* Stranger: *On your last site walk, could you have spoken into your phone over the noise?* *Yes,
  easily · Yes, most of the time · Only sometimes · No · I can't tell.* For: the first two; against: the last two.
- **Bad (R7 0)** -- Fresco, the condition the segment already settles: *The job kept its logs in Procore or ACC*, for a
  segment of *superintendents at US general contractors whose jobs run on Procore or ACC*. Stranger: *On your last site
  walk, was your job already keeping its daily logs in Procore or ACC?* *Yes · Yes, with some steps · No · I can't
  tell.* **What breaks it:** *Procore or ACC* is true of everyone the study is about -- every answer is Yes, nothing can
  count against, and the condition the pitch rests on (stopping to film and talk) is not tested.

#### 6. Pitfalls the readers have seen

- Rows the segment already settles (*Procore or ACC*, *SLURM or Kubernetes*) taking a slot while the condition the pitch
  rests on (stopping to film and narrate; keeping the current bank) is missing; a row narrower than the mechanism
  (cycle 7, proposal 58; cycle 8, 60).
- A fact offered *Only with help or approval* (AirCaps, Expanse, cycle 4: *nonsense for my own phone*), or a could-you
  label turned into a did-you act so the graded options have no true answer; clipped or vague clauses (*the way things
  were set up*), qualifiers dropped (*two days* for *one to two business days*) (cycle 7, 67; cycle 8, 70; spec 185).
- The belief's doubled subject (*For most superintendents, they could ...*) and a hint pasting the whole segment
  (cycle 7, 57; cycle 8, 59).
<!-- card:solution.compatibility:end -->

---

<!-- card:solution.relative_advantage:begin -->
### Relative advantage · `solution.relative_advantage`

**Registry:** SOLUTION, order 2 · founder `benefit_list` (saves 1 to 4, 9 words; *I'm not sure* allowed) · stranger
`scale_four` (part 2, after the reveal) · compare `fixed_last_two_against` · supports `a_lot_better`, `a_little_better`
· escape `cant_tell` · floor 5.
**Screens:** the founder's Answer and Check · the stranger's item · the card after the answers.

#### 1. What it measures

What your idea must do better than their way today before they would bother to switch.

#### 2. The options' shape

- **The founder's list:** 1 to 4 benefits, all equal, each at most 9 words, a noun phrase naming what changes compared
  with today's way (written against the founder's own Current solution list); one benefit a row, none overlapping; the
  one the founder leads with always a row; a benefit today's way already delivers flagged for the founder to keep or
  drop (the review off); no number the founder did not write. The belief carries every kept benefit, in the order
  typed, joined with *and*: *For most, with it, {hard_case_theirs} would have given them {value}.* -- the moment it
  cost them, the study's problem clause in the founder's words (*their last daily log where they lost site notes*),
  never any last occasion; *their last {occasion}* only where the study holds none. **The review may put a benefit
  aside** (keel-cloud 237, the review switch on): on Save of the Check it reads the benefits back beside the founder's
  Current solution list and the study's hard case -- a benefit today's way already gives (the rungs above the
  founder's line say so), one not true of the hard case, or the second of two rows about one gain (its why naming the
  first) is put aside, never reworded; the one the founder leads with is never put aside, and one row always stays.
  The Check says so in one line (*Keel put one benefit aside so what is left is what only your idea would have given
  them.*), the founder's words stay behind **Put back**, nothing is lost; the belief carries the rows left.
- **The stranger's item:** *Think of {hard_case}. Would {Name}, {what it is}, have helped you {job} better, or
  not?* -- the hard case the advantage is for, as the study's problem clause says it to them (*the last job that ran
  out of memory*; *the last time ...* is said *the most recent time ...*), never any occasion; where the study holds
  none, *Think of the last {occasion} when {circumstance}.*; then the question names the job the idea is for (the
  context's, said to them), never *that* with nothing before it to point at; only the at-stake anchor (*Think of the
  last {occasion} when you had to {job}.*, where neither fits) keeps *have done that better for you, or not?*, its
  *that* the job it names. One thing asked, how much better or not; no benefit of the founder's named in the question
  or the options. The clause is written once per study -- by the founder's Prevalence writer, or by the problem
  card's where the study has no problem questions -- and held by code (H1 the hurt, never the routine; H2 *the last*,
  the occasion once; H3 no idea, product, benefit or number; H4 the spoken cap). **The review may rewrite the hard
  case** (keel-cloud 237, the review switch on): the same read-back reads it against the clause's own went-wrong
  words -- where it is not one moment and the moment it cost them (the routine, the job again, a standing state, an
  absence), it is rewritten from the went-wrong words in both shapes, or written where the study holds none; code
  holds the pair by H1-H4 as the writer's, the clause standing where it fails; the Check says so in one line (*Keel
  changed the moment the question asks about so it is the one that went wrong.*) and the belief reads the new
  moment. **Fixed answers, in
  order and in these words, code's:** `a_lot_better` *A lot better* · `a_little_better` *A little better* ·
  `no_difference` *No difference* · `worse` *Worse*; then *I can't tell*. **One measure:** better or not, and how much.

#### 3. For, against, neither

- **For:** `a_lot_better`, `a_little_better`.
- **Against:** `no_difference`, `worse`.
- **Neither:** `cant_tell` *I can't tell* (apart); a guess; a No at the gate.
- **The bar:** holds if no more than 1 in 3 say no difference or worse; past it *Did not hold*. The card says how many
  of the for said a lot. Floor 5.
- **Balance:** 2 for, 2 against, always the same four.
- **Healthy:** the four, with *No difference* and *Worse* on it. Options that are the founder's benefits (*which of
  these would have made it better?*) leave no answer that says it would not have helped: R7 0.

#### 4. The escape

**Escape:** `cant_tell` *I can't tell*, apart -- must be on the item, and only it. The founder's side: *I'm not sure*
leaves the dimension out.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Lullaby: benefit *Fewer tries before the baby settles*; belief *For most, with it, their last night
  the baby would not settle would have given them fewer tries before the baby settles.* Stranger: *Think of the last
  night your baby would not settle. Would Lullaby, a phone app, have helped you work out what the baby needs better,
  or not?* *A lot better · A little better · No difference · Worse · I can't tell.* -- the night the baby would not
  settle, never *their last night*, which a parent whose last night went fine answers *No difference*; the job named,
  so *better* says at what (what it is gives way to its head before the job leaves the question).
- **Bad (R7 0)** -- the founder's benefits served as the options (the shape before spec 159): *Which of these would have
  made your last night better? Fewer tries before the baby settles · Knowing why the baby cried · Getting back to sleep
  sooner · I can't tell.* **What breaks it:** every option is a benefit -- there is no *No difference* or *Worse*, so
  every answer counts for and the belief can never be refuted; and the founder's benefits are shown to the stranger.

#### 6. Pitfalls the readers have seen

- The belief keeping only the first benefit the founder typed (eleven of twelve failures in cycle 8), or rows bundling
  two gains, splitting one, or dropping the one the founder leads with (cycle 7, proposals 60 and 61; cycle 8, 62 and
  63).
- The stranger's occasion any last one, not one where the job was at stake (*a call they handled fine*), or an
  ambiguous word (*your last pole*, *cash decision*); *go better* leaving which better unclear (cycle 7, 68; cycle 8,
  71).
- The occasion narrowed to a single item no benefit can be true of (*their last shipment*) (cycle 8, 62 and 63).
- The stranger asked about an ordinary day -- the job or a standing state (*the most recent time you had to get each
  job to run to the end*, *had no time to manage the cash*), not the moment it went wrong; a benefit today's way
  already gives kept as the advantage; *done that better* pointing at nothing once the hard case came first (cycles 15
  to 17).
<!-- card:solution.relative_advantage:end -->

---

<!-- card:solution.adoption_friction:begin -->
### Adoption friction · `solution.adoption_friction`

**Registry:** SOLUTION, order 3 · founder `item_list` (saves 1 to 4, 9 words, picked, with `asked`; *I'm not sure*
allowed) · stranger `fixed_four` (part 2, after the reveal) · compare `fixed_last_two_against` · supports `yes`,
`yes_if_worth_it` · conditional `yes_if_worth_it` · escape `cant_tell` · floor 5.
**Screens:** the founder's Answer, Check and Choose · the stranger's item · the card after the answers.

#### 1. What it measures

The extra effort it asks of them to start using it: setting it up, learning it, changing a habit.

#### 2. The options' shape

- **The founder's list:** 1 to 4 efforts, the founder's own, in their order, each one effort of at most 9 words, a
  base-form verb phrase in one voice (*their*, never *your*), each a step these people take **themselves** -- never
  another role's sign-off, a setup the founder's team or the product does. Each carries its stranger's clause (`asked`,
  at most 10 words, *it* for the idea), framed by code to at most 20. Keel may add **at most one** suggested step -- a
  one-time step before first use, or the new habit first use asks -- last, with its why, outside the 1 to 4, never the
  belief unless the founder picks it. No two the same step; none a condition another screen already tests (fitting what
  they use now is Compatibility, getting it bought Purchase friction); only the founder's numbers. The founder picks one.
  Belief: *Most would {value}.*
- **The stranger's item:** *To use {Name}, you'd {asked}. Would you do that, or not?* **Fixed answers, in order:**
  `yes` *Yes* · `yes_if_worth_it` *Only if {condition}* -- the stranger's own condition, written beside the clause:
  the assurance that would make them say Yes, what it has to do or promise in their work (*Only if it hands me the hard
  calls*), never the danger they fear (*Only if they risk my job failing*: keel-cloud 216, `K12`), never one
  true of every step; *Yes, if it was clearly worth it* where the item carries none · `probably_not` *Probably not* · `no` *No*; then *I can't tell*. **One measure:**
  would they take this effort.

#### 3. For, against, neither

- **For:** `yes` and `yes_if_worth_it` -- the conditional yes counts for, drawn lighter, split in the count line.
- **Against:** `probably_not`, `no`.
- **Neither:** `cant_tell` *I can't tell* (apart); a guess; a No at the gate.
- **The bar:** holds if no more than 1 in 3 say probably not or no; past it *Did not hold*. An effort too much for most
  is amber, never red: this line never reads *Not holding up*. Floor 5.
- **Balance:** 2 for, 2 against.
- **Healthy:** the effort is one the person takes themselves, so their answer answers it; the condition in *Only if* is
  this person's and not true of every step (else it is a second *Yes*). An effort someone else does leaves the options
  nothing true to say: R7 0.

- **Settled by keel-cloud 205 (the registry's note):** 2026-11-03, spec 205 (FR-4; the dimension card's Open point): the
  note above ends on spec 184 -- since spec 198 (FR-9) the conditional yes is the person's own condition again: asked.md
  writes `condition` beside the clause (at most 7 words) and code serves 'Only if {condition}'
  (RespondentItems.onlyIfOptions), the plain 'Yes, if it was clearly worth it' the fallback where an item carries none.
  Codes, supports, conditional and the compare rule unchanged.

#### 4. The escape

**Escape:** `cant_tell` *I can't tell*, apart -- must be on the item, and only it. The founder's side: *I'm not sure*
leaves the dimension out.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Lullaby: effort *Hold the phone near the cot for ten seconds*; belief *Most would hold the phone
  near the cot for ten seconds.* Stranger: *To use it, you'd hold your phone near the cot for ten seconds. Would you do
  that, or not?* *Yes · Only if it didn't wake the baby · Probably not · No · I can't tell.* For: the first two;
  against: the last two.
- **Bad (R7 0)** -- a clinic's medical assistants, the effort another role's sign-off: *To use it, you'd get your
  clinic manager to approve it. Would you do that, or not?* *Yes · Yes, if it was clearly worth it · Probably not · No ·
  I can't tell.* **What breaks it:** *get your clinic manager to approve it* is someone else's step (and Purchase
  friction's ground) -- the assistant's answer says whether they would ask, not whether they would take on the effort
  of using it, so no option answers the belief.

#### 6. Pitfalls the readers have seen

- The fixed *Yes, if it was clearly worth it* blurring into plain *Yes* and hiding the real catch (clinic approval, a
  minute before the next call) -- spec 198 FR-9's *Only if {condition}* (cycle 7, proposal 66; cycle 8, 69).
- Rows slipping from *their* to *your*; the hardest step, a new habit of use, missing because the suggestion admitted
  only a one-time setup; a row repeating what Compatibility or Purchase friction tests (cycle 7, 55; cycle 8, 56).
- Choose options bundling two efforts, or steps another role, the founder's team or the product does (a sign-off, a
  vendor-built wallet) (cycle 8, 57).
<!-- card:solution.adoption_friction:end -->

---

<!-- card:commercial.existing_sacrifice:begin -->
### Existing sacrifice · `commercial.existing_sacrifice`

**Registry:** COMMERCIAL, order 1 · founder `cost_estimate` (*I'm not sure* allowed) · stranger `value_box` (part 3; on
a business study the decision-maker's link) · compare `interval_contains_median`, supporting side `costs_more` · escape
`dont_know` · floor 5.
**Screens:** the founder's question (q) · the stranger's item · the card after the answers.

#### 1. What it measures

What the problem already costs them: money they spend, time it takes, or a share they lose, over a period you choose.

#### 2. The options' shape

- **The founder's question -- no options.** Asked of the one who pays (the founder's unit: the company, the site, the
  household), never of people who only do the work. The mode first, each in the people's words naming what is spent or
  lost: money they spend (`MONEY`, $), time it takes (`HOURS`; a consumer's own time never priced), or a share they lose
  (`RATE`: a percent of the founder's base, or a count word, with *what do they lose?*) -- never a bare *a share*. Then a
  range (low above 0; a percent at most 100), the base and the unit (the founder's words, 1 to 8 words, no digits; the
  base required on a rate), and one period of six -- a day, a week, a month, a quarter, a year, each (*each time*); the
  periods never share a list with the modes. The founder's mode, measure and numbers are kept exactly: money is never a
  count, a count never shown with %, no number rounded. Code writes the question and the belief: *What does this
  problem cost {payer} today?* and *The problem already costs {deciders} {value}.* -- the heading's payer and the
  belief's {deciders} one and the same, the unit that pays, in the plural (keel-cloud 216, 227): on a business study
  the organisation the people work at, as the context names it (*hotel groups*, *venture-backed startups*); where the
  user pays, the people; never a role inside it (*operations leads*, *finance leads*, *the director*). A count is a
  count: *{payer} already lose about {low} to {high} {measure} per {unit} a {period}* (*about 12 conversations per
  person a month*), no *of {base}*, its measure word drawn where a percent draws %; a percent keeps *of {base}*. The
  unit is the founder's as typed, its *per {unit}* kept wherever the equation shows it (*of the reserved GPU hours per
  cluster a month*), said once where the base already names it; with none typed, no *per* at all, never a word from
  the base or the loss line. The time path keeps the people who spend the hours.
- **The stranger's item -- one value box, code's**, in the founder's own unit and period: the question takes its verb,
  its thing and its base from the founder's loss line, by code where code reads it, else written from the line by the
  writer under the same rule (keel-cloud 222, 239: the clause in *Last {period}, about what percent of {base} ...?* or
  *... about how many {measure} ...?*, a word of the line kept, every word one {actor_plural} use for the founder's
  meaning, no idea, number or money, the thing said once, within 20 words; asked whenever the item would otherwise
  carry a neutral verb, on a money-only study by its part-3 job; two repair turns), in the person's own words and the
  past -- the thing they see go. Never *lose*, *lost*, *miss*, *go without* or *fell through*: past the writer's second
  failure, the plain not-done by code where the line has a verb it can say so (*unanswered*: *did not get answered*;
  *lost track of*: *did you not keep track of*), else the founder's own line said to the person, and the Check says
  Keel could not name what they see go. The base is the one the line names where it names one (*interest on operating
  cash*: the operating cash; the Check says so), else the founder's; the typed *per {unit}* kept in the question and
  the label on the decision-maker's link, said once; the label after the box one plain phrase (*hours per site last
  month*); answered *between ... and ...* (one number fills both). *None* is the number 0 while it is served. Then the
  one escape; spoken *Or say you can't recall.* **One measure:** the founder's own unit, base and period.

#### 3. For, against, neither

Each answer is read by its low end against the founder's low:

- **For:** at the founder's low or above (above the founder's high: *it costs more than you think*).
- **Against:** below the founder's low -- *None* (0) included on a business study.
- **Neither:** `dont_know` *I can't recall* (apart); on a consumer study, *None* after a Yes at the gate (apart: it named
  no cost, spec 128 FR-21); a guess. In a rate mode a *None* is never read as *it costs less than you think*.
- **The bar:** at least 2 in 3 at the founder's low or above. Floor 5.
- **Balance:** an open box -- any number below the founder's low counts against, any at or above it for, so both sides
  are always open while the box measures the founder's cost.
- **Healthy:** the box asks the founder's unit, base and period. A box in another unit (days where the founder typed a
  percent; hours where they typed dollars) leaves no answer that can be placed against the founder's low: R7 0.

#### 4. The escape

**Escape:** `dont_know` *I can't recall*, apart -- must be there, and only it (the consumer's *I'd rather not say* is
gone, spec 198). *None* is an answer (0), never the escape. The founder's side: *I'm not sure* leaves Existing sacrifice
out, and Ability to pay with it.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Fresco: the founder's time, *30 to 60 hours per site a month on the daily log*; belief
  *Construction superintendents on commercial jobs already spend 30 to 60 hours per site a month on the daily log.*
  Decision-maker's link: *Last month, about how many hours per site did your team spend on the daily log?* [ box ]
  *hours per site last month* · *None* · *I can't recall*. For: 30 or more; against: under 30, *None* included.
- **Bad (R7 0)** -- Palus: the founder's *about 2% of the balance per company a year: interest on cash that sits in the
  operating account*. Stranger: *Last year, about how many days did cash sit in your operating account?* [ box ] *days*.
  **What breaks it:** *how many days* against *2% of the balance* -- the box counts days, the belief is a share of
  money, so no answer can be placed at or below the founder's low and nothing counts either way.

#### 6. Pitfalls the readers have seen

- The belief pinning the cost on a role who only does the work (operations leads, *startup founders*) instead of the
  unit that pays; the founder's mode or numbers redrawn (money as a count; *1 to 1.5 points* as *2%*); a count shown
  with %; an opaque *a share they lose* (cycle 7, proposal 16; cycle 8, 17).
- The heading on a role while the belief names the paying unit (*What does this problem cost contractor operations
  leads today?*); a count pushed through the share frame (*about 12 conversations of the conversations they are in*,
  a % beside it); a unit the founder never typed (*jobs*) and the typed *per cluster* dropped (cycle 14; keel-cloud
  227).
- A vague verb or *lost* on the item (*miss*, *lost*, *reserve and never use*); a long window in the founder's unit that
  forces the person to multiply (cycle 7, 26; spec 184 FR-8b (c)).
- The neutral verb served where nobody wrote the clause (*did you go without in booking calls that rang out
  unanswered*, *did you go without* on the base alone, *fell through*: cycles 13 to 18, the money-only studies, whose
  one job was never asked); the base another pot than the line's (*the long-term reserve* where the loss was on the
  operating cash); the typed *per cluster* dropped; a word of the trade's that means something else to the people
  (cycle 18; keel-cloud 239).
- Two ways to say nothing: a *None* chip and a spoken *none is 0*, or a second escape (cycle 7, 26; spec 198 FR-3).

#### Open

- **Spec 198 FR-3 vs registry.** FR-3 drops the *None* chip; the registry keeps it served *until the interview contract
  and keel-web drop it*. The card treats *None* as an answer (0) while it is served.
- **Registry vs code (spec 128 FR-21).** The registry says *'None' is the number 0* and *'Nothing' counts as nothing*;
  code sets a consumer's *None* apart (*named no cost*) and counts it only on a business study. The card follows the
  code.
<!-- card:commercial.existing_sacrifice:end -->

---

<!-- card:commercial.price:begin -->
### Price · `commercial.price`

**Registry:** COMMERCIAL, order 2 · founder `price_range` (not sure: *No price yet*) · stranger `price_ladder` (part 3;
asked of whoever pays) · compare `ordinal_band`, supporting side `higher` · escape `cant_say` · floor 5.
**Screens:** the founder's question (q) · the stranger's item · the card after the answers.

#### 1. What it measures

What the person who pays would give for it, set against what the problem already costs them.

#### 2. The options' shape

- **The founder's question -- no options.** One of four shapes, each named as the founder's trade charges its payers:
  a fixed fee each period (over the payers' own billing unit where they are billed by one: *a fixed fee per site each
  month*); a percent -- **only ever of money** the payer holds, pays or gains, naming what it is a percent of (the cost's
  base, or what it brings back, named as the payers name it), never a count, time, people or a loss rate, never a bare
  *a share*; one price first, then a fee, an optional plan, or nothing; or free to them (only where someone else decides
  to pay: the one who decides is not among the people with the problem, as the WHO DECIDES screen answered). The founder
  types only the amount or the percent; base, unit and period are the cost estimate's, shown locked. Code asks *What
  price do you have in mind for {Name}?* -- the idea by its name where the study holds one, else the offer as the seed
  puts it (a noun phrase naming the product). The belief names the idea the same way and keeps the founder's whole
  range, unit, period and every term they attached: *{deciders} would think {Name} worth {value}.* (a percent: *...
  would think a fee of {value} fair for {Name}.*); *it* only where the study holds no name.
- **The stranger's item -- code's.** The stem names base, unit and period once (*What would Fresco be worth to you a
  month, per site?*), with no word that leans on the amount (*small*, *only*, *just*). **Six rungs:** five bands around
  the founder's lowest price, **one band edge exactly at it**, each the amount alone, no amount in two rungs (*to under*
  on every band but the last, *or more* on the last), then *I wouldn't pay for this*; then the escape. A percent price
  serves percent bands; one price first then a plan serves two ladders of six (the one-off, then the plan); free to
  them serves no item. Spoken in two steps: under the middle band, the middle band, its top or more, or wouldn't pay --
  *Or say: I can't say.* -- then, after *under* or *over*, the two bands on that side. **One measure:** the price, in
  the founder's base, unit and period.

#### 3. For, against, neither

- **For:** a band whose lower edge is the founder's low or above -- the founder's band or higher (above the founder's
  high: *higher than you think*).
- **Against:** every band below the founder's low (the *Under ...* band included) and `would_not_pay` *I wouldn't pay
  for this* -- an answer, counted against. On one price first then a plan, a person is for only when both steps are at
  or above the founder's, and *I wouldn't pay for this* up front is against on both.
- **Neither:** `cant_say` *I can't say* (apart); a guess. Free to them: no item; the line is left out (*Free to them ·
  paid by {role}*).
- **The bar:** at least 2 in 3 at the founder's price or more. Floor 5.
- **Balance:** most ladders: two bands below the founder's low and *I wouldn't pay for this* against (three), three
  bands from the low up for (three). Near the ends of the ladder the split moves (a low at the ladder's first point: one
  band below; near its top: one band from it), and code always keeps both sides.
- **Healthy:** a band edge exactly at the founder's low, at least one band below it and one from it. A ladder whose
  bands all start at or above the founder's low (or all below it) is not code's ladder: R7 0. A percent of something
  that is not money is not a price anyone can pay: R7 0.

#### 4. The escape

**Escape:** `cant_say` *I can't say*, apart, spoken *Or say: I can't say.* -- must be there, and only it. *I wouldn't pay
for this* is an answer, never the escape. The founder's side: *No price yet* leaves Price out, and Ability to pay with
it.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Fresco: the founder asked *What price do you have in mind for Fresco?*, answered *$800 to $1,000
  per site a month*; belief *Contractor operations leads would think Fresco worth $800 to $1,000 per site a month.*
  Stranger: *What would Fresco be worth to you a month, per site?*
  *Under $500 · $500 to under $800 · $800 to under $2,500 · $2,500 to under $5,000 · $5,000 or more · I wouldn't pay
  for this · I can't say.* For: *$800 to under $2,500* and up; against: *Under $500*, *$500 to under $800*, *I wouldn't
  pay for this*.
- **Bad (R7 0)** -- a percent of a count reaching the options (cycles 7 and 8): *Fresco takes a fee of a percent of the
  daily log. What fee would feel fair to you?* *Under 1% · 1% to under 2% · ...* **What breaks it:** *a percent of the
  daily log* -- the log is not money, so no band is a sum anyone pays, and no answer can stand for or against a price.

#### 6. Pitfalls the readers have seen

- A percent of something that is not money (*of the daily log*, *of the conversations*, *of the GPU hours*, *of the
  reservation calls*), a bare *what it gets back*; the per-site, per-user or per-event fee these payers are billed by
  missing (cycle 7, proposal 18; cycle 8, 19).
- The belief narrowing the founder's range, adding a unit, or dropping a term they attached (a pilot, a credit, an
  optional plan) (cycle 7, 17 and 18; cycle 8, 18 and 19).
- The spoken escape *Or say you can't say*; a leaning word (*small*) in the stem; the founder's sticker price sitting on
  a band edge (cycle 7, 27; cycle 8, 29).
- The founder's question and belief not naming an idea the study has named: *What price do you have in mind for
  something for the end-of-day documents?* and *... would think it worth $800 to $1,000 per site a month.* on a study
  whose idea is Fresco (cycle 14; keel-cloud 220).
<!-- card:commercial.price:end -->

---

<!-- card:commercial.ability_to_pay:begin -->
### Ability to pay · `commercial.ability_to_pay`

**Registry:** COMMERCIAL, order 3 · founder `derived` (no founder screen) · stranger `single_choice`, `b2b_link_only`
(the consumer's budget item on the people's link where cost and price share no base) · compare `cost_covers_price`,
supporting side `more_covering` · escape `cant_recall_one` (served `cant_say`: see the escape) · floor 5.
**Screens:** the stranger's item · the card after the answers. There is no founder question.

#### 1. What it measures

Whether the person who pays has money they can use for it at your price.

#### 2. The options' shape

- **The founder's side -- no screen, no options, no answer.** Keel writes the belief from the cost and the price, by
  its reading: *compare* (a money cost and a money price over the same unit and period), *out of the gain* (a percent of
  the cost's own base), *from what comes back* (a percent of what it brings back), *free* (free to them, paid by the
  decider) or *budget* (no shared base, unit and period: the budget question). Left out when the cost or the price is.
- **Who is asked:** only a person whose Price answer was at or above the founder's price -- the item points back to it.
  Written, per person: *You said about {their band}. If you went ahead at that, where would the money come from?*;
  spoken, one clip for every band: *Think of the price you just gave. If you went ahead at that, where would the money
  come from?*
- **Fixed answers, in order** (the decision-maker's link) -- five sources of money, each a tenseless noun phrase that
  reads after *did* and after *would*, each where the money comes from, never whether there was any:
  `existing_line` *An existing budget line* · `charged_to_users` *Charged back to whoever uses it* ·
  `new_line_signed_off` *A new budget line, signed off for it* · `outside_funding` *New money from outside, such as a
  grant* · `taken_from_other_spend` *Taken from other spending*; then the escape.
- **Each source holds in any organisation** (keel-cloud 241): no label names a unit of one kind of organisation (*team*,
  *site*, *department*, *branch*), and outside money is told apart from a line already there -- *new money from
  outside*, never a grant that already sits in a budget line.
- **The consumer's budget item** (a study where the user pays and cost and price share no base): *Could you pay {price}
  for this from money you already spend, or not?* -- `from_spend` *From money I already spend on this* · `new_money`
  *From other money I'd set aside* · `could_not` *I couldn't pay it*; then *I can't say*.
- On the *compare*, *out of the gain* and *from what comes back* readings the card is read from the cost each person
  typed on Existing sacrifice (only those at or above the price), never from a budget answer; a consumer study then asks
  no budget item.

#### 3. For, against, neither

- **For (budget, business):** `existing_line`, `charged_to_users`, `taken_from_other_spend` -- money already there.
  **(budget, consumer):** `from_spend`.
- **Against (budget, business):** `new_line_signed_off`, `outside_funding` (and a stored `no_budget`). **(budget,
  consumer):** `new_money`, `could_not`.
- **For / against on the derived readings:** *compare* and *out of the gain* -- for, a person whose own cost is at or
  above the founder's price low (*loses your price or more*); against, less. *From what comes back* -- for, loses some;
  against, loses nothing.
- **Neither:** the escape (apart); everyone whose Price answer was below the founder's price, *I wouldn't pay for this*,
  or no price -- not asked, listed apart (*named less*, *would not pay*, *gave no price*); a guess.
- **The bar:** at least 2 in 3 of those asked. Fewer than 5 reached the price: *Too few to call* (*k of n named your
  price or more · 5 needed*); none: *Not reached* -- it decides nothing. Floor 5.
- **Balance:** business 3 for, 2 against; consumer 1 for, 2 against.
- **Healthy:** sources on both sides, each a source of money in a tense that fits *would*. Options that say whether
  there was money (*There was no budget for it*) or a list that is all one side cannot answer the question asked: R7 0.

#### 4. The escape

**Escape:** served `cant_say` *I can't say*, apart, on the item that points back to the price and on the consumer's
budget item; the registry's `cant_recall_one` *I can't recall one* (it covers *it was free*) on the past-tool question
(*Think of the last tool your team paid for. Where did the money come from?*) where no price chain is read. Must be
there, one. The founder's side: no *I'm not sure* of its own -- left out when the cost or the price is left out.

- **Settled by keel-cloud 205 (the registry's note):** 2026-11-03, spec 205 (FR-4; the dimension card's Open point):
  this code and label are the past-tool question's ('Think of the last tool your team paid for'), asked where no price
  chain is read. On a chain study code serves `cant_say` 'I can't say' instead, apart, spoken 'Or say: I can't say.' --
  on the item that points back to the person's own price (spec 181, CommercialChain.side) and on the consumer's budget
  item (spec 115). The field keeps naming the past-tool escape; nothing here moves.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Fresco, budget reading, a contractor whose Price answer was *$800 to under $2,500*: *You said about
  $800 to $2,500 a month. If you went ahead at that, where would the money come from?* *An existing budget line ·
  Charged back to whoever uses it · A new budget line, signed off for it · New money from outside, such as a grant ·
  Taken from other spending · I can't say.* For: the first, second and fifth; against: the third and fourth.
- **Bad (R7 0)** -- the same item with the list before spec 198: *... where would the money come from?* *A budget line
  we already had · A new budget line, signed off · Taken from other spending · There was no budget for it.* **What
  breaks it:** *There was no budget for it* is not a source of money, and its past tense cannot follow *would*; money
  money charged back to whoever uses it and new money from outside have no home.

#### 6. Pitfalls the readers have seen

- *There was no budget for it*: not a source of money, past tense under a *would* stem; grants and money charged to the
  units that use the tool missing (cycle 7, proposal 23; cycle 8, 25).
- The card reading *1 of 1 (at least 2 in 3)* as met beside a 5-needed floor, and showing Keel's derived belief as one
  the founder checked (cycle 7, 9; cycle 8, 9).
- Asked of everyone, not only those at the price, it read *Holding up* beside a failing Price (cycle 4; spec 181).
- *Charged to the teams or sites that use it* named the units of one kind of organisation, and *A grant or outside
  funding* blurred with a grant already in an existing line: neither held in every organisation the readers walked
  (cycle 18, proposal 6; keel-cloud 241).

#### Open

- **Registry note vs the chain.** The registry's `compare_rules.cost_covers_price` describes only the reading before the
  chain (a person's cost at or above the price low, over Existing sacrifice's people); the chain's readings (specs 115,
  181, 198) live in the row's `_note` and in code. The card follows the code.
<!-- card:commercial.ability_to_pay:end -->

---

<!-- card:commercial.buyer_payer_alignment:begin -->
### Buyer and payer · `commercial.buyer_payer_alignment`

**Registry:** COMMERCIAL, order 4 · founder `role_list` (saves 1 to 3, 4 words, picked, `nobody_else` fixed first; *I'm
not sure* allowed) · stranger `fixed_four` (part 3) · compare `first_supports` · supports `had_to_agree`,
`decided_alone` · escape `cant_recall_one` (*I can't say*) · floor 5.
**Screens:** the founder's Answer, Check and Choose · the stranger's item · the card after the answers.

#### 1. What it measures

Whether the person who uses it, the person who decides and the person who pays are one person, and who else has to agree.

#### 2. The options' shape

- **The founder's list:** *Nobody else* first (`nobody_else`, fixed), then the roles the founder named as having to
  agree -- **at most two, one row each, in their words and order, each at most 4 words; Keel adds none, drops none**.
  Every row carries one plain tag (has the problem · decides to buy · has to agree · does not have to agree); the person
  with the problem and the decider are one row where they are the same person. The belief carries every role tagged
  *has to agree*, joined with *and*: *{decider} decides, and {value} must agree first.* -- *nobody else* only where the
  founder named nobody or ruled every one out. Choose asks *Which do you want to test?*: the decider alone, or the
  decider with the roles; a list holding only *Nobody else* is a statement to confirm.
- **The stranger's item.** On the decision-maker's link: *Could you sign off on {price} yourself, or would {the role}
  have to agree?*; where the user pays: *The last time you paid for something like this, did {the role} have to
  agree?* (*anyone else* / *someone else* where *Nobody else* is tested). **Fixed answers, in order, from alone to
  someone else's decision, each opening differently, no Yes or No in front:** `decided_alone` *I could sign off myself*
  (past: *I decided on my own*) · `had_to_agree` *{The role} would have to agree* (past: *had to agree*; *Someone else*
  where *Nobody else* is tested) · `someone_else_agreed` *Several people would have to agree* · `someone_else_decided`
  *It's someone else's call*; then *I can't say*. The role in the founder's title for it. **One measure:** who has to
  agree to this purchase.

#### 3. For, against, neither

- **A role tested -- For:** `decided_alone` (easier than the founder said) and `had_to_agree` (as they said).
  **Against:** `someone_else_agreed`, `someone_else_decided` -- it sits wider than the founder said.
- **Nobody else tested -- For:** `decided_alone` alone. **Against:** `had_to_agree`, `someone_else_agreed`,
  `someone_else_decided`.
- **Neither:** `cant_recall_one` *I can't say* (apart); a guess.
- **The bar:** at least 2 in 3. A line that held mostly on *decided alone* reads *fewer had to agree than you said*.
  Floor 5.
- **Balance:** a role tested, 2 for and 2 against -- the belief tested is *as you said or easier*; *Nobody else* tested,
  1 for and 3 against.
- **Healthy:** the four, in order, the tested role named in the second. A belief that says the opposite of the founder's
  list (a typed role read as *nobody else*) counts the founder's own answer against them: R7 0.

#### 4. The escape

**Escape:** `cant_recall_one`, labelled *I can't say* (the code kept, spec 192), apart, spoken *Or say: I can't say.* --
must be there, and only it. The founder's side: *I'm not sure* leaves the dimension out.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Palus, the founder naming the board: belief *The founder decides, and the board must agree first.*
  Decision-maker's link: *Could you sign off on about 0.25% of the balance a year yourself, or would the board have to
  agree?* *I could sign off myself · The board would have to agree · Several people would have to agree · It's someone
  else's call · I can't say.* For: the first two; against: the last two.
- **Bad (R7 0)** -- Palus as cycle 7 found it: the founder typed *The board*; the belief read *The founder decides, and
  nobody else has to agree.*, and the item asked *Could you sign off on it yourself, or would someone else have to
  agree?* **What breaks it:** *nobody else* for a founder who typed *The board* -- the strangers who say the board would
  have to agree, the founder's own answer, are counted against the founder.

#### 6. Pitfalls the readers have seen

- The belief carrying one picked role so a second named role fell out (eight of nine failures in cycle 8), or a typed
  role turned into *nobody else* (Palus) (cycle 7, proposal 10; cycle 8, 10).
- Check rows untagged or cased unevenly, or a role the founder never named (a finance director, a board) shown as if it
  might have to agree; Choose pasting the product's pitch into the bar (*bought stop guessing memory, time and GPUs*)
  (cycle 7, 11 and 12; cycle 8, 11 and 12).
- On the item: a Yes buried behind a No, Yes and No in front of an either-or question, three *someone else* answers
  that blur by ear; the spoken *Or say you can't say* (cycle 7, 24; cycle 8, 26).

#### Open

- **Belief vs item (registry `_why_199`, spec 199 FR-1).** With two roles named, the belief names both (*the CFO and the
  project executive must agree first*) while the stranger's item names only the role picked (*The CFO would have to
  agree*; code `RespondentItems` reads the list's tested item). The item can then confirm only one of the roles the
  belief names. The registry chose it; whether R7 reads it as one rule bent is not settled.
<!-- card:commercial.buyer_payer_alignment:end -->

---

<!-- card:commercial.purchase_friction:begin -->
### Purchase friction · `commercial.purchase_friction`

**Registry:** COMMERCIAL, order 5 · `b2b_only` · founder `item_list` (saves 1 to 4, 9 words, picked) and the founder's
time (1 to 99 days, weeks or months; *I'm not sure* allowed) · stranger `duration_bands` (part 3, the decision-maker's
link) · compare `duration_band` · supports `not_needed` and the bands at or under the founder's time · escape `cant_tell`
· floor 5.
**Screens:** the founder's Answer, Check and Choose (with the time box) · the stranger's item · the card after the
answers.

#### 1. What it measures

The steps between wanting it and buying it: approvals, reviews, setting up an account, switching over.

#### 2. The options' shape

- **The founder's list:** 1 to 4 steps on the buyer's own side that must be cleared before paying, each a brake the
  founder does not control, a noun phrase of at most 9 words with its object (*a security review of an agent on every
  node*); every step the founder typed kept in their words, only true overlaps merged; no step containing or repeating
  another; never the founder's own offer, pitch, trial, pilot, guarantee or onboarding, nor a step the pitch says it
  removes; the biggest blocker first. Keel may add **at most one**, tagged suggested, never a step done inside one of
  the founder's rows, only one this buyer's own process has, and no role but the approver or reviewer the buyer's kind
  of organisation always has. The founder picks one and **types the time it will take -- the founder's alone**, never
  Keel's, never prefilled; *not sure* is an answer, and the belief then names no time. Belief: *Most {deciders} would
  get through {value} within about {duration}, or not need it.*
- **The stranger's item -- code's:** *If you bought {Name}, how long would {the step} take?* -- the step's own time,
  never *before it went through*. **Six chips:** five duration bands around the founder's time, **one band edge exactly
  at it** (the ladder 1 day · 3 days · 1 week · 2 weeks · 1 month · 3 months · 6 months · 1 year · 2 years, the point
  nearest the founder's time giving way to it; the band below it *to under* it), then `not_needed` *It wouldn't be
  needed*; then *I can't tell*. For about 6 weeks: *Under 2 weeks · 2 to under 6 weeks · 6 weeks to 3 months · 3 to 6
  months · Over 6 months · It wouldn't be needed.* Spoken as Price's: under the founder's time, its band, over it, or
  it wouldn't be needed -- then the band within. **One measure:** how long the step would take. Asked only on a
  business study.

- **Settled by keel-cloud 205 (the registry's note):** 2026-11-03, spec 205 (FR-4; the dimension card's Open point):
  b2b_only stands. Spec 182's FR-6 (a consumer path: a founder whose user pays may name a timed obstacle) was not opened
  (182's tasks.md), so the dimension is calibrated and asked on business studies only.

#### 3. For, against, neither

- **For:** every band at or under the founder's time (its upper edge at the time or below) and `not_needed` *It
  wouldn't be needed*.
- **Against:** every band above the founder's time -- from the band that **starts at** the founder's time upward.
- **Neither:** `cant_tell` *I can't tell* (apart); a guess.
- **The bar:** holds if no more than 1 in 3 say it would take longer than the founder expects; past it *Did not hold*.
  The card names the band most often chosen by those who expect longer. Floor 5.
- **Balance:** most times: two bands and *It wouldn't be needed* for (three), three bands against (three). A very short
  time (1 day) leaves one band for and four against; a very long one (about 2 years) four for and one against -- code
  always keeps both sides.
- **Healthy:** the founder's own time is the edge, and the step is a brake on the buyer's side, so a long answer means
  the sale waits. A step that is the purchase itself or the founder's own offer, or a time the founder never typed,
  measures nothing of this buyer: R7 0. (A list saved before spec 182 has no time and asked the fixed three: *Yes, and it
  would take a long time* against; *Yes, but it would be quick* and *No, it wouldn't be needed* for.)

#### 4. The escape

**Escape:** `cant_tell` *I can't tell*, apart -- the question is about a purchase not yet made; must be there, and only
it. *It wouldn't be needed* is an answer, and counts for. The founder's side: *I'm not sure* leaves the dimension out.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Expanse: step *A security review of an agent on every node*, about 6 weeks; belief *Most cluster
  operators would get through a security review of an agent on every node within about 6 weeks, or not need it.*
  Stranger: *If you bought Expanse, how long would a security review of an agent on every node take?* *Under 2 weeks ·
  2 to under 6 weeks · 6 weeks to 3 months · 3 to 6 months · Over 6 months · It wouldn't be needed · I can't tell.* For:
  the first two and *It wouldn't be needed*; against: *6 weeks to 3 months* and longer.
- **Bad (R7 0)** -- Keel's suggestion picked, with Keel's time: step *A signed contract*, *about 2 weeks* the founder
  never typed. Stranger: *If you bought Fresco, how long would a signed contract take?* *Under 1 week · 1 to under 2
  weeks · 2 weeks to 1 month · 1 to 3 months · Over 3 months · It wouldn't be needed · I can't tell.* **What breaks
  it:** *a signed contract* is the purchase itself, not a step between wanting it and buying it, and *about 2 weeks* is
  not the founder's -- the edge the whole scale turns on is no one's belief.

#### 6. Pitfalls the readers have seen

- The belief carrying a time the founder never typed (*about 2, 4 or 6 weeks*), and the saved list keeping one of the
  founder's three steps (cycle 7, proposal 19; cycle 8, 20).
- Keel's added row a formality every deal has or the purchase itself (a signed contract, a paid pilot, a budget
  approval repeating who decides) while the real gate this buyer's trade and place impose (a data protection review, a
  works council) is missing; overlapping rows (cycle 8, 21).
- *How long would it take before it went through* -- a trial, a check or a waiver does not go through (cycle 8, 30); the
  card counting the band that starts at the founder's own time against without saying so (cycle 7, 20; cycle 8, 22).
<!-- card:commercial.purchase_friction:end -->

---

<!-- card:commercial.commitment:begin -->
### Commitment · `commercial.commitment`

**Registry:** COMMERCIAL, order 6 · founder `one_step` (saves 1 to 2, 9 words; *I'm not sure* allowed) · stranger
`fixed_four` (part 3) · compare `fixed_last_two_against` · supports `yes_start`, `yes_after_trying` · conditional
`yes_after_trying` · escape none · floor 5.
**Screens:** the founder's Answer and Check · the stranger's item · the card after the answers.

#### 1. What it measures

What they would actually do before paying: give their time, install it, share their data, introduce someone, put down a deposit or join a trial.

#### 2. The options' shape

- **The founder's step** (code `step`): the first real step, in base form so it follows *would*, at most 9 words, in
  the people's words, keeping every term that changes what the person agrees to (free, no commitment, a small part,
  returnable, money back, the product's name, who does the work), naming what it acts on and where the money goes;
  where the founder's side does the work, the person lets them do it; no timing, urgency or condition the founder did
  not write; no number they did not write. Then, **only when the step costs the person money, data or a signature**, a
  smaller step that costs nothing (code `smaller_step`, a noun phrase of at most 9 words), drafted on the Check for the
  founder to keep or change: installing or running anything of the founder's on their systems, letting it read or
  measure them, or handing over their records counts as data, free or not; only a step that takes none of the three
  goes without. Belief: *Most {actor_plural} would {value}.*; where someone else decides, *In most cases {decider} would
  {value}.*
- **The stranger's item:** *If it were ready today, would you {step}, or not?* **Fixed answers, in order:** `yes_start`
  *Yes, I'd {step}* (the step's own verb and the step whole, eleven words with its frame -- §10's one exception; never
  *Yes, I'd start one*) · `yes_after_trying` the soft yes -- *Probably, after {smaller step} first* where the founder's
  list carries one (one opening on its act said in its *-ing* form, *Probably, after trying a pair first*), *Probably
  yes* where it does not -- on every list · `probably_not` *Probably not* · `no` *No*. No escape. Spoken: *Yes, you'd
  {step}; probably yes; probably not; or no.*
  **One measure:** would they take this step.

#### 3. For, against, neither

- **For:** `yes_start` (the step as asked) and `yes_after_trying` (the soft yes, drawn lighter, split in the count line).
- **Against:** `probably_not`, `no`.
- **Neither:** a guess; a No at the gate on the people's link. The item has no escape.
- **The bar:** holds if no more than 1 in 3 say probably not or no; past it *Did not hold*. Floor 5.
- **Balance:** 2 for, 2 against -- a firm and a soft answer on each side.
- **Healthy:** the first option says yes to the founder's own step, and the soft yes is a yes to it too. A first option
  that names no step, or a second that is the step again, cannot answer the belief: R7 0. An escape on this item is a
  broken rule: *No* is the floor.

- **Settled by keel-cloud 205 (the registry's note):** 2026-11-03, spec 205 (FR-4; the dimension card's Open points):
  the _decided line's second yes 'counted neither for nor against' is history -- spec 180 (FR-1) counts the soft yes for
  (drawn lighter, split in the count line) and spec 198 (FR-1) serves one on every list: 'Probably, after {smaller step}
  first' where the list carries a smaller step, 'Probably yes' where it does not. The drift template loses 'now', as
  spec 199 (FR-5) took it out of both belief templates.
- **The drift template:** *you said most would {founder} · {observed} of {n} would* (the registry's `drift_template`,
  without *now*).

#### 4. The escape

**Escape:** none -- *No* is the floor (the registry's `escape: null`). An escape here would let a hesitant person count
for nobody instead of saying *Probably not*. The founder's side: *I'm not sure* leaves the dimension out.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Fresco: step *start a paid pilot on one site*, which costs money, so the list carries the free
  smaller step *a look at how it works*; belief *In most cases the general contractor would start a paid pilot on one
  site.* Decision-maker's link: *If it were ready today, would you start a paid pilot on one site, or not?* *Yes, I'd
  start a paid pilot on one site · Probably, after a look at how it works first · Probably not · No.* For: the first
  two; against: the last two.
- **Bad (R7 0)** -- AirCaps as cycle 4 served it: *If it were ready today, would you order a pair with free returns, or
  not?* *Yes, I'd start one · Yes, after trying it first · Probably not · No.* **What breaks it:** *Yes, I'd start one*
  names no step, so a yes to it is not a yes to ordering a pair; *Yes, after trying it first* is the step again (free
  returns is trying it first) -- neither yes answers the belief.

#### 6. Pitfalls the readers have seen

- Both belief templates adding a *now* no founder wrote; the step cut to nine words by dropping the terms that define it
  (*free*, *no commitment*, the euro sign, *glasses*) (cycle 7, proposal 13; cycle 8, 13 and 14).
- *Probably not* with no *Probably yes*, so a hesitant yes had to overstate; only three options served where the
  founder's list had no smaller step (cycle 7, 25; cycle 8, 27).
- The step worded as if the person did the founder's work, or *the trial* said as if strangers knew of it (cycle 8, 14).
<!-- card:commercial.commitment:end -->
