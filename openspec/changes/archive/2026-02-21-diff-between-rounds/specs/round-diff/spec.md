## ADDED Requirements

### Requirement: Snapshot file on review decision
The system SHALL write a snapshot of the markdown file's content to `<filename>.snapshot` when the reviewer approves or requests changes, but only if the file's content hash differs from the previously stored hash.

#### Scenario: First review decision creates snapshot
- **WHEN** the reviewer approves or requests changes on a file that has no existing `.snapshot` file
- **THEN** the system writes the current markdown content to `<filename>.snapshot`

#### Scenario: Subsequent decision overwrites snapshot when content changed
- **WHEN** the reviewer approves or requests changes and the current content hash differs from the hash at the time of the last snapshot
- **THEN** the system overwrites `<filename>.snapshot` with the current markdown content

#### Scenario: Decision on unchanged content does not overwrite snapshot
- **WHEN** the reviewer approves or requests changes but the content hash matches the hash stored from the previous decision
- **THEN** the system does not overwrite the existing `.snapshot` file

### Requirement: Block-level diff computation
The system SHALL compute a block-level diff between the snapshot content and the current file content, tagging each rendered markdown block with a diff state.

#### Scenario: Diff with changes
- **WHEN** a snapshot exists and the current content differs from the snapshot
- **THEN** the system computes line-level opcodes using `difflib.SequenceMatcher`, maps them to markdown blocks via `source_range`, and tags each block as `unchanged`, `changed`, `new`, or `removed`

#### Scenario: No snapshot exists
- **WHEN** no `.snapshot` file exists for the current file (first review)
- **THEN** no diff is computed and all blocks are treated as `unchanged`

#### Scenario: Content identical to snapshot
- **WHEN** a snapshot exists but the current content is identical to the snapshot
- **THEN** no diff is computed and the system indicates "no changes since last review"

### Requirement: Diff view toggle
The system SHALL provide a keybinding `v` to toggle between diff view and clean view.

#### Scenario: Toggle diff on
- **WHEN** the reviewer presses `v` and a diff is available (snapshot exists, content differs)
- **THEN** the view switches to diff mode with block-level change annotations

#### Scenario: Toggle diff off
- **WHEN** the reviewer presses `v` while in diff mode
- **THEN** the view switches to clean mode with no diff annotations

#### Scenario: Toggle when no diff available
- **WHEN** the reviewer presses `v` but no snapshot exists or content is unchanged
- **THEN** a notification is shown: "No changes to diff" (first review) or "No changes since last review"

#### Scenario: Default view on open
- **WHEN** mdreview opens a file that has a snapshot and the content differs
- **THEN** diff mode is OFF by default; the reviewer toggles it on with `v`

### Requirement: Diff block styling
The system SHALL apply distinct visual styles to blocks based on their diff state when diff mode is active.

#### Scenario: Changed block styling
- **WHEN** a block is tagged `changed` and diff mode is active
- **THEN** the block is rendered with a green left border and dark green background tint, and a red-styled placeholder showing the previous version of the block is injected above it

#### Scenario: New block styling
- **WHEN** a block is tagged `new` and diff mode is active
- **THEN** the block is rendered with a left border and background tint using the success/green palette

#### Scenario: Removed block placeholder
- **WHEN** a block was present in the snapshot but absent in the current content and diff mode is active
- **THEN** a placeholder element is shown at the position where the block was removed, styled with the error/red palette and dimmed text showing the removed content

#### Scenario: Unchanged block styling
- **WHEN** a block is tagged `unchanged` and diff mode is active
- **THEN** the block is rendered normally with no additional styling

#### Scenario: Clean mode hides diff styling
- **WHEN** diff mode is toggled off
- **THEN** all diff-related styling and removed-block placeholders are hidden

### Requirement: Footer and help updates
The system SHALL display the `v` keybinding in the footer bar when a diff is available, and include it in the help overlay.

#### Scenario: Footer shows diff toggle
- **WHEN** a diff is available for the current file
- **THEN** the footer bar includes `v diff` among the keybinding hints

#### Scenario: Footer hides diff toggle when unavailable
- **WHEN** no diff is available (no snapshot or no changes)
- **THEN** the footer bar does not show the `v` keybinding

#### Scenario: Help overlay includes diff toggle
- **WHEN** the help overlay is displayed
- **THEN** it includes the `v` keybinding with description "Toggle diff view (changes since last review)"

### Requirement: No-changes indicator
The system SHALL inform the reviewer when a file has not changed since the last review decision.

#### Scenario: Notification on open
- **WHEN** mdreview opens a file that has a snapshot and the content is identical
- **THEN** a transient notification is shown: "No changes since last review"
