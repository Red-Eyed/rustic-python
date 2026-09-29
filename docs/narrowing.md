# Narrowing through a predicate

[Project overview and reading path](../README.md)

A helper recognizes nonempty text in a `str | int` value. Its caller wants to strip the text after the check.

**Typical Python**

```text
def is_nonempty_text(value: str | int) -> bool:
    return isinstance(value, str) and bool(value.strip())

def normalize_name(value: str | int) -> str:
    if is_nonempty_text(value):
        return value.strip()
    raise ValueError("name must be nonempty text")
```

The checker rejects `.strip()` because a plain `bool` return does not tell it which type the predicate recognized.

**Alternative**

[Source](../examples/checker_limits.py)

```python
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
```

`TypeGuard[str]` communicates the narrowing. `normalize_name(" training ")`
returns `"training"`, and the checker accepts `.strip()` in the guarded branch.
For a single use, an inline type check may be simpler than a predicate.

The checker trusts the guard's author; it does not prove the predicate correct or
encode nonemptiness in `str`. Invalid input aborts this internal normalization.
External schema validation belongs at a [boundary](data-modeling.md).
