"""Contract tests for repository hygiene, PEP 621 metadata, CI guardrails, and Pfad B invariants."""

from __future__ import annotations

import tomllib
from pathlib import Path

import app_rotator

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_pep621_metadata_and_urls() -> None:
    """Verify PEP 621 compliance, version, and required project URLs in pyproject.toml."""
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.is_file()

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data.get("project", {})

    assert project.get("name") == "app-rotator"
    assert project.get("version") == "0.2.2"

    urls = project.get("urls", {})
    required_urls = [
        "Homepage",
        "Documentation",
        "Repository",
        "Issues",
        "Bug Tracker",
        "Changelog",
        "Security",
        "Umbrella",
        "Parent Organization",
        "Umbrella Ecosystem",
        "Third-Party Licenses",
        "Marketing",
    ]
    for key in required_urls:
        assert key in urls, f"Missing project URL: {key}"
        assert urls[key].startswith("https://"), f"Invalid URL for {key}: {urls[key]}"

    classifiers = project.get("classifiers", [])
    assert "Operating System :: Microsoft :: Windows" in classifiers
    assert "Programming Language :: Python :: 3.11" in classifiers
    assert "Programming Language :: Python :: 3.12" in classifiers
    assert "Programming Language :: Python :: 3.13" in classifiers
    assert "License :: OSI Approved :: MIT License" in classifiers
    assert "Topic :: System :: Monitoring" in classifiers

    pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "-v" in pytest_opts.get("addopts", "")

    ruff_select = data.get("tool", {}).get("ruff", {}).get("lint", {}).get("select", [])
    for rule in ["E", "F", "W", "I", "UP", "B", "SIM", "C4", "PT", "RUF"]:
        assert rule in ruff_select, f"Missing ruff lint rule: {rule}"


def test_ci_workflow_guardrails() -> None:
    """Verify CI workflow includes concurrency, ruff linting, compileall, and pytest -v."""
    ci_path = ROOT / ".github" / "workflows" / "tests.yml"
    assert ci_path.is_file()

    content = ci_path.read_text(encoding="utf-8")
    assert "cancel-in-progress: true" in content
    assert "windows-latest" in content
    assert "timeout-minutes: 15" in content
    assert "3.11" in content
    assert "3.12" in content
    assert "3.13" in content
    assert "ruff check" in content
    assert "compileall" in content
    assert "pytest -v" in content


def test_security_policy_structure() -> None:
    """Verify SECURITY.md bilingual structure, supported versions, SLAs, and maintainer contacts."""
    security_path = ROOT / "SECURITY.md"
    assert security_path.is_file()

    content = security_path.read_text(encoding="utf-8")
    assert "## Deutsch" in content
    assert "## English" in content
    assert "0.2.x" in content
    assert "security@open-bricks.org" in content
    assert "support@lukasgeiger.com" in content
    assert "github.com/dev-bricks/app-rotator/security/advisories" in content
    assert "100% Local-First & Zero Network Egress" in content
    assert "48-Hour Response SLA" in content or "48-Stunden-Reaktions-SLA" in content
    assert "5-Business-Day Triage Guarantee" in content or "5-Werktage-Triage-Zusage" in content


def test_llms_txt_and_docs_sync() -> None:
    """Verify llms.txt contains canonical repository, version, invariants, and timestamp."""
    llms_path = ROOT / "llms.txt"

    assert llms_path.is_file()

    content = llms_path.read_text(encoding="utf-8")
    assert "Last-checked: 2026-09-11" in content
    assert "https://github.com/dev-bricks/app-rotator" in content
    assert "0.2.2" in content
    assert "INV-LOCAL-01" in content
    assert "INV-SLA-10" in content
    assert "MARKETING-LOG.txt" in content
    assert "THIRD_PARTY_LICENSES.md" in content


def test_readme_badges_consistency() -> None:
    """Verify essential shields.io badges in English and German READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme in (readme_en, readme_de):
        assert "actions/workflows/tests.yml/badge.svg" in readme
        assert "badge/version-0.2.2-blue.svg" in readme
        assert "badge/Python-3.11" in readme
        assert "badge/Platform-Windows" in readme or "badge/Plattform-Windows" in readme
        assert "dev--bricks" in readme
        assert "open--bricks" in readme
        assert "SECURITY.md" in readme
        assert "llms.txt" in readme
        assert "MARKETING-LOG.txt" in readme
        assert "2026--09--11" in readme


def test_quick_navigation_14_points_parity() -> None:
    """Verify exactly 14 quick navigation points are defined with parity across READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "### 🧭 Quick Navigation" in readme_en
    assert "### 🧭 Schnellnavigation" in readme_de

    for i in range(1, 15):
        assert f"- [{i}." in readme_en, f"Missing navigation point {i} in README.md"
        assert f"- [{i}." in readme_de, f"Missing navigation point {i} in README_de.md"


def test_dual_mermaid_diagrams_in_readmes() -> None:
    """Verify dual interactive Mermaid diagrams (flowchart and sequenceDiagram) in both READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme in (readme_en, readme_de):
        assert "```mermaid\nflowchart TD" in readme
        assert "```mermaid\nsequenceDiagram\n    autonumber" in readme
        assert "pause-all" in readme
        assert "stagger-resume" in readme
        assert "app-rotator.lock" in readme


def test_governance_invariants_table_parity() -> None:
    """Verify all 10 governance and runtime invariants are documented in both READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    invariants = [
        "INV-LOCAL-01",
        "INV-UNPRIV-02",
        "INV-DRYRUN-03",
        "INV-SCOPING-04",
        "INV-ATOMIC-05",
        "INV-DELEGATION-06",
        "INV-LOCKFILE-07",
        "INV-AUMID-08",
        "INV-SYNC-09",
        "INV-SLA-10",
    ]
    for inv in invariants:
        assert inv in readme_en, f"Missing invariant {inv} in README.md"
        assert inv in readme_de, f"Missing invariant {inv} in README_de.md"


def test_sibling_ecosystem_matrix_parity() -> None:
    """Verify partner repositories are linked and described in both READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    partner_repos = [
        "WikiStub-Seed",
        "privacymaildesk",
        "githubbot",
        "system-auditor",
        "system-explorer",
        "ellmos-controlcenter-mcp",
        "ellmos-delegation-authority",
        "sqlite-transit-sync",
        "clip-storyboard-director",
        "ExplorerPro",
        "prosync",
        "cleanmarkdown",
        "KlangpultLight",
        "open-bricks",
    ]
    for repo in partner_repos:
        assert repo.lower() in readme_en.lower(), f"Missing partner repo {repo} in README.md"
        assert repo.lower() in readme_de.lower(), f"Missing partner repo {repo} in README_de.md"


def test_version_parity() -> None:
    """Verify package version is consistent across pyproject, package __init__, and CHANGELOG."""
    pyproject_path = ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    pyproject_version = data.get("project", {}).get("version")

    package_version = app_rotator.__version__
    assert package_version == pyproject_version == "0.2.2"

    changelog_content = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {package_version}" in changelog_content


def test_german_umlauts_utf8_integrity() -> None:
    """Verify README_de.md uses native German umlauts and valid UTF-8 without corruption."""
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "ä" in readme_de
    assert "ö" in readme_de
    assert "ü" in readme_de
    assert "ß" in readme_de
    assert "\ufffd" not in readme_de


def test_gitignore_hygiene() -> None:
    """Verify .gitignore includes sync conflict and lock patterns."""
    gitignore_path = ROOT / ".gitignore"
    assert gitignore_path.is_file()

    content = gitignore_path.read_text(encoding="utf-8")
    assert "*.sync-conflict-*" in content
    assert "*-conflict-*" in content
    assert "LOCK*.txt" in content
    assert "LOCK.*" in content
    assert ".mypy_cache/" in content
    assert "*-WORKSTATION*" in content
    assert "* (kopie)*" in content


def test_third_party_licenses_inventory() -> None:
    """Verify THIRD_PARTY_LICENSES.md documents key dependencies and licenses."""
    licenses_path = ROOT / "THIRD_PARTY_LICENSES.md"
    assert licenses_path.is_file()

    content = licenses_path.read_text(encoding="utf-8")
    assert "Pillow" in content
    assert "psutil" in content
    assert "pystray" in content
    assert "pytest" in content
    assert "ruff" in content
    assert "BSD-3-Clause" in content
    assert "MIT License" in content


def test_marketing_log_parity() -> None:
    """Verify MARKETING-LOG.txt documents Pfad B release and Pfad A hygiene measures."""
    marketing_path = ROOT / "MARKETING-LOG.txt"
    assert marketing_path.is_file()

    content = marketing_path.read_text(encoding="utf-8")
    assert "0.2.2" in content
    assert "2026-09-09" in content
    assert "2026-09-11" in content
    assert "INV-LOCAL-01" in content
    assert "Mermaid" in content


def test_desktop_shortcut_installer_script() -> None:
    """Verify per-user installer script exists and handles unprivileged installation."""
    installer_path = ROOT / "scripts" / "install-desktop-shortcut.ps1"
    assert installer_path.is_file()

    content = installer_path.read_text(encoding="utf-8")
    assert "AppRotator" in content
    assert "LOCALAPPDATA" in content
    assert "Desktop" in content


def test_extended_ruff_linter_compliance() -> None:
    """Verify pyproject.toml defines extended ruff lint rulesets and enforces zero-warning standard."""
    pyproject_path = ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    select_rules = set(data.get("tool", {}).get("ruff", {}).get("lint", {}).get("select", []))
    expected_rules = {"E", "F", "W", "I", "UP", "B", "SIM", "C4", "PT", "RUF"}
    assert expected_rules.issubset(select_rules)


def test_ci_timeout_minutes_guardrail() -> None:
    """Verify CI workflow defines a safe, bounded execution timeout."""
    ci_path = ROOT / ".github" / "workflows" / "tests.yml"
    content = ci_path.read_text(encoding="utf-8")
    assert "timeout-minutes: 15" in content
