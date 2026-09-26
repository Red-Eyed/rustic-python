"""Express supported narrowing without casts or project-wide suppressions."""

from collections.abc import Mapping
from typing import TypeGuard


def is_nonempty_text(value: object) -> TypeGuard[str]:
    """Identify strings with visible content; promise only str to the checker."""
    return isinstance(value, str) and bool(value.strip())


def normalize_name(value: object) -> str:
    """Strip a validated name; raise ValueError for other values."""
    if is_nonempty_text(value):
        return value.strip()
    raise ValueError("name must be nonempty text")


def record_name(payload: object) -> str:
    """Read a text name from a mapping; reject other structures with ValueError."""
    # Pyrefly 1.3.1 needs explicit Mapping narrowing before this pattern.
    # tests/test_guide.py reproduces the limitation for review during upgrades.
    if not isinstance(payload, Mapping):
        raise ValueError("expected a mapping")
    match payload:
        case {"name": str(name)}:
            return normalize_name(name)
    raise ValueError("expected a text name field")


name = record_name({"name": " training "})
# rejected[bad-assignment]: count: int = name
