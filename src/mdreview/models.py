"""Data models for mdreview."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class ReviewStatus(str, Enum):
    UNREVIEWED = "unreviewed"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"


@dataclass
class Comment:
    line_start: int
    line_end: int
    anchor_text: str
    body: str
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    orphaned: bool = False  # True if anchor could not be re-matched after drift
    updated_at: str | None = None


@dataclass
class ReviewFile:
    file: str
    content_hash: str = ""
    status: ReviewStatus = ReviewStatus.UNREVIEWED
    comments: list[Comment] = field(default_factory=list)
    reviewed_at: str | None = None
