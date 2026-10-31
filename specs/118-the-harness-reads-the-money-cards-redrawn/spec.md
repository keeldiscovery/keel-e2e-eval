# Spec 118 -- The harness reads the cards redrawn and the question screens (keel-cloud 180-185, keel-web 155-156)

The founder's decisions of 2026-10-31 on the six COMMERCIAL cards, the stage header and the Insights tab (keel-cloud
180 the words and the wire, 181 Ability to pay's chain question, 182 Purchase friction's duration item, 183 the why's
placement; keel-web 155 the drawing) move words the harness mirrors, add two respondent items it must answer, and
change the after-answers leg's reading. Corpus revision 20.

## Rules

- **FR-1 Mirrors (keel-cloud 180's tasks.md).** `instructions/brief_facts.py`: `KEEL_BAR` (Purchase friction *holds if
  no more than 1 in 3 say it would take longer than you expect*), `NOT_ASKED_WHY` / `DERIVED_ABILITY_LINE` (Ability to
  pay's belief per reading, 181 FR-4), the Price band labels *to under*, the status words incl. *Not reached*, the
  decider word in place of *the payer*, the hours belief without dollars, the Commitment rows from the step's verb, the
  friction words; every pinned sentence that moved, with why. `cloud_facts_at_104` (117's tense tolerance) is removed:
  the build is past it.
- **FR-2 The two new items.** `harness/vectors_script.py` / the readers answer Ability to pay only when served (181:
  the pointing-back question, written form quoting the respondent's own band; the skip when the respondent's Price
  answer is below the founder's price, *I wouldn't pay*, or the escape) and Purchase friction's six duration chips
  (182). The corpus entries gain each person's duration band and, where the entry's Price answer is at or above the
  founder's price, a budget answer; the back-test yaml entries follow keel-cloud 182 FR-7 (the duration beside the
  step). Corpus revision 20: `corpus_reader` and `corpus_script` read it; r19 readers retire as r18's did.
- **FR-3 The spoken guard.** `instructions/spoken.py` reads the two new items' `spoken` and the Price labels: no S1-S8
  fault on the regenerated record; the eval founders' walks read the chips back as served.
- **FR-4 The after-answers leg (109/117).** `evals/backtest.py` reads `bar-strip` (`data-side` cells, the marker's
  label) on every card, the served `ruleLine`, `countLine` and `soLine`, `statusWord` as the verdict, the stage's served
  tally line, and on Insights the box header (belief, status word, status line) and `countLine`; the reader's screens
  carry them so section B reads what the page says. The DRY compare (`evals/corpus_scenario.py:4843`) reads the new
  lines through `brief_facts.py`.
- **FR-4b The problem and solution cards (keel-cloud 184).** Mirrors for the seven cards' words (the belief from the
  gate / question clause, the Importance caption and both questions, the Current solution sentence, Compatibility's
  served labels, Adoption friction's plain conditional label, the new footer sentence, the Insights headings); the
  Adoption friction and Compatibility corpus answers follow the option labels of revision 20; the leg reads the
  Prevalence people-axis strip and the Current solution line.
- **FR-4c The question screens (keel-cloud 185, keel-web 156; the founder's decisions of 2026-10-31).** (a) **The reader
  sees the spoken form.** On every respondent item screen the reader's `{{screen}}` carries the served `spoken` (anchor,
  stem, count line, options line, escape line, and Price's two second-step lines), so R6 is scored on what the voice
  says, not on the written list (cycle 4: Price's R6 was judged from the six written rungs while the code served a
  four-option first step; the gate's *Yes or no.* was reported unread). (b) **Price in two steps.** The eval
  respondents answer the ladder on the AI link as the voice asks it: step one, then the side's two bands; the corpus
  entries' Price answers are read through the two steps; the harness's spoken mirror (`instructions/spoken.py`) reads
  the second-step lines and the amount-only labels (*to under* / *or more*). (c) **Compatibility's three** on a fact:
  the readers and the corpus answer three where three are served; the mirrors read the ability scale's *most of the
  time*. (d) **The idea card.** The walk types the project name as the name and accepts Keel's plain words for *what it
  is*; the mirrors read the composed line *Imagine {name}, {what}.* (e) **The screener.** The mirrors read the writer's
  decider clause (no *you decide for*); the Palus condition's one-sentence test; *any* on a set. (f) **The interviewer
  screens.** Mirrors for the lock and send screens' sentences (156 FR-1, FR-2) and the format's new name *Read and tap*
  wherever the harness reads it (the send dialog, the Sent list, the link's choice screen). Corpus revision 20 with
  FR-2.
- **FR-4d One scripted line per follow-up.** keel-cloud 180's builder found (tasks.md, not foreseen 3) that the
  AirCaps walk typed the same scripted why into both of a person's two follow-ups (spec 142 allows two), which the
  cycle read as a quote filed twice. The walk answers each follow-up with its own line from the corpus entry (the
  entry carries one why per rung asked); a test that no person's two follow-ups receive the same text.
- **FR-5 The quality readers.** `quality/readers/*.md` for section B are unchanged in criteria; the stage/dimension
  screen descriptions name the strip and the lines so the reader scores them, not their absence.
- **FR-6 Tests.** Each moved mirror pinned with why; the two items answered on a fixture study; the leg's reader on
  a fixture page with and without `bar-strip`; `make unit` ZERO failed.

## Acceptance

`make unit` ZERO failed against keel-cloud 180-185 and keel-web 155-156 merged; a `make backtest ENTRY=08-fresco
SCOPE=COMMERCIAL` on the local stack reaches its end (paid: the coordinator runs it on the founder's word, inside
cycle 5). `tests/fixtures/sample/s006-reads.json` is re-recorded by `make sample` (the coordinator's step) rather than
hand-edited.
