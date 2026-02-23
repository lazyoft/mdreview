"""Comment picker modal for selecting from multiple comments."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView

from mdreview.models import Comment


class CommentItem(ListItem):
    """A single comment entry in the picker."""

    def __init__(self, comment: Comment, index: int) -> None:
        super().__init__()
        self.comment = comment
        self.comment_index = index

    def compose(self) -> ComposeResult:
        range_str = (
            f"L{self.comment.line_start}"
            if self.comment.line_start == self.comment.line_end
            else f"L{self.comment.line_start}-{self.comment.line_end}"
        )
        # Truncate body to first line, max 40 chars
        first_line = self.comment.body.split("\n", 1)[0]
        preview = first_line[:40] + ("..." if len(first_line) > 40 else "")
        yield Label(f" {range_str}: {preview}")


class CommentPicker(ModalScreen[Comment | None]):
    """Modal for picking a comment from a list."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    DEFAULT_CSS = """
    CommentPicker {
        align: center middle;
    }

    CommentPicker > Vertical {
        width: 60;
        max-height: 60%;
        background: $surface;
        border: thick $accent;
        padding: 1 2;
    }

    CommentPicker > Vertical > Label#cpk-title {
        text-style: bold;
        padding-bottom: 1;
    }

    CommentPicker > Vertical > ListView {
        height: auto;
        max-height: 12;
    }

    CommentPicker > Vertical > Label#cpk-help {
        color: $text-muted;
        padding-top: 1;
    }
    """

    def __init__(self, comments: list[Comment], title: str = "Select comment") -> None:
        super().__init__()
        self._comments = comments
        self._title = title

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._title, id="cpk-title")
            items = [CommentItem(c, i) for i, c in enumerate(self._comments)]
            yield ListView(*items)
            yield Label(
                "\u2191\u2193 navigate  Enter select  Esc cancel", id="cpk-help"
            )

    @on(ListView.Selected)
    def on_list_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, CommentItem):
            self.dismiss(event.item.comment)

    def action_cancel(self) -> None:
        self.dismiss(None)
