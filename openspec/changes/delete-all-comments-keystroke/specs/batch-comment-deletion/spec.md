## ADDED Requirements

### Requirement: Batch delete all comments on current file
The system SHALL allow the user to delete all comments on the currently viewed file via a single keystroke `D` (Shift+D), guarded by a confirmation dialog.

#### Scenario: Trigger batch delete with comments present
- **WHEN** the current file has one or more comments and the user presses `D`
- **THEN** a confirmation dialog appears with the message "Delete all N comments on this file?" where N is the comment count

#### Scenario: Confirm batch deletion
- **WHEN** the confirmation dialog is shown and the user selects Yes (or presses `y`)
- **THEN** all comments are removed from the current file's review, the sidecar file is saved with an empty comments array, the review status is set to UNREVIEWED, the popover is hidden, and all comment highlights are cleared

#### Scenario: Cancel batch deletion
- **WHEN** the confirmation dialog is shown and the user selects No (or presses `Escape`)
- **THEN** no comments are deleted and the view remains unchanged

#### Scenario: No comments to delete
- **WHEN** the current file has no comments and the user presses `D`
- **THEN** nothing happens (no dialog, no error)

#### Scenario: Batch delete while in selection mode
- **WHEN** the user is in selection mode (after first `c` press) and presses `D`
- **THEN** the keystroke is ignored and selection mode continues
