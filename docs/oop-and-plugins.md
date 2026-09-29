# Small protocols

[Project overview and reading path](../README.md)

A preprocessing helper accepts interchangeable transforms. Each must return a numerical vector; a method with the right name but the wrong return type is insufficient.

**Typical Python**

```text
def prepare(values, transform):
    return transform.transform(values)

class Describe:
    def transform(self, values):
        return f"{len(values)} features"

features = prepare((1.0, 2.0), Describe())
```

The helper returns text where later code expects numbers. The interface is implicit, so the mismatch reaches runtime.

**Alternative**

[Source](../examples/small_protocols.py)

```python
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
```

`Identity` is accepted and returns `(1.0, 2.0)`. Passing `Describe` is rejected
as `bad-argument-type`: its return type violates `FeatureTransform`.
Implementations satisfy the protocol structurally, without inheriting from it.
Positional-only arguments avoid requiring identical parameter names.

The checker does not prove preserved length, purity, or failure behavior. Test
those contracts. Use a protocol where substitution is needed, not for every helper.

Framework inheritance is a separate requirement. For example, `nn.Module` supplies
PyTorch parameter registration; a protocol cannot replace that lifecycle. Keep
the framework base where required and expose only the capability a caller needs.
