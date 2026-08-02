# App Rotator

App Rotator is a small Windows tray application that time-slices resource-heavy desktop apps. It starts exactly one configured app, closes it after its allotted time, waits with all managed apps closed, and continues in configured order.

The shipped configuration is deliberately **disabled and dry-run**. It logs intended actions but cannot launch or terminate anything until both settings are changed explicitly.

## Behavior

- **Play from stopped:** closes all configured, path-restricted desktop processes and starts at index 0 with a fresh timer.
- **Pause:** closes every configured app, cancels pending Codex reactivation work, and retains phase, index, and remaining time.
- **Play from paused:** resumes that exact phase and remaining time. An app phase launches the current app fresh.
- **Stop / Aus:** closes all apps, calls the external controller's `cancel`, and resets the loop to index 0.
- **Automatic stop:** `overall_stop_seconds` performs the same safe Stop operation after the configured active runtime. Time spent manually paused does not count.
- **Cycle:** app phase -> all-closed inter-app gap -> next app -> all-closed cycle pause -> index 0.

State is saved atomically in `%LOCALAPPDATA%\AppRotator\state.json`; control commands use an atomic mailbox and events are appended to `events.jsonl`. A file lock permits only one `run` or `tray` instance.

## Install and initialize

```powershell
$env:PYTHONIOENCODING = "utf-8"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\app-rotator.exe config-init
.\.venv\Scripts\app-rotator.exe config-validate
.\.venv\Scripts\app-rotator.exe tray
```

On Windows, the supported per-user installation also creates a system-independent
desktop shortcut. It resolves the real Desktop special folder and installs the
runtime below `%LOCALAPPDATA%`, so the shortcut does not depend on a repository or
OneDrive path:

```powershell
.\scripts\install-desktop-shortcut.ps1
```

Tray Settings exposes the on/off switch, dry-run, provider order and durations,
gaps, cycle pause, total runtime, Codex controller, and reactivation spacing.
Every user-facing time value in Settings is entered and displayed in **minutes**;
the persisted engine format remains seconds. Restart the tray process after
saving settings.

The provider list contains built-in entries for Codex Desktop, Claude Desktop,
and Antigravity. Each provider has an **Enabled / in rotation** checkbox.
Unchecked providers remain saved but are omitted from the loop and its process
operations. Providers can be added manually, reordered, and removed; built-in
entries stay registered and can instead be unchecked.

Older configuration files are migrated atomically to schema version 2. Existing
provider settings and order are retained. Missing built-in providers are added
unchecked so migration cannot silently expand an existing live rotation.

CLI:

```text
app-rotator run
app-rotator tray
app-rotator status
app-rotator play | pause | stop
app-rotator config-init [--force]
app-rotator config-validate
```

## Safe process selection

An app must define a process name **and exactly one path restriction** (`path_exact` or `path_contains`). A process without a readable executable path is never matched. The Codex default matches `ChatGPT.exe` only below `WindowsApps\OpenAI.Codex_`; npm/CLI `codex.exe` is therefore outside its kill scope. Claude is similarly restricted to `WindowsApps\Claude_`, and Antigravity uses an exact executable path.

AppX applications launch through:

```text
explorer.exe shell:AppsFolder\<AUMID>
```

Default AUMIDs are `OpenAI.Codex_2p2nqsd0c76g0!App` and `Claude_pzs8sxrjxfjjc!Claude`.

## Codex safe-start contract

App Rotator never reads or edits `automation.toml`. It delegates provider-native automation control to one explicitly configured executable:

```text
controller.exe pause-all
controller.exe stagger-resume --interval-seconds 60
controller.exe cancel
```

For a Codex app phase it calls `pause-all`, launches Codex, then asks the controller to perform staggered reactivation. Pause, Stop, phase exit, and Quit cancel outstanding reactivation. When the controller is absent, `missing_behavior` is fail-closed `block` by default (rotation pauses with a visible state reason); `skip` explicitly skips the Codex stage. Dry-run records the contract without requiring a controller.

The external controller is intentionally not bundled: its implementation must use Codex's native automation management and retain its own rollback/readback guarantees.

## Tests

```powershell
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

Tests use fake processes and a mock controller. They do not start or kill desktop apps.
