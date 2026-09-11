"""Stackless: the `remote` profile -- three URLs, no processes, and the gate credential that
rides two requests (spec 017; keel-cloud `canon/designs/e2e-matrix-design.md` §5.3, §11).

**Every test here has a local twin.** The invariant this spec is written around is §11's *"the
referee is not modified to accommodate a deployment"*, and the only way to hold it is to assert
the eval and playground profiles' own answers beside the remote one, in the same file, from the
same functions. Where a test below reads `remote`, the test beside it reads `eval` and expects
what `eval` expected before this spec existed.

Nothing here opens a socket: the three URL checks, the registry calls and the browserless
sign-in are all asked of a fake, because what is being measured is *which request this harness
makes*, not whether a staging box in Virginia is up.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from harness import browser as browser_module
from stack import auth as auth_module
from stack import lifecycle, oidc, remote, runtime as stack_runtime
from stack.config import (PROFILES, REMOTE_CELL_VAR, REMOTE_CLOUD_URL_VAR,
                          REMOTE_GATE_PASSWORD_VAR, REMOTE_GATE_USER_VAR, REMOTE_OIDC_URL_VAR,
                          REMOTE_PROFILE, REMOTE_WEB_URL_VAR, ConfigError, StackConfig,
                          load_config, remote_gate, remote_urls)

WEB = "https://eval.keeldiscovery.com"


def _config(**env) -> StackConfig:
    """A remote config from an environment dict and nothing else -- `validate=False` because the
    sibling checkouts have nothing to do with which URL a profile names."""
    return load_config(validate=False, profile=REMOTE_PROFILE, env={REMOTE_WEB_URL_VAR: WEB,
                                                                    **env})


@pytest.fixture
def eval_config() -> StackConfig:
    return load_config(validate=False)


# ------------------------------------------------------------------------- the profile, parsed

def test_remote_is_the_third_profile_and_the_first_two_are_where_they_were():
    assert PROFILES == ("eval", "playground", "remote")
    assert REMOTE_PROFILE == "remote"


def test_an_unknown_profile_is_still_a_config_error(tmp_path):
    with pytest.raises(ConfigError):
        load_config(tmp_path / "absent.toml", validate=False, profile="staging")


def test_the_two_companion_urls_default_from_the_web_one():
    """One Caddy serves all three on the staging twin: keel-web at the root, keel-cloud's `/v2/*`
    behind the same origin, and the stub at `/oidc` (§3)."""
    config = _config()
    assert config.web_base_url == WEB
    assert config.cloud_base_url == WEB
    assert config.oidc_base_url == f"{WEB}/oidc"


def test_a_deployment_that_splits_them_names_them():
    config = _config(**{REMOTE_CLOUD_URL_VAR: "https://api.example.test",
                        REMOTE_OIDC_URL_VAR: "https://issuer.example.test/oidc"})
    assert config.cloud_base_url == "https://api.example.test"
    assert config.oidc_base_url == "https://issuer.example.test/oidc"
    assert config.web_base_url == WEB


def test_trailing_slashes_are_taken_off_every_one_of_them():
    """`f"{base}/v2/me"` is how every URL in this harness is built; a base with a trailing slash
    would produce `//v2/me`, which some servers answer and some do not."""
    config = _config(**{REMOTE_WEB_URL_VAR: f"{WEB}/",
                        REMOTE_CLOUD_URL_VAR: "https://api.example.test/"})
    assert config.web_base_url == WEB
    assert config.cloud_base_url == "https://api.example.test"
    assert config.oidc_base_url == f"{WEB}/oidc"


def test_a_missing_web_url_names_the_variable_that_is_missing():
    with pytest.raises(ConfigError) as exc:
        load_config(validate=False, profile=REMOTE_PROFILE, env={})
    assert REMOTE_WEB_URL_VAR in str(exc.value)
    assert REMOTE_OIDC_URL_VAR in str(exc.value)


def test_remote_urls_reads_the_environment_it_is_handed():
    assert remote_urls({REMOTE_WEB_URL_VAR: WEB}) == {
        "web": WEB, "cloud": WEB, "oidc": f"{WEB}/oidc"}


def test_the_ports_a_remote_config_carries_are_the_ones_its_urls_name():
    """There is no local port on this profile; these exist so a printed `StackConfig` says
    something true."""
    config = _config(**{REMOTE_CLOUD_URL_VAR: "http://localhost:18080"})
    assert (config.web_port, config.cloud_port) == (443, 18080)
    assert config.postgres_port == 0


# --------------------------------------------------------------------------- the two local ones

def test_the_eval_profile_names_exactly_what_it_named_before(eval_config):
    assert eval_config.web_base_url == "http://localhost:5173"
    assert eval_config.cloud_base_url == "http://localhost:18080"
    assert eval_config.oidc_base_url == "http://localhost:18090"
    assert eval_config.is_remote is False
    assert eval_config.gate_credential is None


def test_the_playground_profile_too():
    config = load_config(validate=False, profile="playground")
    assert config.web_base_url == "http://localhost:5174"
    assert config.cloud_base_url == "http://localhost:18081"
    assert config.oidc_base_url == "http://localhost:18091"
    assert config.gate_credential is None


def test_the_local_profiles_ignore_the_remote_variables_entirely(monkeypatch):
    """A founder with `KEEL_REMOTE_WEB_URL` exported from an earlier staging run must not have
    their next `make eval` quietly point at staging."""
    monkeypatch.setenv(REMOTE_WEB_URL_VAR, WEB)
    monkeypatch.setenv(REMOTE_GATE_USER_VAR, "harness")
    monkeypatch.setenv(REMOTE_GATE_PASSWORD_VAR, "shh")
    config = load_config(validate=False)
    assert config.cloud_base_url == "http://localhost:18080"
    assert config.gate_credential is None


# --------------------------------------------------------------------------- the gate credential

def test_both_gate_variables_or_neither():
    assert remote_gate({}) is None
    assert remote_gate({REMOTE_GATE_USER_VAR: "harness",
                        REMOTE_GATE_PASSWORD_VAR: "secret"}) == ("harness", "secret")
    for half in ({REMOTE_GATE_USER_VAR: "harness"}, {REMOTE_GATE_PASSWORD_VAR: "secret"}):
        with pytest.raises(ConfigError):
            remote_gate(half)


def test_the_gate_credential_reaches_the_config():
    config = _config(**{REMOTE_GATE_USER_VAR: "harness", REMOTE_GATE_PASSWORD_VAR: "secret"})
    assert config.gate_credential == ("harness", "secret")
    assert remote.gate_auth(config) == ("harness", "secret")


def test_a_remote_run_against_a_deployment_with_no_gate_carries_none():
    assert _config().gate_credential is None


def test_playwright_gets_the_credential_scoped_to_the_issuers_origin():
    """**Scoped**, because keel-web's pages and keel-cloud's `/v2/*` are as open as production's
    and only `/oidc/authorize` is behind Caddy's basic auth (§4.2). A context that sent the
    password everywhere would hand it to whatever a redirect pointed at."""
    config = _config(**{REMOTE_GATE_USER_VAR: "harness", REMOTE_GATE_PASSWORD_VAR: "secret"})
    credentials = browser_module.gate_http_credentials(config)
    assert credentials == {"username": "harness", "password": "secret",
                           "origin": "https://eval.keeldiscovery.com"}


def test_no_gate_means_no_http_credentials_anywhere(eval_config):
    assert browser_module.gate_http_credentials(eval_config) is None
    assert browser_module.gate_http_credentials(_config()) is None
    assert browser_module.context_options(eval_config) == {}
    assert browser_module.context_options(eval_config, viewport=None) == {"viewport": None}


class _FakeBrowser:
    def __init__(self):
        self.calls = []
        self.closed = False

    def new_context(self, **kwargs):
        self.calls.append(kwargs)
        return f"context-{len(self.calls)}"

    def close(self):
        self.closed = True


def test_the_gated_browser_adds_the_credential_and_delegates_everything_else():
    config = _config(**{REMOTE_GATE_USER_VAR: "harness", REMOTE_GATE_PASSWORD_VAR: "secret"})
    fake = _FakeBrowser()
    wrapped = browser_module.GatedBrowser(fake, config)
    assert wrapped.new_context(viewport=None) == "context-1"
    assert fake.calls == [{"viewport": None,
                           "http_credentials": {"username": "harness", "password": "secret",
                                                "origin": "https://eval.keeldiscovery.com"}}]
    wrapped.close()
    assert fake.closed is True


def test_an_explicit_http_credentials_argument_wins(eval_config):
    fake = _FakeBrowser()
    config = _config(**{REMOTE_GATE_USER_VAR: "harness", REMOTE_GATE_PASSWORD_VAR: "secret"})
    browser_module.new_context(fake, config, http_credentials={"username": "somebody",
                                                               "password": "else"})
    assert fake.calls[0]["http_credentials"]["username"] == "somebody"


def test_the_conftest_fixture_only_wraps_when_there_is_a_gate():
    """Read as source, because the fixture itself needs a Playwright process. The two branches
    are the whole of the claim: a local session yields the raw `Browser` object."""
    from stack.config import REPO_ROOT

    source = (REPO_ROOT / "evals" / "conftest.py").read_text()
    assert "GatedBrowser(b, stack_config) if gate_http_credentials(stack_config) else b" in source


# ------------------------------------------------------------------ what the runtime is told

def test_the_runtime_home_is_this_profiles_own_and_names_the_remote_keel(tmp_path, monkeypatch):
    config = _config()
    assert stack_runtime.home_dir(config).name == "keel-home-remote"
    home = tmp_path / "keel-home"
    monkeypatch.setattr(stack_runtime, "home_dir", lambda _config: home)
    stack_runtime.reset(config)
    import json
    assert json.loads((home / "config.json").read_text())["base_url"] == WEB


def test_the_issuer_the_stub_lifecycle_names_is_the_remote_one(eval_config):
    assert oidc.issuer_url(_config()) == f"{WEB}/oidc"
    assert oidc.discovery_url(_config()) == f"{WEB}/oidc/.well-known/openid-configuration"
    # ... and the eval profile's is exactly what it was.
    assert oidc.issuer_url(eval_config) == "http://localhost:18090"


def test_the_environment_keel_cloud_would_be_pointed_at_it_with(eval_config):
    """Nobody points a *remote* keel-cloud at anything from here -- staging's `.env` does that --
    but `cloud_env` is the one place the issuer and the callback are composed, and a profile that
    composed a localhost callback for a remote cloud would be a profile that could not sign in."""
    env = oidc.cloud_env(_config())
    assert env["KEEL_OIDC_ISSUER"] == f"{WEB}/oidc"
    assert env["KEEL_GOOGLE_REDIRECT_URI"] == f"{WEB}/v2/auth/google/callback"
    assert oidc.cloud_env(eval_config)["KEEL_GOOGLE_REDIRECT_URI"] == \
        "http://localhost:18080/v2/auth/google/callback"


# -------------------------------------------------------------------------- the three questions

class _FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload

    @property
    def text(self):
        return str(self._payload)


def _answers(monkeypatch, **by_url):
    seen = []

    def fake_get(url, **kwargs):
        seen.append((url, kwargs))
        return by_url[url]

    monkeypatch.setattr(remote.requests, "get", fake_get)
    return seen


def _all_good(config):
    return {
        f"{config.web_base_url}/": _FakeResponse(200),
        f"{config.cloud_base_url}/v2/me": _FakeResponse(401),
        f"{config.oidc_base_url}/.well-known/openid-configuration":
            _FakeResponse(200, {"issuer": config.oidc_base_url}),
    }


def test_the_three_checks_are_web_200_cloud_401_and_a_discovery_document(monkeypatch):
    config = _config()
    seen = _answers(monkeypatch, **_all_good(config))
    assert [(what, ok) for what, ok, _ in remote.checks(config)] == [
        ("keel-web", True), ("keel-cloud", True), ("issuer", True)]
    assert [url for url, _ in seen] == [
        f"{WEB}/", f"{WEB}/v2/me", f"{WEB}/oidc/.well-known/openid-configuration"]
    # None of the three carries the gate credential: all three are open on staging by design,
    # and asking them anonymously also asks what a stranger sees (§9 S6).
    assert all(kwargs.get("auth") is None for _, kwargs in seen)


def test_a_cloud_that_answers_200_to_v2_me_is_a_failure(monkeypatch):
    """401 is the readiness gate, and a 200 would mean this harness is carrying somebody's
    session -- or that the URL names something that is not keel-cloud."""
    config = _config()
    answers = _all_good(config)
    answers[f"{config.cloud_base_url}/v2/me"] = _FakeResponse(200)
    _answers(monkeypatch, **answers)
    assert remote.is_up(config) is False
    with pytest.raises(remote.RemoteNotAnswering):
        remote.require_answering(config)


def test_a_discovery_document_that_names_a_different_issuer_is_a_failure(monkeypatch):
    config = _config()
    answers = _all_good(config)
    answers[f"{config.oidc_base_url}/.well-known/openid-configuration"] = _FakeResponse(
        200, {"issuer": "https://accounts.google.com"})
    _answers(monkeypatch, **answers)
    ok = dict((what, ok) for what, ok, _ in remote.checks(config))
    assert ok["issuer"] is False


def test_a_url_that_does_not_answer_at_all_reads_as_a_failure_naming_it(monkeypatch):
    config = _config()

    def fake_get(url, **kwargs):
        raise remote.requests.exceptions.ConnectionError("nope")

    monkeypatch.setattr(remote.requests, "get", fake_get)
    with pytest.raises(remote.RemoteNotAnswering) as exc:
        remote.require_answering(config)
    assert f"{WEB}/" in str(exc.value)


# ------------------------------------------------------------------------ boot, teardown, status

def test_boot_on_the_remote_profile_starts_nothing(monkeypatch):
    config = _config()
    started = []
    for module_name in ("postgres", "cloud", "web", "oidc"):
        module = getattr(lifecycle, module_name)
        monkeypatch.setattr(module, "up",
                            lambda _config, _n=module_name: started.append(_n))
    monkeypatch.setattr(lifecycle.remote, "require_answering", lambda _config: None)
    monkeypatch.setattr(lifecycle.runtime, "reset", lambda _config: None)
    lifecycle.boot(config)
    assert started == []


def test_teardown_on_the_remote_profile_stops_nothing_but_the_runtime(monkeypatch):
    """A referee that could tear down the deployment it is refereeing is a referee with a
    footgun -- and on staging that deployment has other cells running against it (§8)."""
    config = _config()
    stopped = []
    monkeypatch.setattr(lifecycle.postgres, "down", lambda _config: stopped.append("postgres"))
    monkeypatch.setattr(lifecycle, "teardown_all_processes",
                        lambda profile: stopped.append("processes"))
    monkeypatch.setattr(lifecycle.oidc, "clear_key", lambda _config: stopped.append("key"))
    monkeypatch.setattr(lifecycle.runtime, "disconnect",
                        lambda _config: {"outcome": "not_running", "via": "bundled"})
    lifecycle.teardown(config)
    assert stopped == []


def test_status_on_the_remote_profile_is_the_three_questions(monkeypatch):
    config = _config()
    asked = []
    monkeypatch.setattr(lifecycle.remote, "is_up",
                        lambda _config: asked.append("remote") or True)
    monkeypatch.setattr(lifecycle.oidc, "is_up",
                        lambda _config: asked.append("oidc") or True)
    assert lifecycle.quick_gates_pass(config) is True
    assert asked == ["remote"]


def test_the_local_profiles_still_boot_all_four_processes(monkeypatch, eval_config):
    started = []
    for module_name in ("oidc", "postgres", "cloud", "web"):
        module = getattr(lifecycle, module_name)
        monkeypatch.setattr(module, "up", lambda _config, _n=module_name: started.append(_n))
    monkeypatch.setattr(lifecycle.runtime, "require_bundled_runtime", lambda _config: None)
    monkeypatch.setattr(lifecycle.runtime, "bundled_runtime_version", lambda _config: "test")
    monkeypatch.setattr(lifecycle.runtime, "reset", lambda _config: None)
    lifecycle.boot(eval_config)
    assert started == ["oidc", "postgres", "cloud", "web"]


# ------------------------------------------------------------------------- the registry helpers

class _Recorder:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def __call__(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def test_register_cell_identity_posts_with_the_gate_credential_and_returns_a_founder(monkeypatch):
    config = _config(**{REMOTE_GATE_USER_VAR: "harness", REMOTE_GATE_PASSWORD_VAR: "secret"})
    post = _Recorder(_FakeResponse(201, {"id": "ubuntu-1", "sub": "cell-ubuntu-1",
                                          "email": "ubuntu-1@keel-e2e-eval.test",
                                          "name": "Eval 0911 ubuntu"}))
    monkeypatch.setattr(remote.requests, "post", post)
    founder = remote.register_cell_identity(config, "2026-09-11 - running", id="ubuntu-1")
    url, kwargs = post.calls[0]
    assert url == f"{WEB}/oidc/identities"
    assert kwargs["auth"] == ("harness", "secret")
    assert kwargs["json"]["id"] == "ubuntu-1"
    assert kwargs["json"]["label"] == "2026-09-11 - running"
    assert "sub" not in kwargs["json"], "the sub is derived by the issuer, never sent (§4.3)"
    # What comes back is what a scenario signs in as, with no translation step in between.
    assert (founder.id, founder.sub, founder.name) == (
        "ubuntu-1", "cell-ubuntu-1", "Eval 0911 ubuntu")


def test_a_refused_registration_says_the_status_and_the_body(monkeypatch):
    config = _config()
    monkeypatch.setattr(remote.requests, "post",
                        _Recorder(_FakeResponse(409, {"error": "taken"})))
    with pytest.raises(remote.RegistryRefused) as exc:
        remote.register_cell_identity(config, "label", id="cell-1")
    assert exc.value.status == 409
    assert "taken" in str(exc.value)


def test_label_cell_identity_patches_the_label_and_nothing_else(monkeypatch):
    config = _config(**{REMOTE_GATE_USER_VAR: "harness", REMOTE_GATE_PASSWORD_VAR: "secret"})
    patch = _Recorder(_FakeResponse(200, {"id": "ubuntu-1", "label": "PASSED 5.0 (S-001)"}))
    monkeypatch.setattr(remote.requests, "patch", patch)
    body = remote.label_cell_identity(config, "ubuntu-1", "PASSED 5.0 (S-001)")
    url, kwargs = patch.calls[0]
    assert url == f"{WEB}/oidc/identities/ubuntu-1"
    assert kwargs["json"] == {"label": "PASSED 5.0 (S-001)"}
    assert kwargs["auth"] == ("harness", "secret")
    assert body["label"] == "PASSED 5.0 (S-001)"


def test_a_refused_label_is_raised_rather_than_swallowed(monkeypatch):
    config = _config()
    monkeypatch.setattr(remote.requests, "patch", _Recorder(_FakeResponse(404, {})))
    with pytest.raises(remote.RegistryRefused):
        remote.label_cell_identity(config, "nobody", "x")


def test_a_scenario_asks_once_and_gets_the_built_in_founder_off_remote(monkeypatch, eval_config):
    """**The one call a scenario makes.** On eval and playground it is *Eval Founder* and no HTTP
    happens at all, which is how one scenario runs on three profiles."""
    def explode(*args, **kwargs):  # pragma: no cover - the point is that it is never called
        raise AssertionError("a local profile must not talk to a registry")

    monkeypatch.setattr(remote.requests, "post", explode)
    assert remote.identity_to_sign_in_as(eval_config, "a label") is auth_module.FOUNDER_ONE


def test_on_remote_the_same_call_registers_this_cells_own_founder(monkeypatch):
    config = _config()
    monkeypatch.setattr(remote.requests, "post",
                        _Recorder(_FakeResponse(201, {"id": "c", "sub": "cell-c",
                                                       "email": "c@e.test", "name": "Cell"})))
    founder = remote.identity_to_sign_in_as(config, "2026-09-11 - running")
    assert founder.name == "Cell"


def test_the_identity_a_cell_registers_is_named_for_the_cell_and_never_repeats(monkeypatch):
    monkeypatch.setenv(REMOTE_CELL_VAR, "windows-copilot-py3.9")
    assert remote.cell_name() == "windows-copilot-py3.9"
    first = remote.new_identity_id()
    assert first.startswith("windows-copilot-py3.9-")
    assert first != remote.new_identity_id(), (
        "two runs of one cell in the same second are two founders, or the second inherits the "
        "first's project and proves nothing (§8: cells never delete)")
    monkeypatch.delenv(REMOTE_CELL_VAR)
    assert remote.cell_name() == "local"


# ------------------------------------------------------- the browserless sign-in, gate and all

class _FakeSession:
    """Enough of `requests.Session` for `stack/auth.py`'s three hops."""

    def __init__(self):
        self.cookies = {}
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if "/v2/auth/google/start" in url:
            response = _FakeResponse(302)
            response.headers = {"Location": f"{WEB}/oidc/authorize?state=s&nonce=n"}
            return response
        landed = _FakeResponse(200)
        landed.url = f"{WEB}/"
        return landed


def _fake_session_factory(monkeypatch, module):
    created = []

    def factory():
        session = _FakeSession()
        created.append(session)
        return session

    monkeypatch.setattr(module.requests, "Session", factory)
    return created


def test_the_browserless_sign_in_sends_the_gate_on_the_authorize_hop_and_no_other(monkeypatch):
    """Caddy stands in front of `/oidc/authorize` only, so this is the only request in the whole
    harness that carries the credential besides the browser context's own (§4.2)."""
    config = _config(**{REMOTE_GATE_USER_VAR: "harness", REMOTE_GATE_PASSWORD_VAR: "secret"})
    created = _fake_session_factory(monkeypatch, auth_module)
    auth_module.sign_in_session(config, auth_module.FOUNDER_ONE)
    calls = created[0].calls
    start_url, start_kwargs = calls[0]
    authorize_url, authorize_kwargs = calls[1]
    assert "/v2/auth/google/start" in start_url
    assert start_kwargs.get("auth") is None
    assert authorize_url.startswith(f"{WEB}/oidc/authorize")
    assert authorize_kwargs["auth"] == ("harness", "secret")


class _LocalSession(_FakeSession):
    """The eval profile's own three hops: keel-cloud on 18080 redirecting to the stub on
    18090."""

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if "/v2/auth/google/start" in url:
            response = _FakeResponse(302)
            response.headers = {"Location": "http://localhost:18090/authorize?state=s&nonce=n"}
            return response
        landed = _FakeResponse(200)
        landed.url = "http://localhost:5173/"
        return landed


def test_the_local_profiles_browserless_sign_in_carries_no_auth_at_all(monkeypatch, eval_config):
    created = []
    monkeypatch.setattr(auth_module.requests, "Session",
                        lambda: created.append(_LocalSession()) or created[-1])
    auth_module.sign_in_session(eval_config, auth_module.FOUNDER_ONE)
    assert [url for url, _ in created[0].calls] == [
        "http://localhost:18080/v2/auth/google/start",
        "http://localhost:18090/authorize?state=s&nonce=n&identity=founder-a"]
    assert all(kwargs.get("auth") is None for _, kwargs in created[0].calls)


def test_a_config_built_by_hand_before_this_spec_still_constructs(eval_config):
    """Every new field is defaulted and last: `replace(config, profile="playground")` is what
    half this repository's own tests do."""
    playground = replace(eval_config, profile="playground", cloud_port=18081)
    assert playground.cloud_base_url == "http://localhost:18081"
    assert playground.gate_credential is None
    assert playground.is_remote is False


# ------------------------------------------------------- the private siblings, absent on a runner

def test_remote_loads_without_keel_cloud_or_keel_web_beside_it(tmp_path, monkeypatch):
    """A GitHub runner has the two public siblings checked out and the two private ones absent
    (spec 020); the remote profile starts neither, so it must not demand them."""
    from stack import config as cfgmod
    (tmp_path / "keel-runtime").mkdir()
    (tmp_path / "keel-connect-skill").mkdir()
    toml = tmp_path / "stack.toml"
    toml.write_text(
        "[paths]\n"
        f'keel_cloud = "{tmp_path / "keel-cloud"}"\n'
        f'keel_web = "{tmp_path / "keel-web"}"\n'
        f'keel_runtime = "{tmp_path / "keel-runtime"}"\n'
        f'keel_connect_skill = "{tmp_path / "keel-connect-skill"}"\n'
    )
    env = {"KEEL_REMOTE_WEB_URL": "https://eval.example.test"}
    cfg = cfgmod.load_config(toml, profile="remote", env=env)
    assert cfg.is_remote and cfg.keel_connect_skill == tmp_path / "keel-connect-skill"
    # and the two the referee runs itself are still required
    (tmp_path / "keel-connect-skill").rmdir()
    import pytest as _pytest
    with _pytest.raises(cfgmod.ConfigError):
        cfgmod.load_config(toml, profile="remote", env=env)
    # the local profile still demands all four
    (tmp_path / "keel-connect-skill").mkdir()
    with _pytest.raises(cfgmod.ConfigError):
        cfgmod.load_config(toml, profile="eval")


# ------------------------------------------------------------- the referee is never a visitor

def test_every_referee_context_carries_goatcounters_opt_out():
    from harness.browser import RefereeBrowser, SKIP_GOATCOUNTER_INIT, GatedBrowser
    assert GatedBrowser is RefereeBrowser
    assert "skipgc" in SKIP_GOATCOUNTER_INIT and "'t'" in SKIP_GOATCOUNTER_INIT

    class FakeContext:
        def __init__(self): self.scripts = []
        def add_init_script(self, script): self.scripts.append(script)

    class FakeBrowser:
        def __init__(self): self.kwargs = None
        def new_context(self, **kwargs):
            self.kwargs = kwargs; return FakeContext()

    from stack import config as cfgmod
    cfg = cfgmod.load_config(profile="eval", validate=False)
    fake = FakeBrowser()
    ctx = RefereeBrowser(fake, cfg).new_context()
    assert ctx.scripts == [SKIP_GOATCOUNTER_INIT]
    assert fake.kwargs == {}  # no gate on the eval profile: the caller's own options, untouched
