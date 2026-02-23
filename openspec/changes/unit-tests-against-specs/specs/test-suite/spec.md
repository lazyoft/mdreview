## ADDED Requirements

### Requirement: Test infrastructure
The system SHALL include a pytest-based test suite with fixtures for creating temporary markdown files, review sidecars, and snapshots.

#### Scenario: Run tests with pytest
- **WHEN** a developer runs `pytest` from the project root
- **THEN** all tests are discovered and executed, with results reported to stdout

#### Scenario: Test dependencies installable
- **WHEN** a developer runs `pip install -e ".[test]"`
- **THEN** pytest and all test dependencies are installed

### Requirement: Storage tests
The test suite SHALL validate all storage operations defined in the inline-comments and round-diff specs.

#### Scenario: Test comment persistence roundtrip
- **WHEN** a review with comments is saved and reloaded
- **THEN** all comment fields (id, line_start, line_end, anchor_text, body, created_at, updated_at) are preserved exactly

#### Scenario: Test anchor drift reconciliation
- **WHEN** a markdown file is modified (lines inserted/deleted) and comments are reconciled
- **THEN** comments with matching anchor text are re-positioned and comments without matches are marked orphaned

#### Scenario: Test snapshot save and load
- **WHEN** a snapshot is saved and loaded
- **THEN** the content matches exactly

#### Scenario: Test content hash computation
- **WHEN** the hash is computed for identical content twice
- **THEN** the results are equal

### Requirement: Diff computation tests
The test suite SHALL validate block-level diff computation defined in the round-diff spec.

#### Scenario: Test diff with changes
- **WHEN** snapshot and current content differ
- **THEN** blocks are correctly tagged as unchanged, changed, or new

#### Scenario: Test diff with identical content
- **WHEN** snapshot and current content are identical
- **THEN** all blocks are tagged as unchanged

#### Scenario: Test removed block detection
- **WHEN** blocks present in the snapshot are absent in current content
- **THEN** RemovedBlock entries are generated with correct position and content

### Requirement: Model tests
The test suite SHALL validate data model construction and serialization.

#### Scenario: Test Comment creation
- **WHEN** a Comment is created with all required fields
- **THEN** all fields are set correctly and id is an 8-character hex string

#### Scenario: Test ReviewFile defaults
- **WHEN** a ReviewFile is created with minimal fields
- **THEN** status defaults to UNREVIEWED and comments defaults to an empty list

### Requirement: Mermaid tests
The test suite SHALL validate mermaid preprocessing.

#### Scenario: Test mermaid block detection
- **WHEN** markdown content contains a mermaid code block
- **THEN** preprocess_mermaid extracts the diagram source and line range

#### Scenario: Test mermaid live URL generation
- **WHEN** a mermaid source string is provided
- **THEN** mermaid_live_url returns a valid mermaid.live URL
