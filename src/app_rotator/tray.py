from __future__ import annotations

import threading
import tkinter as tk
from importlib.resources import files
from tkinter import messagebox, ttk

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from .config import ConfigError, load_config, save_config
from .engine import RotationEngine
from .settings import ProviderDraft, apply_settings, seconds_to_minutes


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
        minutes = seconds_to_minutes(state.remaining_seconds)
        return f"{state.status.value}: {app} ({minutes} min)"

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
        root.geometry("980x860")
        frame = ttk.Frame(root, padding=12)
        frame.pack(fill="both", expand=True)
        enabled = tk.BooleanVar(value=config.enabled)
        dry_run = tk.BooleanVar(value=config.dry_run)
        values = {
            "gap_minutes": tk.StringVar(
                value=seconds_to_minutes(config.inter_app_gap_seconds)
            ),
            "cycle_pause_minutes": tk.StringVar(
                value=seconds_to_minutes(config.cycle_pause_seconds)
            ),
            "overall_stop_minutes": tk.StringVar(
                value=seconds_to_minutes(config.overall_stop_seconds)
            ),
            "reactivation_interval_minutes": tk.StringVar(
                value=seconds_to_minutes(
                    config.codex_controller.reactivation_interval_seconds
                )
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
            ("Gap between providers (minutes)", "gap_minutes"),
            ("Pause after full cycle (minutes)", "cycle_pause_minutes"),
            ("Automatic overall stop (minutes)", "overall_stop_minutes"),
            ("Codex reactivation spacing (minutes)", "reactivation_interval_minutes"),
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
        ttk.Label(
            frame,
            text="Providers (checked entries participate in the rotation)",
        ).grid(row=row, column=0, sticky="w", pady=(8, 0))

        provider_host = ttk.Frame(frame)
        provider_host.grid(row=row + 1, column=0, sticky="nsew")
        canvas = tk.Canvas(provider_host, highlightthickness=0)
        scrollbar = ttk.Scrollbar(provider_host, orient="vertical", command=canvas.yview)
        provider_frame = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=provider_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        provider_frame.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(window_id, width=event.width),
        )
        frame.rowconfigure(row + 1, weight=1)
        frame.columnconfigure(0, weight=1)
        drafts = [ProviderDraft.from_app(app) for app in config.apps]
        provider_rows: list[dict[str, tk.Variable]] = []
        protected_ids = {"codex", "claude", "antigravity"}

        def sync_drafts() -> None:
            for draft, variables in zip(drafts, provider_rows, strict=True):
                draft.id = str(variables["id"].get())
                draft.label = str(variables["label"].get())
                draft.duration_minutes = str(variables["duration"].get())
                draft.process_name = str(variables["process"].get())
                draft.path_mode = str(variables["path_mode"].get())
                draft.path_value = str(variables["path"].get())
                draft.launch_type = str(variables["launch_type"].get())
                draft.launch_value = str(variables["launch_value"].get())
                draft.launch_args_json = str(variables["launch_args"].get())
                draft.enabled = bool(variables["enabled"].get())
                draft.codex_safe_start = bool(variables["safe_start"].get())

        def move_provider(index: int, offset: int) -> None:
            sync_drafts()
            destination = index + offset
            if destination < 0 or destination >= len(drafts):
                return
            drafts[index], drafts[destination] = drafts[destination], drafts[index]
            render_providers()

        def remove_provider(index: int) -> None:
            sync_drafts()
            if drafts[index].id in protected_ids:
                messagebox.showinfo(
                    "App Rotator",
                    "Built-in providers stay registered; uncheck them to skip rotation.",
                )
                return
            drafts.pop(index)
            render_providers()

        def render_providers() -> None:
            for child in provider_frame.winfo_children():
                child.destroy()
            provider_rows.clear()
            for index, draft in enumerate(drafts):
                box = ttk.LabelFrame(provider_frame, text=f"{index + 1}. {draft.label}", padding=8)
                box.grid(row=index, column=0, sticky="ew", pady=(0, 8))
                box.columnconfigure(1, weight=1)
                box.columnconfigure(3, weight=1)
                variables: dict[str, tk.Variable] = {
                    "enabled": tk.BooleanVar(value=draft.enabled),
                    "id": tk.StringVar(value=draft.id),
                    "label": tk.StringVar(value=draft.label),
                    "duration": tk.StringVar(value=draft.duration_minutes),
                    "process": tk.StringVar(value=draft.process_name),
                    "path_mode": tk.StringVar(value=draft.path_mode),
                    "path": tk.StringVar(value=draft.path_value),
                    "launch_type": tk.StringVar(value=draft.launch_type),
                    "launch_value": tk.StringVar(value=draft.launch_value),
                    "launch_args": tk.StringVar(value=draft.launch_args_json),
                    "safe_start": tk.BooleanVar(value=draft.codex_safe_start),
                }
                provider_rows.append(variables)
                ttk.Checkbutton(
                    box,
                    text="Enabled / in rotation",
                    variable=variables["enabled"],
                ).grid(row=0, column=0, columnspan=2, sticky="w")
                ttk.Checkbutton(
                    box,
                    text="Codex safe-start contract",
                    variable=variables["safe_start"],
                ).grid(row=0, column=2, columnspan=2, sticky="w")
                fields = [
                    ("Provider ID", "id", "Label", "label"),
                    ("Duration (minutes)", "duration", "Process name", "process"),
                    ("Path match", "path_mode", "Restricted path", "path"),
                    ("Launch type", "launch_type", "Launch target", "launch_value"),
                    ("Launch arguments (JSON)", "launch_args", None, None),
                ]
                for field_row, (left_label, left_key, right_label, right_key) in enumerate(
                    fields,
                    start=1,
                ):
                    ttk.Label(box, text=left_label).grid(
                        row=field_row, column=0, sticky="w", padx=(0, 5)
                    )
                    if left_key == "path_mode":
                        left_widget = ttk.Combobox(
                            box,
                            textvariable=variables[left_key],
                            values=("contains", "exact"),
                            state="readonly",
                        )
                    elif left_key == "launch_type":
                        left_widget = ttk.Combobox(
                            box,
                            textvariable=variables[left_key],
                            values=("appsfolder", "executable", "command"),
                            state="readonly",
                        )
                    else:
                        left_widget = ttk.Entry(box, textvariable=variables[left_key])
                    left_widget.grid(row=field_row, column=1, sticky="ew", padx=(0, 10))
                    if right_label and right_key:
                        ttk.Label(box, text=right_label).grid(
                            row=field_row, column=2, sticky="w", padx=(0, 5)
                        )
                        ttk.Entry(box, textvariable=variables[right_key]).grid(
                            row=field_row, column=3, sticky="ew"
                        )
                controls = ttk.Frame(box)
                controls.grid(row=6, column=0, columnspan=4, sticky="e", pady=(5, 0))
                ttk.Button(
                    controls,
                    text="Up",
                    command=lambda current=index: move_provider(current, -1),
                ).pack(side="left", padx=2)
                ttk.Button(
                    controls,
                    text="Down",
                    command=lambda current=index: move_provider(current, 1),
                ).pack(side="left", padx=2)
                ttk.Button(
                    controls,
                    text="Remove",
                    command=lambda current=index: remove_provider(current),
                ).pack(side="left", padx=2)
            provider_frame.columnconfigure(0, weight=1)

        def add_provider() -> None:
            sync_drafts()
            drafts.append(ProviderDraft.new())
            render_providers()
            canvas.yview_moveto(1.0)

        render_providers()

        def save() -> None:
            try:
                sync_drafts()
                updated = apply_settings(
                    config,
                    enabled=enabled.get(),
                    dry_run=dry_run.get(),
                    gap_minutes=values["gap_minutes"].get(),
                    cycle_pause_minutes=values["cycle_pause_minutes"].get(),
                    overall_stop_minutes=values["overall_stop_minutes"].get(),
                    reactivation_interval_minutes=values[
                        "reactivation_interval_minutes"
                    ].get(),
                    controller_executable=values["controller"].get(),
                    missing_behavior=values["missing"].get(),
                    providers=drafts,
                )
                save_config(self.config_path, updated)
                messagebox.showinfo(
                    "App Rotator",
                    "Saved. Restart the tray app to load the new configuration.",
                )
                root.destroy()
            except (ConfigError, ValueError, TypeError) as exc:
                messagebox.showerror("Invalid settings", str(exc))

        actions = ttk.Frame(frame)
        actions.grid(row=row + 2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(actions, text="Add provider", command=add_provider).pack(side="left")
        ttk.Button(actions, text="Save", command=save).pack(side="right")
        root.mainloop()

    def run(self) -> None:
        self._thread.start()
        self.icon.run()
