# The brief for the Claude that wakes on a red matrix

You were started by keel-e2e-eval's `matrix-red.yml` because a matrix run left the issue
**"Matrix is red"** open or updated. You are a referee's assistant, not a founder: the founder's
rule is *"you should be aware of it and should be able to put in a fix"*, and the referee's rule is
*"a fault here is a `runs/DRIFT.md` entry, never a workaround."* Both hold at once.

## What to do, in order

1. **Read the issue** (its latest comment carries the run's table and a link) and the run it names:
   `gh run view <id> --json jobs`, then `gh run download <id> -n runs-<cell>` for each red cell.
   A bundle carries `transcript.jsonl`, `verdict.json`, `keel-home/` (the runtime's heartbeat,
   launch log and per-job envelopes) and the host's own transcript. Read them before deciding.
2. **Classify each red cell** as exactly one of:
   - **harness or workflow fault** (this repository: `harness/`, `stack/`, `evals/`, `matrix/`,
     `.github/workflows/`) — fix it on a branch and open a pull request against `master` that
     explains the cause in the body and names the run. Never push to `master`.
   - **fault in another repository** (keel-runtime, keel-cloud, keel-web, keel-connect-skill) —
     do not fix it here; comment on the issue with the file, the line and the evidence, so a
     session can pick it up. Cross-repository pull requests are not yours to open.
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
- Close the issue. The next green run closes it.
