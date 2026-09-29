# Preserve types with generics

[Project overview and reading path](../README.md)

A helper selects the first job from a batch. Callers need its job type, and selection requires at least one item.

**Typical Python**

```text
def first(items):
    return items[0]

job = first(jobs)
```

The helper has no declared relationship between its input and output types.
Callers rely on knowing what `jobs` contains. An empty collection also fails with
`IndexError` when selected.

**Alternative**

[Source](../examples/generic_batches.py)

```python
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
```

`first(Batch(Job("report")))` returns a `Job`. Assigning it to `str` is rejected;
`T` connects the stored item type to the return type. Requiring `head` also makes
`Batch()` a `missing-argument` error before execution.

The example selects `Job(name="report")`. An external collection can still be
empty: its boundary must handle absence before constructing the batch. A required
first item is useful only after that decision; an unchecked `items[0]` would merely
move the runtime failure elsewhere.
