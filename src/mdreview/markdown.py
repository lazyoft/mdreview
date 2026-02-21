"""Custom Markdown widget with comment gutter/highlight support."""

from __future__ import annotations

from textual.widgets import Markdown, Static
from textual.widgets._markdown import MarkdownBlock

from mdreview.models import Comment


class DiffPlaceholder(Static):
    """Placeholder widget for diff context (old content or removed content)."""

    DEFAULT_CSS = """
    DiffPlaceholder {
        border-left: wide #e05050;
        background: #3d1515;
        color: #e08080;
        padding: 0 0;
        height: auto;
    }
    """


class ReviewMarkdown(Markdown):
    """Markdown widget that highlights commented blocks and tracks a cursor."""

    DEFAULT_CSS = """
    ReviewMarkdown {
        height: auto;
    }

    /* Constant left border so nothing shifts */
    ReviewMarkdown MarkdownBlock {
        border-left: wide transparent;
    }

    /* Comments: blue */
    ReviewMarkdown MarkdownBlock.has-comment {
        border-left: wide #6090d0;
        background: #152040;
    }

    /* Diff: green */
    ReviewMarkdown MarkdownBlock.diff-changed {
        border-left: wide #50b050;
        background: #153d15;
    }

    ReviewMarkdown MarkdownBlock.diff-new {
        border-left: wide #50b050;
        background: #153d15;
    }

    /* Selection */
    ReviewMarkdown MarkdownBlock.selecting {
        border-left: wide $success;
        background: $success 10%;
    }

    /* Cursor: LAST so it always wins for border-left.
       Background from comments/diff still shows through. */
    ReviewMarkdown MarkdownBlock.cursor {
        border-left: wide $accent;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cursor_index: int = 0
        self._comments: list[Comment] = []
        self._diff_tags: list[str] = []

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

    @property
    def diff_tags(self) -> list[str]:
        return self._diff_tags

    def set_comments(self, comments: list[Comment]) -> None:
        """Update the comment list and refresh highlights."""
        self._comments = comments
        self._update_comment_classes()

    def apply_diff(self, diffs: list, removed_blocks: list) -> None:
        """Apply diff results: tag blocks, inject old-content and removed placeholders."""
        from mdreview.diff import BlockDiff, RemovedBlock

        blocks = self.blocks
        self._diff_tags = [d.tag for d in diffs]
        self._update_diff_classes()

        # Collect changed blocks that need old-content placeholders
        # Process in reverse so mount operations don't shift indices
        for i in range(len(blocks) - 1, -1, -1):
            if i < len(diffs) and diffs[i].tag == "changed" and diffs[i].old_lines:
                old_text = "\n".join(diffs[i].old_lines)
                placeholder = DiffPlaceholder(old_text)
                self.mount(placeholder, before=blocks[i])

        # Inject removed-block placeholders
        for rb in sorted(removed_blocks, key=lambda r: r.after_line, reverse=True):
            insert_after = None
            for block in blocks:
                if block.source_range and block.source_range[0] >= rb.after_line:
                    break
                insert_after = block
            lines = rb.content.splitlines()
            if len(lines) > 5:
                preview = "\n".join(lines[:5]) + f"\n... ({len(lines) - 5} more lines)"
            else:
                preview = rb.content
            placeholder = DiffPlaceholder(preview)
            if insert_after is not None:
                self.mount(placeholder, after=insert_after)
            elif blocks:
                self.mount(placeholder, before=blocks[0])

    def clear_diff(self) -> None:
        """Remove all diff styling and placeholders."""
        self._diff_tags = []
        for block in self.blocks:
            block.remove_class("diff-changed")
            block.remove_class("diff-new")
        for placeholder in self.query(DiffPlaceholder):
            placeholder.remove()

    def _update_diff_classes(self) -> None:
        blocks = self.blocks
        for i, block in enumerate(blocks):
            block.remove_class("diff-changed")
            block.remove_class("diff-new")
            if i < len(self._diff_tags):
                tag = self._diff_tags[i]
                if tag == "changed":
                    block.add_class("diff-changed")
                elif tag == "new":
                    block.add_class("diff-new")

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

    def diff_tag_for_block(self, block: MarkdownBlock) -> str | None:
        """Return the diff tag for a block, or None if no diff active."""
        if not self._diff_tags:
            return None
        blocks = self.blocks
        try:
            idx = blocks.index(block)
        except ValueError:
            return None
        if idx < len(self._diff_tags):
            return self._diff_tags[idx]
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
