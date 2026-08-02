from pathlib import Path
from types import SimpleNamespace

from app_rotator.config import CodexControllerConfig
from app_rotator.controller import CodexAutomationController, ControllerError


class Events:
    def write(self, *_args, **_kwargs):
        pass


def test_mock_controller_contract(tmp_path: Path):
    executable = tmp_path / "controller.exe"
    executable.write_text("mock", encoding="utf-8")
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stderr="")

    config = CodexControllerConfig(str(executable), 60, "block", 5)
    controller = CodexAutomationController(config, Events(), dry_run=False, runner=runner)
    controller.pause_all()
    controller.stagger_resume()
    controller.cancel()
    assert [call[0][1] for call in calls] == ["pause-all", "stagger-resume", "cancel"]
    assert calls[1][0][-2:] == ["--interval-seconds", "60"]


def test_controller_failure_is_fail_closed(tmp_path: Path):
    executable = tmp_path / "controller.exe"
    executable.write_text("mock", encoding="utf-8")

    def runner(*_args, **_kwargs):
        return SimpleNamespace(returncode=4, stderr="provider refused")

    controller = CodexAutomationController(
        CodexControllerConfig(str(executable)), Events(), dry_run=False, runner=runner
    )
    try:
        controller.pause_all()
    except ControllerError as exc:
        assert "provider refused" in str(exc)
    else:
        raise AssertionError("ControllerError expected")
