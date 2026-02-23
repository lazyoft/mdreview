## Context

mdreview supports deleting individual comments via `d` when the popover is visible. When a file has many comments (e.g., after a thorough first review), clearing them all requires navigating to each commented block and pressing `d` repeatedly. This is especially tedious when starting a fresh review round.

The existing `ConfirmDialog` widget provides a reusable Yes/No prompt that can guard destructive actions.

## Goals / Non-Goals

**Goals:**
- Provide a single-keystroke action to delete all comments on the current file
- Prevent accidental mass deletion via confirmation
- Keep the UX consistent with existing keybinding patterns

**Non-Goals:**
- Deleting comments across all files at once (scope: current file only)
- Undo/redo support for deleted comments
- Selective batch deletion (e.g., only orphaned comments)

## Decisions

### 1. Keybinding: `D` (Shift+D) with ConfirmDialog

**Choice**: Use `D` (uppercase) to trigger batch deletion, guarded by the existing `ConfirmDialog`.

**Alternatives considered**:
- *Double-press `d d`*: Requires a timer/debounce mechanism, adds state complexity, and conflicts with fast repeated single deletes. Rejected.
- *`Ctrl+D`*: Already used by some terminals for EOF. Risky.
- *Menu-based*: Inconsistent with the keyboard-driven UX.

**Rationale**: `D` is mnemonic (Delete all), mirrors the vim convention of uppercase for "bigger" actions, and the confirmation dialog is already implemented and proven.

### 2. Confirmation message

The dialog SHALL show: "Delete all N comments on this file?" with Yes/No buttons.

### 3. Post-deletion state

After deletion:
- All comments removed from the `ReviewFile.comments` list
- Sidecar saved (empty comments array)
- Review status reset to `UNREVIEWED` (a file with no comments and no decision should be unreviewed)
- Popover hidden
- Comment highlights cleared from all blocks
- Title bar updated to reflect new status

## Risks / Trade-offs

- **[Accidental keystroke]** → Mitigated by ConfirmDialog requiring explicit Yes
- **[Status reset surprise]** → User may not expect status to reset; the confirm message makes clear this is a destructive action
