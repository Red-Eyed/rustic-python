# State, generics, and immutability

[Project overview and reading path](../README.md)

## Encode preprocessing state in the type

**Mistake:** a scaler exposes `transform` before it has statistics, using
`mean: float | None` and a runtime "not fitted" exception.

Return a different type after fitting. Here a one-dimensional mean-centering
transform makes the state transition explicit.

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

**Static guarantee:** `UnfittedCenterer` has no transformation operation. Callers
working through this API must obtain a fitted value first.

**Runtime obligation:** this is not Rust move semantics. The old unfitted object
remains usable, and the public `FittedCenterer` constructor can be called directly.
The pattern communicates permitted operations; it is not an unforgeable certificate
of training provenance. Validation-only fitting is still leakage even if it type-checks.

## Preserve relationships with generics

**Mistake:** a helper accepts and returns `object`, erasing what kind of sample it
contains. Callers then cast the result back to the type they hoped to receive.

Use a type parameter when an output's type depends on an input's type.

[Source](../examples/generic_batches.py)

```python
"""Preserve the sample type through a batch selection helper."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Batch(Generic[T]):
    """Group samples of one statically known type."""

    samples: tuple[T, ...]


@dataclass(frozen=True, slots=True)
class LabeledSample:
    """Pair a feature vector with its class index."""

    features: tuple[float, ...]
    label: int


def first(batch: Batch[T]) -> T:
    """Return the first sample, or raise ValueError for an empty batch."""
    if not batch.samples:
        raise ValueError("batch must be nonempty")
    return batch.samples[0]


batch = Batch((LabeledSample((0.2, 0.8), label=1),))
sample: LabeledSample = first(batch)
# rejected[bad-assignment]: label: int = first(batch)
```

**Static guarantee:** `first(Batch[LabeledSample])` returns a `LabeledSample`.
The relationship survives without a cast. Reusing a type parameter is meaningful
when it relates inputs, outputs, or fields; it is not decoration.

**Runtime obligation:** `tuple[T, ...]` can be empty. If nonemptiness is central to
an API, model a required first element and a remaining tuple rather than repeatedly
checking it. A generic type also does not prove that every feature vector has the
same length. Python generics do not imply Rust-style monomorphization or a speedup.

## Be precise about immutability

**Mistake:** a supposedly frozen experiment config holds a mutable list, and a later
augmentation step changes it through an alias.

[Source](../examples/immutable_config.py)

```python
"""Keep a small experiment configuration immutable at each stored level."""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class Experiment:
    """Record a seed and an immutable sequence of feature names."""

    seed: int
    features: tuple[str, ...]


config = Experiment(seed=17, features=("height", "width"))
DEFAULT_SEED: Final[int] = 17
# rejected[read-only]: config.seed = 23
# rejected[missing-attribute]: config.features.append("area")
# rejected[bad-assignment]: DEFAULT_SEED = 23
```

**Static guarantee:** field reassignment, the nonexistent tuple mutation operation,
and rebinding a `Final` name are rejected.

**Runtime obligation:** frozen dataclasses are shallow. A frozen record containing
a tensor still allows in-place tensor operations; a tuple can contain mutable
objects. `Final` prevents checked rebinding, not mutation of the referenced object.
Read-only interfaces such as `Sequence` limit what a consumer may do through that
interface but cannot prevent another alias from changing the underlying object.
None of these mechanisms establishes exclusive ownership or freedom from data races.
