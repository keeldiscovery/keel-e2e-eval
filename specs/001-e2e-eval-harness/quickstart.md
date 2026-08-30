# Quickstart: keel-e2e-eval

## Prerequisites
Sibling checkouts (`../keel-cloud`, `../keel-web`, `../keel-skill`); Docker/Colima running;
JDK 21 + Node 20; `pip install pytest playwright requests && playwright install chromium`.

## Run
```bash
make up            # boots the stack, prints each health gate
make eval K=s001   # runs the smoke; prints the run directory
make down
```

## Review
Open `runs/<id>/report.html` — every founder screen and every participant survey step as
screenshots, protocol transcript inline, verdict up top.

## Prove the failure path (SC-003)
`make up`, kill the vite process, `make eval K=s001` → fails at a browser step; the report
still generates with page HTML + console at the failing step.
