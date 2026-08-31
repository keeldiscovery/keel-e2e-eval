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
