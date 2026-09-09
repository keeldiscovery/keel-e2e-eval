"""Stackless: stack.toml loading, defaults, and the missing-sibling error (T007)."""

import pytest

from stack.config import ConfigError, load_config


def test_defaults_apply_when_stack_toml_is_absent(tmp_path):
    config = load_config(tmp_path / "does-not-exist.toml", validate=False)
    assert config.postgres_port == 55432
    assert config.cloud_port == 18080
    assert config.web_port == 5173
    assert config.cloud_boot_timeout == 120
    assert config.web_boot_timeout == 60


def test_partial_toml_fills_in_the_rest_from_defaults(tmp_path):
    toml_path = tmp_path / "stack.toml"
    toml_path.write_text('[ports]\ncloud = 19999\n')
    config = load_config(toml_path, validate=False)
    assert config.cloud_port == 19999
    assert config.postgres_port == 55432  # default, since [ports] only overrode cloud
    assert config.web_port == 5173


def test_missing_sibling_directory_raises_a_clear_error(tmp_path):
    toml_path = tmp_path / "stack.toml"
    toml_path.write_text(
        '[paths]\n'
        'keel_cloud = "./nowhere-near-here"\n'
    )
    with pytest.raises(ConfigError) as excinfo:
        load_config(toml_path, validate=True)
    message = str(excinfo.value)
    assert "keel_cloud" in message
    assert "nowhere-near-here" in message


def test_relative_default_paths_resolve_to_absolute_paths(tmp_path):
    # validate=False so we can inspect resolution without needing real sibling checkouts.
    # Relative defaults resolve against this repo's own root, not the toml file's directory --
    # so `make` works the same regardless of the caller's cwd.
    config = load_config(tmp_path / "absent.toml", validate=False)
    assert config.keel_cloud.name == "keel-cloud"
    assert config.keel_cloud.is_absolute()


# ------------------------------------------------------- the connect-stack siblings (spec 005)

def test_keel_runtime_and_keel_connect_skill_default_paths_resolve(tmp_path):
    config = load_config(tmp_path / "absent.toml", validate=False)
    assert config.keel_runtime.name == "keel-runtime"
    assert config.keel_runtime.is_absolute()
    assert config.keel_connect_skill.name == "keel-connect-skill"
    assert config.keel_connect_skill.is_absolute()


def test_connect_check_script_path_is_under_keel_connect_skill_scripts(tmp_path):
    config = load_config(tmp_path / "absent.toml", validate=False)
    assert config.connect_check_script_path == (
        config.keel_connect_skill / "scripts" / "keel_connect_check.py"
    )


def test_stack_toml_can_override_keel_runtime_path(tmp_path):
    toml_path = tmp_path / "stack.toml"
    toml_path.write_text('[paths]\nkeel_runtime = "./somewhere-else"\n')
    config = load_config(toml_path, validate=False)
    assert config.keel_runtime.name == "somewhere-else"


# ------------------------------------------------- split-stacks: the playground profile (T012)

def test_default_profile_is_eval(tmp_path):
    config = load_config(tmp_path / "absent.toml", validate=False)
    assert config.profile == "eval"


def test_playground_profile_uses_its_own_default_ports_when_stack_toml_is_absent(tmp_path):
    config = load_config(tmp_path / "absent.toml", validate=False, profile="playground")
    assert config.profile == "playground"
    assert config.postgres_port == 55433
    assert config.cloud_port == 18081
    assert config.web_port == 5174
    # Every other table is shared between profiles -- unaffected by the profile switch.
    assert config.cloud_boot_timeout == 120


def test_playground_profile_never_collides_with_the_eval_profiles_ports(tmp_path):
    eval_config = load_config(tmp_path / "absent.toml", validate=False, profile="eval")
    playground_config = load_config(tmp_path / "absent.toml", validate=False, profile="playground")
    eval_ports = {eval_config.postgres_port, eval_config.cloud_port, eval_config.web_port}
    playground_ports = {playground_config.postgres_port, playground_config.cloud_port,
                         playground_config.web_port}
    assert eval_ports.isdisjoint(playground_ports)


def test_playground_ports_override_from_stack_toml(tmp_path):
    toml_path = tmp_path / "stack.toml"
    toml_path.write_text('[playground.ports]\ncloud = 28080\n')
    config = load_config(toml_path, validate=False, profile="playground")
    assert config.cloud_port == 28080
    assert config.postgres_port == 55433  # default, since only cloud was overridden
    # The eval profile reading the same file is unaffected by the [playground] table at all.
    eval_config = load_config(toml_path, validate=False, profile="eval")
    assert eval_config.cloud_port == 18080


def test_unknown_profile_raises_config_error(tmp_path):
    with pytest.raises(ConfigError):
        load_config(tmp_path / "absent.toml", validate=False, profile="nope")


# ---------------------------------------------------- what keel-cloud is told about keel-web
# (spec 015 second half; keel-cloud `canon/designs/google-sign-in-design.md` §5.1, §10.3)

def test_the_founder_base_url_is_an_origin_and_carries_no_path(tmp_path):
    """**A harness fault this spec found and fixed, before any of it ran.**

    `KEEL_V2_FOUNDER_BASE_URL` used to be `http://localhost:5173/p`, matching the deleted
    `keel.v2.founder-base-url` *property* that had a project path baked onto it for `OpenWebUrls`.
    keel-cloud now derives three things from the env var, all by appending to it:
    `/connect` (`keel.v2.connect.verification-uri`), `/v2/auth/google/callback`
    (`keel.v2.auth.google.redirect-uri`) and -- since spec 032 -- **`/login`**, where every
    refused sign-in lands (`AuthError.location`) and, plus the stored `return_to`, where a
    successful one is sent (`GoogleCallbackController`). Its own default is a bare
    `http://localhost:5173`.

    Left at `.../p`, this stack would have sent a signed-in founder to `/p/` and a refused one to
    `/p/login?auth_error=...` -- both of which keel-web's router resolves through
    `/p/:projectId/*`, as a project whose id is the word *login*. Every scenario would have gone
    red at its first step, for a reason none of their screens could have explained.
    """
    from stack import cloud

    env = cloud.build_env(load_config(tmp_path / "absent.toml", validate=False))
    assert env["KEEL_V2_FOUNDER_BASE_URL"] == "http://localhost:5173"
    assert not env["KEEL_V2_FOUNDER_BASE_URL"].endswith("/p")
    # The participant base URL is *not* an origin: it is used verbatim to mint invitation links,
    # and keel-web serves the stranger's page at `/i/:token`.
    assert env["KEEL_V2_PARTICIPANT_BASE_URL"] == "http://localhost:5173/i"
    # Both derivations keel-cloud would otherwise compute for itself are still set explicitly,
    # and both must agree with the origin above.
    assert env["KEEL_V2_CONNECT_VERIFICATION_URI"] == "http://localhost:5173/connect"
    assert env["KEEL_GOOGLE_REDIRECT_URI"] == \
        "http://localhost:18080/v2/auth/google/callback"


def test_the_playground_profile_gets_its_own_origin(tmp_path):
    from stack import cloud

    env = cloud.build_env(load_config(tmp_path / "absent.toml", validate=False,
                                      profile="playground"))
    assert env["KEEL_V2_FOUNDER_BASE_URL"] == "http://localhost:5174"
    assert env["KEEL_V2_CONNECT_VERIFICATION_URI"] == "http://localhost:5174/connect"


def test_the_readiness_gate_left_the_route_the_password_took_with_it():
    """§10.3: `stack/cloud.py` polled `GET /v2/setup` for a `200` and keel-cloud spec 032 deletes
    that route. `GET /v2/me` expecting `401` proves the same three things -- the JVM is listening,
    Flyway has run, the security chain is wired -- and adds no route to the product for the
    harness's benefit."""
    import inspect

    from stack import cloud

    assert (cloud.READY_PATH, cloud.READY_STATUS) == ("/v2/me", 401)
    for function in (cloud.is_up, cloud.up):
        source = inspect.getsource(function)
        assert "/v2/setup" not in source, "the boot gate still polls a route that is gone"
        assert "READY_PATH" in source
