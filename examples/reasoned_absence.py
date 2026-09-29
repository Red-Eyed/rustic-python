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
