# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Repository-Hygiene, Bilingual Contributing Parity & Level 1 SBOM Re-Audit (Pfad A, 2026-10-03)
- Expanded `CONTRIBUTING.md` to comprehensive bilingual EN/DE reference standard:
  - Specified all 10 Governance and Runtime Invariants (`INV-LOCAL-01` through `INV-SLA-10`).
  - Documented Plan D Local Development Workflow (`C:\_Local_DEV\repos\app-rotator` Source of Truth).
  - Codified strict Version Freeze Discipline (`T-20260920-167562623`) maintaining version `0.2.3`.
  - Detailed pre-commit quality gates (`pytest`, `ruff check`, `compileall`, `git diff --check`, `git diff -G"version"`).
  - Formalized German statutory liability limitation disclaimer (§ 521 BGB *Gefälligkeitsrecht*) and Zero-Copyleft guarantee on user workloads.
- Hardened `.gitignore` against multi-agent lock patterns (`LOCK.dev.*`, `LOCK.antigravity.*`, `LOCK.bugsearch.*`), Windows shell metadata (`Desktop.ini`, `ehthumbs.db`), and test/coverage caches (`.nyc_output/`).
- Standardized PEP 621 configuration in `pyproject.toml`:
  - Added `"Level 1 SBOM (Text)"` endpoint to `[project.urls]`.
  - Hardened pytest `norecursedirs` with `.tox` and `.nyc_output`.
- Re-audited Level 1 SBOM in `THIRD_PARTY_LICENSES.md` and plain-text companion `THIRD_PARTY_LICENSES.txt` (Stand 2026-10-03) with 100% permissive dependencies, unprivileged `RunAsInvoker` non-elevation, and 48h Security Response SLA.
- Synchronized Shields.io repository badges (`pytest-72+ passed | 100% green`, `Contributing-Guide` / `Mitwirken-Leitfaden`, `Verified-2026--10--03`, `Last Checked-2026--10--03`), `llms.txt`, and local `MARKETING-LOG.txt`.
- Expanded automated contract test suite in `tests/test_metadata.py` with 5 new contract tests verifying bilingual contributing parity, 10 invariants, extended lock defenses, PEP 621 metadata, and audit recency.

### Discoverability, 18-Point Bilingual Navigation Parity, ASCII Architecture Topology & Level 1 SBOM (Pfad B, 2026-09-29)
- Upgraded documentation to symmetrical 18-point bilingual quick navigation parity across `README.md` and `README_de.md` with reciprocal dual HTML anchor aliases (`<a id="..."></a>`) and tabular `#sec-01`..`#sec-18` quick links.
- Embedded Four-View ASCII Architecture Topology Projection (`[VIEW 1: USER RUNTIMES]` through `[VIEW 4: AIR-GAP DEFENSE PERIMETER]`) in Section 2 across both English and German documentation, mapping components to invariants `INV-LOCAL-01`..`INV-SLA-10`.
- Implemented clean 16 / 17 / 18 section split separating Third-Party Licenses & Level 1 SBOM (Sec 16), Development & Verification (Sec 17), and Statutory Notice & § 521 BGB Disclaimer (Sec 18).
- Expanded Level 1 SBOM Plain-Text Companion `THIRD_PARTY_LICENSES.txt` with OpenChain compliant schema, component inventory, full invariant cross-reference matrix (`INV-LOCAL-01`..`INV-SLA-10`), and complete permissive license texts (MIT, BSD-3-Clause, HPND, LGPL-3.0 dynamic link summary, PSF-2.0).
- Standardized PEP 621 packaging in `pyproject.toml` with 20 saturated remote GitHub topics sorted alphabetically and added URLs `"Level 1 SBOM"` and `"Plain-Text License"` pointing to `THIRD_PARTY_LICENSES.txt`.
- Synchronized repository shields badges (Level 1 SBOM plain text audited, Verified 2026-09-29, Last Checked 2026-09-29), `llms.txt`, and local `MARKETING-LOG.txt`.
- Expanded automated contract test suite in `tests/test_metadata.py` for 18-point quick navigation parity, reciprocal dual anchors, Four-View ASCII topology presence, Level 1 SBOM invariants, and 20 topics saturation.

### Repository-Hygiene, CI-Lifecycle-Workflows & PEP 621 Standardisierung (Pfad A, 2026-09-28)
- Provisioned automated CI/CD community lifecycle workflows:
  - `.github/workflows/auto-assign.yml` (`actions/github-script@v7`, `timeout-minutes: 5`, concurrency `cancel-in-progress: true` on `${{ github.workflow }}-${{ github.ref }}`, least-privilege permissions `pull-requests: write`, `issues: write`).
  - `.github/workflows/label-sync.yml` (`EndBug/label-sync@v2`, `timeout-minutes: 5`, concurrency `cancel-in-progress: true`, permissions `issues: write`).
  - `.github/labels.yml` with 11 standard community governance labels according to GOVERNANCE.md §4.2.
- Hardened `.gitignore` against fleet sync patterns (`*-IDEAPAD*`, `*-IDEAPAD-GEI*`), lockfiles (`uv.lock`), test caches (`.pytest_temp/`, `.pytest_tmp*/`), and agent internal control files (`TASKPLAN_*.md`, `TASKPLAN_STATUS_*.md`).
- Standardized PEP 621 metadata in `pyproject.toml`:
  - Added `license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]`.
  - Added project URLs for `Contributing`, `Third-Party Licenses (Text)`, and `LLM Ready`.
  - Saturated keywords to 20 topics (`tray-icon`, `process-manager`, `offline-first`, `resource-management`).
  - Hardened pytest options with `addopts = "-ra -v --basetemp=.pytest_temp"` and extended `norecursedirs`.
- Created formal plain-text third-party inventory `THIRD_PARTY_LICENSES.txt` and contributor guide `CONTRIBUTING.md`.
- Updated `THIRD_PARTY_LICENSES.md` Level 1 SBOM audit date to 2026-09-28 with RunAsInvoker non-elevation certification and 100% offline zero-egress invariants.
- Synchronized `llms.txt`, Shields.io status badges, and local `MARKETING-LOG.txt` (Audit 2026-09-28).
- Expanded automated contract test suite in `tests/test_metadata.py` to verify auto-assign/label-sync workflows, labels.yml, Contributing/Plain-text licenses URLs, .gitignore fleet patterns, and SBOM audit recency.

### Discoverability, Visual Architecture & Level 1 SBOM Parity (Pfad B)
- Saturated GitHub repository topics to 20/20 platform maximum (`dev-bricks`, `fail-closed`, `open-bricks`, `python`, `zero-egress`).
- Upgraded documentation to symmetrical 17-point bilingual quick navigation parity across `README.md` and `README_de.md` with reciprocal dual HTML anchor aliases (`<a id="..."></a>`).
- Added structured Target Personas & High-Intent SEO queries (`[PERSONA-01]` Autonomous AI Desktop Engineers, `[PERSONA-02]` Local-First & Air-Gapped Developers, `[PERSONA-03]` Windows Power Users & Performance Tuners, `[PERSONA-04]` Security & Infrastructure Compliance Auditors) across both languages.
- Integrated comprehensive 10-dimension 5-way comparative matrix vs. traditional alternatives (Manual Task Manager / Alt+F4, Windows Sleep / Power Plans, Generic Process Killers / AutoHotkey Scripts, VM / Container Sandboxes) mapped to Governance Invariants `INV-LOCAL-01` through `INV-SLA-10`.
- Added formal root open-source attribution notice `NOTICE` for Lukas Geiger, `dev-bricks`, and `open-bricks`.
- Added explicit German statutory liability limitation disclaimer according to § 521 BGB (*Gefälligkeitsrecht*) in Section 16 of both READMEs.
- Upgraded `THIRD_PARTY_LICENSES.md` with Level 1 SBOM, Invariant Cross-Reference Matrix mapping `INV-LOCAL-01`..`INV-SLA-10`, and re-audit date 2026-09-21.
- Standardized PEP 621 packaging in `pyproject.toml` with `license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md"]`, Notice URL, and discoverability keywords.
- Synchronized `llms.txt`, Shields.io status badges, and local `MARKETING-LOG.txt`.
- Expanded automated contract test suite in `tests/test_metadata.py` with tests for 17-point navigation, reciprocal dual anchors, target personas, comparative matrix, § 521 BGB statutory disclaimer, and Level 1 SBOM compliance.

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
