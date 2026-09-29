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
```

`unfitted.transform(5.0)` is now rejected as `missing-attribute`. Fitting
returns the type that offers transformation, and the valid call produces `1.0`.
The caller no longer needs to remember a separate “fitted” flag.

The `first` argument also makes an empty checked fit call invalid. The type
checker cannot prove values are finite or that they came from the intended
dataset; validate those properties at an input boundary with a typed outcome.
The old unfitted value remains usable, and the public fitted constructor can
bypass fitting. These types are not proof of training provenance or Rust-style
move semantics.
