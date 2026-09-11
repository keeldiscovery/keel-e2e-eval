# Implementation Plan: the remote profile

**Branch**: `remote-profile-and-gated-stub` | **Spec**: [spec.md](spec.md) | **Tasks**:
[tasks.md](tasks.md)

## 1. Where the new code goes

| File | What it is |
|---|---|
| `stack/config.py` | `PROFILES` gains `"remote"`; `remote_urls()` and `remote_gate()` read the environment; `StackConfig` gains five defaulted fields (three URLs, two halves of a credential) and four properties — `web_base_url`, `oidc_base_url`, `is_remote`, `gate_credential` — beside the `cloud_base_url` that was already there. `load_config` takes an `env` argument, so every rule here is testable without touching `os.environ`. |
| `stack/remote.py` | **New.** The three checks (`checks`, `is_up`, `require_answering`), the gate credential accessor, and the registry calls a cell makes: `register_cell_identity`, `label_cell_identity`, `registered_identities`, `identity_to_sign_in_as`, plus `cell_name`/`new_identity_id`. |
| `stack/lifecycle.py` | Three branches, each one line deep: `quick_gates_pass` asks `remote.is_up`, `boot` asks the three questions and resets the runtime home, `teardown` disconnects the runtime and stops. |
| `stack/cli.py` | Nothing but a docstring, a friendlier "already answering" line, and `RemoteNotAnswering` in the caught set — `PROFILES` did the rest, so `make up PROFILE=remote` needed **no Makefile change**. |
| `stack/oidc.py`, `stack/auth.py` | `issuer_url` and `cloud_base` read the config's own base URLs instead of composing `http://localhost:<port>`; `sign_in_session` puts `auth=config.gate_credential` on the `/authorize` hop. Both are identity transforms on the local profiles. |
| `harness/browser.py` | `gate_http_credentials`, `context_options`, `new_context` and `GatedBrowser` — the wrapper that adds the credential to `new_context` and delegates everything else. `Auth.sign_in` gains a paragraph of docstring and no code. |
| `evals/conftest.py` | The `browser` fixture yields `GatedBrowser(b, config)` **only** when there is a gate, and the login-screen capture reads `stack.web_base_url`. |
| `tests/test_remote_profile.py` | **New**, stackless, 40 tests. Every one of them has a local twin in the same file. |

## 2. The three decisions worth writing down

**The credential goes on the browser *context*, not into nineteen scenarios.** Nineteen scenario
modules call `browser.new_context()`, and each of those calls is the referee's own contract with
the product. Threading a credential through all of them would be modifying the referee to
accommodate a deployment, which is the one thing §11 forbids. So `evals/conftest.py` wraps the
session's `Browser` once — and only when `gate_http_credentials` is not `None`, so on the eval and
playground profiles the fixture yields the same raw object it always yielded and `GatedBrowser` is
never constructed. The credential is scoped to the issuer's origin, because keel-web's pages and
keel-cloud's `/v2/*` are as open on staging as they are in production and a context that sent a
password everywhere would hand it to whatever a redirect pointed at.

**`remote_urls`/`remote_gate` live in `config.py`, and the HTTP lives in `remote.py`.** The
obvious shape — one `stack/remote.py` holding everything — is a cycle: `config` would import
`remote` for the URLs and `remote` would import `auth` (for `StubFounder`), which imports `oidc`,
which imports `config`. Reading two environment variables is not HTTP and belongs where the other
configuration parsing is; everything that talks to a network is in `remote.py`, which may import
freely.

**A remote `StackConfig` still carries ports, and they are the ones its URLs name.** A profile
that starts no process has no port, but `StackConfig` is frozen and a dozen call sites print one.
Deriving 443 from `https://…` (and the explicit port when there is one) means a printed config
says something true rather than something invented, and `postgres_port` is `0` because there is no
Postgres to name.

## 3. What is deliberately not built

- **No scenario conversion.** See the spec's own last section: `019-journey-through-a-host` is in
  these files on another branch, and `tests/test_bundled_runtime.py` pins S-001's inline
  `f"localhost:{stack.cloud_port}"` as the thing that names which Keel it reached. What this spec
  lands is what that one will use.
- **No `KEEL_REMOTE_*` reading outside `config.py`.** One place parses the environment; everything
  else reads the config it was handed. A scenario never calls `os.environ`.
- **No second `Auth` class, no `if remote:` in a page object.** The gate is transport; the screens
  are the screens.
- **No lifecycle for the deployment.** `boot` cannot deploy and `teardown` cannot stop: on staging
  the box has other cells running against it, and a referee that could tear down the thing it is
  refereeing is a referee with a footgun.

## 4. Risks, and what each one costs

| Risk | Cost | What is done about it |
|---|---|---|
| An operator with `KEEL_REMOTE_WEB_URL` still exported runs `make eval` | a local run silently pointed at staging | The variables are read **only** when the profile is `remote`; a test asserts an eval config built with all of them exported is the local one. |
| Half a gate credential (a typo in one variable name) | a 401 from Caddy that reads as a broken login | Both or neither: one without the other is a `ConfigError` naming both variables. |
| The gate credential reaching a run bundle or a log | a password in a repository | Nothing writes it: the `up` banner prints the gate *user*, `versions.json` carries ports and paths, and the credential exists only in the config object and two request calls. |
| The twin is mid-deploy when a cell starts | a red cell with an unreadable failure | The three checks run first and name what did not answer. A workflow-level gate is spec 020's (§6.3). |
| `/v2/me` answering 200 rather than 401 | the harness carrying somebody's session, or a URL that is not keel-cloud | It is a failure, with the status printed. |
