## Context

mdreview is a personal project ready to be shared publicly. It has no LICENSE, README, contributing guide, or CI. These are the minimum requirements for an open-source project that welcomes external contributions.

## Goals / Non-Goals

**Goals:**
- Add standard open-source scaffolding: LICENSE, README, CONTRIBUTING, templates
- Set up GitHub Actions CI for linting and testing
- Make the project discoverable and approachable for contributors

**Non-Goals:**
- Marketing or documentation site (GitHub README is sufficient)
- Complex CI/CD (no deployment, release automation, or publishing pipeline)
- Code of conduct (can be added later if community grows)
- Changelog automation

## Decisions

### 1. License: MIT

**Choice**: MIT license — permissive, widely understood, no contributor friction.

**Alternatives considered**:
- *Apache 2.0*: Patent clause adds complexity without benefit for a TUI tool. Rejected.
- *GPL*: Too restrictive for a developer tool. Rejected.

### 2. README structure

- Project title + one-line description
- Screenshot or demo GIF
- Installation (pipx/uv/pip)
- Usage (basic commands)
- Development setup
- Contributing link
- License

### 3. CI: GitHub Actions

Single workflow file `.github/workflows/ci.yml`:
- Trigger: push to main, pull requests
- Matrix: Python 3.10, 3.11, 3.12, 3.13
- Steps: checkout, setup Python, install deps, ruff check, pytest
- Keep it simple — no caching, no publishing, no release automation

### 4. Issue and PR templates

Minimal templates:
- Bug report template (steps to reproduce, expected vs actual)
- Feature request template (description, use case)
- PR template (summary, test plan)

### 5. CONTRIBUTING.md

Cover:
- Development setup (`pip install -e ".[test]"`)
- Code style (ruff formatting, enforced by CI)
- Testing (`pytest`)
- PR workflow (fork, branch, PR)

## Risks / Trade-offs

- **[Stale templates]** → Keep templates minimal to reduce maintenance
- **[CI costs]** → GitHub free tier provides 2000 minutes/month, more than sufficient
