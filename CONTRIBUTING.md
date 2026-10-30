# Contributing Guide

Thank you for your interest in contributing to OTAnalytics.

This repository welcomes both human-authored and AI-assisted contributions. Start with the [README](./README.md) for product-level context, then use this guide for contribution workflow.

## Documentation Hierarchy

Use the repository docs in this order:

1. `CONTRIBUTING.md`: contributor workflow and project policy
2. `AGENTS.md`: runtime instructions for coding agents
3. `docs/development/*.md`: detailed implementation, testing, and review references

If you see conflicting instructions, treat this file as the source of truth for contribution policy and raise the inconsistency in your PR.

## Getting Started

Contributions are welcome in several forms:
- bug reports and issue triage
- documentation improvements
- tests and regression coverage
- feature work and bug fixes

For code contributions:

1. Fork the repository and clone your fork.
2. Create a branch using `<type>/<issue_number>-<short-description>`.
3. Make the change, add or update tests as needed, and open a pull request.

For agent-based work, also read [AGENTS.md](./AGENTS.md).

## Development Setup

OTAnalytics requires Python `3.12` exactly and [uv](https://docs.astral.sh/uv/).

Install the development environment:
- Linux/macOS: `./install_dev.sh`
- Windows: `install_dev.cmd`

Common commands:

| Task | Command |
|---|---|
| Run tests | `uv run pytest` |
| Type check | `uv run mypy OTAnalytics tests` |
| Full verification | `uv run pre-commit run --all-files` and `uv run pytest` |

## Coding Standards

High-level expectations:
- preserve backward compatibility unless there is an explicit deprecation path
- add complete type annotations to new functions and methods
- use Google-style docstrings for public modules, classes, and functions
- avoid wildcard imports, bare `except:`, and commented-out code
- prefer `pathlib.Path` over `os.path` and `logging` over `print` in library code

Detailed guidance lives here:
- [Development References](./docs/development/README.md)
- [Code Style Reference](./docs/development/code-style.md)
- [Testing Reference](./docs/development/testing.md)
- [Reviewing Reference](./docs/development/reviewing.md)

## Testing Expectations

- Every bug fix must add a regression test.
- Every new public function must have at least one happy-path and one edge-case test.
- Tests must be deterministic and should mock only external I/O.
- Aim for at least 90% coverage on new code.

See [docs/development/testing.md](./docs/development/testing.md) for the Stage Play structure and detailed examples.

## Pull Requests

Before marking a PR as ready:
- run `uv run pre-commit run --all-files`
- run `uv run pytest`
- confirm new or changed behavior is covered by tests
- include AI disclosure in the PR description when applicable

In the PR description:
- explain what changed and why
- reference the related OpenProject issue, for example `OP#142`
- keep the PR focused on one logical change

## AI-Assisted Contributions

AI-assisted contributions are welcome, but the submitter remains accountable for the full diff.

If AI materially contributed to code, tests, or docs, disclose:
- which tool was used
- which parts were AI-assisted
- what you reviewed and validated yourself

Commit attribution is required when AI materially contributes:
- fully AI-generated commit: `Co-Authored-By: <tool or author>`
- human-driven commit with AI assistance: `Assisted-by: <tool>`

Use honest attribution that matches the actual workflow.

## Issues, Branches, and Commits

Branch format:

```text
<type>/<issue_number>-<short-description>
```

Allowed branch types: `task`, `bug`, `feature`, `refactor`

Commit format:

```text
OP#<issue_number>: <short summary, imperative, max 72 chars>
```

Every commit must reference the relevant OpenProject issue.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md).
Report violations to [team@opentrafficcam.org](mailto:team@opentrafficcam.org).
