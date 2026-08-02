from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .config import CodexControllerConfig
from .runtime import EventLog


class ControllerError(RuntimeError):
    pass


Runner = Callable[..., Any]


class CodexAutomationController:
    """Fail-closed adapter for an external automation controller.

    The adapter deliberately knows nothing about automation.toml. The external
    executable owns the provider-native pause/resume implementation.
    """

    def __init__(
        self,
        config: CodexControllerConfig,
        events: EventLog,
        *,
        dry_run: bool,
        runner: Runner = subprocess.run,
    ):
        self.config = config
        self.events = events
        self.dry_run = dry_run
        self._runner = runner

    def available(self) -> bool:
        executable = self.config.executable.strip()
        if not executable:
            return False
        candidate = Path(os.path.expandvars(executable)).expanduser()
        return candidate.is_file()

    def _call(self, action: str, *args: str) -> None:
        executable = str(Path(os.path.expandvars(self.config.executable)).expanduser())
        command = [executable, action, *args]
        self.events.write("codex_controller", action=action, command=command, dry_run=self.dry_run)
        if self.dry_run:
            return
        if not self.available():
            raise ControllerError("Codex automation controller is unavailable")
        try:
            completed = self._runner(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ControllerError(f"Codex controller {action} failed: {exc}") from exc
        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            raise ControllerError(
                f"Codex controller {action} returned {completed.returncode}: {stderr[:300]}"
            )

    def pause_all(self) -> None:
        self._call("pause-all")

    def stagger_resume(self) -> None:
        self._call(
            "stagger-resume",
            "--interval-seconds",
            str(self.config.reactivation_interval_seconds),
        )

    def cancel(self) -> None:
        if self.dry_run or self.available():
            self._call("cancel")
        else:
            self.events.write("codex_controller_cancel_skipped", reason="controller_unavailable")
