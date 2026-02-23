# mdreview

Terminal UI for reviewing markdown documents with inline comments. Built with Python/Textual.

## Commands

```bash
pip install -e .          # Install in dev mode (uses .venv)
mdreview <file.md>        # Review a single file
mdreview --dir <path>     # Review all .md files in a directory
```

## Architecture

```
src/mdreview/
  cli.py              # Click CLI entry point (mdreview command)
  app.py              # ReviewApp - main Textual app, keybindings, file navigation
  models.py           # Comment, ReviewFile, ReviewStatus dataclasses
  storage.py          # .review.json sidecar read/write + anchor drift reconciliation
  markdown.py         # ReviewMarkdown widget - cursor, selection, comment highlighting
  mermaid.py          # Mermaid diagram -> ASCII art preprocessing
  widgets/
    comment_input.py   # Modal for typing comments (Ctrl+S to submit)
    comment_popover.py # Floating overlay showing comments for current block
    file_selector.py   # Modal file picker with status indicators
    help_overlay.py    # Keybinding help screen
    confirm.py         # Yes/No confirmation dialog
```

## Key Patterns

- **Sidecar files**: Reviews stored as `<file>.md.review.json` alongside the markdown file. Gitignored via `.review.json` pattern.
- **Anchor drift**: When markdown content changes between sessions, `storage.reconcile_drift()` fuzzy-matches comment anchors to new line positions (threshold: 0.6 similarity ratio). Unmatched comments are marked `orphaned`.
- **Mermaid rendering**: Mermaid code blocks are preprocessed into ASCII art via `mermaid-ascii-diagrams`. Press `o` to open in mermaid.live, `m` to toggle ASCII/raw.
- **Exit codes**: 0 = all approved, 1 = changes requested, 2 = incomplete/unreviewed files.
- **Block-level cursor**: Navigation operates on Textual MarkdownBlock elements, not individual lines. Comments reference source line ranges.

## OpenSpec

This project uses [OpenSpec](https://github.com/anthropics/claude-code) for structured change management. Use `/openspec-new-change` to start a new change, `/openspec-continue-change` to progress through artifacts, and `/openspec-apply-change` to implement.

- **Specs** live in `openspec/specs/` — each subdirectory has a `spec.md` with requirements and scenarios.
- **Changes** go through proposal -> design -> delta specs -> tasks -> implementation -> archive.
- **Archived changes** in `openspec/changes/archive/` preserve the full artifact trail.

## Testing

```bash
pip install -e ".[test]"   # Install with test dependencies
pytest                     # Run all tests
pytest -v                  # Verbose output
pytest tests/test_storage.py  # Run a specific module
```

Tests cover models, storage (sidecar I/O, drift reconciliation), diff computation, and mermaid preprocessing. Test cases map to scenarios defined in `openspec/specs/`.
