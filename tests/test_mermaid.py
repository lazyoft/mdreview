"""Tests for mdreview.mermaid — preprocessing and URL generation."""

from __future__ import annotations

import base64
import json

from mdreview.mermaid import mermaid_live_url, preprocess_mermaid


class TestPreprocessMermaid:
    """Mermaid block detection and line range extraction."""

    def test_detects_mermaid_block(self):
        content = "# Title\n\n```mermaid\ngraph TD\n  A --> B\n```\n\nMore text.\n"
        processed, diagrams = preprocess_mermaid(content, render_ascii=False)
        assert len(diagrams) == 1
        assert diagrams[0]["source"] == "graph TD\n  A --> B"

    def test_line_range_1_indexed(self):
        content = "Line 1\nLine 2\n```mermaid\ngraph TD\n  A --> B\n```\nLine 7\n"
        _, diagrams = preprocess_mermaid(content, render_ascii=False)
        assert diagrams[0]["line_start"] == 3  # 1-indexed
        assert diagrams[0]["line_end"] == 6  # closing ```

    def test_multiple_diagrams(self):
        content = (
            "```mermaid\ngraph TD\n  A-->B\n```\n"
            "text\n"
            "```mermaid\nsequenceDiagram\n  A->>B: Hi\n```\n"
        )
        _, diagrams = preprocess_mermaid(content, render_ascii=False)
        assert len(diagrams) == 2

    def test_no_mermaid_blocks(self):
        content = "# Just markdown\n\nNo diagrams here.\n"
        processed, diagrams = preprocess_mermaid(content, render_ascii=False)
        assert diagrams == []
        assert processed == content

    def test_url_generated_for_each_diagram(self):
        content = "```mermaid\ngraph TD\n  A-->B\n```\n"
        _, diagrams = preprocess_mermaid(content, render_ascii=False)
        assert diagrams[0]["url"].startswith("https://mermaid.live/edit#base64:")


class TestMermaidLiveUrl:
    """Mermaid live URL generation."""

    def test_returns_valid_url(self):
        url = mermaid_live_url("graph TD\n  A-->B")
        assert url.startswith("https://mermaid.live/edit#base64:")

    def test_base64_contains_source(self):
        source = "graph TD\n  A-->B"
        url = mermaid_live_url(source)
        encoded_part = url.split("#base64:")[1]
        decoded = json.loads(base64.urlsafe_b64decode(encoded_part))
        assert decoded["code"] == source.strip()
        assert decoded["mermaid"]["theme"] == "default"
        assert decoded["autoSync"] is True
