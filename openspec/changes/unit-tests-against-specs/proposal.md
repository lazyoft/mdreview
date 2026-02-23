## Why

mdreview has no test suite. The existing OpenSpec specs (`inline-comments`, `comment-editing`, `round-diff`) define clear requirements and scenarios that can be directly translated into automated tests. Adding tests now prevents regressions as new features are developed and provides confidence for contributors.

## What Changes

- Add a `tests/` directory with pytest-based unit and integration tests
- Write tests that validate each scenario defined in existing specs:
  - `inline-comments/spec.md`: Comment creation, deletion, sidecar persistence, anchor drift reconciliation, orphan marking
  - `comment-editing/spec.md`: Edit flow, field preservation, `updated_at` tracking
  - `round-diff/spec.md`: Snapshot save/load, block diff computation, diff tagging
- Add pytest and any test dependencies to `pyproject.toml`
- Add a test command to CLAUDE.md

## Capabilities

### New Capabilities

- `test-suite`: pytest infrastructure, test organization, and spec-derived test cases

### Modified Capabilities

_(none — tests validate existing behavior without changing it)_

## Impact

- New `tests/` directory with test modules
- `pyproject.toml`: Add `[project.optional-dependencies]` for test deps (pytest, pytest-asyncio for Textual)
- `CLAUDE.md`: Document test commands
