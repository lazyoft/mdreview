## 1. License

- [x] 1.1 Create `LICENSE` file with MIT license text, current year, and author name

## 2. README

- [x] 2.1 Create `README.md` with: project title, one-line description, feature highlights, installation instructions (pipx/uv/pip), usage examples, development setup, and license reference

## 3. Contributing Guide

- [x] 3.1 Create `CONTRIBUTING.md` with: development setup (`pip install -e ".[test]"`), code style (ruff), testing (pytest), and PR workflow (fork, branch, PR)

## 4. GitHub Templates

- [x] 4.1 Create `.github/ISSUE_TEMPLATE/bug_report.md` with fields for steps to reproduce, expected behavior, actual behavior, environment
- [x] 4.2 Create `.github/ISSUE_TEMPLATE/feature_request.md` with fields for description and use case
- [x] 4.3 Create `.github/pull_request_template.md` with summary and test plan sections

## 5. CI Workflow

- [x] 5.1 Create `.github/workflows/ci.yml` with: trigger on push to main and PRs, Python 3.10-3.13 matrix, steps for checkout, setup Python, install deps, ruff check, pytest

## 6. Gitignore

- [x] 6.1 Review and update `.gitignore` to include: `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`, `dist/`, `build/`, `.review.json`, `.snapshot`, common IDE files
