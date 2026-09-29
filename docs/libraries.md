# Typed iterators and deferred failures

[Project overview and reading path](../README.md)

A stream must be processed in complete batches while preserving its element type. With five items and batches of two, the final item must not be silently accepted as a full batch.

**Typical Python**

```text
def batches(items, size):
    return [items[start:start + size] for start in range(0, len(items), size)]

batches([1, 2, 3, 4, 5], 2)
```

This produces `[[1, 2], [3, 4], [5]]`. It requires a sized sequence, returns partial batches, and leaves the element type implicit.

**Alternative**

[Source](../examples/iterator_batches.py)

```python
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
```

The first batch is `[1, 2]`, followed by `[3, 4]`. The checker preserves
`Iterator[list[int]]` and rejects assigning it to `Iterator[list[str]]`.
The example uses more-itertools 11.1.0.

Completeness is a runtime policy, not a property of `list[T]`. Invalid size fails
immediately; an incomplete tail fails during iteration, after earlier batches
have already been yielded. If partial batches are supported, expose that policy
instead. Buffered iterator helpers may retain data; account for that on large streams.

Prefer a standard-library operation when it meets the contract. This guide's
Python 3.11 baseline predates `itertools.batched`, introduced in 3.12.
