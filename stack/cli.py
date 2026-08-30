"""`python -m stack.cli up|down|status` -- the Makefile's own entrypoint into the stack package
(FR-001). Kept intentionally thin: all logic lives in stack/lifecycle.py so evals/conftest.py can
call the same functions.
"""

from __future__ import annotations

import sys

from stack.config import ConfigError, load_config
from stack.lifecycle import boot, quick_gates_pass, teardown
from stack.processes import HealthGateTimeout, PortTaken


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"up", "down", "status"}:
        print("usage: python -m stack.cli up|down|status", file=sys.stderr)
        return 2
    action = sys.argv[1]

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"[config] {exc}", file=sys.stderr)
        return 1

    if action == "status":
        print("up" if quick_gates_pass(config) else "down")
        return 0

    if action == "down":
        teardown(config)
        return 0

    # up
    if quick_gates_pass(config):
        print("[up] stack already answering on all three ports -- attaching, not re-booting")
        return 0
    try:
        boot(config)
    except (PortTaken, HealthGateTimeout) as exc:
        print(f"[up] failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
