# Feature Specification: the remote profile

**Feature Branch**: `remote-profile-and-gated-stub`

**Created**: 2026-09-10

**Status**: Implemented, stackless. `make unit`: **638** before, **712** after, green. **No run was
taken**: `make up PROFILE=remote` against the staging twin is step 3 of the design's §13 order and
the twin does not exist yet (keel-cloud's spec `036-staging-twin` builds it). Nothing here was
exercised against a deployment, and nothing here changed how the eval or playground profiles
behave — which is the invariant the whole spec is written around and the thing the existing 638
tests prove.

**Input**: keel-cloud `canon/designs/e2e-matrix-design.md` §2 (*"the stack cannot yet point at a
remote"*), §4.2 (the gate), §5.3 (what a cell is), §6.4 (where a verdict is recorded), §11 (*"a
`remote` profile in `stack/config.py`: URLs, not processes; `make eval PROFILE=remote` against a
base URL; the gate credential on the login step"*).

## What changes, stated first

**This repository has two profiles and both of them are a stack.** `eval` and `playground` differ
in ports, in a Compose project and in a runtime home; they are identical in the only thing that
matters here — both *start* Postgres, keel-cloud, keel-web and the stub issuer as local processes
and own their lifecycle. There has never been a way to say *"the thing under test is over there,
and it is already running."*

`remote` is that third column:

| | `eval` | `playground` | `remote` |
|---|---|---|---|
| what `make up` does | boots four processes | boots four processes | **asks three URLs whether they answer** |
| what `make down` does | kills them, drops the volume | the same, its own | **nothing** |
| where the URLs come from | ports 18080 / 5173 / 18090 | 18081 / 5174 / 18091 | `KEEL_REMOTE_*` |
| the runtime home | `runs/.stack/keel-home` | `…-playground` | `…-remote`, naming the remote Keel |
| the gate | none | none | basic auth on the issuer's origin, when set |

**The invariant, stated once and held everywhere**: §11's *the referee is not modified to
accommodate a deployment*. Every line this spec adds is reached only when
`config.profile == "remote"`. The scenarios are untouched. `harness/browser.py`'s `Auth.sign_in`
makes the same clicks in the same order. The browserless sign-in walks the same three hops. What
differs is a base URL, and — when a deployment has Caddy's basic auth in front of its issuer's
picker — a credential on exactly two requests: Playwright's browser context (scoped to the
issuer's origin) and the one `requests` call that follows `?identity=`.

**And the cell's own two calls.** On staging a cell signs in as *its own* founder (design §4.3),
so the spec carries `register_cell_identity(config, label)` — the before — and
`label_cell_identity(config, id, label)` — the verdict, after. `identity_to_sign_in_as(config,
label)` is what a scenario calls: it registers on remote and returns the built-in *Eval Founder*
everywhere else, with no I/O at all, which is how one scenario runs on three profiles.

## User scenarios

### The founder, from their Mac, against the twin (design §13 step 3)

```bash
export KEEL_REMOTE_WEB_URL=https://eval.keeldiscovery.com
export KEEL_REMOTE_GATE_USER=harness
export KEEL_REMOTE_GATE_PASSWORD=...          # from the founder's own manager, never a file here
make up PROFILE=remote                        # three questions, no processes
make eval K=s001 PROFILE=remote               # the journey, against the twin
make down PROFILE=remote                      # a no-op that says so
```

`make up PROFILE=remote` prints three lines and passes or fails on them:

```
[up] (remote) keel-web: ok -- https://eval.keeldiscovery.com/ -- 200, expected 200
[up] (remote) keel-cloud: ok -- https://eval.keeldiscovery.com/v2/me -- 401, expected 401
[up] (remote) issuer: ok -- .../oidc/.well-known/openid-configuration -- 200, expected 200
```

### A cell, on a runner (design §5.3)

1. `KEEL_REMOTE_CELL=windows-copilot-py3.9` and the three URLs come from the workflow.
2. `register_cell_identity(config, "2026-09-11 · windows · copilot · py3.9 — running")` → the
   identity to sign in as, named for the cell and the day.
3. The journey, through the gate, against the twin, with the runtime's `KEEL_BASE_URL` pointed at
   the twin's cloud URL by the run's own temp home.
4. `label_cell_identity(config, identity.id, "… — PASSED 5.0 (S-001)")`.

## Requirements

- **FR-001** `remote` is a third value of `PROFILE`, accepted everywhere `eval` and `playground`
  are: `make up`, `make down`, `make eval`, `make eval-all`, `python -m stack.cli`, and
  `KEEL_EVAL_PROFILE`.
- **FR-002** The three base URLs come from `KEEL_REMOTE_WEB_URL` (required),
  `KEEL_REMOTE_CLOUD_URL` (default: the web URL) and `KEEL_REMOTE_OIDC_URL` (default:
  `<web>/oidc`). A missing web URL is a `ConfigError` naming the variable, raised before anything
  connects to anything. Trailing slashes are stripped from all three.
- **FR-003** `make up PROFILE=remote` **starts no process**. It asks three questions — keel-web
  `/` answers 200, keel-cloud `/v2/me` answers 401, the issuer's discovery document answers 200
  *and names itself* — prints each, and fails naming the ones that did not answer.
- **FR-004** `make down PROFILE=remote` stops nothing but a runtime this machine left running. It
  never touches Postgres, a Compose project, a pid file or a signing key, because none of those
  are its.
- **FR-005** The runtime home is this profile's own (`runs/.stack/keel-home-remote`, the S-012
  shape), reset by `make up`, carrying a `config.json` that names the **remote cloud URL** — so
  `KEEL_BASE_URL` for the runtime is the cloud URL without anybody exporting anything.
- **FR-006** When `KEEL_REMOTE_GATE_USER` and `KEEL_REMOTE_GATE_PASSWORD` are both set, every
  Playwright browser context carries `http_credentials` **scoped to the issuer's origin**, and the
  browserless sign-in sends the same basic auth on the `/authorize` hop **and on no other
  request**. One without the other is a `ConfigError`.
- **FR-007** `register_cell_identity(config, label, …)` POSTs `{id, name, email, label}` to
  `<oidc>/identities` with the gate credential and returns a `StubFounder` to sign in as. It never
  sends a `sub`. A non-201 raises, carrying the status and the body.
- **FR-008** `label_cell_identity(config, id, label)` PATCHes `{"label": …}` and nothing else.
- **FR-009** `identity_to_sign_in_as(config, label)` returns the built-in `FOUNDER_ONE` on any
  non-remote profile, **with no HTTP at all**.
- **FR-010** A cell's identity id is named for `KEEL_REMOTE_CELL` and the day, and two runs of one
  cell in the same second are two identities (cells never delete; §8).
- **FR-011** The eval and playground profiles are **unchanged in behaviour**: same URLs, same four
  processes, same teardown, no credential anywhere, and the remote environment variables ignored
  even when the operator's shell has them exported.

## What is deliberately not built

- **No scenario is converted.** `evals/test_s001_smoke.py` and its siblings still compose
  `http://localhost:{stack.web_port}` inline, and `tests/test_bundled_runtime.py` pins that they
  do. Parameterising the journey — by host, and by profile — is spec `019-journey-through-a-host`,
  which is being written on another branch in this repository right now; doing it here would have
  put two agents in the same nineteen files. What this spec lands is the profile, the URLs, the
  gate and the two registry calls those scenarios will use.
- **No deploy, no workflow, no schedule.** keel-cloud's `036` builds the twin; spec `020` runs the
  matrix.
- **No secret in this repository.** The gate password is read from the caller's shell and written
  nowhere — not to a run bundle, not to `runs/.stack/`, not to a log line (the `up` banner prints
  the gate *user*, never the password).
- **No retry and no wait-for-deploy.** If the twin is mid-deploy, `make up PROFILE=remote` fails
  with the status it got. A workflow's own gate is spec 020's job (§6.3).
- **No sibling-validation exemption.** A remote run still resolves `stack.toml`'s four sibling
  paths, because the runtime a scenario starts is still the one inside keel-connect-skill. A
  runner that has no siblings is a question spec 020 answers when it has one.
