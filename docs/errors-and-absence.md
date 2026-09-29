# Errors and absence

[Project overview and reading path](../README.md)

## Make expected failures explicit

**Mistake:** a caller must distinguish accepted and rejected labels, but the
parser returns `-1` or an empty dictionary that hides the rejection reason.

Use typed outcomes when the caller can retry, choose a fallback, correct input,
or reject a record and continue. Use exceptions when the operation has no
supported recovery path and must unwind. Recovery is relative to that operation;
an outer boundary may still clean up or report an exception.

A `Raises:` docstring does not expose a recoverable failure to the type checker.
`Result[Config, ReadError | InvalidConfig]` does: callers must narrow the outcome
before using the configuration. A caller can still discard the entire result,
and Python's type system does not prove that unexpected exceptions cannot escape.

Translate specific recoverable library exceptions at the boundary. Do not turn
programming defects into ordinary rejected records. The deliberately broad SDK
adapter has a [separate policy](third-party-boundaries.md#why-catch-exception-here).

## Choose a representation for the caller's decisions

Use domain alternatives such as `AcceptedRow | RejectedRow` when their names and
fields describe the decisions best. For generic success/failure, use
`Result[T, E] = Ok[T] | Err[E]`: two frozen records, with a `value` or an `error`.
Handle them with `match` and `assert_never`, without a shared result base class,
third-party result package, or unchecked unwrap.

The parser below accepts `"7"` as `Ok(7)` and rejects `"cat"` as
`Err(InvalidLabel(raw="cat", reason="not a nonnegative integer"))`. The caller can
report the rejected input and continue. `Generic[T]` supplies Python 3.11 type
parameters; it adds no shared result behavior.

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

**Static guarantee verified here:** callers cannot assign the result container
to an `int`, change its declared success or error type, or access `.value` or
`.error` before narrowing to the appropriate variant. No `.unwrap()` method exists.
Matching `Ok(value=label)` yields an `int`; matching `Err(error=error)` yields an
`InvalidLabel`. `assert_never` checks exhaustive handling of the closed union;
the regression suite verifies that adding another alternative breaks the handler.

**Runtime obligation:** Python has no Rust-style `must_use` guarantee here. A caller
can discard the result entirely, and the type does not prove that a function never
raises. This parser also does not know the dataset's class count. Its caller must
validate that a nonnegative label is within that dataset's range. Frozen variants
prevent normal field reassignment but do not freeze mutable payloads or enforce
ownership. Annotations do not validate dynamically supplied constructor arguments.

## Know where a failure happened

A result retains only the error information supplied to it:

| Payload | Useful for | Limit |
| --- | --- | --- |
| `Err(InvalidLabel(raw="cat", reason="not a nonnegative integer"))` | Reporting bad input | No original exception or traceback |
| `Err(error)` containing a caught `ValidationError` | Diagnosing the failing code | No record of functions that later pass the result along |

For an import, include a source `Path`, row, and column when callers need to find
the bad record. For a retained exception, `error.add_note(...)` adds context and
`traceback.print_exception(error)` displays its existing traceback. Printing
`str(error)` alone omits it. Logging and output belong at the caller that decides
whether to retry, reject, or stop.

Wrapping an exception does not raise it or create a chain. Use `raise ... from error`
when deliberately translating it to a different exception. A newly constructed
exception has no original traceback; a record's `cause` field does not create one.

Tracebacks retain stack frames and potentially large local objects. For large
collections of rejected rows, prefer compact error details and source coordinates.
Do not assume exception objects survive serialization or process boundaries.
[Exception notes](https://docs.python.org/3.11/library/exceptions.html#BaseException.add_note),
[traceback formatting](https://docs.python.org/3.11/library/traceback.html#traceback.print_exception).

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

**Results:** `precision(0, 0)` returns `Absent("no predicted positives")`;
`precision(0, 12)` returns `0.0`. Their formatted values are
`"undefined: no predicted positives"` and `"0.000"`.

**Static guarantee:** consumers must narrow the union before treating the result as
a float. Keep required identity fields required instead of making every field absent.

**Runtime obligation:** counts must represent the same evaluation population. Avoid
truthiness checks: a real `0.0` is falsy. If absence reasons drive control flow,
promote them to an enum or separate variants instead of matching free-form strings.
