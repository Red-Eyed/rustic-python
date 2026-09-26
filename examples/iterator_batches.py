"""Preserve element types while forming strict batches with more-itertools."""

from collections.abc import Iterable, Iterator
from typing import TypeVar

from more_itertools import chunked

T = TypeVar("T")


def full_batches(samples: Iterable[T], batch_size: int) -> Iterator[list[T]]:
    """Yield full lists; reject invalid size now and a partial tail on iteration."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    return chunked(samples, batch_size, strict=True)


batches: Iterator[list[int]] = full_batches((1, 2, 3, 4), batch_size=2)
first_batch = next(batches)
# rejected[bad-assignment]: wrong: Iterator[list[str]] = batches
