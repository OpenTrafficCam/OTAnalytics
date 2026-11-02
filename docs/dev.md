# Development

## Setup

This project manages its dependencies with [uv](https://docs.astral.sh/uv/). Make
sure `uv` is installed, then run

```bash
./install_dev.sh   # Windows: install_dev.cmd
```

It installs the project with the `dev` dependency group, the Playwright browsers and
the git hooks. To do the steps by hand:

```bash
uv sync --group dev
uv run playwright install
just install-hooks
```

`just install-hooks` installs both the `pre-commit` and the `pre-push` git hook. Plain
`pre-commit install` only installs the `pre-commit` hook and silently skips hooks
configured with `stages: [pre-push]`, e.g. `super-linter`.

See [dependency_management.md](./dependency_management.md) for how to add or update
dependencies.

## Tests

```bash
just test       # all tests
just test-unit  # unit tests only
```

The acceptance and benchmark tests drive a browser, so they need
`uv run playwright install` first.

## Code quality

| Recipe           | What it does                                                     |
| ---------------- | ---------------------------------------------------------------- |
| `just lint`      | `ruff check`: flake8-equivalent rules (E, F, W) and import order |
| `just fix`       | `ruff check --fix`                                               |
| `just format`    | `ruff format`                                                    |
| `just typecheck` | `mypy` over `OTAnalytics` and `tests`                            |
| `just super-lint`| super-linter in Docker, the same config as CI                    |

The `pre-commit` hooks run ruff and mypy. The `pre-push` hook runs super-linter in
Docker, which also covers YAML (yamllint), shell scripts (shellcheck, shfmt), GitHub
Actions and more. The config shared by CI, the hook and `just super-lint` is in
[`.github/super-linter.env`](../.github/super-linter.env). Local runs also apply the
fixes from [`.github/super-linter-fix.env`](../.github/super-linter-fix.env), so check
`git status` afterwards.

When you bump the super-linter version, change it in the `pre-push` hook, the
`justfile` and the CI workflow `.github/workflows/linter.yml`.

## just

The `justfile` lists the available recipes, run `just` to see them. `super-lint` needs
the `docker` CLI. If you use a compatible runtime like `podman`, make sure you have an
alias or symlink in place.
