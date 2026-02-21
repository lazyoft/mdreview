## Why

mdreview is the human-in-the-loop checkpoint in an AI-driven development workflow. The human reviews AI-generated artifacts, leaves comments, the AI addresses them, and the cycle repeats. Currently, when the AI returns an updated file, the reviewer sees a fresh render with no indication of what changed. They must re-read the entire document to verify their comments were addressed. This makes multi-round reviews slow and error-prone.

## What Changes

- Store a snapshot of each file's content when the reviewer makes a decision (approve or request changes)
- On subsequent reviews, compute a block-level diff between the snapshot and the current content
- Provide a toggle to switch between clean view and diff view
- In diff view, visually distinguish changed, new, and removed blocks
- Correlate diff with existing comments to surface "addressed" vs "autonomous change" signals
- Show "no changes since last review" when content is identical to snapshot

## Capabilities

### New Capabilities
- `round-diff`: Snapshot storage, diff computation between review rounds, and diff-aware rendering in the TUI

### Modified Capabilities
- `inline-comments`: Comments gain awareness of whether their anchored block was changed since last review (addressed detection)

## Impact

- **Storage**: New `.snapshot` sidecar file per reviewed markdown file (plain text, same content as the markdown at decision time)
- **Models**: `ReviewFile` or storage layer needs snapshot read/write logic
- **App**: New keybinding to toggle diff view, new CSS classes for diff block states
- **Markdown widget**: Block-level diff annotations (changed/new/removed styling)
- **Footer/Help**: Updated to reflect new keybinding
