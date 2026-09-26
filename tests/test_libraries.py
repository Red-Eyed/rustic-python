"""Verify the supported library paths and their documented runtime limitations."""

import pytest

from examples.iterator_batches import full_batches


def test_strict_batches_fail_only_when_reaching_the_partial_tail() -> None:
    """Earlier batches can be consumed before strict chunking discovers a tail."""
    batches = full_batches((1, 2, 3, 4, 5), batch_size=2)
    assert next(batches) == [1, 2]
    assert next(batches) == [3, 4]
    with pytest.raises(ValueError):
        next(batches)


@pytest.mark.parametrize("size", [0, -1])
def test_batch_size_is_validated_before_iteration(size: int) -> None:
    """Reject an invalid size even if the caller never consumes the iterator."""
    with pytest.raises(ValueError):
        full_batches((1, 2), batch_size=size)
