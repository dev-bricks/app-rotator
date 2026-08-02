from __future__ import annotations

import json
import threading
import tkinter as tk
from importlib.resources import files
from tkinter import messagebox, ttk

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from .config import RotatorConfig, load_config, save_config
from .engine import RotationEngine


def create_icon() -> Image.Image:
    try:
        icon_path = files("app_rotator").joinpath("assets/app-rotator-icon.png")
        with icon_path.open("rb") as handle:
            return Image.open(handle).convert("RGBA")
    except (FileNotFoundError, OSError):
        # Keep the tray usable even when a broken third-party packager omits assets.
        pass
    image = Image.new("RGB", (64, 64), "#172033")
    draw = ImageDraw.Draw(image)
    draw.arc((10, 10, 54, 54), 35, 300, fill="#63d2ff", width=7)
    draw.polygon([(49, 9), (58, 27), (39, 25)], fill="#63d2ff")
    return image


class TrayApp:
    def __init__(self, engine: RotationEngine, config_path):
        self.engine = engine
        self.config_path = config_path
        self.icon = Icon("app-rotator", create_icon(), "App Rotator", self._menu())
        self._thread = threading.Thread(target=engine.run_forever, daemon=True)

    def _menu(self) -> Menu:
        return Menu(
            MenuItem(lambda _item: self._title(), None, enabled=False),
            MenuItem("Play / Start", self._play),
            MenuItem("Pause", self._pause),
            MenuItem("Stop / Aus", self._stop),
            Menu.SEPARATOR,
            MenuItem("Settings", self._settings),
            MenuItem("Quit", self._quit),
        )

    def _title(self) -> str:
        state = self.engine.state
        app = self.engine.apps[state.app_index].label if self.engine.apps else "-"
        return f"{state.status.value}: {app} ({state.remaining_seconds:.0f}s)"

    def _refresh(self) -> None:
        self.icon.menu = self._menu()
        self.icon.update_menu()

    def _play(self, *_args) -> None:
        try:
            self.engine.play()
        except RuntimeError as exc:
            self.icon.notify(str(exc), "App Rotator")
        self._refresh()

    def _pause(self, *_args) -> None:
        self.engine.pause()
        self._refresh()

    def _stop(self, *_args) -> None:
        self.engine.stop()
        self._refresh()

    def _quit(self, *_args) -> None:
        self.engine.quit()
        self.icon.stop()

    def _settings(self, *_args) -> None:
        threading.Thread(target=self._settings_window, daemon=True).start()

    def _settings_window(self) -> None:
        config = load_config(self.config_path)
        root = tk.Tk()
        root.title("App Rotator Settings")
        root.geometry("780x720")
        frame = ttk.Frame(root, padding=12)
        frame.pack(fill="both", expand=True)
        enabled = tk.BooleanVar(value=config.enabled)
        dry_run = tk.BooleanVar(value=config.dry_run)
        values = {
            "inter_app_gap_seconds": tk.StringVar(value=str(config.inter_app_gap_seconds)),
            "cycle_pause_seconds": tk.StringVar(value=str(config.cycle_pause_seconds)),
            "overall_stop_seconds": tk.StringVar(value=str(config.overall_stop_seconds)),
            "reactivation_interval_seconds": tk.StringVar(
                value=str(config.codex_controller.reactivation_interval_seconds)
            ),
            "controller": tk.StringVar(value=config.codex_controller.executable),
            "missing": tk.StringVar(value=config.codex_controller.missing_behavior),
        }
        ttk.Checkbutton(frame, text="Rotation enabled", variable=enabled).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Checkbutton(
            frame,
            text="Dry-run (no launches or kills)",
            variable=dry_run,
        ).grid(row=1, column=0, sticky="w")
        labels = [
            ("Gap between apps (seconds)", "inter_app_gap_seconds"),
            ("Pause after full cycle (seconds)", "cycle_pause_seconds"),
            ("Automatic overall stop (seconds)", "overall_stop_seconds"),
            ("Codex reactivation spacing (seconds)", "reactivation_interval_seconds"),
            ("External Codex controller executable", "controller"),
        ]
        row = 2
        for label, key in labels:
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=(8, 0))
            ttk.Entry(frame, textvariable=values[key], width=72).grid(
                row=row + 1, column=0, sticky="ew"
            )
            row += 2
        ttk.Label(frame, text="If Codex controller is missing").grid(
            row=row, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Combobox(
            frame,
            textvariable=values["missing"],
            values=("block", "skip"),
            state="readonly",
        ).grid(row=row + 1, column=0, sticky="w")
        row += 2
        ttk.Label(frame, text="Apps JSON (array order is rotation order)").grid(
            row=row, column=0, sticky="w", pady=(8, 0)
        )
        text = tk.Text(frame, height=19, wrap="none")
        text.grid(row=row + 1, column=0, sticky="nsew")
        apps_payload = [
            {field: getattr(app, field) for field in app.__dataclass_fields__}
            for app in config.apps
        ]
        text.insert(
            "1.0",
            json.dumps(apps_payload, ensure_ascii=False, indent=2),
        )
        frame.rowconfigure(row + 1, weight=1)
        frame.columnconfigure(0, weight=1)

        def save() -> None:
            try:
                raw_apps = json.loads(text.get("1.0", "end"))
                raw = config.to_dict()
                raw.update(
                    enabled=enabled.get(),
                    dry_run=dry_run.get(),
                    inter_app_gap_seconds=float(values["inter_app_gap_seconds"].get()),
                    cycle_pause_seconds=float(values["cycle_pause_seconds"].get()),
                    overall_stop_seconds=float(values["overall_stop_seconds"].get()),
                    apps=raw_apps,
                )
                raw["codex_controller"].update(
                    executable=values["controller"].get(),
                    reactivation_interval_seconds=float(values["reactivation_interval_seconds"].get()),
                    missing_behavior=values["missing"].get(),
                )
                updated = RotatorConfig.from_dict(raw)
                save_config(self.config_path, updated)
                messagebox.showinfo(
                    "App Rotator",
                    "Saved. Restart the tray app to load the new configuration.",
                )
                root.destroy()
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                messagebox.showerror("Invalid settings", str(exc))

        ttk.Button(frame, text="Save", command=save).grid(
            row=row + 2, column=0, sticky="e", pady=(10, 0)
        )
        root.mainloop()

    def run(self) -> None:
        self._thread.start()
        self.icon.run()
