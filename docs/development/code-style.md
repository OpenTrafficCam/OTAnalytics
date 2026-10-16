# Code Style Reference

Use this file for detailed implementation standards. `CONTRIBUTING.md` remains the policy source; this file expands it.

## General Rules

- Type-annotate all function signatures, including private helpers.
- Write Google-style docstrings for public modules, classes, and functions.
- Keep imports at the top of the file and sorted with `isort`.
- Do not use wildcard imports.
- Raise specific exception types and avoid bare `except:` blocks.
- Prefer `pathlib.Path` for file handling.
- Use `logging` for diagnostic output in library code.
- Remove dead code, unused imports, and commented-out code.

## Naming

| Construct | Convention | Example |
|---|---|---|
| Module | `snake_case` | `data_loader.py` |
| Class | `PascalCase` | `DataLoader` |
| Function or method | `snake_case` | `load_records()` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES = 3` |
| Private symbol | leading underscore | `_internal_helper()` |
| Type alias | `PascalCase` | `RecordList = list[...]` |

Names should be intention-revealing, pronounceable, and searchable. Avoid redundant prefixes, unclear abbreviations, and magic values embedded directly in logic.

## Functions and Classes

- Keep one level of abstraction per function.
- More than three parameters is a design smell; prefer a value object or dataclass when parameters belong together.
- Avoid hidden side effects.
- Keep classes focused on one reason to change.
- Avoid reaching through object graphs when a collaborator method would express the intent more cleanly.

## Comments and Duplication

- Prefer self-documenting code; comments should explain why, not restate what the code already says.
- Extract repeated logic or repeated magic values into named helpers or constants.
