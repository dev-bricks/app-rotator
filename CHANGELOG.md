# Changelog

All notable changes to this project are documented here.

## 0.2.3 — 2026-09-19

### Maintenance & Technical Hygiene (Pfad A)
- Added automated community lifecycle workflows:
  - `.github/workflows/stale.yml` (`actions/stale@v9`, daily cron `30 1 * * *`, `timeout-minutes: 10`, least-privilege permissions `issues: write`, `pull-requests: write`).
  - `.github/workflows/welcome.yml` (`actions/first-interaction@v3`, `timeout-minutes: 5`, concurrency `cancel-in-progress: true`, least-privilege permissions `issues: write`, `pull-requests: write`).
- Hardened `.gitignore` against multi-host sync conflicts (`*conflicted copy*`, `* (Kopie)*`, `* (Copy)*`, `*-WORKSTATION*`, `*-WORKSTATION-LG*`, `*-LAPTOP*`, `*-ASUS*`, `*-ASUS-GEI*`, `*-Mac Studio*`, `*-MacBook*`), canonical lockfiles (`LOCK`, `LOCK.*`, `LOCK*.txt`, `LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`, `LOCK.permissions.json`, `.automation-lock`), and package lock preservation (`!package-lock.json`).
- Standardized PEP 621 packaging and tooling in `pyproject.toml`:
  - Added standard `license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]`.
  - Configured pytest `minversion = "7.0"` and explicit `norecursedirs`.
- Upgraded `THIRD_PARTY_LICENSES.md` audit to 2026-09-19 v0.2.3 with Level 1 SBOM verification, unprivileged `RunAsInvoker` non-elevation certification, and zero-copyleft re-audit.
- Synchronized version `0.2.3` across manifests, `__init__.py`, `pyproject.toml`, `assets/banner.svg`, `llms.txt`, `MARKETING-LOG.txt`, `README.md`, and `README_de.md`.
- Expanded automated metadata contract test suite in `tests/test_metadata.py` with contract tests verifying lifecycle workflows, extended multi-host lock defense, PEP 621 license files, and release 0.2.3 parity.

## 0.2.2 — 2026-09-09

### Maintenance & Hygiene — 2026-09-11

- Hardened CI workflow (`.github/workflows/tests.yml`) with `timeout-minutes: 15`.
- Modernized codebase to satisfy extended Ruff linter rulesets (`E, F, W, I, UP, B, SIM, C4, PT, RUF`):
  - Used `contextlib.suppress(FileNotFoundError)` in atomic config writer.
  - Simplified process matching branching logic in `src/app_rotator/processes.py`.
  - Used dict literals and idiomatic `pytest.raises` context managers across unit and controller tests.
- Enriched `pyproject.toml` with `Bug Tracker` URL and `Topic :: System :: Monitoring` classifier.
- Hardened `.gitignore` against multi-host conflict tokens, `.mypy_cache/`, `.tox/`, and OS artifacts.
- Synchronized repository shields, `llms.txt`, and extended contract test suite in `tests/test_metadata.py`.

- **Pfad B Marketing, Discoverability & Visual Architecture Release**:
  - Established full bilingual parity across `README.md` (English) and `README_de.md` (German) with bidirectional language switcher and synchronized 14-point quick navigation (`Quick Navigation` / `Schnellnavigation`).
  - Added dual interactive Mermaid diagrams:
    - `flowchart TD`: Subsystem architecture & state machine (Tray UI & Menu, CLI & Atomic Mailbox, RotatorEngine Core, Safe Process Scoping & AppX Launchers, External Controller Contract).
    - `sequenceDiagram`: End-to-end 14-step execution lifecycle with autonumbering covering play, mailbox enqueue, mutex lock, controller pause-all, AppX activation, stagger-resume, phase countdown, graceful termination, inter-app gap cooldown, and cycle resets.
  - Formulated and documented the **10 Governance & Runtime Invariants** table (`INV-LOCAL-01` to `INV-SLA-10`) guaranteeing 100% local-first zero-egress, non-elevation `RunAsInvoker`, fail-closed dry-run defaults, strict path scoping, atomic persistence, external provider delegation, single-instance file locks, non-invasive AppX activation, cloud-sync resilience, and 48h SLA / 5-day triage.
  - Integrated 16-repository Sibling Tools & Ecosystem Matrix spanning `dev-bricks`, `file-bricks`, `doc-bricks`, `ellmos-ai`, `entertain-and-more`, and `open-bricks`.
  - Upgraded `SECURITY.md` with binding 48-hour response SLA and 5-business-day triage guarantee in both German and English sections, supported version lifecycle `0.2.x`, and comprehensive maintainer/umbrella contact channels (`security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`, `lukas@open-bricks.org`).
  - Added comprehensive third-party software license inventory (`THIRD_PARTY_LICENSES.md`) covering Pillow, psutil, pystray, pytest, ruff, and setuptools.
  - Added repository-local Pfad B register `MARKETING-LOG.txt`.
  - Hardened `.gitignore` against multi-host cloud-sync conflicts (`*-conflict-*`, `*.sync-temp-*`, `*.sync-conflict-*`, `*.conflict`, `*-CONFLIT-*`) and multi-agent lockfiles (`LOCK`, `LOCK.*`, `*.lock`, `LOCK*.txt`).
  - Hardened CI workflow (`.github/workflows/tests.yml`) with verbose test execution (`pytest -v`), bytecode compilation gate, and pip caching across Python 3.11, 3.12, and 3.13 on Windows runners.
  - Enriched PEP 621 metadata in `pyproject.toml` (version 0.2.2, URLs for Third-Party Licenses and Marketing Log, verbose pytest options `-ra -v`).
  - Synchronized `llms.txt` with canonical links, version 0.2.2, 10 invariants, and test counts.
  - Expanded automated contract test suite in `tests/test_metadata.py` from 8 to 15 tests, verifying complete metadata and visual architecture parity.

## 0.2.1 — 2026-09-08

- Added GitHub Actions CI workflow (`.github/workflows/tests.yml`) targeting Windows runners across Python 3.11, 3.12, and 3.13 with pip caching, ruff linting, compileall, and pytest.
- Added bilingual security policy (`SECURITY.md`) specifying 48-hour response SLA, supported version lifecycle (`0.2.x`), GitHub Security Advisories reporting, and 5 core safety invariants (100% Local-First & Zero Egress, Fail-Closed & Dry-Run by Default, Path-Restricted Process Scoping, Non-Elevation User-Mode, External Controller Delegation Contract).
- Added automated metadata and contract test suite (`tests/test_metadata.py`) validating PEP 621 compliance, URLs, CI workflow integrity, SECURITY.md structure, llms.txt sync, README badge consistency, version parity, and German UTF-8 encoding.
- Enriched PEP 621 metadata in `pyproject.toml` with standard classifiers and comprehensive ecosystem URLs (`Parent Organization`, `Umbrella Ecosystem`, `Security`, `Changelog`, `Issues`, `Documentation`).
- Added Shields.io status badges and quick navigation headers across `README.md` and `README_de.md`.
- Synchronized `llms.txt` with canonical links, version 0.2.1, and 41 verified pytest tests.
- Hardened `.gitignore` with cloud synchronization conflict patterns and lockfile exclusions.

## 0.2.0 — 2026-08-02

- Minute-based provider settings.
- Branded icon and desktop installer (`scripts/install-desktop-shortcut.ps1`).
- Hardened controller and persisted state recovery.
- Initial safe, configurable desktop app rotator (tray + CLI).
