## ADDED Requirements

### Requirement: Inline ASCII rendering of mermaid diagrams
The system SHALL detect mermaid code blocks in the markdown and render them as Unicode/ASCII art inline within the document.

#### Scenario: Flowchart diagram
- **WHEN** the markdown contains a mermaid flowchart code block
- **THEN** the diagram is rendered as ASCII art in place of the raw mermaid syntax

#### Scenario: Unsupported diagram type
- **WHEN** the mermaid diagram type is not supported by the ASCII renderer
- **THEN** the system displays the raw mermaid source with a note indicating external preview is available via the `o` key

### Requirement: External browser preview for mermaid diagrams
The system SHALL allow opening a mermaid diagram in the user's default browser for full-fidelity rendering.

#### Scenario: Open diagram in browser
- **WHEN** user positions cursor on a mermaid diagram and presses `o`
- **THEN** the system opens the diagram in the default browser using mermaid.live or a local renderer

### Requirement: Toggle between ASCII and raw mermaid source
The system SHALL allow toggling between the ASCII-rendered view and the raw mermaid source for any diagram.

#### Scenario: Toggle view
- **WHEN** user positions cursor on a mermaid diagram and presses `m`
- **THEN** the view switches between ASCII rendering and raw mermaid syntax
