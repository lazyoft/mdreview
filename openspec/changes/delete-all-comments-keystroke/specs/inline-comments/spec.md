## MODIFIED Requirements

### Requirement: Delete a comment
The system SHALL allow the user to delete an existing comment from the popover, or delete all comments on the current file via batch deletion.

#### Scenario: Delete comment from popover
- **WHEN** the comment popover is active and user presses `d`
- **THEN** the comment is removed from the sidecar file, the popover updates or dismisses, and the left-border indicator / background highlight are removed if no other comments remain on those lines

#### Scenario: Batch delete all comments
- **WHEN** the user presses `D` (Shift+D) and the current file has comments
- **THEN** a confirmation dialog is shown; on confirmation all comments are removed, sidecar is saved, and review status is reset to UNREVIEWED
