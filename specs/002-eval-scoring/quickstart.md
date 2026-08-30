# Quickstart: scored runs

## Run scored
make up && make eval K=s001 → open runs/<id>/report.html: X/5 header, category bars,
interaction cards with checks; scorecard.json beside it.

## Prove the teeth (SC-002)
.venv/bin/python -m pytest tests/ -q — seeded-loss fixtures: truncated statement fails its
FID check, leaked enum fails CLA-U1, empty display fails ORI-H1/GUI-H1.

## Re-score an old bundle
make report RUN=runs/<old-id> — scoring re-runs from the bundle; a bumped policy stamps its
version; transcript and screenshots untouched (SC-004).

## Interrupted run
Kill the stack mid-eval: bundle still scores what it saw, gated at 2/5, verdict failed (SC-003).
