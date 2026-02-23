"""Shared fixtures for mdreview tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mdreview.models import Comment, ReviewFile, ReviewStatus
from mdreview.storage import compute_hash, save_review, save_snapshot


@pytest.fixture
def tmp_md_file(tmp_path: Path) -> Path:
    """Create a temporary markdown file with sample content."""
    md = tmp_path / "test.md"
    md.write_text("# Hello\n\nSome content here.\n\n## Section 2\n\nMore text.\n")
    return md


@pytest.fixture
def tmp_review_file(tmp_md_file: Path) -> tuple[Path, ReviewFile]:
    """Create a markdown file with an associated .review.json sidecar."""
    content = tmp_md_file.read_text()
    review = ReviewFile(
        file=tmp_md_file.name,
        content_hash=compute_hash(content),
        status=ReviewStatus.CHANGES_REQUESTED,
        comments=[
            Comment(
                line_start=1,
                line_end=1,
                anchor_text="# Hello",
                body="Consider a better title",
                id="aabbccdd",
                created_at="2026-01-01T00:00:00+00:00",
            ),
            Comment(
                line_start=3,
                line_end=3,
                anchor_text="Some content here.",
                body="Needs more detail",
                id="eeff0011",
                created_at="2026-01-01T00:01:00+00:00",
                updated_at="2026-01-02T00:00:00+00:00",
            ),
        ],
        reviewed_at="2026-01-01T00:05:00+00:00",
    )
    save_review(tmp_md_file, review)
    return tmp_md_file, review


@pytest.fixture
def tmp_snapshot_file(tmp_md_file: Path) -> tuple[Path, str]:
    """Create a markdown file with a .snapshot file."""
    snapshot_content = "# Old Title\n\nOld content.\n"
    save_snapshot(tmp_md_file, snapshot_content)
    return tmp_md_file, snapshot_content
