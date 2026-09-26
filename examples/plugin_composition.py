"""Extend a transform pipeline through protocols, composition, and a registry."""

from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite
from typing import Protocol, TypeAlias

Features: TypeAlias = tuple[float, ...]


class Transform(Protocol):
    """Transform finite features without mutation, preserving their length."""

    def transform(self, values: Features, /) -> Features:
        """Return finite transformed features, or raise if transformation fails."""
        ...


@dataclass(frozen=True, slots=True)
class Scale:
    """Multiply coordinates by a fixed finite factor."""

    factor: float

    def __post_init__(self) -> None:
        """Reject nonfinite scale factors at construction."""
        if not isfinite(self.factor):
            raise ValueError("factor must be finite")

    def transform(self, values: Features, /) -> Features:
        """Scale finite coordinates; raise ValueError on nonfinite results."""
        scaled = tuple(value * self.factor for value in values)
        if not all(isfinite(value) for value in scaled):
            raise ValueError("scaled values must be finite")
        return scaled


@dataclass(frozen=True, slots=True)
class Clip:
    """Provide an additional plugin without inheriting a common base class."""

    limit: float

    def __post_init__(self) -> None:
        """Require a finite positive symmetric clipping limit."""
        if not isfinite(self.limit) or self.limit <= 0:
            raise ValueError("limit must be finite and positive")

    def transform(self, values: Features, /) -> Features:
        """Clip finite coordinates to the configured symmetric interval."""
        if not all(isfinite(value) for value in values):
            raise ValueError("values must be finite")
        return tuple(max(-self.limit, min(self.limit, value)) for value in values)


@dataclass(frozen=True, slots=True)
class Pipeline:
    """Compose transforms while depending only on their shared protocol."""

    stages: tuple[Transform, ...]

    def transform(self, values: Features, /) -> Features:
        """Apply stages in order; propagate any stage's transformation failure."""
        for stage in self.stages:
            values = stage.transform(values)
        return values


@dataclass(frozen=True, slots=True)
class CheckedTransform:
    """Add runtime contract checks by wrapping an existing transform."""

    inner: Transform

    def transform(self, values: Features, /) -> Features:
        """Require finite, same-length output; propagate wrapped exceptions."""
        if not all(isfinite(value) for value in values):
            raise ValueError("values must be finite")
        transformed = self.inner.transform(values)
        if len(transformed) != len(values):
            raise ValueError("transform changed the feature count")
        if not all(isfinite(value) for value in transformed):
            raise ValueError("transform returned nonfinite features")
        return transformed


@dataclass(frozen=True, slots=True)
class UnknownPlugin:
    """Preserve the requested name when registry lookup cannot resolve it."""

    name: str


def select_plugin(
    name: str, plugins: Mapping[str, Transform]
) -> Transform | UnknownPlugin:
    """Resolve a plugin without a global registry or a hardcoded list of kinds."""
    try:
        return plugins[name]
    except KeyError:
        return UnknownPlugin(name)


class Describe:
    """Demonstrate an incompatible implementation with a familiar method name."""

    def transform(self, values: Features, /) -> str:
        """Return text rather than the required feature vector."""
        return f"{len(values)} features"


plugins: Mapping[str, Transform] = {"scale": Scale(2.0), "clip": Clip(1.0)}
pipeline = Pipeline((plugins["scale"], CheckedTransform(plugins["clip"])))
transformed = pipeline.transform((-2.0, 0.25, 3.0))
selected = select_plugin("clip", plugins)
# rejected[bad-argument-type]: Pipeline((Describe(),))
# rejected[missing-attribute]: selected.transform((1.0,))
