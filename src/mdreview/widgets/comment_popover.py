"""Comment popover widget for displaying comments on the current block."""

from __future__ import annotations

import textwrap

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static

from mdreview.models import Comment

POPOVER_INNER_WIDTH = 36  # chars available for text inside borders+padding


class CommentCard(Static):
    """A single comment displayed in the popover."""

    DEFAULT_CSS = """
    CommentCard {
        border: round $warning;
        padding: 0 1;
        margin-bottom: 1;
        background: $warning 5%;
        width: 1fr;
        height: auto;
    }

    CommentCard > Label {
        width: 1fr;
        height: auto;
    }

    CommentCard > Label.cc-header {
        color: $text-muted;
        text-style: italic;
    }

    CommentCard > Label.cc-body {
        padding-top: 0;
    }

    CommentCard > Label.cc-orphaned {
        color: $error;
        text-style: bold;
    }
    """

    def __init__(self, comment: Comment) -> None:
        super().__init__()
        self.comment = comment

    def compose(self) -> ComposeResult:
        range_str = (
            f"L{self.comment.line_start}"
            if self.comment.line_start == self.comment.line_end
            else f"L{self.comment.line_start}-{self.comment.line_end}"
        )
        yield Label(f"Comment ({range_str})", classes="cc-header")
        if self.comment.orphaned:
            yield Label("[anchor lost - text may have moved]", classes="cc-orphaned")
        yield Label(self.comment.body, classes="cc-body")


def _estimate_height(comments: list[Comment]) -> int:
    """Estimate the popover height in rows based on comment content.

    We compute this manually because Textual's auto-height doesn't work
    reliably for overlay-layer widgets outside the normal layout flow.
    """
    # Inner width for text wrapping (popover width minus borders, padding, card padding)
    wrap_width = POPOVER_INNER_WIDTH - 4  # card border(2) + card padding(2)
    total = 0
    for comment in comments:
        # Card border top/bottom = 2 rows
        total += 2
        # Header line ("Comment (L1-5)") = 1 row
        total += 1
        # Orphaned warning = 1 row
        if comment.orphaned:
            total += 1
        # Body: wrap text and count lines
        body_lines = 0
        for paragraph in comment.body.split("\n"):
            wrapped = textwrap.wrap(paragraph, width=wrap_width) or [""]
            body_lines += len(wrapped)
        total += body_lines
        # Margin-bottom between cards = 1 row
        total += 1
    # Help label "[d] delete  [e] edit" = 1 row + padding-top(1)
    if comments:
        total += 2
    # Popover border (top + bottom) = 2, padding (top + bottom) = 2
    total += 4
    return total


class CommentPopover(Widget):
    """Floating overlay showing comments for the current block.

    Positioned on the right side of the screen at the same vertical
    height as the cursor block. Uses explicit sizing since auto-height
    doesn't work for overlay-layer widgets.
    """

    DEFAULT_CSS = """
    CommentPopover {
        layer: overlay;
        background: $surface;
        border: thick $warning;
        padding: 1;
        display: none;
    }

    CommentPopover.visible {
        display: block;
    }

    CommentPopover > Label.cp-help {
        color: $text-muted;
        padding-top: 1;
        height: auto;
    }
    """

    class DeleteComment(Message):
        def __init__(self, comment_id: str) -> None:
            super().__init__()
            self.comment_id = comment_id

    _version = reactive(0, recompose=True)

    def __init__(self) -> None:
        super().__init__()
        self._comments: list[Comment] = []

    def compose(self) -> ComposeResult:
        for comment in self._comments:
            yield CommentCard(comment)
        if self._comments:
            yield Label("[d] delete  [e] edit", classes="cp-help")

    def show_comments(self, comments: list[Comment], block_y: int = 0) -> None:
        self._comments = comments
        if comments:
            self.add_class("visible")
            self._size_and_position(comments, block_y)
        else:
            self.remove_class("visible")
        self._version += 1

    def _size_and_position(self, comments: list[Comment], block_y: int) -> None:
        """Compute explicit size and position the popover."""
        try:
            screen_width = self.app.size.width
            screen_height = self.app.size.height

            # Width: fixed
            outer_width = POPOVER_INNER_WIDTH + 4  # + border(2) + padding(2)
            self.styles.width = outer_width

            # Height: computed from content
            h = _estimate_height(comments)
            max_h = screen_height - 4  # leave room for title + footer + margin
            h = min(h, max_h)
            self.styles.height = h

            # X: right-aligned
            x = screen_width - outer_width
            # Y: aligned to the cursor block, clamped to screen
            y = max(1, min(block_y, screen_height - h - 1))
            self.styles.offset = (x, y)
        except Exception:
            pass

    def hide(self) -> None:
        self.remove_class("visible")
        self._comments = []
        self._version += 1

    @property
    def active_comments(self) -> list[Comment]:
        return self._comments
