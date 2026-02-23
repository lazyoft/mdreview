## 1. Dependencies

- [x] 1.1 Add `watchfiles` to `pyproject.toml` dependencies

## 2. File Watcher

- [x] 2.1 Add `_start_file_watcher` method in `app.py` that uses `watchfiles.awatch()` in a Textual background worker to watch all reviewed file paths
- [x] 2.2 Add `_stop_file_watcher` method to cancel the watcher worker
- [x] 2.3 Call `_start_file_watcher` in `on_mount()` and `_stop_file_watcher` in `on_unmount()`

## 3. Reload Handler

- [x] 3.1 Add `_handle_file_change(changed_path)` method that re-reads file content, computes new hash, runs drift reconciliation if hash differs, re-preprocesses mermaid, and re-renders the markdown widget
- [x] 3.2 Preserve cursor position (clamp to new block count) and scroll position across reload
- [x] 3.3 Show Textual notification "File reloaded: {filename}" after successful reload

## 4. Directory Mode

- [x] 4.1 In directory mode, configure the watcher to monitor the directory for new `.md` files
- [x] 4.2 When a new `.md` file is detected, append it to the file list and show notification "New file detected: {filename}"

## 5. Edge Cases

- [x] 5.1 Handle file deletion: show notification "File removed: {filename}", keep current content visible
- [x] 5.2 Ignore changes to the currently-being-viewed file if content hash matches (no-op reload)
