## 1. Snapshot Storage

- [x] 1.1 Add `snapshot_path(md_path)` function to `storage.py` that returns `<filename>.snapshot`
- [x] 1.2 Add `save_snapshot(md_path, content)` function that writes raw content to the snapshot file
- [x] 1.3 Add `load_snapshot(md_path)` function that reads the snapshot file content (returns `None` if not found)
- [x] 1.4 Integrate snapshot saving into `_do_approve()` and `action_request_changes()` in `app.py` — write snapshot only if content hash differs from stored hash

## 2. Diff Computation

- [x] 2.1 Create `diff.py` module with a `compute_block_diff(snapshot_lines, current_lines, blocks)` function that returns a list of diff tags (`unchanged`, `changed`, `new`, `removed`) per block, using `difflib.SequenceMatcher` opcodes mapped to block `source_range`
- [x] 2.2 Handle removed blocks — return metadata (line content, position) for blocks present in snapshot but absent in current, for placeholder rendering

## 3. Diff-Aware Rendering

- [x] 3.1 Add `diff_tags` property to `ReviewMarkdown` that stores per-block diff state and applies CSS classes (`diff-changed`, `diff-new`, `diff-removed`)
- [x] 3.2 Add CSS rules in `ReviewMarkdown` for diff block states: green for `changed` and `new`, red for old-content placeholders and `removed`
- [x] 3.3 Handle removed-block placeholders — inject `Static` widgets styled with error/red palette showing removed content at the correct position

## 4. Diff Toggle and State

- [x] 4.1 Add `_diff_mode` flag and `_diff_available` per-file flag to `ReviewApp`
- [x] 4.2 Add `v` keybinding bound to `action_toggle_diff` that toggles `_diff_mode` and re-renders the current file with or without diff annotations
- [x] 4.3 On file load: check if snapshot exists and content differs; if so, set `_diff_available = True` (diff mode defaults to OFF, opt-in via `v`); otherwise set `_diff_available = False`
- [x] 4.4 Show notification "No changes since last review" when snapshot exists but content is identical

## 5. Comment Correlation

- [x] 5.1 In `CommentPopover`, when diff mode is active and the current block has tag `changed`, append a hint line `[block changed since last review]` to the popover display

## 6. Footer and Help

- [x] 6.1 Add `v diff` to `FooterBar.NORMAL` string, conditionally shown when diff is available
- [x] 6.2 Add diff toggle entry (`v`) to `HelpOverlay` keybindings reference
