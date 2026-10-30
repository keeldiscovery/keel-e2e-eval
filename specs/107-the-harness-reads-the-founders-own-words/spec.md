# Spec 107 -- The harness treats the founder's own words as not jargon, as keel-cloud 175 does

keel-cloud 175 (merged 2026-10-30, cloud master `7e65b637`; its tasks.md lists every pin): the M5 plain-words check, the
J1 jargon notes and `ProblemSentence` exempt every word or phrase found whole, case-insensitively, in the founder's own
texts (the context's typed fields, the problem seed, the solution seed, `audience_words`); a word Keel introduced is
still checked and the breach names it (*… and not one the founder typed*). The project now stores the solution seed
(`ProjectDocument.SCHEMA_VERSION` 34; a card confirmed before 175 has none). The harness mirrors the old checks and will
disagree: 05-paidly's own seed says *A platform that …*, so GET idea no longer notes *platform* and the strict J1 check
fails on the golden journey.

## Rules

- **FR-1 The J1 mirror.** `harness/vectors_script.py` `expected_j1` (~:668-672) subtracts every word typed in the entry's
  statements and context fields (whole-word, case-insensitive, hyphen joins), so the golden journeys' strict J1 check
  (`evals/corpus_scenario.py:1520-1526`) expects what the cloud now serves; 05-paidly's *platform* the named case.
- **FR-2 The M5 mirror.** `instructions/corpus.py` `m5_faults` (~:1699-1720) and `plain_line` (~:1794-1830, the M5 loop)
  exempt founder-typed words the same way; `LOCK_PLAIN_WORDS` (~:1728-1746) keeps its rows but each fires only on a word
  the entry did not type (10-palus, 11-issen, 12-transload, 21-codyco, 14-code-four's rows are their own seeds' words;
  16-pairio's *CMMS* / *ERP* are not in its seed and stand). `evals/scope_marks.py` `sentence_faults` (~:83-92) the same.
- **FR-3 The breach text.** Where a test matches the breach message, the unchanged opening still matches; a test that
  expects a founder-typed word to be refused is re-pinned to a Keel-introduced word, with why.
- **FR-4 Fewer refusals are not a regression.** The walk's `lock_refused` findings drop; the judge's reading and the
  quality record say nothing new. The document version pin (`interviewer_leg.py:780`, `>= 22`) stands.
- **FR-5 Tests.** `tests/test_founders_own_words_107.py`: `expected_j1` on 05-paidly's seed; `m5_faults` on 10-palus's
  card in its own words (no fault) and on a card adding *API* (fault); `LOCK_PLAIN_WORDS` firing only on Keel's word;
  `sentence_faults`. `make unit` ZERO failed (master's counts as 104's tasks.md records them).

## Acceptance

`make unit` ZERO failed; then, on the local stack, `make eval K=s005` (05-paidly's golden journey) green -- the
coordinator runs it (it brings the stack up; the founders on it are on fakes). Build after 105; one builder at a time
in this repo.
