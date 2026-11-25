# Tasks -- spec 171

Base: `origin/master` `5f7fd25` (170 merged; spec 171 committed). Built 2026-11-25 by a builder (Claude Opus 5.5) in
the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-171`, branch `171-the-judge-reads-the-told-card`.
Nothing paid: no model, no key, no vendor, no stack, no pip install (the main checkout's `.venv`, symlinked, ignored), no
network but `git fetch` / `git push` of this branch. The wire read from keel-cloud-docs master `2606b07a` (keel-cloud 281
merged, contract 95: `BriefFacts.problem.told` = `ExperienceTold`, `InvitationDetail.experience` = `ExperienceBoxes`;
`git show master:canon/openapi-v2.yaml`, read-only); the screens' test ids from keel-web 273's spec
(`/Users/athulrajeev/Documents/projects/keel-web/specs/273-hear-the-interview/spec.md`, read-only; 273 not yet on
keel-web master `04773133` when this was built).

- [x] T0 Set up: the worktree's `.venv`, the base's `make unit` (the reds listed below), this file.
- [x] T1 FR-1 the ground truth: `harness/film_told.py` (new) -- the stub strangers' stories from the walk (`film.json`
  `strangers.walks`, the bundle's `plans`), the founder's board from the problem film's `story.json` (`act` / `steps`,
  `limits[]`, `cost`), one told-reader call a story (`quality/readers/told-reader.md`, `truth` part; the film reader's
  `[film_reader]` model through its door), the answer parsed (the limitations described by index, the way and the pain
  same / differs / none, a real occasion or a guess), `told_truth.json` written beside `film.json`; `DRY=1` the prompts.
- [x] T2 FR-2 the told card captured: `harness/film_strangers.founder_page_after` on a PROBLEM project reads the wire
  (`standings.facts.problem.told`, each teller's `GET invitations/{id}` `experience` / `anchoring`, the story's
  `limits`), the page as drawn (Insights -> `insights-view-problem` -> `told-card`: its text and screenshot) and three
  people's popups (`row-open` -> `popup-tab-insights`: the first with a hit, the first with a new row, the first guess,
  where they exist); kept in the strangers' record (`film.json` `strangers.told`) and the bundle (`founder_page.told`).
  The comparison against the truth: per person the ticks, the way and the pain; per card the counts and bands
  recomputed from the truth; the verdict.
- [x] T3 FR-3 / FR-4 the four criteria and the table: `quality/FILM-RUBRIC.md` *The told card (the told-reader)* T1-T4
  (`film-told` markers); `quality/film_rubric.py` (`T_CRITERIA`, `told_summary`, the score file's `told` validated, the
  weak rule over T1-T4); T1-T3 code's over the comparison (T3's rows placed by the told-reader's card call), T4 the
  told-reader's; `told_pct` under `told` in the problem film's score file beside `founder_pct`, never in `film_pct`;
  `make read-films` writes it (`TOLD=0` skips); `quality/film_table.py` the `told` column after `founder_pct`, the T
  lines in each entry's whys, the comparison's moves; DRIFT: a T1 / T2 at 0 one finding a person / row with both
  readings, an absent card *(capture): no told card*.
- [x] T4 FR-5 the tests: `tests/test_the_judge_reads_the_told_card_171.py` (the truth file from a fixture walk,
  payroll; T1-T4 on a card that matches, one off and wrong; `told_pct`; the table column; the DRIFT line; the absent
  card); `make unit` after, no new red.
- [x] T5 FR-6 and this file: nothing here writes respondent words; how each FR is met, the judgement calls, `make unit`
  before and after, the commits, open.

## How each FR is met

| FR | Where | What holds |
|---|---|---|
| FR-1 | `harness/film_told.py` (`board_of`, `stories_of`, `truth_prompt`, `parse_truth`, `truth_card`, `write_truth`, `load_truth`, `band`, `verdict_of`); `quality/readers/told-reader.md` (`truth`); `harness/film_strangers.walk_summary` (`story`); `quality/film_reader.read_told` | every stub stranger who told a story on the film's link (the walk's `story`, else the screens bundle's `plans`; a chip, a gate No, no words: none) is read in one call through the film reader's door (`[film_reader]`, text only, `quality.readers.ask_twice`'s once-more on a fault), from the story alone against the founder's board (the problem film's `story.json`: `act` / `steps`, `limits[]` numbered, `cost`): the limitations described (1-based in, kept 0-based as keel-cloud 281's `limitsHit`), its own, the way and the pain `same` / `differs` / `none`, `real` / `guess`, a why. Code adds the card the truth makes (keel-cloud 281's bands over the real occasions). `told_truth.json` beside `film.json`, written once (a second read reuses it); `DRY=1` writes the prompts |
| FR-2 | `harness/film_told.py` (`capture`, `wire_people`, `card_on_screen`, `popup_on_screen`, `sample`, `READ_JS`, `compare_people`, `compare_rows`, `theirs_rows`, `compare_verdict`); `harness/film_strangers.founder_page_after(walks=)`; `evals/run_film.strangers_leg` | on a PROBLEM project after the answers: `standings.facts.problem.told`, each person's `GET invitations/{id}` (`experience`, `anchoring`), the story; Insights -> `insights-view-problem` -> `told-card` (its words, its `data-*` parts, an element screenshot in `<evidence>/told/`); Sent -> the row's `row-open` -> `popup-tab-insights` for the first with a hit, the first with a new row, the first guess (distinct people; none existing, the first story read). Kept in `film.json` `strangers.told` and the bundle's `founder_page.told`; never a stop. Compared: per person the ticks (extra / missed), the way, the pain; per founder's row the count and band; the amber rows; the verdict recomputed |
| FR-3 | `quality/FILM-RUBRIC.md` (*The told card (the told-reader)*, `film-told` markers, the weak rule, *Versions*); `quality/film_rubric.py` (`T_CRITERIA`, `TOLD_VERSION`, `prompt_told`, `criteria("told")`, `told_pct`, `validate_told`, `weak_criteria`); `harness/film_told.py` (`t1`, `t2`, `t3`, `drawn_notes`, `card_request`, `parse_card_answer`, `score`, `absent`, `absent_block`); `quality/film_reader.py` (`read_told`, `--no-told`, `told` / `told_cost_usd` in the score file); `Makefile` (`TOLD=0`); `quality/film_table.py` (`told` column, `told_cell`, `told_lines`, `_measures`); `quality/FILM-TABLE.md` | T1 / T2 / T3 code's (0 off 2, one 1, more 0), T3 over the told-reader's placing of every amber row in the stories (and whether it rewords a founder's row), T4 the told-reader's (the card's and the popups' words and screenshots, code's notes on order / tag / band words / foot line); a why each, an instead under 2; `told_pct` = sum / 8 x 100 under `told`, beside `founder_pct`, never in `film_pct`; the table's `told` column right after `founder_pct` (`absent` / `--`), the T whys under the problem film, T1-T4 under the weak rule (`kind: told`) and in the comparison's moves. An absent card (no `told` served; served but not drawn) scores nothing (`told_pct` null) and is the capture note *(capture): no told card*; nothing is spent on it |
| FR-4 | `harness/film_told.drift_items`; `quality/film_table.findings` / `drift_text` (`TOLD_SPEC`, `TOLD_DOES`) | a T1 at 0: one finding a person whose ticks are off (*the truth -- the story describes limitations ...; Keel's reading -- ticked ...*), a T2 at 0: one a row off (*the truth -- k of n (BAND); Keel's reading -- k (BAND)*), headed *Both readings*, found by spec `171-the-judge-reads-the-told-card`, owed by keel-cloud 281 FR-1 / FR-3; `DRIFT=1` appends them |
| FR-5 | `tests/test_the_judge_reads_the_told_card_171.py` (new, 26) | the truth file from a fixture walk (payroll, four stories and a chip); the prompt; refusals; the stories' sources; the walk keeps the story said, never a tap; bands and verdict; the sampling; the capture on a page that draws nothing; nothing written by the capture; T1-T4 on a card that matches (100.0), one off (50.0, no DRIFT) and wrong (0.0, flagged, the DRIFT items with both readings); the card answer's refusals; the rubric's T table and the card prompt; `told_pct` in the score file and its validation; the absent card three ways; the table's column, cells, whys and DRIFT lines; the weak rule; the comparison; `make read-films` end to end on a stubbed door (1 film + 4 truth + 1 card calls, the truth reused on a second read), an absent card spending nothing, `TOLD=0`, the dry run; nothing paid |
| FR-6 | -- | nothing here writes a respondent's words: the truth reads the stories the walk said (the corpus's people's recorded words), the card's and the popups' words are keel-cloud's and keel-web's, the capture only reads (no POST / PUT); the told-reader's prompts are the judge's, never a stranger's |

## Constants (new)
- `harness/film_told.py`: `SPEC = "171"`, `TRUTH_FILE = "told_truth.json"`, `TOLD_VERSION = fr.TOLD_VERSION`,
  `T_CRITERIA = fr.T_CRITERIA`, `VIEW_PROBLEM_ID = "insights-view-problem"`, `VIEW_ANSWERS_ID = "insights-view-answers"`,
  `TOLD_CARD_ID = "told-card"`, `ROW_OPEN_ID = "row-open"`, `POPUP_TAB_INSIGHTS_ID = "popup-tab-insights"`,
  `STORY_FOLD_ID = "insights-story-fold"`, `CARD_TITLE = "What they told you"`, `BLOCK_HEADINGS = ("How they do it
  today", "Where it falls short", "What it costs them")`, `BAND_WORDS = {"MOST": "reinforced by most", "SOME":
  "mentioned by some", "NONE": "not mentioned"}`, `TAG_WORDS = {"MOSTLY_KNOWN": "Mostly what you knew", "HALF_NEW":
  "Half new", "MOSTLY_NEW": "Mostly new"}`, `FOOT_LINE = "Counted from what people told, not from a question"`,
  `THEIRS_HEAD = "Theirs, not on your board"`, `MATCHES = ("same", "differs", "none")`, `OCCASIONS = ("real", "guess")`,
  `SAMPLE_WHYS = ("the first with a hit", "the first with a new row", "the first guess")`, `ABSENT_WHAT = "(capture):
  no told card"`, `ABSENT_OWED`.
- `quality/film_rubric.py`: `T_CRITERIA = ("t1", "t2", "t3", "t4")`, `TOLD_VERSION = 1`, `_MARKERS["told"] = "film-told"`.
- `quality/film_reader.py`: `TOLD_PROMPT_PATH = QUALITY / "readers" / "told-reader.md"`.
- `quality/film_table.py`: `TOLD_SPEC = "171-the-judge-reads-the-told-card"`, `TOLD_DOES`, `FILM_DOES`.
- `FILM_RUBRIC_VERSION` stays **1**; `CARDS_SHA256` unchanged (`aec2abb9...` before and after: no card touched).

## Judgement calls
1. **`FILM_RUBRIC_VERSION` not bumped.** FILM-RUBRIC.md bumps on a change to a criterion, an anchor, the weak rule or
   `film_pct`; T1-T4 are new criteria in a block of their own beside `founder_pct` and the weak rule only gains them.
   A bump would make the five-run (`20261125T084949Z-film-walk`) and the trial on two untableable against the next
   paid walk (`load_films` / `BASELINE` refuse a mix), for no change in what F, S or R measure. So the told block
   carries its own `version` (`TOLD_VERSION` 1) and *Versions* says so; a file without `told` tables beside one with it.
2. **The board is the problem film's served story** (`story.json`: `act` / `steps`, `limits[]`, `cost`), not the entry
   yaml: keel-cloud 281's `limitsHit` indexes into that `limits[]`, so the truth and Keel's reading count over the same
   rows. The truth is still independent of Keel's *reading* (FR-1): it sees the story text and the board alone.
3. **T1-T3 are code's, T4 the reader's.** T1 / T2 are exact comparisons the spec spells out; T3 needs meaning (which
   stories say an amber row, whether it rewords a founder's row), so the told-reader's card call places each amber row
   and code scores T3 from that placing; T4 is a reading. The whys and insteads of T1-T3 are composed by code from the
   comparison. One card call for T3 + T4 (not one a criterion).
4. **T1 compares the served `experience`, the screens are evidence.** keel-web 273's popup markup is not pinned by its
   spec beyond the tab ids, so the popup and the card are read whole (words, `data-*` parts, element screenshots) and
   handed to the told-reader for T4; T1's ticks are the served `limitsHit` the popup draws from. *Within one person*
   (T2): a row holds where its count is within one of the truth's and its band is one a count within one gives.
5. **The verdict** is compared (`verdict`: Keel's, the truth's, holds) but not a criterion: the truth's is recomputed
   from the truth's rows and the amber rows the told-reader placed in two or more stories. The tellers' counts (Keel's
   ANCHORED vs the truth's real occasions) are recorded beside it.
6. **Absent, three ways.** No `told` served where a story was told (keel-cloud before 281), or served and not drawn
   (keel-web before 273, no `insights-view-problem`): scores nothing, DRIFTs *(capture): no told card*. No story told,
   a walk before 171 (no capture) or a capture that stopped: scores nothing, no DRIFT (nothing owed by the product).
   An absent card spends nothing (the truth is not read).
7. **Sampling distinct people.** The first with a hit, then the first *other* person with a new row, then the first
   other guess; none existing, the first person whose story was read.
8. **The truth is written at `make read-films`**, not on the walk: the walk calls no model (the free walk stays free);
   the reader's door is the film reader's (`[film_reader]`, the Anthropic API) as FR-1 says (*the film-reader's model*).
9. **The committed `quality/FILM-TABLE.md` re-rendered** for the new column with this code from the five-run's score
   files and the main checkout's `runs/20261125T084949Z-film-walk` (read-only), `BASELINE` the trial on two as it was:
   the diff is the `told` column (`--` on every row: no score file carries `told` yet) and its sentence alone. The
   cycle record `quality/cycles/20261125-c7079b5-film.md` is not rewritten.
10. **`make unit` on archived siblings**, as 170: this worktree's `stack.toml` (never committed; restored) pointed at
    the scratchpad's `sib171/` (keel-cloud-docs master `2606b07a` by `git archive`; keel-web `04773133`, keel-runtime
    `3988131`, keel-connect-skill `c677950` from 170's `sib170/`). The keel-cloud Gradle gate and the sibling
    checkouts untouched.
11. **The table's rule line**: 166 drew one column too many under the header; with `told` added it is exact again (the
    same `+ 13`).

## make unit
Both on the same archived siblings (judgement call 10), the main checkout's `.venv`:
- Before (the base `5f7fd25` + T0's tasks.md; 17:10-17:18 ET): **79 failed, 6228 passed, 169 skipped** -- the same 79
  by name as 170's final run.
- After (`c7c00b3` less a no-op tidy of the solution's strangers record; 17:21-17:28 ET): **79 failed, 6254 passed, 169
  skipped -- no new red** (the lists diffed by name: identical); the 26 new tests green. The 79 are the base's (the
  contract pins, the connect `VERSION`, the charge tables, the git-dependent 165/166 tests on non-git sibling copies,
  ...), none touched here.

## Commits
| Commit | FR | What |
|---|---|---|
| `bb9b209` | -- | this file's T0..T5 |
| `c7c00b3` | FR-1..FR-6 | the truth, the capture, the comparison, T1-T4, the rubric, the reader's prompts, the table, DRIFT, the tests |
| (this commit) | -- | this file: how each FR is met, the constants, the judgement calls, `make unit`, open |

## DRIFT
No new entry: no stack was run here, so no product red was met.

## Open
- **The acceptance on a paid walk** (the founder's word): the next `make film-walk` on a stack with keel-cloud 281 and
  keel-web 273, then `make read-films` (the truth's calls, one a story, and the card's call: about seven extra API
  calls a problem film) and `make read-film-table`. Nothing was run here.
- **keel-web 273 not on its master** when this was built: the ids are its spec's (`insights-view-problem`, `told-card`,
  `row-open`, `popup-tab-insights`); its inner markup is read whole. If 273 lands other ids, `film_told`'s constants move.
  The popup is found as the last `[role=dialog]` on Sent (`tr[data-invitation=...]` holds `row-open`).
- **The free walk's scripted runtime** (`DOOR=fake`, `own_ai`): it hands `EXPERIENCE_WAYS`; keel-cloud 281 folds that
  into `EXPERIENCE_GROUPS` and adds `EXPERIENCE_READ`. Their scripts on the free walk are not written here (no stack to
  try them on): on the fakes the told card may come back with nothing read, which the judge scores as it finds it.
- The base's 79 reds are not this spec's and are unchanged.
