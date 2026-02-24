"""Main ReviewApp TUI application."""

from __future__ import annotations

import webbrowser
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Static

from mdreview.diff import compute_block_diff
from mdreview.keybindings import DEFAULT_BINDINGS, ACTION_LABELS, key_label
from mdreview.markdown import ReviewMarkdown
from mdreview.mermaid import preprocess_mermaid
from mdreview.models import Comment, ReviewFile, ReviewStatus
from mdreview.operations import (
    add_comment,
    approve_file,
    compute_exit_code,
    delete_all_comments,
    delete_comment,
    edit_comment,
    format_summary,
    handle_content_change,
    request_changes,
    should_save_snapshot,
)
from mdreview.storage import (
    compute_hash,
    load_review,
    load_snapshot,
    reconcile_drift,
    save_review,
    save_snapshot,
)
from mdreview.widgets.comment_input import CommentInput
from mdreview.widgets.comment_picker import CommentPicker
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

    def __init__(self, keybindings: dict[str, str] | None = None) -> None:
        super().__init__()
        self._mode = "normal"
        self._diff_available = False
        self._has_comments = False
        self._keys = keybindings or dict(DEFAULT_BINDINGS)

    def _hint(self, action: str, label: str) -> str:
        """Format a single keybinding hint."""
        return f"[bold ansi_bright_yellow]{key_label(self._keys[action])}[/] {label}  "

    def set_mode(self, mode: str = "normal") -> None:
        self._mode = mode
        self._refresh()

    def set_diff_available(self, available: bool) -> None:
        self._diff_available = available
        self._refresh()

    def set_has_comments(self, has_comments: bool) -> None:
        self._has_comments = has_comments
        self._refresh()

    def _refresh(self) -> None:
        if self._mode == "selecting":
            comment_key = key_label(self._keys["comment"])
            select_up = key_label(self._keys["select_up"])
            select_down = key_label(self._keys["select_down"])
            text = (
                f" [bold ansi_bright_yellow]{comment_key}[/] confirm selection  "
                f"[bold ansi_bright_yellow]{select_up}/{select_down}[/] extend  "
                "[bold ansi_bright_yellow]Esc[/] cancel"
            )
            self.update(text)
        else:
            prev_key = key_label(self._keys["prev_file"])
            next_key = key_label(self._keys["next_file"])
            text = (
                " "
                + self._hint("comment", "comment")
                + self._hint("open_file_selector", "files")
                + f"[bold ansi_bright_yellow]{prev_key}{next_key}[/] prev/next  "
                + self._hint("approve", "approve")
                + self._hint("request_changes", "request changes")
            )
            if self._has_comments:
                text += self._hint("delete_all_comments", "delete all")
            if self._diff_available:
                text += self._hint("toggle_diff", "diff")
            text += (
                self._hint("show_help", "help")
                + f"[bold ansi_bright_yellow]{key_label(self._keys['quit'])}[/] quit"
            )
            self.update(text)


class ReviewApp(App):
    """Main TUI application for reviewing markdown documents."""

    DEFAULT_CSS = """
    ReviewApp {
        layout: vertical;
    }

    #content-scroll {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding(
            DEFAULT_BINDINGS[action],
            action if action != "quit" else "quit_app",
            ACTION_LABELS.get(action, action),
            priority=True,
            id=action,
        )
        for action in DEFAULT_BINDINGS
    ] + [
        Binding("escape", "cancel_selection", "Cancel selection", show=False),
    ]

    def __init__(
        self,
        files: list[Path],
        watch_dir: Path | None = None,
        keybindings: dict[str, str] | None = None,
    ) -> None:
        self._keybindings = keybindings or dict(DEFAULT_BINDINGS)
        super().__init__()
        # Apply custom keybindings via Textual's keymap system
        keymap = {
            action: self._keybindings[action]
            for action in DEFAULT_BINDINGS
            if self._keybindings[action] != DEFAULT_BINDINGS[action]
        }
        if keymap:
            self.set_keymap(keymap)
        self._files = files
        self._watch_dir = watch_dir
        self._watcher_worker = None
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
        yield FooterBar(keybindings=self._keybindings)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Disable app-level actions when a modal screen is active."""
        from textual.screen import ModalScreen

        if isinstance(self.screen, ModalScreen):
            return False
        return True

    def on_mount(self) -> None:
        self._load_file(0)
        self.query_one(FooterBar).set_mode("normal")
        self._start_file_watcher()

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
        footer.set_has_comments(bool(self._reviews[self._current_index].comments))

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
            popover.show_comments(
                comments, block_y=screen_y, block_changed=block_changed
            )
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

    def action_cancel_selection(self) -> None:
        """Escape: cancel active selection."""
        if self._selecting:
            self._selecting = False
            self._selection_start = None
            self.query_one(ReviewMarkdown).clear_selection()
            self.query_one(FooterBar).set_mode("normal")

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
        review = self._reviews[self._current_index]
        lines = self._lines[self._current_index]
        add_comment(review, lines, line_start, line_end, body)
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

        if len(popover.active_comments) == 1:
            self._do_delete_comment(popover.active_comments[0])
        else:
            self.push_screen(
                CommentPicker(popover.active_comments, title="Delete which comment?"),
                callback=lambda c: c and self._do_delete_comment(c),
            )

    def _do_delete_comment(self, comment: Comment) -> None:
        review = self._reviews[self._current_index]
        delete_comment(review, comment.id)
        save_review(self._files[self._current_index], review)

        md = self.query_one(ReviewMarkdown)
        md.set_comments(review.comments)

        self._update_popover()
        self._update_title_bar()
        self._update_footer()
        self._notify("Comment deleted")

    def action_edit_comment(self) -> None:
        popover = self.query_one(CommentPopover)
        if not popover.active_comments:
            return

        if len(popover.active_comments) == 1:
            self._do_edit_comment(popover.active_comments[0])
        else:
            self.push_screen(
                CommentPicker(popover.active_comments, title="Edit which comment?"),
                callback=lambda c: c and self._do_edit_comment(c),
            )

    def _do_edit_comment(self, comment: Comment) -> None:
        range_str = (
            f"L{comment.line_start}"
            if comment.line_start == comment.line_end
            else f"L{comment.line_start}-{comment.line_end}"
        )

        def on_edit(text: str | None) -> None:
            if text:
                review = self._reviews[self._current_index]
                result = edit_comment(review, comment.id, text)
                if result:
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

    def action_delete_all_comments(self) -> None:
        if self._selecting:
            return
        review = self._reviews[self._current_index]
        if not review.comments:
            return

        count = len(review.comments)

        def on_confirm(confirmed: bool) -> None:
            if confirmed:
                deleted = delete_all_comments(review)
                save_review(self._files[self._current_index], review)

                md = self.query_one(ReviewMarkdown)
                md.set_comments(review.comments)
                self.query_one(CommentPopover).hide()
                self._update_title_bar()
                self._update_footer()
                self._notify(f"Deleted {deleted} comment(s)")

        from mdreview.widgets.confirm import ConfirmDialog

        self.push_screen(
            ConfirmDialog(f"Delete all {count} comments on this file?"),
            callback=on_confirm,
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
        approve_file(review)
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

        request_changes(review)
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
        if should_save_snapshot(content, existing_snapshot):
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

        if not self._diff_mode.get(idx, False) or not self._diff_available.get(
            idx, False
        ):
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

    # --- File watcher ---

    def _start_file_watcher(self) -> None:
        """Start watching reviewed files for changes."""
        self._watcher_worker = self.run_worker(
            self._watch_files(), exclusive=True, name="file-watcher"
        )

    async def _watch_files(self) -> None:
        """Background task that watches for file changes."""
        from watchfiles import awatch, Change

        # Determine watch paths
        watch_paths: set[str] = set()
        if self._watch_dir:
            watch_paths.add(str(self._watch_dir))
        else:
            # Watch parent directories of all files
            for f in self._files:
                watch_paths.add(str(f.parent))

        async for changes in awatch(*watch_paths):
            for change_type, changed_path_str in changes:
                changed_path = Path(changed_path_str).resolve()

                if change_type == Change.deleted:
                    # Check if it's a watched file
                    if changed_path in [f.resolve() for f in self._files]:
                        self.call_from_thread(
                            self._notify, f"File removed: {changed_path.name}"
                        )
                    continue

                # Only care about .md files
                if changed_path.suffix != ".md":
                    continue

                # Skip sidecar and snapshot files
                if changed_path.name.endswith(
                    ".review.json"
                ) or changed_path.name.endswith(".snapshot"):
                    continue

                # Check if it's an existing watched file
                resolved_files = [f.resolve() for f in self._files]
                if changed_path in resolved_files:
                    idx = resolved_files.index(changed_path)
                    self.call_from_thread(self._handle_file_change, idx)
                elif self._watch_dir and change_type == Change.added:
                    # New file in watched directory
                    self.call_from_thread(self._handle_new_file, changed_path)

    def _stop_file_watcher(self) -> None:
        """Stop the file watcher worker."""
        if self._watcher_worker and not self._watcher_worker.is_finished:
            self._watcher_worker.cancel()

    def _handle_file_change(self, file_index: int) -> None:
        """Re-read and re-render a file that changed on disk."""
        path = self._files[file_index]

        if not path.exists():
            return

        content = path.read_text()
        review = self._reviews[file_index]
        result = handle_content_change(review, content, review.content_hash)

        if not result.changed:
            return

        self._lines[file_index] = result.lines
        save_review(path, review)

        # Update snapshot diff availability
        snapshot = self._snapshots.get(file_index)
        self._diff_available[file_index] = snapshot is not None and snapshot != content
        self._diff_mode[file_index] = False

        # If this is the currently viewed file, reload it
        if file_index == self._current_index:
            # Save cursor and scroll position before reload
            md = self.query_one(ReviewMarkdown)
            saved_cursor = md.cursor_index
            try:
                scroll = self.query_one("#content-scroll", ScrollableContainer)
                saved_scroll = scroll.scroll_y
            except Exception:
                saved_scroll = 0

            # Re-render
            if self._mermaid_ascii_on.get(file_index, True):
                processed, diagrams = preprocess_mermaid(content, render_ascii=True)
            else:
                processed, diagrams = preprocess_mermaid(content, render_ascii=False)
            self._mermaid_data[file_index] = diagrams
            md.update(processed)

            def restore_after_reload() -> None:
                md = self.query_one(ReviewMarkdown)
                review = self._reviews[file_index]
                md.set_comments(review.comments)
                # Clamp cursor to new block count
                blocks = md.blocks
                md.cursor_index = min(saved_cursor, len(blocks) - 1) if blocks else 0
                self._apply_diff_if_needed()
                self._update_popover()
                self._update_title_bar()
                self._update_footer()
                # Restore scroll
                try:
                    scroll = self.query_one("#content-scroll", ScrollableContainer)
                    scroll.scroll_y = saved_scroll
                except Exception:
                    pass

            self.set_timer(0.1, restore_after_reload)

        self._notify(f"File reloaded: {path.name}")

    def _handle_new_file(self, new_path: Path) -> None:
        """Handle a new .md file detected in the watch directory."""
        resolved = new_path.resolve()
        if resolved in [f.resolve() for f in self._files]:
            return  # Already tracked

        content = new_path.read_text()
        idx = len(self._files)
        self._files.append(resolved)

        review = load_review(resolved)
        result = handle_content_change(review, content, review.content_hash)
        self._lines[idx] = result.lines
        self._reviews.append(review)
        self._mermaid_ascii_on[idx] = True

        snapshot = load_snapshot(resolved)
        self._snapshots[idx] = snapshot
        self._diff_available[idx] = snapshot is not None and snapshot != content
        self._diff_mode[idx] = False

        self._update_title_bar()
        self._notify(f"New file detected: {new_path.name}")

    # --- Help ---

    def action_show_help(self) -> None:
        self.push_screen(HelpOverlay(keybindings=self._keybindings))

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
        self._exit_code = compute_exit_code(self._reviews)
        self.exit(self._exit_code)

    def on_unmount(self) -> None:
        self._stop_file_watcher()
        self._print_summary()

    def _print_summary(self) -> None:
        """Print review summary to stdout after TUI closes."""
        print(format_summary(self._files, self._reviews))
