VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PLAYWRIGHT := $(VENV)/bin/playwright

.PHONY: up down eval eval-live eval-all report venv unit instruction-eval instruction-screen acceptance oidc-image \
        matrix-check keels-ai sample backtest gallery noise-check read-screens read-table \
        quality-walk quality-advise quality-accept quality-due

# Idempotent: safe to depend on from every other target. Re-run costs a few seconds once the
# venv already exists (pip/playwright no-op when nothing changed).
venv: $(PY)

$(PY):
	python3 -m venv $(VENV)
	$(PIP) install -q -r requirements.txt
	$(PLAYWRIGHT) install chromium

# PROFILE=playground boots/tears down the split-stacks playground profile (its own ports/volume,
# relay-design.md §12.5) instead of the default eval profile -- `make up PROFILE=playground`.
# PROFILE=remote (spec 017) starts nothing at all: `up` asks the three URLs named by
# KEEL_REMOTE_WEB_URL (and its two optional companions) whether they answer, and `down` is a
# no-op that says so.
up: venv
	$(PY) -m stack.cli up $(if $(PROFILE),$(PROFILE),eval)

down: venv
	$(PY) -m stack.cli down $(if $(PROFILE),$(PROFILE),eval)

# make eval K=s001 runs only that scenario; bare `make eval` runs every scenario module.
# PROFILE=playground attaches evals/conftest.py's own stack fixture to the split-stacks
# playground profile instead of the default eval profile -- `make eval K=s001 PROFILE=playground`
# (relay-design.md §12.5: two profiles never share ports, a database, or now a runtime home).
eval: venv
	KEEL_EVAL_PROFILE=$(if $(PROFILE),$(PROFILE),eval) $(PY) -m pytest evals -q -m "not live" $(if $(K),-k "$(K)",)

# make sample (spec 060; keel-cloud `canon/designs/landing-page-design.md` §18.11) runs S-006 on the local stack with
# the export on: the finished 05-paidly project at its twenty answers -- overview, plan, standings, roles, people,
# readings and every batch, invitations and every link, names kept (spec 061), emails, the founder and tokens
# withheld -- written as static JSON with a manifest.json into keel-web's `public/sample/` (the checkout stack.toml
# names) unless KEEL_SAMPLE_EXPORT names another directory.
# It refuses (exit 1, the reason named) unless the verdict is the corpus's own. **It writes into a sibling checkout**
# and commits nothing there: committing the snapshot is the operator's step, in keel-web. `make eval` never sets the
# variable, so the eval cell is unchanged.
#
#   make sample                                         into keel-web/public/sample/
#   make sample KEEL_SAMPLE_EXPORT=/tmp/sample          anywhere else
sample: venv
	KEEL_EVAL_PROFILE=$(if $(PROFILE),$(PROFILE),eval) \
	KEEL_SAMPLE_EXPORT="$(if $(KEEL_SAMPLE_EXPORT),$(KEEL_SAMPLE_EXPORT),$$($(PY) -c 'from stack.config import load_config; print(load_config(validate=False).keel_web / "public" / "sample")'))" \
	$(PY) -m pytest evals -q -m "not live" -k s006

# make gallery (spec 063; spec 106: three studies an example) exports the example gallery: for each entry, its three
# back-test run directories -- the problem, solution and money studies (SCOPE=PROBLEM, SOLUTION, COMMERCIAL), RUNS=<dir>[,
# <dir>...], each a path or a name under RUNS_DIR; default the newest finished `runs/*-backtest-<id>` of each study of
# every entry in instructions/gallery_names.toml -- the 060 file set each run's export/ holds, plus interview.json (the
# served interview per link, text only) and manifest.json, into OUT/<slug>/<problem|solution|money>/, and one
# OUT/index.json, B2B and B2C alternating, each row's top-level fields the problem study's and `studies: {problem,
# solution, money}` each study's own decision, howSure, pilot, price, answered and invited. An entry lacking one of
# the three studies (or given one twice, or a run of another scope) is refused by name and nothing is written for it.
# Since the amendment of record (2026-10-23) each example is a SIMULATED study attributed to the real company: nothing
# is renamed, and every index row and manifest carry inspiredBy, publicDescription (with URL and date), assumptions,
# simulated and the disclaimer, which says the study's own people in words (spec 106 FR-2: "seven people answered, all
# simulated") -- a slug missing any of them is refused, nothing written. Which run made which study is written once
# OUTSIDE OUT, to runs/gallery/provenance-<exportedAt>.json (PROVENANCE_DIR= overrides; never under OUT), and no entry id
# or run name may appear in any byte under OUT. A slug's cover.jpg and the row's title, image and tests (keel-web's own)
# are kept across the refresh. No stack, no model, no money.
# **It writes into a sibling checkout** when OUT is left out (keel-web's public/sample/, the checkout stack.toml names)
# and commits nothing there: committing the snapshot is the operator's step, with keel-web 100. The root
# public/sample/*.json of `make sample` is left as it is.
#
#   make gallery                                                  newest runs, into keel-web/public/sample/
#   make gallery RUNS=runs/<a>,runs/<b>,runs/<c> OUT=/tmp/sample  those runs (one entry's three studies), elsewhere
#   make gallery RUNS_DIR=/path/to/keel-e2e-eval/runs OUT=...      the newest runs of another checkout
# Spec 079 FR-6 / 106 FR-3: SCORES=quality/scores puts the readers' gate in front: a run whose latest score file at the
# current rubric version has a flagged screen (or that has no score file) is refused by name, and the runs' overall
# score_pct is held to the gallery's own last accepted one (the newest provenance file that records one): below it the
# export is refused and nothing is written; at or above, or with none yet, it is built and the score recorded. BAR=<pct>
# is an optional stricter gate (a run under it is refused), off by default; CYCLE=<record name> is recorded in the
# provenance. `make quality-accept` runs it so, from one cycle's bundles, with SCORES alone.
#   make gallery RUNS=runs/<a>,runs/<b>,runs/<c> SCORES=quality/scores OUT=/tmp/sample
gallery: venv
	PYTHONPATH=. $(PY) -m evals.gallery \
	  --out "$(if $(OUT),$(OUT),$$($(PY) -c 'from stack.config import load_config; print(load_config(validate=False).keel_web / "public" / "sample")'))" \
	  $(if $(RUNS),--runs "$(RUNS)",) $(if $(RUNS_DIR),--runs-dir "$(RUNS_DIR)",) \
	  $(if $(PROVENANCE_DIR),--provenance-dir "$(PROVENANCE_DIR)",) \
	  $(if $(SCORES),--scores "$(SCORES)",) $(if $(BAR),--bar "$(BAR)",) $(if $(CYCLE),--cycle "$(CYCLE)",)

# make backtest (spec 062) walks ONE BACK-TEST ENTRY -- a real founder's idea, written from public material in the
# corpus schema with no golden expectations, in keel-cloud's `canon/designs/measured-beliefs/backtest/<ENTRY>.yaml` --
# through `corpus_scenario.run` with `strict=False` (S-012's mode: nothing held to the file) ON KEEL'S AI, locally. The
# founder (*Backtest Founder*, backtest@keel-backtest.test, outside keel-cloud's `fake-for`) signs up through /signup;
# contacts, renders and the transcriber stay the stack's fakes, so nothing but model calls leaves the machine.
# It writes `runs/<stamp>-backtest-<ENTRY>/`: `backtest.md` and `backtest.json` (every founder screen, every served
# respondent question per link, the brief, the readings beside the file's anchoring, cost and time), `screens/`
# (founder-NN-*.png, respondent-<link>-NN-*.png) and `export/` (060/061's snapshot, names kept, no verdict gate).
#
# IT SPENDS MONEY: Keel's own Anthropic key, read into this one command's environment and never written anywhere --
# about $0.50 of inference and 1,700 credits for a twenty-person entry (08-fresco, 30 jobs, 6.5 minutes, spec 062). It REFUSES without the key, and
# refuses a stack already up (`make down` first): it boots its own, so keel-cloud inherits the key, and tears it down.
# Never in `make eval`, `make unit`, the matrix or a schedule (`evals/run_backtest.py` is no `test_*.py` file).
#
#   KEEL_ANTHROPIC_API_KEY="$$(...)" make backtest ENTRY=08-fresco
#
# **DOOR={keel,host}** (spec 066), default `keel`, which is the above byte for byte. `DOOR=host` asks for no key: the
# back-test starts keel-connect-skill's runtime itself (`python -m keel_runtime connect --executor claude --host claude
# --home <run>/keel_home --no-browser`, stdout to keel_home/launch.log), the founder signs in with its device code and
# approves it at /connect, and EVERY JOB IS ANSWERED BY THE FOUNDER'S OWN CLAUDE CODE LOGIN (CLAUDE_CONFIG_DIR as the
# shell has it, or CLAUDE_CODE_OAUTH_TOKEN) -- it spends the founder's plan, not Keel's account. `HOST=claude` is the
# one host built (another is refused by name); `MODEL=` is refused (the runtime has no session-wide pin since
# keel-runtime spec 009: each job carries keel-cloud's routing table's model). `scripts/backtest-host.sh <id>...` runs
# entries one after another and waits out the plan's limit.
#
#   make backtest DOOR=host ENTRY=08-fresco
# Spec 071 FR-4: SCOPE=PROBLEM|SOLUTION|SOLUTION_COMMERCIAL|COMMERCIAL walks the entry as a study of that scope (keel-cloud
# 133; ALL, the whole study, when unsaid) and records it in backtest.json; scripts/backtest-host.sh takes --scope.
#   make backtest DOOR=host ENTRY=08-fresco SCOPE=PROBLEM
# Spec 106 FR-2: PEOPLE=<n> sends the first n people on the person's own link, in corpus order (the decision-makers
# whole); every person the scope sends when unsaid. `make quality-walk` passes quality/cycle.toml's people (seven).
#   make backtest DOOR=host ENTRY=08-fresco SCOPE=PROBLEM PEOPLE=7
backtest:
	@if [ -n "$(DOOR)" ] && [ "$(DOOR)" != "keel" ] && [ "$(DOOR)" != "host" ]; then echo "make backtest refuses: DOOR=$(DOOR) is not a door -- \`DOOR=keel\` (Keel's AI, spec 062) or \`DOOR=host\` (the founder's own Claude Code through the runtime, spec 066)"; exit 2; fi
	@if [ "$(DOOR)" != "host" ] && [ -z "$$KEEL_ANTHROPIC_API_KEY" ]; then echo "make backtest refuses: KEEL_ANTHROPIC_API_KEY is not set in this shell -- the local stack passes it to keel-cloud, which answers every job of the back-test on Keel's AI (spec 062 FR-2); it is never logged, echoed or written"; exit 2; fi
	@if [ -z "$(ENTRY)" ]; then echo "make backtest refuses: no ENTRY -- name a back-test entry, \`make backtest ENTRY=<id>\` (keel-cloud canon/designs/measured-beliefs/backtest/<id>.yaml)"; exit 2; fi
	@$(MAKE) --no-print-directory venv
	KEEL_EVAL_PROFILE=eval KEEL_BACKTEST_ENTRY=$(ENTRY) $(if $(SCOPE),KEEL_BACKTEST_SCOPE=$(SCOPE) ,)$(if $(PEOPLE),KEEL_BACKTEST_PEOPLE=$(PEOPLE) ,)$(if $(filter host,$(DOOR)),KEEL_BACKTEST_DOOR=host KEEL_BACKTEST_HOST=$(if $(HOST),$(HOST),claude) $(if $(MODEL),KEEL_BACKTEST_MODEL=$(MODEL) ,),)$(PY) -m pytest evals/run_backtest.py -q -rs -l

# make noise-check (spec 074 FR-3) is THE NOISE-CAPTURE CERTIFICATE: the 1,260 samples of 2026-10-26 (thirty spoken
# answers, two voices each, quiet and five noise beds at 20 / 10 / 5 / 0 dB) read from KEEL_NOISE_SAMPLES (default
# ~/Documents/projects/keel-noise-check-2026-10-26/audio, the kept set; synthesized there when absent) and sent down
# Keel's answer path exactly as the product calls it -- gpt-transcribe with the item's hints and prompt, then
# claude-haiku-4-5-20251001 at temperature 0 and max_tokens 400 (keel-cloud 137) on the cloud checkout's own
# classify-answer.md -- and read by `Classification.validated()`'s rules with keel-cloud 136's partial pick. It writes
# runs/<stamp>-noise-check/ (results.jsonl, summary.json, noise-check.md, page/, register-row.md; the row appended to
# runs/noise-check-register.md) and prints the certificate: quiet closed answers 100%, every bed at 20 / 10 / 5 dB
# > 90%, confident wrong <= 2% and stories' meaning kept >= 90% in each cell -- PASS, or FAIL naming the first failing
# cell; every 0 dB cell reported outside the bar. Exit 0 on PASS only.
#
# IT SPENDS MONEY (about $2 and twenty minutes for the whole set): both keys from this shell, read into the request
# headers alone and never logged, echoed or written. Never in `make eval`, `make unit`, the matrix or a schedule; run on
# the founder's word. ONLY= (an id substring), SNRS= (e.g. 5,clean) and LIMIT= make a cheap partial run, whose
# certificate is INCOMPLETE; RESUME=runs/<stamp>-noise-check finishes one.
#
#   KEEL_OPENAI_API_KEY="$$(...)" KEEL_ANTHROPIC_API_KEY="$$(...)" make noise-check
#   ... make noise-check ONLY=c5- SNRS=clean,5
noise-check:
	@if [ -z "$$KEEL_OPENAI_API_KEY" ] || [ -z "$$KEEL_ANTHROPIC_API_KEY" ]; then echo "make noise-check refuses: KEEL_OPENAI_API_KEY and KEEL_ANTHROPIC_API_KEY must both be set in this shell -- the check calls gpt-transcribe and Haiku as the product does (spec 074 FR-3, about \$$2); they are never logged, echoed or written"; exit 2; fi
	@$(MAKE) --no-print-directory venv
	PYTHONPATH=. $(PY) -m evals.noise.pipeline $(if $(ONLY),--only "$(ONLY)",) $(if $(SNRS),--snrs "$(SNRS)",) $(if $(LIMIT),--limit $(LIMIT),) $(if $(RESUME),--resume "$(RESUME)",)

# make read-screens (spec 078) is THE QUESTION-QUALITY READERS: one back-test bundle's backtest.json (spec 062 FR-4)
# read as text, every founder screen by the founder-reader (the entry's .sources.md whole) and every served respondent
# screen of each link by the respondent-reader (the person the walk took on that link), one call a screen against
# quality/RUBRIC.md, then the three whole-flow questions once per audience. The readers run through the `claude` CLI
# exactly as instructions/judge.py does, with --model and --effort from quality/readers.toml (Opus 5.5, medium): it
# refuses on a missing binary or a failed one-word probe, and reads no key. Every prompt and answer is recorded under
# runs/<stamp>-read-<entry>/calls/; the score file is written to quality/scores/<entry>/ and committed (FR-4).
# DRY=1 prints every prompt and writes no score; LIMIT=n (the first n screens per audience) and ONLY=<text> (screens
# whose name or dimension carries it) make a partial run, whose score.json stays in the run folder.
# PAID (the founder's plan): never in `make eval`, `make unit`, the matrix or a schedule; run on the founder's word.
#
#   make read-screens RUN=runs/<stamp>-backtest-21-codyco DRY=1
#   make read-screens RUN=runs/<stamp>-backtest-21-codyco LIMIT=1 ONLY=problem.prevalence    the two-call smoke
#   make read-screens RUN=runs/<stamp>-backtest-21-codyco                                     one bundle, of record
read-screens: venv
	@if [ -z "$(RUN)" ]; then echo "make read-screens refuses: no RUN -- name a back-test bundle, \`make read-screens RUN=runs/<stamp>-backtest-<entry>\` (spec 078 FR-4)"; exit 2; fi
	PYTHONPATH=. $(PY) -m quality.readers --run "$(RUN)" $(if $(DRY),--dry-run,) $(if $(LIMIT),--limit $(LIMIT),) $(if $(ONLY),--only "$(ONLY)",) $(if $(OUT),--out "$(OUT)",)

# make read-table (spec 078 FR-5 / FR-6) builds quality/TABLE.md from every committed score file: the overall score_pct
# against the founder's bar of 90%, one row per (dimension, audience, screen kind) with the five means, the 0s, the
# instead lines and the fix location, weak rows marked, and the trend per entry. BASELINE=1 adds the comparison with
# quality/BASELINE.md and its verdict (better / same / worse). Free: no model, no stack.
#
#   make read-table
#   make read-table BASELINE=1
# Spec 079 FR-3: CYCLE=<record> puts the cycle's three-line head on top (this cycle, the baseline, the bar).
read-table: venv
	PYTHONPATH=. $(PY) -m quality.table $(if $(BASELINE),--baseline,) $(if $(CYCLE),--cycle "$(CYCLE)",)

# THE QUALITY CYCLE (spec 079): quality/CYCLE.md is the runbook -- a session told "kick off the instruction set" reads
# that file and nothing else. quality/cycle.toml holds the entries, the scopes, the bar, the weak rule, the reader and
# the adviser. None of these four targets is a dependency of anything; none runs from `make eval`, `make unit`, the
# matrix or a checker (FR-9).
#
# make quality-walk (PAID: Keel's AI or the founder's plan for the walks, the founder's plan for the readers) is the
# kick-off: per entry and per scope `make backtest ENTRY= SCOPE= DOOR=`, then `make read-screens` on the new bundle,
# then `make read-table BASELINE=1 CYCLE=<record>`; it writes quality/cycles/<yyyymmdd>-<cloud7>.md. ENTRIES=default
# walks cycle.toml's entries; SCOPES= defaults to cycle.toml's three. It refuses without ENTRIES, without WHY (the
# founder's words, carried in the record), with a dirty keel-cloud checkout, on DOOR=keel without the key in the shell,
# without the `claude` CLI, on an unknown entry or scope, and when BUILD= is not the checkout's sha. DRY=1 prints the plan
# and runs nothing. Spec 106 FR-2: every study sends quality/cycle.toml's `people` (seven) on the person's own link --
# the first in corpus order, the decision-makers whole; PEOPLE=<n> overrides it for one walk.
#   make quality-walk DRY=1 ENTRIES=21-codyco SCOPES=PROBLEM WHY="dry"
#   KEEL_ANTHROPIC_API_KEY="$$(...)" make quality-walk ENTRIES=default WHY="the registry's Frequency row moved"
#   make quality-walk ENTRIES=default DOOR=host WHY="a week since the last cycle"
quality-walk: venv
	PYTHONPATH=. $(PY) -m quality.cycle walk --entries "$(ENTRIES)" $(if $(SCOPES),--scopes "$(SCOPES)",) \
	  $(if $(DOOR),--door "$(DOOR)",) $(if $(BUILD),--build "$(BUILD)",) $(if $(DRY),--dry-run,) \
	  $(if $(PEOPLE),--people "$(PEOPLE)",) $(if $(WHY),--why "$(WHY)",)

# make quality-advise (PAID, one call per weak row, the founder's plan) hands each weak row of a cycle to the adviser
# (quality/readers/adviser.md, Opus 5.5 through the claude CLI) with the current text at its fix location read from
# the keel-cloud checkout; the proposals go to quality/cycles/<record>-advice.md, NEVER APPLIED. DRY=1 prints the
# prompts and calls nothing. Spec 087: a weak row quality/decisions.toml has decided is snoozed -- listed under
# Decided before, never sent; the adviser reads the founder's declined decisions on its row.
#   make quality-advise CYCLE=quality/cycles/<record>.md DRY=1
quality-advise: venv
	@if [ -z "$(CYCLE)" ]; then echo "make quality-advise refuses: no CYCLE -- name a cycle record, \`CYCLE=quality/cycles/<yyyymmdd>-<cloud7>.md\` (spec 079 FR-4)"; exit 2; fi
	PYTHONPATH=. $(PY) -m quality.cycle advise --cycle "$(CYCLE)" $(if $(DRY),--dry-run,)

# make quality-accept (FREE, on the founder's word only) holds the cycle's score_pct to the gallery's own last accepted
# one first (spec 106 FR-3: below it, refused -- nothing cut, nothing written; the first acceptance passes), then cuts
# quality/BASELINE.md from the cycle's score files (the old one kept under quality/baselines/<date>.md), builds the
# gallery from the cycle's bundles behind the readers' gate alone (`make gallery SCORES=quality/scores`, no bar: three
# studies an example, a flagged screen refused) into keel-web's public/sample (OUT= elsewhere), records the score in
# the provenance, prints what changed in the snapshot and the sentence the keel-web refresh spec starts from. It
# commits nothing anywhere. RUNS_DIR= says where the bundles are by name; QUALITY_OUT= writes the baseline elsewhere
# and PROVENANCE_DIR= the provenance (a dry rehearsal: both, with OUT=).
#   make quality-accept CYCLE=quality/cycles/<record>.md
quality-accept: venv
	@if [ -z "$(CYCLE)" ]; then echo "make quality-accept refuses: no CYCLE -- name a cycle record, \`CYCLE=quality/cycles/<yyyymmdd>-<cloud7>.md\` (spec 079 FR-6)"; exit 2; fi
	PYTHONPATH=. $(PY) -m quality.cycle accept --cycle "$(CYCLE)" $(if $(OUT),--out "$(OUT)",) \
	  $(if $(RUNS_DIR),--runs-dir "$(RUNS_DIR)",) $(if $(QUALITY_OUT),--quality-out "$(QUALITY_OUT)",) \
	  $(if $(PROVENANCE_DIR),--provenance-dir "$(PROVENANCE_DIR)",)

# make quality-due (FREE) says whether a cycle is due (spec 079 FR-7): a registry, instruction or routing change in
# keel-cloud since the last record's build, or a week since it. It runs nothing else: the founder kicks off.
quality-due: venv
	PYTHONPATH=. $(PY) -m quality.cycle due

# make eval-live runs the scenarios marked `live` -- a real `claude`, real money (spec 008-stranger-
# who-gives-orders). Opt-in only; never part of `make eval`/`make eval-all`. Needs a logged-in
# `claude` on PATH and a stack `make up` has already brought up (S-004 attacks S-001's project).
#
# **HOST={claude,copilot}**, default `copilot`, and it means something to exactly one scenario:
# S-012, the journey through a host (spec 019-journey-through-a-host; keel-cloud
# `canon/designs/e2e-matrix-design.md` §5.1, where the host is one of the matrix's three axes).
# It decides which CLI installs the plugin from the marketplace, which CLI is told "keel connect",
# which executor the runtime must end up on, and what the run bundle is called
# (`runs/<stamp>-s012-journey-<host>/`). The default is `copilot` so the command that produced the
# spec 016 run of record still means what it meant. `HOST` reaches the scenario as
# `KEEL_JOURNEY_HOST` -- the same spelling `instruction-eval` uses for its own two hosts, and a
# different variable, because they are different subjects and one run never sets both.
#
# **LEGS={short,full}**, default `full`, and it also means something to S-012 alone (spec
# 021-short-journey). `full` is the whole journey -- both legs, three stages, the person, the
# reading, the brief. `short` is the host leg entire (marketplace, "keel connect", device
# approval, the runtime on the host's executor) plus the FIRST model job only -- the PROBLEM
# frame's confirmation card landing -- and then the way out. Same assertions, up to that point;
# nothing new is asserted from the model's prose. The short bundle says so in its own name
# (`runs/<stamp>-s012-journey-<host>-short/`); the full one's name is unchanged.
#
# **ENTRY=<corpus entry id>**, default `03-lullaby`. S-012's founder is a **golden corpus**
# founder now, not the smoke's payroll fixture: the entry's title is the project name, its market
# is the market, its three statements are typed verbatim, and its first person answers with their
# own story text and their own picks. The corpus is keel-cloud's
# `canon/designs/measured-beliefs/corpus/`, read through the same `harness/corpus_script.py` the
# six scripted scenarios read it through. An id the corpus does not hold is refused by name.
#
#   make eval-live K=s012                 the Copilot journey, whole (today's command, unchanged)
#   make eval-live K=s012 HOST=claude     the same journey through Claude Code
#   make eval-live K=s012 HOST=claude LEGS=short    the per-change cell's own run
#   make eval-live K=s012 ENTRY=05-paidly           a different founder walks it
#   make eval-live K=s012 PEOPLE=2                  two people answer instead of five
#   make eval-live K=s004                 the stranger who gives orders (none of these apply)
#
# **PEOPLE=<n>**, default five on the full journey and always one on the short one (the founder,
# 2026-09-13: five people so the brief at the end has a verdict -- the product calls a line *Too
# few to call* under five; readings run on the routing table's light model, so five is cheap).
# HOST=/LEGS=/ENTRY=/PEOPLE= on the command line win; otherwise the environment's own KEEL_JOURNEY_* is
# kept (a cell exports them from cells.toml and then calls this target -- run 34614646990's
# macOS cells ran the FULL journey because this line used to overwrite `short` with `full`);
# only with neither does the default apply.
eval-live: venv
	KEEL_EVAL_PROFILE=$(if $(PROFILE),$(PROFILE),eval) \
	KEEL_JOURNEY_HOST=$(if $(HOST),$(HOST),$(if $(KEEL_JOURNEY_HOST),$(KEEL_JOURNEY_HOST),copilot)) \
	KEEL_JOURNEY_LEGS=$(if $(LEGS),$(LEGS),$(if $(KEEL_JOURNEY_LEGS),$(KEEL_JOURNEY_LEGS),full)) \
	KEEL_JOURNEY_ENTRY=$(if $(ENTRY),$(ENTRY),$(if $(KEEL_JOURNEY_ENTRY),$(KEEL_JOURNEY_ENTRY),03-lullaby)) \
	KEEL_JOURNEY_PEOPLE=$(if $(PEOPLE),$(PEOPLE),$(KEEL_JOURNEY_PEOPLE)) \
	$(PY) -m pytest evals -q -rs -l -m live $(if $(K),-k "$(K)",)

# make keels-ai runs S-012 through THE OTHER DOOR (spec 024-keels-ai-cell; keel-cloud
# `canon/designs/ai-credits-design.md` §6: "The door decides the AI"). The founder signs up at
# keel-web's /signup instead of saying "keel connect" to a CLI, keel-cloud marks the account
# `ai_path = KEEL` from the door alone and grants 1,500 credits, and every job of the journey is
# answered by keel-cloud on KEEL'S OWN Anthropic account. Nothing is installed, no runtime is
# started, and this run's KEEL_HOME is asserted empty at the end.
#
# IT SPENDS THE COMPANY'S MONEY, NOT THE FOUNDER'S. Every other live target bills the founder's
# own plan; this one bills Keel's Anthropic account -- about 1,355 credits a journey, which is
# $13.55 at list price and about $2.44 of actual inference (design §6.3, the five-participant
# row, re-summed at price version 12: readings 0, 30 at each person's Begin -- keel-cloud 156). That is why the matrix buys it once a Saturday and never on a merge, and why there is no
# short form of it here.
#
# PROFILE=remote by default, because the door only exists on a deployment: it needs keel-cloud
# with spec 044 and spec 045 and a KEEL_ANTHROPIC_API_KEY, and keel-web with spec 024. Point it
# at a local stack with PROFILE=eval if you have one carrying all four.
#
#   make keels-ai                          the whole journey, against KEEL_REMOTE_WEB_URL
#   make keels-ai ENTRY=05-paidly          a different corpus founder walks it
#   make keels-ai PEOPLE=2                 two people answer instead of five (cheaper)
#
# It is `eval-live` with the host axis set, and nothing else: one scenario, one command, four
# doors (AGENTS.md's third named LLM place, widened rather than multiplied).
keels-ai: venv
	$(MAKE) eval-live K=s012 HOST=keel LEGS=full \
	  PROFILE=$(if $(PROFILE),$(PROFILE),remote) \
	  $(if $(ENTRY),ENTRY=$(ENTRY),) $(if $(PEOPLE),PEOPLE=$(PEOPLE),)

# make eval-all runs the FULL scenario set (s001 included) against one stack session (attaches to
# an already-up stack from `make up`; does not tear it down -- `make down` is a separate step) and
# writes runs/INDEX-<stamp>.html summarizing every run this invocation produced.
eval-all: venv
	KEEL_EVAL_PROFILE=$(if $(PROFILE),$(PROFILE),eval) $(PY) -m harness.eval_all

# make report RUN=runs/<id> rebuilds report.html from that run's transcript.jsonl alone.
report: venv
	@if [ -z "$(RUN)" ]; then echo "usage: make report RUN=runs/<id>"; exit 2; fi
	$(PY) -m harness.evidence --rebuild "$(RUN)"

# The harness's own stackless unit tests (steps/evidence/report/config) -- no stack required.
unit: venv
	$(PY) -m pytest tests -q

# spec 013-skill-distribution: the packaging beds (keel-cloud `canon/designs/keel-skill-design.md`
# §10.2 B1 and §10.4 B3). Builds the two acceptance images -- Debian 12 with Python 3.11, Node 22
# and both host CLIs; Debian 11, which *is* the 3.9 floor -- for `linux/arm64` and `linux/amd64`,
# and runs the skill's own script inside each against the eval stack on the host
# (`KEEL_BASE_URL=http://host.docker.internal:18080`). Needs `make up` first.
#
# Two halves. The **stackless** one needs no secret and always runs. The **model-driven** one
# (`claude -p "keel connect"`, `copilot -p "keel connect"`) needs `ANTHROPIC_API_KEY` /
# `COPILOT_GITHUB_TOKEN` **from the caller's own shell** -- never a file, never a keychain (T-5) --
# and is skipped, by name and with its reason in the run record, when they are not there. Like
# `eval-live` and `instruction-eval` it costs real money when it does run.
#
#   make acceptance                          both architectures, both images
#   make acceptance PLATFORMS=linux/arm64    the native one only
#   make acceptance SKIP_BUILD=1             re-run the checks against images already built
acceptance: venv
	PLATFORMS="$(if $(PLATFORMS),$(PLATFORMS),linux/arm64 linux/amd64)" \
	SKIP_BUILD="$(if $(SKIP_BUILD),$(SKIP_BUILD),0)" \
	stack/containers/acceptance/run-acceptance.sh

# spec 009-instruction-eval: does keel-cloud's inference-instruction prose, sent to a real model
# exactly as production sends it, produce the measured beliefs the frozen golden corpus says it
# should? Unlike every other target here it needs **no `make up`** and no stack at all -- it talks
# to no service, only to keel-cloud's exporter, keel-runtime's own build_prompt, and the `claude`
# CLI. Like `eval-live` it **costs real money** on the founder's own account (149 model cases a
# pass at N=1 since MARKS_VERSION 18, the seven BRIEF readings and fourteen ASKED faces included), so
# start with DRY=1 and read a prompt.
# Deliberately NOT a dependency of `eval`,
# `eval-all` or `eval-live`, and it never reads or writes evals/policy.py -- its own rubric is
# versioned separately as instructions/marks.py's MARKS_VERSION.
#
# **HOST={claude,copilot}**, default `claude` (spec 014; keel-cloud
# `canon/designs/keel-skill-design.md` §5.5, the third part of the "supported" gate). It decides
# three things and nothing else: which CLI the pre-flight requires and probes, which executor
# keel-runtime's own `get_executor` constructs, and which of that runtime's two renderings of the
# same prompt body the host is sent. Corpus, contract, marks, `MARKS_VERSION`, judge, scorer and
# bundle layout are shared -- a comparison whose sides were sent different prompts measures
# nothing. **Two hosts' runs are different measurements and are never averaged**; a Copilot run
# lands in `runs/<stamp>-instructions-copilot/` and its report and register say whose words they
# are. Copilot bills the founder's plan in premium requests, not dollars, and neither figure is
# ever converted into the other.
#
#   make instruction-eval DRY=1 K=01-countly    prints the prompts, calls nothing
#   make instruction-eval BASELINE=1            the before-picture, once, and never again
#   make instruction-eval K=reading N=1         one subject, one run per case
#   make instruction-eval K=brief N=1           the BRIEF paragraph, seven calls
#   make instruction-eval HOST=copilot N=1      the other host, one run per case
# The screen (the founder, 2026-09-12): one entry of the seven, every stage and every person,
# three times -- about a seventh of the corpus -- for shopping models and checking a prompt change
# before the full run. It is never a run of record: the refusal mark's denominator is the whole
# corpus, and the gate says so.
# **MODELS=<file>|exported** (keel-cloud `canon/designs/model-routing-design.md` §7): pin each
# job class -- assumptions, reading, brief -- to the model the table names for this host, through
# the job's own `model` key, exactly as the cloud will send it. `MODELS=exported` uses the table
# keel-cloud's exporter wrote beside the contracts: the run of record for the cloud's own table.
# Never beside `KEEL_<HOST>_MODEL` (the runtime drops it at 0.5.0); the run refuses both at once.
#
# **And since keel-cloud table v6 (spec 047, 2026-09-30) the same file pins the EFFORT**, through
# the job's own `effort` key, from the table's `efforts` block at the same host x tier coordinate.
# A certificate is a model AND an effort level: run 20260930T024851Z-instructions certified
# claude-sonnet-5-5 *at effort medium*, and the Claude Code CLI's own default is xhigh.
#
# **Do not export CLAUDE_CODE_EFFORT_LEVEL to run at an effort.** It is process-wide: it reaches
# the judge as well as the subject, which is the whole reason `instructions/judge.py` strips it by
# name in `judge_env()` -- a run set that way would score itself at its own setting. With MODELS
# the effort travels per job, on the path a founder's job takes, and the bundle RECORDS it
# (`manifest.json`'s `effort.per_class`, the scorecard's and verdict's `efforts_used`), so a run of
# record can state the effort it was taken at instead of it being a fact about whoever typed the
# command. Readings are exempt by construction: `reading` routes to the `light` tier, whose row
# carries no effort, because `effort` errors on Haiku 4.5.
#
# **WHY=<event>** (the founder, 2026-09-13, design §7.1): every run that spends says why --
# `WHY=instruction:<file>`, `WHY=prompt:<file>`, `WHY=contract:<file>` earn a screen;
# `WHY=new-model:<host>:<model>` and `WHY=marks:<version>` earn the full run. Without one the run
# refuses at the door and prints the policy; `DRY=1` needs none. The reason is written into the
# bundle's manifest.
#
# `marks:` is the fifth event (spec 025 FR-023) and is **full-run only**. The other four name a
# change to the *subject*; this one names a change to the *ruler*, and the standing gate reads
# "green at the current MARKS_VERSION" -- so a rubric that moved has no run of record at all until
# one is spent, and a screen is one entry and cannot be one.
#
#   make instruction-screen HOST=codex WHY=contract:brief.md MODELS=candidates.json   one entry
#   make instruction-eval HOST=codex WHY=new-model:codex:gpt-6-astra MODELS=exported   the certificate
#   make instruction-eval HOST=claude WHY=new-model:claude:claude-sonnet-5-5 MODELS=exported
#       -- the 2026-09-30 certificate's own shape: claude-sonnet-5-5 at medium, from the table
#   make instruction-eval HOST=claude WHY=marks:8 MODELS=exported
#       -- MARKS_VERSION 8's own run of record (spec 025 T030), ~2.5 h and ~$15
#   make instruction-eval HOST=claude WHY=marks:9 MODELS=exported
#       -- MARKS_VERSION 9's own run of record, runs/20261008T194906Z-instructions (spec 029), ~$20
#   make instruction-eval HOST=claude WHY=marks:10 MODELS=exported
#       -- MARKS_VERSION 10's own run of record (spec 030), never spent: v11 superseded it
#   make instruction-eval HOST=claude WHY=marks:11 MODELS=exported
#       -- MARKS_VERSION 11's own run of record (spec 031), never spent: v12 superseded it
#   make instruction-eval HOST=claude WHY=marks:12 MODELS=exported
#       -- MARKS_VERSION 12's own run of record (spec 032), ON HOLD by the founder, never spent: v13 superseded it
#   make instruction-eval HOST=claude WHY=marks:13 MODELS=exported
#       -- MARKS_VERSION 13's own run of record (spec 033), never spent: v14 superseded it
#   make instruction-eval HOST=claude WHY=marks:14 MODELS=exported
#       -- MARKS_VERSION 14's own run of record (spec 034), never spent: v15 superseded it
#   make instruction-eval HOST=claude WHY=marks:15 MODELS=exported
#       -- MARKS_VERSION 15's own run of record (spec 036), never spent: v16 superseded it
#   make instruction-eval HOST=claude WHY=marks:16 MODELS=exported
#       -- MARKS_VERSION 16's own run of record (spec 037), never spent: v17 superseded it
#   make instruction-eval HOST=claude WHY=marks:17 MODELS=exported
#       -- MARKS_VERSION 17's own run of record (spec 038), never spent: v18 superseded it
#   make instruction-eval HOST=claude WHY=marks:18 MODELS=exported
#       -- MARKS_VERSION 18's own run of record (spec 040): none yet -- the certificate, on the founder's word only
#   make instruction-screen HOST=claude WHY=instruction:asked.md K=asked MODELS=exported
#       -- the eighth screen's instruction (keel-cloud 088), before routing v11's `asked: light` row is trusted
#   make instruction-screen HOST=claude K=08-fresco/PROBLEM_INTERPRET N=3 MODELS=exported WHY=instruction:169
#   make instruction-screen HOST=claude K=169-banking-gaming N=3 MODELS=exported WHY=instruction:169
#       -- spec 105 FR-3: a needle naming a keel-cloud back-test entry (canon/designs/measured-beliefs/backtest/)
#          screens its three interpretation screens, and one naming a probe (.../probes/, keel-cloud 169) its two
#          frame screens, marked on the first turn (NEEDS_INPUT, one question naming the planted term, two readings);
#          a kind word (K=frame) and the full eval read the golden corpus alone, as before
instruction-screen: venv
	$(PY) -m instructions.run --host $(if $(HOST),$(HOST),claude) \
		$(if $(DRY),--dry-run,) -k "$(if $(K),$(K),01-countly)" -n $(if $(N),$(N),3) \
		$(if $(MARKS),--marks $(MARKS),) $(if $(MODELS),--models $(MODELS),) \
		$(if $(WHY),--why "$(WHY)",)

instruction-eval: venv
	$(PY) -m instructions.run --host $(if $(HOST),$(HOST),claude) \
		$(if $(DRY),--dry-run,) $(if $(BASELINE),--baseline,) \
		$(if $(K),-k "$(K)",) $(if $(N),-n $(N),) $(if $(MARKS),--marks $(MARKS),) \
		$(if $(MODELS),--models $(MODELS),) $(if $(WHY),--why "$(WHY)",)

# spec 018-gated-registry-stub: the stub OIDC issuer as a container, which is the one service the
# staging twin runs that production does not (keel-cloud `canon/designs/e2e-matrix-design.md` §3
# and §4). Same package the eval profile spawns as a local process; `--gated` and `--registry` are
# the only difference, and they are flags rather than a build.
#
# arm64 because the staging box is a `t4g.micro`. **buildx when there is one, the legacy builder
# when there is not**: the founder's own Docker (29.5.2, through Colima) has no `docker buildx`,
# which `runs/DRIFT.md` #50 already records for the acceptance bed -- so this probes rather than
# assuming, and prints which builder it used.
#
#   make oidc-image TAG=$(git rev-parse --short HEAD)
#   make oidc-image TAG=<sha> PLATFORM=linux/amd64
#   make oidc-image TAG=<sha> PUSH=1 OIDC_IMAGE_REPO=<account>.dkr.ecr.<region>.amazonaws.com/keel-oidc
oidc-image:
	@if [ -z "$(TAG)" ]; then echo "usage: make oidc-image TAG=<tag> [PUSH=1]"; exit 2; fi
	@set -eu; \
	export DOCKER_HOST="$(if $(DOCKER_HOST),$(DOCKER_HOST),unix://$(HOME)/.colima/default/docker.sock)"; \
	platform="$(if $(PLATFORM),$(PLATFORM),linux/arm64)"; \
	image="$(if $(OIDC_IMAGE_REPO),$(OIDC_IMAGE_REPO),keel-oidc):$(TAG)"; \
	if docker buildx version >/dev/null 2>&1; then \
		echo "[oidc-image] buildx, $$platform -> $$image"; \
		docker buildx build --platform "$$platform" \
			-f stack/containers/oidc/Dockerfile -t "$$image" \
			$(if $(PUSH),--push,--load) . ; \
	else \
		echo "[oidc-image] no buildx on this Docker -- legacy builder, $$platform -> $$image"; \
		docker build --platform "$$platform" \
			-f stack/containers/oidc/Dockerfile -t "$$image" . ; \
		$(if $(PUSH),docker push "$$image",true) ; \
	fi

# spec 020-matrix-workflow: the three named cell sets, validated and printed -- the SAME code
# `.github/workflows/matrix.yml`'s `select` job runs (`python -m matrix --set <name> --json`), so a
# founder who edits matrix/cells.toml finds out here what a runner would otherwise find out after
# assuming a role and deploying a box. Stackless, offline, stdlib only: no venv, no network, no
# secret, nothing to spend.
#
#   make matrix-check                      the three sets, one line a cell
#   make matrix-check SET=nightly          just that one
#   make matrix-check SET=weekly CELLS=ubuntu-24.04-claude-py3.13
#
# Python 3.11+ (tomllib). A cell's own Python is a different question and is never this one.
matrix-check:
	python3 -m matrix $(if $(SET),--set $(SET),) $(if $(CELLS),--cells $(CELLS),)
