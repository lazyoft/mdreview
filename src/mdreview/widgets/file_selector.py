"""File selector popup widget."""

from __future__ import annotations

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView

from mdreview.models import ReviewStatus


class FileItem(ListItem):
    """A single file entry in the file selector."""

    def __init__(
        self, path: Path, status: ReviewStatus, comment_count: int, index: int
    ) -> None:
        super().__init__()
        self.file_path = path
        self.file_status = status
        self.comment_count = comment_count
        self.file_index = index

    def compose(self) -> ComposeResult:
        icon = self._status_icon()
        name = self.file_path.name
        parent = self.file_path.parent.name
        display = f"{parent}/{name}" if parent != "." else name

        count_str = (
            f"  {self.comment_count} comment{'s' if self.comment_count != 1 else ''}"
            if self.comment_count > 0
            else ""
        )
        yield Label(f" {icon}  {display}{count_str}")

    def _status_icon(self) -> str:
        match self.file_status:
            case ReviewStatus.APPROVED:
                return "\u2713"  # ✓
            case ReviewStatus.CHANGES_REQUESTED:
                return "\u25cf"  # ●
            case _:
                return "\u25cb"  # ○


class FileSelector(ModalScreen[int | None]):
    """Modal popup for selecting a file to review."""

    BINDINGS = [
        Binding("escape", "dismiss_selector", "Close"),
    ]

    DEFAULT_CSS = """
    FileSelector {
        align: center middle;
    }

    FileSelector > Vertical {
        width: 60;
        max-height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    FileSelector > Vertical > Label#fs-title {
        text-style: bold;
        width: 100%;
        content-align: center middle;
        padding-bottom: 1;
    }

    FileSelector > Vertical > ListView {
        height: auto;
        max-height: 20;
    }

    FileSelector > Vertical > Label#fs-help {
        color: $text-muted;
        padding-top: 1;
        content-align: center middle;
    }
    """

    class FileSelected(Message):
        def __init__(self, index: int) -> None:
            super().__init__()
            self.index = index

    def __init__(
        self,
        files: list[tuple[Path, ReviewStatus, int]],
        current_index: int = 0,
    ) -> None:
        super().__init__()
        self._files = files
        self._current_index = current_index

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Files", id="fs-title")
            items = []
            for i, (path, status, count) in enumerate(self._files):
                item = FileItem(path, status, count, i)
                items.append(item)
            yield ListView(*items, initial_index=self._current_index)
            yield Label("\u2191\u2193 navigate  Enter select  Esc close", id="fs-help")

    @on(ListView.Selected)
    def on_list_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, FileItem):
            self.dismiss(event.item.file_index)

    def action_dismiss_selector(self) -> None:
        self.dismiss(None)
