VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PLAYWRIGHT := $(VENV)/bin/playwright

.PHONY: up down eval eval-live eval-all report venv unit instruction-eval

# Idempotent: safe to depend on from every other target. Re-run costs a few seconds once the
# venv already exists (pip/playwright no-op when nothing changed).
venv: $(PY)

$(PY):
	python3 -m venv $(VENV)
	$(PIP) install -q -r requirements.txt
	$(PLAYWRIGHT) install chromium

# PROFILE=playground boots/tears down the split-stacks playground profile (its own ports/volume,
# relay-design.md §12.5) instead of the default eval profile -- `make up PROFILE=playground`.
up: venv
	$(PY) -m stack.cli up $(if $(PROFILE),$(PROFILE),eval)

down: venv
	$(PY) -m stack.cli down $(if $(PROFILE),$(PROFILE),eval)

# make eval K=s001 runs only that scenario; bare `make eval` runs every scenario module.
# PROFILE=playground attaches evals/conftest.py's own stack fixture to the split-stacks
# playground profile instead of the default eval profile -- `make eval K=s001 PROFILE=playground`
# (relay-design.md §12.5: two profiles never share ports, a database, or now a runtime home).
eval: venv
	KEEL_EVAL_PROFILE=$(if $(PROFILE),$(PROFILE),eval) $(PY) -m pytest evals -q -m "not live" $(if $(K),-k $(K),)

# make eval-live runs the scenarios marked `live` -- a real `claude`, real money (spec 008-stranger-
# who-gives-orders). Opt-in only; never part of `make eval`/`make eval-all`. Needs a logged-in
# `claude` on PATH and a stack `make up` has already brought up (S-004 attacks S-001's project).
eval-live: venv
	KEEL_EVAL_PROFILE=$(if $(PROFILE),$(PROFILE),eval) $(PY) -m pytest evals -q -m live $(if $(K),-k $(K),)

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

# spec 009-instruction-eval: does keel-cloud's inference-instruction prose, sent to a real model
# exactly as production sends it, produce the measured beliefs the frozen golden corpus says it
# should? Unlike every other target here it needs **no `make up`** and no stack at all -- it talks
# to no service, only to keel-cloud's exporter, keel-runtime's own build_prompt, and the `claude`
# CLI. Like `eval-live` it **costs real money** on the founder's own account (about 127 calls a
# pass at N=1), so start with DRY=1 and read a prompt. Deliberately NOT a dependency of `eval`,
# `eval-all` or `eval-live`, and it never reads or writes evals/policy.py -- its own rubric is
# versioned separately as instructions/marks.py's MARKS_VERSION.
#
#   make instruction-eval DRY=1 K=01-countly    prints the prompts, calls nothing
#   make instruction-eval BASELINE=1            the before-picture, once, and never again
#   make instruction-eval K=reading N=1         one subject, one run per case
instruction-eval: venv
	$(PY) -m instructions.run $(if $(DRY),--dry-run,) $(if $(BASELINE),--baseline,) \
		$(if $(K),-k $(K),) $(if $(N),-n $(N),) $(if $(MARKS),--marks $(MARKS),)
