### Requirement: Edit an existing comment
The system SHALL allow the user to edit the body of an existing comment in-place, preserving its id, line range, anchor text, and created_at timestamp.

#### Scenario: Edit comment from popover
- **WHEN** the comment popover is active and user presses `e`
- **THEN** a modal appears pre-filled with the comment's current body text, with the title "Edit Comment (L{start}-{end})"

#### Scenario: Submit edited comment
- **WHEN** user modifies the text in the edit modal and presses `Ctrl+S`
- **THEN** the comment body is updated in-place, `updated_at` is set to the current UTC timestamp, the sidecar file is saved, and the popover refreshes with the new text

#### Scenario: Cancel editing
- **WHEN** user presses `Escape` during editing
- **THEN** the edit modal is dismissed and the comment remains unchanged

#### Scenario: No comments to edit
- **WHEN** user presses `e` but the popover has no active comments
- **THEN** nothing happens (no modal, no error)

#### Scenario: Edit with single comment
- **WHEN** exactly one comment exists on the current block and user presses `e`
- **THEN** the edit modal opens directly for that comment

#### Scenario: Edit with multiple overlapping comments
- **WHEN** multiple comments overlap on the current block and user presses `e`
- **THEN** a picker dialog lists all comments (showing line range and body preview), and the selected comment is opened for editing

#### Scenario: Cancel comment picker
- **WHEN** the comment picker is shown and user presses `Escape`
- **THEN** the picker is dismissed and no comment is edited

### Requirement: Comment updated_at tracking
The system SHALL track when a comment was last edited via an `updated_at` field on the Comment model.

#### Scenario: New comment has no updated_at
- **WHEN** a new comment is created
- **THEN** its `updated_at` field is `None`

#### Scenario: Edited comment has updated_at set
- **WHEN** a comment is edited and saved
- **THEN** its `updated_at` field is set to the current UTC ISO timestamp

#### Scenario: Backward compatibility with existing review files
- **WHEN** a `.review.json` file without `updated_at` fields is loaded
- **THEN** all comments deserialize with `updated_at` as `None` and the application functions normally
