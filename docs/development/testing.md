# Testing Reference

Use this file for test structure, examples, and detailed expectations.

## Baseline Expectations

- Every bug fix adds a regression test.
- Every new public function gets at least one happy-path and one edge-case test.
- Test files should mirror the production module path.
- Use `pytest.raises` for expected exceptions.
- Mock only external I/O such as filesystem, network, or time.
- Tests must be deterministic.

## Stage Play Structure

Unit tests in this repository follow the Stage Play pattern.

Actors:
- `given`: inputs, collaborators, mocks, and preconditions
- `target`: object or callable under test
- `actual`: observed result from the single act
- `expected`: reference value when needed

Recommended module structure:
- keep the test class near the top of the file
- define the `Given` dataclass below the test class
- provide module-level `setup()`, `configure_*()`, and `create_target()` helpers

Story rules:
- keep one act per test
- keep one logical assertion cluster per test
- use behavior-focused test names
- give every test a docstring with `#Requirement OP#<number>` or `#Bugfix OP#<number>`

## Example Skeleton

```python
from dataclasses import dataclass
from unittest.mock import Mock


class TestUseCase:
    def test_returns_expected_value(self) -> None:
        """Verify that the use case returns the expected value.

        #Requirement OP#142
        """
        given = setup()
        target = create_target(given)

        actual = target.execute()

        assert actual == given.expected_value


@dataclass
class Given:
    dependency: Mock
    expected_value: str


def setup() -> Given:
    return Given(dependency=Mock(), expected_value="value")


def create_target(given: Given):
    return SomeUseCase(given.dependency)
```

## Useful Commands

```bash
uv run pytest
uv run pytest tests/unit/
uv run pytest tests/acceptance/
uv run pytest tests/benchmark/
uv run pytest tests/regression/
uv run pytest -k "test_name_fragment"
uv run pytest --cov=OTAnalytics --cov-report=term-missing
```
