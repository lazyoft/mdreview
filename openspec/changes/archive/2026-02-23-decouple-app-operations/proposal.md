## Why

`app.py` (942 lines) is a god object: every user operation (commenting, approving, deleting, diffing, file watching) lives as methods on `ReviewApp`, interleaved with Textual widget queries, scroll management, and UI updates. This makes operations impossible to test without booting the full TUI and hard to reason about in isolation. Extracting pure domain logic from UI orchestration lets us test business rules directly and keeps the app as a thin event-routing layer.

## What Changes

- Extract all mutating operations (add comment, delete comment, edit comment, delete all comments, approve, request changes, handle file change, handle new file) into standalone pure functions in a new `operations.py` module
- Each function takes state in (ReviewFile, lines, etc.) and returns state out (updated ReviewFile, new Comment, etc.) with no Textual imports, no `self`, no widget queries
- `ReviewApp` action methods become thin wrappers: call the operation, then update the UI
- Extract exit code computation and review summary generation into pure functions
- Existing tests remain valid; new tests can cover operations directly without Textual

## Capabilities

### New Capabilities
- `review-operations`: Pure functions for all review operations (add/edit/delete comment, approve, request changes, file change handling) — decoupled from Textual, independently testable

### Modified Capabilities
- `inline-comments`: Comment creation, deletion, and editing now delegate to `review-operations` functions instead of inline logic in app methods. No behavioral change — same inputs produce same outputs.
- `round-diff`: Snapshot saving on review decisions now delegates to a pure function. No behavioral change.

## Impact

- **Code**: `app.py` shrinks significantly. New `src/mdreview/operations.py` contains all extracted logic. Widget code untouched.
- **Tests**: New unit tests for `operations.py` covering every operation without Textual. Existing tests unaffected.
- **API**: No change to CLI, keybindings, sidecar format, or user-facing behavior.
- **Dependencies**: No new dependencies. `operations.py` only imports from `models.py` and `storage.py`.
