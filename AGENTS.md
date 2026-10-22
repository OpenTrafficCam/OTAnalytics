# AGENTS.md

> Runtime instructions for coding agents working in this repository.
> Human contributors should start with [CONTRIBUTING.md](./CONTRIBUTING.md).

## Precedence

Use this hierarchy when instructions overlap:

1. `AGENTS.md` defines agent runtime constraints and task execution rules.
2. `CONTRIBUTING.md` defines human contribution workflow and repository policy.
3. `docs/development/*.md` provides detailed reference material and examples.
If `AGENTS.md` conflicts with another documentation file, follow `AGENTS.md` for agent behavior and report the drift.

## Repo Snapshot

OTAnalytics analyzes traffic trajectories and produces counts, events, and statistics.

Important entry points:
- `OTAnalytics/__init__.py`: public API surface
- `OTAnalytics/__main__.py`: GUI entry point and CLI via `--cli`
- `OTAnalytics/plugin_cli/`: CLI implementation

## Environment

- Python `3.12` is required exactly.
- Use [`uv`](https://docs.astral.sh/uv/) for Python commands.
- Development setup:
  - Linux/macOS: `./install_dev.sh`
  - Windows: `install_dev.cmd`

## Hard Constraints For Agents

- Do not change dependency versions, CI workflows, license headers, or unrelated files without explicit human instruction.
- Do not push directly to `main` or `develop`.
- Before creating a branch, suggest a name using `<type>/<issue_number>-<short-description>` and wait for confirmation.
- Every commit message must start with `OP#<issue_number>:`.
- Include honest AI attribution when AI materially contributed to a commit.
- Prefer repository sources over model memory when repository docs or code answer the question.

## Change-Type Verification

Use the smallest verification set that honestly matches the change.

| Change type | Minimum verification |
|---|---|
| Docs-only | Check changed Markdown for accuracy, links, and command examples |
| Python change in one area | Run focused tests for the affected area during development |
| Cross-cutting or risky Python change | Run focused tests while iterating and full verification before handoff |

Before handing off Python code changes or opening a PR, run both:

```bash
uv run pre-commit run --all-files
uv run pytest
```

If you intentionally skip a command because the change is docs-only or blocked by environment issues, say so explicitly.

## Retrieval Pointers

Use these files instead of keeping long guidance in passive context:

- [CONTRIBUTING.md](./CONTRIBUTING.md): contributor workflow, PR expectations, AI disclosure
- [docs/development/README.md](./docs/development/README.md): index of detailed development references
- [docs/development/code-style.md](./docs/development/code-style.md): coding standards and naming rules
- [docs/development/testing.md](./docs/development/testing.md): test expectations and Stage Play structure
- [docs/development/reviewing.md](./docs/development/reviewing.md): implementation and review checklists

## Agent Notes

- Keep changes scoped to the request.
- Fix contradictions in docs when you see them instead of copying them into new files.
- Prefer linking to detailed guidance over duplicating it.
