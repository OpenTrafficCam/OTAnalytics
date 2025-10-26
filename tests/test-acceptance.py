"""
Shim module to support the acceptance workflow path ./tests/test-acceptance.py.

The actual acceptance tests live in tests/test_acceptance.py (underscore).
We execute that file in this module's global namespace so that pytest can
collect the tests without changing the workflow configuration.
"""

from pathlib import Path

# Determine the real test file with underscore name
_real = Path(__file__).with_name("test_acceptance.py")

if not _real.exists():
    raise FileNotFoundError(f"Expected acceptance test at {_real} not found")

# Execute the real test file in this module's globals so pytest sees the tests
_globals = globals()
with open(_real, "rb") as _f:
    _code = compile(_f.read(), str(_real), "exec")
    exec(_code, _globals, _globals)
