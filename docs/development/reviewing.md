# Reviewing Reference

Use this file when implementing or reviewing changes. It collects the detailed checklists that do not belong in passive agent context.

## Implementation Checklist

Before handing work off, confirm:
- the change satisfies the issue requirements
- edge cases are covered where relevant
- public API changes include a deprecation path when needed
- new functions are fully typed
- tests and docs were updated for the behavior change
- security-sensitive input handling is still safe
- no unnecessary performance regressions were introduced

## Reviewer Checklist

Must-block findings:
- tests are absent for new or changed behavior
- public API is broken without a deprecation path
- secrets or credentials appear in code or tests
- bare `except:` swallows errors silently
- untrusted input is passed unsafely to command execution or evaluation APIs
- a bug fix is missing a regression test

Should-flag findings:
- logic is duplicated instead of extracted
- `TODO` or `FIXME` appears without a linked issue
- `# noqa` or `# type: ignore` is unexplained
- tests assert implementation details instead of observable behavior
- a public API addition lacks a docstring

Positive signals:
- edge cases are covered with focused tests
- complex logic includes a short explanation of the underlying constraint
- deprecations are explicit and time-bounded
