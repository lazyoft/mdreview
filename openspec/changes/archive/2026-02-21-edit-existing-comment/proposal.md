## Why

Users can add and delete comments but cannot edit them. To fix a typo or refine feedback, the user must delete the comment and re-create it from scratch, losing the original timestamp and requiring re-selection of the line range. Editing in-place is a basic expectation for any comment system.

## What Changes

- Add an "edit comment" action (`e` key) accessible from the comment popover
- Reuse the existing comment input modal, pre-filled with the comment's current body
- Update the comment in-place (preserve id, line range, anchor text, created_at) and record an `updated_at` timestamp
- Persist the updated comment to the `.review.json` sidecar file

## Capabilities

### New Capabilities
- `comment-editing`: Inline editing of existing comments via the popover, including modal pre-fill, in-place update, and updated_at tracking

### Modified Capabilities
- `inline-comments`: The comment data model gains an `updated_at` field and the popover gains an edit action

## Impact

- **Models**: `Comment` dataclass gains `updated_at: str | None` field
- **Storage**: `.review.json` format includes optional `updated_at` on comment objects (backward-compatible — existing files without it default to `None`)
- **Widgets**: `CommentInput` modal supports pre-filling text for edit mode; `CommentPopover` shows `[e] edit` hint
- **App**: New `action_edit_comment` binding and handler in `ReviewApp`
