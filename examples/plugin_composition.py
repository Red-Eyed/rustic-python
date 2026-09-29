"""Extend a transform pipeline through protocols, composition, and a registry."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Annotated, Protocol, TypeAlias

from pydantic import ConfigDict, Field, FiniteFloat
from pydantic.dataclasses import dataclass as validated_dataclass

Features: TypeAlias = tuple[float, ...]


class Transform(Protocol):
    """Transform features without mutation while preserving their length."""

    def transform(self, values: Features, /) -> Features:
        """Return transformed features with the same structural type."""
        ...


@validated_dataclass(frozen=True, slots=True, config=ConfigDict(strict=True))
class Scale:
    """Multiply coordinates by a fixed finite factor."""

    factor: FiniteFloat

    def transform(self, values: Features, /) -> Features:
        """Scale coordinates by the configured factor."""
        return tuple(value * self.factor for value in values)


@validated_dataclass(frozen=True, slots=True, config=ConfigDict(strict=True))
class Clip:
    """Provide an additional plugin without inheriting a common base class."""

    limit: Annotated[FiniteFloat, Field(gt=0)]

    def transform(self, values: Features, /) -> Features:
        """Clip coordinates to the configured symmetric interval."""
        return tuple(max(-self.limit, min(self.limit, value)) for value in values)


@dataclass(frozen=True, slots=True)
class Pipeline:
    """Compose transforms while depending only on their shared protocol."""

    stages: tuple[Transform, ...]

    def transform(self, values: Features, /) -> Features:
        """Apply stages in order."""
        for stage in self.stages:
            values = stage.transform(values)
        return values


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
pipeline = Pipeline((plugins["scale"], plugins["clip"]))
transformed = pipeline.transform((-2.0, 0.25, 3.0))
selected = select_plugin("clip", plugins)
# rejected[bad-argument-type]: Pipeline((Describe(),))
# rejected[missing-attribute]: selected.transform((1.0,))
