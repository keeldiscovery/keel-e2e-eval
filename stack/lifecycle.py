"""Whole-stack up/down/status, shared by the Makefile's CLI entrypoint and evals/conftest.py's
attach-or-boot fixture (contracts/stack-contract.md).
"""

from __future__ import annotations

import time

from stack import cloud, oidc, postgres, remote, runtime, web
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

    Spec 015 makes it **four**: the stub OIDC issuer (`stack/oidc.py`) is a long-running process
    of the same kind, and once keel-cloud's login is Google sign-in a stack whose issuer is down
    is a stack nobody can log into -- so "already up" must include it, or `make eval` would
    cheerfully attach to a stack with no way in.

    Spec 017 makes it **three answers instead of four processes** on the `remote` profile: there
    is nothing local to be up, so "already up" is the same three questions `make up
    PROFILE=remote` asks (`stack/remote.py:checks`) -- and they are the right ones, because a
    scenario attaching to a deployment that is mid-deploy would fail somewhere far less
    legible.
    """
    if config.is_remote:
        return remote.is_up(config)
    return (oidc.is_up(config) and postgres.is_up(config) and cloud.is_up(config)
            and web.is_up(config))


def boot(config: StackConfig) -> None:
    """Brings the whole stack up, printing each gate as it passes (FR-001, SC-001).

    **The `remote` profile boots nothing** (spec 017; e2e-matrix-design.md §11). It names three
    URLs that already answer and the whole of `make up PROFILE=remote` is asking them whether
    they do -- keel-web 200, keel-cloud's `/v2/me` 401, the issuer's discovery document 200 and
    naming itself. Starting a Postgres, a JVM or a Vite here would be starting a *second* Keel
    beside the one under test, and tearing one down would be tearing down somebody's staging box.
    """
    if config.is_remote:
        print("[up] (remote) nothing to start -- checking the three URLs this profile "
              "names")
        print(f"[up] (remote) web {config.web_base_url}, cloud {config.cloud_base_url}, "
              f"issuer {config.oidc_base_url}"
              f"{' (behind a gate as ' + config.gate_user + ')' if config.gate_credential else ''}")
        remote.require_answering(config)
        # The runtime home is still this run's own (spec 012 FR-004, and S-012's own temp home):
        # `runs/.stack/keel-home-remote`, wiped, carrying a `config.json` that names the *remote*
        # Keel. That is what makes `KEEL_BASE_URL` for the runtime the cloud URL without anybody
        # exporting anything.
        print(f"[up] (remote) runtime-home: resetting {runtime.home_dir(config)} ...")
        runtime.reset(config)
        print(f"[up] (remote) runtime-home: ready, naming {config.cloud_base_url}")
        print("[up] all gates passed")
        return
    # The stub issuer comes up **first** (keel-cloud google-sign-in-design.md 10.3): keel-cloud
    # fetches the discovery document lazily, on the first sign-in rather than at startup, so
    # nothing here depends on the order -- but bringing it up first means the first login of a run
    # is never also the first discovery of a dead port. It is stateless: nothing of it survives.
    print(f"[up] ({config.profile}) stub-oidc: booting on {config.oidc_port} ...")
    oidc.up(config)
    print(f"[up] ({config.profile}) stub-oidc: ready on {config.oidc_port}, signing for "
          f"{[identity.id for identity in oidc.STUB_IDENTITIES]}")

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
    `postgres.down(config)` only ever addresses that profile's own Compose project, and
    `oidc.clear_key(config)` only ever removes that profile's own signing key. There is no stored
    founder credential left to scope: it went with the password (google-sign-in-design.md §10.4).
    """
    config = config or load_config()
    if config.is_remote:
        # A no-op, and deliberately a loud one (spec 017). There is nothing local to stop, and
        # the thing this profile names is a deployment other cells may be mid-run against -- a
        # referee that could tear it down is a referee with a footgun. The runtime a scenario
        # left running is disconnected, because that one *is* this machine's.
        print("[down] (remote) nothing to stop -- this profile starts no process")
        outcome = runtime.disconnect(config)
        print(f"[down] (remote) keel-runtime: {outcome.get('outcome')} "
              f"(via {outcome.get('via')})")
        print("[down] (remote) done")
        return
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
    print(f"[down] ({config.profile}) stopping keel-web, keel-cloud and the stub issuer ...")
    teardown_all_processes(config.profile)
    time.sleep(0.5)
    print(f"[down] ({config.profile}) stopping postgres ...")
    postgres.down(config)
    # The stub issuer keeps nothing but its signing key, and that key never outlives the run that
    # made it (spec 015; keel-cloud google-sign-in-design.md 10.3). Both profiles, not just eval:
    # each clears only its own.
    oidc.clear_key(config)
    # Nothing else to clear. `runs/.stack/founder.json` and `stack.auth.clear_stored()` went
    # with the password (keel-cloud google-sign-in-design.md §10.4): an account exists the moment
    # somebody signs in with Google, the stub is stateless, and this harness therefore persists
    # no credential of any kind between runs.
    print(f"[down] ({config.profile}) done")
