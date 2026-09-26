# Errors and absence

[Project overview and reading path](../README.md)

## Make expected failures explicit

**Mistake:** malformed labels are represented by `-1`, an empty dictionary, or an
exception that disappears from the function signature.

Use a result union when failure is an expected outcome the caller should inspect.
Keep exceptions for failures whose propagation is the chosen API contract.

A simple validation helper may raise `ValueError` without introducing a result
hierarchy. Choose an explicit outcome when callers need to route or collect failures;
see [acceptable simplifications](practical-choices.md#acceptable-simplifications-and-when-to-stop-simplifying).

[Source](../examples/explicit_results.py)

```python
"""Parse labels with an explicit, typed failure outcome."""

from dataclasses import dataclass
from typing import Annotated, Generic, TypeAlias, TypeVar, assert_never, final

from pydantic import Field, TypeAdapter, ValidationError

T = TypeVar("T")
E = TypeVar("E")
LABEL = TypeAdapter[int](Annotated[int, Field(ge=0)])


@final
@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Carry the successful value of an operation."""

    value: T


@final
@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Carry an expected failure without a success value."""

    error: E


@dataclass(frozen=True, slots=True)
class InvalidLabel:
    """Preserve the rejected input and the reason it was rejected."""

    raw: str
    reason: str


Result: TypeAlias = Ok[T] | Err[E]


def parse_label(raw: str) -> Result[int, InvalidLabel]:
    """Parse a nonnegative label; return Err for malformed or negative input."""
    try:
        label = LABEL.validate_python(raw)
    except ValidationError:
        return Err(InvalidLabel(raw, "not a nonnegative integer"))
    return Ok(label)


def describe_label(result: Result[int, InvalidLabel]) -> str:
    """Describe both outcomes without discarding the failure reason."""
    match result:
        case Ok(value=label):
            return f"class {label}"
        case Err(error=error):
            return f"rejected {error.raw!r}: {error.reason}"
        case _:
            assert_never(result)


outcome = parse_label("7")
description = describe_label(outcome)
# rejected[bad-assignment]: label: int = outcome
# rejected[missing-attribute]: label = outcome.value
```

**Static guarantee:** the caller cannot use the union as an `int` or access `.value`
before narrowing away `Err`.

**Runtime obligation:** Python has no Rust-style `must_use` guarantee here. A caller
can discard the result entirely, and the type does not prove that a function never
raises. This parser also does not know the dataset's class count. Its caller must
validate that a nonnegative label is within that dataset's range.

## Preserve the reason a value is absent

**Mistake:** precision with no predicted positives is recorded as `0.0`. That makes
"undefined" indistinguishable from "all positive predictions were wrong."

Python's `float | None` is a checked union, not an untyped null pointer. But `None`
does not explain absence. Use a reason-carrying variant when the distinction matters.

[Source](../examples/reasoned_absence.py)

```python
"""Keep an undefined metric distinct from a real zero."""

from dataclasses import dataclass
from typing import assert_never, final


@final
@dataclass(frozen=True, slots=True)
class Absent:
    """Explain why a domain value is unavailable."""

    reason: str


def precision(true_positives: int, false_positives: int) -> float | Absent:
    """Compute precision; reject negative counts and explain a zero denominator."""
    if true_positives < 0 or false_positives < 0:
        raise ValueError("counts must be nonnegative")
    predicted_positives = true_positives + false_positives
    if predicted_positives == 0:
        return Absent("no predicted positives")
    return true_positives / predicted_positives


def format_precision(value: float | Absent) -> str:
    """Render a metric without silently assigning a numeric value to absence."""
    match value:
        case Absent(reason=reason):
            return f"undefined: {reason}"
        case int(score) | float(score):
            return f"{score:.3f}"
        case _:
            assert_never(value)


undefined = precision(0, 0)
zero = precision(0, 12)
# rejected[bad-assignment]: score: float = undefined
```

**Static guarantee:** consumers must narrow the union before treating the result as
a float. Keep required identity fields required instead of making every field absent.

**Runtime obligation:** counts must represent the same evaluation population. Avoid
truthiness checks: a real `0.0` is falsy. If absence reasons drive control flow,
promote them to an enum or separate variants instead of matching free-form strings.
