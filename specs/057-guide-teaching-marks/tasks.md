# Tasks 057

Built against keel-cloud-docs master `7b3cd84` (109, contract 22) and keel-web 086 **as built in parallel** in
`wt/keel-web-086` (read-only; the run was on its `afbf38b` plus its working tree). The test ids are 086's own:
`guide-report` and `guide-opener` (`TeachingSheet` over 080's `GuideSheet`), `button.guide-pill` with
`guide-pill-{report-read,report-fails,stage,explain}` and the dot `guide-pill-new`, `guide-band`, `guide-chapter`.
No assumption is left open.

- [x] T001 FR-1 / FR-3 `evals/guide_marks.py` **`GUIDE_MARKS_VERSION` 2**: G6 report sheet once (D44), G7 the
  Overview's two pills (D45), G8 two chapters (D43, D46), G9 the money pair by kind (D47), G10 an explainer under
  every question incl. *Your idea* (D27), G11 openers once in Vector order (D25), G12 no project word (D42, D48);
  `DESIGN_IDS`; a mark whose clips the manifest says are absent passes as **not applicable** (`Check.applicable`,
  the card's `not_applicable`); G3 reads `welcomeSeen` / `openersSeen` alone (contract 22 adds two flags).
  `MARKS_VERSION` stays 20; `instructions/marks.py` gains the Spec 057 paragraph (the changelog).
- [x] T002 `harness/vectors_screens.py`: `GuideTeaching` (served manifest, `vtt`, `pills`, `band`, `fields`,
  `primary_disabled`, `open_pill`, `band_skip`, `band_end`, `seek`, `wait_chip`), `normal_manifest`;
  `GuideWelcome(sheet=…)` reads the report / opener sheet, `absent(seen_key=…)`; `Corridor.frame()` gains `pills`,
  `openers`; `Answers.board()` gains `guide_pills`, `report_sheet`.
- [x] T003 FR-2 `evals/corpus_scenario.py` on every corpus journey (both profiles): `teaching_start` after the
  welcome, `opener` at each stage's first open, `explainer_band` on each stage's first question, `report_sheet`
  before the first report read, `overview_read` on each Overview read, `watch_line_failed` (local, the seam) after
  the final board, `stage_band` on each stage page, `captions_read` (all served vtts) before the score. On remote,
  chapter 2's chip and the line-failed end are skipped with `REMOTE_SEAM_WHY`.
- [x] T004 Acceptance 1: `tests/test_guide_teaching_marks.py` (88): sheet-once faults, the two-pill table, chapter
  chip faults, the pair table, explainer / opener faults, the word-guard table, the manifest shapes, today's and
  nothing-rendered not-applicable cards, 086's ids against keel-web's files (skip before 086).
- [x] T005 Acceptance 2, the stack (below). Acceptance 3 `make unit` (below; this repo has no `make check`).

## Judgement calls

1. **G12 reads the served URL** (`/guide/<key>.vtt` for every present key); the unit test also reads keel-web's
   checkout. Only the words found are kept in the record, not the text.
2. **G10's band runs once per stage** (its first question). The primary is already off before an answer is picked,
   so the band is held to *disables while open, as before after*, and the proof is the fields: hidden while open
   (0), back after (086 hides the field rather than disabling it).
3. **G8 / G9 are applicable only when both chapters are present**; Will they pay's pair is chosen from the entry's
   kind (`vs.is_b2b`), so a page playing the other pair fails G9.
4. Insights' second pill (086 FR-6) is not read: G7 is the Overview's.

## Discovered

- **D-01** `_playing` (054 call 8): the welcome face went `readyState` 1 -> 4 inside the 600 ms read with the clock
  still 0 and failed; now the clock is owed a move only when the first read could already play. One table row.
- **D-02** `stack/vite.eval.config.ts` allows a worktree's linked `node_modules` (`server.fs.allow`): keel-web 086's
  worktree links the main checkout's, and the client failed to hydrate (no login screen).
- **D-03** the snippet half of G12 read **0** snippet texts on the stack (the bands' and sheets' snippet slot is
  empty at the moment it is read); the captions half read all 26 vtts. keel-web 086 FR-10's own unit test greps the
  snippet sources.
- **D-04 (risk, not in scope)** the preludes (`MarketStep.start`'s pass-by) pass the welcome only: a non-corpus
  journey that opens a stage or the report on keel-web 086 will meet an opener or the report sheet over its page.

## Measured (2026-10-20)

**Stack, S-005 countly** (`COMPOSE_PROJECT_NAME=keel-e2e-eval-057`, cloud 18082 / web 5183 / oidc 18092, postgres
55432 as the compose file fixes it; **stack.toml's `keel_web` pointed at `../../wt/keel-web-086` for the run and put
back, not committed**): `make eval K=s005` **1 passed in 286 s** (`runs/20261020T203648Z-s005-countly`), chromium.
Guide marks **12 of 12**, none unmeasured, **none not applicable** (all 26 clips present): one `{report: true}` 204,
no sheet on 3 later reads; *When a line fails* fresh, played to its end, one `{lineFailed: true}` 204, the dot gone;
chips *1 of 2* then *2 of 2* on all three stage pages, the b2c money pair; the band on Prevalence, Compatibility and
Existing sacrifice (fields 5 -> 0 -> 5); `openersSeen` PROBLEM, SOLUTION, COMMERCIAL; 26 vtts, no project word. Two
runs before were red on D-02 and D-01, a third on G10's first reading (call 2).

**`make unit`** (keel-web at the 086 worktree, ports put back): **2,709 passed / 53 skipped** against master's
2,620 / 53 (+89: 88 new, 1 `_playing` row). Against keel-web master the seven checks of 086's files skip (not run).
