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
from urllib.parse import parse_qs, urlsplit

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


# ------------------------------------------------------------------- spec 092: strangers on a group link

#: Where every stranger's address lives (spec 092 FR-2: the journey never prints a real person's email). `.test` is
#: reserved (RFC 2606): nothing at this domain can ever reach anybody.
STRANGER_EMAIL_DOMAIN = "strangers.keel-e2e-eval.test"

#: keel-cloud 162's own cookie on the participant callback's path: the arrival's token, so the same browser signing in
#: again on the same group link comes back to the same arrival (`keel_arrival_<groupId hex>`).
ARRIVAL_COOKIE_PREFIX = "keel_arrival_"


@dataclass(frozen=True)
class StubStranger:
    """Spec 092 FR-1: one stranger the stub issuer signs in on a group link's arrival card -- registered on the stub
    (`POST /identities`, ungated on the local profiles) for this run alone. `id` is the picker's and `?identity=`'s
    handle; `sub` is derived by the stub from it (`cell-<id>`, never supplied: keel-cloud 162 finds an arrival by its
    group and this `sub`); `email` sits under `STRANGER_EMAIL_DOMAIN`; `name` is what the ID token's `name` carries and
    `given_name` (the stub's `given_name` claim: the name's first word) is what the interview serves as `personName`."""

    id: str
    sub: str
    email: str
    name: str

    @property
    def given_name(self) -> str:
        return self.name.partition(" ")[0]


def stranger_email(stranger_id: str) -> str:
    return f"{stranger_id}@{STRANGER_EMAIL_DOMAIN}"


def register_stranger(config: StackConfig, stranger_id: str, name: str, *,
                      label: str | None = None) -> StubStranger:
    """`POST {issuer}/identities` -- one stranger, before they open the link (the stub's registry, e2e-matrix-design.md
    §4.3, in memory on the local profiles). 201 or a RuntimeError naming the stub's answer (409: the id is taken)."""
    body = {"id": stranger_id, "name": name, "email": stranger_email(stranger_id)}
    if label:
        body["label"] = label
    response = requests.post(f"{oidc.issuer_url(config)}/identities", json=body, timeout=10,
                             auth=config.gate_credential)
    if response.status_code != 201:
        raise RuntimeError(f"the stub issuer refused to register {stranger_id!r}: {response.status_code} "
                           f"{response.text[:200]!r}")
    made = response.json()
    return StubStranger(id=made["id"], sub=made["sub"], email=made["email"], name=made["name"])


def token_of(url: str) -> str:
    """The token a participant link carries: the last segment of `/i/{token}`, without its query."""
    path = urlsplit(url).path if "://" in url else url.split("?", 1)[0]
    return path.rstrip("/").rsplit("/", 1)[-1]


@dataclass(frozen=True)
class ArrivalSignIn:
    """What one wire sign-in on a group link came to (spec 092 FR-1). `refused` is the start's status when keel-cloud
    would not send the person to the issuer (410: the link is closed, full, or the founder's balance is under one
    interview; 404: not a group's token); else `landed` is where the callback sent them -- their own `/i/{token}`
    (`token`), or the group's page with `auth_error`. `cookie` names the `keel_arrival_` cookie the session holds
    afterwards; `hops` is every hop's status and URL, in order."""

    group_token: str
    refused: int | None = None
    landed: str | None = None
    token: str | None = None
    auth_error: str | None = None
    cookie: str | None = None
    hops: tuple = ()


def arrival_cookie(session: requests.Session) -> str | None:
    names = sorted(c.name for c in session.cookies if c.name.startswith(ARRIVAL_COOKIE_PREFIX))
    return names[0] if names else None


def sign_in_arrival(config: StackConfig, group_url: str, stranger: StubStranger, *,
                    session: requests.Session | None = None) -> tuple[requests.Session, ArrivalSignIn]:
    """**A stranger signs in on a group link, on the wire** (spec 092 FR-1; keel-cloud 162 FR-3) -- `sign_in_session`'s
    three hops, on the participant's routes: `GET /v2/i/{groupToken}/auth/google/start` (keel-cloud writes the login
    attempt keyed to the group and sends the issuer the participant callback, no `hd`), the stub's `/authorize` with
    the click supplied (`identity=<id>` appended to the URL keel-cloud produced, so its `state`, `nonce`,
    `redirect_uri` and PKCE challenge are the ones that travel), and `GET /v2/i/auth/google/callback`, which verifies
    the ID token, finds or creates the arrival by (group, `sub`) and 302s to the arrival's own `/i/{token}` with the
    `keel_arrival_<group>` cookie. Every redirect is followed by hand, so the 302 that lands the person is read as
    keel-cloud sent it and never fetched from keel-web. Pass the same `session` again to sign in a second time from
    the same "browser" (the cookie rides it); a fresh session is another browser."""
    session = session or requests.Session()
    group_token = token_of(group_url)
    hops: list[tuple[int, str]] = []
    start_url = f"{cloud_base(config)}/v2/i/{group_token}/auth/google/start"
    started = session.get(start_url, allow_redirects=False, timeout=10)
    hops.append((started.status_code, start_url))
    if started.status_code != 302:
        return session, ArrivalSignIn(group_token=group_token, refused=started.status_code, hops=tuple(hops))
    authorize_url = started.headers.get("Location", "")
    if not authorize_url.startswith(oidc.issuer_url(config)):
        raise RuntimeError(
            f"keel-cloud sent the group link's sign-in to {authorize_url[:120]!r}, not to this profile's stub issuer "
            f"at {oidc.issuer_url(config)} -- is KEEL_OIDC_ISSUER reaching the JVM?")
    joined = "&" if "?" in authorize_url else "?"
    picked_url = f"{authorize_url}{joined}identity={stranger.id}"
    picked = session.get(picked_url, allow_redirects=False, timeout=15, auth=config.gate_credential)
    hops.append((picked.status_code, authorize_url))
    if picked.status_code != 302:
        raise RuntimeError(f"the stub issuer answered {picked.status_code} for {stranger.id!r}: "
                           f"{picked.text[:200]!r}")
    callback_url = picked.headers.get("Location", "")
    called = session.get(callback_url, allow_redirects=False, timeout=15)
    hops.append((called.status_code, callback_url.split("?", 1)[0]))
    if called.status_code != 302:
        raise RuntimeError(f"the participant callback answered {called.status_code}, not a 302: "
                           f"{called.text[:200]!r}")
    landed = called.headers.get("Location", "")
    query = parse_qs(urlsplit(landed).query)
    auth_error = (query.get("auth_error") or [None])[0]
    return session, ArrivalSignIn(group_token=group_token, landed=landed,
                                  token=None if auth_error else token_of(landed), auth_error=auth_error,
                                  cookie=arrival_cookie(session), hops=tuple(hops))
