### Requirement: Select line range for commenting
The system SHALL allow the user to select a line range using the `c` key to define the region a comment applies to.

#### Scenario: Start and confirm selection
- **WHEN** user navigates to a line and presses `c` to mark the start, then navigates to another line and presses `c` again to confirm the range
- **THEN** the selected range is highlighted and a comment input modal appears

#### Scenario: Single-line comment
- **WHEN** user presses `c` on a line and presses `c` again on the same line (or presses `Enter` immediately)
- **THEN** the comment is anchored to that single line and the comment input modal appears

#### Scenario: Cancel selection
- **WHEN** user presses `Escape` while a selection is in progress (after first `c` but before second)
- **THEN** the selection is cleared and no comment input appears

### Requirement: Write and save comments
The system SHALL provide a modal text input for writing a comment and persist it to the sidecar review file upon submission. Comment creation logic SHALL be delegated to the `add_comment` operation from `operations.py`.

#### Scenario: Submit a comment
- **WHEN** user types a comment in the modal input and presses `Ctrl+Enter`
- **THEN** the app calls `add_comment(review, lines, line_start, line_end, body)` from `operations.py`, then calls `save_review()` to persist, then updates the UI (comment highlighting, popover, title bar)

#### Scenario: Cancel comment input
- **WHEN** user presses `Escape` during comment input
- **THEN** the comment input modal is dismissed and the selection is cleared without saving

### Requirement: View existing comments via popover
The system SHALL display a floating popover with comment details when the cursor enters a commented line range. When diff mode is active and the commented block is tagged as `changed`, the popover SHALL include a hint indicating the block was modified since the last review.

#### Scenario: Popover appears on commented lines
- **WHEN** user navigates to a line that has a left-border gutter indicator
- **THEN** a floating popover appears anchored to that region showing the comment body, line range, and action hints `[d] delete  [e] edit`, styled with a blue (`#6090d0`) border and dark blue background tint

#### Scenario: Popover dismisses when leaving region
- **WHEN** user navigates away from a commented line range
- **THEN** the popover disappears

#### Scenario: Multiple comments on overlapping ranges
- **WHEN** multiple comments overlap on the same lines
- **THEN** the popover shows all comments for that region, stacked vertically

#### Scenario: Comment on changed block in diff mode
- **WHEN** the popover is shown for a block tagged `changed` while diff mode is active
- **THEN** the popover includes a hint line: "[block changed since last review]"

#### Scenario: Comment on unchanged block in diff mode
- **WHEN** the popover is shown for a block tagged `unchanged` while diff mode is active
- **THEN** the popover shows normally with no additional hint

### Requirement: Delete a comment
The system SHALL allow the user to delete an existing comment from the popover, or delete all comments on the current file via batch deletion.

#### Scenario: Delete with single comment
- **WHEN** the comment popover is active with exactly one comment and user presses `d`
- **THEN** the comment is removed from the sidecar file, the popover updates or dismisses, and the left-border indicator / background highlight are removed if no other comments remain on those lines

#### Scenario: Delete with multiple comments
- **WHEN** the comment popover is active with multiple comments and user presses `d`
- **THEN** a picker dialog lists all comments (showing line range and body preview), and the selected comment is deleted

#### Scenario: Batch delete all comments
- **WHEN** the user presses `D` (Shift+D) and the current file has comments
- **THEN** a confirmation dialog is shown; on confirmation all comments are removed, sidecar is saved, and review status is reset to UNREVIEWED

### Requirement: Comment persistence format
The system SHALL store comments in a JSON sidecar file named `<filename>.review.json` alongside the reviewed markdown file.

#### Scenario: Sidecar file structure
- **WHEN** a comment is saved
- **THEN** the sidecar file contains: file name, content hash (SHA-256 of the markdown), review status, and an array of comment objects each with id, line_start, line_end, anchor_text, body, created_at, and optional updated_at

#### Scenario: Comment anchor drift detection
- **WHEN** the markdown file has changed since comments were written (content hash mismatch)
- **THEN** the system attempts to re-anchor comments using fuzzy text matching and flags any comments that could not be re-anchored
