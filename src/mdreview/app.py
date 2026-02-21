"""Main ReviewApp TUI application."""

from __future__ import annotations

import webbrowser
from datetime import datetime, timezone
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Static

from mdreview.diff import compute_block_diff
from mdreview.markdown import ReviewMarkdown
from mdreview.mermaid import preprocess_mermaid
from mdreview.models import Comment, ReviewFile, ReviewStatus
from mdreview.storage import (
    compute_hash,
    load_review,
    load_snapshot,
    reconcile_drift,
    save_review,
    save_snapshot,
)
from mdreview.widgets.comment_input import CommentInput
from mdreview.widgets.comment_popover import CommentPopover
from mdreview.widgets.file_selector import FileSelector

from mdreview.widgets.help_overlay import HelpOverlay


class TitleBar(Static):
    """Title bar showing filename, position, and status dots."""

    DEFAULT_CSS = """
    TitleBar {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 2;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._filename = ""
        self._index = 0
        self._total = 0
        self._statuses: list[ReviewStatus] = []

    def set_state(
        self,
        filename: str,
        index: int,
        total: int,
        statuses: list[ReviewStatus],
    ) -> None:
        self._filename = filename
        self._index = index
        self._total = total
        self._statuses = statuses
        self._refresh_display()

    def _refresh_display(self) -> None:
        dots = []
        for i, status in enumerate(self._statuses):
            match status:
                case ReviewStatus.APPROVED:
                    dots.append("\u2713" if i != self._index else "[\u2713]")
                case ReviewStatus.CHANGES_REQUESTED:
                    dots.append("\u25cf" if i != self._index else "[\u25cf]")
                case _:
                    dots.append("\u25cb" if i != self._index else "[\u25cb]")

        dots_str = " ".join(dots)
        pos = f"[{self._index + 1}/{self._total}]"
        self.update(f" {dots_str}  {pos}  {self._filename}")


class FooterBar(Static):
    """Bottom bar showing available keybindings."""

    DEFAULT_CSS = """
    FooterBar {
        dock: bottom;
        height: 1;
        background: $primary-darken-2;
        color: $text;
        padding: 0 1;
    }
    """

    NORMAL_BASE = (
        " [bold ansi_bright_yellow]c[/] comment  "
        "[bold ansi_bright_yellow]f[/] files  "
        "[bold ansi_bright_yellow]\u2190\u2192[/] prev/next  "
        "[bold ansi_bright_yellow]A[/] approve  "
        "[bold ansi_bright_yellow]R[/] request changes  "
    )
    DIFF_HINT = "[bold ansi_bright_yellow]v[/] diff  "
    NORMAL_TAIL = (
        "[bold ansi_bright_yellow]?[/] help  "
        "[bold ansi_bright_yellow]q[/] quit"
    )
    SELECTING = (
        " [bold ansi_bright_yellow]c[/] confirm selection  "
        "[bold ansi_bright_yellow]Shift+\u2191\u2193[/] extend  "
        "[bold ansi_bright_yellow]Esc[/] cancel"
    )

    def __init__(self) -> None:
        super().__init__()
        self._mode = "normal"
        self._diff_available = False

    def set_mode(self, mode: str = "normal") -> None:
        self._mode = mode
        self._refresh()

    def set_diff_available(self, available: bool) -> None:
        self._diff_available = available
        self._refresh()

    def _refresh(self) -> None:
        if self._mode == "selecting":
            self.update(self.SELECTING)
        else:
            text = self.NORMAL_BASE
            if self._diff_available:
                text += self.DIFF_HINT
            text += self.NORMAL_TAIL
            self.update(text)


class ReviewApp(App):
    """Main TUI application for reviewing markdown documents."""

    BINDINGS = [
        Binding("q", "quit_app", "Quit", priority=True),
        Binding("f", "open_file_selector", "Files", priority=True),
        Binding("c", "comment", "Comment", priority=True),
        Binding("d", "delete_comment", "Delete comment", priority=True),
        Binding("e", "edit_comment", "Edit comment", priority=True),
        Binding("A", "approve", "Approve", priority=True),
        Binding("R", "request_changes", "Request changes", priority=True),
        Binding("question_mark", "show_help", "Help", priority=True),
        Binding("right", "next_file", "Next file", priority=True),
        Binding("left", "prev_file", "Previous file", priority=True),
        Binding("up", "cursor_up", "Up", priority=True),
        Binding("down", "cursor_down", "Down", priority=True),
        Binding("shift+up", "select_up", "Select up", priority=True),
        Binding("shift+down", "select_down", "Select down", priority=True),
        Binding("o", "open_mermaid", "Open mermaid", priority=True),
        Binding("m", "toggle_mermaid", "Toggle mermaid", priority=True),
        Binding("v", "toggle_diff", "Toggle diff", priority=True),
    ]

    DEFAULT_CSS = """
    ReviewApp {
        layout: vertical;
    }

    #content-scroll {
        height: 1fr;
    }
    """

    def __init__(self, files: list[Path]) -> None:
        super().__init__()
        self._files = files
        self._current_index = 0
        self._reviews: list[ReviewFile] = []
        self._lines: dict[int, list[str]] = {}  # file index -> source lines
        self._mermaid_data: dict[int, list[dict]] = {}  # file index -> mermaid diagrams
        self._mermaid_ascii_on: dict[int, bool] = {}  # file index -> show ascii?
        self._scroll_positions: dict[int, float] = {}
        self._selecting = False
        self._selection_start: int | None = None
        self._exit_code = 2  # incomplete by default
        self._snapshots: dict[int, str | None] = {}  # file index -> snapshot content
        self._diff_available: dict[int, bool] = {}  # file index -> diff available?
        self._diff_mode: dict[int, bool] = {}  # file index -> diff mode on?

        # Load reviews
        for i, path in enumerate(files):
            content = path.read_text()
            self._lines[i] = content.splitlines()
            review = load_review(path)
            current_hash = compute_hash(content)

            if (
                review.content_hash
                and review.content_hash != current_hash
                and review.comments
            ):
                reconcile_drift(review, self._lines[i])

            review.content_hash = current_hash
            self._reviews.append(review)
            self._mermaid_ascii_on[i] = True

            snapshot = load_snapshot(path)
            self._snapshots[i] = snapshot
            has_diff = snapshot is not None and snapshot != content
            self._diff_available[i] = has_diff
            self._diff_mode[i] = False

    def compose(self) -> ComposeResult:
        yield TitleBar()
        with ScrollableContainer(id="content-scroll"):
            yield ReviewMarkdown()
        yield CommentPopover()
        yield FooterBar()

    def on_mount(self) -> None:
        self._load_file(0)
        self.query_one(FooterBar).set_mode("normal")

    def _load_file(self, index: int) -> None:
        # Save scroll position of current file
        try:
            scroll = self.query_one("#content-scroll", ScrollableContainer)
            self._scroll_positions[self._current_index] = scroll.scroll_y
        except Exception:
            pass

        self._current_index = index
        path = self._files[index]
        content = path.read_text()

        # Preprocess mermaid
        if self._mermaid_ascii_on.get(index, True):
            processed, diagrams = preprocess_mermaid(content, render_ascii=True)
        else:
            processed, diagrams = preprocess_mermaid(content, render_ascii=False)
        self._mermaid_data[index] = diagrams

        md = self.query_one(ReviewMarkdown)
        md.update(processed)

        # Need to defer comment/cursor setup until after markdown is rendered
        self.set_timer(0.1, self._post_load)

    def _post_load(self) -> None:
        idx = self._current_index
        md = self.query_one(ReviewMarkdown)
        review = self._reviews[idx]
        md.set_comments(review.comments)
        md.cursor_index = 0

        # Apply diff if available and enabled
        self._apply_diff_if_needed()

        # Notify about unchanged files
        snapshot = self._snapshots.get(idx)
        if snapshot is not None and not self._diff_available.get(idx, False):
            self._notify("No changes since last review")

        self._update_popover()
        self._update_title_bar()
        self._update_footer()

        # Restore scroll position
        saved = self._scroll_positions.get(idx, 0)
        if saved:
            scroll = self.query_one("#content-scroll", ScrollableContainer)
            scroll.scroll_y = saved

    def _update_title_bar(self) -> None:
        path = self._files[self._current_index]
        parent = path.parent.name
        name = path.name
        display = f"{parent}/{name}" if parent and parent != "/" else name

        statuses = [r.status for r in self._reviews]
        self.query_one(TitleBar).set_state(
            display, self._current_index, len(self._files), statuses
        )

    def _update_footer(self) -> None:
        footer = self.query_one(FooterBar)
        footer.set_diff_available(self._diff_available.get(self._current_index, False))

    def _update_popover(self) -> None:
        md = self.query_one(ReviewMarkdown)
        popover = self.query_one(CommentPopover)
        block = md.cursor_block
        if block:
            comments = md.comments_for_block(block)
            # Get block's Y position relative to the screen
            try:
                block_region = block.region
                scroll = self.query_one("#content-scroll", ScrollableContainer)
                scroll_y = scroll.scroll_offset.y
                # block_region.y is relative to the scroll container content
                # Subtract scroll offset, add title bar height (1)
                screen_y = block_region.y - scroll_y + 1
            except Exception:
                screen_y = 5
            block_changed = (
                self._diff_mode.get(self._current_index, False)
                and md.diff_tag_for_block(block) == "changed"
            )
            popover.show_comments(comments, block_y=screen_y, block_changed=block_changed)
        else:
            popover.hide()

    def _notify(self, message: str) -> None:
        self.notify(message, timeout=3)

    # --- Navigation ---

    def action_cursor_up(self) -> None:
        md = self.query_one(ReviewMarkdown)
        if md.cursor_index > 0:
            md.cursor_index -= 1
            if self._selecting and self._selection_start is not None:
                md.set_selection_range(self._selection_start, md.cursor_index)
            block = md.cursor_block
            if block:
                block.scroll_visible()
            self._update_popover()

    def action_cursor_down(self) -> None:
        md = self.query_one(ReviewMarkdown)
        md.cursor_index += 1
        if self._selecting and self._selection_start is not None:
            md.set_selection_range(self._selection_start, md.cursor_index)
        block = md.cursor_block
        if block:
            block.scroll_visible()

        self._update_popover()

    def action_select_up(self) -> None:
        """Shift+Up: start or extend selection upward."""
        md = self.query_one(ReviewMarkdown)
        footer = self.query_one(FooterBar)
        if not self._selecting:
            self._selecting = True
            self._selection_start = md.cursor_index
            footer.set_mode("selecting")
        if md.cursor_index > 0:
            md.cursor_index -= 1
            md.set_selection_range(self._selection_start, md.cursor_index)
            block = md.cursor_block
            if block:
                block.scroll_visible(top=True)

    def action_select_down(self) -> None:
        """Shift+Down: start or extend selection downward."""
        md = self.query_one(ReviewMarkdown)
        footer = self.query_one(FooterBar)
        if not self._selecting:
            self._selecting = True
            self._selection_start = md.cursor_index
            footer.set_mode("selecting")
        md.cursor_index += 1
        md.set_selection_range(self._selection_start, md.cursor_index)
        block = md.cursor_block
        if block:
            block.scroll_visible()

    def action_next_file(self) -> None:
        if self._selecting:
            return
        if self._current_index < len(self._files) - 1:
            self._load_file(self._current_index + 1)

    def action_prev_file(self) -> None:
        if self._selecting:
            return
        if self._current_index > 0:
            self._load_file(self._current_index - 1)

    # --- File selector ---

    def action_open_file_selector(self) -> None:
        if self._selecting:
            return
        file_info = []
        for i, path in enumerate(self._files):
            review = self._reviews[i]
            file_info.append((path, review.status, len(review.comments)))

        def on_select(index: int | None) -> None:
            if index is not None:
                self._load_file(index)

        self.push_screen(
            FileSelector(file_info, self._current_index),
            callback=on_select,
        )

    # --- Comments ---

    def action_comment(self) -> None:
        md = self.query_one(ReviewMarkdown)
        footer = self.query_one(FooterBar)

        if not self._selecting:
            # Start selection
            self._selecting = True
            self._selection_start = md.cursor_index
            md.set_selection_range(self._selection_start, self._selection_start)
            footer.set_mode("selecting")
        else:
            # Confirm selection and open input
            self._selecting = False
            footer.set_mode("normal")
            selection_end = md.cursor_index

            start_idx = min(self._selection_start or 0, selection_end)
            end_idx = max(self._selection_start or 0, selection_end)

            blocks = md.blocks
            if not blocks or start_idx >= len(blocks) or end_idx >= len(blocks):
                md.clear_selection()
                return

            start_block = blocks[start_idx]
            end_block = blocks[end_idx]

            line_start = (
                (start_block.source_range[0] + 1) if start_block.source_range else 1
            )
            line_end = (
                end_block.source_range[1] if end_block.source_range else line_start
            )

            def on_comment(text: str | None) -> None:
                md.clear_selection()
                if text:
                    self._add_comment(line_start, line_end, text)

            self.push_screen(CommentInput(line_start, line_end), callback=on_comment)

    def _add_comment(self, line_start: int, line_end: int, body: str) -> None:
        lines = self._lines[self._current_index]
        anchor = lines[line_start - 1].strip() if line_start - 1 < len(lines) else ""

        comment = Comment(
            line_start=line_start,
            line_end=line_end,
            anchor_text=anchor,
            body=body,
        )

        review = self._reviews[self._current_index]
        review.comments.append(comment)
        save_review(self._files[self._current_index], review)

        md = self.query_one(ReviewMarkdown)
        md.set_comments(review.comments)

        self._update_popover()
        self._update_title_bar()
        self._notify(f"Comment added (L{line_start}-{line_end})")

    def action_delete_comment(self) -> None:
        popover = self.query_one(CommentPopover)
        if not popover.active_comments:
            return

        # Delete the first visible comment
        comment = popover.active_comments[0]
        review = self._reviews[self._current_index]
        review.comments = [c for c in review.comments if c.id != comment.id]
        save_review(self._files[self._current_index], review)

        md = self.query_one(ReviewMarkdown)
        md.set_comments(review.comments)

        self._update_popover()
        self._update_title_bar()
        self._notify("Comment deleted")

    def action_edit_comment(self) -> None:
        popover = self.query_one(CommentPopover)
        if not popover.active_comments:
            return

        comment = popover.active_comments[0]
        range_str = (
            f"L{comment.line_start}"
            if comment.line_start == comment.line_end
            else f"L{comment.line_start}-{comment.line_end}"
        )

        def on_edit(text: str | None) -> None:
            if text and text != comment.body:
                comment.body = text
                comment.updated_at = datetime.now(timezone.utc).isoformat()
                review = self._reviews[self._current_index]
                save_review(self._files[self._current_index], review)

                md = self.query_one(ReviewMarkdown)
                md.set_comments(review.comments)
                self._update_popover()
                self._notify(f"Comment updated ({range_str})")

        self.push_screen(
            CommentInput(
                comment.line_start,
                comment.line_end,
                initial_text=comment.body,
                title=f"Edit Comment ({range_str})",
            ),
            callback=on_edit,
        )

    # --- Review actions ---

    def action_approve(self) -> None:
        if self._selecting:
            return
        review = self._reviews[self._current_index]

        if review.comments:
            # Confirm approval with existing comments
            def on_confirm(confirmed: bool) -> None:
                if confirmed:
                    self._do_approve()

            from mdreview.widgets.confirm import ConfirmDialog

            self.push_screen(
                ConfirmDialog(
                    f"Approve with {len(review.comments)} existing comment(s)?"
                ),
                callback=on_confirm,
            )
        else:
            self._do_approve()

    def _do_approve(self) -> None:
        review = self._reviews[self._current_index]
        review.status = ReviewStatus.APPROVED
        review.reviewed_at = datetime.now(timezone.utc).isoformat()
        save_review(self._files[self._current_index], review)
        self._maybe_save_snapshot()
        self._update_title_bar()
        self._notify(f"Approved: {self._files[self._current_index].name}")
        self._advance_to_next()

    def action_request_changes(self) -> None:
        if self._selecting:
            return
        review = self._reviews[self._current_index]

        if not review.comments:
            self._notify("Add at least one comment before requesting changes")
            return

        review.status = ReviewStatus.CHANGES_REQUESTED
        review.reviewed_at = datetime.now(timezone.utc).isoformat()
        save_review(self._files[self._current_index], review)
        self._maybe_save_snapshot()
        self._update_title_bar()
        self._notify(f"Changes requested: {self._files[self._current_index].name}")
        self._advance_to_next()

    def _maybe_save_snapshot(self) -> None:
        """Save a snapshot of the current file if content differs from existing snapshot."""
        idx = self._current_index
        path = self._files[idx]
        content = path.read_text()
        existing_snapshot = self._snapshots.get(idx)
        if existing_snapshot != content:
            save_snapshot(path, content)
            self._snapshots[idx] = content
            self._diff_available[idx] = False
            self._diff_mode[idx] = False

    def _advance_to_next(self) -> None:
        """Move to the next unreviewed file, or stay if all are reviewed."""
        for i in range(len(self._files)):
            idx = (self._current_index + 1 + i) % len(self._files)
            if self._reviews[idx].status == ReviewStatus.UNREVIEWED:
                self._load_file(idx)
                return

        # All reviewed - check if we should exit
        all_reviewed = all(r.status != ReviewStatus.UNREVIEWED for r in self._reviews)
        if all_reviewed:
            self._notify("All files reviewed!")

    # --- Diff ---

    def _apply_diff_if_needed(self) -> None:
        """Compute and apply diff tags if diff mode is on for the current file."""
        idx = self._current_index
        md = self.query_one(ReviewMarkdown)
        md.clear_diff()

        if not self._diff_mode.get(idx, False) or not self._diff_available.get(idx, False):
            return

        snapshot = self._snapshots.get(idx)
        if snapshot is None:
            return

        path = self._files[idx]
        current_content = path.read_text()
        snapshot_lines = snapshot.splitlines()
        current_lines = current_content.splitlines()

        from textual.widgets._markdown import MarkdownBlock

        # Only tag leaf blocks — skip parent containers (e.g. UnorderedList)
        # whose range covers child blocks and would highlight everything
        block_ranges = []
        for b in md.blocks:
            has_children = bool(b.query(MarkdownBlock))
            block_ranges.append(b.source_range if not has_children else None)

        diffs, removed = compute_block_diff(snapshot_lines, current_lines, block_ranges)
        md.apply_diff(diffs, removed)

    def action_toggle_diff(self) -> None:
        idx = self._current_index
        if not self._diff_available.get(idx, False):
            snapshot = self._snapshots.get(idx)
            if snapshot is None:
                self._notify("No changes to diff (first review)")
            else:
                self._notify("No changes since last review")
            return

        self._diff_mode[idx] = not self._diff_mode.get(idx, False)
        self._apply_diff_if_needed()
        self._update_footer()

    # --- Mermaid ---

    def action_open_mermaid(self) -> None:
        diagrams = self._mermaid_data.get(self._current_index, [])
        if not diagrams:
            self._notify("No mermaid diagrams in this document")
            return
        # Find the diagram closest to the cursor
        md = self.query_one(ReviewMarkdown)
        block = md.cursor_block
        if block and block.source_range:
            cursor_line = block.source_range[0] + 1  # 1-indexed
            diagram = min(diagrams, key=lambda d: abs(d["line_start"] - cursor_line))
        else:
            diagram = diagrams[0]
        webbrowser.open(diagram["url"])

    def action_toggle_mermaid(self) -> None:
        idx = self._current_index
        self._mermaid_ascii_on[idx] = not self._mermaid_ascii_on.get(idx, True)
        self._load_file(idx)

    # --- Help ---

    def action_show_help(self) -> None:
        self.push_screen(HelpOverlay())

    # --- Quit ---

    def action_quit_app(self) -> None:
        if self._selecting:
            # Cancel selection
            self._selecting = False
            self._selection_start = None
            self.query_one(ReviewMarkdown).clear_selection()
            self.query_one(FooterBar).set_mode("normal")
            return

        unreviewed = [
            self._files[i].name
            for i, r in enumerate(self._reviews)
            if r.status == ReviewStatus.UNREVIEWED
        ]

        if unreviewed:

            def on_confirm(confirmed: bool) -> None:
                if confirmed:
                    self._exit_with_summary()

            from mdreview.widgets.confirm import ConfirmDialog

            msg = f"{len(unreviewed)} file(s) not reviewed. Quit anyway?"
            self.push_screen(ConfirmDialog(msg), callback=on_confirm)
        else:
            self._exit_with_summary()

    def _exit_with_summary(self) -> None:
        # Compute exit code
        has_changes = any(
            r.status == ReviewStatus.CHANGES_REQUESTED for r in self._reviews
        )
        has_unreviewed = any(r.status == ReviewStatus.UNREVIEWED for r in self._reviews)

        if has_unreviewed:
            self._exit_code = 2
        elif has_changes:
            self._exit_code = 1
        else:
            self._exit_code = 0

        self.exit(self._exit_code)

    def on_unmount(self) -> None:
        self._print_summary()

    def _print_summary(self) -> None:
        """Print review summary to stdout after TUI closes."""
        print("\nReview complete:")
        for i, path in enumerate(self._files):
            review = self._reviews[i]
            parent = path.parent.name
            name = f"{parent}/{path.name}" if parent else path.name

            match review.status:
                case ReviewStatus.APPROVED:
                    icon = "\u2713"
                    label = "approved"
                case ReviewStatus.CHANGES_REQUESTED:
                    count = len(review.comments)
                    icon = "\u2717"
                    label = f"changes requested ({count} comment{'s' if count != 1 else ''})"
                case _:
                    icon = "-"
                    label = "not reviewed"

            print(f"  {icon} {name:40s} {label}")

        approved = sum(1 for r in self._reviews if r.status == ReviewStatus.APPROVED)
        changes = sum(
            1 for r in self._reviews if r.status == ReviewStatus.CHANGES_REQUESTED
        )
        unreviewed = sum(
            1 for r in self._reviews if r.status == ReviewStatus.UNREVIEWED
        )
        print()
        if approved:
            print(f"  {approved} approved")
        if changes:
            print(f"  {changes} changes requested")
        if unreviewed:
            print(f"  {unreviewed} not reviewed")
        print(f"\nExit code: {self._exit_code}")
