"""Expose transformation only after fitting a scalar centering model."""

from dataclasses import dataclass
from math import isfinite
from statistics import mean


@dataclass(frozen=True, slots=True)
class FittedCenterer:
    """Hold the fitted offset for a scalar feature."""

    offset: float

    def transform(self, value: float) -> float:
        """Center a finite scalar; reject nonfinite input."""
        if not isfinite(value):
            raise ValueError("value must be finite")
        return value - self.offset


@dataclass(frozen=True, slots=True)
class UnfittedCenterer:
    """Provide fitting without exposing transformation."""

    def fit(self, training_values: tuple[float, ...]) -> FittedCenterer:
        """Fit finite, nonempty training values; otherwise raise ValueError."""
        if not training_values or not all(isfinite(x) for x in training_values):
            raise ValueError("training values must be nonempty and finite")
        return FittedCenterer(offset=mean(training_values))


unfitted = UnfittedCenterer()
fitted = unfitted.fit((2.0, 4.0, 6.0))
centered = fitted.transform(5.0)
# rejected[missing-attribute]: unfitted.transform(5.0)
