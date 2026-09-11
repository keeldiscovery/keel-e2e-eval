# Feature Specification: the gated registry stub

**Feature Branch**: `018-gated-registry-stub`

**Created**: 2026-09-10

**Status**: Implemented, stackless. `make unit`: **638** before, **712** after, green. No stack was
started and no model was called: every rule here is provable against a server on an ephemeral
socket, which is what `tests/test_stub_oidc_registry.py` does. The container image was **built and run** on this Mac
(`linux/arm64`: discovery 200, gated `/authorize` 403, `POST /identities` 201 with a derived
`sub`) and is **not pushed anywhere**; pushing it to ECR and putting Caddy in front of it is step 2
of the design's implementation order (§13) and belongs to keel-cloud's spec `036-staging-twin`.

**Input**: keel-cloud `canon/designs/e2e-matrix-design.md` §4 (the whole of it), §3 (the twin and
the one service it adds), §9 (security), §11 (what changes by repository), §12 (invariants M4, M5,
M6), and google-sign-in-design.md §10.1–§10.3 (the stub's existing contract, which this must not
break).

The siblings, read at these commits:

| Sibling | Commit | What this feature depends on |
|---|---|---|
| keel-cloud | `canon/designs/e2e-matrix-design.md` as written 2026-09-10 | §4.2's Caddy block and the `X-Keel-Gate-User` header it forwards; §4.3's three routes; §4.4's founder identity; §8's monthly reset. |
| keel-cloud | `canon/designs/google-sign-in-design.md` §10 | The stub's existing contract -- four routes, one key, the picker, `?login_hint=`, `stub_break` -- none of which may move. |

## What changes, stated first

**The stub issuer becomes two things at once, and the second must not disturb the first.**

Today `stack/stub_oidc/` is a standard-library OIDC issuer with two identities in a list, started
by `make up` on 18090, reachable only because `KEEL_OIDC_ISSUER` names it. On the staging twin the
*same package* is a container behind Caddy, serving eighteen cells a week, each of which registers
its own founder, signs in as it, and patches its verdict into the label the founder reads the next
morning.

So this spec adds three things and moves none:

- **A gate.** `--gated` makes `/authorize` and the registry routes refuse a request with no
  `X-Keel-Gate-User` header — the header Caddy sets from the basic auth it just checked. The stub
  never sees a password; all it learns is a user name, and it uses it for exactly one thing:
  `founder` may sign in as any identity, and every other principal may sign in only as identities
  it registered (invariant **M6** — *the harness cannot be the founder*).
- **A registry.** `--registry <path>` names a JSON file; without it the registry is an in-memory
  list, which is what the eval and playground profiles want. `POST /identities`,
  `PATCH /identities/<id>` and `GET /identities` write and read it, the picker renders it newest
  first with each registered identity's label under its button, and `?identity=`/`?login_hint=`
  find registered identities exactly as they find built-in ones.
- **A container image.** `stack/containers/oidc/Dockerfile` and `make oidc-image TAG=<tag>`, so the
  bytes that answer on staging are the bytes the local suite refereed.

**Ungated is unchanged, and that is the requirement the rest hang off.** No flag, no header, no
registry file: two built-in identities, the same picker HTML, the same 302s, the same ID tokens.
`tests/test_stub_oidc.py` — spec 015's own file — is **not edited by this feature**, and its 54
tests passing is the proof.

**One structural move, and why.** `Identity`, `CLIENT_ID`, `CLIENT_SECRET` and the two built-in
founders moved from `stack/oidc.py` into `stack/stub_oidc/identity.py`, and `stack/oidc.py`
re-exports the same objects under the same names. The reason is the image: `stack/oidc.py` imports
`requests`, `stack.config` and `stack.processes`, none of which a stub issuer needs, and a
container that carried them would carry a `stack.config` whose `REPO_ROOT` points at a checkout
that is not there. After the move `stack/stub_oidc/` imports nothing outside itself and the image
is `python:3.12-slim` + `openssl` + two `COPY`s, with **no `pip install` at all**.

## User scenarios

### The founder's morning (design §7), which is what the registry is for

1. The founder opens `https://eval.keeldiscovery.com`, clicks *Sign in with Google* — it is the
   stub behind it — and the browser asks for the gate. They answer `founder` and their own
   password, once per browser session.
2. The picker lists every cell **newest first**, each button the cell's short name and the line
   under it the cell's label — the day, the cell, and the verdict the run patched in. The two
   built-in founders are last.
3. They click yesterday's Windows / Copilot / 3.9 and they are that founder: the project the
   scenario built, owner-scoped, through the same screens everyone else gets.

### A cell (design §5.3 step 4 and §6.4), which is what the gate is for

1. The cell `POST /oidc/identities` with `{id, name, email, label}` and the `harness` gate
   credential. 201, and the `sub` comes back derived (`cell-<id>`) — never one it chose.
2. It signs in as that identity through the picker, with the same credential on the browser
   context.
3. It runs the journey, and `PATCH /oidc/identities/<id>` writes the verdict into the label.
4. It cannot sign in as `founder-a`, as the founder's own identity, or as another cell's: 403,
   plain text.

## Requirements

- **FR-001** `--gated` refuses `/authorize` with **403 and a plain-text body** when the request
  carries no `X-Keel-Gate-User` header. Not a redirect to the client, not HTML, not a hint about
  who may pass.
- **FR-002** Gated, `founder` may sign in as any identity; any other gate user may sign in only as
  identities registered **by that user** (M6). A refusal is 403 plain text.
- **FR-003** Ungated behaviour is byte-for-byte what it was: no header is read, the two built-in
  identities sign in, and the picker's HTML is unchanged (no label element is emitted for an
  identity that has none).
- **FR-004** `--registry <path>` keeps the identity list in that JSON file; the default is an
  in-memory list, so the local profiles pass nothing and need nothing.
- **FR-005** `POST /identities` takes `{id, name, email, label}` and answers **201** with the
  stored record. `sub` is derived as `cell-<id>` and **never taken from the request**;
  `email_verified` is always true in the token; `hd` is never set.
- **FR-006** `POST /identities` answers **409** on a duplicate id, including an id that belongs to
  a built-in identity, and **400** on a malformed id, a missing name or email, or a body that is
  not a JSON object.
- **FR-007** `PATCH /identities/<id>` changes **the label and nothing else** — a request that also
  carries a name, an email or a `sub` changes none of them — and answers 404 for an unknown id,
  400 with no `label`.
- **FR-008** `GET /identities` answers the registrations **newest first**, and names the built-in
  identities separately (they are not registrations and nothing may patch them).
- **FR-009** When gated, the registry routes are writable by `harness` and `founder` only; any
  other gate user is 403. A principal may relabel only what it may sign in as (FR-002).
- **FR-010** The picker lists registered identities **newest first, then the built-in ones**, with
  each registered identity's **label immediately after its button**, HTML-escaped like every other
  word on that page.
- **FR-011** `?identity=<id>` and `?login_hint=<sub>` resolve registered identities exactly as they
  resolve built-in ones.
- **FR-012** Every write to the registry file is **atomic**: a temp file in the same directory and
  `os.replace`. A reader on `/authorize` never sees a partial document, and nothing is left beside
  the file.
- **FR-013** A registry file that is missing or corrupt reads as **empty**, not as a dead issuer:
  the built-in identities still sign in.
- **FR-014** `stack/containers/oidc/Dockerfile` builds the stub package on `python:3.12-slim` with
  `openssl` and no Python dependency, entrypoint `python -m stack.stub_oidc`, and
  `make oidc-image TAG=<tag>` builds it for `linux/arm64` through buildx.
- **FR-015** Nothing in `stack/oidc.py` passes `--gated` or `--registry`: a local `make up` can
  never gate itself, and a test asserts the absence.

## What is deliberately not built

- **No password in the stub.** The gate is Caddy's. The stub learns a user name from a header and
  nothing else, and it must never grow a credential of its own (google-sign-in-design §10.8).
- **No authorization of the *picker's list*.** The picker lists every identity to any principal
  that got through the gate, exactly as §4.3 says; what is authorized is the **choice**, at the
  one place a wrong choice would matter. A harness that browsed the list learns two founders'
  names it already knows from the source.
- **No delete route.** Cells never delete (M7); the monthly reset is `rm` of a directory (§8).
- **No pagination, no query language, no index.** Eighteen rows a week and a monthly reset.
- **No Caddyfile, no compose overlay, no deploy.** Those are keel-cloud's spec `036-staging-twin`.
- **No ECR push from here.** `make oidc-image PUSH=1` exists and names no registry of its own; the
  workflow that pushes is spec `020-matrix-workflow`.
