## Context

mdreview is a TUI for reviewing markdown documents with inline comments. Users can add and delete comments but cannot edit them. To correct a mistake, the user must delete and re-create the comment, losing the original timestamp and requiring re-selection of the line range.

The codebase already has a `CommentInput` modal (used for new comments), a `CommentPopover` (shows comments on the current block with `[d] delete`), and a `Comment` dataclass persisted to `.review.json` sidecar files.

## Goals / Non-Goals

**Goals:**
- Allow editing the body of an existing comment in-place
- Preserve the comment's id, line range, anchor text, and created_at
- Track when a comment was last edited via an `updated_at` field
- Reuse the existing `CommentInput` modal rather than creating a new widget

**Non-Goals:**
- Editing the line range of a comment (re-anchoring is a separate concern)
- Editing multiple comments at once
- Undo/redo for edits
- Comment history or versioning

## Decisions

### D1: Reuse CommentInput modal for editing

Add optional parameters to `CommentInput` to accept initial text and a title override (e.g., "Edit Comment (L15-22)" instead of "Add Comment (L15-22)"). The modal already handles text input and Ctrl+S submission — no new widget needed.

**Alternative considered:** A separate `CommentEditor` modal. Rejected because the UI is identical; a single modal with an optional `initial_text` parameter is simpler.

### D2: Edit targets the first comment in the popover

When multiple comments overlap on the same block, pressing `e` edits the first comment shown in the popover (same pattern as `d` for delete). This is consistent with the existing UX and avoids adding a comment-selection mechanism.

**Alternative considered:** A numbered list letting the user pick which comment to edit. Rejected as over-engineering for the current use case — most blocks have a single comment.

### D3: Add `updated_at` field to Comment dataclass

Add `updated_at: str | None = None` to the `Comment` dataclass. This field is set on edit and serialized to `.review.json`. Existing review files without this field will deserialize with `None` (backward-compatible).

### D4: Keybinding `e` for edit

Bind `e` to `action_edit_comment` in `ReviewApp`. This is consistent with the existing `d` for delete and `c` for comment. The popover help text becomes `[d] delete  [e] edit`.

## Risks / Trade-offs

- [Minimal risk] Adding `updated_at` to existing `.review.json` files: no migration needed since the field defaults to `None` and is optional in serialization.
- [Low risk] `CommentInput` gains an optional parameter: this is a purely additive change with no impact on the existing "add comment" flow.
