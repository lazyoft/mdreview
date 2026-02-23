"""Help overlay showing all keybindings."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label

from mdreview.keybindings import DEFAULT_BINDINGS, key_label


def _build_help_text(keys: dict[str, str]) -> str:
    """Build the help text from the active keybinding configuration."""
    k = {action: key_label(key) for action, key in keys.items()}

    return f"""\
 Navigation
   {k["cursor_up"]:15s} Move cursor between blocks
   / {k["cursor_down"]}
   {k["prev_file"]:15s} Previous / next file
   / {k["next_file"]}
   PgUp / PgDn     Scroll page
   Home / End      Jump to start / end

 Comments
   {k["comment"]:15s} Start/confirm line selection
   {k["select_up"]}/{k["select_down"]:<10s} Start or extend selection
   Ctrl+S          Submit comment
   {k["delete_comment"]:15s} Delete comment (when popover visible)
   {k["delete_all_comments"]:15s} Delete all comments on file
   Esc             Cancel selection or input

 Files
   {k["open_file_selector"]:15s} Open file selector

 Review
   {k["approve"]:15s} Approve document
   {k["request_changes"]:15s} Request changes

 Diff
   {k["toggle_diff"]:15s} Toggle diff view (changes since last review)

 Mermaid
   {k["open_mermaid"]:15s} Open diagram in browser
   {k["toggle_mermaid"]:15s} Toggle ASCII / raw source

 General
   {k["show_help"]:15s} Toggle this help
   {k["quit"]:15s} Quit"""


class HelpOverlay(ModalScreen[None]):
    """Modal help screen showing keybindings."""

    BINDINGS = [
        Binding("escape", "dismiss_help", "Close"),
        Binding("question_mark", "dismiss_help", "Close"),
    ]

    DEFAULT_CSS = """
    HelpOverlay {
        align: center middle;
    }

    HelpOverlay > Vertical {
        width: 52;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    HelpOverlay > Vertical > Label#help-title {
        text-style: bold;
        content-align: center middle;
        width: 100%;
        padding-bottom: 1;
    }

    HelpOverlay > Vertical > Label#help-body {
        height: auto;
    }

    HelpOverlay > Vertical > Label#help-footer {
        color: $text-muted;
        padding-top: 1;
        content-align: center middle;
    }
    """

    def __init__(self, keybindings: dict[str, str] | None = None) -> None:
        super().__init__()
        self._keybindings = keybindings or dict(DEFAULT_BINDINGS)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Keybindings", id="help-title")
            yield Label(_build_help_text(self._keybindings), id="help-body")
            yield Label("Press Esc or ? to close", id="help-footer")

    def action_dismiss_help(self) -> None:
        self.dismiss(None)
