"""Preserve an item's type while making an empty batch unrepresentable."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Batch(Generic[T]):
    """Group at least one item of a statically known type."""

    head: T
    rest: tuple[T, ...] = ()


@dataclass(frozen=True, slots=True)
class Job:
    """Identify work awaiting processing."""

    name: str


def first(batch: Batch[T]) -> T:
    """Return the required first item without losing its type."""
    return batch.head


batch = Batch(Job("report"), (Job("backup"),))
job: Job = first(batch)
# rejected[bad-assignment]: name: str = first(batch)
# rejected[missing-argument]: empty: Batch[Job] = Batch()
