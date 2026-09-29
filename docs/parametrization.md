# Parametrize a contract

[Project overview and reading path](../README.md)

A centerer must work below, at, and above its fitted mean. Each case should be independently visible when a test fails.

**Typical Python**

```text
def test_centering(fitted_centerer):
    for value, expected in [(1.0, -3.0), (4.0, 0.0), (7.0, 3.0)]:
        assert fitted_centerer.transform(value) == expected
```

The first failure stops the loop. The remaining cases are not evaluated as separate tests.

**Alternative**

[Source](../tests/pytest_patterns/test_centering.py)

```python
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
```

Pytest reports each named case independently. With a mean of `4`, the three
outputs are `-3`, `0`, and `3`; empty and nonfinite fitting inputs raise the
specified `ValueError`. `fitted_centerer` comes from the [fixtures](fixtures.md),
while `value` and `expected` come from parametrization.

This improves runtime coverage and diagnosis, not static guarantees. Parameter
objects are not copied: keep cases immutable or construct fresh mutable inputs.
Use the specific exception around only the operation expected to fail.
