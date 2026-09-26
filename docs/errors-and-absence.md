# Errors and absence

[Project overview and reading path](../README.md)

## Make expected failures explicit

**Mistake:** a caller must distinguish accepted and rejected labels, but the
parser returns `-1` or an empty dictionary that hides the rejection reason.

Prefer ordinary exceptions when failure should propagate to a caller that can
handle it. Use explicit outcomes when callers need to inspect, route, or collect
failures as part of normal control flow. A generic result is one optional
representation, not the default return type for every fallible function.

For example, an importer processing 1,000 rows may collect 12 rejected records
while accepting the rest. Typed outcomes help express that policy. If application
startup cannot load its configuration, a validation exception propagating to the
entry point is usually simpler than forwarding an `Err` through every layer.

The maintainers of the archived `result` library questioned the practical fit of
this programming style in Python's ecosystem. That is a useful caution against
adopting it wholesale, not evidence that all explicit domain alternatives are
unhelpful. See [the maintenance discussion](https://github.com/rustedpy/result/issues/201#issuecomment-2559270994).
In Python, converting exceptions into results does not prevent other exceptions
from escaping, and manually forwarding unchanged errors can add noise. Keep
exception handling at the layer that can decide what to do; introduce a result
only when its typed alternatives improve that decision.

Domain-specific alternatives such as `AcceptedRow | RejectedRow` can communicate
more than generic success/failure. Use `Result[T, E]` when the shared success/error
shape itself is useful. The small implementation below teaches that option.

`Result[T, E]` is the closed union `Ok[T] | Err[E]`: two independent frozen
records with no shared result base class. For example, parsing `"7"` yields
`Ok(7)`; parsing `"cat"` yields `Err(InvalidLabel(...))` with the rejected input
and its reason. `Ok` has only a `value` field; `Err` has only an `error` field.

Keep the implementation small: two dataclasses and a union alias. Handle outcomes
with structural pattern matching and `assert_never`, rather than adding unchecked
unwrap methods or a hierarchy of result abstractions. These are concrete class
variants, not structurally interchangeable protocols. `Generic[T]` is Python 3.11
syntax for type parameters; it introduces no shared result implementation.

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

The implementation is a self-contained lesson, not a shared framework for the
other examples. Prefer ordinary exceptions when propagation is clearer, and use
domain-specific variants when success/failure does not capture all alternatives.

## Know where a failure happened

A result carries the error value you put into it. It does not automatically
record the history of the computation. Suppose row 1843 in a dataset contains
the label `"cat"` where an integer is required. Two representations serve
different needs:

| Error payload | What you retain | What you lose |
| --- | --- | --- |
| `Err(InvalidLabel(raw="cat", reason="not a nonnegative integer"))` | Structured information for routing or reporting the rejected record | The original validation exception and its traceback |
| `Err(error)` containing the caught `ValidationError` | The exception, its validation details, original traceback, and existing exception chain | Nothing automatically records the later functions that merely pass the result along |

The label example above deliberately takes the first approach. Its `raw` and
`reason` fields explain **what** failed, but not the source file or row. In a data
pipeline, include typed provenance such as a source `Path`, row index, and column
name in the error record when callers need to locate bad data. A traceback alone
often cannot identify which of millions of records triggered the same parser.

When diagnosing **where in the code** a failure originated matters, keep the
exception caught by `except ValidationError as error` and return `Err(error)`.
Use a precise signature such as `Result[int, ValidationError]`. For a config-file
loader that also handles file errors, use `Result[Config, OSError | ValidationError]`
and catch only those expected exceptions. Do not turn unrelated programming bugs
into ordinary rejected records.

On Python 3.11+, `error.add_note("While validating labels in shard 12, row 1843")`
adds context without replacing the exception or its traceback. Notes appear in
formatted tracebacks; they do not change the exception type. Avoid placing raw
secrets or entire samples in diagnostic notes.
[Python exception notes](https://docs.python.org/3.11/library/exceptions.html#BaseException.add_note).

Wrapping an exception in `Err` does not raise it or add traceback frames. Its
existing traceback, notes, and cause remain on the same exception object. A newly
constructed exception that was never raised has no original traceback to preserve.
A structured error record likewise cannot recreate an exception discarded during
validation. Storing an exception in a record's `cause` field does not automatically
create an exception chain.

After matching `Err(error=error)`, use `traceback.print_exception(error)` at a CLI
boundary, or pass the exception as `exc_info` to your logger. If the caller chooses
to stop with a different exception, explicitly use `raise ... from error` to chain
it. There is no implicit unwrap failure or automatic chaining in these records.
Merely printing `str(error)` omits the traceback. Outside an active `except` block,
do not rely on `logging.exception()` to find an exception stored in a result.
Emit diagnostics once at the layer that decides whether to stop, retry, or reject
a record.
[Traceback formatting](https://docs.python.org/3.11/library/traceback.html#traceback.print_exception).

**Cost and simplification:** traceback objects retain stack frames and can keep
large arrays or other local objects alive. Do not accumulate millions of caught
exceptions in a rejected-row collection. For routine invalid records, retain
compact error details and source coordinates. Preserve exception objects when
the diagnostic value justifies their lifetime; do not assume exception objects
and tracebacks survive JSON serialization or process boundaries.

The distinction is simple: **structured errors locate the bad data when you
include provenance; preserved tracebacks locate the failing code.** Choose the
information callers actually need, and never claim the result container recreates
information discarded at the boundary.

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
