"""Validate job configuration before starting an operation."""

from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints, TypeAdapter, with_config
from typing_extensions import TypedDict


@with_config(ConfigDict(strict=True, extra="ignore"))
class JobMetadata(TypedDict):
    """Require a job name and a positive worker count."""

    name: Annotated[str, StringConstraints(pattern=r"\S")]
    workers: Annotated[int, Field(ge=1)]


METADATA = TypeAdapter[JobMetadata](JobMetadata)


def parse_metadata(payload: str) -> JobMetadata:
    """Load startup JSON; invalid configuration aborts with ValidationError."""
    return METADATA.validate_json(payload)


metadata = parse_metadata('{"name": "report", "workers": 4}')
workers = metadata["workers"]
# rejected[bad-typed-dict-key]: workers = metadata["worker_count"]
# rejected[bad-typed-dict-key]: broken: JobMetadata = {"name": "report"}
# rejected[bad-argument-type]: parse_metadata({})
