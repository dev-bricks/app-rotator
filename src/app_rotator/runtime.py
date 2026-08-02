from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from .config import atomic_write_json


class RunStatus(StrEnum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class Phase(StrEnum):
    APP = "app"
    GAP = "gap"
    CYCLE_PAUSE = "cycle_pause"


@dataclass(slots=True)
class RuntimeState:
    status: RunStatus = RunStatus.STOPPED
    phase: Phase = Phase.APP
    app_index: int = 0
    remaining_seconds: float = 0.0
    active_elapsed_seconds: float = 0.0
    last_command_id: int = 0
    blocked_reason: str | None = None
    updated_at: float = 0.0

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> RuntimeState:
        value = dict(raw)
        value["status"] = RunStatus(value.get("status", RunStatus.STOPPED))
        value["phase"] = Phase(value.get("phase", Phase.APP))
        return cls(**value)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StateStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> RuntimeState:
        try:
            return RuntimeState.from_dict(json.loads(self.path.read_text(encoding="utf-8")))
        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
            return RuntimeState()

    def save(self, state: RuntimeState) -> None:
        state.updated_at = time.time()
        atomic_write_json(self.path, state.to_dict())


class EventLog:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()

    def write(self, event: str, **details: Any) -> None:
        item = {"timestamp": time.time(), "event": event, **details}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


class CommandStore:
    def __init__(self, path: Path):
        self.path = path

    def send(self, command: str) -> int:
        current = self.read()
        command_id = int(current.get("id", 0)) + 1
        atomic_write_json(
            self.path,
            {"id": command_id, "command": command, "timestamp": time.time()},
        )
        return command_id

    def read(self) -> dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"id": 0, "command": ""}


class InstanceLock:
    """Non-blocking single-instance lock with a diagnostic PID sidecar."""

    def __init__(self, path: Path):
        self.path = path
        self._handle: Any = None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.path.open("a+b")
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            return False
        handle.seek(0)
        handle.truncate()
        handle.write(str(os.getpid()).encode("ascii"))
        handle.flush()
        self._handle = handle
        return True

    def release(self) -> None:
        if not self._handle:
            return
        self._handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        finally:
            self._handle.close()
            self._handle = None

    def __enter__(self) -> InstanceLock:
        if not self.acquire():
            raise RuntimeError("App Rotator is already running")
        return self

    def __exit__(self, *_args: object) -> None:
        self.release()
