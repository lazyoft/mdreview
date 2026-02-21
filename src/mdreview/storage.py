"""Read/write .review.json sidecar files and handle anchor drift."""

from __future__ import annotations

import hashlib
import json
from difflib import SequenceMatcher
from pathlib import Path

from mdreview.models import Comment, ReviewFile, ReviewStatus

DRIFT_THRESHOLD = 0.6  # Minimum similarity ratio to accept a fuzzy re-anchor


def compute_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode()).hexdigest()


def sidecar_path(md_path: Path) -> Path:
    return md_path.with_suffix(md_path.suffix + ".review.json")


def load_review(md_path: Path) -> ReviewFile:
    """Load the review sidecar for a markdown file, or create a fresh one."""
    sp = sidecar_path(md_path)
    if not sp.exists():
        return ReviewFile(file=md_path.name)

    data = json.loads(sp.read_text())
    comments = [Comment(**c) for c in data.get("comments", [])]
    status = ReviewStatus(data.get("status", "unreviewed"))
    return ReviewFile(
        file=data.get("file", md_path.name),
        content_hash=data.get("content_hash", ""),
        status=status,
        comments=comments,
        reviewed_at=data.get("reviewed_at"),
    )


def save_review(md_path: Path, review: ReviewFile) -> None:
    """Write the review sidecar to disk."""
    sp = sidecar_path(md_path)
    data = {
        "file": review.file,
        "content_hash": review.content_hash,
        "status": review.status.value,
        "comments": [
            {
                "id": c.id,
                "line_start": c.line_start,
                "line_end": c.line_end,
                "anchor_text": c.anchor_text,
                "body": c.body,
                "created_at": c.created_at,
                "orphaned": c.orphaned,
            }
            for c in review.comments
        ],
        "reviewed_at": review.reviewed_at,
    }
    sp.write_text(json.dumps(data, indent=2) + "\n")


def snapshot_path(md_path: Path) -> Path:
    return md_path.with_suffix(md_path.suffix + ".snapshot")


def load_snapshot(md_path: Path) -> str | None:
    """Load the snapshot content for a markdown file, or None if not found."""
    sp = snapshot_path(md_path)
    if not sp.exists():
        return None
    return sp.read_text()


def save_snapshot(md_path: Path, content: str) -> None:
    """Write the snapshot content to disk."""
    sp = snapshot_path(md_path)
    sp.write_text(content)


def reconcile_drift(review: ReviewFile, lines: list[str]) -> bool:
    """Re-anchor comments when the markdown content has changed.

    Returns True if any comments were modified or orphaned.
    """
    changed = False
    for comment in review.comments:
        if not comment.anchor_text:
            continue

        # Check if anchor text still matches at recorded position
        start = comment.line_start - 1  # 1-indexed to 0-indexed
        if (
            0 <= start < len(lines)
            and lines[start].strip() == comment.anchor_text.strip()
        ):
            continue  # Still in place

        # Fuzzy search for the anchor text in the file
        best_idx = -1
        best_ratio = 0.0
        for i, line in enumerate(lines):
            ratio = SequenceMatcher(
                None, comment.anchor_text.strip(), line.strip()
            ).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_idx = i

        if best_ratio >= DRIFT_THRESHOLD and best_idx >= 0:
            offset = best_idx - (comment.line_start - 1)
            comment.line_start += offset
            comment.line_end += offset
            comment.anchor_text = lines[best_idx].strip()
            comment.orphaned = False
            changed = True
        else:
            comment.orphaned = True
            changed = True

    return changed
