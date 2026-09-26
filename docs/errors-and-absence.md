# Errors and absence

[Project overview and reading path](../README.md)

## Make expected failures explicit

**Mistake:** malformed labels are represented by `-1`, an empty dictionary, or an
exception that disappears from the function signature.

Use a result type when failure is an expected outcome the caller should inspect.
Keep exceptions for failures whose propagation is the chosen API contract.

`Result[T, E]` describes either a successful value of type `T` or an error of type
`E`. Rust calls these alternatives `Ok` and `Err`; the **returns** package calls
them `Success` and `Failure`. For example, parsing `"7"` yields `Success(7)`;
parsing `"cat"` yields a `Failure` carrying the rejected input and its reason.

Use `from returns.result import Result, Success, Failure`. **Do not implement
custom generic `Ok`, `Err`, or `Result` classes.** Define your domain error record
when useful, but use the library's containers. See the
[returns Result documentation](https://returns.readthedocs.io/en/latest/pages/result.html).

A simple validation helper may raise `ValueError` without introducing a result
hierarchy. Choose an explicit outcome when callers need to route or collect failures;
see [acceptable simplifications](practical-choices.md#acceptable-simplifications-and-when-to-stop-simplifying).

[Source](../examples/explicit_results.py)

```python
"""Parse labels with an explicit, typed failure outcome."""

from dataclasses import dataclass
from typing import Annotated

from pydantic import Field, TypeAdapter, ValidationError
from returns.result import Failure, Result, Success

LABEL = TypeAdapter[int](Annotated[int, Field(ge=0)])


@dataclass(frozen=True, slots=True)
class InvalidLabel:
    """Preserve the rejected input and the reason it was rejected."""

    raw: str
    reason: str


def parse_label(raw: str) -> Result[int, InvalidLabel]:
    """Parse a nonnegative label; return Failure for malformed or negative input."""
    try:
        label = LABEL.validate_python(raw)
    except ValidationError:
        return Failure(InvalidLabel(raw, "not a nonnegative integer"))
    return Success(label)


def label_name(label: int) -> str:
    """Render a parsed class index without changing its meaning."""
    return f"class {label}"


def describe_label(result: Result[int, InvalidLabel]) -> str:
    """Describe both outcomes without discarding the failure reason."""
    match result:
        case Success():
            return label_name(result.unwrap())
        case Failure():
            error = result.failure()
            return f"rejected {error.raw!r}: {error.reason}"
        case _:
            raise TypeError("unsupported Result implementation")


outcome = parse_label("7")
description = describe_label(outcome)
rendered: Result[str, InvalidLabel] = outcome.map(label_name)
# rejected[bad-assignment]: label: int = outcome
# rejected[bad-assignment]: wrong: Result[str, InvalidLabel] = outcome
# rejected[bad-assignment]: wrong_error: Result[int, str] = outcome
```

**Static guarantee verified here:** the caller cannot assign the result container
to an `int`, or silently change its declared success or error type. `map` changes
the success type while preserving the error type; a failure skips the callback.

**Unwrapping can raise:** `Success(7).unwrap()` returns `7`, while
`Failure("bad").unwrap()` raises `UnwrapFailedError`. Conversely, `.failure()`
raises on a success. Pyrefly permits these calls even without a preceding variant
check. The example checks the variant before extracting its payload; unchecked
unwrapping is an assertion by the programmer, not a static guarantee.

`returns.Result` is a base class, not a statically closed Python union. Do not
claim `assert_never` proves this match exhaustive. The fallback rejects an
unsupported implementation at runtime. For closed domain alternatives such as
classification/regression, keep the separate [sum-type lesson](data-modeling.md).

**Runtime obligation:** Python has no Rust-style `must_use` guarantee here. A caller
can discard the result entirely, and the type does not prove that a function never
raises. This parser also does not know the dataset's class count. Its caller must
validate that a nonnegative label is within that dataset's range.
The tests cover success, failure, preserved error details, skipped mapping, and
the runtime exception from unchecked unwrapping. `map` does not automatically
catch callback exceptions. Plugin-dependent APIs need their own Pyrefly checks;
returns' mypy plugin does not extend Pyrefly.

## Know where a failure happened

A result carries the error value you put into it. It does not automatically
record the history of the computation. Suppose row 1843 in a dataset contains
the label `"cat"` where an integer is required. Two representations serve
different needs:

| Error payload | What you retain | What you lose |
| --- | --- | --- |
| `Failure(InvalidLabel(raw="cat", reason="not a nonnegative integer"))` | Structured information for routing or reporting the rejected record | The original validation exception and its traceback |
| `Failure(error)` containing the caught `ValidationError` | The exception, its validation details, original traceback, and existing exception chain | Nothing automatically records the later functions that merely pass the result along |

The label example above deliberately takes the first approach. Its `raw` and
`reason` fields explain **what** failed, but not the source file or row. In a data
pipeline, include typed provenance such as a source `Path`, row index, and column
name in the error record when callers need to locate bad data. A traceback alone
often cannot identify which of millions of records triggered the same parser.

When diagnosing **where in the code** a failure originated matters, keep the
exception caught by `except ValidationError as error` and return `Failure(error)`.
Use a precise signature such as `Result[int, ValidationError]`. For a config-file
loader that also handles file errors, use `Result[Config, OSError | ValidationError]`
and catch only those expected exceptions. Do not turn unrelated programming bugs
into ordinary rejected records.

On Python 3.11+, `error.add_note("While validating labels in shard 12, row 1843")`
adds context without replacing the exception or its traceback. Notes appear in
formatted tracebacks; they do not change the exception type. Avoid placing raw
secrets or entire samples in diagnostic notes.
[Python exception notes](https://docs.python.org/3.11/library/exceptions.html#BaseException.add_note).

If that result is later unwrapped, returns raises `UnwrapFailedError` **from the
stored exception**. The normal chained traceback shows the original failure,
its notes, and the later unwrap location. A newly constructed exception that was
never raised has no original traceback to preserve. A string or ordinary error
record is not an exception cause: unwrapping it only supplies the traceback of
the unwrap failure. Storing an exception in a record's `cause` field does not make
returns discover it automatically; the caller must handle that cause explicitly.
[returns implementation](https://returns.readthedocs.io/en/latest/_modules/returns/result.html).

You do not need to unwrap just to see the original traceback. After checking for
`Failure`, obtain `error = result.failure()` and use
`traceback.print_exception(error)` at a CLI boundary, or pass the exception as
`exc_info` to your logger. Merely printing `str(error)` omits the traceback.
Outside an active `except` block, do not rely on `logging.exception()` to find an
exception stored in a result. Emit diagnostics once at the layer that decides
whether to stop, retry, or reject a record.
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
