# Changelog

All notable changes to this project are documented here.

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
