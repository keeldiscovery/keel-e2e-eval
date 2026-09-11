# The brief for reading a red matrix

This is what a session does when the founder asks for the matrix report, or finds the issue
**"Matrix is red"** open (the founder's decision, 2026-09-11: no automatic Claude in Actions --
"I would rather do the next day when I ask for a report"). The founder's rule is *"you should be
aware of it and should be able to put in a fix"*, and the referee's rule is *"a fault here is a
`runs/DRIFT.md` entry, never a workaround."* Both hold at once.

## What to do, in order

1. **Read the issue** (its latest comment carries the run's table and a link) and the run it names:
   `gh run view <id> --json jobs`, then `gh run download <id> -n runs-<cell>` for each red cell.
   A bundle carries `transcript.jsonl`, `verdict.json`, `keel-home/` (the runtime's heartbeat,
   launch log and per-job envelopes) and the host's own transcript. Read them before deciding.
2. **Classify each red cell** as exactly one of:
   - **harness or workflow fault** (this repository: `harness/`, `stack/`, `evals/`, `matrix/`,
     `.github/workflows/`) — fix it, with a stackless test, and say which run found it.
   - **fault in another repository** (keel-runtime, keel-cloud, keel-web, keel-connect-skill) —
     fix it there, prove it there (keel-runtime's acceptance run; keel-cloud's suite), release the
     plugin if the runtime changed, and let the next matrix run prove it.
   - **model-behaviour event** (a live model wrote a shape the referee refused: no deal-breaker
     line, a `COMPLETED` with no `result`, an overrun) — write it up on the issue as a candidate
     `runs/DRIFT.md` entry in that file's own voice (what was observed, where, why it matters),
     and stop. **Never loosen an assertion, widen a timeout, retry a run, or change a scenario's
     expectations to make a run green.** That is the one thing the referee must never do.
   - **infrastructure** (a runner, a token, staging itself) — comment what you found and stop.
3. **One comment per run, on the issue**, saying per cell which of the four it was and what you
   did. Short. Evidence, not prose.

## What you must not do

- Touch production, `deploy/`, or anything under `/keel/prod/`. Production deploys are the
  founder's word alone.
- Spend model calls on live scenarios (`make eval-live`) — the runs' bundles are your evidence.
- Change `matrix/cells.toml`, `evals/policy.py` or any assertion in `evals/` to make a run pass.
- Close the issue by hand. The next green run closes it.
