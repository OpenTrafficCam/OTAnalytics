# AGENTS.md

> Instructions for AI coding agents (Claude Code, Codex, Copilot, Cursor, Gemini CLI, Amp, etc.).
> Human contributors: see [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Project Overview

OTAnalytics is a core module of the [OpenTrafficCam framework](https://github.com/OpenTrafficCam) that performs
traffic analysis on trajectories of road users tracked by OTVision or other tools. It processes trajectory data,
defines and analyzes traffic flows, counts vehicles assigned to flows, and generates event lists and statistics.

```
OTAnalytics/          # Main package
  __init__.py         # Public API surface
  __main__.py         # Entry point
  domain/             # Core domain logic (entities, use cases)
  application/        # Application layer (orchestration)
  adapter_ui/         # UI adapters
  adapter_intersect/  # Intersection adapters
  adapter_visualization/
  plugin_*/           # Plugin implementations (parser, datastore, UI, CLI, etc.)
  helpers/            # Shared utilities
tests/
  unit/               # Unit tests
  acceptance/         # Acceptance / end-to-end tests (Playwright)
  benchmark/          # Performance benchmarks
  regression/         # Regression tests
docs/
```

Key entry points: `OTAnalytics/__init__.py` (public API), `OTAnalytics/__main__.py` (GUI, or CLI
with `--cli` parameter), `OTAnalytics/plugin_cli/` (CLI implementation).

---

## Environment Setup

Requires **Python 3.12** (exact) and [uv](https://docs.astral.sh/uv/).

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

Do **not** commit changes to `.venv/`, `*.egg-info/`, `__pycache__/`, or `dist/`.

---

## Before Every Commit — Mandatory Checklist

Run these two commands before every commit. Both must pass with zero errors before you open a PR.

```bash
# 1. Run all linters and formatters (flake8, black, isort, mypy, etc.)
uv run pre-commit run --all-files

# 2. Full test suite
uv run pytest
```

`uv run pre-commit run --all-files` runs all configured hooks (formatting, linting, type checking) in the correct
order on the entire codebase. If a hook auto-fixes files, it will report a failure on the first run — re-run it
once to confirm everything is clean.

Do **not** suppress hook errors with `# noqa`, `# type: ignore`, or `SKIP=` env vars unless there is a documented
reason in a comment on the same line.

---

## Running Tests

```bash
uv run pytest                                      # all tests
uv run pytest tests/unit/                          # unit tests only
uv run pytest tests/acceptance/                    # acceptance tests only
uv run pytest tests/benchmark/                     # benchmarks only
uv run pytest tests/regression/                    # regression tests only
uv run pytest -k "test_name_fragment"              # filter by name
uv run pytest --cov=OTAnalytics --cov-report=term-missing  # with coverage report
uv run pytest -x                                   # stop on first failure
uv run pytest --tb=short                           # compact tracebacks
```

**Coverage target:** aim for ≥90% on new code. Check the report before submitting.

---

## Code Conventions

### General

- Type-annotate all function signatures (parameters + return type), including private helpers.
- Google-style docstrings on all public functions, classes, and modules.
- No wildcard imports (`from foo import *`).
- **All imports must be at the top of the file**, grouped and sorted by `isort`. Never use inline or conditional
  imports except for circular-import resolution, and document that case with a comment.
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

Sort order (enforced by `isort --profile black`):
1. Standard library
2. Third-party packages
3. Local (`from OTAnalytics import ...`)

### Line length

Max 88 characters (Black default). Strings and comments may exceed this only when breaking them would reduce
readability.

---

## Testing Conventions

- Every bug fix **must** add a regression test that fails before the fix and passes after.
- Every new public function **must** have at least one happy-path and one edge-case test.
- Test file names mirror source file names: `OTAnalytics/domain/core.py` → `tests/unit/OTAnalytics/domain/test_core.py`.
- Bug fix tests must include the OpenProject issue number in their docstring:
  ```python
  def test_empty_input_raises_value_error():
      """Verify that empty input raises ValueError.

      This test was written to fix OP#87.
      """
  ```
- Use `pytest.raises` for expected exceptions — never `try/except` in tests.
- Use `unittest.mock` as the mock library. Do not mock things you own; mock only external I/O (network,
  filesystem, time).
- Use builders in `tests/utils/` for test data creation; use fixtures from `conftest.py` where available.
- Tests must be deterministic. Do not rely on ordering, real timestamps, or network calls.

### Stage Play Test Structure

Unit tests follow the **"Every Unit Test Is a Stage Play"** pattern
(see [Part I](https://schneide.blog/2024/08/26/every-unit-test-is-a-stage-play-part-i/),
[Part II](https://schneide.blog/2024/09/02/every-unit-test-is-a-stage-play-part-ii/),
[Part III](https://schneide.blog/2024/09/30/every-unit-test-is-a-stage-play-part-iii/)).
Every test tells a short, readable story using four named actors:

| Actor | Role |
|---|---|
| `given` | Preconditions, inputs, mocks, and collaborators (instance of a `Given` dataclass) |
| `target` | The object/code under test |
| `actual` | The value returned by calling `target` |
| `expected` | The reference value for the assertion (when needed) |

**File structure** — module-level functions and the `Given` dataclass appear *below* the test class,
keeping the test methods at the top as the entry point for the reader:

```python
from dataclasses import dataclass
from unittest.mock import Mock

from OTAnalytics.domain.foo import FooRepository
from OTAnalytics.application.use_cases.foo import DoFoo


class TestDoFoo:
    def test_happy_path(self) -> None:
        given = configure_foo_exists(setup())
        target = create_target(given)

        actual = target.execute()

        assert actual == given.expected_result
        given.repository.find.assert_called_once()

    def test_bug_op_87(self) -> None:
        """Verify that empty input raises ValueError.

        This test was written to fix OP#87.
        """
        given = setup()
        target = create_target(given)

        with pytest.raises(ValueError):
            target.execute()


@dataclass
class Given:
    repository: Mock
    expected_result: list[Mock]


def setup() -> Given:
    repository = Mock(spec=FooRepository)
    expected_result = [Mock(), Mock()]
    return Given(repository=repository, expected_result=expected_result)


def configure_foo_exists(given: Given) -> Given:
    given.repository.find.return_value = given.expected_result
    return given


def create_target(given: Given) -> DoFoo:
    return DoFoo(given.repository)
```

**Rules:**
- `Given` is a `@dataclass` holding all mocks and preconditions for the scenario.
- `setup()` is a module-level function that creates the base `Given` with sensible defaults.
- `configure_*()` functions are module-level and adjust `Given` for a specific scenario. They accept
  and return a `Given` so they can be chained: `configure_b(configure_a(setup()))`.
- `create_target()` is a module-level function that constructs the class under test from `given`.
- Test method names are snake_case and describe the behaviour, not the implementation:
  `test_returns_empty_list_when_repository_is_empty` not `test_execute`.
- Keep the test method body short — extract any complex setup into `configure_*()` helpers.
- Do not use literal `# Given / # When / # Then` comments; the structure is expressed through naming.

---

## Mandatory Reviewer Agent Pass

After completing an implementation, **before marking a PR as ready**, a reviewer agent must perform a full code
review of the diff against this guide. This is not optional.

The reviewer agent must work through every item in the [What a Reviewer Agent Should Check](#what-a-reviewer-agent-should-check)
section below and report:
- All **must-block** findings (each must be resolved before the PR proceeds)
- All **should-flag** findings (each must be acknowledged or addressed)
- A short summary confirming which coding guidelines were verified

The implementing agent must not self-certify the review. Reviewer and implementer should be separate agent
invocations or clearly separated reasoning steps.

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
- [ ] Is the change backwards-compatible with Python 3.12?

### Types
- [ ] Do all new functions have complete type annotations?
- [ ] Does `uv run mypy OTAnalytics tests` pass with zero new errors?

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
- `mypy` or `flake8` errors exist anywhere in the diff.
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
<type>/<issue_number>-<short-description>
```

Types: `task`, `bug`, `feature`, `refactor`

Examples:
```
task/9478-add-contributing-markdown-files
bug/9461-fix-python-version-requirement-in-readme
feature/142-add-csv-export
refactor/201-simplify-loader
```

When starting work on an issue, **always suggest a branch name** to the user before creating it and wait for
confirmation.

---

## Commit Message Format

```
OP#<issue_number>: <short summary, imperative, max 72 chars>

[optional body: explain WHY, not WHAT]

Co-Authored-By: Claude <noreply@anthropic.com>
```

**The `OP#<issue_number>` prefix is mandatory.** Every commit must reference the OpenProject issue it belongs to.
If no issue exists, create one before starting work.

**AI attribution is mandatory** whenever a commit was fully generated by or substantially assisted by an AI tool:

- Fully AI-generated: use `Co-Authored-By: Claude <noreply@anthropic.com>` (or the relevant tool)
- AI-assisted: use `Assisted-by: GitHub Copilot` (or the relevant tool)

Claude Code adds `Co-Authored-By` automatically — keep it. For other tools, add the trailer manually.

Examples:

```
OP#9478: Add CONTRIBUTING.md and AGENTS.md files

Co-Authored-By: Claude <noreply@anthropic.com>
```

```
OP#87: Fix empty input raising wrong exception type

Assisted-by: GitHub Copilot
```

---

## Pull Request Checklist

Before marking a PR as ready for review, confirm:

- [ ] `uv run pre-commit run --all-files` — all hooks pass
- [ ] `uv run pytest` — all tests pass
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
