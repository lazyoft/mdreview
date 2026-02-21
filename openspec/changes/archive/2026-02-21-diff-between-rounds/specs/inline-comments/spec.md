## MODIFIED Requirements

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
