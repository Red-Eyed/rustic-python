"""Verify that simple APIs still define boundaries and edge-case behavior."""

import pytest

from examples.practical_defaults import batch_count
from examples.reasoned_absence import Absent, format_precision


@pytest.mark.parametrize(
    ("samples", "size", "drop_last", "expected"),
    [
        pytest.param(0, 2, False, 0, id="empty"),
        pytest.param(0, 2, True, 0, id="empty-drop-last"),
        pytest.param(4, 2, False, 2, id="exact"),
        pytest.param(5, 2, False, 3, id="keep-tail"),
        pytest.param(5, 2, True, 2, id="drop-tail"),
        pytest.param(1, 2, False, 1, id="small-dataset"),
        pytest.param(1, 2, True, 0, id="drop-only-batch"),
    ],
)
def test_batch_policy(samples: int, size: int, drop_last: bool, expected: int) -> None:
    """Compute the declared empty-input and partial-tail policy exactly."""
    assert batch_count(samples, batch_size=size, drop_last=drop_last) == expected


@pytest.mark.parametrize(("samples", "size"), [(-1, 2), (5, 0), (5, -1)])
def test_invalid_ranges(samples: int, size: int) -> None:
    """Well-typed integers still require application-level range checks."""
    with pytest.raises(ValueError, match="nonnegative.*positive"):
        batch_count(samples, batch_size=size)


@pytest.mark.parametrize(("samples", "size"), [(True, 2), (5, True)])
def test_booleans_are_not_counts(samples: int, size: int) -> None:
    """Reject bool even though it is assignable to int in Python typing."""
    with pytest.raises(TypeError, match="excluding booleans"):
        batch_count(samples, batch_size=size)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(0, "0.000", id="integer-zero"),
        pytest.param(0.0, "0.000", id="float-zero"),
        pytest.param(0.5, "0.500", id="fraction"),
        pytest.param(
            Absent("no predictions"), "undefined: no predictions", id="absent"
        ),
    ],
)
def test_numeric_metric_formatting(value: float | Absent, expected: str) -> None:
    """Honor the annotated numeric contract without confusing zero and absence."""
    assert format_precision(value) == expected
