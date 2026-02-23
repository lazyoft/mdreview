# Contributing to mdreview

Thanks for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/lazyoft/mdreview.git
cd mdreview
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

## Code Style

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
ruff check src/         # Lint
ruff format src/        # Format
```

CI will check both — please run them before submitting a PR.

## Testing

```bash
pytest              # Run all tests
pytest -v           # Verbose output
pytest tests/test_storage.py   # Run a specific module
```

Tests live in the `tests/` directory. When adding new features, include tests that validate the expected behavior.

## Pull Request Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Run tests and linting: `pytest && ruff check src/`
5. Commit with a clear message
6. Push and open a pull request against `main`

Keep PRs focused — one feature or fix per PR.
