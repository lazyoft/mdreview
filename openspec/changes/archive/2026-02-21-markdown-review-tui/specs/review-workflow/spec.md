## ADDED Requirements

### Requirement: Approve a document
The system SHALL allow the user to approve a document, recording the approval in the sidecar review file.

#### Scenario: Approve document
- **WHEN** user presses `A`
- **THEN** the sidecar file status is set to `"approved"`, the `reviewed_at` timestamp is recorded, and the TUI moves to the next unreviewed file (or exits if all files are reviewed)

#### Scenario: Approve with existing comments
- **WHEN** user presses `A` on a document that has comments
- **THEN** the system prompts for confirmation ("Approve with N existing comments?") before setting status to `"approved"`

### Requirement: Request changes on a document
The system SHALL allow the user to mark a document as needing changes, requiring at least one comment to exist.

#### Scenario: Request changes
- **WHEN** user presses `R` and comments exist on the document
- **THEN** the sidecar file status is set to `"changes_requested"` and the `reviewed_at` timestamp is recorded

#### Scenario: Request changes without comments
- **WHEN** user presses `R` and no comments exist
- **THEN** the system shows a message: "Add at least one comment before requesting changes"

### Requirement: Review status display
The system SHALL display the current review status of each file in the title bar and file selector popup.

#### Scenario: Title bar dot indicators
- **WHEN** reviewing files
- **THEN** the title bar shows dot indicators for all files: ○ unreviewed, ● has comments / changes requested, ✓ approved

#### Scenario: Status in file selector popup
- **WHEN** the file selector popup is open
- **THEN** each file shows its status icon and comment count (if any)

### Requirement: Exit with summary
The system SHALL display a review summary upon exit showing the status of all reviewed files.

#### Scenario: Exit after reviewing all files
- **WHEN** user has reviewed all files and exits (or the last file is reviewed)
- **THEN** the TUI prints a summary to stdout: number approved, number with changes requested, and the paths to all sidecar review files

#### Scenario: Exit with unreviewed files
- **WHEN** user presses `q` to quit with unreviewed files remaining
- **THEN** the system prompts for confirmation before exiting and notes which files were not reviewed

### Requirement: CLI interface
The system SHALL be invokable as `mdreview` with positional arguments for file paths and optional flags.

#### Scenario: Basic invocation
- **WHEN** user runs `mdreview proposal.md design.md specs/*/spec.md`
- **THEN** the TUI launches with all matching files loaded for review

#### Scenario: Directory mode
- **WHEN** user runs `mdreview --dir openspec/changes/my-change/`
- **THEN** the TUI loads all `.md` files found recursively in that directory

#### Scenario: Exit code
- **WHEN** the review session completes
- **THEN** exit code 0 means all files approved, exit code 1 means at least one file has changes requested, exit code 2 means review was incomplete (user quit early)
