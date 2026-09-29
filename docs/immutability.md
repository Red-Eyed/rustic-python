# Immutable fields

[Project overview and reading path](../README.md)

Several components share feature configuration. One component must not silently change the features seen by another.

**Typical Python**

```python,ignore
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    features: list[str]


config = Config(["height", "width"])
config.features.append("area")
```

Freezing the record blocks field reassignment but permits mutation of the list. The append succeeds and changes shared state.

**Alternative**

[Source](../examples/immutable_config.py)

```python
"""Prevent checked mutation of a small experiment configuration."""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class Experiment:
    """Store feature names in an immutable tuple."""

    seed: int
    features: tuple[str, ...]


config = Experiment(seed=17, features=("height", "width"))
DEFAULT_SEED: Final[int] = 17
# rejected[read-only]: config.seed = 23
# rejected[missing-attribute]: config.features.append("area")
# rejected[bad-assignment]: DEFAULT_SEED = 23
```

The tuple field has no `.append`, so that operation is rejected as
`missing-attribute`. Frozen fields reject reassignment, and `Final` protects
the default binding in checked code.

Immutability is shallow. A frozen record containing a mutable array still exposes
that array's mutation. Here each feature name is a string, so a tuple fits the
actual contract. Environment parsing is a separate [boundary](settings.md).
