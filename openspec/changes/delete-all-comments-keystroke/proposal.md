## Why

When reviewing a file with many comments, there is no way to clear all comments at once — the reviewer must delete them one-by-one with `d`. This is tedious when re-reviewing a file from scratch or resetting a review. A batch-delete keystroke with a safety mechanism prevents accidental data loss while enabling a fast workflow.

## What Changes

- Add a new keybinding (e.g., `D` or double-press `d d`) to delete **all comments on the current file**
- Require confirmation before executing: either a double-keystroke sequence (press twice within a short window) or a `ConfirmDialog` prompt
- After deletion, clear the popover, save the sidecar, and reset review status to UNREVIEWED

## Capabilities

### New Capabilities

- `batch-comment-deletion`: Keystroke and confirmation flow for deleting all comments on the current file at once

### Modified Capabilities

- `inline-comments`: Adding a new deletion pathway (batch delete) alongside the existing single-comment `d` delete

## Impact

- `app.py`: New action method and keybinding
- `widgets/confirm.py`: Reuse existing `ConfirmDialog` (or implement double-keystroke timer)
- `storage.py`: No changes — existing `save_review()` handles empty comment lists
- `widgets/comment_popover.py`: Hide after batch deletion
- `widgets/help_overlay.py`: Add new keybinding to help text
