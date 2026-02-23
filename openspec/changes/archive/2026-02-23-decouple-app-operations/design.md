## Context

`ReviewApp` in `app.py` (942 lines) owns all review state and every user operation as instance methods. Each action method (e.g., `_add_comment`, `_do_approve`, `action_delete_comment`) mixes domain logic (create a Comment, set status to APPROVED, reconcile drift) with UI updates (`query_one(ReviewMarkdown).set_comments()`, `_update_popover()`, `_notify()`). This coupling means:

- Testing any operation requires a running Textual app
- Understanding a business rule requires mentally filtering out widget code
- The file has no natural seam for a new developer to understand "what happens when you approve"

The existing modules (`storage.py`, `diff.py`, `models.py`, `mermaid.py`) are already well-decoupled. This change applies the same pattern to the operations themselves.

## Goals / Non-Goals

**Goals:**
- Every mutating review operation is a pure function: takes data in, returns data out
- Operations have zero Textual imports — testable with plain pytest
- `ReviewApp` action methods become 3-5 line wrappers: call operation, apply results to UI
- No behavioral change — identical user experience, identical sidecar output

**Non-Goals:**
- Not restructuring the Textual widget tree or CSS
- Not introducing a state management layer, event bus, or reactive framework
- Not changing the `ReviewMarkdown`, `CommentPopover`, or other widget internals
- Not extracting navigation (cursor up/down, file switching) — these are inherently UI operations
- Not adding new features or changing keybindings

## Decisions

### 1. Single `operations.py` module, not a package

Put all operations as module-level functions in `src/mdreview/operations.py`.

**Why not an `operations/` package?** There are ~8 operations. Splitting into 8 files would be over-engineering for a TUI. A single module keeps them discoverable and easy to scan. If it grows past ~300 lines, split later.

**Why not classes (UseCase pattern)?** The SBA UseCase pattern with `__init__` + `execute` makes sense when you have dependency injection and external services. These operations take dataclasses in and return dataclasses out. Functions are the right abstraction.

### 2. Operations return result objects, not mutate in place

Each operation returns either a new/updated object or a named tuple with the results. The caller (app) applies the returned state.

Example: `approve_file(review, content, snapshot) -> ApproveResult(review, new_snapshot, snapshot_changed)` rather than mutating the review and saving the snapshot inside the function.

**Why?** Keeps operations pure. The app decides when to persist (via `save_review`) and when to update the UI. Testing becomes `assert result.review.status == APPROVED` with no mocks.

**Exception:** `add_comment` creates a `Comment` and appends it to `review.comments`. This is a mutation, but it's the natural API — the caller passes the review, gets back the new comment, and the review is updated. Avoiding this would require returning a new list and re-assigning, which is ceremony for no benefit.

### 3. Operations import only from `models.py` and `storage.py`

`operations.py` can import `Comment`, `ReviewFile`, `ReviewStatus` from `models.py` and `compute_hash`, `reconcile_drift` from `storage.py`. No imports from `textual`, `markdown.py`, or any widget.

**Why allow `storage.py` imports?** `reconcile_drift` is pure domain logic that happens to live in `storage.py`. `compute_hash` is a utility. Neither touches the filesystem — that's `save_review`/`load_review` which stay in the app layer.

### 4. Don't extract navigation or UI-only actions

Cursor movement, scroll restoration, selection mode toggling, and popover positioning are inherently tied to Textual widget state. Extracting them would create a leaky abstraction where the "pure" function needs to know about block indices, scroll offsets, and widget queries.

**Extracted (domain logic):** add_comment, edit_comment, delete_comment, delete_all_comments, approve_file, request_changes, compute_exit_code, handle_file_change, handle_new_file

**Stays in app (UI logic):** cursor movement, selection mode, file loading/rendering, popover updates, mermaid toggling, file watcher async loop

### 5. `handle_file_change` returns a diff of what changed

The current `_handle_file_change` is 40 lines mixing hash checks, drift reconciliation, mermaid preprocessing, and scroll restoration. Extract the domain part: given old hash + new content + review → return updated review + whether re-render is needed + updated diff availability.

The app then handles the re-render and scroll restoration if the result says re-render is needed.

## Risks / Trade-offs

- **[Risk] Indirection overhead** — Callers must now unpack results and apply them. Each action method goes from "do everything" to "call operation, apply 3-4 state updates, update UI."
  → Mitigation: This is exactly the right trade-off. The action methods become a clear checklist of "operation result → state update → UI update." More lines, but each line is obvious.

- **[Risk] Drift between operation and app** — If an operation's return type changes, the app wrapper must change too.
  → Mitigation: Types are simple dataclasses/NamedTuples. Tests on both sides catch drift.

- **[Risk] Temptation to over-extract** — Once the pattern exists, there's a pull to extract navigation, selection mode, and other UI logic too.
  → Mitigation: The non-goal is explicit. If it needs `self.query_one()`, it stays in app.
