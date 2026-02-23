## ADDED Requirements

### Requirement: Detect file changes on disk
The system SHALL watch reviewed markdown files for changes on disk and trigger a reload when modifications are detected.

#### Scenario: File modified externally
- **WHEN** a reviewed markdown file is modified on disk while mdreview is running
- **THEN** the system detects the change and reloads the file content within 1 second

#### Scenario: File not modified
- **WHEN** no changes occur to reviewed files on disk
- **THEN** no reload is triggered and no resources are consumed beyond the background watcher

#### Scenario: Watcher starts on app launch
- **WHEN** mdreview launches with one or more files
- **THEN** the file watcher begins monitoring all provided files immediately

#### Scenario: Watcher stops on app exit
- **WHEN** the user quits mdreview
- **THEN** the file watcher is cleanly stopped and all resources released

### Requirement: Reload preserves review state
The system SHALL preserve comments, review status, cursor position, and scroll position when reloading a file after an external change.

#### Scenario: Comments preserved on reload
- **WHEN** a file with existing comments is modified externally and reloaded
- **THEN** anchor drift reconciliation runs on all comments, re-matching them to new positions where possible and marking unmatched comments as orphaned

#### Scenario: Cursor position preserved on reload
- **WHEN** a file is reloaded after external modification
- **THEN** the cursor remains at the same block index (clamped to the new block count if the file shrank)

#### Scenario: Scroll position preserved on reload
- **WHEN** a file is reloaded after external modification
- **THEN** the scroll position is restored to the nearest equivalent position

#### Scenario: Review status preserved on reload
- **WHEN** a file with status APPROVED or CHANGES_REQUESTED is modified externally
- **THEN** the review status is preserved (the reviewer decides when to change it)

### Requirement: Reload notification
The system SHALL show a transient notification when a file is reloaded due to external changes.

#### Scenario: Notification on reload
- **WHEN** a file is reloaded after external modification
- **THEN** a notification is displayed: "File reloaded: {filename}"

#### Scenario: File deleted notification
- **WHEN** a reviewed file is deleted from disk while mdreview is running
- **THEN** a notification is displayed: "File removed: {filename}" and the current content remains visible

### Requirement: Detect new files in directory mode
The system SHALL detect new `.md` files added to the watched directory and append them to the file list.

#### Scenario: New file added to directory
- **WHEN** mdreview is running in directory mode and a new `.md` file is created in the watched directory
- **THEN** the file is appended to the file list and a notification is displayed: "New file detected: {filename}"

#### Scenario: Non-markdown file added
- **WHEN** a non-markdown file is created in the watched directory
- **THEN** the system ignores it and no notification is shown
