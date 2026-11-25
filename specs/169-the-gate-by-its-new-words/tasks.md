# Tasks -- spec 169

Base: `origin/master` `9fa2d6f` (168 merged at `12e7804`, spec 169 committed). Built 2026-11-25 by a builder (Claude
Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-169`, branch
`169-the-gate-by-its-new-words`. Nothing paid: no model, no key, no vendor, no stack, no pip install (the main
checkout's `.venv`, symlinked, ignored), no network but `git fetch` / `git push` of this branch. keel-cloud 277's words
read from its spec (`keel-cloud-docs/specs/277-have-you-encountered-this-issue/spec.md`, read-only; the cloud build is
not on master yet): `story_gate` = *In {window}, have you encountered this issue?*, `{window}` filled by code
(*the last month*, *the last 7 days*), the same words on the solution link's uncounted check.

- [x] T0 Set up: the worktree's `.venv`, the base's `make unit` (the reds listed below), this file.
- [x] T1 FR-1 the gate found by its new words: `harness/three_surfaces.py` `GATE_WORDS` a case-insensitive regex on
  *have you encountered this issue?* with any window before it, the question mark optional, and `is_gate_words` /
  `gate_found`; `harness/interviewer_screens.py` and `evals/three_views_strangers.py` `GATE_WORDS` the same match;
  the readers (`evals/three_views_strangers.py`'s wire checks of the gate and the anchor, `harness/solution_surfaces
  .link_faults`' check) and the walks (the orb / face walk `link_walk`, the text walk `story_screens.StoryLinkText`)
  find the gate by that match; the strangers' plan answers it by `recency` as today; the one-script check (269 FR-8)
  compares the three surfaces' gate words to each other; the old words match nowhere.
- [x] T2 FR-2 `quality/FILM-RUBRIC.md` (F7) and `quality/CYCLE.md` quote the new words; no criterion moves,
  `FILM_RUBRIC_VERSION` stays 1; 168's DRIFT finding unchanged in code, `CYCLE.md` saying it is now a capture note on
  a study with no film only.
- [x] T3 FR-3, FR-4 the tests (`tests/test_the_strangers_on_the_films_link_165.py`, the surfaces tests, the solution
  tests): *In the last month, have you encountered this issue?* found and answered, the old words not; 168's
  READY-first test unchanged; `make unit` after; nothing here writes respondent words; this file's sections.

## How each FR is met

| FR | Where | What holds |
|---|---|---|
| FR-1 | `harness/three_surfaces.py` (`GATE_WORDS`, `is_gate_words`, `gate_found`, `gate_answer`, `same_gate`; `GATE_WORDS_BEFORE_277`, `GATE_EXAMPLE`); `harness/interviewer_screens.py` and `evals/three_views_strangers.py` `GATE_WORDS` (the same object); `evals/three_views_strangers.py` (`wire_checks`, `link_walk`, `four_questions_served`, `three_surfaces_check`, `solution_wire_checks`' words); `harness/solution_surfaces.link_faults`; `harness/story_screens.StoryLinkText._kind`; `harness/film_strangers.py` (docstrings) | `GATE_WORDS` is now the regex `(?:in\s+[^?,]+?,?\s+)?have\s+you\s+encountered\s+this\s+issue\s*\??` (`re.IGNORECASE`), held with `fullmatch` on the words with their spaces folded: *have you encountered this issue?* with any window before it (*In the last month, ...*, *In the last 7 days, ...*, the registry's *In {window}, ...*), the question mark optional; *Did this happen to you?*, 259's *In your last {window}, did this happen to you?* and a framed clause never match. The gate's wire checks (the problem link's gate, the solution link's anchor/check) hold the served question to the match; the orb / face walk (`link_walk`) and the text walk (`StoryLinkText`) find the gate on a film link by the match (`gate_found`; a link with no film keeps the framed clause, found as served) and answer it by the plan's gate, i.e. the person's `recency` (`gate_answer`, the same rule as before); the one-script check (269 FR-8) holds the orb's, the face's and the Copilot card's gate words to each other (`same_gate`: one wording on all three, and that wording found by the match), no constant |
| FR-2 | `quality/FILM-RUBRIC.md` F7, `quality/CYCLE.md` (the film walk's questions; a Spec 168 / Spec 169 note under the table), `quality/film.py` (docstring), `quality/film_table.py` (a comment) | the rubric and CYCLE.md quote *In {window}, have you encountered this issue?*; no criterion moves, `FILM_RUBRIC_VERSION` stays 1; 168's DRIFT finding (*(capture): the lock's calibration was written again on the founder's retry*) unchanged in code, CYCLE.md saying that since 277 it is a capture note on a study with no film only (on a film study it is the calibration writer's drift) |
| FR-3 | `tests/test_the_strangers_on_the_films_link_165.py` (five new tests, 18 cases), `tests/test_the_solution_walked_162.py` (one new), `tests/test_the_solution_film_judged_166.py` (the solution plans' check), `tests/test_four_questions_161.py`, `tests/test_mirrors_of_258_164.py`, `tests/test_three_views_157.py` | *In the last month, have you encountered this issue?* (and the 7-day, no-mark, upper-case, no-comma, spaced, template and window-less forms) found; *Did this happen to you?*, 259's words, a framed clause, a longer sentence, another prefix, empty and None not; on a film link the gate found and answered *yes* / *no* by `recency` (and *no* on `no_on="gate"`), the old words not found even where served; a link with no film finds its framed clause as served and not the new words; `same_gate` same / different windows / old words / a surface missing; every reader's `GATE_WORDS` the one object; the solution link's check clean on the new words and faulted on the old; the fixtures carry 277's example where they carried 269's words; the registry mirrors (161, 157) hold `story_gate` to the match and skip *keel-cloud before 277* while the sibling still says 269's words. 168's READY-first test (`test_a_calibration_ready_the_first_time_presses_no_retry`) unchanged and green |
| FR-4 | -- | the stub founder's and the strangers' words untouched; the gate's words are read from the wire. `GATE_EXAMPLE` is keel-cloud 277's acceptance example for the fixtures only, sent nowhere |

## Judgement calls
1. **The regex's reach.** The prefix is optional (*Have you encountered this issue?* alone matches): 277 always fills a
   window, but a window-less wording is still the gate's words and the spec asks for the words "with any window before
   them", not for a window. A prefix must start with *In* and end before the words (a comma optional); anything after
   the words (a second sentence) does not match, so a framed clause or a gate with words added reads as not found.
2. **Film link vs no film.** The walks find the gate by the match only on a link that serves the film (`story`); on a
   link with no film keel-cloud 277 keeps the framed clause (*In {window}, did you ...?*), which the match must not
   take, so there the gate is found as served (`gate_found`). The older walkers that match the served question
   (`evals/interviewer_leg.py`, `evals/corpus_scenario.py`, `evals/backtest.py`) are wire-driven, pin no words and
   are left as they are.
3. **`GATE_WORDS` stays the name**, now a compiled pattern (the spec: *"`GATE_WORDS` becomes a match"*); the string
   constant of 269 is kept as `GATE_WORDS_BEFORE_277` for the negatives and the registry mirrors' skip, and the fixtures
   use `GATE_EXAMPLE`.
4. **The registry mirrors skip before 277** (the sibling's `story_gate` still 269's on the archived `a64bde86`), as
   the earlier mirrors skip *keel-cloud before 269*; once 277 merges they assert the match and the `{window}`
   placeholder.
5. **`quality/readers/dimensions.md` left as it is.** Prevalence's card says the fixed words *Did this happen to you?*
   (the readers' cards); it is pinned by `CARDS_SHA256` (spec 162) and keel-cloud 277 FR-5 re-cuts its own
   `dimension-cards.md` Prevalence card in words this spec does not have. Changing it here (tried, then reverted) reds
   `test_the_cards_digest_is_the_one_spec_162_moved` and could part from the cloud's card; it is outside FR-2 (the
   rubric and CYCLE.md only). Named under Open.
6. **The DRIFT finding unchanged in code** (the brief: *168's DRIFT finding unchanged*); FR-2's "now reads as a capture
   note on a study with no film only" is said in CYCLE.md and the constant's comment.
7. **`make unit` on archived siblings**, as 168 (its judgement call 6): this worktree's `stack.toml` (never committed;
   restored) pointed at the scratchpad's `git archive` copies (keel-cloud-docs `a64bde86`, keel-web `e732c7b6`,
   keel-runtime `3988131e`, keel-connect-skill `c6779509`); the keel-cloud Gradle gate beside me and the sibling
   checkouts untouched.

## make unit
Both on the same archived siblings (judgement call 7), the main checkout's `.venv`, nothing else of mine running:
- Before (the base `9fa2d6f` with this file only, before any code change; 08:08-08:15 ET): **79 failed, 6191 passed,
  171 skipped** -- the same 79 by name as 168's base and head.
- After (`28402c6`; 08:17-08:24 ET): **79 failed, 6209 passed, 173 skipped -- no new red** (the lists diffed by name:
  the same 79). The two new skips are the registry mirrors (161, 157), *keel-cloud before 277* on the archived
  `a64bde86`; the new mirrors green.
- `tests/test_the_strangers_on_the_films_link_165.py`, `tests/test_the_solution_film_judged_166.py`,
  `tests/test_four_questions_161.py`, `tests/test_three_views_157.py` and `tests/test_the_mirrors_of_263_167.py` on the
  `git init` sibling copies (`sibgit`, as 168): **178 passed, 3 skipped, 2 failed** -- the two contract-87 / credits
  reds of the base (`test_contract_87_is_the_one_the_walk_reads`, `test_a_free_reading_that_moved_credits_is_named`),
  the git-dependent five green.

## Commits
| Commit | FR | What |
|---|---|---|
| `c72234d` | -- | this file's T0..T3 |
| `28402c6` | FR-1..FR-3 | the gate's match and its helpers, every reader and walk on it, the one-script check to each other, the rubric / CYCLE.md / film.py words, the mirrors |
| (this commit) | FR-4 | this file: how each FR is met, the judgement calls, `make unit`, open |

## DRIFT
No new entry: no stack was run here, so no product red was met.

## Open
- **The acceptance on a stack** (*every entry's problem leg sends its link with no `LockFailed` at step 2*) waits on the
  next paid walk on Keel's door (the founder's word) on a keel-cloud with 277 merged; until 277 is deployed a walk
  meets the old words, and the gate's wire checks and the walks will fail on them by design (FR-1).
- **Prevalence's card in `quality/readers/dimensions.md`** still says the film's gate is *Did this happen to you?*
  (judgement call 5): once keel-cloud 277's `dimension-cards.md` lands, re-cut the card's sentence, `CARDS_SHA256`
  and `CARDS_MOVED_162` (or vendor the cloud's card) in a small spec, before the next paid read of §A.
- The registry mirrors (161, 157) assert the match only once the sibling has 277's registry; on today's archived
  siblings they skip.
