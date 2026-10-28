# The baseline

Cut 2026-10-25 on the founder's word (spec 078 FR-6). Every later run is compared with it by `make read-table BASELINE=1`; a new baseline is cut only on his word, and this file is then kept under `quality/baselines/<date>.md`.

- RUBRIC_VERSION 1; overall score_pct 100.0%, flagged 0.0%
- studies (entry · scope): 08-fresco · PROBLEM
- score files: 20261025-PROBLEM-r1-0000aaa-v13-claude-opus-5-5.json
- cloud sha(s): 0000aaa; routing version(s): 13
- reader(s): claude-opus-5-5 (medium)

| row | R1 / G1 | R2 / G2 | R3 | R4 | R5 | weak |
|---|---|---|---|---|---|---|
| PROBLEM · founder · problem.importance · q | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 |  |
| PROBLEM · respondent · problem.importance · item | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 |  |
| PROBLEM · respondent · problem.prevalence · gate | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 |  |

<!-- baseline:data -->
```json
{
 "cut": "2026-10-25",
 "rubric_version": 1,
 "score_pct": 100.0,
 "flagged_pct": 0.0,
 "files": [
  "20261025-PROBLEM-r1-0000aaa-v13-claude-opus-5-5.json"
 ],
 "studies": [
  "08-fresco · PROBLEM"
 ],
 "cloud_shas": [
  "0000aaa"
 ],
 "routing_versions": [
  "13"
 ],
 "readers": [
  "claude-opus-5-5 (medium)"
 ],
 "rows": {
  "PROBLEM · founder · problem.importance · q": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0
   },
   "weak": false
  },
  "PROBLEM · respondent · problem.importance · item": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0
   },
   "weak": false
  },
  "PROBLEM · respondent · problem.prevalence · gate": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0
   },
   "weak": false
  }
 }
}
```
