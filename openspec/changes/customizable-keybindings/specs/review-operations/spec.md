## MODIFIED Requirements

### Requirement: Dynamic help overlay
The help overlay SHALL display keybinding labels derived from the active keybinding configuration rather than hardcoded key strings. The `HelpOverlay` widget SHALL accept the active keybinding dict and use `key_label()` to render each action's key.

#### Scenario: Help overlay with default bindings
- **WHEN** the help overlay is opened with default keybindings
- **THEN** the displayed keys SHALL match the current hardcoded help text (e.g., "q" for quit, "c" for comment)

#### Scenario: Help overlay with custom bindings
- **WHEN** the help overlay is opened and the user has remapped `quit` to `x` and `approve` to `a`
- **THEN** the help overlay SHALL show `x` next to "Quit" and `a` next to "Approve"

### Requirement: Dynamic footer bar
The `FooterBar` widget SHALL render keybinding hints from the active keybinding configuration rather than hardcoded key labels. It SHALL accept the active keybinding dict and use `key_label()` to render each action's key.

#### Scenario: Footer with default bindings
- **WHEN** the footer bar is displayed with default keybindings
- **THEN** the displayed hints SHALL match the current hardcoded footer (e.g., "c comment", "f files")

#### Scenario: Footer with custom bindings
- **WHEN** the footer bar is displayed and the user has remapped `comment` to `n` and `files` to `p`
- **THEN** the footer SHALL show `n` next to "comment" and `p` next to "files"
