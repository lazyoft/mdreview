## Why

Users who install mdreview globally (via pipx or uv tool) have no built-in way to check for or install newer versions. A self-update command lets them upgrade without remembering which tool they used to install.

## What Changes

- Add a `mdreview --update` flag that upgrades the package to the latest version using pip
- Detect the current installation method (pipx, uv tool, pip) and use the appropriate upgrade command
- Print the current and new version before/after the upgrade

## Capabilities

### New Capabilities

- `self-update`: CLI `--update` flag that upgrades mdreview to the latest version

### Modified Capabilities

None.

## Impact

- `src/mdreview/cli.py`: Add `--update` flag with upgrade logic
- No new dependencies (uses `subprocess` to invoke pip/pipx/uv)
- Requires the package to be published to PyPI (or installable from a git URL) for remote upgrades
