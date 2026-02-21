"""Custom Markdown widget with comment gutter/highlight support."""

from __future__ import annotations

from textual.widgets import Markdown
from textual.widgets._markdown import MarkdownBlock

from mdreview.models import Comment


class ReviewMarkdown(Markdown):
    """Markdown widget that highlights commented blocks and tracks a cursor."""

    DEFAULT_CSS = """
    ReviewMarkdown {
        height: auto;
    }

    /* All blocks get a constant left border so nothing shifts */
    ReviewMarkdown MarkdownBlock {
        border-left: wide transparent;
    }

    ReviewMarkdown MarkdownBlock.has-comment {
        border-left: wide $error;
        background: $error 8%;
    }

    ReviewMarkdown MarkdownBlock.cursor {
        border-left: wide $accent;
    }

    ReviewMarkdown MarkdownBlock.cursor.has-comment {
        border-left: wide $error;
        background: $error 15%;
    }

    ReviewMarkdown MarkdownBlock.selecting {
        border-left: wide $success;
        background: $success 10%;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cursor_index: int = 0
        self._comments: list[Comment] = []

    @property
    def blocks(self) -> list[MarkdownBlock]:
        return list(self.query(MarkdownBlock))

    @property
    def cursor_index(self) -> int:
        return self._cursor_index

    @cursor_index.setter
    def cursor_index(self, value: int) -> None:
        blocks = self.blocks
        if not blocks:
            return
        self._cursor_index = max(0, min(value, len(blocks) - 1))
        self._update_cursor_classes()

    @property
    def cursor_block(self) -> MarkdownBlock | None:
        blocks = self.blocks
        if blocks and 0 <= self._cursor_index < len(blocks):
            return blocks[self._cursor_index]
        return None

    def set_comments(self, comments: list[Comment]) -> None:
        """Update the comment list and refresh highlights."""
        self._comments = comments
        self._update_comment_classes()

    def _update_cursor_classes(self) -> None:
        for i, block in enumerate(self.blocks):
            if i == self._cursor_index:
                block.add_class("cursor")
            else:
                block.remove_class("cursor")

    def _update_comment_classes(self) -> None:
        for block in self.blocks:
            if self._block_has_comment(block):
                block.add_class("has-comment")
            else:
                block.remove_class("has-comment")

    def _block_has_comment(self, block: MarkdownBlock) -> bool:
        if not block.source_range:
            return False
        block_start, block_end = block.source_range
        for comment in self._comments:
            c_start = comment.line_start - 1
            c_end = comment.line_end
            if block_start < c_end and block_end > c_start:
                return True
        return False

    def comments_for_block(self, block: MarkdownBlock) -> list[Comment]:
        """Return all comments whose ranges overlap with this block."""
        if not block.source_range:
            return []
        block_start, block_end = block.source_range
        result = []
        for comment in self._comments:
            c_start = comment.line_start - 1
            c_end = comment.line_end
            if block_start < c_end and block_end > c_start:
                result.append(comment)
        return result

    def block_index_for_line(self, line: int) -> int | None:
        """Find the block index containing the given 1-indexed source line."""
        target = line - 1  # 0-indexed
        for i, block in enumerate(self.blocks):
            if block.source_range:
                start, end = block.source_range
                if start <= target < end:
                    return i
        return None

    def set_selection_range(self, start_idx: int, end_idx: int) -> None:
        """Mark blocks in range as 'selecting'."""
        lo, hi = min(start_idx, end_idx), max(start_idx, end_idx)
        for i, block in enumerate(self.blocks):
            if lo <= i <= hi:
                block.add_class("selecting")
            else:
                block.remove_class("selecting")

    def clear_selection(self) -> None:
        for block in self.blocks:
            block.remove_class("selecting")
