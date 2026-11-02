# Plan 128 -- The confirmed context is read as spelt

Branch `spec-128` (worktree `wt/keel-e2e-eval-128`), on master `8ee0bb1` (the spec's commit). No stack, no model, no
paid call, no key read.

## Where the letter-for-letter holds live

The sweep of `evals/`, `harness/`, `quality/` and `instructions/` for a served string held to `founder.context_fields`
(or the typed seeds) found three places, all in `evals/corpus_scenario.py`:

1. `leg_context`'s step *the context is confirmed on the wire*: `for key, value in founder.context_fields.items():
   assert fields.get(key) == value` -- cycle 8's stop.
2. The same step: the confirmed `fields.occasion` against the card's occasion field (served by 196 from the respelled
   text; held the same way so a corrected word in the noun is not a fault).
3. `context_reopened`: `edited.get("fields") == founder.context_fields` -- Edit's form is filled from the served fields.

The seeds (`problem_seed`, `solution_seed`) are sent, never held letter for letter against a served text; the strict
read-backs (`vs.read_back`, `card_condition`, `segment_of`) are the entry's own words on golden walks, which type no
typo. `typist.leaks` (126 FR-3) is untouched.

## The change

1. **Held as spelt** (FR-1). `harness/typist.py` gains `as_spelt(typed, served)`: both texts split into words and the
   runs between them (`instructions.spelling`'s word split), the same count, every run between words the same (spaces
   collapsed), every served word equal to the typed word or `spelling.same_word` it; a value that is not text is held
   exactly. `spelt_faults(typed_fields, served_fields, whole=False)` names each field that is not (`whole`: the key sets
   equal too, as the dict compare held).
2. **What is recorded** (FR-2). `respelled(typed_fields, served_fields)`: `{field, typed, served}` for each word the
   cloud spelt otherwise. The confirmed step's `record_assert` keeps the typed fields as the want, records the view as the
   seen with `respelled` beside it; `j.changed["context_wire"]["respelled"]` carries it into the bundle.
3. **Typos off** (FR-3). Equal texts are `as_spelt`; no test of record re-pinned.
4. **Tests** (FR-4). `tests/test_spelt_context_128.py`.
