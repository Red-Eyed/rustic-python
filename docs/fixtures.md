# Compose fixtures through dependencies

[Project overview and reading path](../README.md)

Several tests need the same training values, fitted centerer, and file of samples. Each test should declare what it needs without rebuilding the setup sequence.

**Typical Python**

```python,ignore
def test_file(tmp_path):
    values = (2.0, 4.0, 6.0)
    fitted = UnfittedCenterer().fit(values)
    path = tmp_path / "samples.txt"
    path.write_text("2.0\n4.0\n6.0\n")
    with path.open() as stream:
        actual = tuple(fitted.transform(float(line)) for line in stream)
    assert actual == (-2.0, 0.0, 2.0)
```

This is reasonable for one test. Across many tests, copying the setup can make fitting values and file contents drift apart.

**Alternative**

[Source](../tests/pytest_patterns/conftest.py)

```python
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
```

[Source](../tests/pytest_patterns/test_file_samples.py)

```python
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
```

Both fixture branches request `training_values`, so pytest shares that value
within the test. The test requests `fitted_centerer` and `sample_stream`, then
performs the transformation itself. The result is `(-2.0, 0.0, 2.0)`.

Put shared setup in the nearest `conftest.py`; request fixtures through arguments
rather than importing or calling them. Dependency relationships determine order.
The benefit is consistent setup and managed resources, not a static proof of
pytest's injection. [Fixture annotations](fixture-types.md) explain that limit;
[lifetimes](fixture-lifetimes.md) cover cleanup and sharing.
