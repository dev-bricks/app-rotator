from __future__ import annotations

import os
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Protocol

from .config import AppSpec
from .runtime import EventLog


def _norm_path(value: str) -> str:
    expanded = os.path.expandvars(os.path.expanduser(value))
    return os.path.normcase(os.path.normpath(expanded))


def process_matches(app: AppSpec, name: str, executable: str | None) -> bool:
    expected_name = app.process_name.casefold()
    actual_name = name.casefold()
    if actual_name != expected_name:
        if expected_name.endswith(".exe") and actual_name == expected_name[:-4]:
            pass
        elif actual_name.endswith(".exe") and actual_name[:-4] == expected_name:
            pass
        else:
            return False
    if not executable:
        return False
    normalized = _norm_path(executable)
    if app.path_exact:
        return normalized == _norm_path(app.path_exact)
    if app.path_contains:
        return _norm_path(app.path_contains) in normalized
    return False


class ProcessLike(Protocol):
    info: dict[str, Any]
    pid: int

    def terminate(self) -> None: ...

    def kill(self) -> None: ...


class ProcessManager:
    def __init__(
        self,
        events: EventLog,
        *,
        dry_run: bool,
        terminate_timeout: float,
        process_iter: Any | None = None,
        wait_procs: Any | None = None,
        popen: Any = subprocess.Popen,
    ):
        self.events = events
        self.dry_run = dry_run
        self.terminate_timeout = terminate_timeout
        if process_iter is None or wait_procs is None:
            import psutil

            process_iter = psutil.process_iter
            wait_procs = psutil.wait_procs
            self._process_errors = (psutil.Error, OSError, PermissionError)
        else:
            self._process_errors = (OSError, PermissionError)
        self._process_iter = process_iter
        self._wait_procs = wait_procs
        self._popen = popen

    def matching(self, app: AppSpec) -> list[ProcessLike]:
        result: list[ProcessLike] = []
        for process in self._process_iter(["pid", "name", "exe"]):
            try:
                info = process.info
                if process_matches(app, info.get("name") or "", info.get("exe")):
                    result.append(process)
            except self._process_errors:
                continue
        return result

    def close_app(self, app: AppSpec) -> None:
        matches = self.matching(app)
        self.events.write(
            "process_close_requested",
            app=app.id,
            pids=[item.pid for item in matches],
            dry_run=self.dry_run,
        )
        if self.dry_run or not matches:
            return
        for process in matches:
            try:
                process.terminate()
            except self._process_errors:
                continue
        _, alive = self._wait_procs(matches, timeout=self.terminate_timeout)
        for process in alive:
            try:
                process.kill()
            except self._process_errors:
                continue

    def close_all(self, apps: Iterable[AppSpec]) -> None:
        for app in apps:
            self.close_app(app)

    def launch(self, app: AppSpec) -> None:
        if app.launch_type == "appsfolder":
            command = ["explorer.exe", f"shell:AppsFolder\\{app.launch_value}"]
        elif app.launch_type == "executable":
            command = [os.path.expandvars(os.path.expanduser(app.launch_value)), *app.launch_args]
        else:
            command = [app.launch_value, *app.launch_args]
        self.events.write(
            "process_launch_requested",
            app=app.id,
            command=command,
            dry_run=self.dry_run,
        )
        if self.dry_run:
            return
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        cwd = str(Path(command[0]).parent) if app.launch_type == "executable" else None
        self._popen(command, cwd=cwd, creationflags=creationflags)
