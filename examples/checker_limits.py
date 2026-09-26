"""Express supported narrowing without casts or project-wide suppressions."""

from typing import TypeGuard


def is_nonempty_text(value: str | int) -> TypeGuard[str]:
    """Identify strings with visible content; promise only str to the checker."""
    return isinstance(value, str) and bool(value.strip())


def normalize_name(value: str | int) -> str:
    """Strip a validated name; raise ValueError for other values."""
    if is_nonempty_text(value):
        return value.strip()
    raise ValueError("name must be nonempty text")


name = normalize_name(" training ")
# rejected[bad-assignment]: count: int = name
