## ADDED Requirements

### Requirement: MIT License
The project SHALL include an MIT license file at the repository root.

#### Scenario: License file present
- **WHEN** the repository root is inspected
- **THEN** a `LICENSE` file exists containing the MIT license text with the current year and author name

### Requirement: README with project documentation
The project SHALL include a README.md at the repository root with installation, usage, and development instructions.

#### Scenario: README sections present
- **WHEN** the `README.md` is inspected
- **THEN** it contains sections for: project description, installation (pipx/uv/pip), usage (CLI commands), development setup, and license reference

#### Scenario: Installation instructions work
- **WHEN** a user follows the README installation instructions
- **THEN** mdreview is installed and the `mdreview` command is available

### Requirement: Contributing guide
The project SHALL include a CONTRIBUTING.md with development workflow instructions.

#### Scenario: Contributing guide present
- **WHEN** the `CONTRIBUTING.md` is inspected
- **THEN** it contains: development setup instructions, code style (ruff), testing instructions (pytest), and PR workflow

### Requirement: GitHub issue templates
The project SHALL include issue templates for bug reports and feature requests.

#### Scenario: Bug report template
- **WHEN** a user creates a new issue on GitHub
- **THEN** they can choose a "Bug Report" template with fields for steps to reproduce, expected behavior, actual behavior, and environment

#### Scenario: Feature request template
- **WHEN** a user creates a new issue on GitHub
- **THEN** they can choose a "Feature Request" template with fields for description and use case

### Requirement: Pull request template
The project SHALL include a PR template with a summary and test plan section.

#### Scenario: PR template applied
- **WHEN** a contributor opens a new pull request
- **THEN** the PR description is pre-filled with summary and test plan sections

### Requirement: CI workflow
The project SHALL include a GitHub Actions workflow that runs linting and tests on push and pull requests.

#### Scenario: CI runs on push to main
- **WHEN** code is pushed to the main branch
- **THEN** the CI workflow runs ruff linting and pytest across Python 3.10-3.13

#### Scenario: CI runs on pull request
- **WHEN** a pull request is opened or updated
- **THEN** the CI workflow runs ruff linting and pytest across Python 3.10-3.13

#### Scenario: CI fails on lint error
- **WHEN** the code has ruff violations
- **THEN** the CI workflow fails and reports the violations

#### Scenario: CI fails on test failure
- **WHEN** a test fails
- **THEN** the CI workflow fails and reports the test failure

### Requirement: Gitignore completeness
The project SHALL have a `.gitignore` that covers common Python, IDE, and OS artifacts.

#### Scenario: Standard patterns ignored
- **WHEN** the `.gitignore` is inspected
- **THEN** it includes patterns for: `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`, `dist/`, `build/`, `.review.json`, `.snapshot`, and common IDE files
