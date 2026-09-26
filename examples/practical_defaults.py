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
