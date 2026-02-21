## ADDED Requirements

### Requirement: Render markdown with rich formatting
The system SHALL display markdown documents with full rich formatting including headings, bold, italic, code blocks with syntax highlighting, lists, tables, links, and blockquotes.

#### Scenario: Open a markdown file
- **WHEN** user runs `mdreview <file.md>`
- **THEN** the TUI displays the rendered markdown with proper formatting in a full-width content pane

#### Scenario: Syntax-highlighted code blocks
- **WHEN** the markdown contains fenced code blocks with a language identifier
- **THEN** the code block is rendered with syntax highlighting for that language

#### Scenario: Tables render correctly
- **WHEN** the markdown contains pipe-delimited tables
- **THEN** the tables are rendered with borders and aligned columns

### Requirement: Scrollable document navigation
The system SHALL allow navigating the rendered document via keyboard (arrow keys, page up/down, home/end) and mouse scroll.

#### Scenario: Keyboard scrolling
- **WHEN** user presses arrow down, page down, or end
- **THEN** the document scrolls accordingly, maintaining rendering quality

#### Scenario: Mouse scroll
- **WHEN** user scrolls with the mouse wheel
- **THEN** the document scrolls smoothly in the corresponding direction

### Requirement: Multi-file review session
The system SHALL accept multiple markdown files as arguments and allow switching between them via a file selector popup.

#### Scenario: Open multiple files
- **WHEN** user runs `mdreview file1.md file2.md file3.md`
- **THEN** the TUI displays the first file and shows filename + position in the title bar (e.g., `proposal.md [1/4]`)

#### Scenario: Open file selector
- **WHEN** user presses `f`
- **THEN** a popup overlay appears listing all files with their review status and comment counts

#### Scenario: File status indicators
- **WHEN** the file selector popup is displayed
- **THEN** each file shows a status icon: ○ for unreviewed, ● for has comments / changes requested, ✓ for approved

#### Scenario: Select a file
- **WHEN** user navigates to a file in the popup with arrow keys and presses `Enter`
- **THEN** the popup closes and the selected file is displayed, preserving scroll position of the previous file

#### Scenario: Dismiss file selector
- **WHEN** user presses `Escape` in the file selector popup
- **THEN** the popup closes without changing the current file

### Requirement: Full-width layout with title bar and footer
The system SHALL use the full terminal width for markdown rendering, with a title bar showing current file info and a footer showing keybindings.

#### Scenario: Title bar
- **WHEN** a file is open for review
- **THEN** the title bar displays the filename, position in file list (e.g., `[1/4]`), and dot indicators showing review status of all files

#### Scenario: Footer keybinding bar
- **WHEN** the TUI is in its default state
- **THEN** the footer displays available keybindings: `[c] comment  [f] files  [A] approve  [R] request changes  [?] help  [q] quit`

### Requirement: Comment visibility indicators
The system SHALL display gutter markers and background highlights on lines that have comments attached.

#### Scenario: Gutter markers on commented lines
- **WHEN** the document has comments anchored to specific line ranges
- **THEN** a `●` marker appears in the left gutter for each line within a commented range

#### Scenario: Background highlight on commented lines
- **WHEN** the document has comments anchored to specific line ranges
- **THEN** commented lines have a subtle background color change (dim amber/yellow) distinguishing them from uncommented lines

#### Scenario: No comments
- **WHEN** the document has no comments
- **THEN** no gutter markers or background highlights are shown
