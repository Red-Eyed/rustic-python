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
