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
