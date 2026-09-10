# Tasks: A stub issuer, and two founders

**Both halves are here.** Phases 1–4 and the two sections after them are the **first half**,
written and closed on 2026-09-09 before keel-cloud spec 032 existed. Phases 5–8 at the bottom are
the **second half** ([spec-second-half.md](spec-second-half.md)), written against keel-cloud
`master` `866a611` once 032 had landed.

---

# The first half

**Input**: [spec.md](spec.md) (FR-001..010, SC-001..004, the six clarifications) with
[plan.md](plan.md), against keel-cloud `canon/designs/google-sign-in-design.md` §10.1–§10.3,
§10.8 and §12 step 4.

**The siblings, read at**: keel-cloud `216f265` on `master` (the design; **not** its code — its
`032-google-sign-in` branch is being built in parallel), keel-web `b0a5015`, keel-runtime
`a0756b6`, keel-connect-skill `20cf41d`.

**Rules** (AGENTS.md): this repo owns no product code, never writes to a sibling repository, and
reports cross-repo gaps as `runs/DRIFT.md` entries with a bundle — this half found none, because
nothing in a sibling was run against it. `POLICY_VERSION` and `MARKS_VERSION` do not move. The
scenarios stay **nine** and stay deterministic; the two named LLM exceptions do not change in
number or in name.

---

## Phase 1: the issuer

- [X] T001 `stack/stub_oidc/keys.py` (FR-002): one RSA key from `openssl genrsa`, both PEM
      dialects parsed by a forty-line DER reader, RSASSA-PKCS1-v1_5 over SHA-256 with `pow()`, a
      public JWK, a compact RS256 JWS, and a `verify_rs256` that uses the **public** half alone.
      The decision (openssl for the key, `pow()` for the arithmetic, no new dependency) is argued
      in the module docstring, because it is the one place this repository does arithmetic.
- [X] T002 `stack/stub_oidc/server.py` (FR-001, FR-003, FR-004): `StubIssuer` (the state and the
      answers, no HTTP in it) plus a `ThreadingHTTPServer` handler. Discovery naming its own
      origin; `/jwks` and its `/jwks.json` alias; `/authorize` validating client, redirect URI,
      `state`, `nonce`, `response_type`, `scope` and `S256`, then the picker or the redirect;
      `/token` checking client id and secret (form **or** Basic), the code, the redirect URI and
      the PKCE verifier, burning the code on any redemption attempt. Everything else `404`. §10.8's
      prohibitions are quoted in the docstring so the next person to add something reads them.
- [X] T003 The picker (FR-004): `<h1>Choose an account</h1>` and one `<button>` per identity
      labelled with that identity's own **name**, carrying the whole authorize request back, plus
      a `Cancel` link that redirects with `error=access_denied`. `?identity=` and `?login_hint=`
      supply the click for a browserless caller.
- [X] T004 `?stub_break=<iss|aud|exp|sig|nonce|email_verified>` (§10.1): the negative-testing
      lever, landed with the stub and proven here, so **S-011** — which is the second half — starts
      from an issuer known to lie in exactly six declared ways.
- [X] T005 `stack/stub_oidc/__main__.py`: `python -m stack.stub_oidc --port 18090 --key <pem>`,
      taking its identities and client from `stack/oidc.py` rather than from argv, so there is no
      second copy on a command line to drift.

## Phase 2: the fourth service

- [X] T006 `stack/oidc.py` (FR-005): `NAME`, `_process_name`, `issuer_url`, `key_path`,
      `ensure_key`/`clear_key`, `cloud_env`, `is_up`, `up`. The two identities live here and
      nowhere else (§10.2), founder A keeping today's `FOUNDER_NAME`/`FOUNDER_EMAIL`.
- [X] T007 The ports (FR-006): `stack.toml` `[ports] oidc = 18090` and `[playground.ports]
      oidc = 18091`, `DEFAULT_PORTS`, `DEFAULT_PLAYGROUND_PORTS`, and `oidc_port` on the frozen
      `StackConfig` — defaulted and last, so a `StackConfig` built by hand still constructs.
- [X] T008 `stack/lifecycle.py` (FR-007): `boot()` is five gates with **`oidc.up` first**;
      `quick_gates_pass` gains `oidc.is_up`, so `make eval` can never attach to a stack with no way
      in; `teardown` calls `oidc.clear_key(config)` — the key never outlives the run that made it.
- [X] T009 `stack/processes.py` (FR-007): `teardown_all_processes` gains `oidc` /
      `oidc-playground`, each profile tearing down only its own; `require_port_free`'s message
      names the fourth port.
- [X] T010 `stack/cloud.py` (FR-008): `build_env` carries `KEEL_OIDC_ISSUER`,
      `KEEL_GOOGLE_CLIENT_ID`, `KEEL_GOOGLE_CLIENT_SECRET` and `KEEL_GOOGLE_REDIRECT_URI` through
      `oidc.cloud_env`. Inert until keel-cloud 032 lands, and **no** `KEEL_GOOGLE_ALLOWED_DOMAIN`.

## Phase 3: the proof

- [X] T011 `tests/test_stub_oidc.py` (FR-009) — **48 stackless tests** against a real server on a
      real socket: the two documents, the authorize→token walk with the ID token verified RS256
      against the published JWKS, the picker's markup, the refusals, the six `stub_break`s, both
      PEM dialects, `alg: none`, a token signed by another key, a tampered payload, and the
      lifecycle wiring including the fresh key.
- [X] T012 `tests/test_stub_oidc.py::test_the_second_half_is_untouched` (FR-010): `stack/auth.py`
      still has its password, and `evals/test_s010_*.py` / `test_s011_*.py` do not exist. That is
      the test that would notice the second half being started by accident.
- [X] T013 `README.md` and `AGENTS.md`: the fourth service, the ports, the two founders, and that
      only the first half has landed.

## Phase 4: the run of record

One stack session on the **eval** profile, 2026-09-09, with the playground profile left running
and untouched throughout (AGENTS.md: two referee sessions never share a profile).

**`make up` — the stub is gate one, and it passed:**

```
[up] (eval) stub-oidc: booting on 18090 ...
[up] (eval) stub-oidc: ready on 18090, signing for ['founder-a', 'founder-b']
[up] (eval) postgres: booting on 55432 ...
[up] (eval) postgres: ready on 55432
[up] (eval) keel-cloud: booting on 18080 (budget 120s) ...
```

**`curl`, on the eval port:**

| Ask | Answer |
|---|---|
| `GET /.well-known/openid-configuration` | `issuer` `http://localhost:18090`, and `authorization_endpoint`/`token_endpoint`/`jwks_uri` all absolute against it |
| `GET /jwks` | one key: `kty RSA`, `use sig`, `alg RS256`, `kid stub-1`, 2048-bit modulus |
| `GET /authorize` (no identity) | `200`, `<button type="submit">Eval Founder</button>` and `<button type="submit">Nour Haddad</button>` |
| `GET /authorize?client_id=nope…` | `400`, in the browser — never a redirect to an unregistered client's URI |
| `POST /token` with a wrong verifier | `400 {"error": "invalid_grant", "error_description": "PKCE code_verifier does not match code_challenge"}` |
| `GET /userinfo` | `404` |

**The walk** (`/authorize?identity=founder-a` → `/token`, then verify):

```
authorize -> http://localhost:18080/v2/auth/google/callback?code=KBZUkkiJV2Tj…&state=PpyaQ-OvKj1AQ_vfVKUN5Q
token   -> {"iss": "http://localhost:18090", "aud": "keel-eval-client", "azp": "keel-eval-client",
            "sub": "stub-founder-1", "email": "eval-founder@keel-e2e-eval.test",
            "email_verified": true, "name": "Eval Founder", "given_name": "Eval"}
VERIFIED RS256 against http://localhost:18090/jwks kid stub-1
```

The `state` came back verbatim and the `nonce` was asserted inside the token. The verification
read `n` and `e` off the published JWKS and recovered the PKCS#1 block with `pow(sig, e, n)` — the
private half was never in the verifier's hands.

**`make down`:**

```
[down] (eval) keel-runtime: not_running (via keel-connect-skill/scripts/keel_disconnect.py)
[down] (eval) stopping keel-web, keel-cloud and the stub issuer ...
[down] (eval) done
```

18090 stopped answering, `runs/.stack/oidc.pid` and `oidc-key.pem` were both gone, and the
playground stack on 18081/5174 was untouched.

- [X] T014 `make unit` green: **489 → 537**.
- [X] T015 The live walk above, on the eval profile, twice — once before and once after
      `ensure_key` was changed to mint a fresh key per boot.

## What the run could not measure, and why that is not this half's failure

**keel-cloud's gate did not pass, and nothing here can make it.** The `../keel-cloud` checkout is
mid-flight on its own `032-google-sign-in` branch (parallel work, `FounderAccount` reshaped and
`passwordHash()` already gone) and does not compile:

```
JdbcFounderAccountRepository.java:94: error: method of in class FounderAccount cannot be applied
FounderAccountService.java:78: error: cannot find symbol  passwordHash()
3 errors
```

That is a sibling's working tree, not a defect in a shipped commit, so it is **not** a
`runs/DRIFT.md` entry (this repo reports drift against what a sibling *ships*, and never writes to
a sibling to fix it). It is also exactly the situation §12 step 4 anticipates: this half is
*"provable entirely on its own"*, and everything the design asks it to prove — four routes, a
signed token that verifies, the refusals, the picker, the fourth gate, the ports, the four
variables — was proven with keel-cloud absent from the walk.

## What is left undone, and where it goes

**The second half, §10.4–§10.7 of the design — after keel-cloud 032.** In the order §12 step 7
gives, because each gates the next:

1. `stack/cloud.py`'s readiness gate off `/v2/setup` (which spec 032 deletes) and onto
   `GET /v2/me` with `ok_statuses={401}` — **first**, or nothing boots.
2. `stack/auth.py` shrunk: `FOUNDER_PASSWORD`, `account_exists`, `ensure_founder_account`,
   `clear_stored` and `runs/.stack/founder.json` deleted; `FOUNDER_NAME`/`FOUNDER_EMAIL` kept as
   assertion constants; `login_and_keel_session` moved onto `/v2/auth/google/start?login_hint=`.
3. `harness/browser.py:log_in` rewritten to the picker (`Continue with Google`, then the button
   named for the founder); `set_up` deleted with `/setup`.
4. `evals/conftest.py`'s `founder_credentials` → `founder_one` / `founder_two`.
5. **S-001, S-002 and S-003 reconfirmed green through the new login before a line of new scenario
   is written** — the proof the swap changed the door and not the house.
6. **S-010** (two founders, isolation, connect) and **S-011** (a token that isn't right), and the
   scenario set becomes eleven. S-004 gets its one changed login line and is re-run under
   `make eval-live` at the end.
7. The ledger and CANON §4's §1.0 row last, when S-010 and S-011 pass.

**Also waiting on 032**: the playground's one-time `make down PROFILE=playground` before the first
`make up` after `V35`/`V36` lands (§10.5) — its Postgres is a named volume and `founder_account` is
dropped and recreated.


---

# The second half

**Input**: [spec-second-half.md](spec-second-half.md) (FR-101..110, SC-101..103, the five
clarifications), against keel-cloud `canon/designs/google-sign-in-design.md` §10.4–§10.7 and §13.

**The siblings, read at**: keel-cloud `866a611` on `master` (**its code this time**: spec 032
merged at `465b4dd`, and spec 035 *one runtime per founder* at `866a611`), keel-web `07843b0`,
keel-runtime `d30dbd0`, keel-connect-skill `f06f481` (bundled runtime `0.1.0+d30dbd0`).

**Rules** (AGENTS.md): this repo owns no product code and never writes to a sibling. `POLICY_VERSION`
moves to **10** and the reasoning is judgement call 13 in `evals/policy.py`; `MARKS_VERSION` does
not move. The scenarios become **eleven** and S-004 is still the only live one.

## Phase 5: the door, before anything walks through it

- [X] T101 `stack/cloud.py`'s readiness gate off `/v2/setup` (deleted by spec 032) and onto
      `GET /v2/me` with `ok_statuses={401}` (§10.3), as `READY_PATH`/`READY_STATUS` so `is_up` and
      `up` cannot disagree. **First, or nothing boots.**
- [X] T102 **`KEEL_V2_FOUNDER_BASE_URL` becomes an origin.** Found reading spec 032, before
      `make up`: keel-cloud appends `/login` to it for every refused sign-in and the stored
      `return_to` for every successful one, and this stack had it at `.../p`. A harness fault, not
      a sibling's — `tests/test_config.py` holds it with the whole derivation written down.
- [X] T103 `stack/auth.py` shrunk to who the referee signs in as: `StubFounder`,
      `FOUNDER_ONE`/`FOUNDER_TWO` built from `stack/oidc.py`'s own list, `sign_in_session`,
      `read_me`, `login_and_keel_session`. `FOUNDER_PASSWORD`, `ensure_founder_account`,
      `account_exists`, `clear_stored` and `runs/.stack/founder.json` **deleted**;
      `stack/lifecycle.py` no longer imports `stack.auth` at all.
- [X] T104 `harness/browser.py:Auth.sign_in(identity)` — the link, the picker, the founder's own
      name, the callback. `set_up` deleted with `/setup`. `open_login`/`login_screen`/
      `auth_error_text` added for L1 and for S-011's reads. `Landing.greeting()` added, a pure
      getter, for the two-founder assertion.
- [X] T105 `evals/conftest.py`: `founder_credentials` → `founder_one`/`founder_two`, no I/O; the
      virgin-instance capture → **L1**, the login screen before anyone has signed in, which is now
      the same screen on a fresh instance and a busy one.

## Phase 6: every scenario, through the new door

- [X] T106 S-001, S-002 (both logins), S-003, S-005–S-009 and `corpus_scenario.run`: one line each.
- [X] T107 S-004's prelude, and **only** its prelude (decision 12): it is live and deselected from
      `make eval`, so isolation does not live there. Not run — it costs real money.
- [X] T108 `tests/test_stub_oidc.py`'s *"the second half is untouched"* becomes its inverse, plus a
      sweep over every scenario and the page objects for `/v2/setup`, `/v2/login`, `add_cookies`
      and `FOUNDER_PASSWORD` — read off the **code**, never the prose, so a file may still narrate
      what was deleted.

## Phase 7: the two new scenarios

- [X] T109 **S-010** `evals/test_s010_two_founders.py` (§10.6): A signs in, connects a scripted
      runtime and builds a project; B signs in in a fresh browser context; §4.3's ten reads, two
      writes and half-executing reading batch all answer B a bare 404; that 404 is byte-identical
      to one for an id that exists nowhere; A's revision and reading batches are unmoved; the
      participant page names the owner; A's runtime is still A's and B's creation is refused for
      want of **B's** agent.
- [X] T110 **S-011** `evals/test_s011_bad_token.py` (§10.7): six `stub_break`s, the cancel, the
      replay (G2), a state minted in a different browser (G1), and G8 when a run configures a
      domain — each with §5.5's exact line, `/v2/me` 401, and no wire detail on the screen.
- [X] T111 `tests/test_two_founders_and_refusals.py`: what a run would find out too late — that
      S-010 goes at *every* route §4.3 lists, that S-011's five lines are §5.5's verbatim, and that
      every `stub_break` the stub can produce is driven.
- [X] T112 The scenario set becomes **eleven** (`tests/test_scenario_set.py`), still one live.
- [X] T113 Policy **v10** (`evals/policy.py` judgement call 13, `tests/test_policy_v10.py`):
      `ORI-U1` stops exempting `setup`. An exemption for a screen that cannot occur is a hole a
      future capture could be tagged into, silently skipping rather than failing.

## Phase 8: the run of record

- [X] T114 `make unit`: **537 → 571**.
- [X] T115 `make up` (five gates, the stub first on 18090), `make eval-all`, one re-run of S-010,
      `make down` — one stack session, keel-cloud `866a611`, keel-web `07843b0`, keel-runtime
      `d30dbd0`, keel-connect-skill `f06f481`. **Every deterministic scenario green**, every one of
      them signed in through Google, no password anywhere in the run:
      `runs/INDEX-20260910T000441Z.html`. The table, the three harness faults and the evidence are
      in [README.md](../../README.md)'s own section.
- [X] T116 **No `runs/DRIFT.md` entry**, and that is the finding rather than the absence of one.
      §10.6 predicted the participant-page assertion would fail *"for a reason that has nothing to
      do with sign-in"*; it does not, because keel-cloud landed ownership (spec 031) before sign-in
      (spec 032), exactly as §12 step 2 said it should. The first two-founder instance this
      repository has ever booted found every leak §4.3 lists already closed.

## What is left undone

- **S-004 was not run.** It is live, model-backed and costs real money; its one changed login line
  is committed and `make eval-live` is the founder's call.
- **The playground profile's one-time `make down PROFILE=playground`** before its first
  `make up` after `V36` (§10.5): its Postgres is a named volume and `founder_account` was dropped
  and recreated. Not this half's to do, and named here so it is not a surprise.
- **G8, the allowed-domain refusal**, is driven only when a run sets `KEEL_GOOGLE_ALLOWED_DOMAIN`.
  S-011 records the skip with its reason and the line it would have asserted, so it is visible debt
  rather than silent.
- **CANON.md's §4 ledger** is keel-cloud's file and this repo does not write to a sibling. If a
  §1.0 row should now name S-010 and S-011, that is a keel-cloud edit.
