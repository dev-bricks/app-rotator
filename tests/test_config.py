import pytest

from app_rotator.config import ConfigError, default_config


def test_default_config_is_disabled_dry_run_and_valid():
    config = default_config()
    config.validate()
    assert config.enabled is False
    assert config.dry_run is True
    assert config.apps[0].process_name == "ChatGPT.exe"
    assert "OpenAI.Codex_" in config.apps[0].path_contains


def test_name_only_process_filter_is_rejected():
    config = default_config()
    config.apps[0].path_contains = None
    with pytest.raises(ConfigError, match="name-only"):
        config.validate()
