## Context

mdreview is currently only usable via `pip install -e .` inside the project's `.venv`. The `pyproject.toml` already defines a `[project.scripts]` entry point (`mdreview = "mdreview.cli:main"`), so the CLI mechanism works. What's missing is complete packaging metadata for installation via `pipx` or `uv tool install`, which install packages into isolated environments and expose their console scripts globally.

## Goals / Non-Goals

**Goals:**
- Make `pipx install mdreview` and `uv tool install mdreview` work
- Ensure the package installs cleanly in an isolated environment (no dev-only assumptions)
- Complete pyproject.toml metadata for PyPI readiness

**Non-Goals:**
- Publishing to PyPI (that's a manual step for the maintainer)
- Creating platform-specific installers (brew, apt, etc.)
- Building standalone binaries (PyInstaller, Nuitka)

## Decisions

### 1. Complete pyproject.toml metadata

Add missing fields: `description`, `authors`, `license`, `classifiers`, `readme`, `project-urls`. These are required for PyPI and useful for `pipx`/`uv` display.

### 2. Installation methods

Document two primary paths:
- `pipx install mdreview` (recommended for most users)
- `uv tool install mdreview` (for uv users)
- `pip install mdreview` (also works, but pollutes global env)

### 3. Verify entry point works in isolation

Test by running `pipx install .` from the project root and confirming `mdreview --help` works from any directory.

## Risks / Trade-offs

- **[Missing dependency]** → All runtime deps already declared in pyproject.toml; verified by isolated install test
- **[Python version compatibility]** → `requires-python = ">=3.10"` already set; no 3.9-specific features used
