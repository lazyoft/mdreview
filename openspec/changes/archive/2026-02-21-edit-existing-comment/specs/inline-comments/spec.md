## MODIFIED Requirements

### Requirement: View existing comments via popover
The system SHALL display a floating popover with comment details when the cursor enters a commented line range.

#### Scenario: Popover appears on commented lines
- **WHEN** user navigates to a line that has a `●` gutter marker
- **THEN** a floating popover appears anchored to that region showing the comment body, line range, and action hints `[d] delete  [e] edit`

#### Scenario: Popover dismisses when leaving region
- **WHEN** user navigates away from a commented line range
- **THEN** the popover disappears

#### Scenario: Multiple comments on overlapping ranges
- **WHEN** multiple comments overlap on the same lines
- **THEN** the popover shows all comments for that region, stacked vertically

### Requirement: Comment persistence format
The system SHALL store comments in a JSON sidecar file named `<filename>.review.json` alongside the reviewed markdown file.

#### Scenario: Sidecar file structure
- **WHEN** a comment is saved
- **THEN** the sidecar file contains: file name, content hash (SHA-256 of the markdown), review status, and an array of comment objects each with id, line_start, line_end, anchor_text, body, created_at, and optional updated_at

#### Scenario: Comment anchor drift detection
- **WHEN** the markdown file has changed since comments were written (content hash mismatch)
- **THEN** the system attempts to re-anchor comments using fuzzy text matching and flags any comments that could not be re-anchored
