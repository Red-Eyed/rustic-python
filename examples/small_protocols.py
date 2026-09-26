"""Depend on a small feature transformation contract."""

from typing import Protocol, TypeAlias

Features: TypeAlias = tuple[float, ...]


class FeatureTransform(Protocol):
    """Transform a vector without changing or retaining its input."""

    def transform(self, values: Features, /) -> Features:
        """Return transformed features with the same number of coordinates."""
        ...


class Identity:
    """Leave a feature vector unchanged."""

    def transform(self, values: Features, /) -> Features:
        """Return the immutable input without copying it."""
        return values


class Describe:
    """Produce text rather than a transformed feature vector."""

    def transform(self, values: Features, /) -> str:
        """Describe the vector's size."""
        return f"{len(values)} features"


def prepare(values: Features, transform: FeatureTransform) -> Features:
    """Apply the supplied transformation without choosing a concrete backend."""
    return transform.transform(values)


features = prepare((1.0, 2.0), Identity())
# rejected[bad-argument-type]: prepare((1.0, 2.0), Describe())
