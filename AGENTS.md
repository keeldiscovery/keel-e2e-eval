# AGENTS.md

keel-e2e-eval: the referee. It stands the whole connect stack up locally and proves the four
applications (keel-cloud, keel-web, keel-runtime, keel-connect-skill) agree — with each other,
and with the journey. It never talks to keel-skill or the retired agent-protocol/relay surfaces
(archived 2026-09-03, `runs/DRIFT.md`'s dated retirement note); no Prism, no LLM, ever.

**The canon comes first**: keel-cloud `canon/CANON.md` holds the governing documents,
their precedence, and the ledger this repo's `tests/test_journey_coverage.py` enforces. This
repo deliberately floats at sibling HEADs (a referee pinned to the past can't call the present).

**The runtime is a referee's target, not the referee's tool**: `keel connect` is never launched by
this harness directly (`python3 -m keel_runtime`) — only through `keel-connect-skill`'s own
script (`harness/connect.py`), because that skill is itself one of the four applications under
referee. `make up` ends with the runtime not yet running; the one scenario starts it, because
starting it is part of the journey.

Rules of this repo: it owns no product code and never fixes the product — cross-repo defects go
to `runs/DRIFT.md` with evidence and get fixed in the owning repo. The one scenario, S-001, is
deterministic (keel-runtime's `--executor scripted`, never an LLM; the participants' typed
answers are fixture data, never generated) and every assertion enforcing a journey moment cites
it (`§n.m`). The evidence bundle (`runs/<id>/`, report.html) is the product of a run; the scoring
policy (`evals/policy.py`, versioned) is the yardstick. `make up / eval K=s001 / down`;
quickstarts in `specs/*/quickstart.md`.

**Two referee sessions never share the eval profile.** The stack's ports (55432/18080/5173) and
runtime home are fixed per profile, not per process — a second `make up`/`make eval`/`make down`
against the default (eval) profile while another is mid-run restarts keel-cloud and drops the
database out from under it (live-confirmed: two sessions racing the same checkout, 2026-09-03).
If a stack session is already running S-001 on eval, use the split-stacks playground profile for
your own instead (relay-design.md §12.5) — its own ports, its own Postgres project, and (spec
005) its own runtime home (`runs/.stack/keel-home-playground/`, never the eval profile's
`keel-home/`):

```bash
make up PROFILE=playground
make eval K=s001 PROFILE=playground
make down PROFILE=playground
```

`make eval`/`make eval-all` read `PROFILE` via the `KEEL_EVAL_PROFILE` env var they set for
pytest (`evals/conftest.py`'s `stack_config` fixture); nothing here defaults to guessing which
profile a running stack is on, so a mismatched `PROFILE` just attaches to (or boots) the wrong
one's own three ports.
