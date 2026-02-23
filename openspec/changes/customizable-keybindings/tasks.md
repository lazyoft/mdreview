## 0. Branch Setup

- [ ] 0.1 Create a new branch `feat/customizable-keybindings` from main and work there
- [ ] 0.2 Ensure `.claude/` directory is excluded from commits (add to `.gitignore` if not already)

## 1. Keybindings Module

- [ ] 1.1 Create `src/mdreview/keybindings.py` with `DEFAULT_BINDINGS` dict mapping all 18 action names to their default Textual key strings
- [ ] 1.2 Implement `get_config_path() -> Path` returning `~/.config/mdreview/keys.toml`
- [ ] 1.3 Implement `load_keybindings(path: Path | None) -> dict[str, str]` that reads TOML, merges with defaults, warns on unknown keys or parse errors
- [ ] 1.4 Implement `ensure_config(path: Path) -> Path` that creates the config file with all defaults and comments if it doesn't exist
- [ ] 1.5 Implement `key_label(key: str) -> str` that converts Textual key strings to display labels (e.g., `question_mark` → `?`, `shift+up` → `Shift+↑`)

## 2. CLI --config Flag

- [ ] 2.1 Add `--config` flag to `cli.py` that calls `ensure_config`, opens the file in `$EDITOR` (fallback `vi`), and exits without launching the TUI

## 3. Dynamic App Bindings

- [ ] 3.1 Update `ReviewApp.__init__` to accept a keybindings dict and build `self.BINDINGS` dynamically from it instead of using the class-level `BINDINGS` constant
- [ ] 3.2 Update `cli.py` to call `load_keybindings` and pass the result to `ReviewApp`

## 4. Dynamic Help Overlay

- [ ] 4.1 Update `HelpOverlay` to accept the active keybinding dict and render help text using `key_label()` instead of hardcoded strings

## 5. Dynamic Footer Bar

- [ ] 5.1 Update `FooterBar` to accept the active keybinding dict and render hint labels using `key_label()` instead of hardcoded strings
- [ ] 5.2 Update `ReviewApp` to pass keybindings to `FooterBar` on initialization

## 6. Tests

- [ ] 6.1 Add tests for `load_keybindings` (default fallback, partial override, missing file, invalid TOML, unknown keys)
- [ ] 6.2 Add tests for `ensure_config` (creates file with defaults, preserves existing)
- [ ] 6.3 Add tests for `key_label` (special keys, modifiers, simple letters)
- [ ] 6.4 Add tests for dynamic bindings integration (app uses custom keys)

## 7. Documentation

- [ ] 7.1 Update README with keybinding customization section (config location, `--config` usage, example overrides)
