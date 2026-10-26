#!/usr/bin/env bash
# Spec 066 FR-6: back-test entries through the HOST door, one after another, on the founder's own Claude Code.
#
#   scripts/backtest-host.sh 08-fresco 09-karsa ...
#   scripts/backtest-host.sh --scope PROBLEM 08-fresco ...      (spec 071 FR-4: the study's scope, ALL when unsaid)
#
# For each id: waits while any `pytest evals` runs (one eval stack on this machine at a time), `make down`, then
# `make backtest DOOR=host ENTRY=<id>` into runs/backtest-host/<id>.log, and prints one line -- the id, the run
# directory, steps, bad, the decision label -- and (spec 067) the register's re-run row beneath it. A run whose backtest.md says *stopped by the plan's limit at <time>* is
# rerun after that time (or 30 minutes when it names none), at most three times, before the runner moves on.
#
# It prints only that line and its own waits: never the environment, a key, a token or the CLI's login.
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PY:-$REPO/.venv/bin/python}"
LOGS="$REPO/runs/backtest-host"
RERUNS=3
mkdir -p "$LOGS"
SCOPE=ALL
case "${1:-}" in
  --scope) SCOPE="${2:-}"; shift 2 || { echo "usage: scripts/backtest-host.sh [--scope <scope>] <entry id>..." >&2; exit 2; } ;;
  --scope=*) SCOPE="${1#--scope=}"; shift ;;
esac
case "$SCOPE" in
  PROBLEM|SOLUTION|SOLUTION_COMMERCIAL|COMMERCIAL|ALL) ;;
  *) echo "scripts/backtest-host.sh refuses: --scope $SCOPE is not a study scope -- PROBLEM, SOLUTION, SOLUTION_COMMERCIAL, COMMERCIAL or ALL" >&2; exit 2 ;;
esac
if [ "$#" -lt 1 ]; then
  echo "usage: scripts/backtest-host.sh [--scope <scope>] <entry id>..." >&2
  exit 2
fi

# A `pytest evals` run is a python `-m pytest evals...` process. The bracket keeps this pattern from matching a waiting
# shell's own command line (a loop whose text says `pgrep -f "pytest evals"` would otherwise wait on itself forever).
alone() {
  while pgrep -f -- "-m [p]ytest evals" >/dev/null 2>&1; do sleep 30; done
}

for id in "$@"; do
  reruns=0
  while :; do
    alone
    make -C "$REPO" --no-print-directory down >/dev/null 2>&1
    alone
    make -C "$REPO" --no-print-directory backtest DOOR=host ENTRY="$id" SCOPE="$SCOPE" >"$LOGS/$id.log" 2>&1
    (cd "$REPO" && PYTHONPATH=. "$PY" -m evals.backtest summary "$LOGS/$id.log" "$id")
    wait_s="$(cd "$REPO" && PYTHONPATH=. "$PY" -m evals.backtest resume "$LOGS/$id.log" "$id")"
    if [ -z "$wait_s" ] || [ "$reruns" -ge "$RERUNS" ]; then
      break
    fi
    reruns=$((reruns + 1))
    echo "$id: stopped by the plan's limit -- waiting ${wait_s} s, then rerun ${reruns} of ${RERUNS}"
    sleep "$wait_s"
  done
done
