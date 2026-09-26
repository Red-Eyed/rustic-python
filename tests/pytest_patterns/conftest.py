"""Share a small dependency graph of setup resources within this test directory."""

from collections.abc import Iterator
from pathlib import Path
from typing import TextIO

import pytest

from examples.preprocessing_state import FittedCenterer, UnfittedCenterer


@pytest.fixture
def training_values() -> tuple[float, ...]:
    """Provide a small, deterministic training set with a hand-checkable mean."""
    return (2.0, 4.0, 6.0)


@pytest.fixture
def fitted_centerer(training_values: tuple[float, ...]) -> FittedCenterer:
    """Fit the shared training values for tests of subsequent transformation."""
    return UnfittedCenterer().fit(training_values)


@pytest.fixture
def sample_file(tmp_path: Path, training_values: tuple[float, ...]) -> Path:
    """Write one scalar per line in pytest's isolated temporary directory."""
    path = tmp_path / "samples.txt"
    path.write_text("\n".join(str(value) for value in training_values) + "\n")
    return path


@pytest.fixture
def sample_stream(sample_file: Path) -> Iterator[TextIO]:
    """Lend an open stream to one test and close it even if that test fails."""
    with sample_file.open(encoding="utf-8") as stream:
        yield stream
