# List the available recipes
default:
    @just --list

# Install git hooks, including pre-push (not installed by plain `pre-commit install`)
install-hooks:
    uv run --group dev pre-commit install --hook-type pre-commit --hook-type pre-push

test:
    uv run --group dev pytest

test-unit:
    uv run --group dev pytest tests/unit

lint:
    uv run --group dev ruff check

fix:
    uv run --group dev ruff check --fix

format:
    uv run --group dev ruff format

typecheck:
    uv run --group dev mypy OTAnalytics tests --config-file pyproject.toml
