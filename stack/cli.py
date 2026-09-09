"""`python -m stack.cli up|down|status [profile]` -- the Makefile's own entrypoint into the stack
package (FR-001). Kept intentionally thin: all logic lives in stack/lifecycle.py so
evals/conftest.py can call the same functions.

Split-stacks (relay-design.md §12.5): `profile` defaults to "eval" (byte-identical behavior to
before this existed) -- `make up PROFILE=playground` passes "playground" through to
`load_config`, which resolves an entirely separate port set (and, in stack/postgres.py, an
entirely separate Compose project), so a playground boot/teardown can never collide with, or
destroy, the default eval profile's own stack or data.
"""

from __future__ import annotations

import sys

from stack.config import PROFILES, ConfigError, load_config
from stack.lifecycle import boot, quick_gates_pass, teardown
from stack.processes import HealthGateTimeout, PortTaken
from stack.runtime import BundledRuntimeMissing


def main() -> int:
    if len(sys.argv) not in (2, 3) or sys.argv[1] not in {"up", "down", "status"}:
        print("usage: python -m stack.cli up|down|status [profile]", file=sys.stderr)
        return 2
    action = sys.argv[1]
    profile = sys.argv[2] if len(sys.argv) == 3 else "eval"
    if profile not in PROFILES:
        print(f"[config] unknown profile {profile!r} -- expected one of {PROFILES}", file=sys.stderr)
        return 2

    try:
        config = load_config(profile=profile)
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
        print(f"[up] ({config.profile}) stack already answering on all three ports -- "
              f"attaching, not re-booting")
        return 0
    try:
        boot(config)
    except (PortTaken, HealthGateTimeout, BundledRuntimeMissing) as exc:
        # spec 012: a missing bundled runtime fails `make up` fast, with the one command that
        # fixes it -- never a stack that boots and then reports `runtime_unavailable` from inside
        # a scenario, where it reads as a product defect rather than a build step nobody ran.
        print(f"[up] failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
