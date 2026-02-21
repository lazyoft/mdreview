## 1. Model

- [x] 1.1 Add `updated_at: str | None = None` field to `Comment` dataclass in `models.py`

## 2. Comment Input Modal

- [x] 2.1 Add optional `initial_text` and `title` parameters to `CommentInput.__init__` so the modal can be reused for editing (pre-fill TextArea, override title label)

## 3. App Actions

- [x] 3.1 Add `e` keybinding mapped to `action_edit_comment` in `ReviewApp.BINDINGS`
- [x] 3.2 Implement `action_edit_comment` in `ReviewApp`: get first comment from popover, open `CommentInput` with pre-filled body, on submit update comment body and set `updated_at`, save review, refresh UI

## 4. Popover

- [x] 4.1 Update `CommentPopover` help label from `[d] delete comment` to `[d] delete  [e] edit`
