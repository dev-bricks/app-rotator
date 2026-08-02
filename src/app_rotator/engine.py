from __future__ import annotations

import threading
import time
from collections.abc import Callable

from .config import AppSpec, RotatorConfig
from .controller import CodexAutomationController, ControllerError
from .processes import ProcessManager
from .runtime import CommandStore, EventLog, Phase, RunStatus, RuntimeState, StateStore


class RotationEngine:
    def __init__(
        self,
        config: RotatorConfig,
        processes: ProcessManager,
        controller: CodexAutomationController,
        state_store: StateStore,
        events: EventLog,
        command_store: CommandStore | None = None,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.config = config
        self.processes = processes
        self.controller = controller
        self.state_store = state_store
        self.events = events
        self.command_store = command_store
        self.clock = clock
        self.state = state_store.load()
        if (
            self.state.app_index < 0
            or self.state.app_index >= len(self.apps)
            or self.state.remaining_seconds < 0
            or self.state.active_elapsed_seconds < 0
        ):
            last_command = self.state.last_command_id
            self.state = RuntimeState(
                last_command_id=last_command,
                blocked_reason="Persisted state was reset after a configuration change",
            )
            self.state_store.save(self.state)
            self.events.write("invalid_persisted_state_reset")
        self._lock = threading.RLock()
        self._last_tick: float | None = None
        self._quit = threading.Event()

    @property
    def apps(self) -> list[AppSpec]:
        return [app for app in self.config.apps if app.enabled]

    def _persist(self) -> None:
        self.state_store.save(self.state)

    def _cancel_controller(self) -> None:
        try:
            self.controller.cancel()
        except ControllerError as exc:
            self.events.write("codex_controller_cancel_failed", error=str(exc))

    def _start_current_phase(self) -> None:
        if self.state.phase != Phase.APP:
            self.processes.close_all(self.apps)
            return
        app = self.apps[self.state.app_index]
        self.state.blocked_reason = None
        if app.codex_safe_start:
            if not self.controller.available() and not self.controller.dry_run:
                behavior = self.config.codex_controller.missing_behavior
                reason = "Codex controller unavailable"
                self.events.write("codex_stage_unavailable", behavior=behavior, reason=reason)
                if behavior == "skip":
                    self._advance_from_app()
                    return
                self.processes.close_all(self.apps)
                self.state.status = RunStatus.PAUSED
                self.state.blocked_reason = reason
                self._persist()
                return
            try:
                self.controller.pause_all()
                self.processes.launch(app)
                self.controller.stagger_resume()
            except ControllerError as exc:
                self.processes.close_all(self.apps)
                self._cancel_controller()
                self.state.status = RunStatus.PAUSED
                self.state.blocked_reason = str(exc)
                self.events.write("codex_stage_blocked", error=str(exc))
                self._persist()
                return
        else:
            self.processes.launch(app)
        self.events.write(
            "phase_started",
            phase=self.state.phase,
            app=app.id,
            remaining_seconds=self.state.remaining_seconds,
        )

    def play(self) -> None:
        with self._lock:
            if not self.config.enabled:
                raise RuntimeError("Rotation is disabled in Settings")
            if self.state.status == RunStatus.RUNNING:
                return
            if self.state.status == RunStatus.STOPPED:
                self.processes.close_all(self.apps)
                self._cancel_controller()
                self.state = RuntimeState(
                    status=RunStatus.RUNNING,
                    phase=Phase.APP,
                    app_index=0,
                    remaining_seconds=self.apps[0].duration_seconds,
                )
                event = "rotation_started"
            else:
                self.state.status = RunStatus.RUNNING
                self.state.blocked_reason = None
                event = "rotation_resumed"
            self._last_tick = self.clock()
            self.events.write(event, app_index=self.state.app_index, phase=self.state.phase)
            self._start_current_phase()
            self._persist()

    def pause(self) -> None:
        with self._lock:
            if self.state.status != RunStatus.RUNNING:
                return
            self._consume_time(self.clock())
            self.processes.close_all(self.apps)
            self._cancel_controller()
            self.state.status = RunStatus.PAUSED
            self._last_tick = None
            self.events.write(
                "rotation_paused",
                app_index=self.state.app_index,
                phase=self.state.phase,
                remaining_seconds=self.state.remaining_seconds,
            )
            self._persist()

    def stop(self, reason: str = "user") -> None:
        with self._lock:
            self.processes.close_all(self.apps)
            self._cancel_controller()
            last_command = self.state.last_command_id
            self.state = RuntimeState(last_command_id=last_command)
            self._last_tick = None
            self.events.write("rotation_stopped", reason=reason)
            self._persist()

    def quit(self) -> None:
        self.stop(reason="quit")
        self._quit.set()

    def _advance_from_app(self) -> None:
        app = self.apps[self.state.app_index]
        # Reassert the all-closed invariant at every boundary. This also catches
        # a managed app that the user manually reopened during another phase.
        self.processes.close_all(self.apps)
        if app.codex_safe_start:
            self._cancel_controller()
        if self.state.app_index == len(self.apps) - 1:
            self.state.phase = Phase.CYCLE_PAUSE
            self.state.remaining_seconds = self.config.cycle_pause_seconds
        else:
            self.state.phase = Phase.GAP
            self.state.remaining_seconds = self.config.inter_app_gap_seconds
        self._skip_zero_phases()

    def _skip_zero_phases(self) -> None:
        guard = 0
        while self.state.remaining_seconds <= 0 and guard < len(self.apps) * 3 + 3:
            guard += 1
            if self.state.phase == Phase.GAP:
                self.state.app_index += 1
                self.state.phase = Phase.APP
                self.state.remaining_seconds = self.apps[self.state.app_index].duration_seconds
                self._start_current_phase()
                return
            if self.state.phase == Phase.CYCLE_PAUSE:
                self.state.app_index = 0
                self.state.phase = Phase.APP
                self.state.remaining_seconds = self.apps[0].duration_seconds
                self._start_current_phase()
                return
            self._advance_from_app()

    def _advance_phase(self) -> None:
        if self.state.phase == Phase.APP:
            self._advance_from_app()
        elif self.state.phase == Phase.GAP:
            self.state.app_index += 1
            self.state.phase = Phase.APP
            self.state.remaining_seconds = self.apps[self.state.app_index].duration_seconds
            self._start_current_phase()
        else:
            self.state.app_index = 0
            self.state.phase = Phase.APP
            self.state.remaining_seconds = self.apps[0].duration_seconds
            self._start_current_phase()
        self.events.write(
            "phase_advanced",
            phase=self.state.phase,
            app_index=self.state.app_index,
            remaining_seconds=self.state.remaining_seconds,
        )

    def _consume_time(self, now: float) -> None:
        if self._last_tick is None:
            self._last_tick = now
            return
        elapsed = max(0.0, now - self._last_tick)
        self._last_tick = now
        if elapsed == 0:
            return
        overall_remaining = max(
            0.0,
            self.config.overall_stop_seconds - self.state.active_elapsed_seconds,
        )
        elapsed = min(elapsed, overall_remaining)
        self.state.active_elapsed_seconds += elapsed
        while elapsed > 0 and self.state.status == RunStatus.RUNNING:
            consumed = min(elapsed, self.state.remaining_seconds)
            self.state.remaining_seconds -= consumed
            elapsed -= consumed
            if self.state.remaining_seconds <= 1e-9:
                self._advance_phase()
        if self.state.active_elapsed_seconds >= self.config.overall_stop_seconds - 1e-9:
            self.stop(reason="overall_timer")

    def tick(self, now: float | None = None) -> None:
        with self._lock:
            self._poll_command()
            if self.state.status == RunStatus.RUNNING:
                self._consume_time(self.clock() if now is None else now)
                self._persist()

    def _poll_command(self) -> None:
        if not self.command_store:
            return
        command = self.command_store.read()
        command_id = int(command.get("id", 0))
        if command_id <= self.state.last_command_id:
            return
        self.state.last_command_id = command_id
        action = command.get("command")
        try:
            if action == "play":
                self.play()
            elif action == "pause":
                self.pause()
            elif action == "stop":
                self.stop()
        except RuntimeError as exc:
            self.events.write("command_rejected", command=action, error=str(exc))
        self._persist()

    def run_forever(self) -> None:
        if self.state.status == RunStatus.RUNNING:
            # A persisted RUNNING state means the prior owner disappeared. Never
            # assume that its app/controller actions are still coherent.
            self.processes.close_all(self.apps)
            self._cancel_controller()
            self.state.status = RunStatus.PAUSED
            self.state.blocked_reason = "Recovered after an unclean engine exit"
            self._persist()
            self.events.write("unclean_exit_recovered")
        self.events.write("engine_started")
        while not self._quit.wait(self.config.tick_seconds):
            self.tick()
