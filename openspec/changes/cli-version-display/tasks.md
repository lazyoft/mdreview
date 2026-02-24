## 1. Implementation

- [x] 1.1 Add `@click.version_option` decorator to the `main` command in `src/mdreview/cli.py`, using `importlib.metadata.version("mdreview")` for the version string

## 2. Testing

- [x] 2.1 Add test for `mdreview --version` output and exit code 0
- [x] 2.2 Add test that `--version` works without providing any markdown files
