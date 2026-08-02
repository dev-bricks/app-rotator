import json

import pytest

from app_rotator.config import (
    CURRENT_SCHEMA_VERSION,
    ConfigError,
    default_config,
    load_config,
)


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


@pytest.mark.parametrize("existing_enabled", [True, False])
def test_legacy_config_migration_adds_known_providers_without_enabling_them(
    tmp_path,
    existing_enabled,
):
    legacy = default_config().to_dict()
    legacy.pop("schema_version")
    legacy["enabled"] = True
    legacy["dry_run"] = False
    legacy["apps"] = [legacy["apps"][0]]
    legacy["apps"][0]["label"] = "My existing Codex"
    legacy["apps"][0]["enabled"] = existing_enabled
    path = tmp_path / "config.json"
    path.write_text(json.dumps(legacy), encoding="utf-8")

    migrated = load_config(path)

    assert migrated.schema_version == CURRENT_SCHEMA_VERSION
    assert [app.id for app in migrated.apps] == ["codex", "claude", "antigravity"]
    assert migrated.apps[0].label == "My existing Codex"
    assert migrated.apps[0].enabled is existing_enabled
    assert migrated.apps[1].enabled is False
    assert migrated.apps[2].enabled is False
    assert migrated.enabled is True
    assert migrated.dry_run is False
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted["schema_version"] == CURRENT_SCHEMA_VERSION


def test_all_providers_may_be_saved_outside_rotation():
    config = default_config()
    for provider in config.apps:
        provider.enabled = False
    config.validate()
