# Preserve types with generics

[Project overview and reading path](../README.md)

A helper selects the first job from a batch. Callers need its job type, and selection requires at least one item.

**Typical Python**

```python,ignore
def first(items):
    return items[0]


job = first(jobs)
empty_job = first(())
```

The helper has no declared relationship between its input and output types.
Callers rely on knowing what `jobs` contains. An empty collection also fails with
`IndexError` when selected.

**Alternative**

```python,ignore
T = TypeVar("T")


@dataclass(frozen=True)
class Batch(Generic[T]):
    head: T
    rest: tuple[T, ...] = ()


def first(batch: Batch[T]) -> T:
    return batch.head


job = first(Batch(Job("report")))
```

[Source](../examples/generic_batches.py)

`first(Batch(Job("report")))` returns a `Job`. Assigning it to `str` is rejected;
`T` connects the stored item type to the return type. Requiring `head` also makes
`Batch()` a `missing-argument` error before execution.

The example selects `Job(name="report")`. An external collection can still be
empty: its boundary must handle absence before constructing the batch. A required
first item is useful only after that decision; an unchecked `items[0]` would merely
move the runtime failure elsewhere.
