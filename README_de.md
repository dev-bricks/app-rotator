# App Rotator

[![CI](https://github.com/dev-bricks/app-rotator/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/dev-bricks/app-rotator/actions/workflows/tests.yml)
[![Tests](https://img.shields.io/badge/tests-41%20passed-brightgreen.svg)](https://github.com/dev-bricks/app-rotator)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Plattform](https://img.shields.io/badge/Plattform-Windows-blue.svg)](https://github.com/dev-bricks/app-rotator)
[![Lizenz](https://img.shields.io/badge/Lizenz-MIT-green.svg)](LICENSE)
[![Sicherheitsrichtlinie](https://img.shields.io/badge/Sicherheit-Policy-blue.svg)](SECURITY.md)
[![Datenschutz](https://img.shields.io/badge/Datenschutz-100%25%20Lokal--First-success.svg)](SECURITY.md)
[![Organisation](https://img.shields.io/badge/Org-dev--bricks-orange.svg)](https://github.com/dev-bricks)
[![Ökosystem](https://img.shields.io/badge/Ökosystem-open--bricks-blueviolet.svg)](https://github.com/open-bricks)
[![LLM-Kontext](https://img.shields.io/badge/llms.txt-Bereit-blue.svg)](llms.txt)

> **Schnellnavigation:** [English README](README.md) • [Deutsche Version](README_de.md) • [Sicherheitsrichtlinie / Security](SECURITY.md) • [Changelog](CHANGELOG.md) • [LLM-Kontext](llms.txt)

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

Unter Windows erstellt die unterstützte Installation pro Benutzer zusätzlich
eine systemunabhängige Desktop-Verknüpfung. Sie löst den tatsächlichen
Windows-Desktop-Spezialordner auf und installiert die Laufzeit unter
`%LOCALAPPDATA%`; dadurch hängt der Start weder von einem Repo- noch von einem
OneDrive-Pfad ab:

```powershell
.\scripts\install-desktop-shortcut.ps1
```

In den Tray-Einstellungen sind An/Aus, Dry-Run, Provider-Reihenfolge,
Laufzeiten, Abstände, Zykluspause, Gesamtstopp, Codex-Controller und
Reaktivierungsabstand einstellbar. Alle sichtbaren Zeitwerte werden dort in
**Minuten** angezeigt und eingegeben; intern speichert die Engine weiterhin
Sekunden. Nach dem Speichern muss die Tray-App neu gestartet werden.

Die Provider-Verwaltung enthält automatisch Codex Desktop, Claude Desktop und
Antigravity. Jeder Eintrag besitzt die Checkbox **Enabled / in rotation**. Nicht
angehakte Provider bleiben vollständig gespeichert, werden aber im Loop und bei
dessen Prozessoperationen übersprungen. Weitere Provider lassen sich manuell
anlegen und alle Einträge lassen sich sortieren. Die erkannten Basiseinträge
bleiben registriert und werden bei Bedarf lediglich abgewählt.

Ältere Konfigurationen werden atomar auf Schema-Version 2 migriert. Bestehende
Provider, Reihenfolge und Aktivierungszustände bleiben erhalten. Fehlende
Basisprovider werden deaktiviert ergänzt, damit die Migration einen bestehenden
realen Loop nicht unbemerkt erweitert.

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
