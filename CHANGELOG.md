# Changelog

All notable changes for MOVA SDK v0.1.0 (draft).

## [0.1.0] - Draft
### Added
- Initial SDK packaging and entrypoint (`pyproject.toml`).
- CLI: stable MVP command set (`mova_sdk/cli/main.py`) with commands: `run`, `status`, `version`.
- API wrappers:
  - EngineWrapper (`mova_sdk/api/__init__.py`)
  - LLMWrapper (`mova_sdk/api/__init__.py`)
- DTOs: TaskDTO and basic models scaffold (`mova_sdk/models/__init__.py`).
- Tests:
  - Unit tests for CLI and API wrappers (`tests/cli/`, `tests/api/`).
  - DTO tests (`tests/models/`).
- CI: GitHub Actions workflow for lint, mypy and pytest (`.github/workflows/tests.yml`).
- Load-test script for local performance checks (`scripts/load_test.py`).

### Fixed
- Import path handling for local `src/` package in load tests.
- Several lint/style adjustments for consistency.

### Notes
- This is a draft release branch for review. Tagging will be performed after final review and merge.
- Recommended follow-ups:
  1. Finalize docs and examples (`examples/sdk_usage.py`).
  2. Run extended load tests in CI/infra environment.
  3. Prepare CHANGELOG final entries and create GitHub release.