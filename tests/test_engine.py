from pathlib import Path

from app_rotator.config import AppSpec, CodexControllerConfig, RotatorConfig
from app_rotator.engine import RotationEngine
from app_rotator.runtime import Phase, RunStatus, RuntimeState, StateStore


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class Processes:
    def __init__(self):
        self.actions = []

    def close_all(self, apps):
        self.actions.append(("close_all", [app.id for app in apps]))

    def close_app(self, app):
        self.actions.append(("close", app.id))

    def launch(self, app):
        self.actions.append(("launch", app.id))


class Controller:
    dry_run = True

    def __init__(self):
        self.actions = []

    def available(self):
        return True

    def pause_all(self):
        self.actions.append("pause-all")

    def stagger_resume(self):
        self.actions.append("stagger-resume")

    def cancel(self):
        self.actions.append("cancel")


class MissingController(Controller):
    dry_run = False

    def available(self):
        return False


class Events:
    def write(self, *_args, **_kwargs):
        pass


def make_engine(tmp_path: Path, *, overall=100):
    apps = [
        AppSpec(
            "codex",
            "Codex",
            10,
            "ChatGPT.exe",
            path_contains="Codex",
            launch_type="appsfolder",
            launch_value="x",
            codex_safe_start=True,
        ),
        AppSpec(
            "claude",
            "Claude",
            20,
            "Claude.exe",
            path_contains="Claude",
            launch_type="appsfolder",
            launch_value="y",
        ),
    ]
    config = RotatorConfig(
        enabled=True,
        dry_run=True,
        inter_app_gap_seconds=3,
        cycle_pause_seconds=5,
        overall_stop_seconds=overall,
        apps=apps,
        codex_controller=CodexControllerConfig(),
    )
    clock = Clock()
    processes = Processes()
    controller = Controller()
    engine = RotationEngine(
        config,
        processes,
        controller,
        StateStore(tmp_path / "state.json"),
        Events(),
        clock=clock,
    )
    return engine, clock, processes, controller


def test_start_pause_resume_stop_state_machine(tmp_path):
    engine, clock, processes, controller = make_engine(tmp_path)
    engine.play()
    assert engine.state.status == RunStatus.RUNNING
    assert engine.state.app_index == 0
    assert controller.actions[-2:] == ["pause-all", "stagger-resume"]

    clock.now = 4
    engine.tick()
    engine.pause()
    assert engine.state.status == RunStatus.PAUSED
    assert engine.state.remaining_seconds == 6

    engine.play()
    assert engine.state.remaining_seconds == 6
    assert processes.actions[-1] == ("launch", "codex")

    engine.stop()
    assert engine.state.status == RunStatus.STOPPED
    assert engine.state.app_index == 0
    assert engine.state.remaining_seconds == 0
    assert controller.actions[-1] == "cancel"

    engine.play()
    assert engine.state.remaining_seconds == 10


def test_timer_advances_through_gap_and_cycle_pause(tmp_path):
    engine, clock, processes, _ = make_engine(tmp_path)
    engine.play()
    clock.now = 10
    engine.tick()
    assert engine.state.phase == Phase.GAP
    assert engine.state.remaining_seconds == 3
    assert processes.actions[-1] == ("close_all", ["codex", "claude"])
    clock.now = 13
    engine.tick()
    assert engine.state.phase == Phase.APP
    assert engine.state.app_index == 1
    clock.now = 33
    engine.tick()
    assert engine.state.phase == Phase.CYCLE_PAUSE
    clock.now = 38
    engine.tick()
    assert engine.state.phase == Phase.APP
    assert engine.state.app_index == 0


def test_overall_timer_performs_software_stop_and_cancel(tmp_path):
    engine, clock, processes, controller = make_engine(tmp_path, overall=7)
    engine.play()
    clock.now = 7
    engine.tick()
    assert engine.state.status == RunStatus.STOPPED
    assert processes.actions[-1][0] == "close_all"
    assert controller.actions[-1] == "cancel"


def test_missing_codex_controller_blocks_fail_closed(tmp_path):
    engine, _, processes, _ = make_engine(tmp_path)
    engine.controller = MissingController()
    engine.play()
    assert engine.state.status == RunStatus.PAUSED
    assert engine.state.blocked_reason == "Codex controller unavailable"
    assert processes.actions[-1][0] == "close_all"


def test_missing_codex_controller_can_explicitly_skip_stage(tmp_path):
    engine, _, _, _ = make_engine(tmp_path)
    engine.controller = MissingController()
    engine.config.codex_controller.missing_behavior = "skip"
    engine.play()
    assert engine.state.status == RunStatus.RUNNING
    assert engine.state.phase == Phase.GAP
    assert engine.state.app_index == 0


def test_unclean_running_state_recovers_to_paused(tmp_path):
    engine, _, processes, controller = make_engine(tmp_path)
    engine.play()
    engine._quit.set()
    engine.run_forever()
    assert engine.state.status == RunStatus.PAUSED
    assert "unclean" in engine.state.blocked_reason
    assert processes.actions[-1][0] == "close_all"
    assert controller.actions[-1] == "cancel"


def test_invalid_persisted_app_index_is_reset(tmp_path):
    state_store = StateStore(tmp_path / "state.json")
    state_store.save(
        RuntimeState(
            status=RunStatus.PAUSED,
            phase=Phase.APP,
            app_index=99,
            remaining_seconds=10,
        )
    )
    engine, _, _, _ = make_engine(tmp_path)
    assert engine.state.status == RunStatus.STOPPED
    assert engine.state.app_index == 0
    assert "configuration change" in (engine.state.blocked_reason or "")
