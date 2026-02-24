## 1. Core Implementation

- [x] 1.1 Add a `detect_install_method()` function to `src/mdreview/cli.py` that inspects `sys.executable` to determine if installed via pipx, uv tool, or pip
- [x] 1.2 Add a `run_upgrade(method)` function that executes the appropriate upgrade command (`pipx upgrade`, `uv tool upgrade`, or `pip install --upgrade`)
- [x] 1.3 Add `--update` flag to the `main` Click command that calls detect + upgrade, prints version info, and exits

## 2. Testing

- [x] 2.1 Test `detect_install_method()` returns correct method for pipx, uv, and pip executable paths
- [x] 2.2 Test `--update` flag invokes upgrade subprocess and exits with code 0 on success
- [x] 2.3 Test `--update` flag exits with non-zero code when upgrade subprocess fails
