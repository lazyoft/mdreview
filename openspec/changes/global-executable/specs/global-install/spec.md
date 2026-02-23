## ADDED Requirements

### Requirement: Complete package metadata
The `pyproject.toml` SHALL include all metadata fields required for PyPI publishing and tool discovery: description, authors, license, classifiers, readme, and project-urls.

#### Scenario: Metadata fields present
- **WHEN** the `pyproject.toml` is inspected
- **THEN** it contains: `description` (one-line summary), `authors` (name and email), `license` (SPDX identifier), `classifiers` (Python version, topic, environment), `readme` (path to README.md), and `project-urls` (Homepage, Repository, Issues)

### Requirement: Install via pipx
The package SHALL be installable via `pipx install .` (local) or `pipx install mdreview` (from PyPI when published), exposing the `mdreview` command globally.

#### Scenario: Local pipx install
- **WHEN** a user runs `pipx install .` from the project root
- **THEN** the `mdreview` command is available globally and `mdreview --help` displays usage information

#### Scenario: Global invocation after install
- **WHEN** `mdreview` is installed via pipx and the user runs `mdreview sample.md` from any directory
- **THEN** the application launches and displays the markdown file for review

### Requirement: Install via uv tool
The package SHALL be installable via `uv tool install .` (local) or `uv tool install mdreview` (from PyPI when published).

#### Scenario: Local uv tool install
- **WHEN** a user runs `uv tool install .` from the project root
- **THEN** the `mdreview` command is available globally and `mdreview --help` displays usage information

### Requirement: Isolated environment compatibility
The package SHALL install and run correctly in an isolated Python environment without access to dev dependencies or the project's `.venv`.

#### Scenario: No dev dependency leakage
- **WHEN** the package is installed in a fresh isolated environment
- **THEN** all runtime imports succeed without ImportError
