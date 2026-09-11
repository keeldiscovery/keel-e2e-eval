# Implementation Plan: the gated registry stub

**Branch**: `remote-profile-and-gated-stub` | **Spec**: [spec.md](spec.md) | **Tasks**:
[tasks.md](tasks.md)

## 1. Where the new code goes

| File | What it is |
|---|---|
| `stack/stub_oidc/identity.py` | **New.** The `Identity` record, the client id and secret, and the two built-in founders — moved down out of `stack/oidc.py`, which now re-exports them. The move is what lets the package stand alone in a container (§2 below). |
| `stack/stub_oidc/registry.py` | **New.** `Entry`, `Registry`, `RegistryError`. The JSON file, the newest-first order, the atomic write, the derived `sub`, and `registered_by` — which is the fact invariant M6 is enforced against. |
| `stack/stub_oidc/server.py` | `StubIssuer` gains `registry` and `gated`; `identities` becomes a property (registrations newest first, then built-ins); `may_sign_in_as`/`may_register` are the two rules; the handler grows `GET`/`POST /identities` and `PATCH /identities/<id>`, the gate check at the top of `/authorize`, and a label under each registered button. |
| `stack/stub_oidc/__main__.py` | `--gated`, `--registry`, `--host`; defaults now come from `identity.py`, so this module imports nothing outside the package. |
| `stack/oidc.py` | Re-exports the four names. Passes **neither** new flag, which FR-015 pins. |
| `stack/containers/oidc/Dockerfile` | **New.** `python:3.12-slim` + `openssl`, two `COPY`s, `ENTRYPOINT ["python", "-m", "stack.stub_oidc"]`. |
| `Makefile` | **One additive target**, `oidc-image`, and two comment lines on `up`. Nothing existing is edited: another branch is in this file at the same time. |
| `tests/test_stub_oidc_registry.py` | **New**, stackless, 34 tests: every rule in the spec, and every one of them paired with the ungated behaviour it must not disturb. |

## 2. The three decisions worth writing down

**The identities moved down a level, and `stack/oidc.py` re-exports them.** The design says the
staging twin runs *"the same `stack/stub_oidc/` package"* as a container. It could not: the
package's `__main__` imported `stack.oidc` for its defaults, which imports `requests`,
`stack.config` and `stack.processes` — a `pip install` in the image, a `REPO_ROOT` pointing at a
checkout that is not there, and a dependency graph in which the issuer needs the harness. Moving
the data into `stack/stub_oidc/identity.py` makes the package self-contained (the image installs
**no Python package at all**) and costs nothing: `oidc.FOUNDER_A`, `oidc.STUB_IDENTITIES`,
`oidc.CLIENT_ID` are the same objects under the same names, and spec 015's own tests, which assert
against exactly those names, were not touched.

**The picker lists everything; the *choice* is what is authorized.** §4.3 says the picker renders
`GET /identities`'s list. The alternative — filtering the page to what this principal may pick —
was considered and rejected: it makes the founder's page and the harness's page two different
pages, and the harness never renders the page anyway (it passes `?identity=`). So the list is the
list, and `may_sign_in_as` refuses at the one place a wrong choice would matter, with a 403 that
names the identity it refused. M6 holds either way; this way the page is one page.

**A refusal reads the request body first.** Found while writing the tests, and it is the kind of
defect a stub that is *"deliberately strict"* must not have: this is HTTP/1.1 with keep-alive, and
a 403 that answered without draining the body left it in the socket, so the next request on that
connection began parsing at `{"label":` and came back a garbled 400 from a route nobody called.
`do_POST`/`do_PATCH` now read `Content-Length` bytes before anything is decided.
`test_a_refused_write_does_not_poison_the_keep_alive_connection` is the regression.

## 3. What is deliberately not built

- **No `cryptography`.** `keys.py` is unchanged: `openssl genrsa` once, pure-Python RS256 after.
  The image installs the `openssl` binary explicitly rather than trusting the base to carry it.
- **No new state.** The registry is a list in a file. No database, no session, no second client —
  the three things google-sign-in-design §10.8 names as the signal that something belonging in
  keel-cloud has drifted into the harness.
- **No change to `tests/test_stub_oidc.py`.** If this feature had needed one, it would have
  changed the ungated contract, which is the one thing it may not do.
- **No image build in CI, and none required of the implementer.** `make oidc-image` is written and
  the Dockerfile is reviewable; building it is a founder's own command against their Colima
  socket, and pushing it is spec 020's workflow.

## 4. Risks, and what each one costs

| Risk | Cost | What is done about it |
|---|---|---|
| Caddy is configured to forward the header on a route the stub does not gate | a route reachable without the gate | The stub refuses *every* gated route without the header, so a Caddy block that missed one fails closed rather than open. |
| Two cells register the same id in the same second | one cell signs in as the other's founder and the verdicts cross | Ids carry a random tail (`stack/remote.py:new_identity_id`), and a duplicate is a 409 rather than an overwrite. |
| The registry file is written by two requests at once | a lost registration | One process, one lock, and an `os.replace` per write. Eighteen cells a week is not a concurrency problem; a partial read would have been. |
| The image drifts from the package | staging refereed by different bytes | The Dockerfile copies the package; there is no second implementation to drift from. A tag is a sha. |
