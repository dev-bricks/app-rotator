import pytest

from app_rotator.config import ConfigError, default_config
from app_rotator.settings import (
    ProviderDraft,
    apply_settings,
    minutes_to_seconds,
    seconds_to_minutes,
)


@pytest.mark.parametrize(
    ("seconds", "minutes"),
    [(0, "0"), (60, "1"), (90, "1.5"), (1800, "30"), (14_400, "240")],
)
def test_seconds_are_displayed_as_minutes(seconds, minutes):
    assert seconds_to_minutes(seconds) == minutes


def test_minute_parser_accepts_decimal_comma_and_converts_to_seconds():
    assert minutes_to_seconds("1,5", "Duration", allow_zero=False) == 90


def test_subminute_legacy_value_round_trips_with_negligible_error():
    rendered = seconds_to_minutes(10)
    restored = minutes_to_seconds(rendered, "Gap", allow_zero=True)
    assert restored == pytest.approx(10, abs=1e-9)


@pytest.mark.parametrize("value", ["", "-1", "nan", "inf"])
def test_minute_parser_rejects_invalid_values(value):
    with pytest.raises(ConfigError):
        minutes_to_seconds(value, "Duration", allow_zero=False)


def test_settings_convert_every_visible_duration_to_internal_seconds():
    config = default_config()
    drafts = [ProviderDraft.from_app(app) for app in config.apps]
    drafts[0].duration_minutes = "2.5"
    drafts[1].enabled = False

    updated = apply_settings(
        config,
        enabled=True,
        dry_run=True,
        gap_minutes="0.5",
        cycle_pause_minutes="2",
        overall_stop_minutes="120",
        reactivation_interval_minutes="1.25",
        controller_executable="controller.exe",
        missing_behavior="block",
        providers=drafts,
    )

    assert updated.apps[0].duration_seconds == 150
    assert updated.apps[1].enabled is False
    assert updated.inter_app_gap_seconds == 30
    assert updated.cycle_pause_seconds == 120
    assert updated.overall_stop_seconds == 7200
    assert updated.codex_controller.reactivation_interval_seconds == 75


def test_manual_provider_draft_can_be_added_and_saved():
    draft = ProviderDraft.new()
    draft.id = "my-provider"
    draft.label = "My Provider"
    draft.process_name = "MyProvider.exe"
    draft.path_value = r"C:\Tools\MyProvider.exe"
    draft.launch_value = r"C:\Tools\MyProvider.exe"
    draft.enabled = True

    provider = draft.to_app()

    assert provider.id == "my-provider"
    assert provider.enabled is True
    assert provider.duration_seconds == 1800
    assert provider.path_exact == r"C:\Tools\MyProvider.exe"
