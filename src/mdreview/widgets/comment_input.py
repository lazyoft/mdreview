"""Comment input modal widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, TextArea


class CommentInput(ModalScreen[str | None]):
    """Modal dialog for typing a new comment."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    DEFAULT_CSS = """
    CommentInput {
        align: center middle;
    }

    CommentInput > Vertical {
        width: 64;
        height: auto;
        max-height: 60%;
        background: $surface;
        border: thick $accent;
        padding: 1 2;
    }

    CommentInput > Vertical > Label#ci-title {
        text-style: bold;
        padding-bottom: 1;
    }

    CommentInput > Vertical > TextArea {
        height: 6;
        min-height: 3;
    }

    CommentInput > Vertical > Label#ci-help {
        color: $text-muted;
        padding-top: 1;
    }
    """

    def __init__(
        self,
        line_start: int,
        line_end: int,
        initial_text: str = "",
        title: str | None = None,
    ) -> None:
        super().__init__()
        self.line_start = line_start
        self.line_end = line_end
        self._initial_text = initial_text
        self._title = title

    def compose(self) -> ComposeResult:
        range_str = (
            f"L{self.line_start}"
            if self.line_start == self.line_end
            else f"L{self.line_start}-{self.line_end}"
        )
        label = self._title or f"Add Comment ({range_str})"
        with Vertical():
            yield Label(label, id="ci-title")
            yield TextArea(self._initial_text, id="ci-text")
            yield Label("Ctrl+S submit  |  Esc cancel", id="ci-help")

    def on_mount(self) -> None:
        self.query_one("#ci-text", TextArea).focus()

    def on_key(self, event) -> None:
        if event.key == "ctrl+s":
            text = self.query_one("#ci-text", TextArea).text.strip()
            if text:
                self.dismiss(text)
            event.stop()
            event.prevent_default()

    def action_cancel(self) -> None:
        self.dismiss(None)
