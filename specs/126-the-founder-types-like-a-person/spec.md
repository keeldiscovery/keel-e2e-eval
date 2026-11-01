# Spec 126 -- The founder types like a person (typos on the quality walk, and the leak check)

The founder, 2026-11-01: *"A normal human being will have a lot of errors, especially typos, when they write their
problem statement ... sometimes the questions generated out of it do have those typos. If the person introduces typos
while they are writing the problem statement, it should not percolate to the respondent's question. When you run the
cycle, ensure the agent emulates a human by making small typos in their statements."* keel-cloud 195 (*spelling
corrected, words kept*) is the product's answer; this spec makes the quality cycle test it on every entry, every cycle.
Builds on 125.

- **FR-1 The typist.** New `harness/typist.py`: `typos(text, seed) -> (typed, list[Typo])` where `Typo = (meant, typed,
  kind)`. Deterministic from `seed` (the entry id and the field name), so a cycle is reproducible. One typo about every
  twelve words and at least one in any field of four words or more. Kinds, as people make them: an adjacent
  transposition (*the* -> *teh*, *every* -> *evrey*), a dropped letter (*without* -> *withot*, *errors* -> *erros*), a
  doubled letter (*running* -> *runnning*), the ie/ei swap where it applies (*receive* -> *recieve*). Rules: only
  lower-case dictionary words of five letters or more with no digit; **never the first letter** (keel-cloud 195's
  guard); one edit per word; never a capitalised word, a word with a digit, a currency or unit, a word in the entry's
  idea name or offer name, or a word the entry's `product_words` / brand list names (those stand as typed by design). The
  typed text keeps its punctuation and spacing.
- **FR-2 Where the founder types.** On `make quality-walk` only (never `backtest`, `gallery` or the journeys, whose
  golden texts must match), `FounderInputs` is typed through the typist: `problem_seed`, `solution_seed` and the four
  `context_fields` (actor, job, circumstance, segment). The project name, idea name, decider title, calibration answers
  and the window are typed as recorded. `TYPOS=0` turns it off (`--typos off`); `DRY=1` prints every field as it will be
  typed with its typos marked. The cycle head says `typos: N typed on M fields` and the score file carries
  `typos: [{field, meant, typed, kind}]` per entry.
- **FR-3 The leak check** (deterministic; no reader changes). Every served text the walk already reads -- the context
  card, the problem statement and its mechanism line, the three studies' respondent questions (text and the AI
  interviewer's clips' words and passages), the chips and screeners, the brief's and the stage pages' lines -- is
  searched for each `typed` word as a whole word, case-insensitively. A hit is a **typo leak**: `{screen, field, meant,
  typed, text}`, written to the score file's `typo_leaks` and to the cycle record as a defect line under the entry
  (*typo leak: "withot" (meant "without") reached the PROBLEM question "How do you run payroll withot errors?"*), and
  counted in the cycle head (`K leaked`). Where the `meant` word's stem appears in a served question it must be spelt
  right; a served text that corrects the word is the expected outcome and is not reported. The walk never stops on a
  leak and never retypes: the leak is the finding. A typo that lands in a name or a number is a typist fault, not a
  leak, and the typist's tests forbid it.
- **FR-4** The founder-reader is still handed the entry's `.sources.md` as recorded (it judges the served words against
  the founder's meaning, not his spelling). The respondent-reader unchanged. `RUBRIC_VERSION` unchanged.
- **FR-5** `make unit` green (`set -o pipefail`); `tests/test_typist_126.py` (determinism, the kinds, the rules, the
  marked DRY line) and the leak check on a recorded walk.

## Acceptance

`make unit` ZERO failed. Cycle 7 on the five catalog entries runs with typos on by default: the record names every
typo typed and every leak; a leak is a keel-cloud defect to fix (its instructions or a code check that carried the
founder's spelling), never a reason to retype.
