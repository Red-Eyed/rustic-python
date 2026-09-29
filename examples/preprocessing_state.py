"""Expose transformation only after fitting a scalar centering model."""

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True, slots=True)
class FittedCenterer:
    """Hold the fitted offset for a scalar feature."""

    offset: float

    def transform(self, value: float) -> float:
        """Center a scalar using the fitted offset."""
        return value - self.offset


@dataclass(frozen=True, slots=True)
class UnfittedCenterer:
    """Provide fitting without exposing transformation."""

    def fit(self, first: float, *rest: float) -> FittedCenterer:
        """Require at least one training value in the checked call signature."""
        return FittedCenterer(offset=mean((first, *rest)))


unfitted = UnfittedCenterer()
fitted = unfitted.fit(2.0, 4.0, 6.0)
centered = fitted.transform(5.0)
# rejected[missing-attribute]: unfitted.transform(5.0)
# rejected[missing-argument]: unfitted.fit()
