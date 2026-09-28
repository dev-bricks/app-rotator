# Contributing to App Rotator

Thank you for your interest in contributing to **App Rotator** (`dev-bricks/app-rotator`).

## Principles & Invariants

All contributions must adhere to our core architectural invariants:
1. **100% Local-First & Zero Egress (`INV-LOCAL-01`)**: No network requests, telemetry beacons, or external API calls.
2. **Unprivileged Execution (`INV-UNPRIV-02`)**: RunAsInvoker mode; no UAC elevation or administrator requirements.
3. **Fail-Closed & Dry-Run by Default (`INV-DRYRUN-03`)**: Default configuration must be safe and inert until explicitly activated.
4. **Strict Path Scoping (`INV-SCOPING-04`)**: Process targeting requires exact executable path matching.
5. **Quality Gates**: All tests must pass via `pytest`, `ruff check .` must be clean, and `python -m compileall -q .` must succeed.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/dev-bricks/app-rotator.git
cd app-rotator

# Install editable package and dev dependencies
pip install -e .[dev]

# Run full test suite
python -m pytest

# Run linter
ruff check .
```

## Pull Request Guidelines

- Ensure your branch is rebased on `master`.
- Add or update contract and regression tests in `tests/` for any new logic or bug fixes.
- Document changes in `CHANGELOG.md` under `## [Unreleased]`.
- Provide a clear, descriptive PR title and summary.
