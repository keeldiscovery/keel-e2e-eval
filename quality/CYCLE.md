A session told **"kick off the instruction set"** reads this file and nothing else: it is the whole quality cycle (spec 079).

# The quality cycle -- the runbook

The founder, 2026-10-28: *"When I say kick off the instruction set -- a costly one, maybe every week or whenever a key
change happens -- we run it, compare the score with the previous one, have an AI model infer what should be changed,
rerun it, and once we are satisfied that output becomes the homepage examples. Seamlessly. It should not come from
your memory: the framework should support all this."*

Everything the commands below read is committed under `quality/`: the entries, the scopes, the door, the bar, the weak
rule, the reader and the adviser (`quality/cycle.toml`); the rubric (`quality/RUBRIC.md`, `RUBRIC_VERSION`); the reader
and adviser prompts (`quality/readers/`); and **the founder's decisions** on what earlier cycles found
(`quality/decisions.toml`, spec 087 -- step 2). Run every command from the keel-e2e-eval checkout's root (the main checkout,
whose `runs/` holds the bundles), with `export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock` in the shell.
**Every walk, every reader call and every adviser call is paid and runs only on the founder's word**; nothing here runs
from `make eval`, `make unit`, the matrix, a checker or a schedule.

## Where things stand -- the four questions, answered from files

| Question | Read |
|---|---|
| What is the current score? | `quality/TABLE.md`'s head: *this cycle*, *the baseline*, *the bar* -- and the latest record in `quality/cycles/` |
| What changed? | the latest record's *Against the baseline* and *Against the previous cycle*; `TABLE.md`'s *Moved since the baseline* |
| What is proposed? | `quality/cycles/<record>-advice.md` beside that record (absent until step 3 is run) |
| What has the founder already decided? | `quality/decisions.toml`; the record's and the advice's *Decided before* |
| What is on the homepage? | `quality/BASELINE.md` (the cycle accepted last, its studies and score files) and keel-web `public/sample/index.json` |

`make quality-due` (free) says whether a cycle is due, and why (step 6).

## Step 1 -- the kick-off (`make quality-walk`, PAID)

```
KEEL_ANTHROPIC_API_KEY="$(...)" make quality-walk ENTRIES=default WHY="<why this cycle, in the founder's words>"
make quality-walk ENTRIES=default DOOR=host WHY="<...>"        # on the founder's own Claude Code, no key
make quality-walk DRY=1 ENTRIES=21-codyco SCOPES=PROBLEM WHY="dry"   # the plan only: runs nothing, free
```

- **What it does**: for each entry (`ENTRIES=default` is `cycle.toml`'s `entries`; or `ENTRIES=21-codyco,08-fresco`) and
  each scope (`SCOPES=`, default `PROBLEM,SOLUTION,COMMERCIAL` -- one entry is three studies, each judged on its own):
  `make down`, `make backtest ENTRY= SCOPE= DOOR=` (spec 062 / 066 / 071) on the keel-cloud and keel-web checkouts
  stack.toml names, as they stand, then `make read-screens RUN=<the new bundle>` (spec 078); at the end `make read-table
  BASELINE=1 CYCLE=<record>`. `BUILD=<cloud7>` refuses unless keel-cloud is checked out at that sha.
- **It refuses** (one sentence, exit 2, nothing run) without ENTRIES, without WHY, with a dirty keel-cloud checkout (a
  sha must name what was measured), on DOOR=keel without `KEEL_ANTHROPIC_API_KEY` in the shell, without the `claude`
  CLI (the readers' door, and DOOR=host's), on an entry keel-cloud has no back-test file for, or an unknown scope.
- **What it costs**: per study, one back-test (about $0.50 of Keel's AI on DOOR=keel; the founder's plan on DOOR=host,
  6-10 minutes) and one reading (about 60 reader calls on the founder's plan, Opus 5.5 medium, about $4 list-price
  equivalent by the 078 smoke's rate). Five entries x three scopes = fifteen studies, a few hours. The record says what it actually cost.
- **What it writes**: the bundles under `runs/` (ignored); one score file per study under `quality/scores/<entry>/`;
  `quality/TABLE.md`; and the **cycle record** `quality/cycles/<yyyymmdd>-<cloud7>.md` -- the why, the shas, the studies,
  the bundles, the score files, the head, the comparison with the baseline and with the previous cycle, the cost and the
  time. **Commit** the score files, `TABLE.md` and the record together (the command prints the `git add` line).
- **What it pins** (spec 082 FR-3): the keel-cloud and keel-web shas at kick-off (the record's name and header). A
  study walked on another sha (a merge landed mid-cycle) is recorded with its own sha, and the head says *keel-cloud
  moved mid-cycle: <a> -> <b> from <study>* -- named, never refused: a refusal mid-cycle would waste the paid walks
  before it.
- **The founder decides**: nothing yet -- he reads step 2.

## Step 2 -- the comparison (`quality/TABLE.md`, free)

- **What to read**: `TABLE.md`'s first three lines -- **this cycle** (score_pct, flagged_pct), **the baseline** (the
  same), **the bar** (90%) -- and under *this cycle* the walks (spec 082 FR-3: *N of M walks reached their end; K
  stopped early (study -- the step, each); their scores are of the screens served before the stop*, and a sha that
  moved mid-cycle): a cycle whose walks stopped is scored on fewer screens than a whole one -- then the weak rows with their fix location (the design's §1: registry row, shared file,
  code transform, no model) and *instead* lines, and *Moved since the baseline* (each row that moved, turned weak or
  mended, with its *instead* lines). The record's *Against the previous cycle* gives the per-study delta.
- **Decided before** (spec 087; the founder, 2026-10-29: *"all the decisions we made should be recorded so that the
  next time the cycle runs we don't show the same things and have to go through the decision again"*): the record
  matches every weak row against `quality/decisions.toml`, one `[[decision]]` per decision -- `id`, `cycle`,
  `proposals`, `row` (scope, audience, dimension, screen: a string, a list, or `*`; dimension `-` is a row with
  none), `fix` (the fix location as the cycle names it, or a free label for a product ask), `decision` (`taken` |
  `declined` | `held`), `spec` (on `taken`), `until` (`spec-merged` | `never` | a cycle id), `why` (his words), and
  `merged` once the coordinator writes it. A row whose `row` and `fix` match a decision is **snoozed** while its
  `until` holds -- `never` always; a cycle id through that cycle; `spec-merged` until `merged = "<cloud or web sha>"`
  is on the entry -- and is listed under **Decided before** (the decision's id, its word, its spec, its why) instead
  of *Weak rows*; the advise line counts only the rest. A `fix` matches when it is the row's category, names the file
  or phrase its fix location names (whole; `dimension-registry.json` is every `registry row`), or is `*`; a free label
  (*a third persona option*) snoozes nothing -- it is listed when declined, and the adviser reads it (step 3). `make
  unit` refuses a decisions file with a field missing, a word or an until not one of the three, or a row naming a
  scope, audience or screen the cycle does not score; `make quality-walk` refuses it before any paid step.
- **Command**: none (`make read-table BASELINE=1 CYCLE=<record>` rebuilds it, free, if needed).
- **The founder decides**: advise (step 3), rerun after a change he already has in mind (step 4), or accept (step 5).

## Step 3 -- the adviser (`make quality-advise`, PAID: one call per weak row)

```
make quality-advise CYCLE=quality/cycles/<record>.md DRY=1    # the prompts only, free
make quality-advise CYCLE=quality/cycles/<record>.md
```

- **What it does**: for each weak row, one bounded call (`claude -p --model claude-opus-5-5`, the judge's argv,
  `quality/readers/adviser.md`) handed the failing criteria with their anchors, the screens that failed with the
  readers' whys and *instead* lines, the fix location, and **the current text at that location** read from the
  keel-cloud checkout (the registry row's `founder` / `respondent` / `follow_up` block, or the instruction file's named
  section). It answers with one proposed edit: the new text, three sentences of why, and the rung (words / effort /
  split -- the design's §5 ladder).
- **Decided before** (spec 087): a weak row snoozed by `quality/decisions.toml` (step 2) is **not sent** and not
  counted; the advice page lists it at its end under *Decided before*, one line each, so the founder sees what was
  not advised and why (a taken decision whose spec has merged no longer snoozes: its row competed). When every weak
  row is decided, nothing is sent and nothing is written. The adviser's prompt carries, for its row, the declined
  decisions whose `row` matches (a `*` row matches every row) with their whys in full, as *what the founder has already
  said no to*; its answer names in `reopens` any it goes against, and such a proposal is **refused** and recorded by
  row naming the decision, as a special case is (spec 081 FR-6).
- **What it costs**: one call per weak row not decided before (an estimate: about $0.10 each on the founder's plan) and a one-word probe.
- **What it writes**: `quality/cycles/<record>-advice.md`. **Commit it.** It is **never applied**.
- **The founder decides**: which proposals to take -- and every proposal is decided: taken, declined or held.
  **After every walk-through with him, the coordinator adds his decisions to `quality/decisions.toml` before the next
  advise** (one entry per decision, his why in his words, the specs a taken one became), and **after every merge of a
  spec a decision names, writes `merged = "<sha>"` on that entry**, so the next cycle measures the fix and the row
  competes again. A taken proposal becomes a **keel-cloud spec** -- a registry row or
  an instruction file, with the spoken-form acceptance line where a respondent wording moves -- built, gated and merged
  like any other. An `effort` rung is a routing change (a keel-cloud spec too); `split` is a contract change.

## Step 4 -- the rerun (`make quality-walk` again, PAID)

- **When**: after the keel-cloud change of step 3 is merged and the checkout is at it (clean).
- **Command**: the same ENTRIES and SCOPES as the cycle being improved -- the record's *What the founder decides now*
  prints the exact line -- with a new WHY (e.g. `WHY="keel-cloud 151 took the Importance proposal"`).
- **What it writes**: a new record, compared with the baseline AND with the previous cycle (both deltas named).
- **The loop**: steps 2-4 until the founder is satisfied, or the table says the bar is met.

## Step 5 -- the acceptance (`make quality-accept`, FREE, on the founder's word only)

```
make quality-accept CYCLE=quality/cycles/<record>.md
```

- **What it does**: rewrites `quality/BASELINE.md` from that cycle's score files (the old one kept under
  `quality/baselines/<date>.md`), then builds the gallery from that cycle's bundles behind the readers' gate (`make
  gallery SCORES=quality/scores`, spec 063 amended): a bundle whose latest score file at the current rubric version has a
  flagged screen, or a score_pct under the bar, or no score file, is **refused by name**; the rest are built, one
  example per entry (the first passing scope in `cycle.toml`'s `[gallery] scope_order`), into keel-web's
  `public/sample` (`OUT=` elsewhere). A slug's `cover.jpg` is kept across the refresh.
- **What it prints**: the slugs refreshed, the slugs added and still missing a `gallery_names.toml` row or a cover, and
  **the sentence the keel-web refresh spec starts from**.
- **What it writes**: `quality/BASELINE.md` and `quality/baselines/` here (**commit them**); the snapshot in keel-web
  (committed there, by the keel-web spec below); the provenance file under `runs/gallery/` (never committed).
- **The keel-web side** is a keel-web spec per acceptance, light gate, in this shape -- never invented: (1) commit
  `public/sample` as `make quality-accept` wrote it; (2) for an added slug, its `instructions/gallery_names.toml` row (in
  keel-e2e-eval, attribution, launch-era words, today's status) and a 1200x800 `cover.jpg` (keel-web spec 103); (3)
  re-pin the example frames (light, dark, phone) and the example pages' copy pins; (4) deploy on the founder's word.

## Step 6 -- the cadence (`make quality-due`, free)

- **A cycle is due** when a registry or instruction change is merged in keel-cloud (`dimension-registry.json`,
  `inference-instructions/*.md`), when the routing table or a model changes (`model-routing.json`), or when a week
  (`cycle.toml` `[cadence] days`) has passed since the last record. `make quality-due` checks the three and says so.
- **Nothing runs by itself**: none of these events starts a walk. The founder kicks off, and his words are the WHY the
  record's header carries.

## Rules that do not move

- The thirteen bundles of 2026-10-24 are never scored and never enter a baseline or the gallery (walked before the
  screener, at scope ALL; spec 079 judgement call 0). The first cycle walks fresh, three scopes per entry.
- Scores of two rubric versions are never averaged or compared; a rubric change (`RUBRIC_VERSION`) means a new cycle.
- The bar and the weak rule live in `quality/cycle.toml`, held equal to `quality/rubric.py` (the commands refuse when
  they differ); a change is a commit, so every record names the bar it was held to.
- A row the founder has decided is not advised again while his decision holds (`quality/decisions.toml`, spec
  087); he reopens a declined one by editing its entry, never by the adviser asking again.
- The adviser proposes; a keel-cloud spec applies. `quality-accept` is local; the keel-web deploy is its own step.
