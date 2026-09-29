# When a plain function is enough

[Project overview and reading path](../README.md)

A loader needs to count batches. Five items in groups of two means three batches if the tail is kept, or two if it is dropped.

**Typical Python**

```text
batches = sample_count // batch_size
```

The arithmetic silently drops the tail. A type checker cannot know whether that is the intended policy.

**Alternative**

[Source](../examples/practical_defaults.py)

```python
"""Use a plain function when a small, explicit contract needs no domain wrapper."""


def batch_count(sample_count: int, *, batch_size: int, drop_last: bool = False) -> int:
    """Count batches; reject noninteger counts and invalid ranges without I/O."""
    if type(sample_count) is not int or type(batch_size) is not int:
        raise TypeError("counts must be integers, excluding booleans")
    if sample_count < 0 or batch_size <= 0:
        raise ValueError("sample_count must be nonnegative and batch_size positive")
    full_batches, remainder = divmod(sample_count, batch_size)
    if remainder and not drop_last:
        return full_batches + 1
    return full_batches


batches = batch_count(5, batch_size=2)
full_batches_only = batch_count(5, batch_size=2, drop_last=True)
# rejected[bad-argument-type]: batch_count("5", batch_size=2)
```

`batch_count(5, batch_size=2)` returns `3`; setting `drop_last=True` returns `2`.
The signature rejects a string sample count. The tail policy is explicit, but
its correctness still needs behavioral tests: both possible answers are integers.

Ordinary values and one named policy suffice here. Zero samples yield zero
batches. Nonpositive sizes, negative counts, and booleans violate the internal
preconditions and raise. Validate recoverable external input at its boundary.
The helper counts the supplied items; it does not predict filtering or sharding.
