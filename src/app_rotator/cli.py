from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import ConfigError, data_dir, default_config, load_config, save_config
from .controller import CodexAutomationController
from .engine import RotationEngine
from .processes import ProcessManager
from .runtime import CommandStore, EventLog, InstanceLock, StateStore


def paths(config_path: Path | None = None) -> dict[str, Path]:
    root = data_dir()
    return {
        "config": config_path or root / "config.json",
        "state": root / "state.json",
        "events": root / "events.jsonl",
        "commands": root / "command.json",
        "lock": root / "app-rotator.lock",
    }


def build_engine(config_path: Path | None = None) -> tuple[RotationEngine, dict[str, Path]]:
    target = paths(config_path)
    config = load_config(target["config"])
    events = EventLog(target["events"])
    processes = ProcessManager(
        events,
        dry_run=config.dry_run,
        terminate_timeout=config.terminate_timeout_seconds,
    )
    controller = CodexAutomationController(
        config.codex_controller,
        events,
        dry_run=config.dry_run,
    )
    engine = RotationEngine(
        config,
        processes,
        controller,
        StateStore(target["state"]),
        events,
        CommandStore(target["commands"]),
    )
    return engine, target


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="app-rotator")
    result.add_argument("--config", type=Path, help="Override config path")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("run", help="Run the headless rotation engine")
    commands.add_parser("tray", help="Run the Windows tray UI")
    commands.add_parser("status", help="Print persisted runtime state")
    commands.add_parser("play", help="Send Play/Start to the running instance")
    commands.add_parser("pause", help="Send Pause to the running instance")
    commands.add_parser("stop", help="Send Stop/Aus to the running instance")
    init = commands.add_parser("config-init", help="Write a safe disabled dry-run config")
    init.add_argument("--force", action="store_true")
    commands.add_parser("config-validate", help="Validate configuration")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    target = paths(args.config)
    try:
        if args.command == "config-init":
            if target["config"].exists() and not args.force:
                print(f"Refusing to overwrite existing config: {target['config']}", file=sys.stderr)
                return 2
            save_config(target["config"], default_config())
            print(target["config"])
            return 0
        if args.command == "config-validate":
            load_config(target["config"])
            print("valid")
            return 0
        if args.command == "status":
            state = StateStore(target["state"]).load()
            print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
            return 0
        if args.command in {"play", "pause", "stop"}:
            command_id = CommandStore(target["commands"]).send(args.command)
            print(json.dumps({"sent": args.command, "command_id": command_id}))
            return 0
        engine, target = build_engine(args.config)
        with InstanceLock(target["lock"]):
            if args.command == "run":
                engine.run_forever()
            else:
                from .tray import TrayApp

                TrayApp(engine, target["config"]).run()
        return 0
    except (ConfigError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
