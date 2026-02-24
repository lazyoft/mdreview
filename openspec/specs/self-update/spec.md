### Requirement: Update flag triggers self-upgrade
The `mdreview` CLI SHALL support a `--update` flag that upgrades the package to the latest version from PyPI.

#### Scenario: User runs mdreview --update
- **WHEN** the user runs `mdreview --update`
- **THEN** the CLI detects the installation method, runs the appropriate upgrade command, and prints the result

#### Scenario: Update flag works without file arguments
- **WHEN** the user runs `mdreview --update` without providing any markdown files
- **THEN** the CLI performs the upgrade and exits (does not show "no files found" error)

### Requirement: Detect installation method
The CLI SHALL detect how mdreview was installed (pipx, uv tool, or pip) and use the corresponding upgrade command.

#### Scenario: Installed via pipx
- **WHEN** the mdreview executable path contains a pipx venvs directory
- **THEN** the CLI runs `pipx upgrade mdreview`

#### Scenario: Installed via uv tool
- **WHEN** the mdreview executable path contains a uv tools directory
- **THEN** the CLI runs `uv tool upgrade mdreview`

#### Scenario: Installed via pip
- **WHEN** the mdreview executable path does not match pipx or uv tool patterns
- **THEN** the CLI runs `pip install --upgrade mdreview`

### Requirement: Show version information during upgrade
The CLI SHALL print the current version before upgrading and report the outcome after.

#### Scenario: Successful upgrade
- **WHEN** the upgrade subprocess completes successfully
- **THEN** the CLI prints the previous version, the upgrade tool used, and exits with code 0

#### Scenario: Already up to date
- **WHEN** the upgrade subprocess completes and no newer version is available
- **THEN** the CLI prints that mdreview is already up to date and exits with code 0

### Requirement: Handle upgrade errors gracefully
The CLI SHALL report upgrade failures without crashing.

#### Scenario: Upgrade subprocess fails
- **WHEN** the upgrade command exits with a non-zero code
- **THEN** the CLI prints the error output and exits with a non-zero code
