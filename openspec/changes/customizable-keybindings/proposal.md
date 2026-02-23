## Why

All keybindings in mdreview are currently hardcoded in `app.py` and the help overlay. Users who prefer different key mappings (e.g., vim-style `j`/`k` navigation, or remapping conflicting keys) have no way to customize them without modifying source code.

## What Changes

- Add a keybinding configuration file (`~/.config/mdreview/keys.toml`) with all default keybindings pre-populated — users edit this file to customize
- Add `mdreview --config` CLI command that creates the config file (with defaults) if it doesn't exist and opens it in `$EDITOR` for editing
- Load and merge user keybindings at app startup, falling back to built-in defaults for any unspecified keys
- Update the help overlay to dynamically reflect the active (possibly customized) keybindings
- Update the footer bar hints to reflect active keybindings
- Update the README with config file location and usage instructions

## Capabilities

### New Capabilities
- `custom-keybindings`: User-configurable key mappings loaded from a TOML config file, with defaults preserved for unmapped actions

### Modified Capabilities
- `review-operations`: The help overlay and footer bar must dynamically display the active keybinding for each action rather than hardcoded key labels

## Impact

- **Code**: `app.py` (binding definitions, footer bar), `help_overlay.py` (dynamic key labels), new `keybindings.py` module for config loading/merging
- **Dependencies**: None new — Python stdlib `tomllib` (3.11+) handles TOML parsing; the project already requires Python 3.12+
- **Config**: New optional config file at `~/.config/mdreview/keys.toml` (created via `--config`)
- **CLI**: New `--config` flag in `cli.py` to open the keybindings config in `$EDITOR`
- **Docs**: README updated with keybinding customization section
