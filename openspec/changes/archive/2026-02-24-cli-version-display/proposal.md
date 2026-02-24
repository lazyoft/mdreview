## Why

Users have no way to check which version of mdreview is installed. A `--version` flag is the standard way CLI tools expose this, and it helps with bug reports and troubleshooting.

## What Changes

- Add `--version` flag to the `mdreview` CLI command that prints the installed package version and exits
- Use `importlib.metadata.version()` to read the version at runtime (already set by hatch-vcs)

## Capabilities

### New Capabilities

- `cli-version`: CLI `--version` flag that prints the installed package version

### Modified Capabilities

None.

## Impact

- `src/mdreview/cli.py`: Add Click `version_option` decorator to the `main` command
- No new dependencies (uses stdlib `importlib.metadata`)
