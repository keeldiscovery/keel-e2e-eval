# The question-quality table

Built by `make read-table` from `quality/scores/` (spec 078 FR-5) at RUBRIC_VERSION 2. Regenerated and committed with every score file; never edited by hand.

- **This cycle** (`quality/cycles/20261030-fcec453.md`, cloud fcec453, 15 studies): score_pct **84.9%**, flagged 4.4%
  - 8 of 15 walks reached their end; 7 stopped early (08-fresco · COMMERCIAL -- the cost step; 10-palus · SOLUTION -- the lock is answered, not a stop; 10-palus · COMMERCIAL -- founder edits the idea card's how, howDecider line after the lock was refused; 13-aircaps · COMMERCIAL -- Harriet Coleman answers the interview, screen by screen; 17-expanse · COMMERCIAL -- no step named (stopped outside a step); 21-codyco · SOLUTION -- the lock is answered, not a stop; 21-codyco · COMMERCIAL -- founder edits the idea card's how, howDecider line after the lock was refused); their scores are of the screens served before the stop
  - keel-cloud moved mid-cycle: fcec453 -> 9093d99 from 17-expanse · PROBLEM
  - keel-web moved mid-cycle: 78c012f -> ff55387 from 17-expanse · COMMERCIAL, then ff55387 -> eec5856 from 21-codyco · SOLUTION, then eec5856 -> f661542 from 21-codyco · COMMERCIAL
- **The baseline**: none cut yet (`make quality-accept` cuts it, on the founder's word)
- **The bar**: 90% -- this cycle is BELOW it

**Overall score_pct 84.9%** over the latest file of each of 15 studies (entry · scope) -- is BELOW the bar of **90%** the founder named before the remaining entries are walked.

- founder: score_pct 85.8%, flagged 4.4% of 272 screens
- respondent: score_pct 81.0%, spoken_pct 73.9%, insights_pct 95.3%, flagged 4.3% of 46 screens
- scope COMMERCIAL: score_pct 85.9%, flagged 7.9% of 101 screens
- scope PROBLEM: score_pct 83.4%, flagged 3.0% of 100 screens
- scope SOLUTION: score_pct 85.4%, flagged 2.6% of 117 screens
- studies: 08-fresco · COMMERCIAL (20261030-COMMERCIAL-r2-fcec453-v13-claude-opus-5-5.json), 08-fresco · PROBLEM (20261030-PROBLEM-r2-fcec453-v13-claude-opus-5-5.json), 08-fresco · SOLUTION (20261030-SOLUTION-r2-fcec453-v13-claude-opus-5-5.json), 10-palus · COMMERCIAL (20261030-COMMERCIAL-r2-fcec453-v13-claude-opus-5-5.json), 10-palus · PROBLEM (20261030-PROBLEM-r2-fcec453-v13-claude-opus-5-5.json), 10-palus · SOLUTION (20261030-SOLUTION-r2-fcec453-v13-claude-opus-5-5.json), 13-aircaps · COMMERCIAL (20261030-COMMERCIAL-r2-fcec453-v13-claude-opus-5-5.json), 13-aircaps · PROBLEM (20261030-PROBLEM-r2-fcec453-v13-claude-opus-5-5.json), 13-aircaps · SOLUTION (20261030-SOLUTION-r2-fcec453-v13-claude-opus-5-5.json), 17-expanse · COMMERCIAL (20261030-COMMERCIAL-r2-9093d99-v13-claude-opus-5-5.json), 17-expanse · PROBLEM (20261030-PROBLEM-r2-9093d99-v13-claude-opus-5-5.json), 17-expanse · SOLUTION (20261030-SOLUTION-r2-9093d99-v13-claude-opus-5-5.json), 21-codyco · COMMERCIAL (20261030-COMMERCIAL-r2-9093d99-v13-claude-opus-5-5.json), 21-codyco · PROBLEM (20261030-PROBLEM-r2-9093d99-v13-claude-opus-5-5.json), 21-codyco · SOLUTION (20261030-SOLUTION-r2-9093d99-v13-claude-opus-5-5.json)

## The rows

Weak = a 0 on one criterion in two or more entries, or a mean under 1.5 (RUBRIC.md). 57 of 78 rows are weak.

R6 (said aloud) is the respondent-reader's alone: a founder row shows –.

| | scope | audience | dimension | kind | n | R1 | R2 | R3 | R4 | R5 | R6 | 0s | entries with a 0 | fix |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **WEAK** | COMMERCIAL | founder | - | context | 5 | 2.00 | 1.60 | 2.00 | 2.00 | 1.40 | – | 0 |  | shared file: context-interpret.md, and code (ReadBack, Qualifiers) |
|  | COMMERCIAL | founder | - | context-card | 5 | 2.00 | 1.60 | 2.00 | 2.00 | 2.00 | – | 0 |  | shared file: context-interpret.md, and code (ReadBack, Qualifiers) |
| **WEAK** | COMMERCIAL | founder | - | idea | 5 | 2.00 | 1.60 | 2.00 | 1.00 | 1.00 | – | 0 |  | shared file: solution-mechanism.md |
|  | COMMERCIAL | founder | - | market | 5 | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
|  | COMMERCIAL | founder | - | name | 5 | 2.00 | 2.00 | 2.00 | – | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
|  | COMMERCIAL | founder | - | persona | 5 | 2.00 | 1.60 | 2.00 | 1.60 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
| **WEAK** | COMMERCIAL | founder | - | persona-who-answers | 5 | 2.00 | 1.80 | 2.00 | 1.20 | 1.60 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
| **WEAK** | COMMERCIAL | founder | - | problem-card | 5 | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 | – | 0 |  | shared file: problem-interpret.md |
| **WEAK** | COMMERCIAL | founder | - | problem-seed | 5 | 2.00 | 2.00 | 2.00 | – | 1.00 | – | 0 |  | shared file: problem-interpret.md |
| **WEAK** | COMMERCIAL | founder | - | ready-interviewer | 4 | 2.00 | 1.00 | 2.00 | 1.00 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | COMMERCIAL | founder | - | ready-pilot | 4 | 1.75 | 1.00 | 2.00 | 1.00 | 1.25 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
|  | COMMERCIAL | founder | - | send-who | 1 | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
| **WEAK** | COMMERCIAL | founder | - | solution-card | 5 | 2.00 | 1.80 | 2.00 | – | 1.00 | – | 0 |  | shared file: solution-mechanism.md |
| **WEAK** | COMMERCIAL | founder | - | solution-seed | 5 | 2.00 | 2.00 | 2.00 | – | 1.20 | – | 0 |  | shared file: solution-mechanism.md |
|  | COMMERCIAL | founder | commercial.buyer_payer_alignment | answer | 4 | 1.50 | 2.00 | 2.00 | 1.75 | 1.50 | – | 1 | 13-aircaps | registry row: commercial.buyer_payer_alignment's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | COMMERCIAL | founder | commercial.buyer_payer_alignment | check | 4 | 2.00 | 2.00 | 2.00 | 1.00 | 1.50 | – | 0 |  | registry row: commercial.buyer_payer_alignment's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | COMMERCIAL | founder | commercial.buyer_payer_alignment | choose | 4 | 1.25 | 1.25 | 2.00 | 1.00 | 2.00 | – | 1 | 21-codyco | registry row: commercial.buyer_payer_alignment's founder guidance (else founder-lists.md, shared: every dimension re-read); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | COMMERCIAL | founder | commercial.commitment | answer | 4 | 2.00 | 2.00 | 2.00 | 2.00 | 0.50 | – | 2 | 17-expanse, 21-codyco | registry row: commercial.commitment's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | COMMERCIAL | founder | commercial.commitment | check | 3 | 2.00 | 1.67 | 1.67 | – | 1.00 | – | 1 | 21-codyco | registry row: commercial.commitment's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | COMMERCIAL | founder | commercial.existing_sacrifice | q | 5 | 2.00 | 1.00 | 1.80 | 1.00 | 1.00 | – | 1 | 13-aircaps | registry row: commercial.existing_sacrifice's founder guidance (else founder-lists.md, shared: every dimension re-read); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | COMMERCIAL | founder | commercial.price | q | 4 | 2.00 | 1.75 | 2.00 | 0.50 | 1.25 | – | 2 | 13-aircaps, 21-codyco | registry row: commercial.price's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | COMMERCIAL | founder | commercial.purchase_friction | answer | 3 | 2.00 | 2.00 | 2.00 | 2.00 | 1.33 | – | 0 |  | registry row: commercial.purchase_friction's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | COMMERCIAL | founder | commercial.purchase_friction | check | 3 | 2.00 | 2.00 | 2.00 | 1.33 | 2.00 | – | 0 |  | registry row: commercial.purchase_friction's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | COMMERCIAL | founder | commercial.purchase_friction | choose | 3 | 2.00 | 1.67 | 2.00 | 1.00 | 1.33 | – | 0 |  | registry row: commercial.purchase_friction's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | PROBLEM | founder | - | context | 5 | 2.00 | 1.00 | 2.00 | 2.00 | 1.00 | – | 0 |  | shared file: context-interpret.md, and code (ReadBack, Qualifiers); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | PROBLEM | founder | - | context-card | 5 | 2.00 | 1.20 | 2.00 | 2.00 | 2.00 | – | 0 |  | shared file: context-interpret.md, and code (ReadBack, Qualifiers); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
|  | PROBLEM | founder | - | market | 5 | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
|  | PROBLEM | founder | - | name | 5 | 2.00 | 2.00 | 2.00 | – | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
| **WEAK** | PROBLEM | founder | - | problem-card | 5 | 2.00 | 2.00 | 2.00 | 2.00 | 1.20 | – | 0 |  | shared file: problem-interpret.md |
| **WEAK** | PROBLEM | founder | - | problem-seed | 5 | 2.00 | 2.00 | 2.00 | – | 1.00 | – | 0 |  | shared file: problem-interpret.md |
| **WEAK** | PROBLEM | founder | - | ready-interviewer | 5 | 2.00 | 1.00 | 2.00 | 1.00 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | PROBLEM | founder | - | send-format | 4 | 1.75 | 1.00 | 2.00 | 1.25 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
|  | PROBLEM | founder | - | send-who | 5 | 2.00 | 1.60 | 2.00 | 1.80 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
| **WEAK** | PROBLEM | founder | problem.current_solution_satisfaction | answer | 5 | 2.00 | 1.00 | 2.00 | 1.40 | 1.00 | – | 0 |  | registry row: problem.current_solution_satisfaction's founder guidance (else founder-lists.md, shared: every dimension re-read); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | PROBLEM | founder | problem.current_solution_satisfaction | check | 4 | 2.00 | 1.50 | 2.00 | 0.75 | 1.50 | – | 1 | 10-palus | registry row: problem.current_solution_satisfaction's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | PROBLEM | founder | problem.frequency | q | 5 | 1.80 | 1.20 | 1.40 | 2.00 | 2.00 | – | 0 |  | registry row: problem.frequency's founder guidance (else founder-lists.md, shared: every dimension re-read); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | PROBLEM | founder | problem.importance | answer | 5 | 2.00 | 1.20 | 2.00 | 1.80 | 1.60 | – | 0 |  | registry row: problem.importance's founder guidance (else founder-lists.md, shared: every dimension re-read); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | PROBLEM | founder | problem.importance | check | 5 | 2.00 | 1.20 | 2.00 | 1.00 | 2.00 | – | 0 |  | registry row: problem.importance's founder guidance (else founder-lists.md, shared: every dimension re-read); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | PROBLEM | founder | problem.prevalence | q | 5 | 2.00 | 1.60 | 1.20 | 2.00 | 1.20 | – | 0 |  | registry row: problem.prevalence's founder guidance (else founder-lists.md, shared: every dimension re-read) |
|  | PROBLEM | respondent | - | follow_up | 2 | 2.00 | 1.50 | 2.00 | – | 1.50 | 1.50 | 0 |  | registry row: the follow-up ladder (registry data; code writes the words) |
|  | PROBLEM | respondent | - | screener | 5 | 2.00 | 1.80 | 1.80 | 1.60 | 2.00 | 2.00 | 0 |  | shared file: respondent-questions.md (the story clause, the screener question) |
| **WEAK** | PROBLEM | respondent | problem.current_solution_satisfaction | item | 5 | 1.80 | 1.00 | 1.80 | 1.00 | 2.00 | 1.00 | 0 |  | registry row: problem.current_solution_satisfaction's respondent wording, else the code transform (no model); R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | PROBLEM | respondent | problem.frequency | item | 5 | 1.60 | 1.00 | 1.60 | 1.60 | 1.80 | 1.00 | 3 | 10-palus | registry row: problem.frequency's respondent wording, else the code transform (no model); R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | PROBLEM | respondent | problem.importance | item | 5 | 1.60 | 1.20 | 1.60 | 1.00 | 1.80 | 1.40 | 0 |  | registry row: problem.importance's respondent wording, else the code transform (no model); R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | PROBLEM | respondent | problem.prevalence | gate | 5 | 2.00 | 1.20 | 1.80 | 0.80 | 1.40 | 1.60 | 1 | 13-aircaps | shared file: respondent-questions.md (the story clause, the screener question); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | founder | - | context | 5 | 2.00 | 1.00 | 2.00 | 2.00 | 1.40 | – | 0 |  | shared file: context-interpret.md, and code (ReadBack, Qualifiers); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | founder | - | context-card | 5 | 2.00 | 1.00 | 2.00 | 2.00 | 1.80 | – | 0 |  | shared file: context-interpret.md, and code (ReadBack, Qualifiers); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | founder | - | idea | 5 | 2.00 | 1.40 | 2.00 | – | 1.00 | – | 0 |  | shared file: solution-mechanism.md; R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
|  | SOLUTION | founder | - | market | 5 | 2.00 | 2.00 | 1.80 | 2.00 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
|  | SOLUTION | founder | - | name | 5 | 2.00 | 2.00 | 2.00 | – | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
| **WEAK** | SOLUTION | founder | - | problem-card | 5 | 2.00 | 1.80 | 2.00 | 2.00 | 1.00 | – | 0 |  | shared file: problem-interpret.md |
| **WEAK** | SOLUTION | founder | - | problem-seed | 5 | 2.00 | 2.00 | 2.00 | – | 1.00 | – | 0 |  | shared file: problem-interpret.md |
| **WEAK** | SOLUTION | founder | - | ready-interviewer | 5 | 1.80 | 1.00 | 2.00 | 1.00 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | founder | - | ready-pilot | 5 | 2.00 | 1.60 | 2.00 | 1.00 | 1.40 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
| **WEAK** | SOLUTION | founder | - | send-format | 3 | 1.67 | 1.00 | 2.00 | 1.33 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
|  | SOLUTION | founder | - | send-who | 3 | 2.00 | 2.00 | 2.00 | 1.67 | 2.00 | – | 0 |  | no model: the page's own words (keel-web / keel-cloud code) |
| **WEAK** | SOLUTION | founder | - | solution-card | 5 | 2.00 | 1.80 | 2.00 | – | 1.00 | – | 0 |  | shared file: solution-mechanism.md |
| **WEAK** | SOLUTION | founder | - | solution-seed | 5 | 2.00 | 1.80 | 2.00 | – | 1.20 | – | 0 |  | shared file: solution-mechanism.md |
| **WEAK** | SOLUTION | founder | solution.adoption_friction | answer | 5 | 2.00 | 2.00 | 2.00 | 2.00 | 0.60 | – | 2 | 17-expanse, 21-codyco | registry row: solution.adoption_friction's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | SOLUTION | founder | solution.adoption_friction | check | 3 | 2.00 | 2.00 | 1.67 | 1.00 | 1.33 | – | 0 |  | registry row: solution.adoption_friction's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | SOLUTION | founder | solution.adoption_friction | choose | 5 | 2.00 | 1.80 | 1.40 | 1.40 | 1.00 | – | 1 | 17-expanse | registry row: solution.adoption_friction's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | SOLUTION | founder | solution.compatibility | answer | 5 | 2.00 | 1.60 | 2.00 | 2.00 | 1.00 | – | 0 |  | registry row: solution.compatibility's founder guidance (else founder-lists.md, shared: every dimension re-read) |
|  | SOLUTION | founder | solution.compatibility | check | 4 | 2.00 | 2.00 | 2.00 | 1.50 | 2.00 | – | 0 |  | registry row: solution.compatibility's founder guidance (else founder-lists.md, shared: every dimension re-read) |
| **WEAK** | SOLUTION | founder | solution.compatibility | choose | 5 | 2.00 | 1.40 | 2.00 | 1.60 | 1.80 | – | 0 |  | registry row: solution.compatibility's founder guidance (else founder-lists.md, shared: every dimension re-read); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | founder | solution.relative_advantage | answer | 5 | 2.00 | 1.40 | 2.00 | 2.00 | 1.00 | – | 0 |  | registry row: solution.relative_advantage's founder guidance (else founder-lists.md, shared: every dimension re-read); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | founder | solution.relative_advantage | check | 5 | 2.00 | 1.00 | 1.80 | 1.40 | 1.20 | – | 0 |  | registry row: solution.relative_advantage's founder guidance (else founder-lists.md, shared: every dimension re-read); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | respondent | - | follow_up | 1 | 2.00 | 1.00 | 2.00 | – | 2.00 | 2.00 | 0 |  | registry row: the follow-up ladder (registry data; code writes the words); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | respondent | - | reveal | 3 | 2.00 | 2.00 | 2.00 | – | 2.00 | 1.00 | 0 |  | shared file: solution-mechanism.md (the idea card); R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering) |
|  | SOLUTION | respondent | - | screener | 3 | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | 2.00 | 0 |  | shared file: respondent-questions.md (the story clause, the screener question) |
| **WEAK** | SOLUTION | respondent | problem.prevalence | gate | 3 | 2.00 | 1.33 | 2.00 | 1.00 | 1.67 | 1.67 | 0 |  | shared file: respondent-questions.md (the story clause, the screener question); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | respondent | solution.adoption_friction | item | 3 | 2.00 | 1.67 | 1.00 | 1.00 | 1.67 | 1.33 | 0 |  | shared file: asked.md (the clause), else solution.adoption_friction's respondent wording; R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering) |
| **WEAK** | SOLUTION | respondent | solution.compatibility | item | 3 | 1.67 | 1.00 | 1.67 | 1.33 | 1.67 | 1.67 | 0 |  | shared file: asked.md (the clause), else solution.compatibility's respondent wording; R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |
| **WEAK** | SOLUTION | respondent | solution.relative_advantage | item | 3 | 2.00 | 1.00 | 1.33 | 2.00 | 1.33 | 1.67 | 0 |  | registry row: solution.relative_advantage's respondent wording, else the code transform (no model); R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade |

## Insights -- the grouping of the follow-up lines (§G)

| | scope | dimension | kind | lines | G1 | G2 | insights % | 0s | entries with a 0 | fix |
|---|---|---|---|---|---|---|---|---|---|---|
|  | PROBLEM | problem.current_solution_satisfaction | insights | 4 | 2.00 | 2.00 | 100.0 | 0 |  | shared file: the THEMES grouping instruction (themes.md) |
|  | PROBLEM | problem.importance | insights | 4 | 1.75 | 2.00 | 93.8 | 0 |  | shared file: the THEMES grouping instruction (themes.md) |
|  | SOLUTION | solution.adoption_friction | insights | 3 | 1.67 | 2.00 | 91.7 | 0 |  | shared file: the THEMES grouping instruction (themes.md) |
|  | SOLUTION | solution.compatibility | insights | 2 | 2.00 | 2.00 | 100.0 | 0 |  | shared file: the THEMES grouping instruction (themes.md) |
|  | SOLUTION | solution.relative_advantage | insights | 3 | 1.67 | 2.00 | 91.7 | 0 |  | shared file: the THEMES grouping instruction (themes.md) |

## The weak rows, with their *instead* lines

### COMMERCIAL · founder · - · context -- weak on R5
Fix: **shared file** -- context-interpret.md, and code (ReadBack, Qualifiers).
- 10-palus: Finance leads at venture-backed US startups within two years of a raise, banking with Mercury, Brex or similar. When the company decides where that cash sits until it is needed, they want to keep it safe and earning until it is spent.
- 13-aircaps: Keep the screen, but have the summary read: Deaf and hard-of-hearing adults in the US who talk with hearing people every week want to follow and join face-to-face conversations, even when they are too fast or too noisy to follow.
- 21-codyco: Reservation agents at hotel groups in Germany that run a central reservations office or call center. Booking calls come in on every shift, after hours, at peak and on holidays, and not every one gets answered; they want to turn every guest who calls into a booking.

### COMMERCIAL · founder · - · idea -- weak on R4, R5
Fix: **shared file** -- solution-mechanism.md.
- 08-fresco: What: a scribe that turns narrated site-walk videos into your daily notes. How: as drafted. Belief: The people building it believe superintendents would finish their notes during the site walk, not after it, about 90% faster.
- 10-palus: What: 'More yield on your long-term cash without switching banks'. How: 'You link your existing bank through Plaid. Your long-term reserve goes into a managed portfolio of short-duration, floating-rate, government-backed mortgage bonds, targeting 4.5 to 5 percent. Cash returns to checking in one to two business days, and an SEC-licensed custodian holds the assets.' Belief: 'The people building it believe it would reach 4.5 to 5 percent on the long-term reserve, against roughly 3.5 percent from most money market funds.'
- 13-aircaps: What: Glasses that caption conversations. How: You wear lightweight glasses paired to your phone. They show live captions of what the people nearby are saying inside the lens, so you read the words while keeping eye contact. Belief: The people building it believe it would let the wearer follow and join a face-to-face conversation without looking away.
- 17-expanse: What: a tool that predicts the GPU VRAM, utilisation, RAM, CPUs and walltime a job needs before you submit it. How: it runs on every node of your cluster and hooks into SLURM or Kubernetes; at submit it reads your source code, job script and the hardware, gives its prediction with a confidence interval, flags jobs likely to fail and suggests line-level fixes; if a job fails, it tells you why and how to fix it; everything stays on your network.
- 21-codyco: What: an AI agent that answers a hotel's missed calls. How: The hotel forwards the calls nobody picks up to the agent. It answers in the hotel's voice, answers the guest's questions and writes the confirmed booking straight into the hotel's PMS, such as OPERA Cloud, Sihot or Apaleo. It hands a call to the desk by rules the hotel sets.

### COMMERCIAL · founder · - · persona-who-answers -- weak on R4
Fix: **no model** -- the page's own words (keel-web / keel-cloud code).
- 08-fresco: Who decides on paying for Fresco on a job? General contractor's operations lead (the firm pays per site) — change the title if it is someone else at the GC.
- 21-codyco: Who at the hotel group would decide to pay for Codyco, and who should answer the money questions? Revenue director / Reservations director / Hotel owner / Someone else (type the title)

### COMMERCIAL · founder · - · problem-card -- weak on R5
Fix: **shared file** -- problem-interpret.md.
- 08-fresco: Construction superintendents take 30 to 200 photos on their site walks each day. At the end of the day they spend hours in the trailer uploading them to Procore, ACC or OneDrive and typing daily logs and punch lists, mostly for liability or in case of a dispute with the owner.
- 10-palus: Finance leads at startups that raise enough for a long runway leave the money they will not touch for many months in their bank's treasury product, a money market fund that pays a modest return after a fee, giving up yield for same-day access they do not need, because switching banks or managing it themselves is not worth their time.
- 13-aircaps: Deaf or hard-of-hearing adults lose the conversation when they talk with hearing people at a restaurant, a family meal or a meeting. Hearing aids, for those who wear them, are not dependable with background noise, and reading captions on a phone means looking down and missing faces. In a group many understand only a small part and nod along.
- 17-expanse: Researchers and ML engineers running jobs on SLURM or Kubernetes clusters have to guess memory, run time and GPUs before they submit. Guess too low and the job fails mid-run, losing days of work. Guess too high and the compute sits reserved and unused. So everyone over-requests by two to three times, and clusters run at roughly 30% to 40% effective utilisation. [Yes, that's the problem / Let me edit it]
- 21-codyco: Reservation agents at hotel groups in Germany miss about 5% of booking calls, even with a central reservations office or a call center: after hours, at peak hours and on holidays. Each call that rings out is a booking lost to an online travel agency or a competitor, and across a mid-sized group that is a seven-figure rounding error. Is that the problem?

### COMMERCIAL · founder · - · problem-seed -- weak on R5
Fix: **shared file** -- problem-interpret.md.
- 08-fresco: Construction superintendents spend up to 3 hours a day on documents. They take 30-200 photos a day on their site walks, then spend hours at the end of the day in the trailer uploading them to Procore or OneDrive and typing daily logs and punch lists, mostly for liability or a dispute with the owner.
- 10-palus: Finance leads at startups that raise 18 to 24 months of runway leave the money they will not touch for six months or more in their bank's treasury product, a money market fund paying about 3.5% after a fee of 0.15% to 0.60%, because nobody at the company has time to manage it.
- 13-aircaps: Deaf or hard-of-hearing adults lose the conversation when they sit around a table with hearing people, at a restaurant, a family meal, a meeting or the theatre. Their hearing aids are not dependable with background noise, and reading captions on a phone means looking down and missing faces. In a group their understanding can drop to 20% at best, and they nod along.
- 17-expanse: Researchers and ML engineers running jobs on SLURM or Kubernetes clusters have to guess memory, run time and GPUs before they submit. Guess too low and the job fails mid-run, losing days of work. Guess too high and the compute sits reserved and unused. So everyone over-requests by two to three times, and datacenters run at roughly 30% to 40% effective utilisation; on one national-scale HPC cluster we measured for a month, 59% of the compute across 122k jobs was wasted.
- 21-codyco: Hotel groups in Germany miss about 5% of their reservation calls, even with a central reservations office or a call center: after hours, at peak hours and on holidays. Each call that rings out is a booking that goes to an online travel agency or a competitor, a seven-figure rounding error for a mid-sized group.

### COMMERCIAL · founder · - · ready-interviewer -- weak on R2, R4
Fix: **no model** -- the page's own words (keel-web / keel-cloud code).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 10-palus: How should finance leads answer your questions? Options: They read the questions and tap their answers (included) / An AI interviewer asks them, and you choose its face (uses Keel credits).
- 13-aircaps: How should people answer your questions? Options: Read the questions and tap answers (works without hearing) / AI interviewer that speaks with live captions on screen (uses Keel's credits).
- 17-expanse: How should people get your questions? Options: 'They read and tap (included)', 'A recorded face asks, and they tap their answers (included)', 'An AI interviewer talks with them (uses Keel credits)'.
- 21-codyco: Who should ask your questions? Options: "People read and tap (included on your plan)" or "An AI interviewer speaks them (needs Keel credits)".

### COMMERCIAL · founder · - · ready-pilot -- weak on R2, R4, R5
Fix: **no model** -- the page's own words (keel-web / keel-cloud code).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 10-palus: Offer a small first step? After answering, people can ask to try Palus with a small part of their reserve. Nothing here changes their answers. [Offer it] [Not now]
- 13-aircaps: After people answer, should they be able to ask to try the glasses early? Options: Yes, let them ask / No, not now.
- 17-expanse: After people have answered, can they ask to join your pilot (your two-week waste measurement, then the fixed-fee pilot)? Options: Yes, let them ask / No, not in this study.
- 21-codyco: Do you want people who answer to be able to ask about your pilot (€3,000 money-back, one hotel, up to 8 weeks)? Optional, and it does not change their answers.

### COMMERCIAL · founder · - · solution-card -- weak on R5
Fix: **shared file** -- solution-mechanism.md.
- 08-fresco: The people building it believe superintendents will talk over short videos during their site walks, and that this will get their notes done about 90% faster than doing them after.
- 10-palus: You link your existing bank through Plaid, with no switching banks. Palus holds your long-term reserve in a managed portfolio of short-duration, floating-rate, government-backed mortgage bonds, targeting 4.5 to 5 percent against roughly 3.5 from most money market funds. Cash returns to checking in one to two business days, and an SEC-licensed custodian holds the assets. Belief: the people building it believe a startup's long-term reserve can earn 4.5 to 5 percent without switching banks, if the company can wait a day or two for its cash.
- 13-aircaps: You wear lightweight glasses paired to an app on your phone, and live captions of what people nearby are saying appear inside the lens. The people building it believe this would let the wearer follow and join a face-to-face conversation while keeping eye contact. Does this look right?
- 17-expanse: How: Expanse installs on every node and hooks into SLURM or Kubernetes. On submit, it reads source code, submission script and hardware, and predicts the GPU VRAM, utilisation, memory, CPUs and walltime the job needs, with a confidence interval. It flags likely failures and suggests line-level optimisations; a failed job gets why and how to fix it. All on your network. Belief: The people building it believe it would predict what a job actually needs closely enough that researchers stop over-requesting and the wasted capacity comes back.
- 21-codyco: How: The hotel forwards the calls nobody picks up to Codyco. Codyco answers in the hotel's voice, answers the guest's questions and takes the payment. It writes the confirmed booking straight into the hotel's PMS (OPERA Cloud, Sihot, Apaleo) and hands a call to the desk by rules the hotel sets. Belief: We believe it would answer the calls nobody picks up and turn them into confirmed bookings in the PMS.

### COMMERCIAL · founder · - · solution-seed -- weak on R5
Fix: **shared file** -- solution-mechanism.md.
- 08-fresco: Belief: The people building it believe superintendents would talk over short videos during the site walk and get their notes done then, instead of spending hours on them in the trailer at the end of the day.
- 10-palus: How: You link your existing bank through Plaid. It holds your long-term reserve in a managed portfolio of short-duration, floating-rate, government-backed mortgage bonds, targeting 4.5 to 5 percent. Cash returns to checking in one to two business days. A regulated custodian holds the assets in your company's name. Belief: We believe it would earn 4.5 to 5 percent on the long-term reserve, without switching banks.
- 17-expanse: Expanse installs on every node and hooks into SLURM or Kubernetes. On submit, it reads the source code, submission script and hardware, predicts the GPU memory, memory, CPUs and walltime the job needs, flags failures before they happen and suggests line-level optimisations. A failed job gets why and how to fix it. Everything runs on the customer's own network.
- 21-codyco: What: Codyco, an AI reservation agent. How: The hotel forwards the calls nobody picks up to Codyco; the AI answers in the hotel's voice, answers the guest's questions, takes the payment and writes the confirmed booking straight into the PMS (OPERA Cloud, Sihot, Apaleo), handing a call to the desk by rules the hotel sets.

### COMMERCIAL · founder · commercial.buyer_payer_alignment · check -- weak on R4
Fix: **registry row** -- commercial.buyer_payer_alignment's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 10-palus: Keep the belief and label the third row: 'The board · does not have to agree (we test this)'.
- 13-aircaps: Rows: deaf or hard-of-hearing adult · has the problem; deaf or hard-of-hearing adult · decides and pays. Belief: The deaf or hard-of-hearing adult decides and pays, and nobody else has to agree.
- 17-expanse: Keep the rows, label the last two 'has to agree' and 'can block it', and write: The cluster operator decides, the department head has to agree, and the security team can block it.
- 21-codyco: Is this who is involved in the purchase? Reservation agent: has the problem; Hotel group revenue director: decides to buy; The hotel's owner: has to agree (and the finance director only if I add them, with a stated role).

### COMMERCIAL · founder · commercial.buyer_payer_alignment · choose -- weak on R1, R2, R4
Fix: **registry row** -- commercial.buyer_payer_alignment's founder guidance (else founder-lists.md, shared: every dimension re-read).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 10-palus: Besides the founder, who has to agree before the company moves its reserve? Nobody else / The board / A lead investor
- 13-aircaps: Keel will test: the deaf or hard-of-hearing adult decides, and nobody else has to agree; it holds if at least 2 in 3 say they decided on their own. Is this what you believe? (Yes, test this / No, someone else has a say, let me change it)
- 17-expanse: Who else has to agree before a cluster operator can start a paid pilot? Nobody else / The department head / The security team / Finance or procurement / Someone else; holds if at least 2 in 3 operators say the department head had to agree the last time they bought cluster software.
- 21-codyco: Skip the repeat question and show the belief to confirm, with the bar as: 'Holds if at least 2 in 3 revenue directors say the hotel's owner had to agree the last time they bought something like this.' If the choice stays, offer: Nobody else / The hotel's owner / The finance director / The group's managing director / Someone else.

### COMMERCIAL · founder · commercial.commitment · answer -- weak on R5
Fix: **registry row** -- commercial.commitment's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 10-palus: What's the first real step you'd want the startup to take? e.g. move a small part of the reserve into it. Belief: Most startups would move a small part of the reserve now.
- 13-aircaps: What's the first real step you'd want them to take? Belief: Most deaf or hard-of-hearing adults who have this problem would order a pair of the glasses now, with free returns.
- 17-expanse: Keep the question and hint, and rewrite the belief as: 'Most operators of SLURM or Kubernetes clusters of 100 or more GPUs would run a two-week waste measurement on their cluster now.'
- 21-codyco: Question: "What's the first real step you'd want the hotel group's revenue director to take?" Belief: "Most hotel group revenue directors would pay €3,000 now for a money-back pilot at one hotel."

### COMMERCIAL · founder · commercial.commitment · check -- weak on R5
Fix: **registry row** -- commercial.commitment's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 10-palus: Most startup founders would move a small part of the reserve now.
- 13-aircaps: Most deaf or hard-of-hearing adults would order a pair of these glasses now, knowing they can send them back free.
- 21-codyco: Most hotel group revenue directors would pay €3,000 now for a money-back pilot at one hotel; holds if no more than 1 in 3 say probably not or no.

### COMMERCIAL · founder · commercial.existing_sacrifice · q -- weak on R2, R4, R5
Fix: **registry row** -- commercial.existing_sacrifice's founder guidance (else founder-lists.md, shared: every dimension re-read).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: What does keeping the daily log cost the general contractor today? Options: Money they pay out / Hours their people spend / Money lost on disputes and delays; chip: I'm not sure -- then: Between 30 and 60 hours per site a month, at $55 an hour, spent on the daily log.
- 10-palus: What does leaving this cash where it sits cost the company today? Options: Fees and money they pay / Hours it takes / Yield they miss out on, as a % of the balance a year; chip: I'm not sure -- with the belief reading "Companies miss out on about 2% a year on the balance, in interest on cash that sits in the operating account."
- 13-aircaps: In a typical year, how much do deaf or hard-of-hearing adults spend on captioning apps and hearing-aid extras to keep up with conversations? Options: Money they spend: between $200 and $1,500 a year / Conversations they lose the thread of each month / Time it takes each week / chip: I'm not sure
- 17-expanse: What does this problem cost the cluster's operator today? Options: Money they spend / Staff time it takes / A share of the cluster they lose; then: 'Between 30% and 59% of the cluster's GPU hours are reserved by jobs and never used, each month.'
- 21-codyco: What does this problem cost a hotel group today? (Money they spend / Staff time it takes / A share of bookings they lose / I'm not sure), with the belief line: 'About 5% of reservation calls go unanswered, and the bookings on those calls are lost.'

### COMMERCIAL · founder · commercial.price · q -- weak on R4, R5
Fix: **registry row** -- commercial.price's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 10-palus: What price do you have in mind for earning more on raised cash without switching banks? Options: A percent of the balance each year; A fixed fee each year; A share of the yield earned; One setup price, then a fee each year; One price, then nothing more; Free to them. Chip: No price yet.
- 13-aircaps: What price do you have in mind for help following face-to-face conversations? Options: One price, nothing more; One price, then a fee each month; One price, with an optional monthly upgrade; A fixed fee each month; Free to them. Chip: No price yet.
- 17-expanse: What price do you have in mind for a fix for guessing job resources? Options: A fixed fee per cluster each month / A percent of the compute cost it recovers / One price, then a fee each month / One price, then nothing more / Free to them; chip: No price yet
- 21-codyco: What price do you have in mind for a fix for missed booking calls? (A fixed fee each month / A fee per call or per minute answered / A percent of the bookings it wins back / A pilot fee, then a fee each month / One price, then nothing more / Free to them; chip: No price yet), with the belief line: The payer would think it worth €3,000 for the pilot, then €1,000 to €1,500 per hotel a month.

### COMMERCIAL · founder · commercial.purchase_friction · answer -- weak on R5
Fix: **registry row** -- commercial.purchase_friction's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 10-palus: What could slow down or stop a founder moving the company's reserve to you? Diligence, board or investor approval, a tax adviser, switching. Up to 25 words.
- 21-codyco: What could slow down or stop a purchase? Keep the box and hint, and write the belief as: 'A data protection review of guest calls can slow or stop the purchase.'

### COMMERCIAL · founder · commercial.purchase_friction · check -- weak on R4
Fix: **registry row** -- commercial.purchase_friction's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 21-codyco: Keep the belief and change the third row to 'Works council sign-off on recording calls'.

### COMMERCIAL · founder · commercial.purchase_friction · choose -- weak on R4, R5
Fix: **registry row** -- commercial.purchase_friction's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 10-palus: Which step do you believe slows the purchase most? Diligence on a new provider / Board approval of the cash policy / An investor's sign-off / A tax adviser's sign-off. Holds if at least 2 in 3 say it was needed last time and took a long time, and more of them name it as the slowest than any other step.
- 21-codyco: Which one do you believe slows a hotel group's purchase most? A data protection review of guest calls / A check that bookings land in the group's PMS / Works council sign-off on call monitoring -- Holds if at least 2 in 3 say that, the last time their group bought software that touches guest calls, this review was needed and took a long time.

### PROBLEM · founder · - · context -- weak on R2, R5
Fix: **shared file** -- context-interpret.md, and code (ReadBack, Qualifiers).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Superintendents at US general contractors whose jobs run on Procore or ACC. The day's site walks are done and the photos and notes still have to go into the daily log; they want to keep an accurate record of the day's work on site. We'll ask about their last 5 working days.
- 10-palus: Check this reads right: finance leads at US venture-backed startups within two years of a raise, banking with Mercury, Brex or similar, who want to keep raise money safe and earning until it is spent. We'll ask about what they did in the last 3 months when deciding where that cash sits.
- 13-aircaps: Deaf and hard-of-hearing adults in the US who talk with hearing people every week. Looking at the last 7 days: when a conversation with hearing people was too fast or too noisy to follow, did they want to follow and join it face to face? Does this say it right? (Yes / Change it)
- 17-expanse: Researchers and ML engineers on SLURM or Kubernetes clusters of 100 or more GPUs. When a job is ready to submit and its memory, GPUs and run time have to be guessed first, they want it to run to the end without wasting the cluster. We'll ask about their last 5 working days.
- 21-codyco: Reservation agents at hotel groups in Germany with a central reservations office or call center: booking calls come in on every shift, after hours, at peak and on holidays, and not every one gets answered, while they try to turn every guest who calls into a booking. We'll ask about the last 7 days. Is this right?

### PROBLEM · founder · - · context-card -- weak on R2
Fix: **shared file** -- context-interpret.md, and code (ReadBack, Qualifiers).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Superintendents at US general contractors with jobs on Procore or ACC: once the day's site walks are done and the photos and notes still have to go into the daily log, they want an accurate record of the day's work. We'll ask about their last 5 working days. Is that it? (Yes, that's it / No, let me change it)
- 10-palus: Finance leads at venture-backed US startups within two years of a raise, banking with Mercury, Brex or similar. When the company decides where that cash sits until it is needed, they want to keep it safe and earning until it is spent. We'll ask about the last 3 months. Is that right?
- 13-aircaps: Deaf and hard-of-hearing adults in the US who talk with hearing people every week. In the last 7 days, when a conversation with hearing people was too fast or too noisy, they wanted to follow it and join in. Is that right? (Yes, that's it / Not quite)
- 21-codyco: Reservation agents at hotel groups in Germany with a central reservations office or call center. Booking calls come in on every shift, after hours, at peak and on holidays, and not every one gets answered; they want to turn every guest who calls into a booking. We'll ask about the last 7 days. Is that it? (Yes, that's it / Change something)

### PROBLEM · founder · - · problem-card -- weak on R5
Fix: **shared file** -- problem-interpret.md.
- 10-palus: Finance leads at startups that have just raised 18-24 months of runway leave cash they won't touch for six months or more in their bank's treasury product, a money market fund that pays about 3.5% after a fee. They give up yield for same-day liquidity they don't need, because moving it elsewhere looks like more work and risk than it's worth. Is that the problem?
- 13-aircaps: Deaf or hard-of-hearing adults lose the conversation when hearing people talk fast or over noise, at a restaurant, a family meal or a meeting; hearing aids are not dependable with background noise and phone captions mean looking down and missing faces, so they nod along instead of joining in. Is that the problem? (Yes, that's the problem / Close, let me fix it)
- 17-expanse: Researchers and ML engineers running jobs on SLURM or Kubernetes clusters have to guess memory, time and GPUs before they submit. Guess too low and the job fails mid-run, and they lose days of work; guess too high and the compute sits reserved and unused. So everyone over-requests by two to three times, datacenters run at roughly 30% to 40% effective utilisation, and on one cluster we measured, 59% of the compute across 122k jobs was wasted. [Yes, that's the problem / Change it]
- 21-codyco: Reservation agents at hotel groups in Germany that run a central reservations office or call center still miss about 5% of their calls: after hours, during peak hours and on holidays. Those missed calls can lose bookings to an online travel agency or a competitor, and for a mid-sized group that becomes a seven-figure rounding error. [Yes, that's the problem / Not quite, let me edit it]

### PROBLEM · founder · - · problem-seed -- weak on R5
Fix: **shared file** -- problem-interpret.md.
- 08-fresco: Construction superintendents take 30-200 photos a day on their site walks. When the walks are done, they spend up to 3 hours in the trailer uploading the photos to Procore or OneDrive and typing up daily logs and punch lists, mostly for liability or in case of a dispute with the owner.
- 10-palus: Finance leads at startups that raised 18 to 24 months of runway leave the money they will not touch for six months or more in their bank's treasury product, a money market fund paying about 3.5% after a fee of 0.15% to 0.60%, because nobody at the company has time to manage it.
- 13-aircaps: Keep the statement as written, but say: In groups their understanding can drop to 20% at best, so they nod along.
- 17-expanse: Researchers and ML engineers running jobs on SLURM or Kubernetes clusters have to guess memory, time and GPUs before they submit. Guess wrong and the job fails mid-run, and they lose days of work; over-guess and the compute sits reserved and unused. So everyone over-requests by two to three times, datacenters run at roughly 30% to 40% effective utilisation, and on one national-scale HPC cluster we measured for a month, 59% of the compute across 122k jobs was wasted.
- 21-codyco: Hotel groups in Germany miss about 5% of their booking calls even with a central reservations office or call center: after hours, during peak hours and on holidays. Every call that rings out is a booking that goes to an online travel agency or a competitor, a seven-figure rounding error for a mid-sized group.

### PROBLEM · founder · - · ready-interviewer -- weak on R2, R4
Fix: **no model** -- the page's own words (keel-web / keel-cloud code).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Who should ask superintendents at US general contractors your questions? Options: 'Keel's AI interviewer talks with them (uses Keel's credits)' / 'They read the questions and tap their answers (no credits)'.
- 10-palus: Who should ask your questions? Options: "Keel's AI interviewer talks them through it (uses Keel credits)" or "They read the questions and tap their answers (no credits needed)".
- 13-aircaps: How should people get your questions? Options: They read and tap (included) / Keel's AI interviewer asks them, with every question shown on screen as captions (30 credits per person who answers).
- 17-expanse: Who should ask your researchers the questions? Options: 'They read the questions and tap their answers (no credits)' or 'Keel's AI interviewer asks them (uses Keel's credits)'.
- 21-codyco: How should reservation agents answer your questions? Options: Read and tap (included on your account) / Talk to an AI interviewer (uses Keel credits; pick a face).

### PROBLEM · founder · - · send-format -- weak on R2, R4
Fix: **no model** -- the page's own words (keel-web / keel-cloud code).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 10-palus: How should they answer? AI interviewer: a face on video asks each question aloud and they talk, type or tap; it catches nearly every spoken word, even somewhere noisy (uses Keel's credits). / Text only: they read each question and tap or type. / Let them choose: they pick either one when they open the link (uses Keel's credits).
- 13-aircaps: How should deaf and hard-of-hearing people take your study? Options: Text only (they read each question and tap or type; no sound needed) / AI interviewer with captions (a face on video asks aloud with every word on screen; they can answer by typing or tapping; uses Keel's credits) / Let them choose (they pick when they open the link; uses Keel's credits).
- 17-expanse: How should they answer? AI interviewer: a face on video asks each question aloud and they talk, type or tap; we catch every spoken answer correctly in a quiet room and more than 9 in 10 somewhere loud (uses Keel's credits). / Text only: they read each question and tap or type. / Let them choose: they pick the interviewer or text when they open the link (uses Keel's credits).
- 21-codyco: How should they answer? AI interviewer: a face on video asks each question aloud, and they talk, type or tap (we catch every spoken answer in a quiet room, more than 9 in 10 in a loud one; uses Keel's credits) / Text only: they read each question and tap or type / Let them choose when they open the link (uses Keel's credits)

### PROBLEM · founder · problem.current_solution_satisfaction · answer -- weak on R2, R4, R5
Fix: **registry row** -- problem.current_solution_satisfaction's founder guidance (else founder-lists.md, shared: every dimension re-read).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: How do superintendents get the day's photos and notes into the log today, and how well does that work? (e.g. upload to Procore or ACC in the trailer and type it up, takes hours; fill it in on site as they go; an assistant super writes it)
- 10-palus: How do finance leads earn a return on raise cash today, and how well does it work? (e.g. "Leave it in Mercury or Brex Treasury: about 3.5% after fees, no effort, but we give up yield.")
- 13-aircaps: How do they follow a conversation with hearing people today, and how well does it work? Options: lipreading; hearing aids; captions on a phone; asking people to repeat; nodding along. Then: Followed nearly everything / Missed a little, caught up quickly / Caught the gist, missed the details / Lost it and nodded along.
- 17-expanse: How do researchers size a job today, and how does that turn out? e.g. Pad the request two to three times: it runs, but most of the GPUs sit idle; Reuse sizes from past runs: it mostly runs, sometimes dies mid-run.
- 21-codyco: How do your reservation agents handle booking calls nobody picked up today, for example a call center, overflow to the front desk or calling back from a missed-call list, and how many still get lost? Up to 25 words.

### PROBLEM · founder · problem.current_solution_satisfaction · check -- weak on R4
Fix: **registry row** -- problem.current_solution_satisfaction's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 08-fresco: Keep the rows and reword the belief and bar: 'For most construction superintendents, the daily log still eats more than an hour after the site walks or slips past the end of the day'; holds if at least 2 in 3 pick 'Done in the trailer, over an hour', 'Done late, after leaving the site' or 'Never got done that day'.
- 10-palus: Over the last 3 months, what did the cash from your raise earn compared with what you could have safely got? Options: About the best safe rate available / A little below it, and I accept that / Well below it, and it bothers me / Well below it, but moving it isn't worth the work / I don't know what it earned
- 17-expanse: Keep the belief and bar, and use these rows: Sized from past runs; it ran as planned / Padded it a little; it ran, a little idle / Padded it a lot; it ran, mostly idle / Failed partway through, whether padded or not / Failed partway through more than once before it finished.
- 21-codyco: Keep the belief and split the top row: Every call answered live / Missed calls called back within minutes / Missed calls called back within a few hours / Missed calls called back the next day / Missed calls called back only after days / Missed calls never called back.

### PROBLEM · founder · problem.frequency · q -- weak on R2, R3
Fix: **registry row** -- problem.frequency's founder guidance (else founder-lists.md, shared: every dimension re-read).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 10-palus: Of the last 3 months, how many ended with a typical finance lead's raise cash still in the bank's money market fund, earning only a modest return after fees? (0 to 3 months; I'm not sure)
- 13-aircaps: In the last 7 days, on how many days did a typical deaf or hard-of-hearing adult lose the thread of a conversation with hearing people because it was too fast or too noisy?
- 17-expanse: On a typical researcher's or ML engineer's week, on how many of the 5 working days do they submit a job and have to guess its memory, GPUs and run time? (a low-to-high box, 0 to 5 working days; I'm not sure)
- 21-codyco: In the last 7 days, on how many of their shifts did a typical reservation agent have a booking call ring out unanswered? (box: shifts out of those worked; chip: I'm not sure)

### PROBLEM · founder · problem.importance · answer -- weak on R2
Fix: **registry row** -- problem.importance's founder guidance (else founder-lists.md, shared: every dimension re-read).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: What else is hard for supers once the site walks are done and the daily log still has to be written? Name up to four things. We'll test whether the log is one of the two they'd most want made easier.
- 10-palus: Besides idle cash earning too little, what else is hard for finance leads when deciding where cash from a raise sits? Name up to four things, up to 25 words.
- 17-expanse: Name four other things that are hard for researchers and ML engineers around submitting a job, such as waiting in the queue. Up to 25 words. Belief: of these five, guessing memory, GPUs and run time is one of the two they would most like made easier.
- 21-codyco: What else is hard for reservation agents on a busy shift, besides calls ringing out? Name up to four things, 25 words in all.

### PROBLEM · founder · problem.importance · check -- weak on R2, R4
Fix: **registry row** -- problem.importance's founder guidance (else founder-lists.md, shared: every dimension re-read).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Of these five parts of running the job, which two would you most like made easier? Logging the day's photos and notes / Keeping the job on schedule / Getting subs to show up and finish / Chasing RFIs and submittals / Keeping the site safe
- 10-palus: Of these five, which two would you most like made easier when deciding where cash from a raise sits: idle cash earning little after fees; making the cash last longer; keeping cash safe above the insured limit; getting cash back fast when needed; moving money between accounts without mistakes?
- 13-aircaps: Of these five, which two would deaf or hard-of-hearing adults most like made easier when a conversation with hearing people is too fast or too noisy: losing the thread of the conversation; getting a word in at the right moment; having to ask people to repeat themselves; nodding along without knowing what was said; being worn out by the effort of following?
- 17-expanse: Of these five, which two would you most like made easier when you run jobs on the cluster? Guessing memory, GPUs and run time / Waiting for a job to start / Working out why a job failed / Getting software working on the cluster / Running out of the group's allocation
- 21-codyco: Of these five, which two would you most like made easier on your reservation shift? Booking calls ringing out unanswered; Handling guests' requests at the desk; Keeping rates right on every channel; Answering booking emails and group requests; Getting through the check-in and check-out rush.

### PROBLEM · founder · problem.prevalence · q -- weak on R3, R5
Fix: **registry row** -- problem.prevalence's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 08-fresco: In the last 5 working days, how many out of 10 construction superintendents still had the day's photos and notes to put into the daily log after finishing their site walks? (Fewer than 2 in 10 / 2 or 3 in 10 / 4 or 5 in 10 / 6 or 7 in 10 / 8 or more in 10)
- 10-palus: In the last 3 months, how many out of 10 finance leads kept their raise cash in their bank's treasury product, earning about 3.5% or less after fees? (Fewer than 2 in 10 / 2 or 3 / 4 or 5 / 6 or 7 / 8 or more)
- 13-aircaps: In the last 7 days, out of 10 deaf or hard-of-hearing adults in the US who talk with hearing people every week, how many lost the thread of a conversation because it was too fast or too noisy? (same five bands)
- 21-codyco: In the last 7 days, how many out of 10 reservation agents saw a booking call on their shift go unanswered? (Fewer than 2 in 10 / 2 or 3 in 10 / 4 or 5 in 10 / 6 or 7 in 10 / 8 or more in 10)

### PROBLEM · respondent · problem.current_solution_satisfaction · item -- weak on R2, R4, R6
Fix: **registry row** -- problem.current_solution_satisfaction's respondent wording, else the code transform (no model).
Fix for R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Think of your last daily log: where did you finish it? On site; in the trailer; at home; the next morning; or it never got written up properly. Or say Someone else did it.
- 10-palus: Thinking of the last 3 months, how did the return on your idle cash compare with the work it took? Good rate, little work; Fair rate, little work; Fair rate, too much work; Low rate, little work; or Earned nothing in checking. Or say Someone else did it.
- 13-aircaps: How much of your last conversation with hearing people did you follow? Followed nearly everything; Missed a little, caught up quickly; Caught the gist, missed the details; Lost the thread and mostly nodded along; or Could not follow it at all. Or say I can't recall.
- 17-expanse: How did sizing your last job go? Sized from past runs, ran as planned; padded a little, some sat idle; doubled everything, much sat idle; guessed low, it died and was resubmitted; or copied an old script, not sure how it went. Or say Someone else did it.
- 21-codyco: In the last 7 days, what happened to booking calls nobody answered on your shift? All called back within minutes; all called back that day; some called back when there was time; few called back; or none called back. Or say Someone else did it.

### PROBLEM · respondent · problem.frequency · item -- weak on R2, R6
Fix: **registry row** -- problem.frequency's respondent wording, else the code transform (no model).
Fix for R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: In the last 5 working days, on how many days did you do your daily log after your site walks? 1; 2; 3; 4; or 5. Or say I can't recall.
- 10-palus: In the last 3 months, how many months did raised cash sit in your bank's money market fund? 1 month; 2 months; or all 3 months. Or say I can't recall.
- 13-aircaps: In the last 7 days, on how many days did you get lost following a conversation with hearing people? Say a number from 1 to 7, or say I can't recall.
- 17-expanse: In the last 5 working days, on how many days did you have to guess memory, GPUs and run time for a job? 1; 2; 3; 4; or 5. Or say I can't recall.
- 21-codyco: In the last 7 days, on how many of your shifts did a booking call go unanswered? None; 1 or 2; 3 or 4; 5 or more. Or say I can't recall.

### PROBLEM · respondent · problem.importance · item -- weak on R2, R4, R6
Fix: **registry row** -- problem.importance's respondent wording, else the code transform (no model).
Fix for R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Think of your last work week on site. Which one of these would you most like made easier? Getting subs to show up and finish; Keeping the site safe; Chasing RFIs and submittals; Keeping the job on schedule; or Logging the day's photos and notes. Or say None of these.
- 10-palus: Think of the last time you decided where to keep your raised cash. Which one of these would you most like made easier? Knowing the months of runway left; Keeping cash safe above the insured limit; Getting cash back fast when needed; Earning more on idle cash; or Moving money between accounts without mistakes. Or say None of these.
- 13-aircaps: Think of your last conversation with hearing people. Which one of these would you most like to be easier? Keeping up when people talk fast; Following along in a noisy place; Following when several people talk; Getting a word in at the right moment; or Having energy left afterward. Or say None of these.
- 21-codyco: Think of your last shift. Which one of these would you most like made easier? Booking calls ringing out unanswered; Answering booking emails and group requests; Finding availability while the guest waits; Keeping rates right on every channel; or Turning callers into bookings. Or say None of these.

### PROBLEM · respondent · problem.prevalence · gate -- weak on R2, R4, R5
Fix: **shared file** -- respondent-questions.md (the story clause, the screener question).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: In the last 5 working days, did you put your photos and notes into the daily log after your site walks? Yes or No.
- 10-palus: In the last 3 months, was any of the cash from your raise held in a money market fund through your bank? Yes / No
- 13-aircaps: In the last 7 days, did you lose track of what was being said in a conversation with hearing people? Yes; No; or I wasn't in one this week. Or say I can't recall.
- 17-expanse: In the last 5 working days, did you submit a job where you had to guess its memory, GPUs and run time? Yes; No; or say I can't recall.
- 21-codyco: In the last 7 days, did you take a booking call on your shift? Yes or No.

### SOLUTION · founder · - · context -- weak on R2, R5
Fix: **shared file** -- context-interpret.md, and code (ReadBack, Qualifiers).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Keel understands: Construction superintendents at US general contractors whose jobs run on Procore or ACC. When the day's site walks are done and the photos and notes still have to go into the daily log, they want to keep an accurate record of the day's work on site. We'll ask about their last 5 working days.
- 10-palus: Finance leads at venture-backed US startups within two years of a raise, banking with Mercury, Brex or similar, who keep the money from the raise safe and earning until the company spends it. We'll ask about the last 3 months. Is this right?
- 13-aircaps: Deaf and hard-of-hearing adults in the US who talk with hearing people every week. When a conversation is too fast or too noisy to follow, they want to follow and join it. We'll ask about the last 7 days. Is that right?
- 17-expanse: Researchers and ML engineers on SLURM or Kubernetes clusters of 100 or more GPUs. When a job is ready to submit and its memory, GPUs and run time have to be guessed first, they want to get each job to run to the end without wasting the cluster. We'll ask about the jobs they submitted in the last 5 working days.
- 21-codyco: Reservation agents at hotel groups in Germany that run a central reservations office or call center. Booking calls come in on every shift, after hours, at peak and on holidays, and not every one gets answered; they want to turn every guest who calls into a booking. We'll ask about the last 7 days.

### SOLUTION · founder · - · context-card -- weak on R2
Fix: **shared file** -- context-interpret.md, and code (ReadBack, Qualifiers).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Construction superintendents at US general contractors with jobs on Procore or ACC. The day's site walks are done and the photos and notes still have to go into the daily log. We'll ask about their last 5 working days. Is that right?
- 10-palus: Finance leads at venture-backed US startups within two years of a raise, banking with Mercury, Brex or similar. When the company decides where the raise sits until it's needed, they want to keep that money safe and earning until it's spent. We'll ask about the last 3 months. Is that right? [Yes, that's it] [Not quite]
- 13-aircaps: Keep the card, but end it: "We'll ask about the last 7 days: when a conversation with hearing people was too fast or too noisy to follow, and they wanted to follow and join in." (Yes, that's it / Not quite)
- 17-expanse: Researchers and ML engineers on SLURM or Kubernetes clusters of 100 or more GPUs. When a job is ready to submit and its memory, GPUs and run time have to be guessed first, they want to get each job to run to the end without wasting the cluster. We'll ask about jobs they submitted in the last 5 working days. Is that it?
- 21-codyco: Reservation agents at hotel groups in Germany with a central reservations office or call center. Booking calls come in on every shift, after hours, at peak and on holidays, and not every one gets answered; they want every guest who calls to end up booked. We'll ask them about their last 7 days. Is that it?

### SOLUTION · founder · - · idea -- weak on R2, R5
Fix: **shared file** -- solution-mechanism.md.
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: What: an AI scribe for superintendents. How: During the site walk, you take short videos and talk over them, or upload photos. These become notes with photos, assignees and due dates. You text the crew their action items and send the notes to Procore or ACC in one click.
- 10-palus: What: a treasury account for a startup's long-term cash. How: You connect it to your existing bank through Plaid and move your long-term reserve into a managed portfolio of short-duration, floating-rate, government-backed mortgage bonds, held with an SEC-licensed custodian; when you need cash, it returns to checking. Belief: We believe it can target 4.5 to 5 percent, against roughly 3.5 percent from most money market funds, with cash typically back in one to two business days.
- 13-aircaps: When a conversation with hearing people is too fast or too noisy to follow, you wear lightweight glasses paired to your phone, and live captions of what the people nearby are saying appear inside the lens, so you can read the words while keeping eye contact.
- 17-expanse: What: a prediction of the memory, GPUs and run time a job needs, made as you submit it. How: An agent on every node hooks into SLURM or the Kubernetes scheduler, on your own network, and reads the job's source code, submission script and hardware. It predicts VRAM, RAM, CPUs and walltime at submit time, flags likely failures, suggests line-level fixes, and when a job fails says why and how to fix it.
- 21-codyco: what: an AI agent that answers a hotel's missed calls; how: You forward calls nobody picks up to the agent. It answers in the hotel's voice, answers the guest's questions and takes the payment. It writes the confirmed booking straight into the hotel's PMS, such as OPERA Cloud, Sihot or Apaleo, and hands a call to the desk by rules the hotel sets.

### SOLUTION · founder · - · problem-card -- weak on R5
Fix: **shared file** -- problem-interpret.md.
- 08-fresco: Construction superintendents take 30-200 photos a day on their site walks, mostly for liability or in case of a dispute with the owner, then spend hours at the end of the day in the trailer uploading them to Procore or OneDrive and typing up daily logs and punch lists. Is that the problem? (Yes, that's the problem / Not quite, let me fix it)
- 10-palus: Finance leads at startups with a long runway leave cash they won't touch for six months or more in their bank's treasury product, giving up yield for same-day liquidity they don't need, because managing it themselves is too much work.
- 13-aircaps: Deaf and hard-of-hearing adults lose the conversation when hearing people talk too fast or over noise, at a restaurant, a family meal or a meeting. Hearing aids are not dependable with background noise, and phone captions mean looking down and missing faces. In groups they catch only a small part, so they nod along instead of joining in. Is that the problem? (Yes, that's the problem / Close, but I'd change it)
- 17-expanse: Researchers and ML engineers on SLURM or Kubernetes clusters of 100+ GPUs have to guess memory, time and GPUs before they submit. Guess too low and the job fails mid-run, and days of work are lost. Guess too high and the compute sits reserved and unused. So everyone over-requests by two to three times, and datacenters run at roughly 30% to 40% effective utilisation, with up to 59% of the compute wasted. [Yes, that's the problem / Not quite]
- 21-codyco: Reservation agents at hotel groups, even with a central reservations office or a call center, still miss about 5% of booking calls: after hours, at peak hours and on holidays. Many of those callers book through an online travel agency or a competitor instead, and across a mid-sized group it adds up to a seven-figure sum. [Yes, that's the problem / Not quite, let me fix it]

### SOLUTION · founder · - · problem-seed -- weak on R5
Fix: **shared file** -- problem-interpret.md.
- 08-fresco: Construction superintendents spend up to 3 hours a day on documents: they take 30-200 photos a day on their site walks, then spend hours at the end of the day in the trailer uploading them to Procore or OneDrive and typing up daily logs and punch lists, mostly for liability or in case of a dispute with the owner.
- 10-palus: Finance leads at startups that raised 18 to 24 months of runway leave the money they will not touch for six months or more in their bank's treasury product, a money market fund paying about 3.5% after a fee of 0.15% to 0.60%, because nobody at the company has time to manage it.
- 13-aircaps: Deaf and hard-of-hearing adults lose the conversation when they sit around a table with hearing people, at a restaurant, a family meal, a meeting or the theatre. Their hearing aids are not dependable with background noise, and reading captions on a phone means looking down and missing faces. In groups, their understanding can drop to 20% at best, so they nod along.
- 17-expanse: Researchers and ML engineers running jobs on SLURM or Kubernetes clusters have to guess memory, time and GPUs before they submit. Guess too low and the job fails mid-run, and days of work are lost. Guess too high and the compute sits reserved and unused. So everyone over-requests by two to three times, and datacenters run at roughly 30% to 40% effective utilisation; on one national-scale HPC cluster we measured for a month, 59% of the compute across 122k jobs was wasted.
- 21-codyco: Reservation agents at hotel groups, even with a central reservations office or a call center, still see about 5% of booking calls go unanswered: after hours, at peak hours and on holidays. Every call that rings out is a booking that goes to an online travel agency or a competitor, a seven-figure rounding error for a mid-sized group.

### SOLUTION · founder · - · ready-interviewer -- weak on R2, R4
Fix: **no model** -- the page's own words (keel-web / keel-cloud code).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Who should ask your questions? Options: "Keel's AI interviewer (uses Keel credits)" / "No interviewer: people read the questions and tap their answers"
- 10-palus: How should people answer your questions? Options: 'They read and tap (included)' or 'An AI interviewer asks them (30 Keel credits per person who answers)', and if AI, show the face it will use.
- 13-aircaps: How should people answer your questions? Options: They read and tap (included) / An AI interviewer asks them, with captions on screen (uses Keel's credits).
- 17-expanse: How should researchers answer your questions? Options: "They read the questions and tap their answers (included)" / "Keel's AI interviewer asks them, using Keel's credits".
- 21-codyco: How should people answer your questions? Options: 'They read and tap their answers (included with your account)' / 'An AI interviewer asks them out loud (uses Keel credits)'; if the second is picked, then ask 'Which face should they see?'

### SOLUTION · founder · - · ready-pilot -- weak on R4, R5
Fix: **no model** -- the page's own words (keel-web / keel-cloud code).
- 08-fresco: Offer a pilot on one site to people who finish the study? (Yes, let them ask to join / No, not now). Optional, and it does not change their answers.
- 10-palus: Offer early access? Optional. After people have answered, they can ask to try Palus with a small part of their reserve. Nothing here changes their answers.
- 13-aircaps: Do you want people who finish to be able to ask to try the glasses? (Yes, let them ask / Not now) Optional, and it doesn't change their answers.
- 17-expanse: Offer a pilot to people who answer? Options: Yes, let cluster operators ask for the two-week measurement and paid pilot / No, not in this study.
- 21-codyco: Offer your pilot to people who finish the study? They could ask to join the €3,000 money-back pilot at one hotel. Nothing here changes their answers. [Yes, offer it / No, not now]

### SOLUTION · founder · - · send-format -- weak on R2, R4
Fix: **no model** -- the page's own words (keel-web / keel-cloud code).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: How should they answer? AI interviewer: a face on video asks each question aloud and they talk, type or tap; it catches every word in a quiet room and more than 9 in 10 on a loud site (needs Keel's credits). Text only: they read each question and tap or type. Let them choose: they pick when they open the link (needs Keel's credits).
- 13-aircaps: How should they answer? Text only: they read each question and tap or type. AI interviewer: a face on video asks each question aloud with captions on screen, and they talk, type or tap (uses Keel's credits). Let them choose: they pick when they open the link (uses Keel's credits).
- 17-expanse: How should they answer? AI interviewer: a face on video asks each question aloud and they talk, type or tap (it understands nearly every spoken answer, even somewhere loud; uses Keel's credits) / Text only: they read each question and tap or type / Let them choose: they pick when they open the link (uses Keel's credits)

### SOLUTION · founder · - · solution-card -- weak on R5
Fix: **shared file** -- solution-mechanism.md.
- 08-fresco: Belief: The people building it believe superintendents could talk over short videos or upload photos during the site walk and get notes and crew texts, then send the notes to Procore or ACC in one click.
- 10-palus: How: You connect your existing bank through Plaid and move your long-term reserve into a portfolio of short-duration, floating-rate government-backed mortgage-backed securities, held with an SEC-licensed custodian; cash comes back to your checking account when you need it. Belief: We believe it can target 4.5 to 5 percent, against roughly 3.5 percent from most money market funds, with cash back in one to two business days.
- 13-aircaps: When a conversation with hearing people is too fast or too noisy to follow, you wear lightweight glasses paired to your phone; they pick up the people nearby and show live captions inside the lens, visible only to you, so you read the words and keep eye contact.
- 17-expanse: How: Expanse installs an agent on every node and hooks into the SLURM or Kubernetes scheduler, all on your own network. It reads the job's source code, submission script and live hardware telemetry, predicts the GPU VRAM, utilisation, memory, CPUs and walltime the job needs at submit time, flags likely failures, suggests line-level optimisations, and says why a job failed and how to fix it.
- 21-codyco: Keep the card but change one line to: 'It writes the confirmed booking straight into the hotel's PMS, such as OPERA Cloud, Sihot or Apaleo.'

### SOLUTION · founder · - · solution-seed -- weak on R5
Fix: **shared file** -- solution-mechanism.md.
- 08-fresco: The people building it believe it would turn site walk videos into notes and crew texts, and send the notes to Procore or ACC in one click.
- 10-palus: How: You link the treasury account to your existing bank through Plaid. It holds your long-term reserve in a managed portfolio of short-duration, floating-rate, government-backed mortgage bonds, held in your company's name at a regulated custodian. Cash returns to checking. Belief: The people building it believe it would target a 4.5 to 5 percent yield, with the cash back in checking in one to two business days.
- 17-expanse: Expanse installs on every node and hooks into SLURM or Kubernetes, on your own network. It reads the job's source code, submission script and hardware, and at submit time predicts the GPU memory, memory, CPUs and walltime the job needs. It flags failures before they happen and suggests line-level optimisations. When a job fails, it says why and how to fix it.
- 21-codyco: You forward calls nobody picks up to Codyco, an AI reservation agent. It answers in the hotel's voice, answers the guest's questions, takes the payment and writes the confirmed booking straight into the PMS (OPERA Cloud, Sihot, Apaleo). It hands a call to the desk by rules the hotel sets.

### SOLUTION · founder · solution.adoption_friction · answer -- weak on R5
Fix: **registry row** -- solution.adoption_friction's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 08-fresco: What will a superintendent have to do to start using it? (Any setup, extra steps or learning. Up to 25 words.) Same chip, with only the belief drawn from this answer, e.g. "Most would take short videos and talk over them on walks."
- 10-palus: Keep the question and hint, but have Keel write: 'Most would link the company bank account through Plaid and move the long-term reserve out of the bank's treasury', or show which of the two steps it kept for testing and why.
- 13-aircaps: Keep the question and hint, but make the belief: Most would wear the glasses paired to their phone and charge them every day.
- 17-expanse: Keep the question and hint, but change the belief to: Most would use the suggested sizes instead of padding their requests.
- 21-codyco: Keep the question and hint, and write the belief from my answer: 'Most would let an AI answer guests in the hotel's voice and set which calls it hands to the desk.'

### SOLUTION · founder · solution.adoption_friction · check -- weak on R4, R5
Fix: **registry row** -- solution.adoption_friction's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 08-fresco: What would they have to do to start? Take short videos or photos on walks and talk over them; check and fix the notes before they go out; get Procore or ACC connected, by them or the office. Belief: Most would take short videos and talk over them on their walks.
- 10-palus: Keep the screen, but add a row, 'Open the account and move a small first amount', so the belief can test the step I actually ask for first.
- 13-aircaps: Most would wear the glasses, paired to their phone, in their conversations. Rows: Pair the glasses to their phone / Wear the glasses in conversations with hearing people / Keep the glasses charged for the day

### SOLUTION · founder · solution.adoption_friction · choose -- weak on R3, R4, R5
Fix: **registry row** -- solution.adoption_friction's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 08-fresco: Which of these do you most need to be true? Take short videos and talk over them on walks (selected; Keel will test: Most would take short videos and talk over them on walks) / Check and fix the notes before they go out / Connect it to Procore or ACC
- 10-palus: Which step is most likely to stop them? (Link the company bank account through Plaid / Move the long-term reserve out of the bank's treasury) Keel will ask finance leads if they would do it, and your belief holds if no more than 1 in 3 say probably not or no.
- 13-aircaps: Which step do you most need to test? Options: Wear the glasses in conversations, paired to their phone / Keep the glasses charged through the day / Keep their phone with them and online; belief: Most would wear the glasses, paired to their phone, in their conversations.
- 17-expanse: Which step might stop them? Use the suggested sizes instead of padding / Apply the line-level code fixes it suggests -- and drop connecting the cluster, because the operator installs it and the researcher submits as before; Keel tests: Most would use the suggested sizes instead of padding.
- 21-codyco: Which step might stop them? Let an AI answer guests in the hotel's voice / Decide which calls the AI hands to the desk / Have the hotel's booking system connected to the AI (their IT does this); belief: Most would let an AI answer guests in the hotel's voice.

### SOLUTION · founder · solution.compatibility · answer -- weak on R5
Fix: **registry row** -- solution.compatibility's founder guidance (else founder-lists.md, shared: every dimension re-read).
- 08-fresco: Keep the question and hint, but show all three beliefs: "For most, they had their phone out on the walk." / "For most, they could talk over the noise on site." / "For most, the job kept its logs in Procore or ACC."
- 10-palus: What must already be true at their company for this to work? (for example: their bank links through Plaid, they can wait two days for cash, their policy allows bonds beyond Treasuries)
- 13-aircaps: What do they already have with them, or already do, in a conversation that this relies on? (e.g. phone with them and online; wearing glasses throughout; reading while watching faces) -- and test each of my three points as its own belief.
- 17-expanse: How does it fit into the way they work today? Name what they already have or do that it plugs into, and we'll test the one most likely to fail -- here, the source code sits on the cluster beside the job script.
- 21-codyco: How does it fit into the way they work today? Keep Keel's belief to the one thing that matters most, but show it as: "Unanswered calls can be forwarded to another number, and the PMS takes bookings from outside systems."

### SOLUTION · founder · solution.compatibility · choose -- weak on R2
Fix: **registry row** -- solution.compatibility's founder guidance (else founder-lists.md, shared: every dimension re-read).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: What must be true for this to fit their day? Options: They had their phone out on the walk / They could talk over the noise on site / They would be fine talking into their phone with the crew around / Their notes could go straight into Procore or ACC
- 13-aircaps: For most, their phone was with them and online during that conversation.
- 21-codyco: Which must be true at most hotel groups for this to work? Unanswered calls can be forwarded to another number / The PMS accepts bookings from outside systems / Rates and room types are kept up to date; holds if at least 2 in 3 say yes, always.

### SOLUTION · founder · solution.relative_advantage · answer -- weak on R2, R5
Fix: **registry row** -- solution.relative_advantage's founder guidance (else founder-lists.md, shared: every dimension re-read).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: What does it do better than the way they do it today? Belief: For most, it would have given them hours back at the end of the day on their last daily log, and got action items to the crew the same day.
- 10-palus: Keep the question and hint, but have the belief read: 'For most, it would have earned them higher yield on the cash from a raise, without hiring anyone to manage treasury.'
- 13-aircaps: What does it let them do that they can't do today with phone captions, lipreading or asking people to repeat? Belief: For most, it would have let them follow more of their last conversation without asking anyone to repeat.
- 17-expanse: What does it do better than the way they do it today? Belief: For most, their last job would have run first time with no resubmit, and waited less in the queue.
- 21-codyco: Keep the question and hint, and have the belief read: 'For most, it would have answered the booking call nobody picked up on their last shift and turned it into a booking.'

### SOLUTION · founder · solution.relative_advantage · check -- weak on R2, R4, R5
Fix: **registry row** -- solution.relative_advantage's founder guidance (else founder-lists.md, shared: every dimension re-read).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: For most, it would have saved them hours on their last daily log. Rows: Hours saved on the daily log; Notes and action items done during the site walk, not after.
- 10-palus: For most, it would have earned more on the long-term cash from their raise over the last 3 months, without switching banks or adding treasury work. Rows: Higher yield on the cash from a raise / No need to hire for treasury.
- 13-aircaps: Belief: "For most, the glasses would have helped them follow more of their last hard conversation without asking anyone to repeat." Rows: "Followed more of what was said" / "Asked people to repeat less".
- 17-expanse: For most, their last job would have run to the end first time, with no resubmit.
- 21-codyco: Think of the last booking call you could not answer: if an assistant had picked it up and put the booking in your system, how would that have compared with what actually happened? (Much better / A bit better / No difference / Worse)

### SOLUTION · respondent · - · follow_up -- weak on R2
Fix: **registry row** -- the follow-up ladder (registry data; code writes the words).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 13-aircaps: You said only if it connected without any trouble. What would have to happen when you set up the glasses for that to be true?

### SOLUTION · respondent · - · reveal -- weak on R6
Fix: **shared file** -- solution-mechanism.md (the idea card).
Fix for R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering).
- 08-fresco: Imagine Fresco. During the site walk, you take short videos and talk over them. Fresco turns them into notes with photos, assignees and due dates, and texts the crew their action items. You send the notes to Procore or ACC in one click. The people building it believe this would save you the hours of logging after the walk.
- 13-aircaps: Imagine AirCaps. When a conversation with hearing people is too fast or too noisy to follow, you wear lightweight glasses with an app. Live captions of what people nearby are saying appear in the lens. The people building it believe you could read the words while keeping eye contact.
- 17-expanse: Imagine Expanse. It connects to SLURM or Kubernetes on your own network and reads your job's code, submission script and hardware. When you submit, it predicts GPU memory, memory, CPUs and walltime, and if a job fails it says why and how to fix it. The people building it believe its predictions would match what a job actually needs.

### SOLUTION · respondent · problem.prevalence · gate -- weak on R2, R4
Fix: **shared file** -- respondent-questions.md (the story clause, the screener question).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: In the last 5 working days, after your site walks, did you still have photos or notes to put in the daily log? Yes or no, with no escape chips.
- 13-aircaps: In the last 7 days, did you lose track of a conversation with hearing people? Yes; No; or say I can't recall.
- 17-expanse: In the last 5 working days, did you submit a job where you had to guess its memory, GPUs or run time? Yes; No; or say I can't recall.

### SOLUTION · respondent · solution.adoption_friction · item -- weak on R3, R4, R6
Fix: **shared file** -- asked.md (the clause), else solution.adoption_friction's respondent wording.
Fix for R6 -- the registry row's wording or the spoken transform (code: keel-cloud's spoken rendering).
- 08-fresco: Fresco has to connect to your Procore or ACC account. Would you connect it, or not? Yes; Only if the connection is easy; Probably not; or No. Or say I can't tell.
- 13-aircaps: AirCaps means pairing the glasses to your phone. Would you do that, or not? Yes; Yes, if it pairs the first time; Probably not; or No. Or say I can't tell.
- 17-expanse: Would you connect Expanse to your SLURM or Kubernetes cluster, or not? Yes; Only if it ran on our own network; Only if our cluster admins agreed; or No. Or say I can't tell.

### SOLUTION · respondent · solution.compatibility · item -- weak on R2, R4
Fix: **shared file** -- asked.md (the clause), else solution.compatibility's respondent wording.
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Think of your last daily log. Where you did your site walk, could you have spoken your notes into your phone over the noise? Yes, easily; Yes, mostly; Only sometimes; or No. Or say I can't tell.
- 13-aircaps: Think of your last conversation with hearing people. Did you have your phone with you, and was it online? Yes, with me and online; With me, but not online; or Not with me. Or say I can't tell.
- 17-expanse: Think of your last submission. Where was the source code? On the cluster's shared filesystem; in a container image; pulled from a repo at launch; or somewhere else. Or say I can't tell.

### SOLUTION · respondent · solution.relative_advantage · item -- weak on R2, R3, R5
Fix: **registry row** -- solution.relative_advantage's respondent wording, else the code transform (no model).
Fix for R2 -- the registry row, or the instruction gains the trade's words: the writer handed the persona (*in the words of {actor_plural}*), never a condition on one trade.
- 08-fresco: Would Fresco have made your last daily log better, or not? A lot better; A little better; No difference; or Worse. Or say I can't tell.
- 13-aircaps: Think of your last conversation with hearing people: would AirCaps have made it go better for you, or not? A lot better; A little better; No difference; Worse; or I can't tell.
- 17-expanse: Think of your last submission: would Expanse have helped that job run to the end without wasting the cluster, or not? A lot; A little; No difference; It would have been worse; or I can't tell.


## The trend per study (entry · scope; the last three score files)

| study | file | scored | cloud | founder % | respondent % | overall % | spoken % | flagged % | R1 | R2 | R3 | R4 | R5 | R6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 08-fresco · COMMERCIAL | 20261028-COMMERCIAL-r2-88bfce8-v13-claude-opus-5-5.json | 2026-10-28 | 88bfce8 | 89.5 | – | 89.5 | – | 0.0 | 2.00 | 1.50 | 2.00 | 2.00 | 1.50 | – |
| 08-fresco · COMMERCIAL | 20261028-COMMERCIAL-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 82.1 ↓ | – | 82.1 ↓ | – | 0.0 = | 2.00 = | 1.58 ↑ | 1.92 ↓ | 1.50 ↓ | 1.17 ↓ | – |
| 08-fresco · COMMERCIAL | 20261030-COMMERCIAL-r2-fcec453-v13-claude-opus-5-5.json | 2026-10-30 | fcec453 | 89.6 ↑ | – | 89.6 ↑ | – | 0.0 = | 2.00 = | 1.75 ↑ | 2.00 ↑ | 1.60 ↑ | 1.50 ↑ | – |
| 08-fresco · PROBLEM | 20261028-PROBLEM-r2-88bfce8-v13-claude-opus-5-5.json | 2026-10-28 | 88bfce8 | 89.5 | – | 89.5 | – | 0.0 | 2.00 | 1.50 | 2.00 | 2.00 | 1.50 | – |
| 08-fresco · PROBLEM | 20261028-PROBLEM-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 82.9 ↓ | 72.1 | 79.4 ↓ | 80.0 | 0.0 = | 1.95 ↓ | 1.25 ↓ | 1.90 ↓ | 1.39 ↓ | 1.35 ↓ | 1.60 |
| 08-fresco · PROBLEM | 20261030-PROBLEM-r2-fcec453-v13-claude-opus-5-5.json | 2026-10-30 | fcec453 | 87.5 ↑ | 83.8 ↑ | 86.3 ↑ | 90.0 ↑ | 0.0 = | 1.95 ↓ | 1.37 ↑ | 2.00 ↑ | 1.53 ↑ | 1.68 ↑ | 1.80 ↑ |
| 08-fresco · SOLUTION | 20261028-SOLUTION-r2-88bfce8-v13-claude-opus-5-5.json | 2026-10-28 | 88bfce8 | 87.6 | – | 87.6 | – | 0.0 | 2.00 | 1.62 | 2.00 | 1.53 | 1.57 | – |
| 08-fresco · SOLUTION | 20261028-SOLUTION-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 87.0 ↓ | 80.5 | 85.0 ↓ | 75.0 | 3.8 ↑ | 1.96 ↓ | 1.54 ↓ | 1.96 ↓ | 1.48 ↓ | 1.50 ↓ | 1.50 |
| 08-fresco · SOLUTION | 20261030-SOLUTION-r2-fcec453-v13-claude-opus-5-5.json | 2026-10-30 | fcec453 | 85.8 ↓ | 84.1 ↑ | 85.3 ↑ | 83.3 ↑ | 0.0 ↓ | 1.96 = | 1.61 ↑ | 1.85 ↓ | 1.70 ↑ | 1.35 ↓ | 1.67 ↑ |
| 10-palus · COMMERCIAL | 20261028-COMMERCIAL-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 89.5 | – | 89.5 | – | 0.0 | 2.00 | 1.50 | 2.00 | 2.00 | 1.50 | – |
| 10-palus · COMMERCIAL | 20261028-COMMERCIAL-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 85.4 ↓ | – | 85.4 ↓ | – | 0.0 = | 1.95 ↓ | 1.43 ↓ | 2.00 = | 1.47 ↓ | 1.62 ↑ | – |
| 10-palus · COMMERCIAL | 20261030-COMMERCIAL-r2-fcec453-v13-claude-opus-5-5.json | 2026-10-30 | fcec453 | 86.7 ↑ | – | 86.7 ↑ | – | 0.0 = | 2.00 ↑ | 1.74 ↑ | 2.00 = | 1.35 ↓ | 1.48 ↓ | – |
| 10-palus · PROBLEM | 20261028-PROBLEM-r2-88bfce8-v13-claude-opus-5-5.json | 2026-10-28 | 88bfce8 | 89.5 | – | 89.5 | – | 0.0 | 2.00 | 1.50 | 2.00 | 2.00 | 1.50 | – |
| 10-palus · PROBLEM | 20261028-PROBLEM-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 84.0 ↓ | 78.4 | 81.4 ↓ | 78.6 | 5.6 ↑ | 1.83 ↓ | 1.44 ↓ | 1.89 ↓ | 1.36 ↓ | 1.50 = | 1.57 |
| 10-palus · PROBLEM | 20261030-PROBLEM-r2-fcec453-v13-claude-opus-5-5.json | 2026-10-30 | fcec453 | 83.1 ↓ | 73.9 ↓ | 79.6 ↓ | 64.3 ↓ | 9.1 ↑ | 1.91 ↑ | 1.27 ↓ | 1.86 ↓ | 1.31 ↓ | 1.54 ↑ | 1.29 ↓ |
| 10-palus · SOLUTION | 20261028-SOLUTION-r2-88bfce8-v13-claude-opus-5-5.json | 2026-10-28 | 88bfce8 | 89.5 | – | 89.5 | – | 0.0 | 2.00 | 1.50 | 2.00 | 2.00 | 1.50 | – |
| 10-palus · SOLUTION | 20261028-SOLUTION-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 88.0 ↓ | 78.6 | 84.8 ↓ | 75.0 | 0.0 = | 1.96 ↓ | 1.44 ↓ | 1.96 ↓ | 1.67 ↓ | 1.48 ↓ | 1.50 |
| 10-palus · SOLUTION | 20261030-SOLUTION-r2-fcec453-v13-claude-opus-5-5.json | 2026-10-30 | fcec453 | 86.5 ↓ | – | 86.5 ↑ | – | 0.0 = | 2.00 ↑ | 1.47 ↑ | 2.00 ↑ | 1.69 ↑ | 1.47 ↓ | – |
| 13-aircaps · COMMERCIAL | 20261028-COMMERCIAL-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 86.8 | – | 86.8 | – | 0.0 | 2.00 | 1.73 | 2.00 | 1.67 | 1.27 | – |
| 13-aircaps · COMMERCIAL | 20261028-COMMERCIAL-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 87.2 ↑ | – | 87.2 ↑ | – | 5.6 ↑ | 1.94 ↓ | 1.56 ↓ | 2.00 = | 1.50 ↓ | 1.67 ↑ | – |
| 13-aircaps · COMMERCIAL | 20261030-COMMERCIAL-r2-fcec453-v13-claude-opus-5-5.json | 2026-10-30 | fcec453 | 85.7 ↓ | – | 85.7 ↓ | – | 14.3 ↑ | 1.91 ↓ | 1.71 ↑ | 1.95 ↓ | 1.29 ↓ | 1.57 ↓ | – |
| 13-aircaps · PROBLEM | 20261028-PROBLEM-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 84.9 | 86.8 | 85.6 | 70.0 | 5.6 | 2.00 | 1.44 | 2.00 | 1.31 | 1.78 | 1.40 |
| 13-aircaps · PROBLEM | 20261028-PROBLEM-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 84.2 ↓ | 86.5 ↓ | 84.8 ↓ | 87.5 ↑ | 5.3 ↓ | 2.00 = | 1.53 ↑ | 1.95 ↓ | 1.47 ↑ | 1.47 ↓ | 1.75 ↑ |
| 13-aircaps · PROBLEM | 20261030-PROBLEM-r2-fcec453-v13-claude-opus-5-5.json | 2026-10-30 | fcec453 | 84.6 ↑ | 79.4 ↓ | 82.8 ↓ | 60.0 ↓ | 5.3 = | 1.95 ↓ | 1.37 ↓ | 1.90 ↓ | 1.47 = | 1.63 ↑ | 1.20 ↓ |
| 13-aircaps · SOLUTION | 20261028-SOLUTION-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 89.6 | 83.0 | 87.6 | 78.6 | 0.0 | 2.00 | 1.64 | 1.93 | 1.64 | 1.57 | 1.57 |
| 13-aircaps · SOLUTION | 20261028-SOLUTION-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 88.9 ↓ | 87.5 ↑ | 88.5 ↑ | 83.3 ↑ | 0.0 = | 2.00 = | 1.68 ↑ | 2.00 ↑ | 1.56 ↓ | 1.64 ↑ | 1.67 ↑ |
| 13-aircaps · SOLUTION | 20261030-SOLUTION-r2-fcec453-v13-claude-opus-5-5.json | 2026-10-30 | fcec453 | 86.2 ↓ | 84.8 ↓ | 85.8 ↓ | 71.4 ↓ | 0.0 = | 1.96 ↓ | 1.54 ↓ | 1.93 ↓ | 1.58 ↑ | 1.61 ↓ | 1.43 ↓ |
| 17-expanse · COMMERCIAL | 20261028-COMMERCIAL-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 85.5 | – | 85.5 | – | 0.0 | 2.00 | 1.42 | 1.92 | 1.57 | 1.58 | – |
| 17-expanse · COMMERCIAL | 20261028-COMMERCIAL-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 88.3 ↑ | – | 88.3 ↑ | – | 0.0 = | 2.00 = | 1.50 ↑ | 2.00 ↑ | 1.60 ↑ | 1.68 ↑ | – |
| 17-expanse · COMMERCIAL | 20261030-COMMERCIAL-r2-9093d99-v13-claude-opus-5-5.json | 2026-10-30 | 9093d99 | 88.0 ↓ | – | 88.0 ↓ | – | 4.5 ↑ | 1.96 ↓ | 1.77 ↑ | 2.00 = | 1.56 ↓ | 1.46 ↓ | – |
| 17-expanse · PROBLEM | 20261028-PROBLEM-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 86.5 | – | 86.5 | – | 0.0 | 2.00 | 1.39 | 2.00 | 1.54 | 1.69 | – |
| 17-expanse · PROBLEM | 20261028-PROBLEM-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 84.6 ↓ | 77.0 | 81.9 ↓ | 75.0 | 5.0 ↑ | 2.00 = | 1.35 ↓ | 1.85 ↓ | 1.29 ↓ | 1.65 ↓ | 1.50 |
| 17-expanse · PROBLEM | 20261030-PROBLEM-r2-9093d99-v13-claude-opus-5-5.json | 2026-10-30 | 9093d99 | 85.4 ↑ | 81.2 ↑ | 84.1 ↑ | 70.0 ↓ | 0.0 ↓ | 2.00 = | 1.45 ↑ | 1.80 ↓ | 1.47 ↑ | 1.70 ↑ | 1.40 ↓ |
| 17-expanse · SOLUTION | 20261028-SOLUTION-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 89.5 | – | 89.5 | – | 0.0 | 2.00 | 1.50 | 2.00 | 2.00 | 1.50 | – |
| 17-expanse · SOLUTION | 20261028-SOLUTION-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-28 | f48f256 | 88.3 ↓ | 71.8 | 83.5 ↓ | 83.3 | 7.7 ↑ | 1.92 ↓ | 1.46 ↓ | 1.92 ↓ | 1.47 ↓ | 1.46 ↓ | 1.67 |
| 17-expanse · SOLUTION | 20261030-SOLUTION-r2-9093d99-v13-claude-opus-5-5.json | 2026-10-30 | 9093d99 | 84.9 ↓ | 83.3 ↑ | 84.5 ↑ | 83.3 = | 7.7 = | 1.96 ↑ | 1.54 ↑ | 1.85 ↓ | 1.50 ↑ | 1.50 ↑ | 1.67 = |
| 21-codyco · COMMERCIAL | 20261028-COMMERCIAL-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 88.2 | – | 88.2 | – | 0.0 | 2.00 | 1.50 | 2.00 | 1.00 | 1.75 | – |
| 21-codyco · COMMERCIAL | 20261029-COMMERCIAL-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-29 | f48f256 | 86.9 ↓ | – | 86.9 ↓ | – | 0.0 = | 1.95 ↓ | 1.57 ↑ | 2.00 = | 1.47 ↑ | 1.62 ↓ | – |
| 21-codyco · COMMERCIAL | 20261030-COMMERCIAL-r2-9093d99-v13-claude-opus-5-5.json | 2026-10-30 | 9093d99 | 81.3 ↓ | – | 81.3 ↓ | – | 17.4 ↑ | 1.87 ↓ | 1.61 ↑ | 1.96 ↓ | 1.40 ↓ | 1.22 ↓ | – |
| 21-codyco · PROBLEM | 20261028-PROBLEM-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 83.8 | – | 83.8 | – | 0.0 | 1.93 | 1.36 | 1.93 | 1.50 | 1.64 | – |
| 21-codyco · PROBLEM | 20261029-PROBLEM-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-29 | f48f256 | 85.3 ↑ | 78.6 | 84.0 ↑ | 75.0 | 0.0 = | 1.93 = | 1.36 = | 1.79 ↓ | 1.58 ↑ | 1.79 ↑ | 1.50 |
| 21-codyco · PROBLEM | 20261030-PROBLEM-r2-9093d99-v13-claude-opus-5-5.json | 2026-10-30 | 9093d99 | 88.4 ↑ | 76.6 ↓ | 84.8 ↑ | 70.0 ↓ | 0.0 = | 1.85 ↓ | 1.50 ↑ | 1.75 ↓ | 1.67 ↑ | 1.80 ↑ | 1.40 ↓ |
| 21-codyco · SOLUTION | 20261028-SOLUTION-r2-f7b0e05-v13-claude-opus-5-5.json | 2026-10-28 | f7b0e05 | 85.6 | – | 85.6 | – | 0.0 | 2.00 | 1.50 | 1.95 | 1.64 | 1.45 | – |
| 21-codyco · SOLUTION | 20261029-SOLUTION-r2-f48f256-v13-claude-opus-5-5.json | 2026-10-29 | f48f256 | 86.0 ↑ | – | 86.0 ↑ | – | 0.0 = | 2.00 = | 1.63 ↑ | 1.90 ↓ | 1.69 ↑ | 1.37 ↓ | – |
| 21-codyco · SOLUTION | 20261030-SOLUTION-r2-9093d99-v13-claude-opus-5-5.json | 2026-10-30 | 9093d99 | 85.1 ↓ | – | 85.1 ↓ | – | 5.6 ↑ | 2.00 = | 1.72 ↑ | 1.89 ↓ | 1.67 ↓ | 1.22 ↓ | – |
