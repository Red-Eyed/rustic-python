# State-dependent APIs

[Project overview and reading path](../README.md)

A centerer must learn a mean before transforming values. Fitting `(2, 4, 6)` establishes mean `4`; transforming `5` should then return `1`.

**Typical Python**

```python,ignore
class Centerer:
    def __init__(self) -> None:
        self.offset: float | None = None

    def transform(self, value: float) -> float:
        if self.offset is None:
            raise RuntimeError("not fitted")
        return value - self.offset


Centerer().transform(5.0)
```

The method exists before setup, so the checker accepts the call. The lifecycle mistake is discovered only at runtime.

**Alternative**

[Source](../examples/preprocessing_state.py)

```python
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
```

`unfitted.transform(5.0)` is now rejected as `missing-attribute`. Fitting
returns the type that offers transformation, and the valid call produces `1.0`.
The caller no longer needs to remember a separate “fitted” flag.

Empty or nonfinite internal training values abort fitting; the operation has no
fallback model. An ingestion layer supporting bad-row rejection should expose
its own typed outcomes first. The old unfitted value remains usable, and the
public fitted constructor can bypass fitting. These types are not proof of
training provenance or Rust-style move semantics.
