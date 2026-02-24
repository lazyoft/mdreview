## Context

mdreview is published on PyPI and can be installed globally via pipx, uv tool, or pip. Users currently have no built-in way to upgrade. The CLI uses Click and already has `--version` (via `click.version_option`).

## Goals / Non-Goals

**Goals:**
- Let users upgrade mdreview with a single `mdreview --update` command
- Detect the installation method and use the correct upgrade tool
- Show version before and after upgrade

**Non-Goals:**
- Auto-checking for updates on every run (no phone-home)
- Downgrading to a specific version
- Supporting installation from git URLs or local paths

## Decisions

**Detection strategy**: Check how mdreview was installed by inspecting the executable path. pipx installs into `~/.local/pipx/venvs/`, uv tool into `~/.local/share/uv/tools/`. If neither matches, fall back to `pip install --upgrade`.

Alternative considered: asking the user which tool they used. Rejected because the install path reliably indicates the tool, and prompting adds friction.

**Upgrade commands by method:**
- pipx: `pipx upgrade mdreview`
- uv tool: `uv tool upgrade mdreview`
- pip: `pip install --upgrade mdreview`

**Version comparison**: Read the version before upgrade via `importlib.metadata.version("mdreview")`. After running the upgrade subprocess, re-invoke `pip show mdreview` or parse the subprocess output to report the new version.

## Risks / Trade-offs

- [Upgrade subprocess fails due to permissions] -> Print the error and suggest running with appropriate permissions. Do not attempt sudo.
- [Package not on PyPI yet during development] -> The upgrade command will fail with a clear pip error. No special handling needed.
