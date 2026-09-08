# Sicherheitsrichtlinie / Security Policy

## Deutsch

### Sicherheitslücken melden

Wenn Sie eine Sicherheitslücke finden, melden Sie diese bitte verantwortungsvoll:

1. **Kein öffentliches Issue eröffnen**
2. **GitHub Private Vulnerability Reporting verwenden** (`Security` → `Advisories` → `New`)
3. Beschreibung, Reproduktionsschritte und potenzielle Auswirkungen angeben

Falls Private Vulnerability Reporting noch nicht aktiviert ist, kontaktieren Sie
die Maintainer direkt über GitHub oder die unten genannten E-Mail-Adressen und veröffentlichen Sie keine Details in einem
öffentlichen Issue.

### Geltungsbereich & Kern-Sicherheitsinvarianten

Dieses Tool führt sicherheitsrelevante lokale Desktop-Operationen auf Microsoft Windows aus:
- **100% Local-First & Zero Network Egress:** Keine Telemetrie, keine Cloud-Synchronisation, keine externen Netzwerkverbindungen.
- **Fail-Closed & Dry-Run Standard:** Die Standardkonfiguration ist deaktiviert und im Dry-Run-Modus. Ohne explizite Aktivierung werden weder Prozesse gestartet noch beendet.
- **Pfadbeschränkte Prozessauswahl:** Jede verwaltete App erfordert einen Prozessnamen und genau eine strenge Pfadbeschränkung (`path_exact` oder `path_contains`). Nicht lesbare oder fremde Prozesse werden niemals angetastet; CLI-Tools (wie npm `codex.exe`) liegen außerhalb des Beendigungsbereichs.
- **Unprivilegierter User-Mode (Non-Elevation):** Die Ausführung und Desktop-Installation erfolgt ausschließlich im unprivilegierten Benutzerkontext unterhalb von `%LOCALAPPDATA%`.
- **Externer Controller-Delegationsvertrag:** Steuerung von Codex-Automationen erfolgt ausschließlich über einen externen, ungebündelten Controller (`pause-all`, `stagger-resume`, `cancel`). `automation.toml` wird niemals direkt manipuliert. Fehlt der Controller, greift der Fail-Closed-Zustand (`block`).

### Reaktionszeit

Sicherheitsrelevante Meldungen werden innerhalb von maximal 48 Stunden gesichtet und priorisiert bearbeitet. Bitte geben Sie ausreichend Zeit zur Behebung, bevor Sie Details öffentlich machen.

### Unterstützte Versionen

| Version | Unterstützt |
| ------- | ----------- |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:         |

### Kontakt

- E-Mail: `security@open-bricks.org` / `support@lukasgeiger.com`
- GitHub Security Advisories: https://github.com/dev-bricks/app-rotator/security/advisories

---

## English

### Reporting a Vulnerability

If you find a security vulnerability, please report it responsibly:

1. **Do not open a public issue**
2. **Use GitHub Private Vulnerability Reporting** (`Security` → `Advisories` → `New`)
3. Include a description, reproduction steps, and potential impact

If private vulnerability reporting is not enabled yet, contact the maintainers
through GitHub or via the email addresses below and do not publish details in a public issue.

### Scope & Core Security Invariants

This tool performs security-relevant local desktop operations on Microsoft Windows:
- **100% Local-First & Zero Network Egress:** No telemetry, no analytics, no cloud synchronization, and no external network calls.
- **Fail-Closed & Dry-Run by Default:** Shipped configurations are disabled and set to dry-run mode. Neither processes nor external controllers are invoked without explicit opt-in.
- **Path-Restricted Process Scoping:** Managed apps require both a process name and exactly one strict path constraint (`path_exact` or `path_contains`). Inaccessible or unrelated processes are never matched; CLI executables (such as npm `codex.exe`) remain strictly outside the kill scope.
- **Non-Elevation User-Mode:** Runs and installs entirely within the unprivileged user context below `%LOCALAPPDATA%`.
- **External Controller Delegation Contract:** Control of external provider automations is delegated to a separate, unbundled controller (`pause-all`, `stagger-resume`, `cancel`). Internal configuration files like `automation.toml` are never modified directly. A missing controller triggers fail-closed blocking.

### Response Time

Security inquiries are reviewed and prioritized within 48 hours. Please allow reasonable time for remediation before public disclosure.

### Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:         |

### Contact

- Email: `security@open-bricks.org` / `support@lukasgeiger.com`
- GitHub Security Advisories: https://github.com/dev-bricks/app-rotator/security/advisories
