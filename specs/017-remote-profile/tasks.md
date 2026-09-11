# Tasks: the remote profile

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**:
`remote-profile-and-gated-stub`

`make unit`: **638** before, **712** after (40 of the new ones are this spec's), green. No stack
was started, no `make up`/`make down`/`make eval` was run against anything, and no model was
called.

## Phase 1 — read before writing anything

- [X] T001 keel-cloud `canon/designs/e2e-matrix-design.md` in full — §2's *"the stack cannot yet
      point at a remote"*, §4.2 (the gate), §5.3 (what a cell is), §6.4 (the verdict), §11, §12.
- [X] T002 `stack/config.py`, `stack/cli.py`, `stack/lifecycle.py`, `stack/oidc.py`,
      `stack/auth.py`, `stack/runtime.py` — the profile machinery as it stands, and where a URL is
      composed from a port (nine places in `stack/`, nineteen more in `evals/`).
- [X] T003 `harness/browser.py`'s `Auth` and `evals/conftest.py` — the login step and the fixtures
      that hand it a browser. Finding that shaped the plan: `browser.new_context()` is called in
      nineteen scenario modules, so the credential has to ride the fixture.
- [X] T004 `specs/016-copilot-e2e/` — the spec/plan/tasks shape this repository uses, and S-012's
      own run-bundle temp home, which is the shape FR-005 keeps.

## Phase 2 — the profile

- [X] T005 `stack/config.py`: `REMOTE_PROFILE`, the five variable names, `remote_urls`,
      `remote_gate`, `_port_of`.
- [X] T006 `StackConfig`'s five new **defaulted, last** fields and its four new properties.
      `replace(config, profile="playground", cloud_port=18081)` — which half this repository's
      tests do — still constructs, and a test says so.
- [X] T007 `load_config(..., env=…)` so the environment is an argument, not a global.

## Phase 3 — no processes

- [X] T008 `stack/remote.py`: `checks`/`is_up`/`require_answering`, and `gate_auth`.
- [X] T009 `stack/lifecycle.py`'s three branches. `boot` resets the runtime home (FR-005) and
      starts nothing; `teardown` disconnects a runtime and stops.
- [X] T010 `stack/cli.py`: `RemoteNotAnswering` in the caught set and a line that reads right for
      a profile with no ports. **No Makefile change was needed** for `up`/`down` — `PROFILES` is
      what the CLI validates against.

## Phase 4 — the gate

- [X] T011 `harness/browser.py`: `gate_http_credentials` (scoped to the issuer's origin),
      `context_options`, `new_context`, `GatedBrowser`.
- [X] T012 `evals/conftest.py`: the `browser` fixture wraps **only** when there is a gate; the
      login-screen capture reads `stack.web_base_url`.
- [X] T013 `stack/auth.py`: `auth=config.gate_credential` on the `/authorize` hop and nowhere
      else; `cloud_base` reads `config.cloud_base_url`.
- [X] T014 `stack/oidc.py`: `issuer_url` reads `config.oidc_base_url`, and `cloud_env`'s callback
      URI is built from `config.cloud_base_url`.

## Phase 5 — the cell's own two calls

- [X] T015 `register_cell_identity` (POST, gate credential, no `sub` sent, `StubFounder` back).
- [X] T016 `label_cell_identity` (PATCH, label only).
- [X] T017 `identity_to_sign_in_as` — the one call a scenario makes, and no I/O off remote.
- [X] T018 `cell_name`/`new_identity_id` — named for `KEEL_REMOTE_CELL` and the day, with a random
      tail so two runs of one cell are two founders.

## Phase 6 — the tests and the README

- [X] T019 `tests/test_remote_profile.py`, 40 stackless tests, each paired with the local
      behaviour it must not disturb: the URLs and their defaults, the port derivation, the gate
      credential and its scoping, the browser wrapper, boot/teardown/status, the three checks and
      their failure modes, the registry helpers with mocked HTTP, and the browserless sign-in's
      `auth=` on one hop of three.
- [X] T020 README: a *remote profile* section and the environment-variable table.
- [X] T021 `make unit`: 712 passed.

## What is owed, and to whom

- [ ] **A run.** `make up PROFILE=remote` and `make eval K=s001 PROFILE=remote` against the twin
      is step 3 of the design's §13 order, and the twin does not exist yet: keel-cloud's spec
      `036-staging-twin` provisions the box, points DNS at it, and deploys. Until then nothing in
      this spec has been exercised against a deployment, and the spec says so at the top.
- [ ] **The scenarios.** `019-journey-through-a-host` is what turns
      `web_base = f"http://localhost:{stack.web_port}"` into `stack.web_base_url` and calls
      `identity_to_sign_in_as`. It is on another branch in this repository right now, which is
      why this one did not touch those files.
