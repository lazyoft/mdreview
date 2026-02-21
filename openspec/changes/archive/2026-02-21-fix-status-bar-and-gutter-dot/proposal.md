## Why

The footer bar displays keybinding hints as plain text (e.g., `[c] comment  [f] files  ...`) where the key and its description blend together visually. The key bindings don't stand out, making it hard to quickly scan what keys do what. Additionally, the inline-comments spec references a `●` gutter marker on commented lines, but the implementation uses a left border instead - the spec should be updated to match the actual design.

## What Changes

- Style the footer bar so key bindings are visually distinct from their descriptions (e.g., using Rich markup or Textual CSS to highlight the key portion in a different color)
- Update the inline-comments spec to describe the left-border gutter indicator instead of the `●` dot character, aligning the spec with the intentional design decision (D4 in the original design chose border + background highlight)

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `inline-comments`: Update spec language that references `●` gutter marker to describe the left-border indicator that is actually implemented and was the intended design

## Impact

- `src/mdreview/app.py` — FooterBar rendering: use Rich markup or Textual styling to differentiate key bindings from descriptions
- `openspec/specs/inline-comments/spec.md` — Update "gutter marker" references to match actual border-based visual indicator
