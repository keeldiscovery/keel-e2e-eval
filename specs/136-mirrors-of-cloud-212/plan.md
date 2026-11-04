# Plan 136 -- Mirrors of keel-cloud 212: one event, the act that hurts

Branch `spec-136` (worktree `wt/keel-e2e-eval-136`, `.git` a file), off `786ab2e` (the spec). Read only: keel-cloud-docs
master `55bf014d` (212 merged: `specs/212-one-event-the-act-that-hurts/{spec,plan,tasks}.md`, `founder-lists.md`,
`respondent-questions.md`, `dimension-cards.md`, `dimension-registry.json`, `WindowFrame.eventMaxWords` / `packedFault`
/ `routineFault`, `ScreenResultApplier.actThatHurts` / `settledRows`, `RespondentQuestionsRules` E10). No stack, no
model, no walk, no reader, no paid call, no key read; the unit suite only. Master red on the two pins the spec names
(5,354 passed / 2 failed / 85 skipped at `786ab2e`).

## Where each FR lands

| FR | Where |
|---|---|
| FR-1 the cards | `quality/readers/dimensions.md`: the two *One clause (keel-cloud 212)* bullets, byte for byte as the vendored copy carries them (Prevalence's after its fixed answers, Frequency's after its options), so the 133 pin holds at `CARDS_SHA256` `877a5d80...`; the 133 pin's docstring names the digest. `tests/test_seven_templates_115.py`: `FREQUENCY_GUIDANCE_212` (the registry's new Frequency founder guidance), 205's kept as `FREQUENCY_GUIDANCE_205`. |
| FR-2 the mirrors | `instructions/wording.py`: `event_max_words(window)` (20 less *In {window}, {on/in} how many {unit} did you*), `CLAUSE_MAX_WORDS` 25 (code's and the respondent writer's clause), `event_fault(event, window, max_words=None)` (the cap the window's, Java's message), `packed_fault` (E8), `routine_fault` (E7, with `base_of`, `WindowFrame.baseOf`), `SETTLED_BY`. `instructions/score.py`: Prevalence's `routine` / `went_wrong` (E7 missing), E7, E8 and E2 at the window's cap in `calibration_checks` (the actor_plural read off the sent context or the entry); `L35` on Compatibility in `list_faults`; `respondent_checks` takes `founders` -- with the founder's clause the gate is its key alone and a written `event` is `E10`, without it (`problem` null) the writer's clause keeps E1-E4 at 25 words; `score_respondent` reads `problem` off the sent context (else `context.problem_of`). |
| FR-3 the scripted results | `harness/vectors_script.py`: `ACT_THAT_HURTS` (the golden seven: `routine`, `went_wrong`, `event`), `PROBLEM_CLAUSES` follows it (the founder's clause within the window's cap, the strangers' clause its second person, as `WindowFrame.strangersEvent` turns it); `calibration_question` writes `routine` / `went_wrong`; `drafted_list` writes `settled_by: nobody` on every Compatibility row; `respondent_item` writes no `event` where the study holds the founder's clause (`gate_counts`). `tests/v9_fixtures.py`'s good answers likewise. |
| FR-4 the fourteen's clauses | `tests/test_cloud_212_mirror_136.py`: every golden and gallery entry's founder clause (`vs.event_past`, which `context.problem_of` hands the respondent job) counted against its window's cap; the golden seven held to it; the gallery's over-cap clauses pinned as findings (entry and count), never a failure. |
| FR-5 | `make unit` green on `55bf014d`; tasks.md. |

## Judgement calls

1. **The contract export is not vendored here.** `instructions/contract.py` asks keel-cloud's exporter at run time
   (`./gradlew screenContracts export`) and the tests write their own permissive export (`v9_fixtures.write_export`); no
   file in this repository carries the screen contracts' descriptions. Nothing to re-vendor; the run-time export reads
   212's descriptions (contract 25) with nothing edited here. Recorded as found, not built around.
2. **The golden seven's clauses are the eval's own (spec 064 FR-4a, COMPOSED), so FR-3 moves them** to fit the cap:
   five of seven were 10 or 11 words against 9; each is cut by its trailing words, the act and its object kept
   (Countly *by hand* off; ComplianceLog's *by hand*; Linerly *or from*; Paidly *approved*; Mulch Run *for a job*);
   Lullaby and Repeatline stand. `routine` and `went_wrong` are written per entry in the founder's words (the scripted
   writer's own, as `PROBLEM_CLAUSES` always was); E7 and E8 pass on each, held by test.
3. **The gallery's clause is the eval's stand-in**: a back-test entry records no founder clause (revision 24 records
   none), so `event_past` writes *had a time when {circumstance}* -- what `context.problem_of` hands the instruction
   eval's respondent job, and what the scripted writer would write. Those over the cap are FR-4's findings for the next
   corpus revision (the corpus should record the founder's `routine`, `went_wrong` and `event`); no back-test entry is
   walked on the scripted runtime (`make backtest` answers on Keel's AI), so none is served this clause.
4. **E10 is a fault in the eval's `option_validity`**: keel-cloud notes and ignores a served gate `event` where the
   founder's clause is held; the instruction says *write no event*, and the eval marks the instruction, so a written
   one is counted, by name. Without the founder's clause (`problem` null) the gate owes `event` (E2) and keeps E1-E4 at
   `CLAUSE_MAX_WORDS` (25), as `RespondentQuestionsRules.gate` holds the writer's clause; E4 holds the 20 spoken words.
5. **The respondent leak sweeps read what the writer wrote**: with no `event`, the stems are `[None]` as before, so no
   denominator moves (`MARKS_VERSION` stands).
6. **`L36`, `K11` and `Y7` are not mirrored** (212 FR-4's grammar guard on the served Compatibility question):
   212 names them owed by nobody here and the spec names only `settled_by`; the scripted rows' questions are the
   corpus's own faces.
7. **The missing fields are a fault, E7/E8/E2 too** -- the cloud breaches one (repair, then note) and throws the
   others; the eval's validity counts both as the instruction broken, as it does every L / C rule.
