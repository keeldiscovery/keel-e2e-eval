"""Spec 095 -- S-003 and S-010 on the remote profile.

FR-2: a sign-in whose final URL is under the issuer's base is a refusal. On the remote profile the stub is served under
keel-web's own origin (`<web>/oidc`), so M6's 403 -- *'harness' may not sign in as 'founder-a'*
(`stack/stub_oidc/server.py`) -- starts with the web base and carries no `/login`, and the old predicate read it as
signed in. Held twice: on the predicate with the 403 page's URL, and in Chromium against a stand-in shaped as staging
(keel-web and the stub on one origin, the stub's own `picker_html`), where `Auth.sign_in` and `sign_in_with_code` raise
with the page's one line and the step records `ok: false`.

FR-1: S-003 signs in as `remote.identity_to_sign_in_as(stack, <label>, fallback=founder_one)`; S-010 as two distinct
registered identities on the remote profile and the built-ins elsewhere (read statically, as
`test_scenarios_use_the_stack_addresses.py` reads the matrix's scenarios).
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
from playwright.sync_api import sync_playwright

from harness import browser as hb
from harness.steps import Recorder
from stack import auth as auth_module
from stack import oidc, remote
from stack.config import REMOTE_PROFILE, REMOTE_WEB_URL_VAR, load_config
from stack.stub_oidc.server import Identity, picker_html

REPO = Path(__file__).resolve().parent.parent
WEB = "https://eval.keeldiscovery.com"
ISSUER = f"{WEB}/oidc"
M6_LINE = "'harness' may not sign in as 'founder-a'"
CELL = Identity(id="local-20261031T060000-ab12", sub="cell-local-20261031T060000-ab12",
                email="local-20261031T060000-ab12@keel-e2e-eval.test", name="Eval 1031 local")
PARAMS = {"client_id": "keel-web", "redirect_uri": f"{WEB}/v2/auth/google/callback", "response_type": "code",
          "scope": "openid email profile", "state": "s", "nonce": "n", "code_challenge": "c",
          "code_challenge_method": "S256"}
PICKER_URL = f"{ISSUER}/authorize?{urlencode(PARAMS)}"
REFUSED_URL = f"{ISSUER}/authorize?{urlencode({**PARAMS, 'identity': 'founder-a'})}"


def _remote_config():
    return load_config(validate=False, profile=REMOTE_PROFILE, env={REMOTE_WEB_URL_VAR: WEB})


# ------------------------------------------------------------------------------------------- FR-2: the predicate

def test_the_403_pages_url_is_not_a_sign_in():
    config = _remote_config()
    issuer = config.oidc_base_url
    assert issuer == ISSUER
    # The old predicate (URL under the web base, no `/login`) read the 403 page as signed in.
    assert REFUSED_URL.startswith(WEB) and "/login" not in REFUSED_URL
    assert hb.under_issuer(REFUSED_URL, issuer)
    assert not hb.signed_in_at(REFUSED_URL, WEB, issuer)
    assert hb.refused_at_issuer(REFUSED_URL, issuer, PICKER_URL)


def test_keel_webs_own_pages_are_still_a_sign_in():
    issuer = _remote_config().oidc_base_url
    for url in (f"{WEB}/", f"{WEB}/p/abc", f"{WEB}/connect?user_code=ABCD-EFGH", f"{WEB}/oidcish"):
        assert hb.signed_in_at(url, WEB, issuer), url
        assert not hb.refused_at_issuer(url, issuer, PICKER_URL), url
    assert not hb.signed_in_at(f"{WEB}/login?auth_error=cancelled", WEB, issuer)


def test_the_picker_itself_is_not_a_refusal_yet():
    # The click has not landed: the URL the picker was served at is the issuer's, and is waited past.
    assert not hb.refused_at_issuer(PICKER_URL, ISSUER, PICKER_URL)
    assert not hb.signed_in_at(PICKER_URL, WEB, ISSUER)


def test_the_issuer_base_read_off_the_picker_is_the_profiles():
    remote_config = _remote_config()
    assert hb.issuer_base_of(PICKER_URL) == remote_config.oidc_base_url
    local = load_config(validate=False)
    local_picker = f"{local.oidc_base_url}/authorize?{urlencode(PARAMS)}"
    assert hb.issuer_base_of(local_picker) == local.oidc_base_url
    # Local profiles: the issuer is its own origin, so keel-web's pages are never under it.
    assert hb.signed_in_at(f"{local.web_base_url}/", local.web_base_url, local.oidc_base_url)
    assert hb.refused_at_issuer(f"{local.oidc_base_url}/authorize?identity=x", local.oidc_base_url, local_picker)


def test_under_issuer_is_a_path_prefix_not_a_string_prefix():
    assert hb.under_issuer(ISSUER, ISSUER)
    assert hb.under_issuer(f"{ISSUER}?x=1", ISSUER)
    assert not hb.under_issuer(f"{WEB}/oidcish/authorize", ISSUER)
    assert not hb.under_issuer(f"{WEB}/", "")


def test_the_refusal_names_the_line_and_the_place():
    exc = hb.SignInRefused(M6_LINE, REFUSED_URL, "founder-a")
    assert isinstance(exc, AssertionError)
    assert exc.line == M6_LINE and exc.url == REFUSED_URL
    assert M6_LINE in str(exc) and "founder-a" in str(exc)


# ------------------------------------------------------------------------- FR-2: the walk, in Chromium, staging-shaped

def _login_html(door_word: str) -> str:
    return ("<!doctype html><html><body><div class='card'><h1 class='auth-title'>Log in</h1>"
            f"<a class='btn google' href='{PICKER_URL}'>{door_word}</a></div></body></html>")


def _stand_in(route, request):
    """keel-web and the stub on one origin, as on staging: `/login` with the door's link, the stub's own picker at
    `<web>/oidc/authorize`, M6's plain-text 403 for the built-in founder, a 302 home for the registered cell."""
    url = urlsplit(request.url)
    query = {k: v[0] for k, v in parse_qs(url.query).items()}
    if url.path == "/login":
        word = "Continue with Google" if "user_code" in query else "Log in with Google"
        route.fulfill(status=200, content_type="text/html", body=_login_html(word))
    elif url.path == "/oidc/authorize" and "identity" not in query:
        carried = {k: v for k, v in query.items() if k in PARAMS}
        route.fulfill(status=200, content_type="text/html",
                      body=picker_html([CELL, oidc.FOUNDER_A], carried, authorize_url=f"{ISSUER}/authorize"))
    elif url.path == "/oidc/authorize" and query["identity"] == oidc.FOUNDER_A.id:
        route.fulfill(status=403, content_type="text/plain; charset=utf-8", body=M6_LINE)
    elif url.path == "/oidc/authorize":
        route.fulfill(status=302, headers={"Location": f"{WEB}/"}, body="")
    else:
        route.fulfill(status=200, content_type="text/html",
                      body="<!doctype html><html><body><p class='hello'>Hello, Eval</p></body></html>")


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    context.route(f"{WEB}/**", _stand_in)
    page = context.new_page()
    yield page
    context.close()


def _steps(run_dir: Path) -> list[dict]:
    return [json.loads(line) for line in (run_dir / "transcript.jsonl").read_text().splitlines() if line.strip()]


def test_sign_in_as_the_built_in_founder_on_the_twin_raises_with_the_403s_line(page, tmp_path):
    with pytest.raises(hb.SignInRefused) as refused:
        hb.Auth(page, Recorder(tmp_path), WEB).sign_in(auth_module.FOUNDER_ONE)
    assert refused.value.line == M6_LINE
    assert refused.value.url.startswith(f"{ISSUER}/authorize?") and "identity=founder-a" in refused.value.url
    step = _steps(tmp_path)[-1]
    assert step["name"] == "founder signs in with Google"
    assert step["ok"] is False and M6_LINE in (step["error"] or "")


def test_sign_in_with_code_on_the_twin_raises_too(page, tmp_path):
    with pytest.raises(hb.SignInRefused) as refused:
        hb.Auth(page, Recorder(tmp_path), WEB).sign_in_with_code(auth_module.FOUNDER_ONE, "ABCD-EFGH")
    assert refused.value.line == M6_LINE
    assert _steps(tmp_path)[-1]["ok"] is False


def test_a_refusal_on_the_login_expectation_is_raised_not_waited_out(page, tmp_path):
    with pytest.raises(hb.SignInRefused):
        hb.Auth(page, Recorder(tmp_path), WEB).sign_in(auth_module.FOUNDER_ONE, expect="login")


def test_the_registered_cell_signs_in_and_lands_on_keel_web(page, tmp_path):
    cell = auth_module.StubFounder.of(CELL)
    result = hb.Auth(page, Recorder(tmp_path), WEB).sign_in(cell)
    assert result["landed"] == f"{WEB}/"
    assert _steps(tmp_path)[-1]["ok"] is True


# ---------------------------------------------------------------------------------- FR-1: who S-003 and S-010 are

def _calls(module: Path, dotted: str) -> list[ast.Call]:
    tree = ast.parse(module.read_text(encoding="utf-8"))
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and ast.unparse(n.func) == dotted]


def test_s003_signs_in_as_the_identity_remote_hands_it():
    module = REPO / "evals" / "test_s003_every_door.py"
    calls = _calls(module, "remote.identity_to_sign_in_as")
    assert len(calls) == 1
    assert ast.unparse(calls[0].args[0]) == "stack"
    assert {k.arg: ast.unparse(k.value) for k in calls[0].keywords}.get("fallback") == "founder_one"


def test_s010_signs_in_as_two_distinct_registered_identities_on_remote():
    module = REPO / "evals" / "test_s010_two_founders.py"
    calls = _calls(module, "remote.identity_to_sign_in_as")
    assert len(calls) == 2
    fallbacks = sorted({k.arg: ast.unparse(k.value) for k in c.keywords}.get("fallback") for c in calls)
    assert fallbacks == ["founder_one", "founder_two"]
    labels = {ast.unparse(c.args[1]) for c in calls}
    assert len(labels) == 2, "two founders, two labels"


def test_s010_two_founders_are_two_people_on_the_twin(monkeypatch):
    """The names S-010 registers are distinct in the first word (the greeting's word, the participant page's), as the
    built-ins' are -- the scenario's `name.split()[0] in greeting` holds nothing if both founders are *Eval ...*."""
    from evals import test_s010_two_founders as s010
    first = s010.founder_name(auth_module.FOUNDER_ONE)
    second = s010.founder_name(auth_module.FOUNDER_TWO)
    assert first.split()[0] != second.split()[0]
    assert first not in second and second not in first


def test_identity_to_sign_in_as_is_the_built_in_off_remote():
    local = load_config(validate=False)
    assert remote.identity_to_sign_in_as(local, "a", fallback=auth_module.FOUNDER_TWO) is auth_module.FOUNDER_TWO
