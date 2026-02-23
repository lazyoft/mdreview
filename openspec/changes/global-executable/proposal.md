## Why

Currently mdreview can only be run from its development virtualenv (`pip install -e .` in `.venv`). To use it system-wide — reviewing markdown files in any project directory — it needs to be installable as a global CLI tool via `pipx` or `uv tool install`.

## What Changes

- Ensure `pyproject.toml` metadata is complete for PyPI publishing (description, author, license, classifiers, URLs)
- Verify the `[project.scripts]` entry point works when installed outside the dev environment
- Add installation instructions for `pipx install mdreview` and `uv tool install mdreview`
- Ensure the package works with Python 3.10+ as declared

## Capabilities

### New Capabilities

- `global-install`: Packaging metadata, entry point validation, and installation instructions for system-wide CLI usage

### Modified Capabilities

_(none — the CLI interface itself does not change)_

## Impact

- `pyproject.toml`: Add/complete metadata fields (description, author, license, classifiers, project-urls)
- `README.md` or docs: Installation instructions (created as part of `github-open-source-ready` if running together)
- No source code changes expected — the existing `mdreview.cli:main` entry point already works
