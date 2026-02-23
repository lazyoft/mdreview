## Why

When the markdown file being reviewed is edited externally (e.g., by a writer or CI), the reviewer must quit and re-launch mdreview to see updates. Live reload lets the reviewer keep their session open while the file evolves, preserving comments and review state across edits.

## What Changes

- Watch markdown files (or directory) for filesystem changes using a file watcher
- On detected change, re-read the file content, reconcile anchor drift for existing comments, and re-render the markdown view
- Preserve cursor position, scroll position, and review state across reloads
- Show a brief notification when a file reloads (e.g., "File updated" toast)
- In directory mode, detect new `.md` files added to the directory and append them to the file list

## Capabilities

### New Capabilities

- `live-reload`: File watching, content reload, and state preservation when markdown files change on disk

### Modified Capabilities

_(none — existing specs are unaffected; drift reconciliation already exists in storage.py)_

## Impact

- `app.py`: Add file watcher lifecycle (start on mount, stop on unmount), reload handler
- `cli.py`: Pass directory path through for watching
- `storage.py`: Reuse existing `reconcile_drift()` — no changes expected
- New dependency: `watchfiles` (or Textual's built-in file monitoring if available)
