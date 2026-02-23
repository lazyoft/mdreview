"""Tests for mdreview.diff — block-level diff computation."""

from __future__ import annotations

from mdreview.diff import BlockDiff, RemovedBlock, _refine_replace, compute_block_diff


class TestComputeBlockDiff:
    """round-diff: Block-level diff computation."""

    def test_unchanged_content(self):
        """round-diff: Content identical to snapshot."""
        lines = ["# Title", "", "Content"]
        block_ranges = [(0, 1), (2, 3)]
        diffs, removed = compute_block_diff(lines, lines, block_ranges)
        assert all(d.tag == "unchanged" for d in diffs)
        assert removed == []

    def test_changed_block(self):
        """round-diff: Diff with changes — blocks tagged as changed."""
        snapshot = ["# Title", "", "Old content"]
        current = ["# Title", "", "New content"]
        block_ranges = [(0, 1), (2, 3)]
        diffs, removed = compute_block_diff(snapshot, current, block_ranges)
        assert diffs[0].tag == "unchanged"
        assert diffs[1].tag == "changed"
        assert diffs[1].old_lines == ["Old content"]

    def test_new_block(self):
        """round-diff: New blocks tagged as new."""
        snapshot = ["# Title"]
        current = ["# Title", "", "Brand new content"]
        block_ranges = [(0, 1), (2, 3)]
        diffs, removed = compute_block_diff(snapshot, current, block_ranges)
        assert diffs[0].tag == "unchanged"
        assert diffs[1].tag == "new"

    def test_removed_block(self):
        """round-diff: Removed blocks detected."""
        snapshot = ["# Title", "", "This will be removed", "", "Kept"]
        current = ["# Title", "", "Kept"]
        block_ranges = [(0, 1), (2, 3)]
        diffs, removed = compute_block_diff(snapshot, current, block_ranges)
        assert len(removed) >= 1
        assert any("removed" in r.content.lower() for r in removed)

    def test_none_range_treated_as_unchanged(self):
        """Blocks with None source_range are treated as unchanged."""
        snapshot = ["# Title", "Content"]
        current = ["# Title", "Changed"]
        block_ranges = [None, (1, 2)]
        diffs, _ = compute_block_diff(snapshot, current, block_ranges)
        assert diffs[0].tag == "unchanged"
        assert diffs[1].tag == "changed"


class TestRefineReplace:
    """round-diff: Character-level similarity refinement."""

    def test_similar_lines_marked_changed(self):
        """Lines with high similarity to snapshot are marked changed."""
        snapshot = ["The quick brown fox jumps"]
        current = ["The quick brown dog jumps"]
        changed, new, old_map = _refine_replace(snapshot, current, 0, 1, 0, 1)
        assert 0 in changed
        assert not new

    def test_dissimilar_lines_marked_new(self):
        """Lines with no good match are marked new."""
        snapshot = ["aaaa bbbb cccc"]
        current = ["xxxx yyyy zzzz"]
        changed, new, old_map = _refine_replace(snapshot, current, 0, 1, 0, 1)
        assert 0 in new
        assert not changed

    def test_blank_lines_treated_as_new(self):
        """Blank lines in a replace block are filler, treated as new."""
        snapshot = ["content"]
        current = ["", "content modified"]
        changed, new, old_map = _refine_replace(snapshot, current, 0, 1, 0, 2)
        assert 0 in new  # blank line
