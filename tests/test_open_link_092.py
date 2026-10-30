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


# ================================================================================= FR-3: the register read

from playwright.sync_api import sync_playwright                                  # noqa: E402

from harness import interviews_screens as iv                                     # noqa: E402
from harness.steps import Recorder                                               # noqa: E402

WEB = load_config(validate=False).keel_web


def _web_source(relative: str) -> str:
    path = WEB / relative
    if not path.is_file():
        pytest.skip(f"keel-web is not checked out at {WEB}")
    return path.read_text(encoding="utf-8")


def test_send_mores_third_way_is_136s_words():
    """keel-web 136 FR-1 `SEND_WHO.GROUP`, the name box, the cap line, the hint -- read off the checkout the stack
    serves, so a reworded line fails here before it fails a journey."""
    words = _web_source("src/lib/translate.ts")
    for text in (iv.WHO_GROUP, iv.WHO_GROUP_LINE, iv.SEND_GROUP_NAME_LABEL, iv.SEND_GROUP_NAME_EXAMPLE,
                 iv.SEND_GROUP_HINT, iv.KIND_FROM_GROUP, iv.GROUP_NOBODY_YET, iv.SENT_TABS_LABEL,
                 iv.GROUP_COPY_LINK, iv.GROUP_CLOSE_WORD, iv.GROUP_REOPEN_WORD,
                 browser_mod.ARRIVAL_CONTINUE_GOOGLE, browser_mod.ARRIVAL_CONSENT_WORDS):
        assert text.replace("'", "\\'") in words or text in words, text
    lead, _, rest = iv.SEND_GROUP_CAP_LINE.partition(" After")
    assert f'SEND_GROUP_CAP_LEAD = "{lead}"' in words and f'" After{rest}"' in words
    assert f"GROUP_NAME_MAX = {iv.GROUP_NAME_MAX}" in words and f"GROUP_CAP = {iv.GROUP_CAP}" in words
    assert "`Make the link · ${format}`" in words and "`The link for ${group} is ready`" in words
    assert "`${answered} of ${cap} answered`" in words and "`Copy link · ${name}`" in words
    assert "`By name · ${n}`" in words and "`By group · ${n}`" in words
    assert "lead: `${answered} answered`" in words and "rest: ` · ${planned} planned" in words


@pytest.mark.parametrize("relative, ids", [
    ("src/components/interviews/SendMorePopup.tsx",
     ["send-who-${option}", "send-group", "send-group-cap", "group-link-made", 'id="send-group-name"']),
    ("src/components/interviews/SentPage.tsx", ["sent-study-line", "sent-tab-${key}"]),
    ("src/components/interviews/GroupSection.tsx",
     ["sent-group", "data-group=", "data-closed=", "group-name", "group-count", "group-link", "group-close",
      "group-reopen", "group-empty"]),
    ("src/components/interviews/LinksTable.tsx", ["row-email"]),
    ("src/routes/participant/GroupArrivalCard.tsx",
     ["group-arrival", "arrival-heading", "arrival-interviewer", "arrival-places", "arrival-google", "arrival-consent",
      "arrival-auth-error"]),
    ("src/components/interview/IntroScreen.tsx", ["arrival-greeting", "arrival-who", "arrival-not-you"]),
    ("src/components/interview/ai/AiIntro.tsx", ["arrival-greeting", "ai-intro", "choice-write", "choice-talk"]),
    ("src/routes/participant/ParticipantRoute.tsx", ["link-inactive", "GROUP_ARRIVAL"]),
])
def test_every_pin_the_harness_reads_is_in_136s_markup(relative, ids):
    """136's tasks.md, *The pins for keel-e2e-eval 092*: each test id is in the component that draws it."""
    source = _web_source(relative)
    missing = [i for i in ids if i not in source]
    assert not missing, (relative, missing)


@pytest.fixture(scope="module")
def chromium():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _row(invitation: str, name: str, email: str | None, status: str, action: str) -> str:
    mail = f'<span class="lt-email" data-testid="row-email">{email}</span>' if email else ""
    return (f'<tr data-invitation="{invitation}"><td class="lt-c-who" data-label="Who"><b>{name}</b>{mail}</td>'
            f'<td class="lt-c-format soft" data-label="Format">Choice</td>'
            f'<td class="lt-c-made soft" data-label="Made">Today 10:02</td>'
            f'<td class="lt-c-status" data-label="Status">{status}</td>'
            f'<td class="lt-c-action lt-action" data-label=""><button type="button" class="btn link" '
            f'aria-label="{action}, {name}">{action}</button></td></tr>')


SENT_HTML = f"""<!doctype html><html><body><main>
<p class="sent__study" id="sent-study" data-testid="sent-study-line"><b>1 answered</b> · 0 planned · 1 counted</p>
<div class="toggle sent__tabs" role="tablist" aria-label="{iv.SENT_TABS_LABEL}">
  <button type="button" role="tab" id="sent-tab-name" aria-selected="false" data-testid="sent-tab-name">By name · 0</button>
  <button type="button" role="tab" id="sent-tab-group" aria-selected="true" class="on" data-testid="sent-tab-group">By group · 1</button>
</div>
<div role="tabpanel" id="sent-panel-group" aria-labelledby="sent-tab-group">
 <section class="sent__group" data-testid="sent-group" data-group="g-1" data-closed="false" aria-label="Restaurant managers' forum">
  <div class="sent__group-top"><h3 class="lt-head sent__group-name" data-testid="group-name" style="text-transform: uppercase">Restaurant managers' forum</h3>
   <span class="sent__group-count" data-testid="group-count">1 of 20 answered</span></div>
  <div class="sent__group-actions"><span class="linkshort" data-testid="group-link" title="http://localhost:5173/i/gRoUp">…/i/gRoU…up</span>
   <button type="button" class="btn small" aria-label="Copy link · Restaurant managers' forum">Copy link</button>
   <button type="button" class="btn small" data-testid="group-close">Close link</button></div>
  <section class="sent__links" data-testid="links"><div class="sent__register"><table class="ppl ppl--sent"><tbody>
   {_row("inv-c", "Iris Calloway", "c@strangers.keel-e2e-eval.test", "Not opened", "New link")}
   {_row("inv-b", "Tomas Arden", "b@strangers.keel-e2e-eval.test", "Opened, not answered", "New link")}
   {_row("inv-a", "Maya Fenwick", "a@strangers.keel-e2e-eval.test", "Answered · Today 10:09", "See answers")}
  </tbody></table></div><div class="lt-foot"><span class="hint">{iv.KIND_FROM_GROUP}</span></div></section>
 </section>
</div></main></body></html>"""


def test_the_by_group_tab_is_read_as_136_draws_it(tmp_path, chromium):
    """The study line, the two tabs, one group's section (its name as typed -- the DOM text, not the uppercased
    render --, the counter, the short link with the full url as its title, *Copy link*'s name, *Close link*) and its
    rows: the register's own cells, *Who* the name alone, the email under it, *Kind · from* folded from the footer."""
    page = chromium.new_page()
    try:
        page.set_content(SENT_HTML)
        sent = iv.Interviews(page, Recorder(tmp_path), "http://localhost:5173")
        assert sent.study_line() == iv.sent_study_line(1, 0, 1)
        assert sent.tabs() == {"label": iv.SENT_TABS_LABEL,
                               "name": {"text": iv.sent_tab_by_name(0), "role": "tab", "selected": False},
                               "group": {"text": iv.sent_tab_by_group(1), "role": "tab", "selected": True}}
        [group] = sent.groups()
        assert group["id"] == "g-1" and group["closed"] == "false" and group["name_tag"] == "H3"
        assert group["name"] == "Restaurant managers' forum"
        assert group["count"] == iv.group_answered(1) and group["url"] == "http://localhost:5173/i/gRoUp"
        assert group["copy"] == iv.group_link_label("Restaurant managers' forum")
        assert (group["close"], group["reopen"], group["empty"]) == (iv.GROUP_CLOSE_WORD, None, None)
        rows = {r["Who"]: r for r in group["rows"]}
        assert list(rows) == ["Iris Calloway", "Tomas Arden", "Maya Fenwick"]
        maya = rows["Maya Fenwick"]
        assert maya["email"] == "a@strangers.keel-e2e-eval.test" and maya["email_under_name"] is True
        assert maya["Kind · from"] == iv.KIND_FROM_GROUP and maya["actions"] == ["See answers"]
        assert maya["Status"].startswith(iv.REGISTER_STATUS["ANSWERED"]) and maya["invitation"] == "inv-a"
        assert rows["Iris Calloway"]["actions"] == ["New link"]
    finally:
        page.close()


ARRIVAL_HTML = """<!doctype html><html><body><div class="iv-page"><main class="iv-body iv-arrival" data-testid="group-arrival">
<p class="iv-kicker">About this conversation</p>
<h1 class="iv-topic" data-testid="arrival-heading">Eval Founder is exploring how restaurants count stock.</h1>
<div class="iv-arrival__who" data-testid="arrival-interviewer"><span>Keel's interviewer asks the questions · about 9 minutes</span></div>
<div class="iv-arrival__go"><p class="iv-facts" data-testid="arrival-places">20 of 20 places left on this link</p>
<a class="btn google" href="/v2/i/gRoUp/auth/google/start" data-testid="arrival-google"><svg aria-hidden="true"></svg>Continue with Google</a>
<p class="iv-facts" data-testid="arrival-consent">CONSENT</p></div></main></div></body></html>"""


def test_the_arrival_card_is_read_as_136_draws_it(tmp_path, chromium):
    page = chromium.new_page()
    try:
        page.set_content(ARRIVAL_HTML.replace("CONSENT", browser_mod.ARRIVAL_CONSENT_WORDS))
        read = browser_mod.Arrival(page, Recorder(tmp_path), "http://localhost:5173").read()
        assert read["state"] == "GROUP_ARRIVAL" and read["heading_tag"] == "H1"
        assert read["heading"] == "Eval Founder is exploring how restaurants count stock."
        assert read["interviewer"] == browser_mod.arrival_interviewer(9)
        assert read["places"] == browser_mod.arrival_places(20)
        assert read["google"] == {"text": "Continue with Google", "href": "/v2/i/gRoUp/auth/google/start", "tag": "A",
                                  "role_link": 1}
        assert read["consent"] == browser_mod.ARRIVAL_CONSENT_WORDS
        assert read["auth_error"] is None and read["begin"] == 0
        page.set_content('<div class="iv-shell iv"><p class="hello" data-testid="link-inactive">'
                         'This link is no longer active.</p></div>')
        assert browser_mod.Arrival(page, Recorder(tmp_path), "http://x").read()["inactive"] == \
            "This link is no longer active."
    finally:
        page.close()


INTRO_HTML = """<!doctype html><html><body><div class="iv-page"><main class="iv-body" data-testid="ai-intro" data-intro="CHOICE">
<p class="iv-arrival-hi" data-testid="arrival-greeting">Hi Maya. Eval Founder is exploring it.</p>
<p class="iv-arrival-who" data-testid="arrival-who">Signed in with Google as Maya · <a href="/i/gRoUp" data-testid="arrival-not-you">not you?</a></p>
<div class="iv-actions"><button type="button" data-testid="choice-talk">Talk to Daphne · about 9 minutes</button>
<button type="button" data-testid="choice-write">Answer in writing · about 9 minutes</button></div></main></div></body></html>"""


def test_the_intro_after_the_sign_in_is_read_as_136_draws_it(tmp_path, chromium):
    page = chromium.new_page()
    try:
        page.set_content(INTRO_HTML)
        intro = browser_mod.Arrival(page, Recorder(tmp_path), "http://x").intro(timeout_s=5)
        assert intro["state"] == "INTERVIEW" and intro["intro"] == "CHOICE"
        assert intro["greeting"] == browser_mod.arrival_hello("Maya", "Eval Founder is exploring it.")
        assert intro["who"] == browser_mod.arrival_signed_in("Maya") and intro["not_you"] == "/i/gRoUp"
        assert intro["buttons"] == ["choice-talk", "choice-write"]
        page.set_content('<div class="iv-shell iv"><p class="hello">You have already answered. Thank you.</p></div>')
        assert browser_mod.Arrival(page, Recorder(tmp_path), "http://x").intro(timeout_s=5) == {
            "state": "ALREADY_ANSWERED", "line": "You have already answered. Thank you.", "url": "about:blank"}
    finally:
        page.close()


def test_send_group_presses_the_third_way_names_it_and_reads_the_link_once():
    """`Interviews.send_group`: the third radio by its test id, the name in `#send-group-name`, the button by its
    words' start (*Make the link · *), the `POST .../groups` awaited (and keel-web's one silent retry on a stale
    revision followed), the link read from `group-link-made`, Done."""
    source = inspect.getsource(iv.Interviews.send_group)
    for needle in ("send-who-GROUP", "SEND_GROUP_NAME", 're.compile(r"^Make the link · ")', 'endswith("/groups")',
                   "GROUP_LINK_MADE", "SEND_DONE", '"concurrency"'):
        assert needle in source, needle
