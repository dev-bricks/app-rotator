"""Contract tests for repository hygiene, PEP 621 metadata, CI guardrails, and security policies."""

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
    assert project.get("version") == "0.2.1"

    urls = project.get("urls", {})
    required_urls = [
        "Homepage",
        "Documentation",
        "Repository",
        "Issues",
        "Changelog",
        "Security",
        "Umbrella",
        "Parent Organization",
        "Umbrella Ecosystem",
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


def test_ci_workflow_guardrails() -> None:
    """Verify GitHub Actions CI workflow includes concurrency, ruff linting, and Python matrix."""
    ci_path = ROOT / ".github" / "workflows" / "tests.yml"
    assert ci_path.is_file()

    content = ci_path.read_text(encoding="utf-8")
    assert "cancel-in-progress: true" in content
    assert "windows-latest" in content
    assert "3.11" in content
    assert "3.12" in content
    assert "3.13" in content
    assert "ruff check" in content
    assert "compileall" in content
    assert "pytest" in content


def test_security_policy_structure() -> None:
    """Verify SECURITY.md bilingual structure, supported versions, and maintainer contacts."""
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


def test_llms_txt_and_docs_sync() -> None:
    """Verify llms.txt contains the canonical repository, version, and current timestamp."""
    llms_path = ROOT / "llms.txt"
    assert llms_path.is_file()

    content = llms_path.read_text(encoding="utf-8")
    assert "Last-checked: 2026-09-08" in content
    assert "https://github.com/dev-bricks/app-rotator" in content
    assert "0.2.1" in content


def test_readme_badges_consistency() -> None:
    """Verify essential shields.io badges and navigation in English and German READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme in (readme_en, readme_de):
        assert "actions/workflows/tests.yml/badge.svg" in readme
        assert "badge/Python-3.11" in readme
        assert "badge/Platform-Windows" in readme or "badge/Plattform-Windows" in readme
        assert "dev--bricks" in readme
        assert "open--bricks" in readme
        assert "SECURITY.md" in readme
        assert "llms.txt" in readme

    assert "Quick Navigation:" in readme_en
    assert "Schnellnavigation:" in readme_de


def test_version_parity() -> None:
    """Verify package version is consistent across pyproject, package __init__, and CHANGELOG."""
    pyproject_path = ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    pyproject_version = data.get("project", {}).get("version")

    package_version = app_rotator.__version__
    assert package_version == pyproject_version == "0.2.1"

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
    assert "LOCK*.txt" in content
