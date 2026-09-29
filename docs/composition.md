# Compose interchangeable operations

[Project overview and reading path](../README.md)

A processing pipeline supports independently added operations. Scaling and clipping should compose without a new branch in the pipeline for every operation.

**Typical Python**

```python,ignore
def apply(values, operation):
    if operation == "scale":
        return tuple(value * 2 for value in values)
    if operation == "clip":
        return tuple(max(-1, min(1, value)) for value in values)
    raise ValueError("unknown operation")
```

Every new operation edits this dispatcher. The string selector also hides which behavior and configuration an operation provides.

**Alternative**

[Source](../examples/plugin_composition.py)

```python
"""Extend a transform pipeline through protocols, composition, and a registry."""

from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite
from typing import Annotated, Protocol, TypeAlias

from pydantic import ConfigDict, Field, FiniteFloat
from pydantic.dataclasses import dataclass as validated_dataclass

Features: TypeAlias = tuple[float, ...]


class Transform(Protocol):
    """Transform finite features without mutation, preserving their length."""

    def transform(self, values: Features, /) -> Features:
        """Return finite transformed features, or raise if transformation fails."""
        ...


@validated_dataclass(frozen=True, slots=True, config=ConfigDict(strict=True))
class Scale:
    """Multiply coordinates by a fixed finite factor."""

    factor: FiniteFloat

    def transform(self, values: Features, /) -> Features:
        """Scale finite coordinates; raise ValueError on nonfinite results."""
        scaled = tuple(value * self.factor for value in values)
        if not all(isfinite(value) for value in scaled):
            raise ValueError("scaled values must be finite")
        return scaled


@validated_dataclass(frozen=True, slots=True, config=ConfigDict(strict=True))
class Clip:
    """Provide an additional plugin without inheriting a common base class."""

    limit: Annotated[FiniteFloat, Field(gt=0)]

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
```

The example scales `(-2.0, 0.25, 3.0)` by two and clips to one, producing
`(-1.0, 0.5, 1.0)`. New implementations satisfy `Transform` and are composed at
the entry point. Passing `Describe`, which returns text, is a checker error.

Unknown registry names are explicit outcomes; a caller must handle them before
using the transform. `Mapping` restricts this interface's operations, but does
not freeze the underlying dictionary.

The wrapper checks length and finiteness at runtime because signatures cannot
prove them. Violations stop this pipeline. Wrappers and replacements must preserve
error and mutation contracts as well as types. See [plugin discovery](plugin-discovery.md)
when implementations come from installed packages.
