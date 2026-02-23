## Why

mdreview is ready to share publicly. To accept open contributions on GitHub, the project needs standard open-source scaffolding: a license, README, contributing guide, issue/PR templates, and CI. Without these, potential contributors have no guidance and the project looks incomplete.

## What Changes

- Add `LICENSE` file (MIT or similar)
- Add `README.md` with project description, screenshots/demo, installation, usage, and development setup
- Add `CONTRIBUTING.md` with development workflow, code style (ruff), and PR guidelines
- Add GitHub issue and PR templates (`.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`)
- Add GitHub Actions CI workflow for linting (ruff) and tests (pytest)
- Review `.gitignore` for completeness
- Ensure `pyproject.toml` has all fields needed for a public package

## Capabilities

### New Capabilities

- `open-source-scaffolding`: License, README, contributing guide, GitHub templates, and CI workflow for public collaboration

### Modified Capabilities

_(none — no behavioral changes to the application)_

## Impact

- New files: `LICENSE`, `README.md`, `CONTRIBUTING.md`, `.github/` templates and workflows
- `pyproject.toml`: Ensure metadata completeness (overlaps with `global-executable` change)
- `.gitignore`: Review and update
- No source code changes
