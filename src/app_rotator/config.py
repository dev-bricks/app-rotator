from __future__ import annotations

import contextlib
import json
import os
import tempfile
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when a configuration is unsafe or malformed."""


CURRENT_SCHEMA_VERSION = 2


def data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        base = str(Path.home() / "AppData" / "Local")
    return Path(base) / "AppRotator"


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


@dataclass(slots=True)
class AppSpec:
    id: str
    label: str
    duration_seconds: float
    process_name: str
    path_contains: str | None = None
    path_exact: str | None = None
    launch_type: str = "executable"
    launch_value: str = ""
    launch_args: list[str] = field(default_factory=list)
    enabled: bool = True
    codex_safe_start: bool = False

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> AppSpec:
        allowed = {item.name for item in cls.__dataclass_fields__.values()}
        unknown = set(value) - allowed
        if unknown:
            raise ConfigError(f"Unknown app keys: {', '.join(sorted(unknown))}")
        return cls(**value)

    def validate(self) -> None:
        if not self.id.strip() or not self.label.strip():
            raise ConfigError("Every app needs a non-empty id and label")
        if self.duration_seconds <= 0:
            raise ConfigError(f"{self.id}: duration_seconds must be greater than zero")
        if not self.process_name.strip():
            raise ConfigError(f"{self.id}: process_name is required")
        if bool(self.path_contains) == bool(self.path_exact):
            raise ConfigError(
                f"{self.id}: configure exactly one of path_contains or path_exact; "
                "name-only process killing is intentionally rejected"
            )
        if self.launch_type not in {"appsfolder", "executable", "command"}:
            raise ConfigError(f"{self.id}: invalid launch_type {self.launch_type!r}")
        if not self.launch_value.strip():
            raise ConfigError(f"{self.id}: launch_value is required")


@dataclass(slots=True)
class CodexControllerConfig:
    executable: str = ""
    reactivation_interval_seconds: float = 60.0
    missing_behavior: str = "block"
    timeout_seconds: float = 20.0

    def validate(self) -> None:
        if self.reactivation_interval_seconds < 0:
            raise ConfigError("Codex reactivation interval cannot be negative")
        if self.missing_behavior not in {"block", "skip"}:
            raise ConfigError("Codex missing_behavior must be 'block' or 'skip'")
        if self.timeout_seconds <= 0:
            raise ConfigError("Codex controller timeout must be greater than zero")


@dataclass(slots=True)
class RotatorConfig:
    schema_version: int = CURRENT_SCHEMA_VERSION
    enabled: bool = False
    dry_run: bool = True
    inter_app_gap_seconds: float = 10.0
    cycle_pause_seconds: float = 60.0
    overall_stop_seconds: float = 14_400.0
    tick_seconds: float = 0.5
    terminate_timeout_seconds: float = 8.0
    apps: list[AppSpec] = field(default_factory=list)
    codex_controller: CodexControllerConfig = field(default_factory=CodexControllerConfig)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> RotatorConfig:
        allowed = {item.name for item in cls.__dataclass_fields__.values()}
        unknown = set(value) - allowed
        if unknown:
            raise ConfigError(f"Unknown config keys: {', '.join(sorted(unknown))}")
        raw = dict(value)
        raw["apps"] = [AppSpec.from_dict(item) for item in raw.get("apps", [])]
        raw["codex_controller"] = CodexControllerConfig(**raw.get("codex_controller", {}))
        return cls(**raw)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        if self.schema_version != CURRENT_SCHEMA_VERSION:
            raise ConfigError(f"Unsupported schema_version: {self.schema_version}")
        if self.inter_app_gap_seconds < 0 or self.cycle_pause_seconds < 0:
            raise ConfigError("Gap and cycle pause cannot be negative")
        if self.overall_stop_seconds <= 0:
            raise ConfigError("overall_stop_seconds must be greater than zero")
        if self.tick_seconds <= 0:
            raise ConfigError("tick_seconds must be greater than zero")
        if self.terminate_timeout_seconds < 0:
            raise ConfigError("terminate_timeout_seconds cannot be negative")
        identifiers = [app.id for app in self.apps]
        if len(set(identifiers)) != len(identifiers):
            raise ConfigError("App ids must be unique")
        for app in self.apps:
            app.validate()
        self.codex_controller.validate()


def known_provider_specs() -> list[AppSpec]:
    """Return fresh entries for providers recognized by the built-in catalog."""

    return [
        AppSpec(
            id="codex",
            label="Codex Desktop",
            duration_seconds=1800,
            process_name="ChatGPT.exe",
            path_contains=r"WindowsApps\OpenAI.Codex_",
            launch_type="appsfolder",
            launch_value="OpenAI.Codex_2p2nqsd0c76g0!App",
            codex_safe_start=True,
        ),
        AppSpec(
            id="claude",
            label="Claude Desktop",
            duration_seconds=1800,
            process_name="Claude.exe",
            path_contains=r"WindowsApps\Claude_",
            launch_type="appsfolder",
            launch_value="Claude_pzs8sxrjxfjjc!Claude",
        ),
        AppSpec(
            id="antigravity",
            label="Antigravity",
            duration_seconds=1800,
            process_name="Antigravity.exe",
            path_exact=r"%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe",
            launch_type="executable",
            launch_value=r"%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe",
        ),
    ]


def default_config() -> RotatorConfig:
    return RotatorConfig(apps=known_provider_specs())


def migrate_config_payload(value: dict[str, Any]) -> dict[str, Any]:
    """Upgrade older payloads without changing their active rotation.

    Known providers missing from an existing configuration are appended but
    disabled. Existing entries, order, enabled flags, and safety settings win.
    """

    raw_version = value.get("schema_version", 1)
    if not isinstance(raw_version, int) or raw_version > CURRENT_SCHEMA_VERSION:
        raise ConfigError(f"Unsupported schema_version: {raw_version}")
    migrated = deepcopy(value)
    apps = migrated.setdefault("apps", [])
    if not isinstance(apps, list):
        raise ConfigError("apps must be an array")
    existing_ids = {
        item.get("id")
        for item in apps
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for provider in known_provider_specs():
        if provider.id in existing_ids:
            continue
        payload = asdict(provider)
        payload["enabled"] = False
        apps.append(payload)
    migrated["schema_version"] = CURRENT_SCHEMA_VERSION
    return migrated


def load_config(path: Path) -> RotatorConfig:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"Configuration does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc
    migrated = migrate_config_payload(raw)
    config = RotatorConfig.from_dict(migrated)
    config.validate()
    if config.to_dict() != raw:
        atomic_write_json(path, config.to_dict())
    return config


def save_config(path: Path, config: RotatorConfig) -> None:
    config.validate()
    atomic_write_json(path, config.to_dict())
