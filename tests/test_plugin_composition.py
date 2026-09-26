"""Verify extensions and decorators without modifying the pipeline core."""

from dataclasses import dataclass
from math import isfinite

import pytest

from examples.plugin_composition import (
    CheckedTransform,
    Clip,
    Features,
    Pipeline,
    Scale,
    UnknownPlugin,
    select_plugin,
)


@dataclass(frozen=True)
class Offset:
    """Act as an independently defined plugin unknown to the example module."""

    amount: float

    def transform(self, values: Features, /) -> Features:
        """Offset coordinates without mutation; reject any nonfinite result."""
        shifted = tuple(value + self.amount for value in values)
        if not all(isfinite(value) for value in shifted):
            raise ValueError("shifted values must be finite")
        return shifted


class DropsCoordinate:
    """Have a valid signature while violating the transform's length contract."""

    def transform(self, values: Features, /) -> Features:
        """Discard the first coordinate to demonstrate a behavioral violation."""
        return values[1:]


def test_independent_plugin_needs_no_core_changes() -> None:
    """A new structural implementation composes with the existing pipeline."""
    source = (0.0, 1.0)
    pipeline = Pipeline((Scale(2.0), Offset(0.5), Clip(2.0)))
    assert pipeline.transform(source) == (0.5, 2.0)
    assert source == (0.0, 1.0)


def test_registry_accepts_an_independent_plugin() -> None:
    """Lookup depends on supplied registrations rather than built-in class names."""
    plugin = Offset(0.5)
    assert select_plugin("offset", {"offset": plugin}) is plugin
    assert select_plugin("missing", {"offset": plugin}) == UnknownPlugin("missing")


def test_wrapper_enforces_behavior_beyond_signatures() -> None:
    """Composition adds contract validation without changing the wrapped class."""
    transform = CheckedTransform(DropsCoordinate())
    with pytest.raises(ValueError, match="feature count"):
        transform.transform((1.0, 2.0))
