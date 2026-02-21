# Sample Document with Mermaid Diagrams

Some introductory text to test comment indicators against.

## Architecture Overview

Here's a flowchart showing the review process:

```mermaid
flowchart TD
    A[Open files] --> B{Has review?}
    B -->|Yes| C[Load existing comments]
    B -->|No| D[Create fresh review]
    C --> E[Display in TUI]
    D --> E
    E --> F{User action}
    F -->|Comment| G[Add comment]
    F -->|Approve| H[Mark approved]
    F -->|Request changes| I[Mark changes requested]
    G --> E
    H --> J{More files?}
    I --> J
    J -->|Yes| E
    J -->|No| K[Exit with summary]
```

## Data Model

A class diagram of the core models:

```mermaid
classDiagram
    class ReviewFile {
        +str file
        +str content_hash
        +ReviewStatus status
        +List~Comment~ comments
        +str reviewed_at
    }
    class Comment {
        +str id
        +int line_start
        +int line_end
        +str anchor_text
        +str body
        +str created_at
        +str updated_at
        +bool orphaned
    }
    class ReviewStatus {
        <<enumeration>>
        UNREVIEWED
        APPROVED
        CHANGES_REQUESTED
    }
    ReviewFile --> "0..*" Comment
    ReviewFile --> ReviewStatus
```

## User Flow

A sequence diagram of adding a comment:

```mermaid
sequenceDiagram
    participant U as User
    participant T as TUI
    participant S as Storage

    U->>T: Press 'c' (start selection)
    T->>T: Enter selecting mode
    U->>T: Navigate + press 'c' (confirm)
    T->>T: Open CommentInput modal
    U->>T: Type comment + Ctrl+Enter
    T->>S: Save to .review.json
    S-->>T: Confirm saved
    T->>T: Update gutter indicators
    T-->>U: Show popover with comment
```

## Some Regular Content

This section has no diagrams — just text to navigate through and potentially comment on.

- Item one
- Item two
- Item three

### A Subsection

More text here to give the document some depth for testing navigation and commenting.
