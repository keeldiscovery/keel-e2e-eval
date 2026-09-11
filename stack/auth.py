"""Who the referee signs in as, and the one browserless way to hold a founder session
(keel-cloud `canon/designs/google-sign-in-design.md` §10.4).

**What this module used to be, and why almost none of it is left.** Until keel-cloud spec 032 it
held `FOUNDER_PASSWORD`, an `ensure_founder_account` that called `POST /v2/setup` once, and a
`runs/.stack/founder.json` that had to be cleared at teardown so it never outlived the postgres
volume it described. Sign in with Google deletes the whole apparatus: `/v2/setup` and `/v2/login`
are gone from the wire, an account exists the moment somebody signs in, and the stub issuer is
stateless -- so there is nothing to provision, nothing to persist between runs, and nothing to
clear. `FOUNDER_NAME` and `FOUNDER_EMAIL` survive as **assertion constants** (they are in
greetings, participant pages and screenshots, and §10.2 keeps them deliberately), and what joins
them is `StubFounder` plus the two identities the stub is configured with.

**The identities live in `stack/oidc.py`, once.** `FOUNDER_ONE`/`FOUNDER_TWO` here are the same
two records under the names §10.4 gives them, so a scenario reads
`sign_in(page, ..., FOUNDER_TWO)` rather than reaching into the stub's own configuration. They are
not a second source of truth: `test_stub_oidc.py` asserts the two lists are the same objects.

**`login_and_keel_session` is the only browserless founder session in this harness, and it is not
a shortcut** (§10.8). It walks `GET /v2/auth/google/start` -> the stub's `/authorize` -> `GET
/v2/auth/google/callback`, in that order, on a real `requests.Session` whose cookie jar ends up
holding the session the real callback opened. The one thing it supplies that a browser would click
is *which identity*, and it supplies it the way §10.2 says: by adding `identity=<id>` to the
authorize URL keel-cloud itself redirected to. There is no function anywhere in this harness that
produces a founder session by any other means, and there must never be one.

**Why the identity cannot ride on the `/start` call.** §10.4 sketches
`start?return_to=/&login_hint=<sub>` and expects the hint to be carried through. It is not:
`GoogleStartController` reads exactly one query parameter (`return_to`) and `GoogleSignIn.start`
builds the authorize URL from the discovery document and its own configuration, so an extra
parameter on `/start` is dropped on the floor and the browserless caller lands on the picker's
HTML with nothing to click. Following the redirect by hand and appending `identity=` to *the URL
keel-cloud produced* is the same code path with the click supplied -- keel-cloud's own `state`,
`nonce`, `redirect_uri` and PKCE challenge are the ones that travel, untouched -- and it is what
this module does.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests

from stack import oidc
from stack.config import StackConfig
from stack.stub_oidc.server import Identity

#: Founder A's name and address, unchanged across the password's whole retirement (§10.2). Every
#: assertion that reads a greeting, a participant page or a project owner still reads these.
FOUNDER_NAME = "Eval Founder"
FOUNDER_EMAIL = "eval-founder@keel-e2e-eval.test"


@dataclass(frozen=True)
class StubFounder:
    """One founder the referee can sign in as (§10.4). `id` is the handle the stub's picker and
    its `?identity=` parameter answer to, `sub` is what keel-cloud keys the account on (§3.4),
    `name` is the picker button's label and the greeting's word, and `email` is what `/v2/me`
    carries back."""

    id: str
    sub: str
    email: str
    name: str

    @classmethod
    def of(cls, identity: Identity) -> "StubFounder":
        return cls(id=identity.id, sub=identity.sub, email=identity.email, name=identity.name)


#: The two founders, under §10.4's names. Built from `stack/oidc.py`'s own list so the stub and
#: the scenarios can never disagree about who exists.
FOUNDER_ONE = StubFounder.of(oidc.FOUNDER_A)
FOUNDER_TWO = StubFounder.of(oidc.FOUNDER_B)


@dataclass(frozen=True)
class KeelSession:
    """What `GET /v2/me` reports once the callback has opened a session -- `boundAgentSessionId`
    is null until a runtime connects through `keel connect`."""

    keel_session_id: str | None
    bound_agent_session_id: str | None
    agent_connected: bool
    name: str
    email: str
    picture: str | None


def cloud_base(config: StackConfig) -> str:
    """This profile's own Keel: `http://localhost:18080` on eval, `:18081` on playground, and
    whatever `KEEL_REMOTE_CLOUD_URL` names on remote (spec 017)."""
    return config.cloud_base_url


def sign_in_session(config: StackConfig, founder: StubFounder = FOUNDER_ONE, *,
                    return_to: str = "/") -> requests.Session:
    """A `requests.Session` carrying the founder session the **real callback** opened.

    Three hops, none of them skipped: `/v2/auth/google/start` (which writes the `login_attempt`
    row and the state on this caller's own servlet session -- the cookie jar is what makes that
    the same browser), the stub's `/authorize` with the click supplied, and
    `/v2/auth/google/callback`, which verifies the ID token and rotates the session id. What comes
    back is a cookie jar and nothing else; no token of any kind is ever in this process's hands.
    """
    base = cloud_base(config)
    session = requests.Session()
    started = session.get(f"{base}/v2/auth/google/start", params={"return_to": return_to},
                          allow_redirects=False, timeout=10)
    if started.status_code != 302:
        raise RuntimeError(
            f"GET /v2/auth/google/start answered {started.status_code}, not a 302 to the issuer "
            f"({started.text[:200]!r})")
    authorize_url = started.headers.get("Location", "")
    if not authorize_url.startswith(oidc.issuer_url(config)):
        # The one thing worth checking here: keel-cloud is pointed at *this profile's* stub. A
        # redirect to accounts.google.com means KEEL_OIDC_ISSUER never reached the JVM, and every
        # scenario downstream would fail for a reason nobody could read off its own screen.
        raise RuntimeError(
            f"keel-cloud redirected sign-in to {authorize_url[:120]!r}, not to this profile's "
            f"stub issuer at {oidc.issuer_url(config)} -- is KEEL_OIDC_ISSUER reaching the JVM?")
    joined = "&" if "?" in authorize_url else "?"
    # **The gate, on this hop and no other** (spec 017; e2e-matrix-design.md §4.2). On staging
    # Caddy stands basic auth in front of `/oidc/authorize` only, so the browserless sign-in
    # sends the same credential the browser context carries and sends it nowhere else: keel-cloud
    # answers `/start` and the callback with no credential at all, exactly as it does locally.
    # `config.gate_credential` is `None` on every local run, and `requests` with `auth=None` is
    # byte-for-byte the request this line made before this feature existed.
    landed = session.get(f"{authorize_url}{joined}identity={founder.id}", timeout=15,
                         auth=config.gate_credential)
    if landed.status_code >= 400:
        raise RuntimeError(
            f"the sign-in round trip ended {landed.status_code} at {landed.url} "
            f"({landed.text[:200]!r})")
    if "auth_error=" in landed.url:
        raise RuntimeError(f"keel-cloud refused the sign-in: {landed.url}")
    return session


def read_me(config: StackConfig, session: requests.Session) -> KeelSession:
    """`GET /v2/me` -- where `keelSessionId` lives now that `LoginResponse` is gone (§10.4)."""
    response = session.get(f"{cloud_base(config)}/v2/me", timeout=10)
    if response.status_code >= 400:
        raise RuntimeError(f"GET /v2/me answered {response.status_code}: {response.text[:200]}")
    body = response.json()
    return KeelSession(
        keel_session_id=body.get("keelSessionId"),
        bound_agent_session_id=(body.get("agent") or {}).get("agentSessionId"),
        agent_connected=bool((body.get("agent") or {}).get("connected")),
        name=body["name"], email=body["email"], picture=body.get("picture"),
    )


def login_and_keel_session(config: StackConfig, founder: StubFounder = FOUNDER_ONE,
                           ) -> tuple[requests.Session, KeelSession]:
    """Keeps its name and its job from the password era: a founder session on a plain
    `requests.Session`, for the wire-level assertions that want one without a browser. What
    changed is only how the session is opened, and where `keelSessionId` is read from."""
    session = sign_in_session(config, founder)
    return session, read_me(config, session)
