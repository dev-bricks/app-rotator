# Contributing to App Rotator / Mitwirken an App Rotator

[English](#english) | [Deutsch](#deutsch)

---

<a id="english"></a>
## English

Thank you for your interest in contributing to **App Rotator** (`dev-bricks/app-rotator`), a configurable, fail-closed Windows system tray rotator that time-slices resource-heavy desktop applications (Codex Desktop, Claude Desktop, Antigravity IDE) to eliminate VRAM exhaustion, GPU contention, and background runaway execution.

### 1. Architectural Principles & 10 Governance Invariants

All contributions must strictly adhere to our core architectural invariants:

1. **100% Local-First Privacy (`INV-LOCAL-01`)**: Zero outbound telemetry, network tracking, analytics, or mandatory cloud infrastructure. All data and configuration remain exclusively within local `%LOCALAPPDATA%\AppRotator`.
2. **Unprivileged Execution (`INV-UNPRIV-02`)**: Pure `RunAsInvoker` user mode execution below `%LOCALAPPDATA%`. No UAC elevation, administrator credentials, or background Windows services are required or permitted.
3. **Fail-Closed & Dry-Run by Default (`INV-DRYRUN-03`)**: Default configuration is inert (`enabled: false`, `dry_run: true`). Actions execute only after explicit user configuration.
4. **Strict Path-Restricted Process Scoping (`INV-SCOPING-04`)**: Process targeting requires exact executable name AND strict path validation (`path_exact` or `path_contains`) to eliminate collision with unrelated binaries.
5. **Atomic Persistence & Mailbox IPC (`INV-ATOMIC-05`)**: State and mailbox writes execute via temporary file creation followed by atomic replacement (`os.replace`).
6. **Provider Delegation Contract (`INV-DELEGATION-06`)**: External providers are orchestrated exclusively through external CLI contracts (`pause-all`, `stagger-resume`, `cancel`). Direct alteration of provider-internal configuration files is strictly forbidden.
7. **Single-Instance Mutex Lock (`INV-LOCKFILE-07`)**: Strict single-instance file lock protection (`app-rotator.lock`) prevents duplicate engine or system tray instances.
8. **Non-Invasive AppX Shell Activation (`INV-AUMID-08`)**: Modern Windows Store / AppX application launches use fixed parameter vectors (`explorer.exe shell:AppsFolder\<AUMID>`) without shell invocation.
9. **Cloud-Sync & Conflict Resilience (`INV-SYNC-09`)**: Runtime state resides strictly outside cloud-synchronized directories (e.g. OneDrive); `.gitignore` enforces multi-host sync and lock protection.
10. **48h Security Response SLA & 5-Day Triage (`INV-SLA-10`)**: Binding commitment to triage security notices within 48 hours and provide initial assessment within 5 business days via `security@dev-bricks.org`, `security@open-bricks.org`, and `support@lukasgeiger.com`.

### 2. Plan D Local Development Workflow

In accordance with our cross-system architecture (Plan D), the local git repository at `C:\_Local_DEV\repos\app-rotator` serves as the authoritative **Source of Truth**. Development, testing, and commits must take place exclusively in the canonical local clone. Cloud mirrors (e.g. OneDrive) serve solely as gitless read projections.

```bash
# Navigate to the canonical local clone
cd C:\_Local_DEV\repos\app-rotator

# Verify git status and branch
git status
git branch --show-current

# Install editable package and test dependencies
pip install -e ".[dev]"

# Run full test suite with isolated basetemp
pytest

# Verify code formatting and linting
ruff check .
```

### 3. Version Freeze Discipline (`T-20260920-167562623`)

App Rotator operates under strict version-freeze discipline. The version identifier (`0.2.3` in `pyproject.toml`, `src/app_rotator/__init__.py`, and manifests) must not be arbitrarily incremented. All improvements, bug fixes, and hygiene adjustments are documented under `## [Unreleased]` in `CHANGELOG.md`.

### 4. Quality Gates

Before submitting a pull request or pushing commits, verify all local quality gates:

1. `pytest`: 100% green test execution across all unit, contract, and regression suites.
2. `ruff check .`: Zero lint errors.
3. `python -m compileall -q src tests`: Zero bytecode compilation errors.
4. `git diff --check`: Zero whitespace or line-ending anomalies.
5. `git diff -G"version = "`: Zero unauthorized version modifications.

### 5. Statutory Notice (§ 521 BGB) & Zero-Copyleft on User Data

This software is provided free of charge under the permissive MIT License. In accordance with German statutory law (**§ 521 BGB** — *Haftung des Schenkers*), liability for defects in quality and title is strictly limited to intentional misconduct (*Vorsatz*) and gross negligence (*grobe Fahrlässigkeit*).

**Zero-Copyleft Guarantee:** Utilizing App Rotator to time-slice or serialize local applications does **not** subject user workloads, model weights, prompts, or codebases to any viral copyleft licensing obligations.

---

<a id="deutsch"></a>
## Deutsch

Vielen Dank für Ihr Interesse an einer Mitarbeit an **App Rotator** (`dev-bricks/app-rotator`), einem konfigurierbaren, Fail-Closed Windows-Tray-Rotator, der ressourcenintensive Desktop-Anwendungen (Codex Desktop, Claude Desktop, Antigravity IDE) deterministisch durch Time-Slicing steuert, um VRAM-Erschöpfung, GPU-Konflikte und unkontrollierte Hintergrundprozesse zu eliminieren.

### 1. Architektur-Prinzipien & 10 Governance-Invarianten

Alle Beiträge müssen unsere verbindlichen Kern-Invarianten strikt einhalten:

1. **100% Local-First Privatsphäre (`INV-LOCAL-01`)**: Null ausgehende Telemetrie, kein Tracking, keine Analytik und keine Cloud-Abhängigkeit. Alle Daten und Konfigurationen verbleiben ausschließlich lokal unter `%LOCALAPPDATA%\AppRotator`.
2. **Unprivilegierte Ausführung (`INV-UNPRIV-02`)**: Reine `RunAsInvoker`-Benutzermodus-Ausführung unter `%LOCALAPPDATA%`. Keine UAC-Elevation, keine Administratorrechte und keine permanenten Windows-Dienste.
3. **Fail-Closed & Standardmäßiger Dry-Run (`INV-DRYRUN-03`)**: Standardkonfiguration ist inaktiv (`enabled: false`, `dry_run: true`). Aktionen werden erst nach expliziter Benutzerkonfiguration ausgeführt.
4. **Strikte pfadgebundene Prozessauswahl (`INV-SCOPING-04`)**: Prozessidentifikation erfordert zwingend den exakten Dateinamen UND eine strikte Pfadvalidierung (`path_exact` oder `path_contains`), um Verwechslungen mit gleichnamigen Binärdateien auszuschließen.
5. **Atomare Persistenz & Mailbox-IPC (`INV-ATOMIC-05`)**: Zustands- und Mailbox-Schreibvorgänge erfolgen über temporäre Dateien mit anschließendem atomaren Ersetzen (`os.replace`).
6. **Provider-Delegationsvertrag (`INV-DELEGATION-06`)**: Externe Provider werden ausschließlich über CLI-Schnittstellen gesteuert (`pause-all`, `stagger-resume`, `cancel`). Direkte Eingriffe in interne Provider-Dateien sind untersagt.
7. **Single-Instance Mutex-Dateisperre (`INV-LOCKFILE-07`)**: Eine strikte Datei-Sperre (`app-rotator.lock`) verhindert parallele Instanzen von Engine oder System-Tray.
8. **Nicht-invasive AppX-Shell-Aktivierung (`INV-AUMID-08`)**: Moderne Windows-Store-/AppX-Anwendungen werden über feste Parametervektoren (`explorer.exe shell:AppsFolder\<AUMID>`) ohne Shell-Ausführung gestartet.
9. **Cloud-Sync- & Konflikt-Resilienz (`INV-SYNC-09`)**: Laufzeitdaten liegen strikt außerhalb synchronisierter Cloud-Ordner; `.gitignore` schützt vor Multi-Host- und Lock-Konflikten.
10. **48h Sicherheits-SLA & 5-Tage-Triage (`INV-SLA-10`)**: Verbindliche Zusage zur Triage von Sicherheitsmeldungen innerhalb von 48 Stunden und Erstbewertung innerhalb von 5 Werktagen via `security@dev-bricks.org`, `security@open-bricks.org` und `support@lukasgeiger.com`.

### 2. Plan D Lokaler Entwicklungs-Workflow

Gemäß unserer systemweiten Architektur (Plan D) ist das lokale Git-Repository unter `C:\_Local_DEV\repos\app-rotator` die verbindliche **Source of Truth**. Entwicklung, Tests und Commits finden ausschließlich im kanonischen Klon statt. Cloud-Spiegel (z. B. OneDrive) dienen rein als gitlose Leseprojektionen.

```bash
# In den kanonischen lokalen Klon wechseln
cd C:\_Local_DEV\repos\app-rotator

# Git-Status und Branch prüfen
git status
git branch --show-current

# Editierbares Paket und Entwicklerabhängigkeiten installieren
pip install -e ".[dev]"

# Vollständige Testsuite mit isoliertem basetemp ausführen
pytest

# Code-Formatierung und Linter prüfen
ruff check .
```

### 3. Version-Freeze-Disziplin (`T-20260920-167562623`)

App Rotator unterliegt einer strikten Version-Freeze-Disziplin. Die Versionsnummer (`0.2.3` in `pyproject.toml`, `src/app_rotator/__init__.py` und Manifesten) darf nicht willkürlich erhöht werden. Sämtliche Verbesserungen, Fehlerbehebungen und Hygieneanpassungen werden unter `## [Unreleased]` in `CHANGELOG.md` dokumentiert.

### 4. Quality Gates

Vor dem Einreichen von Beiträgen oder Pushes müssen alle lokalen Quality Gates erfolgreich absolviert werden:

1. `pytest`: 100% grüne Testergebnisse über alle Testsuiten.
2. `ruff check .`: Null Linter-Warnungen oder -Fehler.
3. `python -m compileall -q src tests`: Fehlerfreie Bytecode-Kompilierung.
4. `git diff --check`: Keine Whitespace- oder Zeilenende-Unregelmäßigkeiten.
5. `git diff -G"version = "`: Keine unautorisierten Versionsänderungen.

### 5. Gesetzlicher Hinweis (§ 521 BGB) & Zero-Copyleft auf Nutzerdaten

Diese Software wird unentgeltlich unter der permissiven MIT-Lizenz bereitgestellt. Gemäß **§ 521 BGB** (*Haftung des Schenkers*) ist die Haftung für Sach- und Rechtsmängel auf Vorsatz und grobe Fahrlässigkeit beschränkt.

**Zero-Copyleft-Garantie:** Die Verwendung von App Rotator zum Time-Slicing von Desktop-Anwendungen unterwirft Benutzerdaten, Modellgewichte, Prompts oder Quellcode keinerlei Copyleft-Verpflichtung. Alle Benutzerdaten bleiben vollständig privat.
