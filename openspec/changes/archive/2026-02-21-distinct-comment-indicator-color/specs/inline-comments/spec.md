## MODIFIED Requirements

### Requirement: Write and save comments
The system SHALL provide a modal text input for writing a comment and persist it to the sidecar review file upon submission.

#### Scenario: Submit a comment
- **WHEN** user types a comment in the modal input and presses `Ctrl+Enter`
- **THEN** the comment is saved to `<filename>.review.json` with the line range, anchor text, timestamp, and a unique ID, and a left-border indicator + background highlight appear on the commented lines using the `$error` theme color (visually distinct from the `$accent` cursor indicator)

### Requirement: View existing comments via popover
The system SHALL display a floating popover with comment details when the cursor enters a commented line range.

#### Scenario: Popover appears on commented lines
- **WHEN** user navigates to a line that has a left-border gutter indicator
- **THEN** a floating popover appears anchored to that region showing the comment body, line range, and action hints `[d] delete  [e] edit`, styled with a `$error` border and background tint
