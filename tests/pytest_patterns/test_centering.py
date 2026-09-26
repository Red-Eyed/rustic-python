"""Parametrize observable behavior while pytest provides shared typed setup."""

import pytest

from examples.preprocessing_state import FittedCenterer, UnfittedCenterer


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(1.0, -3.0, id="below-training-mean"),
        pytest.param(4.0, 0.0, id="at-training-mean"),
        pytest.param(7.0, 3.0, id="above-training-mean"),
    ],
)
def test_centers_with_fitted_statistics(
    fitted_centerer: FittedCenterer, value: float, expected: float
) -> None:
    """Center each input using training statistics, including the zero result."""
    actual = fitted_centerer.transform(value)
    assert actual == pytest.approx(expected, abs=1e-12)


@pytest.mark.parametrize(
    "samples",
    [
        pytest.param((), id="empty"),
        pytest.param((float("nan"),), id="nan"),
        pytest.param((float("inf"),), id="infinite"),
    ],
)
def test_fit_rejects_invalid_training_values(samples: tuple[float, ...]) -> None:
    """Reject well-typed values that violate the fitting preconditions."""
    with pytest.raises(ValueError, match="nonempty and finite"):
        UnfittedCenterer().fit(samples)
