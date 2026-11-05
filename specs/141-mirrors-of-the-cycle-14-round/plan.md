# Plan 141 -- Mirrors of the cycle 14 round

Branch `spec-141` (worktree `/Users/athulrajeev/Documents/projects/wt/eval-141`, `.git` a file), off master `245d398`.
Read only: keel-cloud-docs master `0844a180` (219, 228, 220, 224, 221, 226, 227, 222, 225 merged; each spec's tasks.md
"Owed" section is the list of record) and branch `spec-223` for 223's owed list (`git show spec-223:...`). 229 is a spec
file alone on master (223 merged at `d019f1ca` while this branch was built; 229 builds on `spec-229`). keel-web master
`480463e1` (178 built: its tasks.md "Owed" section). No stack, no model, no walk, no paid call, no key read; the unit suite only. The corpus yaml,
`quality/decisions.toml` and `RUBRIC_VERSION` untouched. Master red on nine (spec 140's gate): the three cards-digest
pins and six that read keel-cloud's `build/spoken-corpus.txt`, rewritten after 198 for the first time since (the
skips by record age no longer apply), so the pins meet 198's and 221's served words.

## Where each FR lands

| FR | Where |
|---|---|
| FR-4 Commitment (221) | `instructions/spoken.py`: `STEP_OPTION_MAX_WORDS` 11, `STEP_MAX_WORDS` 9, `first_yes` (cut at nine), `step_cut`, `_second_step` (eleven less the frame, `smaller_said`), `opens_on_its_act`, `smaller_act`, `restates_the_step`, `commitment_answers` reads it; 129's cut kept by spec number for older locks (`first_yes_before221`, `second_yes_before221`) in `served_labels`. `instructions/step_cost.py` `DATA_ACTS`. `harness/vectors_script.the_step` (an act-first step said as its act). `instructions/brief_facts.py` the soft yes through `smaller_said`. `instructions/marks.py` revision 16's note retired. Pins: `test_instruction_spoken`, `test_cloud_198_mirror_130`, `test_cloud_211_mirror_133` (the priced entries gain Countly, Expanse, Cubic). |
| FR-5 Prevalence (224) | `instructions/wording.py` `packed_fault` after 212's checks: `STATE_VERBS` / `STATE_FORMS`, `VERDICT_WORDS` (every tense), *have to* at the head allowed. `harness/vectors_script.PROBLEM_CLAUSES["06-repeatline"]` reworded off *by hand*. `tests/test_cloud_212_mirror_136.py` green. |
| FR-2 Relative advantage (219) | `instructions/spoken.py` `hard_case` / `advantage_stem` (*Think of {hard_case}.* first, *the last time* said *the most recent time*); `instructions/corpus.py` `ADVANTAGE_BELIEF_TEMPLATE` / `advantage_belief` (`{hard_case_theirs}`); `harness/vectors_script.py` the scripted PROBLEM_INTERPRET clause fields and Prevalence's two, the gate on the card's clause. |
| FR-3 Price (220) | A test only: the walked Price question and belief name the idea where the study holds a name. |
| FR-6 Current solution (226, 228) | `evals/corpus_scenario.py` reads `lineAfter` beside `line`; the walk leaves the line; the golden fake's Countly / Linerly ladders take one W-rung repair turn (any count allowed); `brief_facts.current_solution_bar` stands. |
| FR-7 Existing sacrifice (222, 227) | `instructions/chain.py` `cost_said` / `cost_belief` (the count frame, the typed unit, the consumer unit), `equation_per_drawn` and `evals/corpus_scenario.chain_words_owed` stop banning *per {unit}* beside a percent; `harness/vectors_script` the scripted part-1 `loss_clause`, `cost_question` / `cost_item` take the clause's frame. |
| FR-8 Importance, Compatibility (223, 225) | `harness/vectors_script.py` `kind` beside `settled_by` on the scripted Compatibility rows; `instructions/spoken.condition_kind` / `corpus._tested_kind` read a written kind; `instructions/score.settled_faults`; the notes as served fields the walk leaves alone; 223's own rows (on its branch, not master: mirrored only where master's tests stay green; else named open). |
| FR-8 keel-web 178 (the coordinator's addition, 2026-11-05) | `harness/vectors_screens.Corridor._list_rows`: a row's `[data-testid=row-note]` its own `note` (a locked row's too), `warn` the reword line alone; the line's words and `data-line` inside `line-control`, left where drawn. `evals/backtest.READ_JS`: a Choose option's `note` by its `-note-` describedby id, `row_notes` apart from the rows' words. `evals/corpus_scenario.chain_fill`: *Per* arrives empty. `chain.equation_per_drawn` / `chain_words_owed` as FR-7. |
| FR-1 the digest | `quality/readers/dimensions.md` = keel-cloud master's `src/main/resources/keel/dimension-cards.md`, last; the three digest pins read the cloud's `CARDS_SHA256`. |
| FR-9 the gate | `set -o pipefail; make unit 2>&1 | tail -1`, tasks.md. |

Order: FR-4 (it turns six of the nine green), FR-5, FR-2, FR-3, FR-6, FR-7, FR-8, FR-1, the gate. One commit per FR,
the branch pushed after each.
