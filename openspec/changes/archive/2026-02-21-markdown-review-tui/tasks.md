## 1. Project Setup

- [x] 1.1 Create `mdreview` Python package structure at `~/dev/personal/mdreview/` (`src/mdreview/`, `pyproject.toml`, `__main__.py`)
- [x] 1.2 Add dependencies: `textual>=0.80`, `mermaid-ascii`, `click` (CLI)
- [x] 1.3 Set up CLI entry point with `click`: accept file paths, `--dir` flag, parse arguments

## 2. Review Data Model

- [x] 2.1 Create `models.py` with dataclasses: `Comment` (id, line_start, line_end, anchor_text, body, created_at), `ReviewFile` (file, content_hash, status, comments, reviewed_at)
- [x] 2.2 Create `storage.py` for reading/writing `.review.json` sidecar files (load, save, compute content hash)
- [x] 2.3 Implement comment anchor drift detection: compare content hash, fuzzy re-anchor by matching anchor_text against current file lines

## 3. Markdown Rendering & Layout

- [x] 3.1 Create main `ReviewApp(App)` class with full-width layout: `MarkdownViewer` (main content), title bar, footer keybinding bar
- [x] 3.2 Implement title bar: filename, position in file list (`[1/4]`), dot indicators (○ unreviewed, ● comments, ✓ approved)
- [x] 3.3 Implement footer keybinding bar: `[c] comment  [f] files  [A] approve  [R] request changes  [?] help  [q] quit`
- [x] 3.4 Wire keyboard navigation: arrow keys, page up/down, home/end for document scrolling

## 4. Comment Visibility

- [x] 4.1 Implement gutter markers: render `●` in left gutter for lines within commented ranges
- [x] 4.2 Implement background highlight: apply subtle amber/yellow background to commented line ranges
- [x] 4.3 Update gutter markers and highlights dynamically when comments are added or deleted

## 5. File Selector Popup

- [x] 5.1 Create file selector popup widget (overlay modal triggered by `f` key)
- [x] 5.2 Display file list with status icons (○ / ● / ✓) and comment counts
- [x] 5.3 Wire arrow key navigation, `Enter` to select, `Escape` to dismiss
- [x] 5.4 Preserve scroll position per file when switching

## 6. Inline Comments

- [x] 6.1 Implement line-range selection: first `c` marks start line (highlight start), navigate, second `c` confirms range and opens comment input modal
- [x] 6.2 Create comment input modal: text area for typing comment, `Ctrl+Enter` to submit, `Escape` to cancel
- [x] 6.3 Wire comment submission to storage: generate unique ID, capture anchor_text, save to `.review.json`
- [x] 6.4 Implement comment popover: floating tooltip appears when cursor enters a commented line range, shows comment body and actions
- [x] 6.5 Handle multiple comments on overlapping ranges: stack comments in popover
- [x] 6.6 Implement comment deletion: `d` key when popover is active

## 7. Mermaid Diagram Support

- [x] 7.1 Create markdown preprocessor that detects mermaid code blocks and replaces them with ASCII-rendered output via `mermaid-ascii`
- [x] 7.2 Implement `o` key binding to open mermaid diagram in browser (mermaid.live URL)
- [x] 7.3 Implement `m` key binding to toggle between ASCII rendering and raw mermaid source

## 8. Review Workflow

- [x] 8.1 Implement approve action (`A` key): set status to `"approved"`, prompt if comments exist, advance to next file
- [x] 8.2 Implement request-changes action (`R` key): set status to `"changes_requested"`, require at least one comment
- [x] 8.3 Update title bar dot indicators when review status changes
- [x] 8.4 Implement exit flow: confirmation prompt if unreviewed files remain, print summary to stdout
- [x] 8.5 Set exit codes: 0 = all approved, 1 = changes requested, 2 = incomplete review

## 9. Polish & Edge Cases

- [x] 9.1 Handle single-file invocation (skip file selector, full-width markdown view)
- [x] 9.2 Handle missing/unreadable files gracefully with error messages
- [x] 9.3 Add help overlay (`?` key) showing all keybindings
- [x] 9.4 Add `--dir` flag support: recursively find `.md` files in directory
