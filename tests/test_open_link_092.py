"""Spec 092 -- one open link for a group: the harness's side (keel-cloud 162, contract 48; keel-web 136).

FR-1 strangers on the stub issuer: registered (`POST /identities`), signed in on the wire (`stack.auth.sign_in_arrival`)
against the real stub on a real socket and a stand-in keel-cloud that answers 162's two participant routes the way
162's tasks.md says they answer, and in the browser (`harness.browser.Arrival`, read for its shape). Stackless.
"""

from __future__ import annotations

import base64
import dataclasses
import hashlib
import inspect
import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
import requests

from harness import browser as browser_mod
from stack import auth, oidc
from stack.config import load_config
from stack.stub_oidc import keys as keymod
from stack.stub_oidc.server import make_server, pkce_challenge

CLIENT_ID = "test-client"
CLIENT_SECRET = "test-client-secret"  # noqa: S105 - a stub's own fixture, never a real secret
GROUP = "gRoUpToKeN"
CLOSED = "cLoSeDgRoUp"
GROUP_ID = "0f1e2d3c"


# ------------------------------------------------------------------------------------- the two servers

@pytest.fixture(scope="module")
def issuer(tmp_path_factory):
    key = keymod.load_or_generate(tmp_path_factory.mktemp("oidc") / "key.pem")
    httpd = make_server(port=0, key=key, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, identities=[])
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd.stub.issuer
    httpd.shutdown()
    httpd.server_close()


class _Cloud:
    """keel-cloud 162's participant sign-in, as its tasks.md describes it, and nothing else: `start` on a group's token
    writes the attempt (state `<groupToken>.<random>`, PKCE, nonce, the participant redirect URI, no `hd`) and 302s to
    the issuer; 410 on a closed group, 404 on anything else; the callback redeems the code at the participant URI,
    finds the arrival by (group, `sub`), keeps its token when the browser's `keel_arrival_<group>` cookie names it
    (else a new token to the same arrival) and 302s to `{participant base}/{token}` with the cookie."""

    def __init__(self, issuer: str):
        self.issuer = issuer
        self.attempts: dict[str, dict] = {}
        self.arrivals: dict[str, dict] = {}       # sub -> {"tokens": [...], "claims": {...}}
        self.authorize_queries: list[dict] = []
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.base = f"http://localhost:{self.httpd.server_address[1]}"
        self.callback = f"{self.base}/v2/i/auth/google/callback"
        self.web = "http://localhost:59999/i"

    def _handler(self):
        cloud = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args) -> None:  # noqa: D401 - quiet
                pass

            def _send(self, status: int, headers: dict | None = None) -> None:
                self.send_response(status)
                for k, v in (headers or {}).items():
                    self.send_header(k, v)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self) -> None:  # noqa: N802
                parts = urlsplit(self.path)
                if parts.path == "/v2/i/auth/google/callback":
                    return cloud.complete(self, parse_qs(parts.query))
                segments = parts.path.strip("/").split("/")
                if len(segments) == 6 and segments[:2] == ["v2", "i"] and segments[3:] == ["auth", "google", "start"]:
                    return cloud.start(self, segments[2])
                return self._send(404)

        return Handler

    def start(self, handler, token: str) -> None:
        if token == CLOSED:
            return handler._send(410)
        if token != GROUP:
            return handler._send(404)
        verifier = secrets.token_urlsafe(48)
        state = f"{token}.{secrets.token_urlsafe(8)}"
        nonce = secrets.token_urlsafe(12)
        self.attempts[state] = {"verifier": verifier, "nonce": nonce}
        query = {"client_id": CLIENT_ID, "redirect_uri": self.callback, "response_type": "code",
                 "scope": "openid email profile", "state": state, "nonce": nonce,
                 "code_challenge": pkce_challenge(verifier), "code_challenge_method": "S256"}
        self.authorize_queries.append(query)
        handler._send(302, {"Location": f"{self.issuer}/authorize?{urlencode(query)}"})

    def complete(self, handler, query: dict) -> None:
        state = (query.get("state") or [""])[0]
        attempt = self.attempts.pop(state, None)
        group_token = state.split(".", 1)[0]
        if attempt is None:
            return handler._send(302, {"Location": f"{self.web}/{group_token}?auth_error=expired"})
        redeemed = requests.post(f"{self.issuer}/token", data={
            "grant_type": "authorization_code", "code": (query.get("code") or [""])[0],
            "redirect_uri": self.callback, "code_verifier": attempt["verifier"],
            "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}, timeout=5)
        if redeemed.status_code != 200:
            return handler._send(302, {"Location": f"{self.web}/{group_token}?auth_error=failed"})
        payload = redeemed.json()["id_token"].split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        assert claims["nonce"] == attempt["nonce"]
        arrival = self.arrivals.setdefault(claims["sub"], {"tokens": [], "claims": claims})
        cookie_name = f"{auth.ARRIVAL_COOKIE_PREFIX}{GROUP_ID}"
        held = None
        for part in (handler.headers.get("Cookie") or "").split(";"):
            name, _, value = part.strip().partition("=")
            if name == cookie_name and value in arrival["tokens"]:
                held = value
        token = held or hashlib.sha256(f"{claims['sub']}{len(arrival['tokens'])}".encode()).hexdigest()[:20]
        if token not in arrival["tokens"]:
            arrival["tokens"].append(token)
        handler._send(302, {"Location": f"{self.web}/{token}",
                            "Set-Cookie": f"{cookie_name}={token}; Path=/v2/i/auth/google/callback; "
                                          "Max-Age=2592000; HttpOnly; SameSite=Lax"})


@pytest.fixture()
def cloud(issuer):
    fake = _Cloud(issuer)
    thread = threading.Thread(target=fake.httpd.serve_forever, daemon=True)
    thread.start()
    yield fake
    fake.httpd.shutdown()
    fake.httpd.server_close()


@pytest.fixture()
def config(tmp_path, issuer, cloud):
    base = load_config(tmp_path / "absent.toml", validate=False)
    return dataclasses.replace(base, cloud_url=cloud.base, oidc_url=issuer)


def _stranger(config, letter: str, name: str) -> auth.StubStranger:
    return auth.register_stranger(config, f"stranger-{letter}-{secrets.token_hex(3)}", name)


# ------------------------------------------------------------------------- FR-1: registering a stranger

def test_a_stranger_is_registered_on_the_stub_with_a_derived_sub_and_a_test_address(config):
    """`POST /identities`: the `sub` is the stub's (`cell-<id>`), never supplied; the address is under the reserved
    `.test` domain (the journey prints no real person's email); `given_name` is the name's first word, as the stub's
    ID token carries it."""
    maya = _stranger(config, "a", "Maya Fenwick")
    assert maya.sub == f"cell-{maya.id}"
    assert maya.email == f"{maya.id}@{auth.STRANGER_EMAIL_DOMAIN}" and maya.email.endswith(".test")
    assert maya.given_name == "Maya"
    listed = requests.get(f"{config.oidc_base_url}/identities", timeout=5).json()["identities"]
    assert [i["id"] for i in listed if i["id"] == maya.id] == [maya.id]


def test_a_taken_id_is_refused_by_name(config):
    maya = _stranger(config, "a", "Maya Fenwick")
    with pytest.raises(RuntimeError, match="409"):
        auth.register_stranger(config, maya.id, "Maya Fenwick")


# ------------------------------------------------------------------------------ FR-1: the wire sign-in

def test_the_wire_sign_in_walks_start_the_issuer_and_the_participant_callback(config, cloud):
    """Three hops, each followed by hand: start (302 to this profile's issuer), the stub's `/authorize` with
    `identity=` appended to the URL keel-cloud produced (302 to the participant callback), the callback (302 to the
    arrival's own `/i/{token}`, its cookie kept by the session)."""
    maya = _stranger(config, "a", "Maya Fenwick")
    _, signed = auth.sign_in_arrival(config, f"http://localhost:5173/i/{GROUP}", maya)
    assert signed.refused is None and signed.auth_error is None
    assert signed.group_token == GROUP
    assert signed.landed == f"{cloud.web}/{signed.token}" and signed.token and signed.token != GROUP
    assert [status for status, _ in signed.hops] == [302, 302, 302]
    assert signed.hops[0][1] == f"{cloud.base}/v2/i/{GROUP}/auth/google/start"
    assert signed.hops[1][1].startswith(f"{config.oidc_base_url}/authorize")
    assert signed.hops[2][1] == cloud.callback
    assert signed.cookie == f"{auth.ARRIVAL_COOKIE_PREFIX}{GROUP_ID}"
    # keel-cloud's own authorize request travelled: its state, its nonce, the participant redirect URI, no `hd`
    sent = cloud.authorize_queries[-1]
    assert sent["redirect_uri"] == cloud.callback and "hd" not in sent and sent["state"].startswith(f"{GROUP}.")
    # the stub's ID token carried the stranger, and `given_name` the name's first word
    claims = cloud.arrivals[maya.sub]["claims"]
    assert (claims["email"], claims["name"], claims["given_name"]) == (maya.email, maya.name, maya.given_name)


def test_the_same_session_comes_back_to_the_same_token_and_another_browser_to_a_new_one(config, cloud):
    """keel-cloud 162 judgement call 3: the `keel_arrival_<group>` cookie keeps the arrival's token for this browser;
    a fresh session is another browser (a new token to the same arrival)."""
    tomas = _stranger(config, "b", "Tomas Arden")
    session, first = auth.sign_in_arrival(config, GROUP, tomas)
    _, again = auth.sign_in_arrival(config, GROUP, tomas, session=session)
    _, elsewhere = auth.sign_in_arrival(config, GROUP, tomas)
    assert again.token == first.token
    assert elsewhere.token and elsewhere.token != first.token
    assert cloud.arrivals[tomas.sub]["tokens"] == [first.token, elsewhere.token]


def test_a_link_that_takes_nobody_is_refused_at_the_start(config):
    """Closed, full, or the founder's balance under one interview: start answers 410 and nobody is sent to the
    issuer."""
    jun = _stranger(config, "d", "Jun Halvorsen")
    _, refused = auth.sign_in_arrival(config, f"/i/{CLOSED}", jun)
    assert refused.refused == 410 and refused.token is None and len(refused.hops) == 1


@pytest.mark.parametrize("url, token", [
    ("http://localhost:5173/i/abc123", "abc123"),
    ("http://localhost:5173/i/abc123/", "abc123"),
    ("http://localhost:5173/i/abc123?auth_error=expired", "abc123"),
    ("/i/abc123?x=1", "abc123"),
    ("abc123", "abc123"),
])
def test_the_token_is_the_links_last_segment(url, token):
    assert auth.token_of(url) == token


# ------------------------------------------------------------------------------- FR-1: the environment

def test_the_participant_callback_is_the_clouds_own_beside_the_founders(tmp_path):
    """keel-cloud 162's tasks.md: `KEEL_GOOGLE_PARTICIPANT_REDIRECT_URI` on the cloud's origin, beside the founder's,
    on both local profiles; `cloud.build_env` carries it."""
    from stack import cloud as cloud_mod
    for profile, port in (("eval", 18080), ("playground", 18081)):
        cfg = load_config(tmp_path / "absent.toml", validate=False, profile=profile)
        env = oidc.cloud_env(cfg)
        assert env["KEEL_GOOGLE_PARTICIPANT_REDIRECT_URI"] == f"http://localhost:{port}/v2/i/auth/google/callback"
        assert env["KEEL_GOOGLE_REDIRECT_URI"] == f"http://localhost:{port}/v2/auth/google/callback"
        assert cloud_mod.build_env(cfg)["KEEL_GOOGLE_PARTICIPANT_REDIRECT_URI"] == \
            env["KEEL_GOOGLE_PARTICIPANT_REDIRECT_URI"]


# ---------------------------------------------------------------------------- FR-1: the browser sign-in

def test_the_browser_sign_in_presses_the_cards_link_then_the_strangers_own_button():
    """`Arrival.sign_in`: the card's *Continue with Google* (a link, keel-web 136's `arrival-google`), the stub's
    picker, the stranger's button by the hidden `identity` field -- as `Auth.sign_in` does for a founder; never a
    cookie set by hand."""
    source = inspect.getsource(browser_mod.Arrival.sign_in)
    assert "ARRIVAL_GOOGLE" in source
    assert 'get_by_role("heading", name="Choose an account")' in source
    assert "chooser_button_selector(stranger.id)" in source
    assert "add_cookies" not in inspect.getsource(browser_mod.Arrival)


def test_the_cards_words_are_136s():
    """keel-web 136 `translate.ts`: the places, the interviewer's row, the heading's rule (J-11), the greeting and the
    who line (J-14)."""
    assert browser_mod.arrival_places(19) == "19 of 20 places left on this link"
    assert browser_mod.arrival_interviewer(9) == "Keel's interviewer asks the questions · about 9 minutes"
    assert browser_mod.arrival_heading("Eval Founder", "Eval is exploring how restaurants count stock.") == \
        "Eval Founder is exploring how restaurants count stock."
    assert browser_mod.arrival_heading("Eval Founder", "Eval Founder is exploring it.") == "Eval Founder is exploring it."
    assert browser_mod.arrival_heading("Eval Founder", "How restaurants count stock.") == \
        "Eval Founder is asking: How restaurants count stock."
    assert browser_mod.arrival_hello("Maya", "Eval Founder is exploring it.") == "Hi Maya. Eval Founder is exploring it."
    assert browser_mod.arrival_signed_in("Maya") == "Signed in with Google as Maya · not you?"
