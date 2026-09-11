"""Stackless: the stub OIDC issuer, end to end, with no stack and no keel-cloud (spec 015, first
half; keel-cloud `canon/designs/google-sign-in-design.md` §10.1-§10.3).

This half of the feature lands **before** keel-cloud's own Google sign-in (its spec 032), so it
has to be provable entirely on its own. That is what this file is: a real server on a real
socket, the real Authorization Code + PKCE walk over HTTP, and an ID token verified RS256 against
the JWKS the same server publishes.

**How the token is verified here.** With `hashlib`, `hmac` and `pow` -- there is no `cryptography`
in this harness (checked: `requirements.txt` and the playwright venv both), so
`stack/stub_oidc/keys.py:verify_rs256` recovers the PKCS#1 v1.5 block with the *public* exponent
from the JWKS and compares it against the SHA-256 DigestInfo it should be. The key itself comes
from `openssl genrsa`, once per session. That is a genuine RSA verification and not a re-run of
the signing code: it uses `e` and `n` off the published JWKS and never touches `d`.
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import threading
import time

import pytest
import requests

from stack import oidc
from stack.auth import FOUNDER_EMAIL, FOUNDER_NAME
from stack.config import load_config
from stack.stub_oidc import keys as keymod
from stack.stub_oidc.server import (STUB_BREAKS, Identity, make_server, picker_html,
                                     pkce_challenge)

CLIENT_ID = "test-client"
CLIENT_SECRET = "test-client-secret"  # noqa: S105 - a stub's own fixture, never a real secret
REDIRECT_URI = "http://localhost:18080/v2/auth/google/callback"

IDENTITIES = [
    Identity(id="founder-a", sub="stub-founder-1", email="a@keel-e2e-eval.test",
             name="Eval Founder"),
    Identity(id="founder-b", sub="stub-founder-2", email="b@keel-e2e-eval.test",
             name="Nour Haddad", picture="http://localhost/p.png", hd="keel-e2e-eval.test"),
]


# --------------------------------------------------------------------------------- the fixture

@pytest.fixture(scope="module")
def rsa_key(tmp_path_factory):
    """One `openssl genrsa` for the whole module -- the same one call `make up` makes."""
    return keymod.load_or_generate(tmp_path_factory.mktemp("oidc") / "key.pem")


@pytest.fixture(scope="module")
def issuer(rsa_key):
    """A real server on a real (ephemeral) socket: everything below goes over HTTP."""
    httpd = make_server(port=0, key=rsa_key, client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                        identities=IDENTITIES)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd.stub.issuer
    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=5)


def _authorize_params(**overrides) -> dict:
    verifier = secrets.token_urlsafe(48)
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": secrets.token_urlsafe(16),
        "nonce": secrets.token_urlsafe(16),
        "code_challenge": pkce_challenge(verifier),
        "code_challenge_method": "S256",
        # The default walk names its founder, the way a wire-level fixture does (§10.2); the
        # picker tests pass `identity=None` to get the page instead.
        "identity": "founder-a",
    }
    params.update(overrides)
    params = {k: v for k, v in params.items() if v is not None}
    params["_verifier"] = verifier
    return params


def _get_code(issuer_url: str, params: dict) -> tuple[str, str]:
    """`/authorize` with an identity chosen -> (code, state), refusing to follow the redirect so
    the `Location` itself can be read."""
    query = {k: v for k, v in params.items() if not k.startswith("_")}
    response = requests.get(f"{issuer_url}/authorize", params=query, allow_redirects=False,
                            timeout=5)
    assert response.status_code == 302, response.text
    location = response.headers["Location"]
    assert location.startswith(REDIRECT_URI)
    returned = requests.utils.urlparse(location).query
    fields = dict(pair.split("=", 1) for pair in returned.split("&"))
    return fields.get("code", ""), fields.get("state", "")


def _redeem(issuer_url: str, code: str, verifier: str, **overrides) -> requests.Response:
    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    form.update(overrides)
    form = {k: v for k, v in form.items() if v is not None}
    return requests.post(f"{issuer_url}/token", data=form, timeout=5)


# ------------------------------------------------------------------------------- the documents

def test_discovery_names_its_own_origin_and_nothing_else(issuer):
    doc = requests.get(f"{issuer}/.well-known/openid-configuration", timeout=5).json()
    assert doc["issuer"] == issuer
    assert doc["authorization_endpoint"] == f"{issuer}/authorize"
    assert doc["token_endpoint"] == f"{issuer}/token"
    assert doc["jwks_uri"] == f"{issuer}/jwks"
    # Every URL is absolute against its own origin, so keel-cloud needs no knowledge of the stub
    # beyond KEEL_OIDC_ISSUER (§10.1).
    for key in ("authorization_endpoint", "token_endpoint", "jwks_uri"):
        assert doc[key].startswith(issuer)


def test_discovery_declares_the_algorithms_the_design_checks(issuer):
    doc = requests.get(f"{issuer}/.well-known/openid-configuration", timeout=5).json()
    assert doc["response_types_supported"] == ["code"]
    assert doc["id_token_signing_alg_values_supported"] == ["RS256"]
    assert doc["code_challenge_methods_supported"] == ["S256"]
    assert set(doc["scopes_supported"]) == {"openid", "email", "profile"}


def test_jwks_serves_exactly_one_rsa_signing_key(issuer):
    jwks = requests.get(f"{issuer}/jwks", timeout=5).json()
    assert list(jwks) == ["keys"]
    (jwk,) = jwks["keys"]
    assert jwk["kty"] == "RSA"
    assert jwk["use"] == "sig"
    assert jwk["alg"] == "RS256"
    assert jwk["kid"] == "stub-1"
    # base64url, unpadded, and a 2048-bit modulus.
    assert "=" not in jwk["n"] and "+" not in jwk["n"] and "/" not in jwk["n"]
    assert len(keymod.b64url_decode(jwk["n"])) == 256
    assert int.from_bytes(keymod.b64url_decode(jwk["e"]), "big") == 65537


def test_jwks_json_is_an_alias_for_the_same_document(issuer):
    assert (requests.get(f"{issuer}/jwks", timeout=5).json()
            == requests.get(f"{issuer}/jwks.json", timeout=5).json())


def test_anything_else_is_a_404(issuer):
    for path in ("/", "/userinfo", "/login", "/.well-known/jwks.json"):
        assert requests.get(f"{issuer}{path}", timeout=5).status_code == 404
    assert requests.post(f"{issuer}/authorize", data={}, timeout=5).status_code == 404


# ------------------------------------------------------------------ the walk, and the ID token

def test_authorize_then_token_yields_an_id_token_that_verifies_against_the_jwks(issuer):
    params = _authorize_params()
    code, state = _get_code(issuer, params)
    assert state == params["state"], "the state travels back verbatim"

    response = _redeem(issuer, code, params["_verifier"])
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"] == "Bearer"
    assert body["access_token"] == "stub-access-token"
    assert body["expires_in"] == 300

    jwk = requests.get(f"{issuer}/jwks", timeout=5).json()["keys"][0]
    claims = keymod.verify_rs256(body["id_token"], jwk)

    assert claims["iss"] == issuer
    assert claims["aud"] == CLIENT_ID
    assert claims["azp"] == CLIENT_ID
    assert claims["sub"] == "stub-founder-1"
    assert claims["email"] == "a@keel-e2e-eval.test"
    assert claims["email_verified"] is True
    assert claims["name"] == "Eval Founder"
    assert claims["given_name"] == "Eval"
    assert claims["family_name"] == "Founder"
    assert claims["nonce"] == params["nonce"]
    assert claims["exp"] > claims["iat"]
    assert "picture" not in claims and "hd" not in claims  # founder A declares neither


def test_the_id_tokens_header_names_the_jwks_key_by_kid(issuer):
    params = _authorize_params()
    code, _ = _get_code(issuer, params)
    token = _redeem(issuer, code, params["_verifier"]).json()["id_token"]
    header = json.loads(keymod.b64url_decode(token.split(".")[0]))
    assert header == {"alg": "RS256", "kid": "stub-1", "typ": "JWT"}


def test_an_identitys_picture_and_hd_ride_the_token_when_it_declares_them(issuer):
    params = _authorize_params(identity="founder-b")
    code, _ = _get_code(issuer, params)
    token = _redeem(issuer, code, params["_verifier"]).json()["id_token"]
    jwk = requests.get(f"{issuer}/jwks", timeout=5).json()["keys"][0]
    claims = keymod.verify_rs256(token, jwk)
    assert claims["sub"] == "stub-founder-2"
    assert claims["name"] == "Nour Haddad"
    assert claims["picture"] == "http://localhost/p.png"
    assert claims["hd"] == "keel-e2e-eval.test"


def test_client_secret_basic_authenticates_the_same_as_the_form(issuer):
    params = _authorize_params()
    code, _ = _get_code(issuer, params)
    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    response = requests.post(f"{issuer}/token", data={
        "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI,
        "code_verifier": params["_verifier"],
    }, headers={"Authorization": f"Basic {basic}"}, timeout=5)
    assert response.status_code == 200, response.text
    assert "id_token" in response.json()


# ------------------------------------------------------------------------------ the picker

def test_authorize_with_no_identity_shows_the_chooser(issuer):
    params = {k: v for k, v in _authorize_params(identity=None).items()
              if not k.startswith("_")}
    response = requests.get(f"{issuer}/authorize", params=params, allow_redirects=False,
                            timeout=5)
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/html")
    page = response.text
    assert "<h1>Choose an account</h1>" in page
    # One button per configured identity, labelled with that identity's own *name* -- which is
    # what `get_by_role("button", name="Eval Founder")` will click (§10.2).
    for identity in IDENTITIES:
        assert f'<button type="submit">{identity.name}</button>' in page
    # and the click carries the whole authorize request back, so the code path is identical.
    for field in ("state", "nonce", "code_challenge"):
        assert f'name="{field}" value="{params[field]}"' in page
    assert "Cancel" in page


def test_the_chooser_says_what_it_is_and_offers_no_password(issuer):
    params = {k: v for k, v in _authorize_params(identity=None).items()
              if not k.startswith("_")}
    page = requests.get(f"{issuer}/authorize", params=params, timeout=5).text
    assert "KEEL_OIDC_ISSUER" in page
    assert "password" not in page.lower().replace("has no password", "")
    assert 'type="password"' not in page


def test_identity_and_login_hint_both_skip_the_page(issuer):
    for hint in ({"identity": "founder-b"},
                 {"identity": None, "login_hint": "stub-founder-2"},
                 {"identity": "b@keel-e2e-eval.test"}):
        params = _authorize_params(**hint)
        code, _ = _get_code(issuer, params)
        token = _redeem(issuer, code, params["_verifier"]).json()["id_token"]
        claims = json.loads(keymod.b64url_decode(token.split(".")[1]))
        assert claims["sub"] == "stub-founder-2"


def test_an_unknown_identity_is_a_404_naming_the_configured_ones(issuer):
    params = {k: v for k, v in _authorize_params(identity="nobody").items()
              if not k.startswith("_")}
    response = requests.get(f"{issuer}/authorize", params=params, timeout=5)
    assert response.status_code == 404
    assert "founder-a" in response.text and "founder-b" in response.text


def test_cancel_redirects_with_access_denied_and_the_state(issuer):
    params = {k: v for k, v in _authorize_params(cancel="1").items() if not k.startswith("_")}
    response = requests.get(f"{issuer}/authorize", params=params, allow_redirects=False,
                            timeout=5)
    assert response.status_code == 302
    location = response.headers["Location"]
    assert "error=access_denied" in location
    assert params["state"] in location
    assert "code=" not in location


# ------------------------------------------------------------------------- the refusals (§10.1)

def test_an_unknown_client_never_reaches_the_redirect_uri(issuer):
    params = {k: v for k, v in _authorize_params(client_id="not-our-client").items()
              if not k.startswith("_")}
    response = requests.get(f"{issuer}/authorize", params=params, allow_redirects=False,
                            timeout=5)
    # 400 in the browser, not a redirect: answering an unknown client *at* its own redirect_uri
    # is how open redirectors are built.
    assert response.status_code == 400
    assert "unknown client_id" in response.text


def test_a_redirect_uri_that_is_not_an_absolute_url_is_refused(issuer):
    for bad in ("/relative", "javascript:alert(1)", ""):
        params = {k: v for k, v in _authorize_params(redirect_uri=bad).items()
                  if not k.startswith("_")}
        response = requests.get(f"{issuer}/authorize", params=params, allow_redirects=False,
                                timeout=5)
        assert response.status_code == 400, bad


def test_authorize_requires_state_and_nonce(issuer):
    for missing in ("state", "nonce"):
        params = {k: v for k, v in _authorize_params(**{missing: ""}).items()
                  if not k.startswith("_")}
        response = requests.get(f"{issuer}/authorize", params=params, allow_redirects=False,
                                timeout=5)
        assert response.status_code == 400
        assert "state and nonce" in response.text


def test_authorize_requires_code_flow_openid_scope_and_s256(issuer):
    cases = {
        "response_type": ({"response_type": "token"}, "unsupported_response_type"),
        "scope": ({"scope": "email profile"}, "invalid_scope"),
        "method": ({"code_challenge_method": "plain"}, "invalid_request"),
        "challenge": ({"code_challenge": ""}, "invalid_request"),
    }
    for label, (override, expected) in cases.items():
        params = {k: v for k, v in _authorize_params(**override).items()
                  if not k.startswith("_")}
        response = requests.get(f"{issuer}/authorize", params=params, allow_redirects=False,
                                timeout=5)
        assert response.status_code == 302, label
        assert f"error={expected}" in response.headers["Location"], label
        assert "code=" not in response.headers["Location"], label


def test_token_refuses_an_unknown_code(issuer):
    response = _redeem(issuer, "not-a-code-anyone-issued", "whatever")
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_grant"


def test_token_refuses_a_bad_pkce_verifier(issuer):
    params = _authorize_params()
    code, _ = _get_code(issuer, params)
    response = _redeem(issuer, code, secrets.token_urlsafe(48))
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_grant"
    assert "code_verifier" in response.json()["error_description"]


def test_token_refuses_a_missing_pkce_verifier(issuer):
    params = _authorize_params()
    code, _ = _get_code(issuer, params)
    assert _redeem(issuer, code, "", code_verifier="").status_code == 400


def test_token_refuses_an_unknown_client(issuer):
    params = _authorize_params()
    code, _ = _get_code(issuer, params)
    response = _redeem(issuer, code, params["_verifier"], client_secret="wrong")
    assert response.status_code == 401
    assert response.json()["error"] == "invalid_client"


def test_token_refuses_a_replayed_code(issuer):
    params = _authorize_params()
    code, _ = _get_code(issuer, params)
    assert _redeem(issuer, code, params["_verifier"]).status_code == 200
    again = _redeem(issuer, code, params["_verifier"])
    assert again.status_code == 400
    assert again.json()["error"] == "invalid_grant"


def test_a_code_is_burned_even_by_a_failed_redemption(issuer):
    """RFC 6749 §4.1.2: a code that has been *offered* is spent. Strictness here is the point --
    a stub that let a second try through would let a keel-cloud replay defect pass (G2)."""
    params = _authorize_params()
    code, _ = _get_code(issuer, params)
    assert _redeem(issuer, code, "wrong-verifier").status_code == 400
    assert _redeem(issuer, code, params["_verifier"]).status_code == 400


def test_token_refuses_a_mismatched_redirect_uri(issuer):
    params = _authorize_params()
    code, _ = _get_code(issuer, params)
    response = _redeem(issuer, code, params["_verifier"],
                       redirect_uri="http://localhost:18081/v2/auth/google/callback")
    assert response.status_code == 400
    assert "redirect_uri" in response.json()["error_description"]


def test_token_refuses_any_grant_but_authorization_code(issuer):
    response = requests.post(f"{issuer}/token", data={
        "grant_type": "client_credentials", "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }, timeout=5)
    assert response.status_code == 400
    assert response.json()["error"] == "unsupported_grant_type"


# ------------------------------------------------- stub_break: for S-011, after keel-cloud 032

def test_every_stub_break_bends_exactly_one_thing(issuer):
    """`?stub_break=<what>` is §10.1's negative-testing lever, and it exists so S-011 can prove
    *keel-cloud* refuses. S-011 itself is the second half of this spec and waits on keel-cloud
    032; the lever is proven here, now, so that scenario starts from a stub that is known good."""
    jwk = requests.get(f"{issuer}/jwks", timeout=5).json()["keys"][0]
    for what in STUB_BREAKS:
        params = _authorize_params(stub_break=what)
        code, _ = _get_code(issuer, params)
        token = _redeem(issuer, code, params["_verifier"]).json()["id_token"]
        claims = json.loads(keymod.b64url_decode(token.split(".")[1]))
        if what == "sig":
            with pytest.raises(keymod.KeyError_):
                keymod.verify_rs256(token, jwk)
            continue
        keymod.verify_rs256(token, jwk)  # everything but `sig` is still correctly signed
        if what == "iss":
            assert claims["iss"] == "https://accounts.google.com" != issuer
        elif what == "aud":
            assert claims["aud"] != CLIENT_ID and claims["azp"] != CLIENT_ID
        elif what == "exp":
            assert claims["exp"] < time.time(), "expired, and iat older still"
            assert claims["iat"] < claims["exp"]
        elif what == "nonce":
            assert claims["nonce"] != params["nonce"]
        elif what == "email_verified":
            assert claims["email_verified"] is False


def test_an_undeclared_stub_break_is_refused(issuer):
    params = {k: v for k, v in _authorize_params(stub_break="everything").items()
              if not k.startswith("_")}
    response = requests.get(f"{issuer}/authorize", params=params, timeout=5)
    assert response.status_code == 400
    assert "unknown stub_break" in response.text


# ---------------------------------------------------------------------------- the key and RS256

def test_openssl_writes_a_key_this_parser_reads(tmp_path):
    key = keymod.load_or_generate(tmp_path / "k.pem")
    assert key.n.bit_length() == 2048
    assert key.e == 65537
    assert (tmp_path / "k.pem").stat().st_mode & 0o777 == 0o600


def test_a_pkcs1_pem_parses_the_same_as_a_pkcs8_one(tmp_path):
    """`openssl genrsa` writes PKCS#8 on OpenSSL 3.x and PKCS#1 on 1.x; both must read."""
    import subprocess
    pkcs8 = keymod.generate_pem(tmp_path / "k8.pem")
    pkcs1 = tmp_path / "k1.pem"
    subprocess.run(["openssl", "rsa", "-in", str(pkcs8), "-traditional", "-out", str(pkcs1)],
                   capture_output=True, check=True, timeout=30)
    assert "BEGIN RSA PRIVATE KEY" in pkcs1.read_text()
    assert keymod.parse_pem_private_key(pkcs1.read_text()) == \
        keymod.parse_pem_private_key(pkcs8.read_text())


def test_rs256_verification_is_against_the_public_key_alone(rsa_key):
    token = keymod.sign_jwt(rsa_key, {"sub": "x"})
    jwk = rsa_key.public_jwk()
    assert "d" not in jwk
    assert keymod.verify_rs256(token, jwk) == {"sub": "x"}


def test_a_tampered_payload_fails_verification(rsa_key):
    header, payload, signature = keymod.sign_jwt(rsa_key, {"sub": "x"}).split(".")
    forged = keymod.b64url(json.dumps({"sub": "somebody-else"}).encode())
    with pytest.raises(keymod.KeyError_):
        keymod.verify_rs256(f"{header}.{forged}.{signature}", rsa_key.public_jwk())


def test_a_token_signed_by_another_key_fails_verification(rsa_key, tmp_path):
    other = keymod.load_or_generate(tmp_path / "other.pem")
    token = keymod.sign_jwt(other, {"sub": "x"})
    with pytest.raises(keymod.KeyError_):
        keymod.verify_rs256(token, rsa_key.public_jwk())


def test_an_alg_none_token_is_not_verified(rsa_key):
    header = keymod.b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = keymod.b64url(json.dumps({"sub": "x"}).encode())
    with pytest.raises(keymod.KeyError_):
        keymod.verify_rs256(f"{header}.{payload}.", rsa_key.public_jwk())


def test_pkce_challenge_is_s256_base64url_unpadded():
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    expected = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    assert pkce_challenge(verifier) == expected
    assert "=" not in pkce_challenge(verifier)


# ------------------------------------------------------- the lifecycle wiring (§10.2, §10.3)

def test_the_two_identities_are_founder_a_and_founder_b():
    assert [i.id for i in oidc.STUB_IDENTITIES] == ["founder-a", "founder-b"]
    assert oidc.FOUNDER_A.sub == "stub-founder-1"
    assert oidc.FOUNDER_B.sub == "stub-founder-2"
    assert oidc.FOUNDER_B.email == "second-founder@keel-e2e-eval.test"
    # Neither declares a picture: the header's no-picture fallback is the state the whole eval
    # set runs in, and the presence of one gets its own assertion, not a default (§10.2).
    assert all(i.picture is None and i.hd is None for i in oidc.STUB_IDENTITIES)


def test_founder_a_keeps_todays_name_and_email():
    """Those strings are already in greetings, participant pages and screenshots; Google sign-in
    is not a reason to churn them (§10.2). `stack/auth.py` keeps them as assertion constants when
    its password goes, in the second half of this spec."""
    assert oidc.FOUNDER_A.name == FOUNDER_NAME == "Eval Founder"
    assert oidc.FOUNDER_A.email == FOUNDER_EMAIL


def test_the_ports_are_fixed_per_profile(tmp_path):
    assert load_config(tmp_path / "absent.toml", validate=False).oidc_port == 18090
    assert load_config(tmp_path / "absent.toml", validate=False,
                       profile="playground").oidc_port == 18091


def test_stack_toml_carries_both_oidc_ports():
    config = load_config(validate=False)
    playground = load_config(validate=False, profile="playground")
    assert (config.oidc_port, playground.oidc_port) == (18090, 18091)
    assert oidc.issuer_url(config) == "http://localhost:18090"
    assert oidc.issuer_url(playground) == "http://localhost:18091"


def test_the_four_variables_keel_cloud_will_be_pointed_at_it_with(tmp_path):
    config = load_config(tmp_path / "absent.toml", validate=False)
    env = oidc.cloud_env(config)
    assert env == {
        "KEEL_OIDC_ISSUER": "http://localhost:18090",
        "KEEL_GOOGLE_CLIENT_ID": "keel-eval-client",
        "KEEL_GOOGLE_CLIENT_SECRET": "keel-eval-client-secret",
        "KEEL_GOOGLE_REDIRECT_URI": "http://localhost:18080/v2/auth/google/callback",
    }
    # No KEEL_GOOGLE_ALLOWED_DOMAIN: the open posture is what the scenarios exercise, and the
    # closed one is a keel-cloud unit test, not a stack variant (§10.3).
    assert "KEEL_GOOGLE_ALLOWED_DOMAIN" not in env


def test_the_playground_profile_points_at_its_own_stub_and_its_own_callback(tmp_path):
    env = oidc.cloud_env(load_config(tmp_path / "absent.toml", validate=False,
                                     profile="playground"))
    assert env["KEEL_OIDC_ISSUER"] == "http://localhost:18091"
    assert env["KEEL_GOOGLE_REDIRECT_URI"] == \
        "http://localhost:18081/v2/auth/google/callback"


def test_cloud_build_env_carries_them(tmp_path):
    from stack import cloud
    config = load_config(tmp_path / "absent.toml", validate=False)
    env = cloud.build_env(config)
    for name, value in oidc.cloud_env(config).items():
        assert env[name] == value


def test_the_process_and_key_names_are_profile_suffixed(tmp_path):
    evalc = load_config(tmp_path / "absent.toml", validate=False)
    play = load_config(tmp_path / "absent.toml", validate=False, profile="playground")
    assert oidc._process_name(evalc) == "oidc"
    assert oidc._process_name(play) == "oidc-playground"
    assert oidc.key_path(evalc).name == "oidc-key.pem"
    assert oidc.key_path(play).name == "oidc-playground-key.pem"
    assert oidc.key_path(evalc).parent.name == ".stack"


def test_every_boot_gets_a_fresh_key_and_teardown_takes_it_with_it(tmp_path, monkeypatch):
    """Nothing of the stub survives a run (§10.3) -- including the key that signed it. `make up`
    generates a new one and `make down` removes it, so this harness holds no long-lived
    secret-shaped file even though it signs real RS256 tokens."""
    from stack import config as config_module

    monkeypatch.setattr(config_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(oidc, "REPO_ROOT", tmp_path)
    cfg = load_config(tmp_path / "absent.toml", validate=False)
    first = oidc.ensure_key(cfg).read_text()
    second = oidc.ensure_key(cfg).read_text()
    assert first != second, "a boot reusing the previous run's key would outlive its run"
    oidc.clear_key(cfg)
    assert not oidc.key_path(cfg).exists()
    oidc.clear_key(cfg)  # idempotent


def test_teardown_clears_this_profiles_key_and_only_this_profiles():
    import inspect

    from stack import lifecycle
    assert "oidc.clear_key(config)" in inspect.getsource(lifecycle.teardown)


def test_make_down_tears_down_each_profiles_own_stub_and_never_the_others():
    import inspect

    from stack import processes
    source = inspect.getsource(processes.teardown_all_processes)
    assert '"oidc"' in source and '"oidc-playground"' in source


def test_boot_brings_the_stub_up_first_and_the_gates_check_it():
    import inspect

    from stack import lifecycle
    boot = inspect.getsource(lifecycle.boot)
    assert boot.index("oidc.up(config)") < boot.index("postgres.up(config)")
    assert "oidc.is_up(config)" in inspect.getsource(lifecycle.quick_gates_pass)


def _code_only(source: str) -> str:
    """A module's source with every docstring and comment removed, so a check for a deleted name
    cannot be tripped by the sentence explaining that it was deleted."""
    import ast

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = node.body
        if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            node.body = body[1:] or [ast.Pass()]
    return ast.unparse(tree)


def test_the_second_half_has_landed_and_the_password_is_gone():
    """The inverse of the assertion this file carried through the first half. keel-cloud spec 032
    landed, so §10.4-§10.7 are built: `stack/auth.py` has no password of any kind, the picker is
    what `harness/browser.py:Auth.sign_in` clicks, and S-010 and S-011 exist.

    `FOUNDER_PASSWORD` is **deleted, not commented out** (§10.8), and so is every other way into
    keel-cloud that is not `/authorize` -> the callback. This test is what would notice one
    growing back."""
    from pathlib import Path

    from stack import auth

    assert not hasattr(auth, "FOUNDER_PASSWORD")
    assert not hasattr(auth, "ensure_founder_account")
    assert not hasattr(auth, "clear_stored")
    # The **code**, not the prose: this module's docstring narrates what was deleted and why, and
    # a check that could not tell that apart from the thing itself would forbid saying so.
    code = _code_only(Path(auth.__file__).read_text())
    for forbidden in ("FOUNDER_PASSWORD", "password", "/v2/setup", "/v2/login"):
        assert forbidden not in code, f"stack/auth.py still carries {forbidden!r}"

    evals = Path(__file__).resolve().parent.parent / "evals"
    assert (evals / "test_s010_two_founders.py").exists()
    assert (evals / "test_s011_bad_token.py").exists()


def test_no_scenario_reaches_a_retired_route_or_a_password():
    """§10.8, swept across the whole scenario set rather than trusted per file: no `/v2/setup`, no
    `/v2/login`, no password field, and no cookie this harness did not receive from a real
    `Set-Cookie`."""
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    offenders = []
    for path in sorted((root / "evals").glob("*.py")) + [root / "harness" / "browser.py"]:
        # Code, never prose: several of these files narrate what the password's retirement took
        # with it, and a sweep that could not tell the two apart would forbid saying so.
        body = _code_only(path.read_text())
        for needle in ("/v2/setup", "/v2/login", "add_cookies", "FOUNDER_PASSWORD"):
            if needle in body:
                offenders.append(f"{path.name}: {needle}")
    assert not offenders, (
        "the login the eval walks must be the one keel-cloud has, with no bypass anywhere: "
        f"{offenders}")


def test_the_sign_in_step_clicks_a_link_and_then_the_founders_own_name():
    """The shape §10.4 asks for, asserted where a browser is not available.

    **The design's own locator is wrong and this is the correction.** §10.4 writes
    `get_by_role("button", name="Continue with Google")`; keel-web's `GoogleSignInButton` renders
    an `<a class="btn google" href="/v2/auth/google/start?...">` -- a navigation, not a fetch --
    whose accessible role is **link**. A button locator would match nothing on the real screen."""
    import inspect

    from harness.browser import Auth

    source = inspect.getsource(Auth.sign_in)
    assert 'get_by_role("link", name=self.GOOGLE_BUTTON)' in source
    assert "chooser_button_selector(founder.id)" in source, (
        "the picker's own submit button, found through the hidden `identity` field its form "
        "carries (§10.2) -- unique by construction, where the visible name is not")
    assert Auth.GOOGLE_BUTTON == "Continue with Google"
    assert not hasattr(Auth, "set_up"), "`set_up` is deleted with /setup (§4.7)"


def test_the_picker_button_the_scenarios_click_is_the_one_the_stub_draws():
    """The one place the harness's two halves could drift apart silently: the label
    `Auth.sign_in` asks Playwright for is the label `picker_html` writes."""
    from stack import oidc

    markup = picker_html(oidc.STUB_IDENTITIES, {"state": "s", "nonce": "n"})
    for identity in oidc.STUB_IDENTITIES:
        assert f"<button type=\"submit\">{identity.name}</button>" in markup
    assert "Eval Founder" in markup and "Nour Haddad" in markup


def test_a_stub_break_survives_the_picker_so_the_click_is_the_ordinary_click():
    """S-011 re-issues the same authorize request with one thing declared broken and then takes
    the ordinary click (`Auth.sign_in(stub_break=...)`). That only works because the stub carries
    `stub_break` back through the picker's hidden fields."""
    from stack import oidc as oidc_module

    markup = picker_html(oidc_module.STUB_IDENTITIES,
                         {"state": "s", "nonce": "n", "stub_break": "sig"})
    assert 'name="stub_break" value="sig"' in markup
    from stack.stub_oidc.server import _CARRIED
    assert "stub_break" in _CARRIED


def test_the_two_founders_are_the_two_stack_auth_names_them():
    from stack import auth, oidc

    assert (auth.FOUNDER_ONE.sub, auth.FOUNDER_ONE.name) == (oidc.FOUNDER_A.sub,
                                                             oidc.FOUNDER_A.name)
    assert (auth.FOUNDER_TWO.sub, auth.FOUNDER_TWO.name) == (oidc.FOUNDER_B.sub,
                                                             oidc.FOUNDER_B.name)
    assert auth.FOUNDER_ONE.name == "Eval Founder"
    assert auth.FOUNDER_TWO.name == "Nour Haddad"
    assert auth.FOUNDER_ONE.id == "founder-a" and auth.FOUNDER_TWO.id == "founder-b"


def test_the_browserless_session_walks_start_authorize_callback_and_nothing_else():
    """§10.8's "no shortcut around the callback", read off the one function that could take one.
    It must reach `/v2/auth/google/start`, must add the identity to *keel-cloud's own* authorize
    URL rather than building one, and must never touch a token endpoint or a cookie directly."""
    import inspect

    from stack import auth

    source = inspect.getsource(auth.sign_in_session)
    assert "/v2/auth/google/start" in source
    assert "identity={founder.id}" in source
    assert "/token" not in source and "cookies.set" not in source
    assert "allow_redirects=False" in source, (
        "the authorize URL has to be read off keel-cloud's own Location header, or the identity "
        "cannot be supplied on the request keel-cloud actually built")
