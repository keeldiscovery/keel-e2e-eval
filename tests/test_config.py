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
