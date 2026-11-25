# Tasks -- spec 171

Base: `origin/master` `5f7fd25` (170 merged; spec 171 committed). Built 2026-11-25 by a builder (Claude Opus 5.5) in
the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-171`, branch `171-the-judge-reads-the-told-card`.
Nothing paid: no model, no key, no vendor, no stack, no pip install (the main checkout's `.venv`, symlinked, ignored), no
network but `git fetch` / `git push` of this branch. The wire read from keel-cloud-docs master `2606b07a` (keel-cloud 281
merged, contract 95: `BriefFacts.problem.told` = `ExperienceTold`, `InvitationDetail.experience` = `ExperienceBoxes`;
`git show master:canon/openapi-v2.yaml`, read-only); the screens' test ids from keel-web 273's spec
(`/Users/athulrajeev/Documents/projects/keel-web/specs/273-hear-the-interview/spec.md`, read-only; 273 not yet on
keel-web master `04773133` when this was built).

- [ ] T0 Set up: the worktree's `.venv`, the base's `make unit` (the reds listed below), this file.
- [ ] T1 FR-1 the ground truth: `harness/film_told.py` (new) -- the stub strangers' stories from the walk (`film.json`
  `strangers.walks`, the bundle's `plans`), the founder's board from the problem film's `story.json` (`act` / `steps`,
  `limits[]`, `cost`), one told-reader call a story (`quality/readers/told-reader.md`, `truth` part; the film reader's
  `[film_reader]` model through its door), the answer parsed (the limitations described by index, the way and the pain
  same / differs / none, a real occasion or a guess), `told_truth.json` written beside `film.json`; `DRY=1` the prompts.
- [ ] T2 FR-2 the told card captured: `harness/film_strangers.founder_page_after` on a PROBLEM project reads the wire
  (`standings.facts.problem.told`, each teller's `GET invitations/{id}` `experience` / `anchoring`, the story's
  `limits`), the page as drawn (Insights -> `insights-view-problem` -> `told-card`: its text and screenshot) and three
  people's popups (`row-open` -> `popup-tab-insights`: the first with a hit, the first with a new row, the first guess,
  where they exist); kept in the strangers' record (`film.json` `strangers.told`) and the bundle (`founder_page.told`).
  The comparison against the truth: per person the ticks, the way and the pain; per card the counts and bands
  recomputed from the truth; the verdict.
- [ ] T3 FR-3 / FR-4 the four criteria and the table: `quality/FILM-RUBRIC.md` *The told card (the told-reader)* T1-T4
  (`film-told` markers); `quality/film_rubric.py` (`T_CRITERIA`, `told_summary`, the score file's `told` validated, the
  weak rule over T1-T4); T1-T3 code's over the comparison (T3's rows placed by the told-reader's card call), T4 the
  told-reader's; `told_pct` under `told` in the problem film's score file beside `founder_pct`, never in `film_pct`;
  `make read-films` writes it (`TOLD=0` skips); `quality/film_table.py` the `told` column after `founder_pct`, the T
  lines in each entry's whys, the comparison's moves; DRIFT: a T1 / T2 at 0 one finding a person / row with both
  readings, an absent card *(capture): no told card*.
- [ ] T4 FR-5 the tests: `tests/test_the_judge_reads_the_told_card_171.py` (the truth file from a fixture walk,
  payroll; T1-T4 on a card that matches, one off and wrong; `told_pct`; the table column; the DRIFT line; the absent
  card); `make unit` after, no new red.
- [ ] T5 FR-6 and this file: nothing here writes respondent words; how each FR is met, the judgement calls, `make unit`
  before and after, the commits, open.
