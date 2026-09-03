# Quickstart: the connect stack (S-001)

## Prerequisites
Sibling checkouts `../keel-cloud`, `../keel-web`, `../keel-runtime`, `../keel-connect-skill`;
Docker/Colima running; JDK 21 (`JAVA_HOME` set per keel-cloud's AGENTS.md) + Node 20; `make` builds
its own `.venv` (pytest, playwright, requests) and installs Chromium.

## Run
```bash
make up               # boots postgres/cloud/web, resets the runtime home; prints four gates
make eval K=s001       # the smoke: starts the runtime via the connect skill, walks the journey
make down              # kills a runtime the smoke left running too, then everything else
```

## Review
Open `runs/<id>/report.html` — every lettered frame (L/B/C/G/C1-C8/R/E/P/B1-B2) as a
screenshot, the score under policy v6 up top, `versions.json` naming all five repos at HEAD.

## Prove the runtime-home gate (US1 acceptance scenario 1)
`make up` → `runs/.stack/keel-home/` exists and `python3 -m keel_runtime status --home
runs/.stack/keel-home` (from `../keel-runtime`) reads `{"running": false}` — no credential or
heartbeat survives from a prior run.

## Stackless tests
```bash
make unit    # config, interactions, scoring, policy v6, journey coverage -- no stack required
```
