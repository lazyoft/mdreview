"""CLI entry point for mdreview."""

import sys
from importlib.metadata import version
from pathlib import Path

import click


def detect_install_method() -> str:
    """Detect how mdreview was installed by inspecting the executable path."""
    executable = sys.executable
    if "pipx" in executable:
        return "pipx"
    if "uv" in executable and "tools" in executable:
        return "uv"
    return "pip"


def get_installed_version() -> str:
    """Get the currently installed version, bypassing import cache."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "mdreview"],
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def run_upgrade(method: str) -> int:
    """Run the appropriate upgrade command. Returns the subprocess exit code."""
    import subprocess

    commands = {
        "pipx": ["pipx", "upgrade", "mdreview"],
        "uv": ["uv", "tool", "upgrade", "mdreview"],
        "pip": [sys.executable, "-m", "pip", "install", "--upgrade", "mdreview"],
    }
    cmd = commands[method]
    result = subprocess.run(cmd)
    return result.returncode


def collect_files(files: tuple[str, ...], directory: str | None) -> list[Path]:
    """Collect markdown files from positional args and --dir flag."""
    paths: list[Path] = []

    for f in files:
        p = Path(f)
        if p.is_file():
            paths.append(p.resolve())
        elif p.is_dir():
            paths.extend(sorted(p.rglob("*.md")))
        else:
            click.echo(f"Warning: skipping '{f}' (not found)", err=True)

    if directory:
        d = Path(directory)
        if d.is_dir():
            paths.extend(sorted(d.rglob("*.md")))
        else:
            click.echo(f"Error: directory '{directory}' not found", err=True)

    # Deduplicate while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in paths:
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)

    return unique


@click.command()
@click.version_option(version=version("mdreview"), prog_name="mdreview")
@click.argument("files", nargs=-1)
@click.option(
    "--dir", "directory", default=None, help="Recursively find .md files in directory"
)
@click.option(
    "--config",
    "open_config",
    is_flag=True,
    default=False,
    help="Open keybinding config in $EDITOR and exit",
)
@click.option(
    "--update",
    "do_update",
    is_flag=True,
    default=False,
    help="Upgrade mdreview to the latest version and exit",
)
def main(
    files: tuple[str, ...], directory: str | None, open_config: bool, do_update: bool
) -> None:
    """Review markdown documents with inline comments."""
    if do_update:
        current = version("mdreview")
        method = detect_install_method()
        click.echo(f"mdreview {current}, upgrading via {method}...")
        exit_code = run_upgrade(method)
        if exit_code != 0:
            raise SystemExit(exit_code)
        new = get_installed_version()
        if new != current:
            click.echo(f"Updated: {current} -> {new}")
        else:
            click.echo(f"Already up to date ({current}).")
        raise SystemExit(0)

    if open_config:
        import os
        import subprocess

        from mdreview.keybindings import ensure_config

        config_path = ensure_config()
        editor = os.environ.get("EDITOR", "vi")
        click.echo(f"Opening {config_path}")
        subprocess.run([editor, str(config_path)])
        raise SystemExit(0)

    paths = collect_files(files, directory)

    if not paths:
        click.echo(
            "No markdown files found. Usage: mdreview <file.md> [file2.md ...] [--dir <path>]"
        )
        raise SystemExit(2)

    from mdreview.app import ReviewApp
    from mdreview.keybindings import load_keybindings

    keybindings = load_keybindings()
    watch_dir = Path(directory).resolve() if directory else None
    app = ReviewApp(paths, watch_dir=watch_dir, keybindings=keybindings)
    result = app.run()
    raise SystemExit(result or 0)
