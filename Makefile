VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PLAYWRIGHT := $(VENV)/bin/playwright

.PHONY: up down eval eval-live eval-all report venv unit instruction-eval instruction-screen acceptance oidc-image \
        matrix-check

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
#   make eval-live K=s004                 the stranger who gives orders (none of these apply)
# HOST=/LEGS=/ENTRY= on the command line win; otherwise the environment's own KEEL_JOURNEY_* is
# kept (a cell exports them from cells.toml and then calls this target -- run 34614646990's
# macOS cells ran the FULL journey because this line used to overwrite `short` with `full`);
# only with neither does the default apply.
eval-live: venv
	KEEL_EVAL_PROFILE=$(if $(PROFILE),$(PROFILE),eval) \
	KEEL_JOURNEY_HOST=$(if $(HOST),$(HOST),$(if $(KEEL_JOURNEY_HOST),$(KEEL_JOURNEY_HOST),copilot)) \
	KEEL_JOURNEY_LEGS=$(if $(LEGS),$(LEGS),$(if $(KEEL_JOURNEY_LEGS),$(KEEL_JOURNEY_LEGS),full)) \
	KEEL_JOURNEY_ENTRY=$(if $(ENTRY),$(ENTRY),$(if $(KEEL_JOURNEY_ENTRY),$(KEEL_JOURNEY_ENTRY),03-lullaby)) \
	$(PY) -m pytest evals -q -rs -l -m live $(if $(K),-k "$(K)",)

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
# CLI. Like `eval-live` it **costs real money** on the founder's own account (about 131 calls a
# pass at N=1, the seven BRIEF paragraphs included), so start with DRY=1 and read a prompt.
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
# **WHY=<event>** (the founder, 2026-09-13, design §7.1): every run that spends says why --
# `WHY=instruction:<file>`, `WHY=prompt:<file>`, `WHY=contract:<file>` earn a screen;
# `WHY=new-model:<host>:<model>` earns the full run. Without one the run refuses at the door and
# prints the policy; `DRY=1` needs none. The reason is written into the bundle's manifest.
#
#   make instruction-screen HOST=codex WHY=contract:brief.md MODELS=candidates.json   one entry
#   make instruction-eval HOST=codex WHY=new-model:codex:gpt-6-astra MODELS=exported   the certificate
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
