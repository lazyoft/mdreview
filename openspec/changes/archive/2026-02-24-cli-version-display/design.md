## Context

mdreview uses Click for its CLI (`src/mdreview/cli.py`) and hatch-vcs for versioning (git tag-based, configured in `pyproject.toml` with `dynamic = ["version"]`). The version is already available at runtime via `importlib.metadata` but is not exposed to users.

## Goals / Non-Goals

**Goals:**
- Let users check the installed version with `mdreview --version`

**Non-Goals:**
- Adding version info to the TUI itself (e.g., in a status bar or about screen)
- Changing the versioning scheme

## Decisions

**Use Click's built-in `@click.version_option`**: Click provides a `version_option` decorator that handles `--version` flag parsing and output formatting. This is simpler than a manual `--version` option and follows Click conventions. The version string is read lazily via `importlib.metadata.version("mdreview")`.

Alternative considered: manual `click.option("--version", is_flag=True)` with custom handler. Rejected because Click's built-in decorator handles edge cases (flag conflicts, help text) and is the idiomatic approach.

## Risks / Trade-offs

- [Version shows "0.0.0" if package not installed in editable mode] -> Document in README that `pip install -e .` is needed for dev. This is standard Python packaging behavior and already the case for the project.
