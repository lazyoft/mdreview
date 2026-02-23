# mdreview

Terminal UI for reviewing markdown documents with inline comments. Built with Python and [Textual](https://textual.textualize.io/).

## Features

- **Inline comments** — select line ranges and add comments, stored in sidecar `.review.json` files
- **Review workflow** — approve or request changes on each file, with exit codes for CI integration
- **Diff between rounds** — see what changed since your last review decision
- **Mermaid diagrams** — ASCII rendering in the terminal, or open in mermaid.live
- **Anchor drift** — comments follow content when lines are added, removed, or moved
- **Live reload** — files reload automatically when modified externally
- **Multi-file** — review multiple files or an entire directory in one session

## Installation

```bash
# From PyPI
pip install mdreview

# Or with uv
uv tool install mdreview

# Or with pipx
pipx install mdreview

# From source
uv tool install git+https://github.com/lazyoft/mdreview.git
```

## Usage

```bash
# Review a single file
mdreview document.md

# Review multiple files
mdreview chapter1.md chapter2.md chapter3.md

# Review all markdown files in a directory
mdreview --dir docs/
```

### Keybindings

| Key | Action |
|-----|--------|
| `Up/Down` | Move cursor between blocks |
| `Left/Right` | Previous/next file |
| `c` | Start/confirm line selection for comment |
| `Shift+Up/Down` | Extend selection |
| `Ctrl+S` | Submit comment (in modal) |
| `Esc` | Cancel selection or input |
| `d` | Delete comment (when popover visible) |
| `D` | Delete all comments on file |
| `e` | Edit comment |
| `A` | Approve file |
| `R` | Request changes |
| `v` | Toggle diff view |
| `f` | Open file selector |
| `m` | Toggle Mermaid ASCII/raw |
| `o` | Open Mermaid diagram in browser |
| `?` | Show help |
| `q` | Quit |

### Customizing Keybindings

All keybindings can be customized via a TOML config file. Run:

```bash
mdreview --config
```

This creates `~/.config/mdreview/keys.toml` (pre-populated with all defaults) and opens it in your `$EDITOR`. Edit any key and save — changes take effect next time you launch mdreview.

Example customization:

```toml
[keys]
quit = "x"
approve = "a"
cursor_up = "k"
cursor_down = "j"
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All files approved |
| `1` | Changes requested on one or more files |
| `2` | Incomplete — unreviewed files remain |

## Development

```bash
# Clone and install in dev mode
git clone https://github.com/lazyoft/mdreview.git
cd mdreview
uv venv && uv pip install -e ".[test]"

# Run tests
uv run pytest

# Lint
uv run ruff check src/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

[MIT](LICENSE)
