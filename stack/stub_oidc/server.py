"""The stub OIDC issuer itself: four routes, one key, no database (keel-cloud
`canon/designs/google-sign-in-design.md` §10.1).

What it is for: keel-cloud's login is *one* code path, and the only thing that differs between
production and this harness is which URL `KEEL_OIDC_ISSUER` names (§3.6, §10.8). So this serves a
real discovery document, a real JWKS, a real Authorization Code + PKCE `/authorize`, and a real
`/token` that signs a real RS256 ID token -- and refuses a bad verifier, a reused code, a
mismatched `redirect_uri` and an unknown client, because a stub that accepts anything proves
nothing about the client's half.

What it must never become (§10.8): a password, a bypass header, a seeded cookie, a second trusted
key, or a way into keel-cloud that is not `/authorize` -> the callback. It holds its codes in a
dict that dies with the process, and it is reachable only because a configuration variable names
it. If it ever grows a database, a session or a second client, something that belongs in
keel-cloud has drifted into the harness.
"""

from __future__ import annotations

import base64
import hashlib
import html
import json
import secrets
import sys
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Sequence
from urllib.parse import parse_qs, urlencode, urlparse

from stack.stub_oidc.keys import KID, RsaKey, b64url, sign_jwt

TOKEN_LIFETIME_S = 300
ACCESS_TOKEN = "stub-access-token"  # noqa: S105 - nobody reads it; keel-cloud discards it unread

#: `?stub_break=<what>` makes the next ID token wrong in exactly one declared way. It exists so
#: S-011 (§10.7, second half -- after keel-cloud 032) can prove *keel-cloud* refuses, rather than
#: proving the stub can lie. Every one of these is a refusal keel-cloud owns: G4 (`iss`, `aud`),
#: G5 (`exp`), G3 (`sig`), G1 (`nonce`), G7 (`email_verified`).
STUB_BREAKS = ("iss", "aud", "exp", "sig", "nonce", "email_verified")


@dataclass(frozen=True)
class Identity:
    """One person the stub will sign in as. `id` is the harness's handle for it (`?identity=`),
    `sub` is what keel-cloud keys the account on (§3.4), and `name` is what the picker's button
    is labelled with -- which is how a browser scenario chooses (§10.2)."""

    id: str
    sub: str
    email: str
    name: str
    picture: str | None = None
    hd: str | None = None

    def matches(self, hint: str) -> bool:
        return hint in (self.id, self.sub, self.email)


@dataclass(frozen=True)
class _Code:
    client_id: str
    redirect_uri: str
    nonce: str
    code_challenge: str
    identity: Identity
    stub_break: str | None
    issued_at: float


class StubIssuer:
    """The state and the answers, with no HTTP in it -- so `tests/test_stub_oidc.py` can ask the
    same questions the wire asks."""

    def __init__(self, *, issuer: str, key: RsaKey, client_id: str, client_secret: str,
                 identities: Sequence[Identity]):
        self.issuer = issuer.rstrip("/")
        self.key = key
        self.client_id = client_id
        self.client_secret = client_secret
        self.identities = list(identities)
        self._codes: dict[str, _Code] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------------------ documents

    def discovery(self) -> dict:
        return {
            "issuer": self.issuer,
            "authorization_endpoint": f"{self.issuer}/authorize",
            "token_endpoint": f"{self.issuer}/token",
            "jwks_uri": f"{self.issuer}/jwks",
            "response_types_supported": ["code"],
            "subject_types_supported": ["public"],
            "grant_types_supported": ["authorization_code"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "code_challenge_methods_supported": ["S256"],
            "scopes_supported": ["openid", "email", "profile"],
            "claims_supported": [
                "iss", "aud", "azp", "sub", "email", "email_verified", "name", "given_name",
                "family_name", "picture", "nonce", "iat", "exp", "hd",
            ],
            "token_endpoint_auth_methods_supported": [
                "client_secret_post", "client_secret_basic",
            ],
        }

    def jwks(self) -> dict:
        return {"keys": [self.key.public_jwk()]}

    def identity_for(self, hint: str) -> Identity | None:
        for identity in self.identities:
            if identity.matches(hint):
                return identity
        return None

    # ------------------------------------------------------------------------------ the flow

    def mint_code(self, *, client_id: str, redirect_uri: str, nonce: str, code_challenge: str,
                  identity: Identity, stub_break: str | None = None) -> str:
        code = secrets.token_urlsafe(32)
        with self._lock:
            self._codes[code] = _Code(
                client_id=client_id, redirect_uri=redirect_uri, nonce=nonce,
                code_challenge=code_challenge, identity=identity, stub_break=stub_break,
                issued_at=time.time(),
            )
        return code

    def _burn(self, code: str) -> _Code | None:
        """Any redemption attempt consumes the code, successful or not (RFC 6749 §4.1.2). A
        second `/token` with the same code is `invalid_grant` whatever else was wrong with the
        first -- which is the property keel-cloud's own replay refusal (G2) sits behind."""
        with self._lock:
            return self._codes.pop(code, None)

    def redeem(self, form: dict[str, str], *, basic_auth: tuple[str, str] | None = None
               ) -> tuple[int, dict]:
        """The whole of `/token`, as (status, body). Every refusal is an OAuth error object."""
        if form.get("grant_type") != "authorization_code":
            return 400, _error("unsupported_grant_type",
                               "this stub issues authorization codes and nothing else")

        client_id = form.get("client_id") or (basic_auth[0] if basic_auth else None)
        client_secret = form.get("client_secret") or (basic_auth[1] if basic_auth else None)
        if client_id != self.client_id or client_secret != self.client_secret:
            return 401, _error("invalid_client", "unknown client id or secret")

        code = form.get("code", "")
        record = self._burn(code)
        if record is None:
            return 400, _error("invalid_grant", "no such authorization code, or it was used")
        if record.client_id != client_id:
            return 400, _error("invalid_grant", "that code was issued to a different client")
        if form.get("redirect_uri") != record.redirect_uri:
            return 400, _error("invalid_grant",
                               "redirect_uri does not match the one given to /authorize")

        verifier = form.get("code_verifier", "")
        if not verifier or pkce_challenge(verifier) != record.code_challenge:
            return 400, _error("invalid_grant", "PKCE code_verifier does not match code_challenge")

        return 200, {
            "token_type": "Bearer",
            "expires_in": TOKEN_LIFETIME_S,
            "access_token": ACCESS_TOKEN,
            "scope": "openid email profile",
            "id_token": self.id_token(record.identity, nonce=record.nonce,
                                      stub_break=record.stub_break),
        }

    def id_token(self, identity: Identity, *, nonce: str, stub_break: str | None = None) -> str:
        """Exactly what §3.3 checks, and nothing else. `stub_break` bends one claim (or the
        signature) so the *client's* refusal can be measured."""
        now = int(time.time())
        given, _, family = identity.name.partition(" ")
        claims = {
            "iss": self.issuer,
            "aud": self.client_id,
            "azp": self.client_id,
            "sub": identity.sub,
            "email": identity.email,
            "email_verified": True,
            "name": identity.name,
            "given_name": given,
            "nonce": nonce,
            "iat": now,
            "exp": now + TOKEN_LIFETIME_S,
        }
        if family:
            claims["family_name"] = family
        if identity.picture:
            claims["picture"] = identity.picture
        if identity.hd:
            claims["hd"] = identity.hd

        if stub_break == "iss":
            claims["iss"] = "https://accounts.google.com"
        elif stub_break == "aud":
            claims["aud"] = claims["azp"] = "some-other-client"
        elif stub_break == "exp":
            claims["iat"] = now - 2 * TOKEN_LIFETIME_S
            claims["exp"] = now - TOKEN_LIFETIME_S
        elif stub_break == "nonce":
            claims["nonce"] = secrets.token_urlsafe(16)
        elif stub_break == "email_verified":
            claims["email_verified"] = False

        token = sign_jwt(self.key, claims, kid=KID)
        if stub_break == "sig":
            head, _, signature = token.rpartition(".")
            token = f"{head}.{_flip_first_char(signature)}"
        return token


def pkce_challenge(verifier: str) -> str:
    """S256, RFC 7636 §4.2."""
    return b64url(hashlib.sha256(verifier.encode("ascii")).digest())


def _flip_first_char(text: str) -> str:
    return ("B" if text[0] == "A" else "A") + text[1:]


def _error(code: str, description: str) -> dict:
    return {"error": code, "error_description": description}


# --------------------------------------------------------------------------------- the picker

_PICKER_CSS = (
    "body{font:16px/1.5 system-ui,sans-serif;margin:3rem auto;max-width:32rem}"
    "button{display:block;width:100%;font:inherit;padding:.75rem;margin:.5rem 0;cursor:pointer}"
    "p{color:#555}"
)


def picker_html(identities: Sequence[Identity], params: dict[str, str]) -> str:
    """One minimal page: `<h1>Choose an account</h1>` and one `<button>` per identity, labelled
    with that identity's own name (§10.2) -- which is what Playwright clicks and what a person on
    the playground profile reads. No styling worth the name."""
    forms = []
    for identity in identities:
        hidden = "".join(
            f'<input type="hidden" name="{html.escape(k)}" value="{html.escape(v)}">'
            for k, v in {**params, "identity": identity.id}.items()
        )
        forms.append(
            f'<form method="get" action="/authorize">{hidden}'
            f'<button type="submit">{html.escape(identity.name)}</button>'
            f'<p>{html.escape(identity.email)}</p></form>'
        )
    cancel = html.escape("/authorize?" + urlencode({**params, "cancel": "1"}))
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>Choose an account</title>"
        f"<style>{_PICKER_CSS}</style></head><body>"
        "<h1>Choose an account</h1>"
        "<p>This is keel-e2e-eval's stub issuer. It is not Google, it has no password, "
        "and it exists only because KEEL_OIDC_ISSUER names it.</p>"
        + "".join(forms)
        + f'<p><a href="{cancel}">Cancel</a></p>'
        "</body></html>"
    )


# ------------------------------------------------------------------------------------ the HTTP

_CARRIED = ("client_id", "redirect_uri", "response_type", "scope", "state", "nonce",
            "code_challenge", "code_challenge_method", "stub_break")


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "keel-stub-oidc/1.0"
    issuer: StubIssuer  # set on the subclass by `make_server`

    # ----------------------------------------------------------------------------- plumbing

    def log_message(self, fmt: str, *args) -> None:  # pragma: no cover - stderr shape only
        # Query strings are never logged: they carry `state`, `nonce` and the code (§11's
        # never-logged list). Method, path and status are the whole of it.
        print(f"[stub-oidc] {self.log_date_time_string()} {fmt % args}", file=sys.stderr,
              flush=True)

    def log_request(self, code="-", size="-") -> None:  # pragma: no cover - stderr shape only
        path = urlparse(self.path).path
        self.log_message("%s %s -> %s", self.command, path, code)

    def _respond(self, status: int, body: bytes, content_type: str,
                 extra: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        self._respond(status, json.dumps(payload, indent=2).encode(), "application/json")

    def _html(self, status: int, markup: str) -> None:
        self._respond(status, markup.encode(), "text/html; charset=utf-8")

    def _text(self, status: int, message: str) -> None:
        self._respond(status, message.encode(), "text/plain; charset=utf-8")

    def _redirect(self, location: str) -> None:
        self._respond(302, b"", "text/plain; charset=utf-8", {"Location": location})

    # ------------------------------------------------------------------------------- routes

    def do_GET(self) -> None:  # noqa: N802 - http.server's own naming
        parsed = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(parsed.query, keep_blank_values=True).items()}
        if parsed.path == "/.well-known/openid-configuration":
            self._json(200, self.issuer.discovery())
        elif parsed.path in ("/jwks", "/jwks.json"):
            # `/jwks` is what the discovery document names and what keel-cloud will fetch;
            # `/jwks.json` is an alias so a curl by hand finds it under either spelling.
            self._json(200, self.issuer.jwks())
        elif parsed.path == "/authorize":
            self._authorize(query)
        else:
            self._text(404, "not found -- this stub serves discovery, /jwks, /authorize, /token")

    def do_POST(self) -> None:  # noqa: N802 - http.server's own naming
        parsed = urlparse(self.path)
        if parsed.path != "/token":
            self._text(404, "not found -- this stub serves discovery, /jwks, /authorize, /token")
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        form = {k: v[0] for k, v in parse_qs(raw, keep_blank_values=True).items()}
        status, body = self.issuer.redeem(form, basic_auth=_basic_auth(self.headers.get(
            "Authorization")))
        self._json(status, body)

    def _authorize(self, query: dict[str, str]) -> None:
        stub = self.issuer
        client_id = query.get("client_id")
        redirect_uri = query.get("redirect_uri", "")
        # An unknown client or an unusable redirect_uri can never be answered *at* the client:
        # doing so is how open redirectors are built. Both refuse here, in the browser.
        if client_id != stub.client_id:
            self._text(400, f"unknown client_id {client_id!r}")
            return
        parsed_redirect = urlparse(redirect_uri)
        if parsed_redirect.scheme not in ("http", "https") or not parsed_redirect.netloc:
            self._text(400, "redirect_uri must be an absolute http(s) URL")
            return

        state = query.get("state", "")
        nonce = query.get("nonce", "")
        if not state or not nonce:
            # Both are required of any client this stub is here to referee: `state` is G1's CSRF
            # binding and `nonce` is what binds the ID token to this login. A client that omits
            # either has a defect, and it should read as one.
            self._text(400, "state and nonce are both required")
            return

        if query.get("cancel"):
            self._redirect(_with_query(redirect_uri, {"error": "access_denied", "state": state}))
            return
        if query.get("response_type") != "code":
            self._redirect(_with_query(redirect_uri, {
                "error": "unsupported_response_type", "state": state}))
            return
        if "openid" not in query.get("scope", "").split():
            self._redirect(_with_query(redirect_uri, {"error": "invalid_scope", "state": state}))
            return
        challenge = query.get("code_challenge", "")
        if not challenge or query.get("code_challenge_method") != "S256":
            self._redirect(_with_query(redirect_uri, {
                "error": "invalid_request", "state": state}))
            return

        stub_break = query.get("stub_break") or None
        if stub_break is not None and stub_break not in STUB_BREAKS:
            self._text(400, f"unknown stub_break {stub_break!r} -- one of {STUB_BREAKS}")
            return

        # `?identity=<id>` (the harness's own handle) and `?login_hint=<sub>` (the parameter a
        # real client would send) both skip the page. Neither is a bypass: the code path is the
        # same one the click takes, with the click supplied (§10.2).
        hint = query.get("identity") or query.get("login_hint")
        if not hint:
            self._html(200, picker_html(stub.identities,
                                        {k: query[k] for k in _CARRIED if query.get(k)}))
            return
        identity = stub.identity_for(hint)
        if identity is None:
            self._text(404, f"no such identity {hint!r} -- "
                            f"configured: {[i.id for i in stub.identities]}")
            return

        code = stub.mint_code(client_id=client_id, redirect_uri=redirect_uri, nonce=nonce,
                              code_challenge=challenge, identity=identity, stub_break=stub_break)
        self._redirect(_with_query(redirect_uri, {"code": code, "state": state}))


def _with_query(url: str, extra: dict[str, str]) -> str:
    parsed = urlparse(url)
    merged = {k: v[0] for k, v in parse_qs(parsed.query, keep_blank_values=True).items()}
    merged.update(extra)
    return parsed._replace(query=urlencode(merged)).geturl()


def _basic_auth(header: str | None) -> tuple[str, str] | None:
    if not header or not header.lower().startswith("basic "):
        return None
    try:
        decoded = base64.b64decode(header.split(" ", 1)[1]).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None
    client_id, sep, client_secret = decoded.partition(":")
    return (client_id, client_secret) if sep else None


def make_server(*, port: int, key: RsaKey, client_id: str, client_secret: str,
                identities: Sequence[Identity], host: str = "127.0.0.1",
                issuer: str | None = None) -> ThreadingHTTPServer:
    """Binds and returns an un-started server. `port=0` picks a free one, and the issuer origin
    is then derived from what the OS gave us -- which is how the tests run without owning
    18090."""
    httpd = ThreadingHTTPServer((host, port), _Handler)
    httpd.daemon_threads = True
    origin = issuer or f"http://localhost:{httpd.server_address[1]}"
    stub = StubIssuer(issuer=origin, key=key, client_id=client_id,
                      client_secret=client_secret, identities=identities)
    handler = type("_BoundHandler", (_Handler,), {"issuer": stub})
    httpd.RequestHandlerClass = handler
    httpd.stub = stub  # type: ignore[attr-defined]
    return httpd
