"""Verify the supported library paths and their documented runtime limitations."""

import pytest
from expression import Result

from examples.expression_results import describe_error, label_name, parse_label
from examples.iterator_batches import full_batches


@pytest.mark.parametrize(
    ("raw", "expected"), [("0", "class 0"), ("bad", "rejected: not an integer")]
)
def test_expression_handles_both_paths(raw: str, expected: str) -> None:
    """Mapping transforms success while the error renderer handles failure."""
    assert parse_label(raw).map(label_name).default_with(describe_error) == expected


def test_expression_ok_access_is_not_statically_guarded() -> None:
    """A checker-accepted attribute access can still fail on an Expression error."""
    failure = Result[int, str].Error("invalid")
    with pytest.raises(AttributeError):
        _ = failure.ok


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
