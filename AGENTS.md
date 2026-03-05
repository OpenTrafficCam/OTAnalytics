# AGENTS.md

> Instructions for AI coding agents (Claude Code, Codex, Copilot, Cursor, Gemini CLI, Amp, etc.).
> Human contributors: see [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Project Overview

<!-- TODO: 2–3 sentences. What does this library do? Who uses it? What is the core abstraction? -->

```
src/
  mypackage/
    __init__.py       # Public API surface
    core.py           # Core logic
    ...
tests/
  unit/
  integration/
docs/
```

Key entry points: `src/mypackage/__init__.py` (public API), `src/mypackage/cli.py` (CLI if present).

---

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Python version requirement: `>=3.11` (see `pyproject.toml`).

Do **not** commit changes to `.venv/`, `*.egg-info/`, `__pycache__/`, or `dist/`.

---

## Before Every Commit — Mandatory Checklist

Run these two commands before every commit. Both must pass with zero errors before you open a PR.

```bash
# 1. Run all linters and formatters (ruff, mypy, etc.)
pre-commit run --all-files

# 2. Full test suite
pytest
```

`pre-commit run --all-files` runs all configured hooks (formatting, linting, type checking) in the correct order on the entire codebase. If a hook auto-fixes files, it will report a failure on the first run — re-run it once to confirm everything is clean.

Do **not** suppress hook errors with `# noqa`, `# type: ignore`, or `SKIP=` env vars unless there is a documented reason in a comment on the same line.

---

## Running Tests

```bash
pytest                                         # all tests
pytest tests/unit/                             # unit tests only
pytest tests/integration/                      # integration tests only
pytest -k "test_name_fragment"                 # filter by name
pytest --cov=src --cov-report=term-missing     # with coverage report
pytest -x                                      # stop on first failure
pytest --tb=short                              # compact tracebacks
```

**Coverage target:** aim for ≥90% on new code. Check the report before submitting.

---

## Code Conventions

### General

- Type-annotate all function signatures (parameters + return type), including private helpers.
- Google-style docstrings on all public functions, classes, and modules.
- No wildcard imports (`from foo import *`).
- **All imports must be at the top of the file**, grouped and sorted by `pre-commit` hooks. Never use inline or conditional imports except for circular-import resolution, and document that case with a comment.
- Raise specific exception types; never bare `except:` or `except Exception:` without re-raising or logging.
- Prefer `pathlib.Path` over `os.path` for file operations.
- Use `logging` (not `print`) for any diagnostic output in library code.

### Naming

| Construct        | Convention              | Example                  |
|------------------|-------------------------|--------------------------|
| Module           | `snake_case`            | `data_loader.py`         |
| Class            | `PascalCase`            | `DataLoader`             |
| Function/method  | `snake_case`            | `load_records()`         |
| Constant         | `UPPER_SNAKE_CASE`      | `MAX_RETRIES = 3`        |
| Private          | leading underscore      | `_internal_helper()`     |
| Type alias       | `PascalCase`            | `RecordList = list[...]` |

### Imports

Sort order (enforced by ruff):
1. Standard library
2. Third-party packages
3. Local (`from mypackage import ...`)

### Line length

Max 88 characters (ruff default). Strings and comments may exceed this only when breaking them would reduce readability.

---

## Testing Conventions

- Every bug fix **must** add a regression test that fails before the fix and passes after.
- Every new public function **must** have at least one happy-path and one edge-case test.
- Test file names mirror source file names: `src/mypackage/core.py` → `tests/unit/test_core.py`.
- Bug fix tests must include the OpenProject issue number in their docstring:
  ```python
  def test_empty_input_raises_value_error():
      """Verify that empty input raises ValueError.

      This test was written to fix OP#87.
      """
  ```
- Use `pytest.raises` for expected exceptions — never `try/except` in tests.
- Do not mock things you own; mock only external I/O (network, filesystem, time).
- Tests must be deterministic. Do not rely on ordering, real timestamps, or network calls.

---

## Mandatory Reviewer Agent Pass

After completing an implementation, **before marking a PR as ready**, a reviewer agent must perform a full code review of the diff against this guide. This is not optional.

The reviewer agent must work through every item in the [What a Reviewer Agent Should Check](#what-a-reviewer-agent-should-check) section below and report:
- All **must-block** findings (each must be resolved before the PR proceeds)
- All **should-flag** findings (each must be acknowledged or addressed)
- A short summary confirming which coding guidelines were verified

The implementing agent must not self-certify the review. Reviewer and implementer should be separate agent invocations or clearly separated reasoning steps.

---

## What to Check When Implementing a Change

Work through this list before considering an implementation complete.

### Correctness
- [ ] Does the change fully satisfy the issue's acceptance criteria?
- [ ] Are all edge cases handled (empty input, `None`, zero, very large values, Unicode)?
- [ ] Does error handling preserve useful context (error messages, original exceptions via `raise ... from`)?
- [ ] Are any assumptions about input documented via assertions or docstrings?

### API & Compatibility
- [ ] Does the change preserve the existing public API? If not, is a deprecation warning added?
- [ ] Are new public symbols exported in `__init__.py` if appropriate?
- [ ] Is the change backwards-compatible with the Python versions listed in `pyproject.toml`?

### Types
- [ ] Do all new functions have complete type annotations?
- [ ] Does `mypy .` pass with zero new errors?

### Tests
- [ ] Do all existing tests still pass?
- [ ] Are new tests added for the changed behaviour?
- [ ] Is test coverage maintained or improved?

### Documentation
- [ ] Do new/changed functions have accurate docstrings?
- [ ] Does the changelog (`CHANGELOG.md`) have an entry under `[Unreleased]`?
- [ ] If the public API changed, is `docs/` updated?

### Security
- [ ] Does the change handle untrusted input safely (no shell injection, path traversal, unsafe deserialization)?
- [ ] Are secrets, tokens, or credentials never hardcoded or logged?
- [ ] Are new dependencies pinned/vetted? Prefer stdlib or already-used packages.

### Performance
- [ ] Does the change introduce any O(n²) or worse operations on unbounded input?
- [ ] Are file handles, database connections, and network sessions closed properly (use `with` blocks)?

---

## What a Reviewer Agent Should Check

If you are acting as a **code reviewer** rather than an implementer, verify the following for every PR diff.

### Must-block (do not approve if any of these fail)

- Tests are absent for new or changed behaviour.
- `mypy` or `ruff` errors exist anywhere in the diff.
- Public API is broken without a deprecation path.
- Secrets, tokens, or credentials appear in code or tests.
- Bare `except:` swallows errors silently.
- Untrusted input is passed to `subprocess`, `eval`, `exec`, or `os.system`.
- New heavyweight dependency added without justification.
- A regression test is missing for a bug fix.

### Should-flag (leave a comment, but may still approve)

- Function is longer than ~50 lines without a clear reason.
- Logic is duplicated instead of extracted into a helper.
- A `TODO` or `FIXME` is left without a linked issue.
- `# type: ignore` or `# noqa` is used without explanation.
- A test asserts on implementation details rather than observable behaviour.
- Log messages expose sensitive data (user IDs, emails, internal paths).
- A docstring is missing on a public function introduced in this PR.

### Positive signals (acknowledge these)

- Edge cases are covered with parametrized tests.
- Complex logic has an explanatory comment linking to the relevant issue or spec.
- Deprecation is handled cleanly with a `DeprecationWarning` and a target version.

---

## Branch Naming

Branch names must include the OpenProject issue number:

```
<type>/OP<issue_number>-<short-description>
```

Examples:
```
feat/OP142-add-csv-export
fix/OP87-handle-empty-input
refactor/OP201-simplify-loader
```

When starting work on an issue, **always suggest a branch name** to the user before creating it and wait for confirmation.

---

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary, imperative, max 72 chars>

[optional body: explain WHY, not WHAT]

OP#<issue_number>
[optional additional footers]
Co-Authored-By: Claude <claude@anthropic.com>
Assisted-by: GitHub Copilot
```

Types: `feat` · `fix` · `docs` · `refactor` · `test` · `chore` · `ci` · `perf`

Breaking changes: append `!` after type, e.g. `feat!: rename load() to load_records()`.

**The `OP#<issue_number>` footer is mandatory.** Every commit must reference the OpenProject issue it belongs to. If no issue exists, create one before starting work. Example: `OP#142`.

---

## Pull Request Checklist

Before marking a PR as ready for review, confirm:

- [ ] `pre-commit run --all-files` — all hooks pass
- [ ] `pytest` — all tests pass
- [ ] New/changed behaviour is covered by tests
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] AI disclosure included in PR description if applicable (see CONTRIBUTING.md)

---

## Out of Scope for Agents

Do **not** do the following without explicit human instruction:

- Bump dependency versions in `pyproject.toml` or `requirements*.txt`
- Modify `CHANGELOG.md` sections other than `[Unreleased]`
- Change CI/CD pipeline files (`.github/workflows/`)
- Alter license or copyright headers
- Refactor files unrelated to the current task
- Push directly to `main` or `develop` — always use a branch + PR
