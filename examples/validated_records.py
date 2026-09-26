"""Validate a small dataset metadata record before using its fields."""

from collections.abc import Mapping
from typing import TypedDict


class DatasetMetadata(TypedDict):
    """Describe the required dataset identity and classifier output size."""

    name: str
    num_classes: int


def parse_metadata(payload: object) -> DatasetMetadata:
    """Validate required fields; ignore extra keys or raise ValueError."""
    if not isinstance(payload, Mapping):
        raise ValueError("metadata must be a mapping")
    match payload:
        case {"name": str(name), "num_classes": int(count)}:
            if name.strip() and type(count) is int and count >= 2:
                return {"name": name, "num_classes": count}
    raise ValueError("expected a nonempty name and integer num_classes >= 2")


metadata = parse_metadata({"name": "cifar10", "num_classes": 10})
classes = metadata["num_classes"]
# rejected[bad-typed-dict-key]: classes = metadata["class_count"]
# rejected[bad-typed-dict-key]: broken: DatasetMetadata = {"name": "cifar10"}
