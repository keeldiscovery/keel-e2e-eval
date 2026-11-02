# The baseline

Cut 2026-11-02 on the founder's word (spec 078 FR-6). Every later run is compared with it by `make read-table BASELINE=1`; a new baseline is cut only on his word, and this file is then kept under `quality/baselines/<date>.md`.

- RUBRIC_VERSION 3; overall score_pct 84.8%, flagged 5.1%
- studies (entry · scope): 14-code-four · COMMERCIAL, 14-code-four · PROBLEM, 14-code-four · SOLUTION
- score files: 20261102-COMMERCIAL-r3-1ce203f-v16-claude-opus-5-2.json, 20261102-PROBLEM-r3-1ce203f-v16-claude-opus-5-5.json, 20261102-SOLUTION-r3-1ce203f-v16-claude-opus-5-2.json
- cloud sha(s): 1ce203fe; routing version(s): 16
- reader(s): claude-opus-5-5 (medium)

| row | R1 / G1 / B1 | R2 / G2 / B2 | R3 / B3 | R4 / B4 | R5 / B5 | R6 / B6 | weak |
|---|---|---|---|---|---|---|---|
| COMMERCIAL · founder · - · context | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| COMMERCIAL · founder · - · context-card | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| COMMERCIAL · founder · - · idea | 2.00 | 1.00 | 2.00 | – | 1.00 | – | yes |
| COMMERCIAL · founder · - · insights-screen | 2.00 | – | 2.00 | 0.00 | 1.00 | 2.00 | yes |
| COMMERCIAL · founder · - · market | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| COMMERCIAL · founder · - · name | 2.00 | 2.00 | 2.00 | – | 2.00 | – |  |
| COMMERCIAL · founder · - · persona | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| COMMERCIAL · founder · - · persona-who-answers | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| COMMERCIAL · founder · - · problem-card | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| COMMERCIAL · founder · - · problem-seed | 2.00 | 2.00 | 2.00 | – | 1.00 | – | yes |
| COMMERCIAL · founder · - · ready-interviewer | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | – | yes |
| COMMERCIAL · founder · - · ready-pilot | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | – | yes |
| COMMERCIAL · founder · - · send-format | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| COMMERCIAL · founder · - · send-who | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| COMMERCIAL · founder · - · solution-card | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| COMMERCIAL · founder · - · solution-seed | 2.00 | 2.00 | 2.00 | – | 2.00 | – |  |
| COMMERCIAL · founder · - · stage | 2.00 | 1.00 | 2.00 | 0.00 | 1.00 | – | yes |
| COMMERCIAL · founder · commercial.ability_to_pay · dimension | 2.00 | 2.00 | 2.00 | 1.00 | 1.00 | – | yes |
| COMMERCIAL · founder · commercial.buyer_payer_alignment · answer | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | – | yes |
| COMMERCIAL · founder · commercial.buyer_payer_alignment · check | 2.00 | 2.00 | 2.00 | 1.00 | 1.00 | – | yes |
| COMMERCIAL · founder · commercial.buyer_payer_alignment · choose | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | – | yes |
| COMMERCIAL · founder · commercial.buyer_payer_alignment · dimension | 1.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| COMMERCIAL · founder · commercial.commitment · answer | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | – | yes |
| COMMERCIAL · founder · commercial.commitment · check | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | – | yes |
| COMMERCIAL · founder · commercial.commitment · dimension | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| COMMERCIAL · founder · commercial.existing_sacrifice · dimension | 1.00 | 2.00 | 2.00 | 1.00 | 1.00 | – | yes |
| COMMERCIAL · founder · commercial.existing_sacrifice · q | 2.00 | 1.00 | 2.00 | 1.00 | 1.00 | – | yes |
| COMMERCIAL · founder · commercial.price · dimension | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| COMMERCIAL · founder · commercial.price · q | 2.00 | 1.00 | 2.00 | 0.00 | 2.00 | – | yes |
| COMMERCIAL · founder · commercial.purchase_friction · answer | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | – | yes |
| COMMERCIAL · founder · commercial.purchase_friction · check | 2.00 | 1.00 | 2.00 | 1.00 | 2.00 | – | yes |
| COMMERCIAL · founder · commercial.purchase_friction · choose | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| COMMERCIAL · founder · commercial.purchase_friction · dimension | 2.00 | 1.00 | 2.00 | 1.00 | 1.00 | – | yes |
| COMMERCIAL · respondent · - · idea | 2.00 | 1.00 | 2.00 | – | 1.00 | 1.00 | yes |
| COMMERCIAL · respondent · commercial.ability_to_pay · item | 2.00 | 1.00 | 2.00 | 1.00 | 2.00 | 1.00 | yes |
| COMMERCIAL · respondent · commercial.commitment · item | 2.00 | 2.00 | 2.00 | 1.00 | 1.00 | 2.00 | yes |
| COMMERCIAL · respondent · commercial.existing_sacrifice · item | 2.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | yes |
| COMMERCIAL · respondent · commercial.price · item | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | 1.00 | yes |
| COMMERCIAL · respondent · commercial.purchase_friction · item | 2.00 | 1.00 | 2.00 | 1.00 | 1.00 | 1.00 | yes |
| PROBLEM · founder · - · context | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| PROBLEM · founder · - · context-card | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| PROBLEM · founder · - · context-window | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | – | yes |
| PROBLEM · founder · - · insights-screen | 2.00 | – | 2.00 | 0.00 | 2.00 | 2.00 | yes |
| PROBLEM · founder · - · market | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| PROBLEM · founder · - · name | 2.00 | 2.00 | 2.00 | – | 2.00 | – |  |
| PROBLEM · founder · - · problem-card | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | – | yes |
| PROBLEM · founder · - · problem-seed | 2.00 | 2.00 | 2.00 | – | 1.00 | – | yes |
| PROBLEM · founder · - · ready-interviewer | 2.00 | 1.00 | 2.00 | 1.00 | 2.00 | – | yes |
| PROBLEM · founder · - · send-format | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | – | yes |
| PROBLEM · founder · - · send-who | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| PROBLEM · founder · - · stage | 1.00 | 1.00 | 2.00 | 1.00 | 1.00 | – | yes |
| PROBLEM · founder · problem.current_solution_satisfaction · answer | 2.00 | 2.00 | 2.00 | 1.00 | 1.00 | – | yes |
| PROBLEM · founder · problem.current_solution_satisfaction · check | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | – | yes |
| PROBLEM · founder · problem.current_solution_satisfaction · dimension | 2.00 | 1.00 | 2.00 | 1.00 | 2.00 | – | yes |
| PROBLEM · founder · problem.frequency · dimension | 2.00 | 1.00 | 1.00 | 1.00 | 1.00 | – | yes |
| PROBLEM · founder · problem.frequency · q | 2.00 | 1.00 | 2.00 | 2.00 | 1.00 | – | yes |
| PROBLEM · founder · problem.importance · answer | 2.00 | 1.00 | 2.00 | 2.00 | 1.00 | – | yes |
| PROBLEM · founder · problem.importance · check | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| PROBLEM · founder · problem.importance · dimension | 2.00 | 1.00 | 2.00 | 1.00 | 1.00 | – | yes |
| PROBLEM · founder · problem.prevalence · dimension | 2.00 | 2.00 | 1.00 | 1.00 | 2.00 | – | yes |
| PROBLEM · founder · problem.prevalence · q | 2.00 | 1.00 | 1.00 | 1.00 | 1.00 | – | yes |
| PROBLEM · respondent · - · screener | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | 2.00 | yes |
| PROBLEM · respondent · problem.current_solution_satisfaction · item | 2.00 | 1.00 | 2.00 | 1.00 | 1.00 | 1.00 | yes |
| PROBLEM · respondent · problem.frequency · item | 2.00 | 1.00 | 1.00 | 1.00 | 2.00 | 2.00 | yes |
| PROBLEM · respondent · problem.importance · item | 2.00 | 2.00 | 2.00 | 1.00 | 1.00 | 2.00 | yes |
| PROBLEM · respondent · problem.prevalence · gate | 2.00 | 1.00 | 2.00 | 1.00 | 1.00 | 2.00 | yes |
| SOLUTION · founder · - · context | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| SOLUTION · founder · - · context-card | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| SOLUTION · founder · - · context-window | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | – | yes |
| SOLUTION · founder · - · idea | 2.00 | 1.00 | 2.00 | – | 1.00 | – | yes |
| SOLUTION · founder · - · insights-screen | 2.00 | – | 2.00 | 1.00 | 2.00 | 2.00 | yes |
| SOLUTION · founder · - · market | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| SOLUTION · founder · - · name | 2.00 | 2.00 | 2.00 | – | 2.00 | – |  |
| SOLUTION · founder · - · problem-card | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | – | yes |
| SOLUTION · founder · - · problem-seed | 2.00 | 2.00 | 2.00 | – | 1.00 | – | yes |
| SOLUTION · founder · - · ready-interviewer | 2.00 | 1.00 | 2.00 | 1.00 | 2.00 | – | yes |
| SOLUTION · founder · - · ready-pilot | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| SOLUTION · founder · - · send-format | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| SOLUTION · founder · - · send-who | 2.00 | 2.00 | 1.00 | 2.00 | 2.00 | – | yes |
| SOLUTION · founder · - · solution-card | 2.00 | 1.00 | 2.00 | – | 2.00 | – | yes |
| SOLUTION · founder · - · solution-seed | 2.00 | 1.00 | 2.00 | – | 1.00 | – | yes |
| SOLUTION · founder · - · stage | 2.00 | 1.00 | 2.00 | 0.00 | 2.00 | – | yes |
| SOLUTION · founder · solution.adoption_friction · answer | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | – | yes |
| SOLUTION · founder · solution.adoption_friction · check | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| SOLUTION · founder · solution.adoption_friction · choose | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | – | yes |
| SOLUTION · founder · solution.adoption_friction · dimension | 2.00 | 1.00 | 2.00 | 1.00 | 1.00 | – | yes |
| SOLUTION · founder · solution.compatibility · answer | 2.00 | 1.00 | 2.00 | 2.00 | 2.00 | – | yes |
| SOLUTION · founder · solution.compatibility · check | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| SOLUTION · founder · solution.compatibility · choose | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – |  |
| SOLUTION · founder · solution.compatibility · dimension | 2.00 | 1.00 | 2.00 | 1.00 | 2.00 | – | yes |
| SOLUTION · founder · solution.relative_advantage · answer | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | – | yes |
| SOLUTION · founder · solution.relative_advantage · check | 2.00 | 2.00 | 2.00 | 1.00 | 1.00 | – | yes |
| SOLUTION · founder · solution.relative_advantage · dimension | 2.00 | 1.00 | 2.00 | 1.00 | 2.00 | – | yes |
| SOLUTION · respondent · - · reveal | 2.00 | 1.00 | 2.00 | – | 1.00 | 1.00 | yes |
| SOLUTION · respondent · - · screener | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | yes |
| SOLUTION · respondent · problem.prevalence · gate | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | 2.00 | yes |
| SOLUTION · respondent · solution.adoption_friction · item | 2.00 | 2.00 | 2.00 | 1.00 | 2.00 | 2.00 | yes |
| SOLUTION · respondent · solution.compatibility · item | 1.00 | 1.00 | 2.00 | 1.00 | 1.00 | 1.00 | yes |
| SOLUTION · respondent · solution.relative_advantage · item | 2.00 | 1.00 | 1.00 | 2.00 | 1.00 | 2.00 | yes |
| COMMERCIAL · respondent · commercial.buyer_payer_alignment · insights | 2.00 | 2.00 | – | – | – | – |  |
| COMMERCIAL · respondent · commercial.price · insights | 2.00 | 2.00 | – | – | – | – |  |

<!-- baseline:data -->
```json
{
 "cut": "2026-11-02",
 "rubric_version": 3,
 "score_pct": 84.8,
 "flagged_pct": 5.1,
 "files": [
  "20261102-COMMERCIAL-r3-1ce203f-v16-claude-opus-5-2.json",
  "20261102-PROBLEM-r3-1ce203f-v16-claude-opus-5-5.json",
  "20261102-SOLUTION-r3-1ce203f-v16-claude-opus-5-2.json"
 ],
 "studies": [
  "14-code-four · COMMERCIAL",
  "14-code-four · PROBLEM",
  "14-code-four · SOLUTION"
 ],
 "cloud_shas": [
  "1ce203fe"
 ],
 "routing_versions": [
  "16"
 ],
 "readers": [
  "claude-opus-5-5 (medium)"
 ],
 "rows": {
  "COMMERCIAL · founder · - · context": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · - · context-card": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "COMMERCIAL · founder · - · idea": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": null,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · - · insights-screen": {
   "means": {
    "b1": 2.0,
    "b2": null,
    "b3": 2.0,
    "b4": 0.0,
    "b5": 1.0,
    "b6": 2.0
   },
   "weak": true
  },
  "COMMERCIAL · founder · - · market": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "COMMERCIAL · founder · - · name": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": null,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "COMMERCIAL · founder · - · persona": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "COMMERCIAL · founder · - · persona-who-answers": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · - · problem-card": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "COMMERCIAL · founder · - · problem-seed": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": null,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · - · ready-interviewer": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · - · ready-pilot": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · - · send-format": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "COMMERCIAL · founder · - · send-who": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · - · solution-card": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "COMMERCIAL · founder · - · solution-seed": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": null,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "COMMERCIAL · founder · - · stage": {
   "means": {
    "b1": 2.0,
    "b2": 1.0,
    "b3": 2.0,
    "b4": 0.0,
    "b5": 1.0,
    "b6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.ability_to_pay · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 2.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 1.0,
    "b6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.buyer_payer_alignment · answer": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.buyer_payer_alignment · check": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.buyer_payer_alignment · choose": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.buyer_payer_alignment · dimension": {
   "means": {
    "b1": 1.0,
    "b2": 2.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 2.0,
    "b6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.commitment · answer": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.commitment · check": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.commitment · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 2.0,
    "b3": 2.0,
    "b4": 2.0,
    "b5": 2.0,
    "b6": null
   },
   "weak": false
  },
  "COMMERCIAL · founder · commercial.existing_sacrifice · dimension": {
   "means": {
    "b1": 1.0,
    "b2": 2.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 1.0,
    "b6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.existing_sacrifice · q": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.price · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 2.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 2.0,
    "b6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.price · q": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 0.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.purchase_friction · answer": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.purchase_friction · check": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.purchase_friction · choose": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "COMMERCIAL · founder · commercial.purchase_friction · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 1.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 1.0,
    "b6": null
   },
   "weak": true
  },
  "COMMERCIAL · respondent · - · idea": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": null,
    "r5": 1.0,
    "r6": 1.0
   },
   "weak": true
  },
  "COMMERCIAL · respondent · commercial.ability_to_pay · item": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": 1.0
   },
   "weak": true
  },
  "COMMERCIAL · respondent · commercial.commitment · item": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": 2.0
   },
   "weak": true
  },
  "COMMERCIAL · respondent · commercial.existing_sacrifice · item": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 1.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": 1.0
   },
   "weak": true
  },
  "COMMERCIAL · respondent · commercial.price · item": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": 1.0
   },
   "weak": true
  },
  "COMMERCIAL · respondent · commercial.purchase_friction · item": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": 1.0
   },
   "weak": true
  },
  "PROBLEM · founder · - · context": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "PROBLEM · founder · - · context-card": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "PROBLEM · founder · - · context-window": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · - · insights-screen": {
   "means": {
    "b1": 2.0,
    "b2": null,
    "b3": 2.0,
    "b4": 0.0,
    "b5": 2.0,
    "b6": 2.0
   },
   "weak": true
  },
  "PROBLEM · founder · - · market": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · - · name": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": null,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "PROBLEM · founder · - · problem-card": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · - · problem-seed": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": null,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · - · ready-interviewer": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · - · send-format": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · - · send-who": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "PROBLEM · founder · - · stage": {
   "means": {
    "b1": 1.0,
    "b2": 1.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 1.0,
    "b6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.current_solution_satisfaction · answer": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.current_solution_satisfaction · check": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.current_solution_satisfaction · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 1.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 2.0,
    "b6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.frequency · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 1.0,
    "b3": 1.0,
    "b4": 1.0,
    "b5": 1.0,
    "b6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.frequency · q": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.importance · answer": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.importance · check": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.importance · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 1.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 1.0,
    "b6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.prevalence · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 2.0,
    "b3": 1.0,
    "b4": 1.0,
    "b5": 2.0,
    "b6": null
   },
   "weak": true
  },
  "PROBLEM · founder · problem.prevalence · q": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 1.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "PROBLEM · respondent · - · screener": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": 2.0
   },
   "weak": true
  },
  "PROBLEM · respondent · problem.current_solution_satisfaction · item": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": 1.0
   },
   "weak": true
  },
  "PROBLEM · respondent · problem.frequency · item": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 1.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": 2.0
   },
   "weak": true
  },
  "PROBLEM · respondent · problem.importance · item": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": 2.0
   },
   "weak": true
  },
  "PROBLEM · respondent · problem.prevalence · gate": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": 2.0
   },
   "weak": true
  },
  "SOLUTION · founder · - · context": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "SOLUTION · founder · - · context-card": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "SOLUTION · founder · - · context-window": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · - · idea": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": null,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · - · insights-screen": {
   "means": {
    "b1": 2.0,
    "b2": null,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 2.0,
    "b6": 2.0
   },
   "weak": true
  },
  "SOLUTION · founder · - · market": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "SOLUTION · founder · - · name": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": null,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "SOLUTION · founder · - · problem-card": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · - · problem-seed": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": null,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · - · ready-interviewer": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · - · ready-pilot": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "SOLUTION · founder · - · send-format": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "SOLUTION · founder · - · send-who": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 1.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · - · solution-card": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": null,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · - · solution-seed": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": null,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · - · stage": {
   "means": {
    "b1": 2.0,
    "b2": 1.0,
    "b3": 2.0,
    "b4": 0.0,
    "b5": 2.0,
    "b6": null
   },
   "weak": true
  },
  "SOLUTION · founder · solution.adoption_friction · answer": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · solution.adoption_friction · check": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · solution.adoption_friction · choose": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · solution.adoption_friction · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 1.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 1.0,
    "b6": null
   },
   "weak": true
  },
  "SOLUTION · founder · solution.compatibility · answer": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · solution.compatibility · check": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "SOLUTION · founder · solution.compatibility · choose": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": null
   },
   "weak": false
  },
  "SOLUTION · founder · solution.compatibility · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 1.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 2.0,
    "b6": null
   },
   "weak": true
  },
  "SOLUTION · founder · solution.relative_advantage · answer": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · solution.relative_advantage · check": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": null
   },
   "weak": true
  },
  "SOLUTION · founder · solution.relative_advantage · dimension": {
   "means": {
    "b1": 2.0,
    "b2": 1.0,
    "b3": 2.0,
    "b4": 1.0,
    "b5": 2.0,
    "b6": null
   },
   "weak": true
  },
  "SOLUTION · respondent · - · reveal": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": null,
    "r5": 1.0,
    "r6": 1.0
   },
   "weak": true
  },
  "SOLUTION · respondent · - · screener": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 2.0,
    "r5": 2.0,
    "r6": 1.0
   },
   "weak": true
  },
  "SOLUTION · respondent · problem.prevalence · gate": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": 2.0
   },
   "weak": true
  },
  "SOLUTION · respondent · solution.adoption_friction · item": {
   "means": {
    "r1": 2.0,
    "r2": 2.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 2.0,
    "r6": 2.0
   },
   "weak": true
  },
  "SOLUTION · respondent · solution.compatibility · item": {
   "means": {
    "r1": 1.0,
    "r2": 1.0,
    "r3": 2.0,
    "r4": 1.0,
    "r5": 1.0,
    "r6": 1.0
   },
   "weak": true
  },
  "SOLUTION · respondent · solution.relative_advantage · item": {
   "means": {
    "r1": 2.0,
    "r2": 1.0,
    "r3": 1.0,
    "r4": 2.0,
    "r5": 1.0,
    "r6": 2.0
   },
   "weak": true
  },
  "COMMERCIAL · respondent · commercial.buyer_payer_alignment · insights": {
   "means": {
    "g1": 2.0,
    "g2": 2.0
   },
   "weak": false
  },
  "COMMERCIAL · respondent · commercial.price · insights": {
   "means": {
    "g1": 2.0,
    "g2": 2.0
   },
   "weak": false
  }
 }
}
```
