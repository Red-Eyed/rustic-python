# An undefined metric is an outcome

[Project overview and reading path](../README.md)

A report calculates precision from true positives and false positives. If there
are no predicted positives, the score is undefined. A real score of zero means
something different: predictions were made, but none was correct.

**Typical Python**

```python,ignore
def precision(true_positives: int, false_positives: int) -> float:
    total = true_positives + false_positives
    return true_positives / total if total else 0.0
```

Both `(0, 0)` and `(0, 12)` return `0.0`. A caller cannot tell an undefined
score from a valid zero.

**Alternative**

[Source](../examples/reasoned_absence.py)

```python
"""Keep an undefined metric distinct from a real zero."""

from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar, assert_never, final

T = TypeVar("T")
E = TypeVar("E")


@final
@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Carry a calculated value."""

    value: T


@final
@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Carry the reason a value could not be calculated."""

    error: E


Result: TypeAlias = Ok[T] | Err[E]


@final
@dataclass(frozen=True, slots=True)
class NoPredictedPositives:
    """Explain why precision is undefined."""


@final
@dataclass(frozen=True, slots=True)
class InvalidCounts:
    """Reject counts that cannot describe a population."""

    true_positives: int
    false_positives: int


def precision(
    true_positives: int, false_positives: int
) -> Result[float, NoPredictedPositives | InvalidCounts]:
    """Compute precision or return why it cannot be calculated."""
    if true_positives < 0 or false_positives < 0:
        return Err(InvalidCounts(true_positives, false_positives))
    predicted_positives = true_positives + false_positives
    if predicted_positives == 0:
        return Err(NoPredictedPositives())
    return Ok(true_positives / predicted_positives)


def format_precision(
    result: Result[float, NoPredictedPositives | InvalidCounts],
) -> str:
    """Render a defined or undefined metric."""
    match result:
        case Ok(value=score):
            return f"{score:.3f}"
        case Err(error=error):
            match error:
                case NoPredictedPositives():
                    return "undefined: no predicted positives"
                case InvalidCounts():
                    return "invalid: counts must be nonnegative"
                case _:
                    assert_never(error)
        case _:
            assert_never(result)


undefined = precision(0, 0)
zero = precision(0, 12)
# rejected[bad-assignment]: score: float = undefined
```

`precision(0, 0)` returns `Err(NoPredictedPositives())`; `precision(0, 12)`
returns `Ok(0.0)`. Formatting produces `"undefined: no predicted positives"`
and `"0.000"` respectively.

The checker rejects assigning the `Result` directly to `float`. The caller must
match both outcomes before using the score, and `assert_never` detects a newly
added outcome variant. This is the same [Result and match](errors-and-absence.md)
pattern used for rejected input: a missing score is a supported outcome of this
calculation.

Negative counts return `Err(InvalidCounts(...))`; callers must handle that
case too. The caller must still ensure both counts describe the same population.
The type checker cannot prove that condition or the numerical correctness of
the formula.
