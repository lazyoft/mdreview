## ADDED Requirements

### Requirement: Version flag prints installed version
The `mdreview` CLI SHALL support a `--version` flag that prints the installed package version and exits.

#### Scenario: User runs mdreview --version
- **WHEN** the user runs `mdreview --version`
- **THEN** the CLI prints the package name and version (e.g., `mdreview, version 0.1.0`) and exits with code 0

#### Scenario: Version flag takes precedence over missing files
- **WHEN** the user runs `mdreview --version` without providing any markdown files
- **THEN** the CLI prints the version and exits with code 0 (does not show "no files found" error)
