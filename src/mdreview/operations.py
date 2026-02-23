"""Pure domain operations for review actions, decoupled from Textual UI."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from mdreview.models import Comment, ReviewFile, ReviewStatus
from mdreview.storage import compute_hash, reconcile_drift


# --- Comment operations ---


def add_comment(
    review: ReviewFile,
    lines: list[str],
    line_start: int,
    line_end: int,
    body: str,
) -> Comment:
    """Create a comment and append it to the review."""
    anchor = lines[line_start - 1].strip() if line_start - 1 < len(lines) else ""
    comment = Comment(
        line_start=line_start,
        line_end=line_end,
        anchor_text=anchor,
        body=body,
    )
    review.comments.append(comment)
    return comment


def delete_comment(review: ReviewFile, comment_id: str) -> bool:
    """Remove a comment by id. Returns True if found and removed."""
    before = len(review.comments)
    review.comments = [c for c in review.comments if c.id != comment_id]
    return len(review.comments) < before


def edit_comment(
    review: ReviewFile, comment_id: str, new_body: str
) -> Comment | None:
    """Update a comment's body. Returns the comment if changed, None otherwise."""
    for c in review.comments:
        if c.id == comment_id:
            if c.body == new_body:
                return None
            c.body = new_body
            c.updated_at = datetime.now(timezone.utc).isoformat()
            return c
    return None


def delete_all_comments(review: ReviewFile) -> int:
    """Remove all comments, reset status. Returns count of deleted comments."""
    count = len(review.comments)
    if count:
        review.comments.clear()
        review.status = ReviewStatus.UNREVIEWED
        review.reviewed_at = None
    return count


# --- Review decision operations ---


def approve_file(review: ReviewFile) -> None:
    """Mark a review as approved."""
    review.status = ReviewStatus.APPROVED
    review.reviewed_at = datetime.now(timezone.utc).isoformat()


def request_changes(review: ReviewFile) -> None:
    """Mark a review as changes requested."""
    review.status = ReviewStatus.CHANGES_REQUESTED
    review.reviewed_at = datetime.now(timezone.utc).isoformat()


# --- Snapshot helper ---


def should_save_snapshot(content: str, existing_snapshot: str | None) -> bool:
    """Determine whether a snapshot should be saved after a review decision."""
    return existing_snapshot != content


# --- Exit code ---


def compute_exit_code(reviews: list[ReviewFile]) -> int:
    """Compute exit code: 0=all approved, 1=changes requested, 2=unreviewed."""
    has_unreviewed = any(r.status == ReviewStatus.UNREVIEWED for r in reviews)
    if has_unreviewed:
        return 2
    has_changes = any(
        r.status == ReviewStatus.CHANGES_REQUESTED for r in reviews
    )
    if has_changes:
        return 1
    return 0


# --- File change handling ---


class ContentChangeResult(NamedTuple):
    changed: bool
    new_hash: str
    lines: list[str]


def handle_content_change(
    review: ReviewFile, new_content: str, old_hash: str
) -> ContentChangeResult:
    """Process a file content change. Reconciles drift if needed."""
    new_hash = compute_hash(new_content)
    lines = new_content.splitlines()

    if new_hash == old_hash:
        return ContentChangeResult(changed=False, new_hash=old_hash, lines=lines)

    if review.comments:
        reconcile_drift(review, lines)

    review.content_hash = new_hash
    return ContentChangeResult(changed=True, new_hash=new_hash, lines=lines)


# --- Summary ---


def format_summary(files: list[Path], reviews: list[ReviewFile]) -> str:
    """Generate the review summary text."""
    lines = ["\nReview complete:"]

    for i, path in enumerate(files):
        review = reviews[i]
        parent = path.parent.name
        name = f"{parent}/{path.name}" if parent else path.name

        match review.status:
            case ReviewStatus.APPROVED:
                icon = "\u2713"
                label = "approved"
            case ReviewStatus.CHANGES_REQUESTED:
                count = len(review.comments)
                icon = "\u2717"
                label = f"changes requested ({count} comment{'s' if count != 1 else ''})"
            case _:
                icon = "-"
                label = "not reviewed"

        lines.append(f"  {icon} {name:40s} {label}")

    approved = sum(1 for r in reviews if r.status == ReviewStatus.APPROVED)
    changes = sum(
        1 for r in reviews if r.status == ReviewStatus.CHANGES_REQUESTED
    )
    unreviewed = sum(
        1 for r in reviews if r.status == ReviewStatus.UNREVIEWED
    )

    lines.append("")
    if approved:
        lines.append(f"  {approved} approved")
    if changes:
        lines.append(f"  {changes} changes requested")
    if unreviewed:
        lines.append(f"  {unreviewed} not reviewed")

    exit_code = compute_exit_code(reviews)
    lines.append(f"\nExit code: {exit_code}")

    return "\n".join(lines)
