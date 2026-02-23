## 1. Test Infrastructure

- [x] 1.1 Create `tests/` directory with `conftest.py` containing shared fixtures: `tmp_md_file`, `tmp_review_file`, `tmp_snapshot_file`
- [x] 1.2 Add `[project.optional-dependencies]` test group to `pyproject.toml` with `pytest` and `pytest-asyncio`
- [x] 1.3 Add `[tool.pytest.ini_options]` section to `pyproject.toml` with `asyncio_mode = "auto"`

## 2. Model Tests

- [x] 2.1 Create `tests/test_models.py` with tests for `Comment` creation (field defaults, id format), `ReviewFile` defaults, and `ReviewStatus` enum values

## 3. Storage Tests

- [x] 3.1 Create `tests/test_storage.py` with tests for `compute_hash` (deterministic, sha256 prefix)
- [x] 3.2 Add tests for `save_review` / `load_review` roundtrip (all fields preserved, missing `updated_at` backward compat)
- [x] 3.3 Add tests for `save_snapshot` / `load_snapshot` roundtrip
- [x] 3.4 Add tests for `reconcile_drift`: successful re-anchor, orphan marking, no-change case

## 4. Diff Tests

- [x] 4.1 Create `tests/test_diff.py` with tests for `compute_block_diff`: unchanged content, changed blocks, new blocks, removed blocks
- [x] 4.2 Add test for `_refine_replace` character-level similarity logic

## 5. Mermaid Tests

- [x] 5.1 Create `tests/test_mermaid.py` with tests for `preprocess_mermaid`: block detection, line range extraction
- [x] 5.2 Add test for `mermaid_live_url`: returns valid URL with base64-encoded state

## 6. Documentation

- [x] 6.1 Update `CLAUDE.md` to document test commands (`pytest`, `pip install -e ".[test]"`)
