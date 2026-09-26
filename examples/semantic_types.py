"""Distinguish raw classifier scores from normalized probabilities."""

from math import exp, isfinite
from typing import NewType

Logits = NewType("Logits", tuple[float, ...])
Probabilities = NewType("Probabilities", tuple[float, ...])


def softmax(scores: Logits) -> Probabilities:
    """Normalize finite, nonempty scores; raise ValueError for invalid input."""
    if not scores or not all(isfinite(score) for score in scores):
        raise ValueError("scores must be nonempty and finite")
    largest = max(scores)
    weights = tuple(exp(score - largest) for score in scores)
    total = sum(weights)
    return Probabilities(tuple(weight / total for weight in weights))


raw = Logits((2.0, -1.0, 0.5))
probabilities = softmax(raw)
# rejected[bad-argument-type]: softmax(probabilities)
# rejected[bad-argument-type]: softmax((2.0, -1.0, 0.5))
