## Context

The footer bar (`FooterBar` in `app.py`) renders keybinding hints as a plain text string where keys and descriptions are visually indistinct. For example, `[c] comment  [f] files  [←→] prev/next` — the keys blend into the surrounding text, making it hard to quickly scan available actions.

Separately, the `inline-comments` spec describes a `●` gutter dot on commented lines, but the implementation (per design decision D4) uses a `border-left: wide $warning` CSS rule instead. The border approach was the intended design — the spec wording needs updating.

## Goals / Non-Goals

**Goals:**
- Make key bindings visually prominent in the footer bar using color/style differentiation
- Align the inline-comments spec with the actual border-based visual indicator design

**Non-Goals:**
- Redesigning the footer bar layout or adding dynamic context-sensitive hints
- Implementing an actual `●` gutter character (the border approach is the correct design)
- Replacing Unicode arrow characters (they render fine — the issue is visual distinction)

## Decisions

### D1: Use Rich markup to style key bindings in the footer bar
**Choice**: Use Textual's Rich text support to render key portions (e.g., `[c]`, `[f]`, `[←→]`) in a distinct color, while keeping descriptions in the default muted text color.
**Rationale**: `FooterBar` extends `Static`, which supports Rich markup out of the box. We can use `[@click]` or simple color tags like `[bold $accent]c[/]` to make keys stand out. This requires no widget restructuring — just changing the string format.
**Alternative considered**: Building a custom footer with individual widgets per keybinding — overkill for a styling change.

### D2: Update spec wording rather than implement gutter dot
**Choice**: Amend the inline-comments spec to reference the left-border indicator.
**Rationale**: The border approach was an intentional design decision (D4). It provides a clear visual indicator without requiring custom gutter rendering, which Textual's Markdown widget doesn't natively support. Changing the spec to match the design is correct; adding a `●` character would mean fighting the framework for no UX benefit.

## Risks / Trade-offs

- **[Rich markup in Static widget]** → Textual's `Static.update()` supports Rich renderables. Verified by existing usage in `TitleBar`. No risk.
