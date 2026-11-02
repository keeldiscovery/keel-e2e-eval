# Spec 128 -- The confirmed context is read as spelt

Cycle 8 (2026-11-02 00:09-01:36 ET, the fourteen on keel-cloud `1ce203f`, typos on): 0 of 42 walks reached their end.
Every one stopped at the step *the context is confirmed on the wire: the four fields ...* (`evals/corpus_scenario.py`,
the loop `for key, value in founder.context_fields.items(): assert fields.get(key) == value`), because keel-cloud spec
196 (the founder's typos stop at the context card, merged 2026-11-01 23:35 ET) now serves `GET context`'s `fields`
**respelled**: the model lists the founder's misspelt words with their dictionary spelling, and code respells every
copy of the typed text through that list, the served fields among them, so the persona screen and the Current solution
question (which keel-web builds from those fields) read *record*, not *rcord*. The harness held the fields to the typed
text letter for letter, which was right before 196 and is wrong after it: a corrected typo is the fix working, not a
fault. The partial record and its 42 score files were not kept (the stop was the harness's, and the scores were of two
screens each). Builds on 125 (the `Spelling.sameWord` mirror, `harness/vectors_script.same_words`) and 126.

## Rules

- **FR-1 Held as spelt.** Wherever the harness holds a served text to a typed context field -- the four fields and the
  occasion on the confirmed `GET context` (`fields`), the form that Edit brings back filled (`edited.fields`, the
  re-opened step), and any other place the builder finds that compares a served string to `founder.context_fields` or
  the entry's typed fields letter for letter -- the comparison is word by word through 125's mirror of
  `Spelling.sameWord`: the same word count, each served word equal to the typed word or within 125's edit allowance of
  it (one edit at four letters, two from five, none under four or with a digit, the first letter the same). A served
  word that is a *different* word is still a fault, as before; a dropped or added word is still a fault.
- **FR-2 What is recorded.** The step's `record_assert` keeps the typed fields as the want and the served fields as
  the seen (as today), and adds `respelled`: the list of `{field, typed, served}` pairs where the two differ, so the
  bundle shows which typos the cloud corrected. `typist.leaks` (126 FR-3) is unchanged: a typed word served letter for
  letter is still a leak.
- **FR-3 Typos off.** With `--typos off` nothing the founder typed is misspelt, so the comparison is exact in effect;
  no test of record changes its meaning. The corpus scenarios (01-07) and the remote journeys hold as they are.
- **FR-4 Tests.** `make unit` green: a served field with one corrected typo passes; with a swapped word fails; with a
  dropped word fails; with no typos the exact text passes; the `respelled` list carries the corrected pair.

## Acceptance

`make unit` green on master after 127. Then cycle 8 is walked again on `1ce203f` (the fourteen, typos on): every walk
passes the context step, and the record's *typo leaks* line is read against cycle 7's 47.
