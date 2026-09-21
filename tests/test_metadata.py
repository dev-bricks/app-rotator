"""Contract tests for repository hygiene, PEP 621 metadata, CI guardrails, and Pfad B invariants."""

from __future__ import annotations

import tomllib
from pathlib import Path

import app_rotator

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_pep621_metadata_and_urls() -> None:
    """Verify PEP 621 compliance, version, keywords, and required project URLs in pyproject.toml."""
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.is_file()

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data.get("project", {})

    assert project.get("name") == "app-rotator"
    assert project.get("version") == "0.2.3"

    keywords = project.get("keywords", [])
    for kw in ["zero-egress", "open-bricks", "dev-bricks", "fail-closed"]:
        assert kw in keywords, f"Missing keyword: {kw}"

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
        "Notice",
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
    assert (
        "Last-checked: 2026-09-11" in content
        or "Last-checked: 2026-09-12" in content
        or "Last-checked: 2026-09-19" in content
        or "Last-checked: 2026-09-21" in content
    )
    assert "https://github.com/dev-bricks/app-rotator" in content
    assert "0.2.3" in content
    assert "INV-LOCAL-01" in content
    assert "INV-SLA-10" in content
    assert "NOTICE" in content
    assert "MARKETING-LOG.txt" in content
    assert "THIRD_PARTY_LICENSES.md" in content


def test_readme_badges_consistency() -> None:
    """Verify essential shields.io badges in English and German READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme in (readme_en, readme_de):
        assert "actions/workflows/tests.yml/badge.svg" in readme
        assert "badge/version-0.2.3-blue.svg" in readme
        assert "badge/Python-3.11" in readme
        assert "badge/Platform-Windows" in readme or "badge/Plattform-Windows" in readme
        assert "dev--bricks" in readme
        assert "open--bricks" in readme
        assert "NOTICE" in readme
        assert "SECURITY.md" in readme
        assert "llms.txt" in readme
        assert "MARKETING-LOG.txt" in readme
        assert (
            "2026--09--11" in readme
            or "2026--09--12" in readme
            or "2026--09--19" in readme
            or "2026--09--21" in readme
        )


def test_quick_navigation_17_points_parity() -> None:
    """Verify exactly 17 quick navigation points are defined with parity across READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "### 🧭 Quick Navigation" in readme_en
    assert "### 🧭 Schnellnavigation" in readme_de

    for i in range(1, 18):
        assert f"- [{i}." in readme_en, f"Missing navigation point {i} in README.md"
        assert f"- [{i}." in readme_de, f"Missing navigation point {i} in README_de.md"


def test_reciprocal_dual_anchors_parity() -> None:
    """Verify reciprocal dual HTML anchors (<a id="..."></a>) exist on all 17 sections."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    anchors = [
        ("why-this-exists", "warum-dieses-projekt-existiert"),
        ("architecture--state-machine-flow", "systemarchitektur--zustandsautomaten-fluss"),
        ("state--cycle-dynamics", "zustandslogik--zyklusdynamik"),
        ("safe-process-scoping--appx-launching", "sichere-prozessauswahl--appx-start"),
        ("external-codex-safe-start-contract", "externer-codex-safe-start-vertrag"),
        ("system-tray--native-settings-ui", "system-tray--native-einstellungs-ui"),
        ("per-user-desktop-installation", "benutzerbezogene-desktop-installation"),
        ("target-personas--high-intent-discoverability", "zielgruppen--auffindbarkeit"),
        (
            "10-dimension-comparative-matrix-vs-alternatives",
            "10-dimensionale-vergleichsmatrix-vs-alternativen",
        ),
        ("key-governance--runtime-invariants", "governance---laufzeit-invarianten"),
        ("end-to-end-execution-lifecycle", "end-to-end-ausfuehrungslebenszyklus"),
        ("sibling-tools--ecosystem-matrix", "geschwisterwerkzeuge--partner-matrix"),
        ("installation--cli-usage", "installation--cli-bedienung"),
        ("configuration--schema-migration", "konfiguration--schema-migration"),
        ("security--zero-egress-privacy", "sicherheit--zero-egress-datenschutz"),
        (
            "statutory-notice-liability--license--521-bgb",
            "gesetzlicher-hinweis-haftungsausschluss--lizenz--521-bgb",
        ),
        ("development--verification", "entwicklung--verifikation"),
    ]
    for en_id, de_id in anchors:
        dual_anchor = f'<a id="{en_id}"></a><a id="{de_id}"></a>'
        assert dual_anchor in readme_en, f"Missing dual anchor {en_id}/{de_id} in README.md"
        assert dual_anchor in readme_de, f"Missing dual anchor {en_id}/{de_id} in README_de.md"


def test_target_personas_sections() -> None:
    """Verify target personas [PERSONA-01] to [PERSONA-04] are documented in both READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    personas = ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]
    for p in personas:
        assert p in readme_en, f"Missing persona {p} in README.md"
        assert p in readme_de, f"Missing persona {p} in README_de.md"


def test_comparative_matrix_sections() -> None:
    """Verify 10-dimension comparative matrix vs alternatives is present in both READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "10-Dimension Comparative Matrix vs. Alternatives" in readme_en
    assert "10-Dimensionale Vergleichsmatrix vs. Alternativen" in readme_de

    for dim in [
        "1. GPU / VRAM",
        "2. Privilege Boundary",
        "3. Fail-Closed Default",
        "4. Strict Path Scoping",
        "5. Atomic Persistence",
        "6. Provider Delegation",
        "7. Single-Instance Mutex",
        "8. UWP / AppX",
        "9. Cloud-Sync Defense",
        "10. Security SLA",
    ]:
        assert dim in readme_en, f"Missing comparative dimension {dim} in README.md"


def test_statutory_notice_bgb_521_parity() -> None:
    """Verify statutory notice and § 521 BGB disclaimer are documented in both READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "§ 521 BGB" in readme_en
    assert "§ 521 BGB" in readme_de
    assert "Gefälligkeitsrecht" in readme_en or "Gratuitous Performance" in readme_en
    assert "Gefälligkeitsrecht" in readme_de
    assert "Lukas Geiger" in readme_en
    assert "Lukas Geiger" in readme_de


def test_notice_and_level1_sbom_compliance() -> None:
    """Verify root NOTICE file exists and Level 1 SBOM Invariant Matrix in THIRD_PARTY_LICENSES."""
    notice_path = ROOT / "NOTICE"
    assert notice_path.is_file(), "Root NOTICE file must exist"
    notice_text = notice_path.read_text(encoding="utf-8")
    assert "Lukas Geiger" in notice_text
    assert "dev-bricks" in notice_text
    assert "open-bricks" in notice_text

    sbom_path = ROOT / "THIRD_PARTY_LICENSES.md"
    assert sbom_path.is_file()
    sbom_text = sbom_path.read_text(encoding="utf-8")
    assert "Invariant Cross-Reference Matrix" in sbom_text
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
        assert inv in sbom_text, f"Missing invariant {inv} in THIRD_PARTY_LICENSES.md"


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
    assert package_version == pyproject_version == "0.2.3"

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
    assert "0.2.3" in content
    assert "2026-09-09" in content
    assert "2026-09-11" in content
    assert "2026-09-12" in content
    assert "2026-09-19" in content
    assert "2026-09-21" in content
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
    """Verify pyproject.toml defines extended ruff lint rulesets."""
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


def test_header_banner_asset_exists_and_linked() -> None:
    """Verify banner assets exist, are non-empty, and are linked in both READMEs."""
    banner_png = ROOT / "assets" / "banner.png"
    banner_svg = ROOT / "assets" / "banner.svg"
    banner_b_svg = ROOT / "assets" / "banner-b.svg"

    assert banner_png.is_file() or banner_svg.is_file() or banner_b_svg.is_file()

    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "assets/banner" in readme_en, "README.md must link assets/banner"
    assert "assets/banner" in readme_de, "README_de.md must link assets/banner"


def test_lifecycle_workflows_present() -> None:
    """Verify stale.yml and welcome.yml lifecycle workflows exist with required guardrails."""
    stale_path = ROOT / ".github" / "workflows" / "stale.yml"
    assert stale_path.is_file(), "stale.yml must exist"
    stale_content = stale_path.read_text(encoding="utf-8")
    assert "actions/stale@v9" in stale_content
    assert "timeout-minutes: 10" in stale_content
    assert "issues: write" in stale_content
    assert "pull-requests: write" in stale_content
    assert "cron: '30 1 * * *'" in stale_content

    welcome_path = ROOT / ".github" / "workflows" / "welcome.yml"
    assert welcome_path.is_file(), "welcome.yml must exist"
    welcome_content = welcome_path.read_text(encoding="utf-8")
    assert "actions/first-interaction@v3" in welcome_content
    assert "timeout-minutes: 5" in welcome_content
    assert "cancel-in-progress: true" in welcome_content
    assert "issues: write" in welcome_content
    assert "pull-requests: write" in welcome_content


def test_gitignore_multihost_and_lock_defense() -> None:
    """Verify .gitignore contains multi-host tokens, conflict copy patterns, and canonical locks."""
    gitignore_path = ROOT / ".gitignore"
    content = gitignore_path.read_text(encoding="utf-8")

    assert "*conflicted copy*" in content
    assert "* (Kopie)*" in content
    assert "* (Copy)*" in content
    assert "*-WORKSTATION*" in content
    assert "*-WORKSTATION-LG*" in content
    assert "*-LAPTOP*" in content
    assert "*-ASUS*" in content
    assert "*-ASUS-GEI*" in content
    assert "*-Mac Studio*" in content
    assert "*-MacBook*" in content
    assert "LOCK" in content
    assert "LOCK.*" in content
    assert "LOCK*.txt" in content
    assert "LOCK.user.*" in content
    assert "LOCK.until.*" in content
    assert "LOCK.condition.*" in content
    assert "LOCK.permissions.json" in content
    assert ".automation-lock" in content
    assert "!package-lock.json" in content


def test_pyproject_pep621_license_files_and_pytest_hardening() -> None:
    """Verify license-files in project and minversion/norecursedirs in pytest options."""
    pyproject_path = ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    project = data.get("project", {})
    assert project.get("license-files") == ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md"]

    pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert pytest_opts.get("minversion") == "7.0"
    norecursedirs = pytest_opts.get("norecursedirs", [])
    assert ".git" in norecursedirs
    assert ".pytest_cache" in norecursedirs


def test_third_party_licenses_audit_recency() -> None:
    """Verify THIRD_PARTY_LICENSES.md includes current audit date and invariants."""
    licenses_path = ROOT / "THIRD_PARTY_LICENSES.md"
    content = licenses_path.read_text(encoding="utf-8")

    assert "Audit Date:** 2026-09-21" in content
    assert "Version:** `0.2.3`" in content
    assert "RunAsInvoker" in content
    assert "Zero-Copyleft Guarantee" in content


def test_changelog_release_023_entry() -> None:
    """Verify CHANGELOG.md contains release 0.2.3 entry with hygiene and lifecycle details."""
    changelog_content = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## 0.2.3 — 2026-09-19" in changelog_content
    assert "stale.yml" in changelog_content
    assert "welcome.yml" in changelog_content
    assert "license-files" in changelog_content
