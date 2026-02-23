## ADDED Requirements

### Requirement: Default keybinding registry
The system SHALL define a `DEFAULT_BINDINGS` dictionary mapping action names to Textual key strings. Action names SHALL match the `action_*` method names in ReviewApp (without the `action_` prefix). This dictionary SHALL serve as the single source of truth for all default keybindings.

#### Scenario: All app actions have a default binding
- **WHEN** the `DEFAULT_BINDINGS` dictionary is loaded
- **THEN** it SHALL contain entries for all 18 actions: quit, files, comment, delete_comment, edit_comment, approve, request_changes, help, next_file, prev_file, cursor_up, cursor_down, select_up, select_down, open_mermaid, toggle_mermaid, toggle_diff, delete_all_comments

### Requirement: Load keybindings from TOML config
The system SHALL provide a `load_keybindings(path: Path | None) -> dict[str, str]` function that reads a TOML config file and merges user overrides with defaults.

#### Scenario: Config file exists with partial overrides
- **WHEN** `load_keybindings` is called with a path to a TOML file containing `[keys]` section with some action=key mappings
- **THEN** the returned dict SHALL contain the user's keys for overridden actions and default keys for all other actions

#### Scenario: Config file does not exist
- **WHEN** `load_keybindings` is called with a path that does not exist
- **THEN** the returned dict SHALL equal `DEFAULT_BINDINGS`

#### Scenario: Config file with no path provided
- **WHEN** `load_keybindings(None)` is called
- **THEN** the system SHALL check `~/.config/mdreview/keys.toml`; if it exists, load it; otherwise return `DEFAULT_BINDINGS`

#### Scenario: Config file contains unknown action name
- **WHEN** the TOML file contains a key under `[keys]` that does not match any known action name
- **THEN** the unknown entry SHALL be ignored and a warning printed to stderr

#### Scenario: Config file contains invalid TOML syntax
- **WHEN** the TOML file cannot be parsed
- **THEN** a warning SHALL be printed to stderr and `DEFAULT_BINDINGS` SHALL be returned

### Requirement: Config file creation with defaults
The system SHALL provide an `ensure_config(path: Path) -> Path` function that creates the config file populated with all default keybindings if it does not already exist.

#### Scenario: Config file does not exist yet
- **WHEN** `ensure_config` is called and the file does not exist
- **THEN** the file SHALL be created at the given path with a `[keys]` section containing all default action=key mappings and comments describing each action

#### Scenario: Config file already exists
- **WHEN** `ensure_config` is called and the file already exists
- **THEN** the existing file SHALL NOT be modified

### Requirement: CLI --config flag
The system SHALL accept a `--config` flag on the `mdreview` CLI command. When `--config` is passed, the app SHALL create the config file (via `ensure_config`) if it does not exist, then open it in `$EDITOR` (falling back to `vi`), and exit without launching the TUI.

#### Scenario: --config with no existing config
- **WHEN** `mdreview --config` is run and no config file exists
- **THEN** the config file SHALL be created at `~/.config/mdreview/keys.toml` with defaults, and opened in `$EDITOR`

#### Scenario: --config with existing config
- **WHEN** `mdreview --config` is run and the config file already exists
- **THEN** the existing file SHALL be opened in `$EDITOR` without modification

#### Scenario: --config with EDITOR unset
- **WHEN** `mdreview --config` is run and `$EDITOR` is not set
- **THEN** the system SHALL fall back to `vi`

### Requirement: Dynamic app bindings from config
The system SHALL build `ReviewApp.BINDINGS` dynamically from the loaded keybinding configuration at app initialization, rather than using hardcoded class-level bindings.

#### Scenario: App started with default config
- **WHEN** ReviewApp is initialized with no user config file
- **THEN** the app BINDINGS SHALL match the current hardcoded defaults

#### Scenario: App started with custom keybindings
- **WHEN** ReviewApp is initialized and the user config maps `quit` to `x` and `approve` to `a`
- **THEN** pressing `x` SHALL trigger quit and pressing `a` SHALL trigger approve; `q` and `A` SHALL have no effect

### Requirement: Key label display utility
The system SHALL provide a `key_label(key: str) -> str` function that converts Textual key strings into human-readable display labels.

#### Scenario: Special key names
- **WHEN** `key_label("question_mark")` is called
- **THEN** it SHALL return `"?"`

#### Scenario: Modifier combinations
- **WHEN** `key_label("shift+up")` is called
- **THEN** it SHALL return `"Shift+↑"`

#### Scenario: Simple letter keys
- **WHEN** `key_label("q")` is called
- **THEN** it SHALL return `"q"`
