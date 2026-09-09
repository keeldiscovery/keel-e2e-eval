"""Whole-stack up/down/status, shared by the Makefile's CLI entrypoint and evals/conftest.py's
attach-or-boot fixture (contracts/stack-contract.md).
"""

from __future__ import annotations

import time

from stack import auth, cloud, postgres, runtime, web
from stack.config import StackConfig, load_config
from stack.processes import teardown_all_processes


def quick_gates_pass(config: StackConfig) -> bool:
    """A fast, non-blocking check: is the whole stack already up and answering? Used so `make
    eval` against an already-up stack attaches instead of re-booting (design pass 5, edge case).
    `boot` below handles the partial case (e.g. only keel-web died) by checking -- and only
    (re)starting -- each piece independently, rather than requiring all-or-nothing here.

    The runtime-home gate is deliberately not part of this: spec 005 US1 says `make up` ends with
    the runtime **not yet running** (the smoke starts it) -- "already up" for attach purposes
    means the three long-running processes answering, exactly as before.
    """
    return postgres.is_up(config) and cloud.is_up(config) and web.is_up(config)


def boot(config: StackConfig) -> None:
    """Brings the whole stack up, printing each gate as it passes (FR-001, SC-001)."""
    print(f"[up] ({config.profile}) postgres: booting on {config.postgres_port} ...")
    postgres.up(config)
    print(f"[up] ({config.profile}) postgres: ready on {config.postgres_port}")

    print(f"[up] ({config.profile}) keel-cloud: booting on {config.cloud_port} "
          f"(budget {config.cloud_boot_timeout}s) ...")
    cloud.up(config)
    print(f"[up] ({config.profile}) keel-cloud: ready on {config.cloud_port}")

    print(f"[up] ({config.profile}) keel-web: booting on {config.web_port} "
          f"(budget {config.web_boot_timeout}s) ...")
    web.up(config)
    print(f"[up] ({config.profile}) keel-web: ready on {config.web_port}")

    # spec 012 FR-002: the runtime a founder runs is the one that travelled inside the skill, so
    # the stack refuses to boot without it and names the one command that builds it. It does not
    # run that command: `make runtime` writes into a sibling repository, and this repo owns no
    # product code (see `runtime.BundledRuntimeMissing` for the whole argument).
    print(f"[up] ({config.profile}) bundled-runtime: checking "
          f"{runtime.bundled_runtime_dir(config)} ...")
    runtime.require_bundled_runtime(config)
    print(f"[up] ({config.profile}) bundled-runtime: ready "
          f"({runtime.bundled_runtime_version(config) or 'no RUNTIME_VERSION stamp'})")

    # spec 005 FR-003/edge cases: wiped every `make up` so no credential or heartbeat from a
    # prior run survives into this session -- the smoke's own first assertion (the landing reads
    # "No agent connected") depends on this gate being genuinely clean. Spec 012 leaves one file
    # behind it: a `config.json` naming this profile's Keel, so the isolated home says which Keel
    # it belongs to (FR-004).
    print(f"[up] ({config.profile}) runtime-home: resetting {runtime.home_dir(config)} ...")
    runtime.reset(config)
    print(f"[up] ({config.profile}) runtime-home: ready, empty of a heartbeat, naming "
          f"{config.cloud_base_url} (the smoke starts the runtime itself)")

    print("[up] all gates passed")


def teardown(config: StackConfig | None = None) -> None:
    """Disconnects a runtime a scenario left running, then killpg the recorded process groups,
    wait, then `docker compose down -v` (contract order). Idempotent and safe when only part of
    the stack came up.

    **`kill` became `disconnect`** (spec 012 FR-003, design §11): teardown asks the runtime to go
    -- the same command keel-connect-skill's own `keel_disconnect.py` shells for a founder who
    says "keel disconnect" -- and reads the outcome that proves it went, instead of signalling a
    pid out of a heartbeat file and hoping. It stays idempotent (`not_running` is a normal,
    successful answer) and it still never fails on `did_not_stop`.

    Split-stacks (relay-design.md §12.5): every step below is scoped to `config.profile` --
    `teardown_all_processes(config.profile)` only ever kills that profile's own pid files, and
    `postgres.down(config)` only ever addresses that profile's own Compose project. The eval
    profile's own founder credentials (`stack/auth.py`) are cleared only when tearing down the
    eval profile itself -- a playground teardown has never touched, and must never touch, the
    eval account's stored credentials.
    """
    config = config or load_config()
    print(f"[down] ({config.profile}) disconnecting keel-runtime (if a scenario left one "
          f"running) ...")
    outcome = runtime.disconnect(config)
    print(f"[down] ({config.profile}) keel-runtime: {outcome.get('outcome')} "
          f"(via {outcome.get('via')})")
    if outcome.get("outcome") in runtime.DID_NOT_STOP_OUTCOMES:
        # Spec 012 FR-003 / keel-runtime's disconnect contract guarantee 3: `timeout` is the one
        # outcome a caller must treat as a failure -- but a teardown that raises leaves Postgres
        # and two JVMs behind, so it is printed loudly and the rest of the teardown runs.
        print(f"[down] ({config.profile}) WARNING: the runtime did not stop -- {outcome}")
    print(f"[down] ({config.profile}) stopping keel-web and keel-cloud ...")
    teardown_all_processes(config.profile)
    time.sleep(0.5)
    print(f"[down] ({config.profile}) stopping postgres ...")
    postgres.down(config)
    if config.profile == "eval":
        # postgres.down() drops the eval project's volume (-v) -- the founder account
        # stack/auth.py stored credentials for no longer exists once this returns
        # (founder-experience round 2).
        auth.clear_stored()
    print(f"[down] ({config.profile}) done")
