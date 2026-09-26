"""Consume two fixture branches without importing or manually calling fixtures."""

from typing import TextIO

import pytest

from examples.preprocessing_state import FittedCenterer


def test_centers_samples_from_a_file(
    fitted_centerer: FittedCenterer, sample_stream: TextIO
) -> None:
    """Transform a real temporary-file stream using the fitted component."""
    samples = tuple(float(line) for line in sample_stream)
    actual = tuple(fitted_centerer.transform(value) for value in samples)
    assert actual == pytest.approx((-2.0, 0.0, 2.0), abs=1e-12)
