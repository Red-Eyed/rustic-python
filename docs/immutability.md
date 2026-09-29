# Immutable fields

[Project overview and reading path](../README.md)

Several components share feature configuration. One component must not silently change the features seen by another.

**Typical Python**

```text
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
"""Keep a small experiment configuration immutable at each stored level."""

from typing import Annotated, Final

from pydantic import Field, StringConstraints, TypeAdapter, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Experiment(BaseSettings, frozen=True):
    """Record a seed and an immutable sequence of feature names."""

    model_config = SettingsConfigDict(env_prefix="RUSTIC_EXPERIMENT_", extra="forbid")
    seed: Annotated[int, Field(ge=0)] = 17
    features: Annotated[
        tuple[Annotated[str, StringConstraints(pattern=r"\S")], ...],
        Field(min_length=1),
    ] = ("height", "width")

    @field_validator("seed", mode="before")
    @classmethod
    def _parse_seed(cls, value: object) -> int:
        """Keep bool distinct from counts while allowing numeric settings text."""
        # A before-validator receives arbitrary library input; recover int here.
        match value:
            case bool():
                raise ValueError("seed must not be a boolean")
        return TypeAdapter(int).validate_python(value)


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
actual contract. Environment loading is covered separately in [settings](settings.md).
