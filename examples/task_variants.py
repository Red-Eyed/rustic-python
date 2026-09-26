"""Represent classification and regression with task-specific configuration."""

from dataclasses import dataclass
from math import isfinite
from typing import TypeAlias, assert_never, final


@final
@dataclass(frozen=True, slots=True)
class Classification:
    """Configure a classifier with at least two output classes."""

    num_classes: int

    def __post_init__(self) -> None:
        """Reject class counts that cannot describe this classifier."""
        if type(self.num_classes) is not int or self.num_classes < 2:
            raise ValueError("num_classes must be an integer of at least two")


@final
@dataclass(frozen=True, slots=True)
class Regression:
    """Configure Huber loss with a finite positive transition threshold."""

    huber_delta: float

    def __post_init__(self) -> None:
        """Reject invalid Huber thresholds at construction."""
        if not isfinite(self.huber_delta) or self.huber_delta <= 0:
            raise ValueError("huber_delta must be finite and positive")


Task: TypeAlias = Classification | Regression


def loss_name(task: Task) -> str:
    """Select the loss family for every supported task variant."""
    match task:
        case Classification():
            return "cross_entropy"
        case Regression():
            return "huber"
        case _:
            assert_never(task)


task = Classification(num_classes=10)
loss = loss_name(task)
# rejected[missing-argument,unexpected-keyword]: Classification(huber_delta=1.0)
# rejected[missing-argument,unexpected-keyword]: Regression(num_classes=10)
