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
