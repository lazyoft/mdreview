## Why

OpenSpec's `ff` command generates multiple markdown artifacts (proposal, design, specs, tasks) in one shot. Currently there's no structured way to review these artifacts before applying them — you either read them manually, approve blindly, or interrupt the flow. We need a TUI that enables Google Docs-style inline commenting and approval, creating a review loop where comments trigger reprocessing and approval triggers implementation.

## What Changes

- New Python TUI application for reviewing markdown documents in the terminal
- Markdown rendering with syntax highlighting and structural formatting
- Mermaid diagram support (inline ASCII rendering or external preview)
- Text selection and inline commenting system (anchor comments to specific text ranges)
- Comment persistence in sidecar files alongside the reviewed markdown
- Review workflow: approve or request-changes per document
- Designed to integrate with OpenSpec's artifact pipeline (`ff` → review → `apply`)

## Capabilities

### New Capabilities
- `markdown-rendering`: Render markdown documents in the terminal with rich formatting, syntax highlighting, and scrollable navigation
- `mermaid-preview`: Display mermaid diagrams either as inline ASCII art or via external preview (browser/image viewer)
- `inline-comments`: Select text ranges and attach comments anchored to specific positions in the document, with comment persistence in sidecar files
- `review-workflow`: Per-document approve/request-changes flow that produces a structured review result (approved vs. needs-amendment with comment list)

### Modified Capabilities
_(none — this is a new standalone tool)_

## Impact

- **New code**: Standalone Python TUI package (likely using Textual or similar)
- **Dependencies**: Python 3.10+, `rich`/`textual` for TUI, `markdown-it-py` or similar for parsing
- **File system**: Introduces `.comments.json` sidecar files next to reviewed markdown files
- **Integration point**: Will be invoked by OpenSpec tooling after `ff` and before `apply`
