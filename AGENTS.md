# AGENTS.md

keel-e2e-eval: the referee. It stands the whole Keel stack up locally and proves the three
applications (keel-cloud, keel-web, keel-skill) agree — with each other, and with the journey.

**The canon comes first**: keel-cloud `specs/projectv2/CANON.md` holds the governing documents,
their precedence, and the ledger this repo's `tests/test_journey_coverage.py` enforces. This
repo deliberately floats at sibling HEADs (a referee pinned to the past can't call the present).

Rules of this repo: it owns no product code and never fixes the product — cross-repo defects go
to `runs/DRIFT.md` with evidence and get fixed in the owning repo. Scenarios are deterministic
(no LLM; payloads from data, never generated) and every assertion enforcing a journey moment
cites it (`§n.m`). The evidence bundle (`runs/<id>/`, report.html) is the product of a run; the
scoring policy (`evals/policy.py`, versioned) is the yardstick. `make up / eval K= / eval-all /
down`; quickstarts in `specs/*/quickstart.md`.
