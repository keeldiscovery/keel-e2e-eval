# Feature Specification: A stub issuer, and two founders — the second half

**Feature Branch**: `015-second-half` (merged into `master`)

**Created**: 2026-09-09

**Status**: **Implemented.** See [tasks.md](tasks.md)'s second half for the task list and the run
of record.

**Input**: keel-cloud `canon/designs/google-sign-in-design.md` §10.4–§10.7 and §13, and this
spec's own [first half](spec.md), which built the issuer this half signs in through. The first
half's closing section — *"What is left undone, and where it goes"* — is this half's task list,
in the order §12 step 7 gives.

The siblings, read at these commits:

| Sibling | Branch | Commit | What this half depends on |
|---|---|---|---|
| keel-cloud | `master` | `866a611` | **its code, at last**: `GET /v2/auth/google/start` and `/callback`, `/v2/setup` and `POST /v2/login` deleted, `KEEL_OIDC_ISSUER`/`KEEL_GOOGLE_*` read, ownership owner-scoped on every founder route |
| keel-web | `master` | `07843b0` | the login screen is one *Continue with Google* control; the five `auth_error` lines; the setup route retired |
| keel-runtime | `master` | `d30dbd0` | **nothing**: the runtime holds a device code and then a bearer token, never a cookie, and has no notion of how the founder logged in |
| keel-connect-skill | `master` | `f06f481` | nothing |

## What changes, stated first

**The referee stops typing a password, because there is no longer one to type.** The first half
built an issuer so this could happen without the harness inventing a shortcut; this half spends it.
`stack/auth.py`'s `FOUNDER_PASSWORD` is deleted, `harness/browser.py:Auth.log_in(email, password)`
becomes `Auth.sign_in(identity)`, and what that method does is click the real *Continue with
Google*, click a founder's own name on the stub's account picker, and come back through the real
callback — `/v2/auth/google/start`, `/authorize`, the picker, `/v2/auth/google/callback`, the token
exchange, the ID-token verification, account creation-or-refresh, session rotation, the
`keel_session` open, and the redirect home. That is more of the real login than the password path
ever covered, in three clicks' worth of code.

Two things follow that the password could not have proved, and they are the two new scenarios.

1. **There can be two founders now**, so *whose project is this* is a question with a wrong answer
   for the first time. S-010 asks it of every route §4.3 lists.
2. **A sign-in can be refused**, and §5.5 is a table of ten failure modes and five founder-voiced
   lines that nothing executed. S-011 executes it.

## Clarifications

### `login_hint` on `/start` does not reach the issuer — **the identity goes on keel-cloud's own authorize URL**

§10.4 writes the browserless path as `GET /v2/auth/google/start?return_to=/&login_hint=<sub>` and
says *"the `login_hint` goes on the start call and is carried through by the stub"*. It is not.
`GoogleStartController.start` reads exactly one query parameter, `return_to`, and
`GoogleSignIn.start` builds the authorize URL from the discovery document and its own
configuration — an extra parameter on `/start` is dropped on the floor, and the browserless caller
lands on the picker's HTML with nothing to click.

So `stack/auth.py:sign_in_session` follows the redirect **by hand**: `/start` with
`allow_redirects=False`, then `GET <the Location keel-cloud produced>&identity=founder-a`. That is
the same code path with the click supplied, exactly as §10.2 intends — keel-cloud's own `state`,
`nonce`, `redirect_uri` and PKCE challenge are the ones that travel, untouched — and it is *more*
honest than the sketch, because the authorize request is built by the client under referee rather
than by the harness. It also gives one assertion the sketch could not: the `Location` must name
**this profile's stub issuer**, so a `KEEL_OIDC_ISSUER` that never reached the JVM fails at the
first sign-in with a sentence saying so, rather than as nine red scenarios.

### The button is a **link** — `get_by_role("link", …)`, never `"button"`

§10.4's sketch is `page.get_by_role("button", name="Continue with Google")`. keel-web's
`GoogleSignInButton` renders `<a class="btn google" href="/v2/auth/google/start?return_to=…">` —
deliberately, because signing in is a navigation and not a fetch (spec 014 FR-001) — so its
accessible role is `link` and a button locator matches nothing on the real screen. Corrected in
`harness/browser.py`, with the reason written beside the constant so it is not "fixed" back.

The picker's own control **is** a `<button>`, labelled with the identity's name, exactly as §10.2
says. One test asserts that the label `Auth.sign_in` asks Playwright for is the label
`picker_html` writes, so the harness's two halves cannot drift apart silently.

### `KEEL_V2_FOUNDER_BASE_URL` is an **origin** — a harness fault, found before `make up`

`stack/cloud.py` set it to `http://localhost:5173/p`, left over from keel-cloud's deleted
`keel.v2.founder-base-url` *property*, which had a project path baked onto it for `OpenWebUrls`.
The env var that outlived that property is now the origin three things derive from: `/connect`,
`/v2/auth/google/callback`, and — since spec 032 — **`/login`**, where every refused sign-in lands
(`AuthError.location`) and, plus the stored `return_to`, where a successful one is sent. Its own
default in `application.yml` is a bare `http://localhost:5173`.

Left at `.../p`, this stack would have sent a signed-in founder to `/p/` and a refused one to
`/p/login?auth_error=…` — both of which keel-web's router resolves through `/p/:projectId/*`, as a
project whose id is the word *login*. Every scenario would have gone red at its first step for a
reason none of their screens could have explained. It is the bare origin now, and
`tests/test_config.py` says why. **Not a `runs/DRIFT.md` entry**: nothing in a sibling was wrong.

### Isolation is S-010, not S-004 — the design's decision 12, taken as written

The brief for this half called it *"S-004's second founder"*. S-004 is *the stranger who gives
orders*: live, model-backed, and deselected from `make eval` and `make eval-all`. Isolation
assertions there would be proven only when somebody opts into a paid model run, which is the
opposite of what an isolation test is for. S-004 gets its one changed login line and nothing else.

### The allowed-domain refusal is conditional, and says so in the bundle

`stack/oidc.py:cloud_env` sets no `KEEL_GOOGLE_ALLOWED_DOMAIN` — the open posture is what the
scenarios exercise (§10.3) — and neither stub identity declares an `hd`, so on an ordinary run
there is no wrong domain to be wrong about. S-011 drives G8 when a run configures a domain and
otherwise records a step naming the variable, the reason, and the line it would have asserted. It
is never silently absent.

## User Scenarios & Testing

### US1 — every existing scenario signs in the way a founder does (P1)

**Acceptance**

1. No scenario, page object or fixture mentions `/v2/setup`, `POST /v2/login`, a password, or a
   cookie this harness did not receive from a real `Set-Cookie` (`tests/test_stub_oidc.py`,
   swept over code and never over prose).
2. `stack/auth.py` has no `FOUNDER_PASSWORD`, `ensure_founder_account`, `account_exists` or
   `clear_stored`, and `runs/.stack/founder.json` is gone; `FOUNDER_NAME`/`FOUNDER_EMAIL` survive
   as assertion constants and founder A still answers to *Eval Founder*.
3. `harness/browser.py:Auth.set_up` is deleted with `/setup`; `Auth.sign_in` clicks the link, then
   the picker's button named for the founder.
4. `stack/cloud.py`'s readiness gate is `GET /v2/me` expecting `401`.
5. S-001, S-002, S-003 and S-005–S-009 pass through the new login with no other change.

### US2 — two founders, one instance (P1)

**Acceptance** (`evals/test_s010_two_founders.py`, deterministic, in `make eval`) — §10.6's own
eight steps: A signs in and is greeted by name; A connects a runtime and builds a project; B signs
in in a fresh browser context and is greeted as themselves while A's session still reads A's; B's
project list is empty; every one of §4.3's ten reads, its two writes and its half-executing reading
batch answers B a **bare 404**; that 404 is byte-identical to the 404 for an id that exists
nowhere; the participant page names the project's **owner**; and A's runtime is still A's.

### US3 — a token that isn't right (P1)

**Acceptance** (`evals/test_s011_bad_token.py`, deterministic, in `make eval`) — all six
`stub_break`s, the cancel, the replay (G2), a `state` minted in a different browser context (G1),
and the allowed domain when a run configures one. Every case: the browser is on `/login`, the
visible line is §5.5's own for that rule and is a **sentence**, `GET /v2/me` is `401`, and no wire
token, rule id, status code or JSON is anywhere on the screen. Afterwards the real login still
works and still names the same founder.

## Requirements

- **FR-101** `stack/auth.py` keeps only who the referee signs in as: `FOUNDER_NAME`,
  `FOUNDER_EMAIL`, `StubFounder`, `FOUNDER_ONE`/`FOUNDER_TWO` built from `stack/oidc.py`'s own
  list, and one browserless sign-in that walks start → authorize → callback.
- **FR-102** `harness/browser.py:Auth.sign_in(identity)` drives the real screen through the real
  callback; `set_up` and the password are deleted, not commented out.
- **FR-103** `evals/conftest.py` offers `founder_one`/`founder_two` with no I/O, and captures L1 —
  the login screen, before anyone has signed in — once per stack session.
- **FR-104** `stack/cloud.py` boots against `GET /v2/me` `401` and passes keel-cloud a founder base
  URL that is an origin.
- **FR-105** Every scenario's login step is one line and no scenario reaches a retired route.
- **FR-106** S-010 exists, is deterministic, is in `make eval`, and goes at **every** route §4.3
  lists.
- **FR-107** S-011 exists, is deterministic, is in `make eval`, and drives every case §10.7 names.
- **FR-108** `POLICY_VERSION` moves to **10**: `ORI-U1` stops exempting `setup`, a screen that
  cannot occur.
- **FR-109** `make unit` grows and the growth covers the sign-in's shape, the two scenarios'
  coverage, the founder base URL and the readiness gate.
- **FR-110** The scenario set becomes **eleven**, still with exactly one live scenario.

## Success Criteria

- **SC-101** `make unit` green, up from 537.
- **SC-102** `make eval-all` green across S-001, S-002, S-003, S-005–S-011 on one stack session.
- **SC-103** No product code is edited in any sibling; product faults, if any, are `runs/DRIFT.md`
  entries with a bundle.

## What this feature deliberately does not do

- **It does not give founder B a runtime.** This profile has one runtime home and two would collide
  on it. What S-010 proves instead is the thing that matters: A's runtime is not B's agent, and B's
  own creation is refused for want of **B's** agent — a refusal about B, never a 404 and never a
  silent success on A's runtime.
- **It does not add `KEEL_GOOGLE_ALLOWED_DOMAIN` to the stack.** §10.3 says the open posture is
  what the scenarios exercise, and the closed one is a keel-cloud unit test.
- **It does not touch S-004 beyond its login line**, and it does not run it: S-004 is live and
  costs real money.
