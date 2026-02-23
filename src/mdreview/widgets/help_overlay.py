"""Help overlay showing all keybindings."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label

HELP_TEXT = """\
 Navigation
   Up / Down       Move cursor between blocks
   Left / Right    Previous / next file
   PgUp / PgDn     Scroll page
   Home / End      Jump to start / end

 Comments
   c               Start/confirm line selection
   Shift+Up/Down   Start or extend selection
   Ctrl+S          Submit comment
   d               Delete comment (when popover visible)
   D               Delete all comments on file
   Esc             Cancel selection or input

 Files
   f               Open file selector

 Review
   A               Approve document
   R               Request changes

 Diff
   v               Toggle diff view (changes since last review)

 Mermaid
   o               Open diagram in browser
   m               Toggle ASCII / raw source

 General
   ?               Toggle this help
   q               Quit"""


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

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Keybindings", id="help-title")
            yield Label(HELP_TEXT, id="help-body")
            yield Label("Press Esc or ? to close", id="help-footer")

    def action_dismiss_help(self) -> None:
        self.dismiss(None)
