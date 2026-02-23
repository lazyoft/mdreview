## MODIFIED Requirements

### Requirement: Snapshot file on review decision
The system SHALL write a snapshot of the markdown file's content to `<filename>.snapshot` when the reviewer approves or requests changes, but only if the file's content hash differs from the previously stored hash. The decision of whether to save SHALL be delegated to `should_save_snapshot` from `operations.py`.

#### Scenario: First review decision creates snapshot
- **WHEN** the reviewer approves or requests changes on a file that has no existing `.snapshot` file
- **THEN** the app calls `should_save_snapshot(content, None)` which returns True, and the app writes the snapshot

#### Scenario: Subsequent decision overwrites snapshot when content changed
- **WHEN** the reviewer approves or requests changes and the current content differs from the existing snapshot
- **THEN** the app calls `should_save_snapshot(content, existing_snapshot)` which returns True, and the app overwrites the snapshot

#### Scenario: Decision on unchanged content does not overwrite snapshot
- **WHEN** the reviewer approves or requests changes but the content matches the existing snapshot
- **THEN** the app calls `should_save_snapshot(content, existing_snapshot)` which returns False, and the app does not overwrite the snapshot
