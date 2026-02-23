## 1. Package Metadata

- [x] 1.1 Add `description` field to `pyproject.toml`: one-line project summary
- [x] 1.2 Add `authors` field with name and email
- [x] 1.3 Add `license` field with SPDX identifier (MIT)
- [x] 1.4 Add `classifiers` list: Python versions, topic, environment (console)
- [x] 1.5 Add `readme` field pointing to `README.md`
- [x] 1.6 Add `[project.urls]` section with Homepage, Repository, and Issues URLs

## 2. Verification

- [x] 2.1 Test `pipx install .` from project root and verify `mdreview --help` works from a non-project directory
- [x] 2.2 Test `uv tool install .` from project root and verify `mdreview --help` works
- [x] 2.3 Verify all runtime imports succeed in the isolated environment (no ImportError)
