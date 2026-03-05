# Contributing Guide

Thank you for your interest in contributing! We welcome contributions from both human developers and AI-assisted
workflows (Claude Code, GitHub Copilot, Cursor, Codex, etc.).

Not familiar with the project yet? Start with the [Readme](./README.md) to understand what OTAnalytics does and how to
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
8. [Branch Naming](#branch-naming)
9. [Commit Message Format](#commit-message-format)
10. [Code of Conduct](#code-of-conduct)

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
2. Create a new branch for your change: `git checkout -b feature/your-feature-name`
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

Key commands (run from the repository root):

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

### Tooling

- **Formatting:** [Black](https://black.readthedocs.io/) (line length 88) and [isort](https://pycqa.github.io/isort/)
  for import ordering.
- **Linting:** [Flake8](https://flake8.pycqa.org/) for style and error checking.
- **Type checking:** [mypy](https://mypy-lang.org/) — all functions and methods (public and private) must have complete
  type annotations.
- **Docstrings:** Google-style docstrings for all public functions, classes, and modules.
- **Backwards compatibility:** Do not break the public API without a deprecation path.

### General rules

- No wildcard imports (`from foo import *`).
- All imports at the top of the file, grouped and sorted by `isort`. No inline or conditional imports except to resolve
  circular imports (document that case with a comment).
- Raise specific exception types. No bare `except:` or `except Exception:` without re-raising or logging.
- Prefer `pathlib.Path` over `os.path` for file operations.
- Use `logging` (not `print`) for diagnostic output in library code.
- No dead code — remove unused imports, variables, and commented-out code before submitting.

### Naming

| Construct       | Convention         | Example                  |
|-----------------|--------------------|--------------------------|
| Module          | `snake_case`       | `data_loader.py`         |
| Class           | `PascalCase`       | `DataLoader`             |
| Function/method | `snake_case`       | `load_records()`         |
| Constant        | `UPPER_SNAKE_CASE` | `MAX_RETRIES = 3`        |
| Private         | leading underscore | `_internal_helper()`     |
| Type alias      | `PascalCase`       | `RecordList = list[...]` |

Beyond casing:

- **Intention-revealing:** names explain *what* and *why*, not *how*. No abbreviations or single-letter names except
  loop counters (`i`, `j`). `elapsed_time_in_days` not `d`.
- **No encodings:** no Hungarian notation, no type prefixes, no redundant context. `User.name` not `User.user_name`.
- **Pronounceable:** names must be speakable. `generation_timestamp` not `gen_ymdhms`.
- **Searchable:** no bare magic numbers or magic strings — extract into named `UPPER_SNAKE_CASE` constants.

### Clean Code

**Functions:**

- Do one thing at one level of abstraction. If you can extract a meaningful sub-function, do it.
- Aim for 0–2 parameters. More than three is a smell — consider a dataclass or value object.
- No hidden side effects: a function does exactly what its name says and nothing more.

**Classes:**

- Single Responsibility Principle: one reason to change. If you describe it with "and", split it.
- Keep classes small (~200 lines is a signal to reconsider).
- Law of Demeter: talk only to direct collaborators. Avoid chaining through object graphs.
- Tell, don't ask: tell an object to do something rather than querying its state to decide externally.

**Comments:**

- Prefer self-documenting code over comments. Comments explain *why*, never *what*.
- No commented-out code — delete it; version control preserves history.
- No redundant comments that merely restate the code.

**Constants and duplication:**

- Extract every magic number and magic string into a named constant.
- Apply DRY: if the same logic or value appears in two places, extract it.

---

## Testing

- Tests are written with [pytest](https://docs.pytest.org/) and live under `tests/unit/`, `tests/acceptance/`,
  `tests/benchmark/`, and `tests/regression/`.
- Test filenames mirror source filenames: `OTAnalytics/domain/core.py` → `tests/unit/OTAnalytics/domain/test_core.py`.
- Every bugfix must include a regression test that fails before the fix and passes after.
- Every new public function must have at least one happy-path and one edge-case test.
- Aim for ≥90% coverage on new code.
- Every test method must have a docstring that references its OpenProject issue using `#Requirement OP#<number>` or
  `#Bugfix OP#<number>`.
- Use `pytest.raises` for expected exceptions — never `try/except` in tests.
- Use `unittest.mock` as the mock library. Mock only external I/O (network, filesystem, time) — do not mock code you
  own.
- Use builders in `tests/utils/` for test data creation and fixtures from `conftest.py` where available.
- Tests must be deterministic. Do not rely on ordering, real timestamps, or network calls.

Unit tests follow the **Stage Play** structure (four named actors: `given`, `target`, `actual`, `expected`;
module-level `setup()`, `configure_*()`, and `create_target()` functions; test class at the top of the file).
See [AGENTS.md](./AGENTS.md) for the full structure and examples.

```bash
uv run pytest                                             # run all tests
uv run pytest tests/unit/                                # unit tests only
uv run pytest -k "test_bar"                              # run tests matching a name
uv run pytest --cov=OTAnalytics --cov-report=term-missing  # with coverage
```

---

## Submitting a Pull Request

Before marking a PR as ready, confirm:

- [ ] `uv run pre-commit run --all-files` — all hooks pass (formatting, linting, type checking)
- [ ] `uv run pytest` — all tests pass
- [ ] New/changed behaviour is covered by tests
- [ ] AI disclosure included in the PR description if applicable (
  see [AI-Assisted Contributions](#ai-assisted-contributions))

In the PR description:

1. Explain *what* changed and *why*.
2. Reference the OpenProject issue (e.g., `OP#142`).
3. Keep PRs focused: one logical change per PR.
4. Be responsive to review feedback.

Maintainers aim to triage new pull requests within **two weeks**. If you have not heard back after that, feel free to
ping the PR thread.

Pull requests that fail CI checks will not be merged.

All merged contributors are automatically listed in the [GitHub contributors graph](../../graphs/contributors).

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

```text
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

AI attribution in commit messages is **mandatory** whenever a commit was fully generated by or substantially
assisted by an AI tool.

For fully AI-generated commits, add a `Co-Authored-By` trailer:

```text
Co-Authored-By: Claude <noreply@anthropic.com>
```

For commits where AI assisted but a human drove the work, use an `Assisted-by` trailer:

```text
Assisted-by: GitHub Copilot
```

Claude Code adds `Co-Authored-By` trailers automatically — keep them. For other tools, add the trailer manually.
The exact format is flexible, but the attribution must be present and honest.

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

## Branch Naming

Branch names must include the OpenProject issue number:

```text
<type>/<issue_number>-<short-description>
```

Types: `task`, `bug`, `feature`, `refactor`

Examples:

```text
task/9478-add-contributing-markdown-files
bug/9461-fix-python-version-requirement-in-readme
feature/142-add-csv-export
refactor/201-simplify-loader
```

---

## Commit Message Format

```text
OP#<issue_number>: <short summary, imperative, max 72 chars>

[optional body: explain WHY, not WHAT]

[Co-Authored-By / Assisted-by footer if AI was involved — see above]
```

Every commit must reference the OpenProject issue it belongs to. If no issue exists, create one before
starting work.

Examples:

```text
OP#9478: Add CONTRIBUTING.md and AGENTS.md files

OP#87: Fix empty input raising wrong exception type
```

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md).
By participating you agree to abide by its terms. Report violations
to [team@opentrafficcam.org](mailto:team@opentrafficcam.org).

---

## Questions?

Open a [Discussion](../../discussions) or email [team@opentrafficcam.org](mailto:team@opentrafficcam.org).
We are happy to help both human and AI-assisted contributors get started.
