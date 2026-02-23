"""CLI entry point for mdreview."""

from pathlib import Path

import click


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
def main(files: tuple[str, ...], directory: str | None, open_config: bool) -> None:
    """Review markdown documents with inline comments."""
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
