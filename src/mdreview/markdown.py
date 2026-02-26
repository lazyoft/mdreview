"""Custom Markdown widget with comment gutter/highlight support."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable

from markdown_it import MarkdownIt
from textual.await_complete import AwaitComplete
from textual.widgets import Markdown, Static
from textual.widgets._markdown import (
    HEADINGS,
    MarkdownBlock,
    MarkdownBlockQuote,
    MarkdownBulletList,
    MarkdownFence,
    MarkdownHorizontalRule,
    MarkdownOrderedList,
    MarkdownOrderedListItem,
    MarkdownParagraph,
    MarkdownTable,
    MarkdownTBody,
    MarkdownTD,
    MarkdownTH,
    MarkdownTHead,
    MarkdownTR,
    MarkdownUnorderedListItem,
)

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

    def update(self, markdown: str) -> AwaitComplete:
        """Override to attach source_range from token.map onto each block."""
        parser = (
            MarkdownIt("gfm-like")
            if self._parser_factory is None
            else self._parser_factory()
        )

        table_of_contents: list[tuple[int, str, str | None]] = []

        def parse_markdown(tokens) -> Iterable[MarkdownBlock]:
            stack: list[MarkdownBlock] = []
            # Track the token.map for the opening token of each stack level
            map_stack: list[list[int] | None] = []
            block_id: int = 0

            for token in tokens:
                token_type = token.type
                if token_type == "heading_open":
                    block_id += 1
                    blk = HEADINGS[token.tag](self, id=f"block{block_id}")
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "hr":
                    blk = MarkdownHorizontalRule(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    yield blk
                elif token_type == "paragraph_open":
                    blk = MarkdownParagraph(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "blockquote_open":
                    blk = MarkdownBlockQuote(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "bullet_list_open":
                    blk = MarkdownBulletList(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "ordered_list_open":
                    blk = MarkdownOrderedList(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "list_item_open":
                    if token.info:
                        blk = MarkdownOrderedListItem(self, token.info)
                    else:
                        item_count = sum(
                            1
                            for b in stack
                            if isinstance(b, MarkdownUnorderedListItem)
                        )
                        blk = MarkdownUnorderedListItem(
                            self,
                            self.BULLETS[item_count % len(self.BULLETS)],
                        )
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "table_open":
                    blk = MarkdownTable(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "tbody_open":
                    blk = MarkdownTBody(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "thead_open":
                    blk = MarkdownTHead(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "tr_open":
                    blk = MarkdownTR(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "th_open":
                    blk = MarkdownTH(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type == "td_open":
                    blk = MarkdownTD(self)
                    blk.source_range = tuple(token.map) if token.map else None
                    stack.append(blk)
                    map_stack.append(token.map)
                elif token_type.endswith("_close"):
                    block = stack.pop()
                    map_stack.pop()
                    if token.type == "heading_close":
                        heading = block._text.plain
                        level = int(token.tag[1:])
                        table_of_contents.append((level, heading, block.id))
                    if stack:
                        stack[-1]._blocks.append(block)
                    else:
                        yield block
                elif token_type == "inline":
                    stack[-1].build_from_token(token)
                elif token_type in ("fence", "code_block"):
                    fence = MarkdownFence(
                        self, token.content.rstrip(), token.info
                    )
                    fence.source_range = tuple(token.map) if token.map else None
                    if stack:
                        stack[-1]._blocks.append(fence)
                    else:
                        yield fence
                else:
                    external = self.unhandled_token(token)
                    if external is not None:
                        if token.map:
                            external.source_range = tuple(token.map)
                        if stack:
                            stack[-1]._blocks.append(external)
                        else:
                            yield external

        markdown_block = self.query("MarkdownBlock")

        async def await_update() -> None:
            BATCH_SIZE = 200
            batch: list[MarkdownBlock] = []
            tokens = await asyncio.get_running_loop().run_in_executor(
                None, parser.parse, markdown
            )

            async with self.lock:
                removed: bool = False

                async def mount_batch(batch: list[MarkdownBlock]) -> None:
                    nonlocal removed
                    if removed:
                        await self.mount_all(batch)
                    else:
                        with self.app.batch_update():
                            await markdown_block.remove()
                            await self.mount_all(batch)
                        removed = True

                for block in parse_markdown(tokens):
                    batch.append(block)
                    if len(batch) == BATCH_SIZE:
                        await mount_batch(batch)
                        batch.clear()
                if batch:
                    await mount_batch(batch)
                if not removed:
                    await markdown_block.remove()

            self._table_of_contents = table_of_contents
            self.post_message(
                Markdown.TableOfContentsUpdated(
                    self, self._table_of_contents
                ).set_sender(self)
            )

        return AwaitComplete(await_update())

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
