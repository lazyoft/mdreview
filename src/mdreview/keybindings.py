"""Keybinding configuration: defaults, loading, and display utilities."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

# Action name -> default Textual key string.
# Action names match ReviewApp.action_* methods (minus the "action_" prefix).
DEFAULT_BINDINGS: dict[str, str] = {
    "quit": "q",
    "open_file_selector": "f",
    "comment": "c",
    "delete_comment": "d",
    "edit_comment": "e",
    "approve": "A",
    "request_changes": "R",
    "show_help": "question_mark",
    "next_file": "right",
    "prev_file": "left",
    "cursor_up": "up",
    "cursor_down": "down",
    "select_up": "shift+up",
    "select_down": "shift+down",
    "open_mermaid": "o",
    "toggle_mermaid": "m",
    "toggle_diff": "v",
    "delete_all_comments": "D",
}

# Human-readable descriptions for each action (used in generated config).
ACTION_DESCRIPTIONS: dict[str, str] = {
    "quit": "Quit the application",
    "open_file_selector": "Open file selector",
    "comment": "Start/confirm line selection for comment",
    "delete_comment": "Delete comment on current block",
    "edit_comment": "Edit comment on current block",
    "approve": "Approve current document",
    "request_changes": "Request changes on current document",
    "show_help": "Toggle help overlay",
    "next_file": "Next file",
    "prev_file": "Previous file",
    "cursor_up": "Move cursor up",
    "cursor_down": "Move cursor down",
    "select_up": "Extend selection up",
    "select_down": "Extend selection down",
    "open_mermaid": "Open mermaid diagram in browser",
    "toggle_mermaid": "Toggle mermaid ASCII/raw",
    "toggle_diff": "Toggle diff view",
    "delete_all_comments": "Delete all comments on file",
}

# Display-friendly descriptions used in the Binding objects.
ACTION_LABELS: dict[str, str] = {
    "quit": "Quit",
    "open_file_selector": "Files",
    "comment": "Comment",
    "delete_comment": "Delete comment",
    "edit_comment": "Edit comment",
    "approve": "Approve",
    "request_changes": "Request changes",
    "show_help": "Help",
    "next_file": "Next file",
    "prev_file": "Previous file",
    "cursor_up": "Up",
    "cursor_down": "Down",
    "select_up": "Select up",
    "select_down": "Select down",
    "open_mermaid": "Open mermaid",
    "toggle_mermaid": "Toggle mermaid",
    "toggle_diff": "Toggle diff",
    "delete_all_comments": "Delete all comments",
}

# Mapping of Textual key names to display characters.
_KEY_DISPLAY: dict[str, str] = {
    "question_mark": "?",
    "up": "\u2191",
    "down": "\u2193",
    "left": "\u2190",
    "right": "\u2192",
    "escape": "Esc",
    "enter": "Enter",
    "tab": "Tab",
    "space": "Space",
    "backspace": "Backspace",
    "delete": "Delete",
    "home": "Home",
    "end": "End",
    "pageup": "PgUp",
    "pagedown": "PgDn",
}

_MODIFIER_DISPLAY: dict[str, str] = {
    "shift": "Shift",
    "ctrl": "Ctrl",
    "alt": "Alt",
}


def get_config_path() -> Path:
    """Return the default config file path: ~/.config/mdreview/keys.toml."""
    return Path.home() / ".config" / "mdreview" / "keys.toml"


def load_keybindings(path: Path | None = None) -> dict[str, str]:
    """Load keybindings from a TOML file, merged with defaults.

    If path is None, checks the default config path. If the file doesn't
    exist, returns DEFAULT_BINDINGS unchanged.
    """
    if path is None:
        path = get_config_path()

    if not path.exists():
        return dict(DEFAULT_BINDINGS)

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"Warning: failed to parse {path}: {e}", file=sys.stderr)
        return dict(DEFAULT_BINDINGS)

    user_keys = data.get("keys", {})
    if not isinstance(user_keys, dict):
        print(f"Warning: [keys] in {path} is not a table, ignoring", file=sys.stderr)
        return dict(DEFAULT_BINDINGS)

    result = dict(DEFAULT_BINDINGS)
    for action, key in user_keys.items():
        if action not in DEFAULT_BINDINGS:
            print(
                f"Warning: unknown action '{action}' in {path}, ignoring",
                file=sys.stderr,
            )
            continue
        if not isinstance(key, str):
            print(
                f"Warning: value for '{action}' in {path} is not a string, ignoring",
                file=sys.stderr,
            )
            continue
        result[action] = key

    return result


def ensure_config(path: Path | None = None) -> Path:
    """Create the config file with defaults if it doesn't exist. Returns the path."""
    if path is None:
        path = get_config_path()

    if path.exists():
        return path

    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# mdreview keybinding configuration",
        "# Edit keys below to customize.",
        "",
        "[keys]",
    ]
    for action, default_key in DEFAULT_BINDINGS.items():
        desc = ACTION_DESCRIPTIONS.get(action, "")
        lines.append(f"# {desc}")
        lines.append(f'{action} = "{default_key}"')
        lines.append("")

    path.write_text("\n".join(lines) + "\n")
    return path


def key_label(key: str) -> str:
    """Convert a Textual key string to a human-readable display label.

    Examples:
        "question_mark" -> "?"
        "shift+up" -> "Shift+\u2191"
        "q" -> "q"
    """
    parts = key.split("+")
    display_parts = []
    for part in parts:
        if part in _MODIFIER_DISPLAY:
            display_parts.append(_MODIFIER_DISPLAY[part])
        elif part in _KEY_DISPLAY:
            display_parts.append(_KEY_DISPLAY[part])
        else:
            display_parts.append(part)
    return "+".join(display_parts)
