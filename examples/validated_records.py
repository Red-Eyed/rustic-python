"""Validate a small dataset metadata record before using its fields."""

from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints, TypeAdapter, with_config
from typing_extensions import TypedDict


@with_config(ConfigDict(strict=True, extra="ignore"))
class DatasetMetadata(TypedDict):
    """Describe the required dataset identity and classifier output size."""

    name: Annotated[str, StringConstraints(pattern=r"\S")]
    num_classes: Annotated[int, Field(ge=2)]


METADATA = TypeAdapter[DatasetMetadata](DatasetMetadata)


def parse_metadata(payload: object) -> DatasetMetadata:
    """Validate required fields; ignore extra keys or raise ValidationError."""
    return METADATA.validate_python(payload)


metadata = parse_metadata({"name": "cifar10", "num_classes": 10})
classes = metadata["num_classes"]
# rejected[bad-typed-dict-key]: classes = metadata["class_count"]
# rejected[bad-typed-dict-key]: broken: DatasetMetadata = {"name": "cifar10"}
