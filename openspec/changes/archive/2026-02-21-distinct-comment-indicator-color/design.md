## Context

Comments and the navigation cursor both use wide left borders in the gutter. Currently comments use `$warning` and the cursor uses `$accent`. In many Textual themes these resolve to visually similar (or identical) colors, making it hard to distinguish commented blocks from the currently selected block at a glance.

All styling is done via Textual `DEFAULT_CSS` blocks — no external `.tcss` files. The relevant widgets are:
- `ReviewMarkdown` in `markdown.py` — gutter border colors for `.has-comment`, `.cursor`, `.cursor.has-comment`
- `CommentPopover` and `CommentCard` in `widgets/comment_popover.py` — popover border and background

## Goals / Non-Goals

**Goals:**
- Give comments a color that is visually distinct from both `$accent` (cursor) and `$success` (selection)
- Keep the color theme-aware by using a Textual CSS variable rather than a hardcoded color

**Non-Goals:**
- Changing cursor-over-comment precedence logic
- Changing the selection (`$success`) color
- Adding user-configurable color settings

## Decisions

**Use `$secondary` for comments instead of `$warning`.**

Rationale: Textual's built-in theme variables are `$primary`, `$secondary`, `$accent`, `$warning`, `$success`, `$error`. The app already uses `$accent` (cursor), `$success` (selection), `$warning` (currently comments), and `$primary` (title/footer bars). `$secondary` is unused and resolves to a distinct color in all built-in Textual themes (typically a blue/purple tone vs the yellow/amber of `$warning` and `$accent`). This gives maximum differentiation with zero custom color definitions.

Alternative considered: Hardcoded ANSI color (e.g., `ansi_cyan`). Rejected because it bypasses theming and may clash with user terminal palettes.

## Risks / Trade-offs

- [Theme overlap] In a custom Textual theme, `$secondary` could happen to match `$accent`. → Acceptable: the built-in themes all differentiate these, and custom theme users can adjust.
