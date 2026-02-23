## MODIFIED Requirements

### Requirement: Write and save comments
The system SHALL provide a modal text input for writing a comment and persist it to the sidecar review file upon submission. Comment creation logic SHALL be delegated to the `add_comment` operation from `operations.py`.

#### Scenario: Submit a comment
- **WHEN** user types a comment in the modal input and presses `Ctrl+Enter`
- **THEN** the app calls `add_comment(review, lines, line_start, line_end, body)` from `operations.py`, then calls `save_review()` to persist, then updates the UI (comment highlighting, popover, title bar)

#### Scenario: Cancel comment input
- **WHEN** user presses `Escape` during comment input
- **THEN** the comment input modal is dismissed and the selection is cleared without saving

### Requirement: Delete a comment
The system SHALL allow the user to delete an existing comment from the popover. Deletion logic SHALL be delegated to the `delete_comment` operation from `operations.py`.

#### Scenario: Delete comment from popover
- **WHEN** the comment popover is active and user presses `d`
- **THEN** the app calls `delete_comment(review, comment_id)` from `operations.py`, then calls `save_review()` to persist, then updates the UI (comment highlighting, popover, title bar)
