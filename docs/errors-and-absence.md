# Result and match

[Project overview and reading path](../README.md)

An importer reads integer labels. A malformed row should be reported while valid rows continue. The caller needs both the parsed value and a way to recognize rejection.

**Typical Python**

```text
def parse_label(raw: str) -> int:
    return int(raw)

labels = [parse_label(raw) for raw in ("7", "cat", "2")]
```

The annotation exposes only success. `"cat"` raises `ValueError` at runtime and interrupts the import. Returning `-1` instead would still look like a valid integer to the checker.

**Alternative**

[Source](../examples/explicit_results.py)

```python
"""Parse labels with an explicit, typed failure outcome."""

from dataclasses import dataclass
from typing import Annotated, Generic, TypeAlias, TypeVar, assert_never, final

from pydantic import Field, TypeAdapter, ValidationError

T = TypeVar("T")
E = TypeVar("E")


@final
@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Carry a successful value; no error field or unchecked extraction method."""

    value: T


@final
@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Carry an expected failure without discarding its typed details."""

    error: E


Result: TypeAlias = Ok[T] | Err[E]

LABEL = TypeAdapter[int](Annotated[int, Field(ge=0)])


@dataclass(frozen=True, slots=True)
class InvalidLabel:
    """Preserve the rejected input and the reason it was rejected."""

    raw: str
    reason: str


def parse_label(raw: str) -> Result[int, InvalidLabel]:
    """Parse a nonnegative label; return Err for malformed or negative input."""
    try:
        label = LABEL.validate_python(raw)
    except ValidationError:
        return Err(InvalidLabel(raw, "not a nonnegative integer"))
    return Ok(label)


def label_name(label: int) -> str:
    """Render a parsed class index without changing its meaning."""
    return f"class {label}"


def describe_label(result: Result[int, InvalidLabel]) -> str:
    """Describe both outcomes without discarding the failure reason."""
    match result:
        case Ok(value=label):
            return label_name(label)
        case Err(error=error):
            return f"rejected {error.raw!r}: {error.reason}"
        case _:
            assert_never(result)


outcome = parse_label("7")
description = describe_label(outcome)
# rejected[bad-assignment]: label: int = outcome
# rejected[bad-assignment]: wrong: Result[str, InvalidLabel] = outcome
# rejected[bad-assignment]: wrong_error: Result[int, str] = outcome
# rejected[missing-attribute]: label = outcome.value
# rejected[missing-attribute]: error = outcome.error
# rejected[missing-attribute]: unchecked = outcome.unwrap()
```

`parse_label("7")` returns `Ok(7)`; `parse_label("cat")` returns an
`Err` carrying the rejected input and reason. `describe_label` uses `match` to
consume either outcome. It produces `"class 7"` or a rejection message.

**Result and match work together:** the union exposes failure, matching narrows
the payload, and `assert_never` checks that no variant is forgotten. Assigning
the result directly to `int`, or reading `.value` before narrowing, is rejected.
A `Raises:` docstring cannot provide that checked contract.

Use typed outcomes for supported retry, fallback, correction, or record rejection.
Use exceptions when the operation has no recovery path and must unwind. Translate
specific recoverable library exceptions at the boundary; do not disguise bugs.
Python can still raise unexpected exceptions, and a caller can discard the whole
result. No return annotation proves exception freedom.

The parser accepts nonnegative integer-valued text, including `"7.0"`; it does
not know the dataset's class count. The two frozen variants freeze their own
fields, not mutable payloads. Keep this small union rather than adding a result
framework or unchecked unwrap methods.
