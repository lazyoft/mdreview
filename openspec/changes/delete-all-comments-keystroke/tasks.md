## 1. Core Implementation

- [x] 1.1 Add `action_delete_all_comments` method in `app.py` that shows a `ConfirmDialog` with "Delete all N comments on this file?" when comments exist, and does nothing when no comments exist
- [x] 1.2 On confirmation: clear `ReviewFile.comments`, set status to `UNREVIEWED`, call `save_review()`, hide popover, refresh comment highlights on all blocks, update title bar
- [x] 1.3 Add `D` (Shift+D) keybinding in `ReviewApp.BINDINGS` mapped to `action_delete_all_comments`, gated to ignore when `_selecting` is True

## 2. UI Updates

- [x] 2.1 Add `D` keybinding to `help_overlay.py` help text under the Comments section
- [x] 2.2 Add `D delete all` to the footer bar hints (shown when current file has comments)
