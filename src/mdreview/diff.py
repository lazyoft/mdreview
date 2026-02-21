"""Block-level diff between snapshot and current markdown content."""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher


@dataclass
class RemovedBlock:
    """A block present in the snapshot but absent in the current content."""

    after_line: int  # 0-indexed line in current content after which this was removed
    content: str  # the removed text


@dataclass
class BlockDiff:
    """Diff result for a single block."""

    tag: str  # "unchanged", "changed", or "new"
    old_lines: list[str] = field(default_factory=list)  # for "changed": the replaced snapshot lines


SIMILARITY_THRESHOLD = 0.4


def _refine_replace(
    snapshot_lines: list[str],
    current_lines: list[str],
    i1: int, i2: int,
    j1: int, j2: int,
) -> tuple[set[int], set[int], dict[int, list[str]]]:
    """Refine a replace opcode into changed vs new lines.

    Uses character-level similarity to match current lines against snapshot
    lines. Lines with high similarity to a snapshot line are "changed";
    lines with no good match are "new" (insertions).

    Returns:
        changed: set of current line indices that are modifications
        new: set of current line indices that are pure insertions
        old_for_line: maps current line index -> snapshot lines it replaced
    """
    snap_chunk = snapshot_lines[i1:i2]
    curr_chunk = current_lines[j1:j2]

    changed: set[int] = set()
    new: set[int] = set()
    old_for_line: dict[int, list[str]] = {}
    matched_snap: set[int] = set()

    for cj, curr_line in enumerate(curr_chunk):
        if not curr_line.strip():
            # Blank lines in a replace block are filler, treat as new
            new.add(j1 + cj)
            continue

        best_ratio = 0.0
        best_si = -1
        for si, snap_line in enumerate(snap_chunk):
            if si in matched_snap or not snap_line.strip():
                continue
            ratio = SequenceMatcher(None, snap_line, curr_line).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_si = si

        if best_ratio >= SIMILARITY_THRESHOLD and best_si >= 0:
            changed.add(j1 + cj)
            old_for_line[j1 + cj] = [snap_chunk[best_si]]
            matched_snap.add(best_si)
        else:
            new.add(j1 + cj)

    return changed, new, old_for_line


def compute_block_diff(
    snapshot_lines: list[str],
    current_lines: list[str],
    block_ranges: list[tuple[int, int] | None],
) -> tuple[list[BlockDiff], list[RemovedBlock]]:
    """Compute diff tags for each markdown block.

    Args:
        snapshot_lines: Lines from the previous snapshot.
        current_lines: Lines from the current file.
        block_ranges: source_range (start, end) for each rendered block, 0-indexed.
            None entries are treated as unchanged.

    Returns:
        A tuple of:
        - List of BlockDiff per block (tag + old content for changed blocks)
        - List of RemovedBlock entries for content deleted between rounds
    """
    matcher = SequenceMatcher(None, snapshot_lines, current_lines)
    opcodes = matcher.get_opcodes()

    # Build line-level classification
    changed_lines: set[int] = set()
    new_lines: set[int] = set()
    old_for_line: dict[int, list[str]] = {}

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "replace":
            snap_count = i2 - i1
            curr_count = j2 - j1
            if snap_count == curr_count:
                # Same size replace — straightforward 1:1 mapping
                for offset in range(snap_count):
                    changed_lines.add(j1 + offset)
                    old_for_line[j1 + offset] = [snapshot_lines[i1 + offset]]
            else:
                # Size mismatch — refine to separate changed from new
                ch, nw, old_map = _refine_replace(
                    snapshot_lines, current_lines, i1, i2, j1, j2
                )
                changed_lines |= ch
                new_lines |= nw
                old_for_line.update(old_map)
        elif tag == "insert":
            for j in range(j1, j2):
                new_lines.add(j)

    # Tag each block
    diffs: list[BlockDiff] = []
    for source_range in block_ranges:
        if source_range is None:
            diffs.append(BlockDiff(tag="unchanged"))
            continue
        start, end = source_range
        block_lines = set(range(start, end))

        block_new = block_lines & new_lines
        block_changed = block_lines & changed_lines

        if block_new and not block_changed:
            diffs.append(BlockDiff(tag="new"))
        elif block_changed:
            # Collect old lines for this block
            old: list[str] = []
            seen: set[int] = set()
            for line_idx in sorted(block_lines & changed_lines):
                if line_idx in old_for_line:
                    # Deduplicate: same old_lines list shared by multiple current lines
                    key = id(old_for_line[line_idx])
                    if key not in seen:
                        old.extend(old_for_line[line_idx])
                        seen.add(key)
            diffs.append(BlockDiff(tag="changed", old_lines=old))
        else:
            diffs.append(BlockDiff(tag="unchanged"))

    # Collect removed blocks
    removed: list[RemovedBlock] = []
    for tag, i1, i2, j1, _j2 in opcodes:
        if tag == "delete":
            content = "\n".join(snapshot_lines[i1:i2])
            removed.append(RemovedBlock(after_line=j1, content=content))

    return diffs, removed
