## Context

mdreview stores review state in `.review.json` sidecar files containing comments, status, and a content hash. The content hash detects drift for comment re-anchoring but the original content is not preserved. There is no mechanism to compare what the reviewer last saw against the current version of the file.

The review loop works like this: human reviews in mdreview, leaves comments, AI addresses them, human re-opens mdreview. Currently round 2+ looks identical to round 1 — a fresh render with no change context.

## Goals / Non-Goals

**Goals:**
- Let the reviewer see what changed between the current file and the version they last rendered judgment on
- Keep the snapshot mechanism simple: one previous version, overwritten on each decision
- Separate snapshot storage from review data so the AI assistant never reads snapshot content
- Surface which blocks were changed, added, or removed with visual indicators
- Correlate changes with existing comments to distinguish "addressed" from "autonomous" changes

**Non-Goals:**
- Full version history (only current vs. previous snapshot)
- Character-level or word-level diff (block-level is sufficient)
- Side-by-side view (inline annotation only — terminal width is precious)
- Diff of the raw markdown source (diff operates on rendered blocks)

## Decisions

### Snapshot storage: separate `.snapshot` file

Store the snapshot as `<filename>.snapshot` (plain text, full file content). Alternatives considered:
- Embed in `.review.json` — rejected because the AI assistant reads that file to get comments, and the snapshot would bloat its context with redundant content
- Separate `.snapshot.json` with metadata — rejected as over-engineering; plain text is sufficient since we only need content for diffing

The `.snapshot` file is a peer to `.review.json`, managed entirely by mdreview, invisible to the assistant.

### Snapshot timing: on approve/reject, only if content changed

Write the snapshot when the user presses `A` (approve) or `R` (request changes), but only if the current content hash differs from the hash stored in `.review.json`. This means:
- First review: no snapshot exists, no diff available
- After first decision: snapshot written
- Subsequent reviews: diff available if file changed
- Re-reviewing unchanged file: snapshot not overwritten, "no changes" indicated

### Diff granularity: block-level

Compare rendered markdown blocks (paragraphs, headings, list items, code blocks) rather than raw source lines. The reviewer interacts with blocks (cursor moves between blocks), so block-level diff matches the mental model.

The diff algorithm:
1. Split both snapshot and current content into lines
2. Use `difflib.SequenceMatcher` to produce opcodes (equal, replace, insert, delete)
3. Map line ranges from opcodes back to markdown blocks via `source_range`
4. Tag each block as: `unchanged`, `changed`, `new`, or `removed`

For removed blocks (present in snapshot, absent in current), insert a synthetic placeholder block showing what was removed.

### Diff view: toggled with `v` keybinding

- Default view on open: **diff mode OFF** (opt-in); the reviewer toggles it on with `v` when a diff is available
- `v` toggles between diff and clean view
- Footer bar updates to show `v` keybinding when diff is available

### Block visual treatment in diff mode

| Block state | CSS treatment |
|------------|---------------|
| `unchanged` | Normal rendering (no extra styling) |
| `changed` | Green left border + dark green background (`#50b050` / `#153d15`). A red placeholder (`#e05050` border, `#3d1515` bg) showing the old content is injected above the block |
| `new` | Green left border + dark green background (`#50b050` / `#153d15`) |
| `removed` | Red placeholder (`#e05050` border, `#3d1515` bg) with dimmed text showing removed content |
| `changed + had comment` | Same as `changed` but popover shows "[block changed since last review]" hint |

### Comment correlation

When diff mode is active and a block is tagged `changed`, check if any existing comments are anchored to lines within that block. If so, the comment popover appends a subtle hint: `[block changed since last review]`. This is informational only — the reviewer decides whether to resolve/delete the comment.

## Risks / Trade-offs

- **Block mapping imprecision**: `difflib` works on lines, but blocks can span multiple lines. A single-line change in a multi-line paragraph marks the whole block as changed. This is acceptable — it tells the reviewer "look at this block again." → Mitigation: none needed, block-level is intentionally coarse.

- **Large files**: Storing full file content in `.snapshot` doubles disk usage per file. → Mitigation: markdown specs are small (typically <100KB). Not a practical concern.

- **Removed block placeholders**: Inserting synthetic blocks into the rendered markdown is non-trivial with Textual's Markdown widget. → Mitigation: Start with a simple approach — show removed blocks as a Static widget injected between markdown blocks, styled distinctly. If too complex, degrade to a summary count ("3 blocks removed") in the title bar.
