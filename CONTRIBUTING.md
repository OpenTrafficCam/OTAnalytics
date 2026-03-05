# Contributing Guide

Thank you for your interest in contributing! We welcome contributions from both human developers and AI-assisted
workflows (Claude Code, GitHub Copilot, Cursor, Codex, etc.).

Not familiar with the project yet? Start with the [README](./README.md) to understand what OTAnalytics does and how to
use it.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Standards](#code-standards)
4. [Testing](#testing)
5. [Submitting a Pull Request](#submitting-a-pull-request)
6. [AI-Assisted Contributions](#ai-assisted-contributions)
7. [Issue Guidelines](#issue-guidelines)
8. [Commit Message Format](#commit-message-format)
9. [Code of Conduct](#code-of-conduct)

---

## Getting Started

Contributions are welcome beyond just code. You can help by:

- **Reporting bugs** — open an issue with reproduction steps
- **Improving documentation** — fix typos, clarify explanations, add examples
- **Triaging issues** — confirm bugs, add missing details, link duplicates
- **Writing or improving tests** — increase coverage or add edge cases
- **Implementing features or fixes** — see below for the code workflow

For code contributions:

1. Fork the repository and clone your fork.
2. Create a new branch for your change: `git checkout -b feat/your-feature-name`
3. Make your changes, add tests, and open a pull request.

For AI agents: also read [AGENTS.md](./AGENTS.md) for machine-readable setup instructions.

---

## Development Setup

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

**Linux/macOS:**

```bash
./install_dev.sh
```

**Windows:**

```cmd
install_dev.cmd
```

This creates a `.venv`, installs all dependencies (including dev extras), installs Playwright browsers,
and sets up the pre-commit hooks.

Key commands (run from the repo root):

| Task         | Command                             |
|--------------|-------------------------------------|
| Run tests    | `uv run pytest`                     |
| Lint         | `uv run flake8`                     |
| Format       | `uv run black .`                    |
| Sort imports | `uv run isort .`                    |
| Type check   | `uv run mypy OTAnalytics tests`     |
| All checks   | `uv run pre-commit run --all-files` |

---

## Code Standards

- **Formatting:** [Black](https://black.readthedocs.io/) for code formatting and [isort](https://pycqa.github.io/isort/) for import ordering.
- **Linting:** [Flake8](https://flake8.pycqa.org/) for style and error checking.
- **Type hints:** All public functions and methods must have type annotations.
- **Docstrings:** Google-style docstrings for all public APIs.
- **No dead code:** Remove unused imports and variables before submitting.
- **Backwards compatibility:** Do not break public API without a deprecation path and a note in the changelog.

---

## Testing

- Tests live in the `tests/` directory and are written with [pytest](https://docs.pytest.org/).
- Every bug fix must include a regression test.
- Every new feature must include unit tests.
- Aim for meaningful coverage of edge cases, not just the happy path.

```bash
pytest                        # run all tests
pytest tests/test_foo.py      # run a single file
pytest -k "test_bar"          # run tests matching a name
pytest --cov=src --cov-report=term-missing  # with coverage
```

---

## Submitting a Pull Request

1. Ensure all tests pass and all linters are clean.
2. Write a clear PR description explaining *what* changed and *why*.
3. Reference the related issue (e.g., `Closes #42`).
4. Keep PRs focused: one logical change per PR.
5. Be responsive to review feedback.

Maintainers aim to triage new pull requests within **two weeks**. If you have not heard back after that, feel free to
ping the PR thread.

Pull requests that fail CI checks will not be merged.

All merged contributors are automatically listed in the [GitHub contributors graph](../../graphs/contributors).
Significant contributions are also noted in the changelog.

By submitting a pull request you confirm that your contribution may be distributed under the project's
[GPL-3.0 License](./LICENSE).

---

## AI-Assisted Contributions

We explicitly welcome contributions created with or assisted by AI tools. To maintain quality and trust, we ask you to
follow these guidelines.

### Disclosure is required

If any part of your contribution (code, tests, documentation) was generated or substantially assisted by an AI tool, you
**must** disclose this in the PR description.

Include:

- **Which tool(s)** you used (e.g., Claude Code, GitHub Copilot, Cursor, ChatGPT)
- **What the AI produced** (e.g., "initial implementation", "refactoring", "docstrings", "test cases")
- **What you reviewed and validated** yourself

Example PR description footer:

```
AI Disclosure: Initial implementation generated with Claude Code (claude-sonnet-4-6).
Tests and docstrings also AI-assisted. I reviewed all logic, ran the full test suite,
and manually verified the behavior against the documented requirements.
```

### You are accountable for all submitted code

AI-generated code is held to exactly the same standards as human-written code. By submitting a PR, you confirm that you
have:

- Read and understood every line of the diff
- Verified correctness against the issue requirements
- Ensured tests cover the relevant cases
- Checked for potential security, licensing, or IP concerns

**Do not submit code you do not understand.** AI tools can produce plausible-looking but incorrect or insecure code. You
are the last line of defense before review.

### Commit attribution

If you used Claude Code or another tool that adds a `Co-Authored-By` trailer automatically, you may keep it. You may
also add it manually:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

Alternatively, use a plain trailer:

```
Assisted-by: GitHub Copilot
```

We do not require a specific format, but attribution should be honest and present.

### Licensing and IP

AI-generated code in this repository falls under the same license as all other contributions. By submitting, you agree
that your contribution may be distributed under the project's license. If you have reason to believe that a generated
snippet reproduces a third-party copyrighted work, do not submit it.

---

## Issue Guidelines

### Reporting a bug

Before filing, search [existing issues](../../issues) to avoid duplicates. When opening a bug report, include:

- **OTAnalytics version** and Python version
- **Operating system**
- **Steps to reproduce** — the minimal sequence that reliably triggers the bug
- **Expected behavior** — what you expected to happen
- **Actual behavior** — what actually happened (error message, stack trace, screenshot)

Bug reports without reproduction steps may be closed without investigation.

### Finding a good first issue

New to the codebase? Issues labelled [`good first issue`](../../labels/good%20first%20issue) are well-scoped entry
points with enough context to get started without deep knowledge of the project.

### Finding AI-ready issues

Issues labelled [`llm-welcome`](../../labels/llm-welcome) are specifically scoped and documented to be well-suited for
AI-assisted contributions. They include:

- A clear problem description
- Expected behavior / acceptance criteria
- Pointers to relevant files
- A defined scope with no hidden dependencies

### Writing AI-ready issues

If you are filing a bug or feature request and want it to be AI-agent-friendly, please include:

```markdown
## Problem

[What is wrong or missing]

## Expected Behavior

[What success looks like]

## Relevant Files

- `src/mypackage/module.py`

## Acceptance Criteria

- [ ] Existing tests still pass
- [ ] New tests cover the described behavior
- [ ] Public API unchanged (or documented as breaking)
```

---

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`

Examples:

```
feat(parser): add support for nested expressions
fix(cli): handle missing config file gracefully
docs: update CONTRIBUTING.md with AI contribution policy
```

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md).
By participating you agree to abide by its terms. Report violations to [team@opentrafficcam.org](mailto:team@opentrafficcam.org).

---

## Questions?

Open a [Discussion](../../discussions) or email [team@opentrafficcam.org](mailto:team@opentrafficcam.org).
We are happy to help both human and AI-assisted contributors get started.
