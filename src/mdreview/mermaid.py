"""Mermaid diagram preprocessing for markdown content."""

from __future__ import annotations

import re


MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def render_mermaid_ascii(source: str) -> str:
    """Render mermaid source as ASCII art."""
    stripped = source.strip()
    try:
        from mermaid_ascii import (
            parse_mermaid,
            render_flowchart_ascii,
            render_sequence_ascii,
        )

        parsed = parse_mermaid(stripped)

        # Dispatch based on parsed type
        type_name = type(parsed).__name__
        if type_name == "SequenceDiagram":
            return render_sequence_ascii(parsed).rstrip()
        else:
            return render_flowchart_ascii(parsed).rstrip()
    except Exception:
        pass
    return f"[mermaid diagram - press 'o' to open in browser]\n{stripped}"


def mermaid_live_url(source: str) -> str:
    """Generate a mermaid.live URL for the given diagram source."""
    import base64
    import json

    state = json.dumps(
        {
            "code": source.strip(),
            "mermaid": {"theme": "default"},
            "autoSync": True,
            "updateDiagram": True,
        }
    )
    encoded = base64.urlsafe_b64encode(state.encode()).decode()
    return f"https://mermaid.live/edit#base64:{encoded}"


def preprocess_mermaid(
    content: str, render_ascii: bool = True
) -> tuple[str, list[dict]]:
    """Replace mermaid code blocks with ASCII art or placeholder.

    Returns (processed_content, list of mermaid block info dicts).
    Each info dict has: source, line_start, line_end, ascii_art, url.
    """
    diagrams: list[dict] = []
    lines = content.split("\n")
    result_lines: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```mermaid"):
            start_line = i
            mermaid_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                mermaid_lines.append(lines[i])
                i += 1
            end_line = i
            i += 1  # skip closing ```

            source = "\n".join(mermaid_lines)
            ascii_art = render_mermaid_ascii(source) if render_ascii else source

            diagrams.append(
                {
                    "source": source,
                    "line_start": start_line + 1,  # 1-indexed
                    "line_end": end_line + 1,
                    "ascii_art": ascii_art,
                    "url": mermaid_live_url(source),
                }
            )

            # Replace with a code block containing the ASCII art
            result_lines.append("```")
            result_lines.extend(ascii_art.split("\n"))
            result_lines.append("```")
        else:
            result_lines.append(line)
            i += 1

    return "\n".join(result_lines), diagrams
