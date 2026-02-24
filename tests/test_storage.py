"""Tests for mdreview.storage — hash, sidecar I/O, snapshots, drift."""

from __future__ import annotations

import json

from mdreview.models import Comment, ReviewFile, ReviewStatus
from mdreview.storage import (
    compute_hash,
    load_review,
    load_snapshot,
    reconcile_drift,
    save_snapshot,
    sidecar_path,
    snapshot_path,
)


class TestComputeHash:
    """inline-comments: Content hash computation."""

    def test_deterministic(self):
        assert compute_hash("hello") == compute_hash("hello")

    def test_sha256_prefix(self):
        h = compute_hash("test")
        assert h.startswith("sha256:")

    def test_different_content_different_hash(self):
        assert compute_hash("a") != compute_hash("b")


class TestSaveLoadReview:
    """inline-comments: Comment persistence roundtrip."""

    def test_roundtrip_preserves_all_fields(self, tmp_review_file):
        md_path, original = tmp_review_file
        loaded = load_review(md_path)

        assert loaded.file == original.file
        assert loaded.content_hash == original.content_hash
        assert loaded.status == original.status
        assert loaded.reviewed_at == original.reviewed_at
        assert len(loaded.comments) == len(original.comments)

        for orig, load in zip(original.comments, loaded.comments):
            assert load.id == orig.id
            assert load.line_start == orig.line_start
            assert load.line_end == orig.line_end
            assert load.anchor_text == orig.anchor_text
            assert load.body == orig.body
            assert load.created_at == orig.created_at
            assert load.orphaned == orig.orphaned
            assert load.updated_at == orig.updated_at

    def test_fresh_review_when_no_sidecar(self, tmp_md_file):
        review = load_review(tmp_md_file)
        assert review.file == tmp_md_file.name
        assert review.status == ReviewStatus.UNREVIEWED
        assert review.comments == []

    def test_sidecar_file_location(self, tmp_md_file):
        sp = sidecar_path(tmp_md_file)
        assert sp.name == "test.md.review.json"

    def test_backward_compat_missing_updated_at(self, tmp_path):
        """comment-editing: Backward compatibility with existing review files."""
        md = tmp_path / "old.md"
        md.write_text("# Old\n")

        # Write a sidecar without updated_at field
        sp = sidecar_path(md)
        sp.write_text(
            json.dumps(
                {
                    "file": "old.md",
                    "content_hash": "",
                    "status": "unreviewed",
                    "comments": [
                        {
                            "id": "12345678",
                            "line_start": 1,
                            "line_end": 1,
                            "anchor_text": "# Old",
                            "body": "A comment",
                            "created_at": "2026-01-01T00:00:00+00:00",
                            "orphaned": False,
                        }
                    ],
                    "reviewed_at": None,
                }
            )
        )

        review = load_review(md)
        assert len(review.comments) == 1
        assert review.comments[0].updated_at is None


class TestSaveLoadSnapshot:
    """round-diff: Snapshot save and load roundtrip."""

    def test_roundtrip(self, tmp_md_file):
        content = "snapshot content here"
        save_snapshot(tmp_md_file, content)
        loaded = load_snapshot(tmp_md_file)
        assert loaded == content

    def test_no_snapshot_returns_none(self, tmp_md_file):
        assert load_snapshot(tmp_md_file) is None

    def test_snapshot_file_location(self, tmp_md_file):
        sp = snapshot_path(tmp_md_file)
        assert sp.name == "test.md.snapshot"


class TestReconcileDrift:
    """inline-comments: Anchor drift detection and reconciliation."""

    def test_no_change_when_anchor_still_matches(self):
        """No drift when anchor text is at the expected position."""
        review = ReviewFile(
            file="test.md",
            comments=[
                Comment(
                    line_start=1,
                    line_end=1,
                    anchor_text="# Hello",
                    body="comment",
                )
            ],
        )
        lines = ["# Hello", "", "Content"]
        changed = reconcile_drift(review, lines)
        assert changed is False
        assert review.comments[0].line_start == 1
        assert review.comments[0].orphaned is False

    def test_successful_reanchor(self):
        """Comment drifts to new position when line is moved."""
        review = ReviewFile(
            file="test.md",
            comments=[
                Comment(
                    line_start=1,
                    line_end=2,
                    anchor_text="# Hello",
                    body="comment",
                )
            ],
        )
        # Line moved from position 0 to position 2 (0-indexed)
        lines = ["New first line", "", "# Hello", "More content"]
        changed = reconcile_drift(review, lines)
        assert changed is True
        assert review.comments[0].line_start == 3  # 1-indexed
        assert review.comments[0].line_end == 4
        assert review.comments[0].orphaned is False

    def test_orphan_marking(self):
        """Comment marked orphaned when anchor text not found."""
        review = ReviewFile(
            file="test.md",
            comments=[
                Comment(
                    line_start=1,
                    line_end=1,
                    anchor_text="This line was deleted entirely",
                    body="comment",
                )
            ],
        )
        lines = ["Completely different content", "Nothing similar at all"]
        changed = reconcile_drift(review, lines)
        assert changed is True
        assert review.comments[0].orphaned is True

    def test_empty_anchor_skipped(self):
        """Comments with empty anchor_text are skipped."""
        review = ReviewFile(
            file="test.md",
            comments=[
                Comment(line_start=1, line_end=1, anchor_text="", body="comment")
            ],
        )
        lines = ["anything"]
        changed = reconcile_drift(review, lines)
        assert changed is False
