# App Rotator

App Rotator ist eine kleine Windows-Tray-App, die ressourcenintensive Desktop-Apps zeitlich nacheinander betreibt. Sie startet genau eine konfigurierte App, beendet sie nach ihrer Laufzeit und wartet zwischen den Stufen mit vollständig geschlossenen verwalteten Apps.

Die ausgelieferte Konfiguration ist absichtlich **deaktiviert und im Dry-Run**. Erst wenn beide Einstellungen bewusst geändert wurden, können echte Starts oder Prozessbeendigungen stattfinden.

## Zustandslogik

- **Play aus Stopped:** beendet alle konfigurierten, pfadbeschränkten Desktop-Prozesse und beginnt frisch bei Index 0.
- **Pause:** beendet alle Apps, verwirft ausstehende Codex-Reaktivierungen und bewahrt Phase, Index und Restzeit.
- **Play aus Paused:** setzt genau dort fort. In einer App-Phase wird die aktuelle App frisch gestartet.
- **Stop / Aus:** beendet alle Apps, ruft beim externen Controller `cancel` auf und setzt den Loop auf Index 0 zurück.
- **Automatischer Stop:** `overall_stop_seconds` löst nach der aktiven Gesamtlaufzeit denselben sicheren Stop aus. Manuelle Pausen zählen nicht mit.
- **Loop:** App -> Abstand mit allen Apps geschlossen -> nächste App -> Zykluspause mit allen Apps geschlossen -> Index 0.

Der Zustand liegt atomar unter `%LOCALAPPDATA%\AppRotator\state.json`, Befehle laufen über eine atomare Mailbox, Ereignisse werden in `events.jsonl` protokolliert. Ein File-Lock erlaubt nur eine laufende `run`- oder `tray`-Instanz.

## Installation

```powershell
$env:PYTHONIOENCODING = "utf-8"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\app-rotator.exe config-init
.\.venv\Scripts\app-rotator.exe config-validate
.\.venv\Scripts\app-rotator.exe tray
```

In den Tray-Einstellungen sind An/Aus, Dry-Run, App-Reihenfolge, Laufzeiten, Abstände, Zykluspause, Gesamtstopp, Codex-Controller und Reaktivierungsabstand einstellbar. Nach dem Speichern muss die Tray-App neu gestartet werden.

## Sichere Prozessauswahl

Jede App benötigt Prozessname **und genau eine Pfadbeschränkung** (`path_exact` oder `path_contains`). Ohne lesbaren Exe-Pfad gibt es keinen Treffer. Codex trifft standardmäßig ausschließlich `ChatGPT.exe` unter `WindowsApps\OpenAI.Codex_`; die Codex-CLI beziehungsweise npm-`codex.exe` bleibt außerhalb des Beendigungsbereichs. Claude ist auf `WindowsApps\Claude_` beschränkt, Antigravity auf den exakten Exe-Pfad.

AppX-Apps starten über `explorer.exe shell:AppsFolder\<AUMID>`. Voreingestellt sind `OpenAI.Codex_2p2nqsd0c76g0!App` und `Claude_pzs8sxrjxfjjc!Claude`.

## Codex-Safe-Start

App Rotator liest oder bearbeitet niemals `automation.toml`. Stattdessen gilt ein fail-closed Vertrag mit einem explizit konfigurierten externen Controller:

```text
controller.exe pause-all
controller.exe stagger-resume --interval-seconds 60
controller.exe cancel
```

Vor einer Codex-Stufe werden alle Automatisierungen pausiert, danach startet Codex und der Controller reaktiviert gestaffelt. Pause, Stop, Phasenende und Quit brechen offene Reaktivierungen ab. Fehlt der Controller, pausiert `block` standardmäßig den Loop mit Begründung; `skip` überspringt die Codex-Stufe ausdrücklich. Im Dry-Run wird der Vertrag nur protokolliert.

Der Controller ist bewusst nicht Teil dieses Repos. Er muss die native Codex-Automatisierungsverwaltung sowie eigene Readback- und Rollback-Garantien verwenden.

## Tests

```powershell
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

Die Tests verwenden Fake-Prozesse und einen Mock-Controller. Sie starten oder beenden keine Desktop-Apps.
