# Spec 037 -- reveal in three lines (marks v16)

Sibling of keel-cloud 084 (merged at fc12b49; inference CONTRACT_VERSION 9 -> 10; document 16 -> 17).

- FR-001 CONTEXT_INTERPRET results carry `occasion` (X1, X3); SOLUTION_MECHANISM results carry `idea_what`, `idea_how`,
  `idea_belief` (L1-L4, W3); RESPONDENT_QUESTIONS results carry no `reveal` (R6 gone). All validated by keel-cloud's
  `screenContracts validate`; this repo adds no copy of the rules.
- FR-002 The part-2 reveal W3 fault (`score_respondent`) and the report's reveal banner retire; a `reveal` that arrives is not read.
- FR-003 MARKS_VERSION 15 -> 16 (call 75), because a mark retired. No threshold moved; corpus stays r8.
- FR-004 `rescore.py` refuses every bundle below 16.
- SC `make unit` green, same skips; `DRY=1` against fc12b49 compare 108/108. No live call; no run of record.
