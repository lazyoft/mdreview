## Context

All keybindings in mdreview are hardcoded in `ReviewApp.BINDINGS` (app.py), with matching hardcoded labels in `FooterBar` and `help_overlay.py`. There is no mechanism for users to remap keys. The project uses Textual's `Binding` system and Python 3.12+.

## Goals / Non-Goals

**Goals:**
- Users can customize any keybinding by editing a single config file
- `mdreview --config` creates the config (with all defaults) and opens it in `$EDITOR`
- Help overlay and footer bar dynamically reflect active keybindings
- Zero-config experience preserved — app works identically without a config file

**Non-Goals:**
- Per-file or per-project keybinding overrides
- Remapping keys inside modal screens (CommentInput, FileSelector, ConfirmDialog)
- GUI-based keybinding editor within the TUI
- Multi-key chord / sequence bindings

## Decisions

### 1. Config format: TOML

**Choice**: TOML at `~/.config/mdreview/keys.toml`

**Rationale**: Python 3.11+ includes `tomllib` in stdlib — no new dependency. TOML is human-friendly for simple key=value mappings. The config path follows XDG conventions on macOS/Linux.

**Alternatives considered**:
- JSON: Less readable for hand-editing, no comments
- YAML: Requires PyYAML dependency
- Python file: Security concerns with exec/import

### 2. Config file structure: flat action=key mapping

```toml
# ~/.config/mdreview/keys.toml
[keys]
quit = "q"
files = "f"
comment = "c"
delete_comment = "d"
edit_comment = "e"
approve = "A"
request_changes = "R"
help = "?"
next_file = "right"
prev_file = "left"
cursor_up = "up"
cursor_down = "down"
select_up = "shift+up"
select_down = "shift+down"
open_mermaid = "o"
toggle_mermaid = "m"
toggle_diff = "v"
delete_all_comments = "D"
```

**Rationale**: Flat mapping with action names as keys is simple to understand. Action names match the `action_*` method names in the app (minus the `action_` prefix). The generated config includes comments explaining each action.

**Alternative considered**: Nested sections by category (navigation, comments, etc.) — adds complexity without real benefit for ~18 keys.

### 3. New module: `keybindings.py`

A new `src/mdreview/keybindings.py` module handles:
- `DEFAULT_BINDINGS`: dict mapping action names to default Textual key strings
- `load_keybindings(path: Path | None) -> dict[str, str]`: reads TOML, merges with defaults
- `get_config_path() -> Path`: returns `~/.config/mdreview/keys.toml`
- `ensure_config(path: Path) -> Path`: creates config with defaults + comments if it doesn't exist
- `key_label(key: str) -> str`: converts Textual key strings to display labels (e.g., `"question_mark"` → `"?"`, `"shift+up"` → `"Shift+↑"`)

### 4. Dynamic BINDINGS in ReviewApp

**Choice**: Override `ReviewApp.__init__` to build `BINDINGS` from the loaded keybinding config rather than using the class-level `BINDINGS` constant.

**Rationale**: Textual's `Binding` objects are read at mount time. Setting `self.BINDINGS` in `__init__` before `compose`/`on_mount` run is the simplest approach.

### 5. `--config` CLI flag

**Choice**: Add `--config` as a standalone flag to `cli.py`. When passed, the app creates the config file (if needed) and opens it with `$EDITOR` (falling back to `vi`), then exits. It does NOT launch the TUI.

**Rationale**: Keeps the config workflow simple — one command to find, create, and edit your config. No need to remember file paths.

### 6. Dynamic help overlay and footer

**Choice**: Pass the active keybinding dict to `HelpOverlay` and `FooterBar` so they render labels from config rather than hardcoded strings.

**Rationale**: The help text and footer currently use hardcoded key labels. Making them config-aware ensures users always see their actual bindings.

## Risks / Trade-offs

- **Invalid key strings in config** → Validate keys at load time; warn on stderr and fall back to default for invalid entries
- **Duplicate keys (two actions mapped to same key)** → Detect at load time, warn on stderr, last-wins behavior (matches Textual behavior)
- **Config path doesn't exist on first run** → No config file needed by default; `--config` creates it. App works without it.
- **EDITOR not set** → Fall back to `vi` on Unix; print path and ask user to edit manually on failure
