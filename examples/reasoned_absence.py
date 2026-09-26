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
