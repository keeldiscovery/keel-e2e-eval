# Spec 111 -- The harness mirrors keel-cloud 176: M5's parenthesis, list and design-note rules yield to the seed

keel-cloud 176 (merged 2026-10-30; its tasks.md lists every pin): a parenthesis or list of names counts as the founder's
when every name in it is found whole in the founder's texts (split on commas and *or* / *and*); a design note counts as
the founder's when its phrase, read to the end of its clause, was typed; a parenthesis of two or more names is spoken as
*, such as A, B or C,*; a list of more than five names is spoken as the first two and *and others*; the written card
keeps the founder's punctuation; `ProblemSentence` yields the same way. The harness's M5 mirror (107) reads the
parenthesis and design-note rules on the line alone.

## Rules

- **FR-1 `instructions/corpus.py`:** `m5_faults`'s parenthesis rule (~:1742-1744) and design-note rule (~:1746-1748) take
  `founder_texts` and exempt the founder's; the *read the line alone (175 T003)* docstring goes; `plain_line` (~:1852-1859)
  keeps a parenthesis, list or note the founder typed; the comment at ~:1776-1779 goes; 16-pairio's three list rows
  fire only on a list Keel introduced (its CMMS / ERP rows stand).
- **FR-2 Tests re-pinned with why:** `tests/test_founders_own_words_107.py:97-104` (Codyco's texts: faults become
  `["design note"]` only -- or none, if the note's clause is typed; say which) and `:122-136` (Pairio loses its three
  list rows in `fires`).
- **FR-3 The spoken mirror:** where the harness composes the reveal aloud (`instructions/spoken.py` / the reveal's spoken
  form in `quality/readers.py`), a typed parenthesis is said *such as …* and a long list *and others*, as the cloud does.
- **FR-4 Fewer `lock_refused` findings** on Codyco's parenthesis and Pairio's list are the spec working.
- **FR-5 Tests:** `tests/test_m5_other_rules_111.py`: Codyco's parenthesis as typed (no fault), a parenthesis with one
  Keel name (fault), Pairio's list as typed (no fault), a design note typed vs Keel's, the spoken *such as* and *and
  others*. `make unit` ZERO failed (master's counts as 110's tasks.md records them).

## Acceptance

`make unit` ZERO failed. Build after 110, before 097; one builder at a time in this repo.
