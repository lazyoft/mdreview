"""Tests for mdreview.models — Comment, ReviewFile, ReviewStatus."""

from __future__ import annotations

import re

from mdreview.models import Comment, ReviewFile, ReviewStatus


class TestReviewStatus:
    """inline-comments: ReviewStatus enum values."""

    def test_enum_values(self):
        assert ReviewStatus.UNREVIEWED.value == "unreviewed"
        assert ReviewStatus.APPROVED.value == "approved"
        assert ReviewStatus.CHANGES_REQUESTED.value == "changes_requested"

    def test_string_coercion(self):
        assert str(ReviewStatus.APPROVED) == "ReviewStatus.APPROVED"
        assert ReviewStatus("approved") == ReviewStatus.APPROVED


class TestComment:
    """inline-comments: Comment creation."""

    def test_required_fields(self):
        c = Comment(line_start=1, line_end=5, anchor_text="# Title", body="Fix this")
        assert c.line_start == 1
        assert c.line_end == 5
        assert c.anchor_text == "# Title"
        assert c.body == "Fix this"

    def test_id_is_8_char_hex(self):
        c = Comment(line_start=1, line_end=1, anchor_text="x", body="y")
        assert len(c.id) == 8
        assert re.fullmatch(r"[0-9a-f]{8}", c.id)

    def test_unique_ids(self):
        ids = {
            Comment(line_start=1, line_end=1, anchor_text="x", body="y").id
            for _ in range(100)
        }
        assert len(ids) == 100

    def test_created_at_auto_set(self):
        c = Comment(line_start=1, line_end=1, anchor_text="x", body="y")
        assert c.created_at  # non-empty ISO string

    def test_orphaned_defaults_false(self):
        c = Comment(line_start=1, line_end=1, anchor_text="x", body="y")
        assert c.orphaned is False

    def test_updated_at_defaults_none(self):
        """comment-editing: New comment has no updated_at."""
        c = Comment(line_start=1, line_end=1, anchor_text="x", body="y")
        assert c.updated_at is None


class TestReviewFile:
    """inline-comments: ReviewFile defaults."""

    def test_defaults(self):
        rf = ReviewFile(file="test.md")
        assert rf.file == "test.md"
        assert rf.content_hash == ""
        assert rf.status == ReviewStatus.UNREVIEWED
        assert rf.comments == []
        assert rf.reviewed_at is None

    def test_with_status(self):
        rf = ReviewFile(file="test.md", status=ReviewStatus.APPROVED)
        assert rf.status == ReviewStatus.APPROVED
