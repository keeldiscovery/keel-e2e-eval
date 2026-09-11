"""Stackless: the gate and the registry the staging twin puts in front of, and behind, the stub
issuer (spec 018; keel-cloud `canon/designs/e2e-matrix-design.md` §4).

Same shape as `tests/test_stub_oidc.py` -- a real server on a real ephemeral socket, every
question asked over HTTP -- because the rules here are rules about *requests*: a header Caddy
sets, a status a stranger gets, an order a picker renders in. Asserting them against the objects
would prove the objects.

**Two servers, and the pairing is the point.** `ungated` is the eval and playground profiles,
unchanged: no `--gated`, an in-memory registry nobody writes to, and a picker that is the two
built-in founders and nothing else. `gated` is staging: `--gated`, a registry file, and the two
gate users Caddy's `basic_auth` block knows. Every gated rule below has an ungated twin somewhere
in this file, because invariant §11 is that **the referee is not modified to accommodate a
deployment** and the cheapest proof of that is the local behaviour being asserted beside the
remote one.
"""

from __future__ import annotations

import json
import secrets
import threading

import pytest
import requests

from stack.stub_oidc import keys as keymod
from stack.stub_oidc.identity import STUB_IDENTITIES
from stack.stub_oidc.registry import SUB_PREFIX, Entry, Registry, RegistryError
from stack.stub_oidc.server import (FOUNDER_GATE_USER, GATE_HEADER, HARNESS_GATE_USER,
                                     Identity, make_server, picker_html, pkce_challenge)

CLIENT_ID = "test-client"
CLIENT_SECRET = "test-client-secret"  # noqa: S105 - a stub's own fixture, never a real secret
REDIRECT_URI = "http://localhost:18080/v2/auth/google/callback"

BUILTINS = [
    Identity(id="founder-a", sub="stub-founder-1", email="a@keel-e2e-eval.test",
             name="Eval Founder"),
    Identity(id="founder-b", sub="stub-founder-2", email="b@keel-e2e-eval.test",
             name="Nour Haddad"),
]


# --------------------------------------------------------------------------------- the fixtures

@pytest.fixture(scope="module")
def rsa_key(tmp_path_factory):
    return keymod.load_or_generate(tmp_path_factory.mktemp("oidc") / "key.pem")


def _serve(key, **kwargs):
    httpd = make_server(port=0, key=key, client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                        identities=BUILTINS, **kwargs)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, thread


@pytest.fixture
def ungated(rsa_key):
    """The local profiles: no gate, no registry file, nothing passed at all."""
    httpd, thread = _serve(rsa_key)
    yield httpd.stub.issuer
    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=5)


@pytest.fixture
def registry_path(tmp_path):
    return tmp_path / "identities.json"


@pytest.fixture
def gated(rsa_key, registry_path):
    """The staging twin: `--gated`, and a registry in a file on the box's own volume."""
    httpd, thread = _serve(rsa_key, gated=True, registry=Registry(registry_path))
    yield httpd.stub.issuer
    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=5)


def _gate(user: str | None) -> dict:
    return {GATE_HEADER: user} if user else {}


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
    }
    params.update(overrides)
    params = {k: v for k, v in params.items() if v is not None}
    params["_verifier"] = verifier
    return params


def _authorize(issuer, *, gate=None, **overrides) -> requests.Response:
    params = {k: v for k, v in _authorize_params(**overrides).items() if not k.startswith("_")}
    return requests.get(f"{issuer}/authorize", params=params, headers=_gate(gate),
                        allow_redirects=False, timeout=5)


def _register(issuer, *, gate=None, **body) -> requests.Response:
    payload = {"id": "cell-1", "name": "Eval 0911 ubuntu/claude/3.13",
               "email": "cell-1@keel-e2e-eval.test", "label": "2026-09-11 - running"}
    payload.update(body)
    payload = {k: v for k, v in payload.items() if v is not None}
    return requests.post(f"{issuer}/identities", json=payload, headers=_gate(gate), timeout=5)


def _claims_for(issuer, identity_id, *, gate=None) -> dict:
    """The whole walk, for one identity: authorize with the click supplied, redeem, and read the
    ID token's claims. What a cell's sign-in actually produces."""
    params = _authorize_params(identity=identity_id)
    query = {k: v for k, v in params.items() if not k.startswith("_")}
    response = requests.get(f"{issuer}/authorize", params=query, headers=_gate(gate),
                            allow_redirects=False, timeout=5)
    assert response.status_code == 302, response.text
    code = dict(pair.split("=", 1) for pair in
                requests.utils.urlparse(response.headers["Location"]).query.split("&"))["code"]
    token = requests.post(f"{issuer}/token", timeout=5, data={
        "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI,
        "code_verifier": params["_verifier"], "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET}).json()["id_token"]
    return json.loads(keymod.b64url_decode(token.split(".")[1]))


# ------------------------------------------------------- ungated: the local profiles, unchanged

def test_ungated_authorize_needs_no_gate_header_at_all(ungated):
    """The eval and playground profiles pass no `--gated` and send no header, and this is the
    same 200 they have always got."""
    assert _authorize(ungated, identity="founder-a").status_code == 302
    assert _authorize(ungated).status_code == 200


def test_an_ungated_picker_is_the_two_built_in_founders_and_nothing_else(ungated):
    page = _authorize(ungated).text
    assert "<h1>Choose an account</h1>" in page
    for identity in BUILTINS:
        assert f'<button type="submit">{identity.name}</button>' in page
    # No registry, so no labels: the page is byte-for-byte the page spec 015 drew.
    assert 'class="label"' not in page


def test_an_ungated_stub_still_registers_and_labels_with_no_header(ungated):
    """The registry exists on every profile; it is *empty* on the local ones because nothing
    writes to it, not because the routes are missing. A founder poking at the playground can use
    them, and the tests below do."""
    created = _register(ungated)
    assert created.status_code == 201, created.text
    patched = requests.patch(f"{ungated}/identities/cell-1", json={"label": "done"}, timeout=5)
    assert patched.status_code == 200
    assert patched.json()["label"] == "done"


def test_an_ungated_registry_is_in_memory_and_writes_no_file(tmp_path, ungated):
    _register(ungated)
    assert list(tmp_path.iterdir()) == []


# ----------------------------------------------------------------------------- the gate itself

def test_gated_authorize_without_the_header_is_a_plain_text_403(gated):
    response = _authorize(gated, identity="founder-a")
    assert response.status_code == 403
    assert response.headers["Content-Type"].startswith("text/plain")
    assert "gated" in response.text
    # Not a redirect to the client, not an HTML page, not a hint about who may pass: a stranger
    # who found the hostname learns only that this is not for them (§9 S6).
    assert "Location" not in response.headers
    assert "<" not in response.text


def test_gated_registry_routes_refuse_without_the_header_too(gated):
    assert requests.get(f"{gated}/identities", timeout=5).status_code == 403
    assert _register(gated).status_code == 403
    assert requests.patch(f"{gated}/identities/cell-1", json={"label": "x"},
                          timeout=5).status_code == 403


def test_the_gate_user_caddy_forwards_is_a_header_and_never_a_password(gated):
    """The stub has no password of its own and must never grow one: the gate is Caddy's
    `basic_auth` and all the stub learns is the user name it forwards (§4.2)."""
    response = _authorize(gated, gate=FOUNDER_GATE_USER)
    assert response.status_code == 200
    assert "password" not in response.text.lower().replace("has no password", "")


def test_founder_may_sign_in_as_any_identity_and_harness_may_not(gated):
    assert _register(gated, gate=HARNESS_GATE_USER).status_code == 201

    # The founder: every identity, built-in or registered (§4.4, and the founder's morning).
    for identity_id in ("founder-a", "founder-b", "cell-1"):
        assert _authorize(gated, gate=FOUNDER_GATE_USER,
                          identity=identity_id).status_code == 302, identity_id

    # The harness: only what it registered. **M6, the whole of it** -- a leaked harness password
    # never signs in as the founder's own identity.
    assert _authorize(gated, gate=HARNESS_GATE_USER, identity="cell-1").status_code == 302
    for identity_id in ("founder-a", "founder-b"):
        refused = _authorize(gated, gate=HARNESS_GATE_USER, identity=identity_id)
        assert refused.status_code == 403, identity_id
        assert "may not sign in as" in refused.text


def test_the_harness_may_not_sign_in_as_an_identity_the_founder_registered(gated):
    assert _register(gated, gate=FOUNDER_GATE_USER, id="founders-own").status_code == 201
    assert _authorize(gated, gate=HARNESS_GATE_USER, identity="founders-own").status_code == 403
    assert _authorize(gated, gate=FOUNDER_GATE_USER, identity="founders-own").status_code == 302


def test_an_unknown_gate_user_may_register_nothing(gated):
    """Caddy's block has two lines in it; anything else reaching this header is a
    misconfiguration, and a misconfiguration that could write to the registry would be one
    nobody noticed."""
    assert _register(gated, gate="somebody-else").status_code == 403
    assert requests.get(f"{gated}/identities", headers=_gate("somebody-else"),
                        timeout=5).status_code == 403


def test_the_harness_may_not_relabel_what_it_did_not_register(gated):
    assert _register(gated, gate=FOUNDER_GATE_USER, id="founders-own").status_code == 201
    refused = requests.patch(f"{gated}/identities/founders-own", json={"label": "mine now"},
                             headers=_gate(HARNESS_GATE_USER), timeout=5)
    assert refused.status_code == 403


# -------------------------------------------------------------------------------- the registry

def test_registering_derives_the_sub_and_never_takes_one(gated):
    created = _register(gated, gate=HARNESS_GATE_USER, sub="stub-founder-1")
    assert created.status_code == 201
    body = created.json()
    assert body["sub"] == f"{SUB_PREFIX}cell-1" == "cell-cell-1"
    assert body["registered_by"] == HARNESS_GATE_USER


def test_a_registered_identitys_token_is_verified_and_carries_no_hosted_domain(gated):
    assert _register(gated, gate=HARNESS_GATE_USER).status_code == 201
    claims = _claims_for(gated, "cell-1", gate=HARNESS_GATE_USER)
    assert claims["sub"] == "cell-cell-1"
    assert claims["email"] == "cell-1@keel-e2e-eval.test"
    assert claims["email_verified"] is True
    assert "hd" not in claims, (
        "a cell's founder has no hosted domain -- `hd` is Google's Workspace claim and the "
        "registry never sets it (§4.3)")


def test_a_duplicate_id_is_a_409_and_the_first_registration_stands(gated):
    assert _register(gated, gate=HARNESS_GATE_USER, label="first").status_code == 201
    again = _register(gated, gate=HARNESS_GATE_USER, label="second")
    assert again.status_code == 409
    listed = requests.get(f"{gated}/identities", headers=_gate(HARNESS_GATE_USER),
                          timeout=5).json()["identities"]
    assert [entry["label"] for entry in listed] == ["first"]


def test_a_built_in_identitys_id_cannot_be_taken_by_a_cell(gated):
    """A cell that registered `founder-a` would shadow the identity every local scenario signs in
    as, and `identity_for` would find the cell's one first."""
    assert _register(gated, gate=HARNESS_GATE_USER, id="founder-a").status_code == 409


def test_a_malformed_registration_is_a_400(gated):
    assert _register(gated, gate=HARNESS_GATE_USER, id="not a valid id").status_code == 400
    assert _register(gated, gate=HARNESS_GATE_USER, name="").status_code == 400
    assert _register(gated, gate=HARNESS_GATE_USER, email="").status_code == 400
    assert requests.post(f"{gated}/identities", data="not json",
                         headers=_gate(HARNESS_GATE_USER), timeout=5).status_code == 400


def test_patch_changes_the_label_and_only_the_label(gated):
    """§6.4: the verdict is written beside the founder the cell signed in as. Nothing else about
    that founder may move -- a run that could rename or re-`sub` itself could rewrite whose
    project it was."""
    _register(gated, gate=HARNESS_GATE_USER)
    patched = requests.patch(
        f"{gated}/identities/cell-1",
        json={"label": "PASSED 5.0 (S-001)", "name": "Somebody Else",
              "email": "elsewhere@example.com", "sub": "stub-founder-1"},
        headers=_gate(HARNESS_GATE_USER), timeout=5)
    assert patched.status_code == 200
    body = patched.json()
    assert body["label"] == "PASSED 5.0 (S-001)"
    assert body["name"] == "Eval 0911 ubuntu/claude/3.13"
    assert body["email"] == "cell-1@keel-e2e-eval.test"
    assert body["sub"] == "cell-cell-1"


def test_patching_an_unknown_identity_is_a_404(gated):
    response = requests.patch(f"{gated}/identities/nobody", json={"label": "x"},
                              headers=_gate(HARNESS_GATE_USER), timeout=5)
    assert response.status_code == 404


def test_patch_without_a_label_is_a_400(gated):
    _register(gated, gate=HARNESS_GATE_USER)
    assert requests.patch(f"{gated}/identities/cell-1", json={"name": "x"},
                          headers=_gate(HARNESS_GATE_USER), timeout=5).status_code == 400


def test_get_identities_is_newest_first(gated):
    for index in range(3):
        assert _register(gated, gate=HARNESS_GATE_USER, id=f"cell-{index}",
                         email=f"cell-{index}@keel-e2e-eval.test").status_code == 201
    listed = requests.get(f"{gated}/identities", headers=_gate(HARNESS_GATE_USER),
                          timeout=5).json()
    assert [entry["id"] for entry in listed["identities"]] == ["cell-2", "cell-1", "cell-0"]
    # The two built-ins are named separately: they are not registrations and nothing may patch
    # them.
    assert [entry["id"] for entry in listed["builtin"]] == ["founder-a", "founder-b"]


# ----------------------------------------------------------------------------- the picker again

def test_the_picker_lists_registered_cells_newest_first_then_the_built_ins(gated):
    for index in range(2):
        _register(gated, gate=HARNESS_GATE_USER, id=f"cell-{index}",
                  name=f"Eval cell {index}", email=f"cell-{index}@keel-e2e-eval.test",
                  label=f"verdict {index}")
    page = _authorize(gated, gate=FOUNDER_GATE_USER).text
    order = [page.index(f'<button type="submit">{name}</button>')
             for name in ("Eval cell 1", "Eval cell 0", "Eval Founder", "Nour Haddad")]
    assert order == sorted(order), (
        "the founder's morning is yesterday's cells at the top and the two fixtures at the "
        "bottom (§4.3)")


def test_a_registered_identitys_label_follows_its_button(gated):
    _register(gated, gate=HARNESS_GATE_USER, label="2026-09-11 - PASSED 5.0 (S-001)")
    page = _authorize(gated, gate=FOUNDER_GATE_USER).text
    button = '<button type="submit">Eval 0911 ubuntu/claude/3.13</button>'
    assert button in page
    assert page.index('<p class="label">2026-09-11 - PASSED 5.0 (S-001)</p>') > page.index(button)
    # The built-in founders have no label and grow no empty element.
    assert page.count('class="label"') == 1


def test_a_label_is_escaped_like_every_other_word_on_that_page(gated):
    _register(gated, gate=HARNESS_GATE_USER, label='<script>alert("x")</script>')
    page = _authorize(gated, gate=FOUNDER_GATE_USER).text
    assert "<script>alert" not in page
    assert "&lt;script&gt;" in page


def test_identity_and_login_hint_both_find_a_registered_cell(gated):
    _register(gated, gate=HARNESS_GATE_USER)
    for hint in ({"identity": "cell-1"}, {"login_hint": "cell-cell-1"},
                 {"identity": "cell-1@keel-e2e-eval.test"}):
        response = _authorize(gated, gate=HARNESS_GATE_USER, **hint)
        assert response.status_code == 302, (hint, response.text)


def test_picker_html_renders_a_label_only_when_there_is_one():
    """The function, directly -- the one place the two shapes sit side by side."""
    page = picker_html([Identity(id="x", sub="cell-x", email="x@e.test", name="X",
                                 label="a verdict"),
                        STUB_IDENTITIES[0]], {"state": "s"})
    assert '<p class="label">a verdict</p>' in page
    assert page.count('class="label"') == 1


# ------------------------------------------------------------------------------ the file itself

def test_the_registry_file_is_json_a_second_reader_can_load(gated, registry_path):
    _register(gated, gate=HARNESS_GATE_USER)
    raw = json.loads(registry_path.read_text())
    assert [entry["id"] for entry in raw["identities"]] == ["cell-1"]
    # A second Registry over the same path is the same list: this is what makes the container's
    # restart, and the founder's own `jq` over the volume, see what the cells wrote.
    assert [entry.identity.id for entry in Registry(registry_path).newest_first()] == ["cell-1"]


def test_writes_are_atomic_and_leave_no_temp_file_behind(tmp_path):
    """`os.replace` over a temp file **in the same directory** -- a reader on every `/authorize`
    must never see half a write (§4.3). The observable halves of that are: no partial document
    is ever at the path, and nothing is left lying beside it."""
    path = tmp_path / "identities.json"
    registry = Registry(path)
    for index in range(5):
        registry.register(id=f"cell-{index}", name=f"Cell {index}",
                          email=f"cell-{index}@keel-e2e-eval.test", registered_by="harness")
        json.loads(path.read_text())  # valid after every single write, not only at the end
    assert sorted(p.name for p in tmp_path.iterdir()) == ["identities.json"]


def test_a_registry_reads_a_file_written_by_a_previous_process(tmp_path):
    path = tmp_path / "identities.json"
    Registry(path).register(id="cell-1", name="Cell 1", email="c@e.test",
                            registered_by="harness")
    assert [e.identity.id for e in Registry(path).newest_first()] == ["cell-1"]


def test_a_truncated_registry_reads_as_empty_rather_than_as_a_dead_issuer(tmp_path):
    path = tmp_path / "identities.json"
    path.write_text("{not json at all")
    assert Registry(path).newest_first() == []


def test_the_registry_refuses_a_duplicate_and_a_bad_id_in_process(tmp_path):
    registry = Registry(tmp_path / "identities.json")
    registry.register(id="cell-1", name="Cell 1", email="c@e.test", registered_by="harness")
    with pytest.raises(RegistryError) as duplicate:
        registry.register(id="cell-1", name="Cell 1", email="c@e.test", registered_by="harness")
    assert duplicate.value.status == 409
    with pytest.raises(RegistryError) as malformed:
        registry.register(id="../escape", name="Cell", email="c@e.test", registered_by="harness")
    assert malformed.value.status == 400
    with pytest.raises(RegistryError) as missing:
        registry.relabel("nobody", "x")
    assert missing.value.status == 404


def test_an_entry_round_trips_through_json(tmp_path):
    entry = Entry.from_json({"id": "cell-1", "name": "Cell 1", "email": "c@e.test",
                             "label": "PASSED", "registered_by": "harness",
                             "registered_at": 1.0})
    assert entry.identity.sub == "cell-cell-1"
    assert Entry.from_json(entry.to_json()) == entry


# --------------------------------------------------------------- what the two flags default to

def test_a_stub_is_ungated_and_in_memory_unless_it_is_told_otherwise(rsa_key):
    """The default *is* the local profiles' configuration, which is why `stack/oidc.py` passes
    neither flag and why spec 015's own test file needed no edit."""
    httpd = make_server(port=0, key=rsa_key, client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                        identities=BUILTINS)
    try:
        assert httpd.stub.gated is False
        assert httpd.stub.registry.path is None
        assert httpd.stub.identities == BUILTINS
        assert httpd.stub.may_sign_in_as(None, BUILTINS[0]) is True
    finally:
        httpd.server_close()


def test_stack_oidc_spawns_the_stub_with_neither_flag():
    """The lifecycle module's own argv, read as text: a local `make up` must never gate itself
    or name a registry file, and a future edit that added one would break this."""
    from stack.config import REPO_ROOT

    source = (REPO_ROOT / "stack" / "oidc.py").read_text()
    assert "--gated" not in source
    assert "--registry" not in source


def test_a_refused_write_does_not_poison_the_keep_alive_connection(gated):
    """Found while writing this file, and worth a test of its own: this is HTTP/1.1, `requests`
    reuses one connection per `Session`, and a refusal that answered *without reading the body*
    left the body in the socket -- so the next request on that connection began parsing at
    `{"label":` and came back a garbled 400 from a route nobody had called. Every refusal reads
    the body first now."""
    session = requests.Session()
    refused = session.post(f"{gated}/identities", json={"id": "cell-9", "name": "Nine",
                                                        "email": "nine@e.test"}, timeout=5)
    assert refused.status_code == 403           # no gate header
    allowed = session.post(f"{gated}/identities", json={"id": "cell-9", "name": "Nine",
                                                        "email": "nine@e.test"},
                           headers=_gate(HARNESS_GATE_USER), timeout=5)
    assert allowed.status_code == 201, allowed.text
    assert session.get(f"{gated}/identities", headers=_gate(HARNESS_GATE_USER),
                       timeout=5).status_code == 200


# ------------------------------------------------------------------ the chooser under a mount

def test_the_chooser_posts_back_to_the_advertised_authorize_url_not_the_site_root():
    """On staging the stub is mounted at https://eval.keeldiscovery.com/oidc; a root-relative
    form action lands on keel-web's 404 (the founder's first click, 2026-09-11). The page must
    use the same absolute /authorize the discovery document advertises."""
    page = picker_html(list(STUB_IDENTITIES), {"state": "s"},
                       authorize_url="https://eval.example.test/oidc/authorize")
    assert 'action="https://eval.example.test/oidc/authorize"' in page
    assert 'action="/authorize"' not in page
    assert 'href="https://eval.example.test/oidc/authorize?' in page


def test_the_served_chooser_uses_the_issuer_it_was_started_with(ungated):
    query = {"client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI, "response_type": "code",
             "scope": "openid email profile", "state": "s", "nonce": "n",
             "code_challenge": "c" * 43, "code_challenge_method": "S256"}
    page = requests.get(f"{ungated}/authorize", params=query, timeout=5).text
    assert f'action="{ungated}/authorize"' in page
