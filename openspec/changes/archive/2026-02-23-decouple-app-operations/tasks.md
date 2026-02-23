## 1. Create operations module

- [x] 1.1 Create `src/mdreview/operations.py` with comment operations: `add_comment(review, lines, line_start, line_end, body) -> Comment`, `delete_comment(review, comment_id) -> bool`, `edit_comment(review, comment_id, new_body) -> Comment | None`, `delete_all_comments(review) -> int`
- [x] 1.2 Add review decision operations: `approve_file(review) -> None`, `request_changes(review) -> None`
- [x] 1.3 Add snapshot helper: `should_save_snapshot(content, existing_snapshot) -> bool`
- [x] 1.4 Add exit code computation: `compute_exit_code(reviews) -> int`
- [x] 1.5 Add file change handling: `handle_content_change(review, new_content, old_hash) -> ContentChangeResult` (returns NamedTuple with `changed: bool`, `new_hash: str`, `lines: list[str]`)
- [x] 1.6 Add summary generation: `format_summary(files, reviews) -> str`

## 2. Wire app.py to operations

- [x] 2.1 Refactor `_add_comment` to call `operations.add_comment` then persist and update UI
- [x] 2.2 Refactor `action_delete_comment` to call `operations.delete_comment` then persist and update UI
- [x] 2.3 Refactor `action_edit_comment` to call `operations.edit_comment` then persist and update UI
- [x] 2.4 Refactor `action_delete_all_comments` to call `operations.delete_all_comments` then persist and update UI
- [x] 2.5 Refactor `_do_approve` to call `operations.approve_file` and `operations.should_save_snapshot`
- [x] 2.6 Refactor `action_request_changes` to call `operations.request_changes` and `operations.should_save_snapshot`
- [x] 2.7 Refactor `_exit_with_summary` to call `operations.compute_exit_code`
- [x] 2.8 Refactor `_print_summary` to call `operations.format_summary`
- [x] 2.9 Refactor `_handle_file_change` to call `operations.handle_content_change` for the domain logic portion
- [x] 2.10 Refactor `_handle_new_file` to use `operations.handle_content_change` for initial state setup

## 3. Tests

- [x] 3.1 Add `tests/test_operations.py` with tests for all comment operations (add, delete, edit, delete_all) covering every scenario from the review-operations spec
- [x] 3.2 Add tests for review decision operations (approve, request_changes)
- [x] 3.3 Add tests for `should_save_snapshot` (content differs, matches, no existing snapshot)
- [x] 3.4 Add tests for `compute_exit_code` (all approved, changes requested, unreviewed)
- [x] 3.5 Add tests for `handle_content_change` (changed with comments, unchanged, changed without comments)
- [x] 3.6 Add tests for `format_summary`
