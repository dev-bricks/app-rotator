from app_rotator.config import AppSpec
from app_rotator.processes import process_matches


def app(**overrides):
    values = {
        "id": "codex",
        "label": "Codex",
        "duration_seconds": 10,
        "process_name": "ChatGPT.exe",
        "path_contains": r"WindowsApps\OpenAI.Codex_",
        "launch_type": "appsfolder",
        "launch_value": "AUMID",
    }
    values.update(overrides)
    return AppSpec(**values)


def test_process_match_requires_name_and_restricted_path():
    spec = app()
    executable = r"C:\Program Files\WindowsApps\OpenAI.Codex_1\app\ChatGPT.exe"
    assert process_matches(spec, "ChatGPT.exe", executable)
    assert not process_matches(spec, "codex.exe", r"C:\Users\x\npm\codex.exe")
    assert not process_matches(spec, "ChatGPT.exe", r"C:\Tools\ChatGPT.exe")
    assert not process_matches(spec, "ChatGPT.exe", None)


def test_exact_path_rejects_same_name_elsewhere():
    spec = app(
        id="agy",
        process_name="Antigravity.exe",
        path_contains=None,
        path_exact=r"C:\Apps\Antigravity.exe",
        launch_type="executable",
        launch_value=r"C:\Apps\Antigravity.exe",
    )
    assert process_matches(spec, "Antigravity.exe", r"C:\Apps\Antigravity.exe")
    assert not process_matches(spec, "Antigravity.exe", r"D:\Apps\Antigravity.exe")
