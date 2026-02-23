## Context

mdreview has zero tests. Three detailed specs exist (`inline-comments`, `comment-editing`, `round-diff`) with well-defined scenarios that map directly to test cases. The codebase has clear separation: data models, storage I/O, diff computation, and the Textual UI layer.

## Goals / Non-Goals

**Goals:**
- Establish pytest infrastructure with a clear test organization
- Write unit tests for non-UI logic: models, storage, diff computation, mermaid preprocessing
- Write integration tests for UI behavior using Textual's `pilot` testing API
- Map test cases to spec scenarios for traceability

**Non-Goals:**
- 100% code coverage — focus on spec-defined scenarios
- Snapshot/visual regression testing
- Performance benchmarks

## Decisions

### 1. Test framework: pytest + pytest-asyncio

**Choice**: Use `pytest` for all tests, `pytest-asyncio` for Textual pilot-based integration tests.

**Alternatives considered**:
- *unittest*: More verbose, less plugin ecosystem. Rejected.
- *Textual's own test runner*: Not a standalone framework. Pilot works with pytest. Rejected.

### 2. Test organization

```
tests/
  conftest.py              # Shared fixtures (tmp markdown files, review files)
  test_models.py           # Comment, ReviewFile, ReviewStatus
  test_storage.py          # load/save review, snapshots, drift reconciliation
  test_diff.py             # compute_block_diff, refinement logic
  test_mermaid.py          # Mermaid preprocessing, URL generation
  test_app.py              # Textual pilot integration tests for app behavior
```

### 3. Spec traceability

Test functions SHALL include a docstring referencing the spec and scenario they validate, e.g.:
```python
def test_submit_comment():
    """inline-comments: Submit a comment"""
```

### 4. Fixtures

- `tmp_md_file`: Creates a temporary markdown file with configurable content
- `tmp_review_file`: Creates a markdown file with an associated `.review.json` sidecar
- `tmp_snapshot_file`: Creates a markdown file with a `.snapshot` file

## Risks / Trade-offs

- **[Textual pilot flakiness]** → Keep pilot tests focused on state changes, not pixel-level rendering
- **[Test maintenance]** → Specs change infrequently; tests map 1:1 to scenarios, so updates are localized
