VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PLAYWRIGHT := $(VENV)/bin/playwright

.PHONY: up down eval eval-all report venv unit

# Idempotent: safe to depend on from every other target. Re-run costs a few seconds once the
# venv already exists (pip/playwright no-op when nothing changed).
venv: $(PY)

$(PY):
	python3 -m venv $(VENV)
	$(PIP) install -q -r requirements.txt
	$(PLAYWRIGHT) install chromium

up: venv
	$(PY) -m stack.cli up

down: venv
	$(PY) -m stack.cli down

# make eval K=s001 runs only that scenario; bare `make eval` runs every scenario module.
eval: venv
	$(PY) -m pytest evals -q $(if $(K),-k $(K),)

# make eval-all runs the FULL scenario set (s001 included) against one stack session (attaches to
# an already-up stack from `make up`; does not tear it down -- `make down` is a separate step) and
# writes runs/INDEX-<stamp>.html summarizing every run this invocation produced.
eval-all: venv
	$(PY) -m harness.eval_all

# make report RUN=runs/<id> rebuilds report.html from that run's transcript.jsonl alone.
report: venv
	@if [ -z "$(RUN)" ]; then echo "usage: make report RUN=runs/<id>"; exit 2; fi
	$(PY) -m harness.evidence --rebuild "$(RUN)"

# The harness's own stackless unit tests (steps/evidence/report/config) -- no stack required.
unit: venv
	$(PY) -m pytest tests -q
