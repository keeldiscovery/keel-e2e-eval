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
from urllib.parse import parse_qs, unquote, urlencode, urlparse

from stack.stub_oidc.identity import Identity
from stack.stub_oidc.keys import KID, RsaKey, b64url, sign_jwt
from stack.stub_oidc.registry import Registry, RegistryError

_NOT_FOUND = ("not found -- this stub serves discovery, /jwks, /authorize, /token, "
              "/identities")

TOKEN_LIFETIME_S = 300
ACCESS_TOKEN = "stub-access-token"  # noqa: S105 - nobody reads it; keel-cloud discards it unread

#: `?stub_break=<what>` makes the next ID token wrong in exactly one declared way. It exists so
#: S-011 (§10.7, second half -- after keel-cloud 032) can prove *keel-cloud* refuses, rather than
#: proving the stub can lie. Every one of these is a refusal keel-cloud owns: G4 (`iss`, `aud`),
#: G5 (`exp`), G3 (`sig`), G1 (`nonce`), G7 (`email_verified`).
STUB_BREAKS = ("iss", "aud", "exp", "sig", "nonce", "email_verified")

#: The header Caddy sets from the basic-auth user it just checked (e2e-matrix-design.md §4.2).
#: The stub never sees a password: the gate is Caddy's, and this is the whole of what the stub
#: learns from it. It matters only when `--gated`; the local profiles never pass the flag and the
#: header is ignored if some curiosity sends one.
GATE_HEADER = "X-Keel-Gate-User"
FOUNDER_GATE_USER = "founder"
HARNESS_GATE_USER = "harness"
#: Who may write to the registry when gated. Two users, because Caddy's `basic_auth` block has
#: two lines in it.
REGISTRARS = (HARNESS_GATE_USER, FOUNDER_GATE_USER)


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
    same questions the wire asks.

    **`gated` and `registry` are the staging twin's two additions** (e2e-matrix-design.md §4.2,
    §4.3) and both are off by default, so an eval or playground stub is the stub it always was:
    no gate, an empty in-memory registry, and `identities` that are exactly the two built-in
    founders `stack/oidc.py` names.
    """

    def __init__(self, *, issuer: str, key: RsaKey, client_id: str, client_secret: str,
                 identities: Sequence[Identity], registry=None, gated: bool = False):
        self.issuer = issuer.rstrip("/")
        self.key = key
        self.client_id = client_id
        self.client_secret = client_secret
        #: The two founders in `stack/oidc.py`. They are the *end* of the picker's list, after
        #: every registered cell, and they are the identities the local profiles have.
        self.builtin_identities = list(identities)
        #: In memory unless `--registry <path>` named a file: the local profiles register
        #: nothing, so their picker is exactly the two built-in founders it always was.
        self.registry = registry if registry is not None else Registry()
        self.gated = gated
        self._codes: dict[str, _Code] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------------------ the list

    @property
    def identities(self) -> list[Identity]:
        """Registered cells **newest first**, then the built-in founders (§4.3). The order is
        the picker's order and `GET /identities`'s order, and it is the order the founder's
        morning depends on: yesterday's cells at the top."""
        return self.registry.identities() + list(self.builtin_identities)

    def may_sign_in_as(self, gate_user: str | None, identity: Identity) -> bool:
        """Invariant M6: **the harness cannot be the founder.** Ungated, everybody may be
        anybody -- that is the local profiles, where the only principal is whoever ran `make up`.
        Gated, `founder` may sign in as any identity and every other principal may sign in only
        as identities *it* registered, which is what makes a leaked harness password unable to
        reach the founder's own identity (§4.2) or another repository's cells."""
        if not self.gated:
            return True
        if not gate_user:
            return False
        if gate_user == FOUNDER_GATE_USER:
            return True
        entry = self.registry.find(identity.id)
        return entry is not None and entry.registered_by == gate_user

    def may_register(self, gate_user: str | None) -> bool:
        """Who may write to the registry when gated: the two users Caddy's basic auth knows
        (§4.2). Ungated, the registry is an in-memory list in a process on somebody's laptop and
        there is nobody else to refuse."""
        return True if not self.gated else gate_user in REGISTRARS

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


def picker_html(identities: Sequence[Identity], params: dict[str, str],
                authorize_url: str = "/authorize") -> str:
    """One minimal page: `<h1>Choose an account</h1>` and one `<button>` per identity, labelled
    with that identity's own name (§10.2) -- which is what Playwright clicks and what a person on
    the playground profile reads. No styling worth the name.

    **A registered identity's `label` follows its button** (e2e-matrix-design.md §4.3): it is how
    the founder's morning reads as the log they asked for -- the cell, the day, and the verdict
    the run patched in. The built-in identities carry no label, so this page is byte-for-byte the
    page it was on the local profiles. It is not a product screen and does not get product
    styling."""
    forms = []
    for identity in identities:
        hidden = "".join(
            f'<input type="hidden" name="{html.escape(k)}" value="{html.escape(v)}">'
            for k, v in {**params, "identity": identity.id}.items()
        )
        label = (f'<p class="label">{html.escape(identity.label)}</p>'
                 if identity.label else "")
        forms.append(
            f'<form method="get" action="{html.escape(authorize_url)}">{hidden}'
            f'<button type="submit">{html.escape(identity.name)}</button>'
            f'{label}'
            f'<p>{html.escape(identity.email)}</p></form>'
        )
    cancel = html.escape(authorize_url + "?" + urlencode({**params, "cancel": "1"}))
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
        elif parsed.path == "/identities":
            self._list_identities()
        else:
            self._text(404, _NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - http.server's own naming
        # **The body is read before anything is decided**, including a refusal. This is HTTP/1.1
        # with keep-alive: a request whose body is left in the socket makes the *next* request on
        # that connection start parsing at the leftover bytes, which reads as a garbled 400 from
        # a route nobody called. Every refusal below returns after this line.
        raw = self._read_body()
        parsed = urlparse(self.path)
        if parsed.path == "/identities":
            self._register_identity(raw)
            return
        if parsed.path != "/token":
            self._text(404, _NOT_FOUND)
            return
        form = {k: v[0] for k, v in parse_qs(raw.decode("utf-8", "replace"),
                                             keep_blank_values=True).items()}
        status, body = self.issuer.redeem(form, basic_auth=_basic_auth(self.headers.get(
            "Authorization")))
        self._json(status, body)

    def do_PATCH(self) -> None:  # noqa: N802 - http.server's own naming
        raw = self._read_body()
        parsed = urlparse(self.path)
        prefix = "/identities/"
        if not parsed.path.startswith(prefix) or len(parsed.path) <= len(prefix):
            self._text(404, _NOT_FOUND)
            return
        self._relabel_identity(unquote(parsed.path[len(prefix):]), raw)

    # -------------------------------------------------------------------------- the registry

    def _gate_user(self) -> str | None:
        """Whoever Caddy's basic auth just checked (§4.2), or `None` when the request carries no
        such header. The stub never sees a password."""
        return self.headers.get(GATE_HEADER) or None

    def _refuse_ungated(self) -> bool:
        """`--gated` and no `X-Keel-Gate-User`: 403, plain text, the same answer for every route
        the gate stands in front of. A stranger who finds the hostname gets this and nothing
        else (§9 S6)."""
        if self.issuer.gated and not self._gate_user():
            self._text(403, "this issuer is gated -- reach it through the gate")
            return True
        return False

    def _read_body(self) -> bytes:
        """Exactly `Content-Length` bytes, once per request, before any routing."""
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length > 0 else b""

    @staticmethod
    def _json_object(raw: bytes) -> dict | None:
        try:
            body = json.loads(raw.decode("utf-8")) if raw else None
        except (ValueError, UnicodeDecodeError):
            return None
        return body if isinstance(body, dict) else None

    def _list_identities(self) -> None:
        """`GET /identities` -- the list, newest first. What the picker renders and what the
        founder's own tooling can read."""
        if self._refuse_ungated():
            return
        if not self.issuer.may_register(self._gate_user()):
            self._text(403, f"{self._gate_user()!r} may not read the registry")
            return
        self._json(200, {
            "identities": [entry.to_json() for entry in self.issuer.registry.newest_first()],
            "builtin": [{"id": i.id, "sub": i.sub, "email": i.email, "name": i.name}
                        for i in self.issuer.builtin_identities],
        })

    def _register_identity(self, raw: bytes) -> None:
        """`POST /identities` -- one cell's founder, before it signs in (§4.3). 201, or 409 on a
        duplicate id: a cell that re-ran must say so in its own id rather than quietly taking
        over yesterday's founder and its project."""
        if self._refuse_ungated():
            return
        gate_user = self._gate_user()
        if not self.issuer.may_register(gate_user):
            self._text(403, f"{gate_user!r} may not register identities")
            return
        body = self._json_object(raw)
        if body is None:
            self._json(400, _error("invalid_request", "a JSON object body is required"))
            return
        try:
            entry = self.issuer.registry.register(
                id=str(body.get("id") or ""), name=str(body.get("name") or ""),
                email=str(body.get("email") or ""),
                label=(str(body["label"]) if body.get("label") else None),
                registered_by=gate_user or "",
                reserved_ids={i.id for i in self.issuer.builtin_identities},
            )
        except RegistryError as exc:
            self._json(exc.status, _error("invalid_request", exc.message))
            return
        self._json(201, entry.to_json())

    def _relabel_identity(self, identity_id: str, raw: bytes) -> None:
        """`PATCH /identities/<id>` -- the label and nothing else, which is how a cell writes its
        verdict back beside the founder it signed in as (§6.4)."""
        if self._refuse_ungated():
            return
        gate_user = self._gate_user()
        if not self.issuer.may_register(gate_user):
            self._text(403, f"{gate_user!r} may not label identities")
            return
        body = self._json_object(raw)
        if body is None or "label" not in body:
            self._json(400, _error("invalid_request", "a JSON object with a `label` is required"))
            return
        existing = self.issuer.registry.find(identity_id)
        if existing is None:
            self._json(404, _error("not_found", f"no such identity {identity_id!r}"))
            return
        if not self.issuer.may_sign_in_as(gate_user, existing.identity):
            # The same ownership rule the gate applies to signing in (M6): a principal that may
            # not *be* a cell's founder may not rewrite what that cell's verdict says either.
            self._text(403, f"{gate_user!r} did not register {identity_id!r}")
            return
        try:
            entry = self.issuer.registry.relabel(identity_id, str(body.get("label") or ""))
        except RegistryError as exc:
            self._json(exc.status, _error("not_found", exc.message))
            return
        self._json(200, entry.to_json())

    def _authorize(self, query: dict[str, str]) -> None:
        stub = self.issuer
        # The gate, before anything else is read (§4.2). Plain text, because the only reader of a
        # refusal here is a person who reached a URL they should not have.
        if self._refuse_ungated():
            return
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
            # The page posts back to the ISSUER's own advertised /authorize, never a root-relative
            # "/authorize": mounted under a path (staging serves the stub at
            # https://eval.keeldiscovery.com/oidc), a root-relative action lands on keel-web's
            # 404 -- the founder's first click on staging, 2026-09-11.
            self._html(200, picker_html(stub.identities,
                                        {k: query[k] for k in _CARRIED if query.get(k)},
                                        authorize_url=f"{stub.issuer}/authorize"))
            return
        identity = stub.identity_for(hint)
        if identity is None:
            self._text(404, f"no such identity {hint!r} -- "
                            f"configured: {[i.id for i in stub.identities]}")
            return
        if not stub.may_sign_in_as(self._gate_user(), identity):
            # M6, at the one place it is enforceable: the harness registered its own cells and
            # may be any of them, and may be nobody else -- the founder's own identity included.
            self._text(403, f"{self._gate_user()!r} may not sign in as {identity.id!r}")
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
                issuer: str | None = None, registry: Registry | None = None,
                gated: bool = False) -> ThreadingHTTPServer:
    """Binds and returns an un-started server. `port=0` picks a free one, and the issuer origin
    is then derived from what the OS gave us -- which is how the tests run without owning
    18090.

    `registry`/`gated` default to the local profiles' answers: an empty in-memory list and no
    gate (e2e-matrix-design.md §4.2)."""
    httpd = ThreadingHTTPServer((host, port), _Handler)
    httpd.daemon_threads = True
    origin = issuer or f"http://localhost:{httpd.server_address[1]}"
    stub = StubIssuer(issuer=origin, key=key, client_id=client_id,
                      client_secret=client_secret, identities=identities,
                      registry=registry, gated=gated)
    handler = type("_BoundHandler", (_Handler,), {"issuer": stub})
    httpd.RequestHandlerClass = handler
    httpd.stub = stub  # type: ignore[attr-defined]
    return httpd
