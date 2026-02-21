## Why

Comment gutter indicators and the cursor/navigation indicator can appear identical because both rely on Textual theme variables (`$warning` and `$accent`) that may resolve to similar colors depending on the terminal theme. Comments should be immediately distinguishable from the navigation cursor at a glance.

## What Changes

- Replace the comment indicator color (`$warning`) with a distinct color that visually separates comments from the navigation cursor
- Update comment popover and comment card styling to use the new comment color for consistency
- No change to cursor-over-comment precedence logic — just the colors

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `inline-comments`: The visual indicator color for comments changes from `$warning` to a distinct color

## Impact

- `src/mdreview/markdown.py` — CSS rules for `.has-comment`, `.cursor.has-comment`
- `src/mdreview/widgets/comment_popover.py` — CSS rules for `CommentPopover` and `CommentCard` border/background colors
