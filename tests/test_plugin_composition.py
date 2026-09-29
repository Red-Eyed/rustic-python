"""Verify independent transforms without modifying the pipeline core."""

from dataclasses import dataclass

from examples.plugin_composition import (
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
        """Offset coordinates without mutation."""
        return tuple(value + self.amount for value in values)


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
