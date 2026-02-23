## ADDED Requirements

### Requirement: Pure comment operations
The system SHALL provide pure functions for adding, editing, deleting, and bulk-deleting comments that operate on ReviewFile and return results without any UI framework dependencies.

#### Scenario: Add comment to review
- **WHEN** `add_comment(review, lines, line_start, line_end, body)` is called with valid parameters
- **THEN** a new Comment is created with an 8-char hex id, the anchor_text set to the stripped content of `lines[line_start - 1]`, timestamps set, and the comment is appended to `review.comments`

#### Scenario: Add comment with out-of-range anchor
- **WHEN** `add_comment` is called with `line_start` beyond the length of `lines`
- **THEN** the comment is created with an empty string as `anchor_text`

#### Scenario: Delete comment from review
- **WHEN** `delete_comment(review, comment_id)` is called with an existing comment id
- **THEN** the comment with that id is removed from `review.comments` and the function returns True

#### Scenario: Delete non-existent comment
- **WHEN** `delete_comment(review, comment_id)` is called with an id not in the review
- **THEN** `review.comments` is unchanged and the function returns False

#### Scenario: Edit comment body
- **WHEN** `edit_comment(review, comment_id, new_body)` is called with an existing comment id and different body text
- **THEN** the comment's `body` is updated, `updated_at` is set to the current UTC ISO timestamp, and the function returns the updated Comment

#### Scenario: Edit comment with unchanged body
- **WHEN** `edit_comment(review, comment_id, new_body)` is called with body text identical to the current body
- **THEN** the comment is unchanged and the function returns None

#### Scenario: Delete all comments
- **WHEN** `delete_all_comments(review)` is called on a review with comments
- **THEN** all comments are removed, status is set to UNREVIEWED, reviewed_at is set to None, and the function returns the count of deleted comments

#### Scenario: Delete all comments on empty review
- **WHEN** `delete_all_comments(review)` is called on a review with no comments
- **THEN** the review is unchanged and the function returns 0

### Requirement: Pure review decision operations
The system SHALL provide pure functions for approve and request-changes decisions that update ReviewFile state without any UI framework dependencies.

#### Scenario: Approve file
- **WHEN** `approve_file(review)` is called
- **THEN** `review.status` is set to APPROVED, `review.reviewed_at` is set to the current UTC ISO timestamp

#### Scenario: Request changes on file
- **WHEN** `request_changes(review)` is called
- **THEN** `review.status` is set to CHANGES_REQUESTED, `review.reviewed_at` is set to the current UTC ISO timestamp

### Requirement: Pure snapshot decision
The system SHALL provide a pure function to determine whether a snapshot should be saved after a review decision.

#### Scenario: Snapshot needed when content differs
- **WHEN** `should_save_snapshot(content, existing_snapshot)` is called and content differs from existing_snapshot
- **THEN** the function returns True

#### Scenario: Snapshot not needed when content matches
- **WHEN** `should_save_snapshot(content, existing_snapshot)` is called and content equals existing_snapshot
- **THEN** the function returns False

#### Scenario: Snapshot needed when no existing snapshot
- **WHEN** `should_save_snapshot(content, None)` is called
- **THEN** the function returns True

### Requirement: Pure exit code computation
The system SHALL provide a pure function that computes the exit code from a list of reviews.

#### Scenario: All files approved
- **WHEN** `compute_exit_code(reviews)` is called and every review has status APPROVED
- **THEN** the function returns 0

#### Scenario: Any file has changes requested
- **WHEN** `compute_exit_code(reviews)` is called and at least one review has status CHANGES_REQUESTED (and none are UNREVIEWED)
- **THEN** the function returns 1

#### Scenario: Any file unreviewed
- **WHEN** `compute_exit_code(reviews)` is called and at least one review has status UNREVIEWED
- **THEN** the function returns 2

### Requirement: Pure file change handling
The system SHALL provide a pure function that processes a file content change and returns the updated state.

#### Scenario: File content changed with comments
- **WHEN** `handle_content_change(review, new_content, old_hash)` is called and the content hash differs from old_hash and the review has comments
- **THEN** the function reconciles comment drift against the new content lines, updates `review.content_hash`, and returns a result indicating the review was modified

#### Scenario: File content unchanged
- **WHEN** `handle_content_change(review, new_content, old_hash)` is called and the content hash matches old_hash
- **THEN** the function returns a result indicating no change occurred

#### Scenario: File content changed without comments
- **WHEN** `handle_content_change(review, new_content, old_hash)` is called and the content hash differs but the review has no comments
- **THEN** the function updates `review.content_hash` and returns a result indicating the review was modified (no drift reconciliation needed)

### Requirement: Pure review summary generation
The system SHALL provide a pure function that generates the review summary text from a list of files and reviews.

#### Scenario: Generate summary with mixed statuses
- **WHEN** `format_summary(files, reviews)` is called with files having different statuses
- **THEN** the function returns a formatted string with a line per file showing status icon and label, plus totals for each status category
