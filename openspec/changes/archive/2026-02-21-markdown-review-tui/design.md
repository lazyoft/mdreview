## Context

OpenSpec's `ff` command generates multiple markdown artifacts. There's no structured review step — you either read files manually or approve blindly. We need a terminal-native review tool that supports inline commenting and an approve/amend workflow, creating a feedback loop with OpenSpec.

Textual 8.0.0 (Python TUI framework) provides `MarkdownViewer` for rendered markdown and `TextArea` for editable text with selection. The `mermaid-ascii` library can render mermaid diagrams as Unicode art in the terminal. No existing Python TUI tool supports markdown review with annotations.

## Goals / Non-Goals

**Goals:**
- Render markdown documents with rich formatting in the terminal
- Allow users to select line ranges and attach comments (like code review tools)
- Persist comments in sidecar files alongside the markdown
- Provide per-document approve/request-changes outcome
- Output structured review results that OpenSpec can consume
- Support mermaid diagrams (inline ASCII or external preview)

**Non-Goals:**
- WYSIWYG markdown editing (this is a review tool, not an editor)
- Character-level text selection within rendered markdown (line-range selection is sufficient)
- Real-time collaboration or multi-user review
- Rendering every markdown extension (GitHub-flavored markdown is enough)
- Building the OpenSpec integration loop (that's a separate concern — this tool just produces review output)

## Decisions

### D1: Textual 8.0.0 as framework
**Choice**: Textual over curses/blessed/prompt_toolkit
**Rationale**: Textual provides `MarkdownViewer` out of the box, a mature widget system, CSS-based styling, and async-first architecture. It renders markdown natively — we don't have to build a renderer. The alternative (Rich + curses) would mean reimplementing scrolling, layout, focus management, and markdown rendering from scratch.

### D2: Line-range selection for comments (not character-level)
**Choice**: Comments anchor to source markdown line ranges (e.g., lines 15-22), not character offsets within rendered output.
**Rationale**: Textual's `MarkdownViewer` renders markdown into widget trees — there's no concept of "selecting rendered text." `TextArea` supports character selection but shows raw markdown. Line-range selection (like GitHub code review) is practical: navigate to a line, mark start, navigate to end, mark end, type comment. Comments remain stable across minor edits since they reference source lines + a content fingerprint for drift detection.
**Alternatives considered**: (a) Raw markdown in TextArea with selection — loses the rendered view benefit. (b) Custom widget that tracks character positions in rendered output — extremely complex, fragile across terminal sizes.

### D3: Sidecar `.review.json` files for comment storage
**Choice**: Store comments in `<filename>.review.json` next to each markdown file.
**Rationale**: One sidecar per document keeps things simple, portable, and version-controllable. The review file contains both comments and the review verdict (approved/changes-requested). A single global file would create merge conflicts and make per-document status tracking harder.
**Format**: JSON with document hash, line-anchored comments, and review status.

### D4: Full-width layout with comment popovers
**Choice**: Full-width markdown view with no permanent side panel. Comments are surfaced via (1) gutter markers (`●`) on commented lines, (2) subtle background highlight on commented line ranges, and (3) a floating popover that appears when the cursor enters a commented region.
**Rationale**: A permanent side panel wastes horizontal space and splits attention. The reviewer's primary task is reading — comments are secondary context that should appear on demand. Gutter markers + background highlight let you see at a glance where comments exist while skimming. The popover shows detail only when you navigate to the relevant lines.
**Alternatives considered**: (a) Permanent side panel — reduces reading width, always visible even when not needed. (b) Gutter-only markers without highlight — harder to spot commented regions at a glance when skimming fast.

### D5: Mermaid via mermaid-ascii with fallback
**Choice**: Use `mermaid-ascii` library for inline rendering. Offer `o` key to open in browser via `mermaid.live` URL.
**Rationale**: ASCII rendering keeps everything in-terminal. But complex diagrams (sequence, state) may not render well in ASCII — the browser fallback handles those cases. We detect mermaid code blocks during markdown parsing and replace them with rendered ASCII output.

### D6: Review output format
**Choice**: The `.review.json` file serves as both comment storage and review output. Structure:
```json
{
  "file": "proposal.md",
  "content_hash": "sha256:...",
  "status": "changes_requested",
  "comments": [
    {
      "id": "c1",
      "line_start": 15,
      "line_end": 22,
      "anchor_text": "first line of selected range...",
      "body": "This section needs more detail on...",
      "created_at": "2026-02-21T10:30:00Z"
    }
  ],
  "reviewed_at": "2026-02-21T10:35:00Z"
}
```
OpenSpec reads this file to decide whether to reprocess (comments exist) or proceed to apply (approved).

### D7: Standalone CLI tool
**Choice**: Ship as `mdreview` CLI command, installable via pip.
**Rationale**: Clean separation from OpenSpec. Can be used independently for any markdown review workflow. OpenSpec invokes it as a subprocess.
**Project location**: `~/dev/personal/mdreview/`
**Package structure**: `src/mdreview/` with `__main__.py` entry point, `pyproject.toml` at root.

### D8: File selector popup (not tab bar)
**Choice**: Files are selected via an overlay popup triggered by `f`, not a persistent tab bar.
**Rationale**: A tab bar consumes vertical space and doesn't scale beyond ~5 files. A popup shows all files with their review status (○ unreviewed, ● has comments, ✓ approved) and comment counts. The title bar shows the current filename and position (e.g., `[1/4]`) with dot indicators for quick status overview.

### D9: Keybinding scheme
**Choice**: Single-key bindings optimized for review flow:
- `c` — start/confirm comment selection (press once to mark start line, navigate, press again to confirm range and open input)
- `f` — open file selector popup
- `A` — approve document
- `R` — request changes
- `d` — delete comment (when popover is active)
- `o` — open mermaid diagram in browser
- `m` — toggle mermaid ASCII/raw source
- `?` — help overlay
- `q` — quit
- `Escape` — cancel current action (selection, input, popup)
- `Ctrl+Enter` — submit comment text
**Rationale**: Single letters for frequent actions, shifted letters for consequential actions (Approve, Request changes). `c` for comment is the most natural mnemonic.

## Risks / Trade-offs

- **[Line-range anchoring may drift]** → Mitigate with content fingerprinting: store the first line's text content alongside the line number. On re-review, if lines shifted, attempt fuzzy matching to re-anchor comments. Flag unresolvable anchors to the user.
- **[Mermaid ASCII rendering quality]** → `mermaid-ascii` handles flowcharts well but may struggle with complex diagrams. The browser fallback (`o` key) handles edge cases. Accept imperfect ASCII as a tradeoff for staying in-terminal.
- **[Textual version coupling]** → Pin to `textual>=0.80,<1.0` (Textual 8.x uses 0.8x PyPI versions). The `MarkdownViewer` API has been stable since v0.40+. Minimal risk.
- **[Large documents may be slow]** → Textual's markdown widget handles large docs well in practice. For pathologically large files (>5000 lines), consider lazy rendering. Not a concern for OpenSpec artifacts which are typically <200 lines.
