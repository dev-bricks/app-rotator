from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation

from .config import AppSpec, ConfigError, RotatorConfig


def seconds_to_minutes(seconds: float) -> str:
    """Format stored seconds as an editable minute value without unit ambiguity."""

    value = Decimal(str(seconds)) / Decimal(60)
    rendered = format(value, ".12f").rstrip("0").rstrip(".")
    return rendered or "0"


def minutes_to_seconds(
    value: str,
    field_name: str,
    *,
    allow_zero: bool,
) -> float:
    """Parse a Settings minute field and return validated seconds."""

    normalized = value.strip().replace(",", ".")
    try:
        minutes = Decimal(normalized)
    except InvalidOperation as exc:
        raise ConfigError(f"{field_name} must be a number in minutes") from exc
    if not minutes.is_finite():
        raise ConfigError(f"{field_name} must be a finite number in minutes")
    if minutes < 0 or (minutes == 0 and not allow_zero):
        qualifier = "zero or greater" if allow_zero else "greater than zero"
        raise ConfigError(f"{field_name} must be {qualifier} minutes")
    return float(minutes * Decimal(60))


@dataclass(slots=True)
class ProviderDraft:
    id: str
    label: str
    duration_minutes: str
    process_name: str
    path_mode: str
    path_value: str
    launch_type: str
    launch_value: str
    launch_args_json: str
    enabled: bool
    codex_safe_start: bool

    @classmethod
    def from_app(cls, app: AppSpec) -> ProviderDraft:
        return cls(
            id=app.id,
            label=app.label,
            duration_minutes=seconds_to_minutes(app.duration_seconds),
            process_name=app.process_name,
            path_mode="exact" if app.path_exact else "contains",
            path_value=app.path_exact or app.path_contains or "",
            launch_type=app.launch_type,
            launch_value=app.launch_value,
            launch_args_json=json.dumps(app.launch_args, ensure_ascii=False),
            enabled=app.enabled,
            codex_safe_start=app.codex_safe_start,
        )

    @classmethod
    def new(cls) -> ProviderDraft:
        identifier = f"provider-{uuid.uuid4().hex[:8]}"
        return cls(
            id=identifier,
            label="New Provider",
            duration_minutes="30",
            process_name="Provider.exe",
            path_mode="exact",
            path_value="",
            launch_type="executable",
            launch_value="",
            launch_args_json="[]",
            enabled=False,
            codex_safe_start=False,
        )

    def to_app(self) -> AppSpec:
        try:
            launch_args = json.loads(self.launch_args_json)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"{self.id}: launch arguments must be a JSON array") from exc
        if not isinstance(launch_args, list) or not all(
            isinstance(argument, str) for argument in launch_args
        ):
            raise ConfigError(f"{self.id}: launch arguments must be a JSON array of strings")
        if self.path_mode not in {"contains", "exact"}:
            raise ConfigError(f"{self.id}: path mode must be contains or exact")
        return AppSpec(
            id=self.id.strip(),
            label=self.label.strip(),
            duration_seconds=minutes_to_seconds(
                self.duration_minutes,
                f"{self.label or self.id} duration",
                allow_zero=False,
            ),
            process_name=self.process_name.strip(),
            path_contains=self.path_value.strip() if self.path_mode == "contains" else None,
            path_exact=self.path_value.strip() if self.path_mode == "exact" else None,
            launch_type=self.launch_type,
            launch_value=self.launch_value.strip(),
            launch_args=launch_args,
            enabled=self.enabled,
            codex_safe_start=self.codex_safe_start,
        )


def apply_settings(
    base: RotatorConfig,
    *,
    enabled: bool,
    dry_run: bool,
    gap_minutes: str,
    cycle_pause_minutes: str,
    overall_stop_minutes: str,
    reactivation_interval_minutes: str,
    controller_executable: str,
    missing_behavior: str,
    providers: list[ProviderDraft],
) -> RotatorConfig:
    controller = replace(
        base.codex_controller,
        executable=controller_executable.strip(),
        reactivation_interval_seconds=minutes_to_seconds(
            reactivation_interval_minutes,
            "Codex reactivation interval",
            allow_zero=True,
        ),
        missing_behavior=missing_behavior,
    )
    updated = replace(
        base,
        enabled=enabled,
        dry_run=dry_run,
        inter_app_gap_seconds=minutes_to_seconds(
            gap_minutes,
            "Gap between providers",
            allow_zero=True,
        ),
        cycle_pause_seconds=minutes_to_seconds(
            cycle_pause_minutes,
            "Cycle pause",
            allow_zero=True,
        ),
        overall_stop_seconds=minutes_to_seconds(
            overall_stop_minutes,
            "Automatic overall stop",
            allow_zero=False,
        ),
        apps=[provider.to_app() for provider in providers],
        codex_controller=controller,
    )
    updated.validate()
    return updated
