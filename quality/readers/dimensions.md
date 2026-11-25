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

**What a card is.** One card per dimension of keel-cloud's registry, twelve, in the registry's order (three of the
problem since keel-cloud 269 retired Current solution, three of the solution, six of the money). Each card says, in plain words and for the founder's screens and the
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
  against); a guess (an answer with no story behind it); a person never asked (a No at the gate answers nothing more but
  Importance, keel-cloud 269; on
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
  No and a person with it Yes. A Yes opens the story; a No goes on to Importance, the story and Frequency skipped
  (keel-cloud 269), and the person is still counted. Where the problem's film is shown first, the gate is the fixed
  words *In {window}, have you encountered this issue?* (keel-cloud 277), the clause read instead; on that study the
  clause is noted, never refused, and may be dropped (keel-cloud 277).
- **One clause (keel-cloud 212).** The strangers' event is the founder's clause, by code: the gate carries the
  founder's Prevalence event (keel-cloud 269: Frequency no longer does), turned to the second person by code, never a
  second writer's. The founder's
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

**Registry:** PROBLEM, order 2 · founder `single_choice` (*I'm not sure* allowed) · stranger `fixed_five` (part 1) ·
compare `share_most_or_every`, supporting side `more` · supports `every_time`, `most_times` · escape none ·
floor 5.
**Screens:** the founder's question (q) · the stranger's item · the card after the answers.

#### 1. What it measures

How often someone who has the problem runs into it, when they do the task.

#### 2. The options' shape

- **The founder's question** is code's (keel-cloud 269): *Out of 10 {actor_plural} who have it, how many face it most
  times or every time?* **Exactly five options, code's, Prevalence's bins:** *Fewer than 2 in 10* (`p_0_20`) · *2 or 3
  in 10* (`p_20_40`) · *4 or 5 in 10* (`p_40_60`) · *6 or 7 in 10* (`p_60_80`) · *8 or more in 10* (`p_80_100`). Code
  writes *6 or 7 in 10* at the boxes' yes; the founder may change it. The belief: *Of these {actor_plural} who have it,
  {value} face it most times or every time.*
- **The stranger's item** is code's whole, asked only after a Yes at the gate: *When you {job}, how often does it
  happen?* -- the story's job, said to them, at most 20 words; never a window, a count or the founder's band. **One
  measure: how often, when they do the task.** **Fixed answers, in order:** `every_time` *Every time* · `most_times`
  *Most times* · `about_half` *About half the time* · `now_and_then` *Now and then* · `never` *Never*. Letters A to E.

#### 3. For, against, neither

- **For:** `every_time` *Every time* and `most_times` *Most times*.
- **Against:** `about_half` *About half the time*, `now_and_then` *Now and then* and `never` *Never*.
- **Neither:** a guess; a No at the gate (never asked); a story chip that ended the interview.
- **The bar:** the share of the yes-sayers on *Every time* or *Most times*, placed against the founder's bin as
  Prevalence's share is: in the bin or above holds, the bin just below is people disagree, lower fails. Floor 5.
- **Balance:** two answers for, three against, so the belief can be supported and refuted.
- **Healthy:** the five fixed answers, in order, on the item.

#### 4. The escape

**Escape:** none -- *Never* is the floor. The founder's side: *I'm not sure* is allowed and leaves the dimension out
(asked of nobody; the brief says untested).

#### 5. A good example and a bad example

- **Good (R7 2)** -- Lullaby. Founder: *Out of 10 parents of babies under six months who have it, how many face it most
  times or every time?* -- *6 or 7 in 10*. Stranger: *When you work out what the baby needs and settle them, how often
  does it happen?* *Every time · Most times · About half the time · Now and then · Never.* For: the first two.
- **Bad (R7 0)** -- a count over the window (*On how many of the last 3 months did you ...?*, keel-cloud 158 to 268):
  **What breaks it:** the unit, the window and the event had to agree, and a lasting state could not be counted by month.

#### 6. Pitfalls the readers have seen

- The window's unit said twice, or dropped past the spoken cap; a lasting state counted by day or month (cycles 4 and
  8) -- gone with the count (keel-cloud 269).

#### Open

- **Spec 270** gives the three answers against their follow-up question.
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

- **Keel-cloud 269: the rows are the role's tasks, from the founder's story.** Code writes the list at the boxes'
  yes: the own row is the story's job said as a task (*Checking the payroll before it goes out*), locked, first; then
  the other tasks the founder named on the story's seventh beat, two to four, in their words. The belief: *Of the
  things {actor_plural} have to do, {value} is one of the two they would most like made easier.* The stranger is
  asked *Of the things you do as a {actor}, which would you most like made easier?*, then *And one more?*, over the
  rows shuffled, the own row never first. The rules below are a list saved before 269's.
- **The founder's list** (code `own` first, then `rival_1` to `rival_4`): the founder's own difficulty -- the problem
  itself, locked, **first** -- then the other difficulties the founder named, **one to four, in their words; Keel adds
  none but a row in place of one the review puts aside** (keel-cloud 243). Save needs three in all (the own item and two), because the stranger picks two.
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
  refuses under the floor is the note alone. **In place of each row put aside, Keel suggests one** (keel-cloud 243): a
  difficulty these same people meet themselves at the moment the problem names, drawn from who they are, their job,
  the circumstance and the founder's words, never a part, a cause or a means of the own row (it never opens on the own
  row's act nor says mostly its words), held by code to the rules for the rows above where the row put aside stood;
  the floor of three is met by it, and one code refuses leaves today's floor (the note alone). The rows are handed to
  the review numbered from 0, the own row 0. The Check shows Keel's row with *In place of "{the founder's words}"* and
  **Put back** (one action: the founder's row back where it stood, Keel's row gone); the record below keeps the row put
  aside, struck, with its reason and *Replaced by ...*; the line counts both (*Keel put three rows aside and suggested
  three in their place, so every row sits at the moment your problem names.*).
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
- **Neither:** a guess; a story chip that ended the interview. A No at the gate goes on to this item and its picks
  count (keel-cloud 269).
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

- **Good (R7 2)** -- Lullaby since keel-cloud 269: own row *Working out what the baby needs and settling them* ·
  *Feeding the baby* · *Changing nappies* · *Getting the baby to nap in the day*; stranger *Of the things you do as a
  parent, which would you most like made easier?*. Before 269 -- Founder's list: *Knowing what the cry means* (own, first, locked) · *Getting the baby back
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

<!-- card:solution.compatibility:begin -->
### Compatibility · `solution.compatibility`

**Registry:** SOLUTION, order 1 · founder `single_choice` (Prevalence's five bins, written by code at the board's yes;
*I'm not sure* allowed) · stranger `yes_no` (part 2, after the idea's film) · compare `share_yes`, supporting side
`more` · supports `yes` · escape none · floor 5.
**Screens:** the founder's review row · the stranger's item · the card after the answers.

#### 1. What it measures

How well your idea fits the way they already work: their tools, their routines, their habits.

#### 2. The options' shape

- **The founder's side** (keel-cloud 271, 272; the spoken walk): never asked. Code writes a share bin at the board's
  yes -- *6 or 7 in 10* (`p_60_80`) -- and the founder may change it on the review page. **Exactly five options,
  code's, Prevalence's bins:** *Fewer than 2 in 10* · *2 or 3 in 10* · *4 or 5 in 10* · *6 or 7 in 10* · *8 or more
  in 10*. The workflow beat's steps are the condition. The belief: *At least {value} would find doing {task} this way,
  with {name}, fits how they work.* -- `{value}` the bin's low edge in words (*six in ten*; *some* for the lowest),
  `doing {task}` the job's -ing form, never *doing check the payroll*.
- **The stranger's item** is code's whole, asked after the idea's film: *Would {task_ing} this way, with {name}, fit
  into how you work?* -- the story's job as the person does it, in the -ing form and the second person, the brand's
  name always said; a job that takes the sentence past 20 words gives way to *Would doing it this way, with {name},
  fit into how you work?*. One wording, text and spoken the same, no option read into it, no number. **Fixed answers,
  in order, code's:** `yes` *Yes* · `no` *No* -- letters A and B, one tap, no escape. **One measure:** would it fit how
  they work.

#### 3. For, against, neither

- **For:** `yes` *Yes*.
- **Against:** `no` *No* -- a why follows on the spot (*What would get in the way?*, heading *What would get in the
  way*), up to two whys an interview.
- **Neither:** a person never asked (a No at the check leaves before the plate, a screener's No before the film); the
  whole dimension where the founder chose *I'm not sure* (left out).
- **The bar:** the share of yes against the founder's bin: at or above its low edge holds (above its high edge
  *stronger*); one bin below, people disagree; two bins below or more, *Not holding up*. The So line is evidence only:
  *{k} of {n} said yes.*, or *{against} of {n} said no, past your bar of {limit}. Their reasons are on the Insights
  tab.* Floor 5.
- **Balance:** 1 for, 1 against.
- **Healthy:** the question names the job these people do and the brand they have just seen; a job everyone already
  does this way, or a product they already use, would make every answer *Yes*: the belief could never be refuted, R7 0.

#### 4. The escape

**Escape:** none -- *Yes* or *No* (keel-cloud 272 D4). The founder's side: *I'm not sure* leaves the dimension out of
the study.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Lullaby: belief *At least six in ten would find working out what the baby needs and settling the
  baby this way, with Lullaby, fits how they work.* Stranger, after the film: *Would working out what the baby needs and
  settling the baby this way, with Lullaby, fit into how you work?* *Yes · No.* For: *Yes*; against: *No*, its why
  after it.
- **Bad (R7 0)** -- the question that asks what everyone already has: *Would keeping your daily logs in the tool your
  job already uses fit into how you work?* *Yes · No.* **What breaks it:** the tool is already how every one of these
  people works -- every answer is *Yes*, nothing can count against, and the way the brand changes the job is never
  asked.

#### 6. Pitfalls the readers have seen

- The four rows of the conditional ladder (*Yes, easily* · *Yes, with some steps* · *Only with help or approval* ·
  *No*) before keel-cloud 272: a fact offered *Only with help or approval*, a condition the segment already settles
  taking the item (cycles 4 to 8) -- gone with the four rows; the workflow beat's steps are the condition now.
- *doing {task}* filled with the job's base form (*doing check the payroll*); the brand's name dropped from the
  question so the person cannot tell which way of working is meant (keel-cloud 271 judgement call 6).
<!-- card:solution.compatibility:end -->

---

<!-- card:solution.relative_advantage:begin -->
### Relative advantage · `solution.relative_advantage`

**Registry:** SOLUTION, order 2 · founder `single_choice` (Prevalence's five bins, written by code at the board's yes;
*I'm not sure* allowed) · stranger `yes_no` (part 2, after Compatibility) · compare `share_yes`, supporting side
`more` · supports `yes` · escape none · floor 5.
**Screens:** the founder's review row · the stranger's item · the card after the answers.

#### 1. What it measures

What your idea must do better than their way today before they would bother to switch.

#### 2. The options' shape

- **The founder's side** (keel-cloud 271, 272; the spoken walk): never asked. Code writes a share bin at the board's
  yes -- *6 or 7 in 10* (`p_60_80`) -- and the founder may change it on the review page. **Exactly five options,
  code's, Prevalence's bins:** *Fewer than 2 in 10* · *2 or 3 in 10* · *4 or 5 in 10* · *6 or 7 in 10* · *8 or more
  in 10*. The solution statement and what it says beyond the limitations are the claim. The belief: *At least {value}
  would find {name} better than the way they {task} today.*
- **The stranger's item** is code's whole, asked after Compatibility: *Compared with the way you {task} today, would
  {name} be better?* -- the story's job in its base form, in the second person; the limitations are not restated (they
  are the founder's claim, shown in the film; the comparison is the person's own); a job that takes the sentence past
  20 words gives way to *Compared with the way you do it today, would {name} be better?*. **Fixed answers, in order,
  code's:** `yes` *Yes* · `no` *No* -- letters A and B, one tap, no escape. **One measure:** better than their way
  today, or not.

#### 3. For, against, neither

- **For:** `yes` *Yes*.
- **Against:** `no` *No* -- a why follows on the spot (*What would it have to do better?*, heading *What it would have
  to do better*), up to two whys an interview.
- **Neither:** a person never asked (a No at the check, a screener's No); the whole dimension where the founder chose
  *I'm not sure* (left out).
- **The bar:** the share of yes against the founder's bin, as Compatibility's; the So line is evidence only. Floor 5.
- **Balance:** 1 for, 1 against.
- **Healthy:** the person compares the brand with their own way today, never with the founder's list of benefits;
  options that are the founder's benefits (*which of these would have made it better?*) leave no answer that says it
  would not be better: R7 0.

#### 4. The escape

**Escape:** none -- *Yes* or *No* (keel-cloud 272 D4). The founder's side: *I'm not sure* leaves the dimension out of
the study.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Lullaby: belief *At least six in ten would find Lullaby better than the way they work out what the
  baby needs and settle the baby today.* Stranger: *Compared with the way you work out what the baby needs and settle
  the baby today, would Lullaby be better?* *Yes · No.* For: *Yes*; against: *No*, its why after it.
- **Bad (R7 0)** -- the founder's benefits served as the options: *Which of these would make your nights better?
  Fewer tries before the baby settles · Knowing why the baby cried · Getting back to sleep sooner.* **What breaks it:**
  every option is a benefit -- there is no *No*, so every answer counts for and the belief can never be refuted; and the
  founder's benefits are shown to the stranger.

#### 6. Pitfalls the readers have seen

- The scale of four (*A lot better* · *A little better* · *No difference* · *Worse*) and its hard-case clause before
  keel-cloud 272: the occasion any last one, an ordinary day in place of the moment it went wrong (cycles 7 to 17) --
  gone with the scale; the film carries the claim, the question names the job.
- The limitations restated inside the question, so the person answers the founder's claim and not their own way.
<!-- card:solution.relative_advantage:end -->

---

<!-- card:solution.adoption_friction:begin -->
### Adoption friction · `solution.adoption_friction`

**Registry:** SOLUTION, order 3 · founder `single_choice` (Prevalence's five bins, written by code at the board's yes;
*I'm not sure* allowed) · stranger `yes_no` (part 2, after Relative advantage) · compare `share_yes`, supporting side
`more` · supports `yes` · escape none · floor 5.
**Screens:** the founder's review row · the stranger's item · the card after the answers.

#### 1. What it measures

The extra effort it asks of them to start using it: setting it up, learning it, changing a habit.

#### 2. The options' shape

- **The founder's side** (keel-cloud 271, 272; the spoken walk): never asked. Code writes a share bin at the board's
  yes -- *6 or 7 in 10* (`p_60_80`) -- and the founder may change it on the review page. **Exactly five options,
  code's, Prevalence's bins:** *Fewer than 2 in 10* · *2 or 3 in 10* · *4 or 5 in 10* · *6 or 7 in 10* · *8 or more
  in 10*. The effort is the setup beat's rows, then the person's own steps of the workflow, else *start using {name}
  for {task}* (keel-cloud 271, `IdeaView.effort`). The belief: *At least {value} could start with {name} without much
  trouble.*
- **The stranger's item** is code's whole, always asked, in one of two forms by the setup: with a setup named, *Before
  you could use {name} for this, you would need {the setup}. Could you start without much trouble?* -- the setup's
  rows joined with commas and *and*, a row that opens on an act taking *to*, in the second person where a row names
  the person, as many whole rows as keep the sentence within 20 words; with none, *Could you start using {name} for
  this tomorrow, with nothing to set up first?*. **Fixed answers, in order, code's:** `yes` *Yes* · `no` *No* --
  letters A and B, one tap, no escape. **One measure:** could they start without much trouble.

#### 3. For, against, neither

- **For:** `yes` *Yes*.
- **Against:** `no` *No* -- a why follows on the spot (*What makes it a trouble?*, heading *What makes it a trouble*),
  up to two whys an interview; a third No goes unasked, counted as capped on the Insights card.
- **Neither:** a person never asked (a No at the check, a screener's No); the whole dimension where the founder chose
  *I'm not sure* (left out).
- **The bar:** the share of yes against the founder's bin, as Compatibility's: two bins below is *Not holding up* (red)
  like the other two -- spec 118's amber belonged to the conditional yes, gone with the four rows (keel-cloud 272
  judgement call 14). The So line is evidence only. Floor 5.
- **Balance:** 1 for, 1 against.
- **Healthy:** the setup is one these people would do themselves before first use, said as the founder said it, so
  their answer answers it; a setup someone else does (a manager's sign-off, a vendor's install) leaves the person
  nothing true to say: R7 0.
- **Settled by keel-cloud 205 (the registry's note):** 2026-11-03, spec 205 (FR-4; the dimension card's Open point): the
  note above ends on spec 184 -- since spec 198 (FR-9) the conditional yes is the person's own condition again: asked.md
  writes `condition` beside the clause (at most 7 words) and code serves 'Only if {condition}'
  (RespondentItems.onlyIfOptions), the plain 'Yes, if it was clearly worth it' the fallback where an item carries none.
  Codes, supports, conditional and the compare rule unchanged.
- **Since keel-cloud 272** the conditional yes and its stem are gone with the four rows: the note above is history.

#### 4. The escape

**Escape:** none -- *Yes* or *No* (keel-cloud 272 D4). The founder's side: *I'm not sure* leaves the dimension out of
the study.

#### 5. A good example and a bad example

- **Good (R7 2)** -- Lullaby, a setup named: belief *At least six in ten could start with Lullaby without much
  trouble.* Stranger: *Before you could use Lullaby for this, you would need to let the app use your phone's microphone
  at night. Could you start without much trouble?* *Yes · No.* For: *Yes*; against: *No*, its why after it.
- **Bad (R7 0)** -- a clinic's medical assistants, the setup another role's: *Before you could use it for this, you
  would need your clinic manager to approve it. Could you start without much trouble?* *Yes · No.* **What breaks it:**
  the approval is someone else's step (and Purchase friction's ground) -- the assistant's answer says whether the
  manager would sign, not whether they could start, so no option answers the belief.

#### 6. Pitfalls the readers have seen

- *Yes, if it was clearly worth it* blurring into plain *Yes* and hiding the real catch (cycles 7 and 8) -- gone with
  the four rows; the setup is said in the question now, so the catch is on the screen.
- A setup cut mid-row to fit the cap (*... 12 months of*: keel-cloud 272 judgement call 21), or a row that opens on an
  act said without *to*.
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
