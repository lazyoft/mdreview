"""Tests for mdreview.operations — pure domain logic decoupled from Textual."""

from pathlib import Path

from mdreview.models import Comment, ReviewFile, ReviewStatus
from mdreview.operations import (
    add_comment,
    approve_file,
    compute_exit_code,
    delete_all_comments,
    delete_comment,
    edit_comment,
    format_summary,
    handle_content_change,
    request_changes,
    should_save_snapshot,
)
from mdreview.storage import compute_hash


# --- Comment operations ---


class TestAddComment:
    def _make_review(self):
        return ReviewFile(file="test.md")

    def test_add_comment_basic(self):
        review = self._make_review()
        lines = ["# Title", "Some content", "More content"]
        comment = add_comment(review, lines, 2, 3, "Needs rewording")

        assert comment.line_start == 2
        assert comment.line_end == 3
        assert comment.anchor_text == "Some content"
        assert comment.body == "Needs rewording"
        assert len(comment.id) == 8
        assert comment.created_at is not None
        assert comment in review.comments

    def test_add_comment_anchor_out_of_range(self):
        review = self._make_review()
        lines = ["only line"]
        comment = add_comment(review, lines, 5, 5, "Ghost comment")

        assert comment.anchor_text == ""
        assert comment in review.comments

    def test_add_comment_strips_anchor(self):
        review = self._make_review()
        lines = ["  indented line  "]
        comment = add_comment(review, lines, 1, 1, "Check indent")

        assert comment.anchor_text == "indented line"


class TestDeleteComment:
    def test_delete_existing_comment(self):
        review = ReviewFile(file="test.md")
        comment = Comment(line_start=1, line_end=1, anchor_text="x", body="y", id="abc123")
        review.comments.append(comment)

        result = delete_comment(review, "abc123")
        assert result is True
        assert len(review.comments) == 0

    def test_delete_nonexistent_comment(self):
        review = ReviewFile(file="test.md")
        comment = Comment(line_start=1, line_end=1, anchor_text="x", body="y", id="abc123")
        review.comments.append(comment)

        result = delete_comment(review, "nonexistent")
        assert result is False
        assert len(review.comments) == 1


class TestEditComment:
    def test_edit_comment_changes_body(self):
        review = ReviewFile(file="test.md")
        comment = Comment(line_start=1, line_end=1, anchor_text="x", body="old", id="abc123")
        review.comments.append(comment)

        result = edit_comment(review, "abc123", "new body")
        assert result is not None
        assert result.body == "new body"
        assert result.updated_at is not None

    def test_edit_comment_unchanged_body(self):
        review = ReviewFile(file="test.md")
        comment = Comment(line_start=1, line_end=1, anchor_text="x", body="same", id="abc123")
        review.comments.append(comment)

        result = edit_comment(review, "abc123", "same")
        assert result is None

    def test_edit_nonexistent_comment(self):
        review = ReviewFile(file="test.md")
        result = edit_comment(review, "nonexistent", "new")
        assert result is None


class TestDeleteAllComments:
    def test_delete_all_with_comments(self):
        review = ReviewFile(
            file="test.md",
            status=ReviewStatus.CHANGES_REQUESTED,
            reviewed_at="2026-01-01T00:00:00+00:00",
        )
        review.comments.append(Comment(line_start=1, line_end=1, anchor_text="x", body="a"))
        review.comments.append(Comment(line_start=2, line_end=2, anchor_text="y", body="b"))

        count = delete_all_comments(review)
        assert count == 2
        assert len(review.comments) == 0
        assert review.status == ReviewStatus.UNREVIEWED
        assert review.reviewed_at is None

    def test_delete_all_with_no_comments(self):
        review = ReviewFile(file="test.md", status=ReviewStatus.APPROVED)
        count = delete_all_comments(review)
        assert count == 0
        assert review.status == ReviewStatus.APPROVED  # unchanged


# --- Review decision operations ---


class TestApproveFile:
    def test_approve_sets_status(self):
        review = ReviewFile(file="test.md")
        approve_file(review)
        assert review.status == ReviewStatus.APPROVED
        assert review.reviewed_at is not None

    def test_approve_overwrites_previous_status(self):
        review = ReviewFile(file="test.md", status=ReviewStatus.CHANGES_REQUESTED)
        approve_file(review)
        assert review.status == ReviewStatus.APPROVED


class TestRequestChanges:
    def test_request_changes_sets_status(self):
        review = ReviewFile(file="test.md")
        request_changes(review)
        assert review.status == ReviewStatus.CHANGES_REQUESTED
        assert review.reviewed_at is not None


# --- Snapshot helper ---


class TestShouldSaveSnapshot:
    def test_content_differs(self):
        assert should_save_snapshot("new content", "old content") is True

    def test_content_matches(self):
        assert should_save_snapshot("same", "same") is False

    def test_no_existing_snapshot(self):
        assert should_save_snapshot("content", None) is True


# --- Exit code ---


class TestComputeExitCode:
    def test_all_approved(self):
        reviews = [
            ReviewFile(file="a.md", status=ReviewStatus.APPROVED),
            ReviewFile(file="b.md", status=ReviewStatus.APPROVED),
        ]
        assert compute_exit_code(reviews) == 0

    def test_changes_requested(self):
        reviews = [
            ReviewFile(file="a.md", status=ReviewStatus.APPROVED),
            ReviewFile(file="b.md", status=ReviewStatus.CHANGES_REQUESTED),
        ]
        assert compute_exit_code(reviews) == 1

    def test_unreviewed(self):
        reviews = [
            ReviewFile(file="a.md", status=ReviewStatus.APPROVED),
            ReviewFile(file="b.md", status=ReviewStatus.UNREVIEWED),
        ]
        assert compute_exit_code(reviews) == 2

    def test_unreviewed_takes_precedence(self):
        reviews = [
            ReviewFile(file="a.md", status=ReviewStatus.CHANGES_REQUESTED),
            ReviewFile(file="b.md", status=ReviewStatus.UNREVIEWED),
        ]
        assert compute_exit_code(reviews) == 2


# --- File change handling ---


class TestHandleContentChange:
    def test_content_changed_with_comments(self):
        review = ReviewFile(file="test.md", content_hash=compute_hash("old"))
        review.comments.append(
            Comment(line_start=1, line_end=1, anchor_text="old line", body="note")
        )

        result = handle_content_change(review, "new content\n", review.content_hash)
        assert result.changed is True
        assert result.new_hash == compute_hash("new content\n")
        assert result.lines == ["new content"]
        assert review.content_hash == result.new_hash

    def test_content_unchanged(self):
        content = "same content"
        current_hash = compute_hash(content)
        review = ReviewFile(file="test.md", content_hash=current_hash)

        result = handle_content_change(review, content, current_hash)
        assert result.changed is False
        assert result.new_hash == current_hash

    def test_content_changed_without_comments(self):
        old_hash = compute_hash("old")
        review = ReviewFile(file="test.md", content_hash=old_hash)

        result = handle_content_change(review, "new", old_hash)
        assert result.changed is True
        assert len(review.comments) == 0  # no drift to reconcile


# --- Summary ---


class TestFormatSummary:
    def test_mixed_statuses(self):
        files = [Path("/docs/a.md"), Path("/docs/b.md"), Path("/docs/c.md")]
        reviews = [
            ReviewFile(file="a.md", status=ReviewStatus.APPROVED),
            ReviewFile(
                file="b.md",
                status=ReviewStatus.CHANGES_REQUESTED,
                comments=[Comment(line_start=1, line_end=1, anchor_text="x", body="fix")],
            ),
            ReviewFile(file="c.md", status=ReviewStatus.UNREVIEWED),
        ]

        text = format_summary(files, reviews)
        assert "approved" in text
        assert "changes requested" in text
        assert "not reviewed" in text
        assert "1 approved" in text
        assert "1 changes requested" in text
        assert "1 not reviewed" in text
        assert "Exit code: 2" in text

    def test_all_approved(self):
        files = [Path("/docs/a.md")]
        reviews = [ReviewFile(file="a.md", status=ReviewStatus.APPROVED)]

        text = format_summary(files, reviews)
        assert "Exit code: 0" in text
