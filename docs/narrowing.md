# Narrowing through a predicate

[Project overview and reading path](../README.md)

A helper recognizes nonempty text in a `str | int` value. Its caller wants to strip the text after the check.

**Typical Python**

```python,ignore
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

from dataclasses import dataclass
from typing import TypeAlias, TypeGuard, assert_never, final


def is_nonempty_text(value: str | int) -> TypeGuard[str]:
    """Identify strings with visible content; promise only str to the checker."""
    return isinstance(value, str) and bool(value.strip())


@final
@dataclass(frozen=True, slots=True)
class InvalidName:
    """Explain why a value cannot be used as a name."""

    value: str | int


NameResult: TypeAlias = str | InvalidName


def normalize_name(value: str | int) -> NameResult:
    """Strip visible text or return a typed rejection."""
    if is_nonempty_text(value):
        return value.strip()
    return InvalidName(value)


outcome = normalize_name(" training ")
match outcome:
    case str() as name:
        pass
    case InvalidName():
        pass
    case _:
        assert_never(outcome)
# rejected[missing-attribute]: name = outcome.strip()
```

`TypeGuard[str]` communicates the narrowing. `normalize_name(" training ")`
returns `"training"`, and the checker accepts `.strip()` in the guarded branch.
The return type also forces callers to distinguish `InvalidName` before calling
string methods. For a single use, an inline type check may be simpler.

The checker trusts the guard's author; it does not prove the predicate correct or
encode nonemptiness in `str`. Invalid input returns `InvalidName`; external schema
validation belongs at a [boundary](data-modeling.md).
