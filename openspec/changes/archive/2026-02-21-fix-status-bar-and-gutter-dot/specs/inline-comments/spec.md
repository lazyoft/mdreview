## MODIFIED Requirements

### Requirement: View existing comments via popover
The system SHALL display a floating popover with comment details when the cursor enters a commented line range.

#### Scenario: Popover appears on commented lines
- **WHEN** user navigates to a line that has a left-border gutter indicator (colored border on the left edge of the block)
- **THEN** a floating popover appears anchored to that region showing the comment body, line range, and action hints `[d] delete  [e] edit`

#### Scenario: Popover dismisses when leaving region
- **WHEN** user navigates away from a commented line range
- **THEN** the popover disappears

#### Scenario: Multiple comments on overlapping ranges
- **WHEN** multiple comments overlap on the same lines
- **THEN** the popover shows all comments for that region, stacked vertically

### Requirement: Delete a comment
The system SHALL allow the user to delete an existing comment from the popover.

#### Scenario: Delete comment from popover
- **WHEN** the comment popover is active and user presses `d`
- **THEN** the comment is removed from the sidecar file, the popover updates or dismisses, and the left-border indicator / background highlight are removed if no other comments remain on those lines
