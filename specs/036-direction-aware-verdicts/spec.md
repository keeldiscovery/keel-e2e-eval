# Spec 036 -- direction-aware verdicts (marks v15)

Sibling of keel-cloud 082 (merged at 438807d; registry VERSION 2; contract stays 9; document stays 16).

- FR-001 Corpus revision 8 only; an r7 file is refused by name as v13's / v14's. Drift may be `stronger` / `short`;
  a vector verdict may be `NOT_TESTED` (never a dimension status). 28 rows moved; people and picks unchanged.
- FR-002 The registry is read as exported at version 2 (`registry_version` passed through to `compare`; the engine refuses 1).
- FR-003 The BRIEF facts carry `decision.split` (NOT_YET with PROBLEM at PEOPLE_DISAGREE) and `decision.notTested`
  (vectors at NOT_TESTED -> KEEP_INTERVIEWING). `BriefReading.check` did not change: the five reading marks are untouched.
- FR-004 MARKS_VERSION 14 -> 15, because the corpus the ruler expects moved (compare_correctness) and the facts changed.
  Call 74. No threshold in `marks.toml` moved.
- FR-005 `rescore.py` refuses every bundle below 15.
- SC `make unit` green with the same skip set (75); `DRY=1` compare against 438807d 108 of 108. No live call; no run of record.
