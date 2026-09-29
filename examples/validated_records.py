"""Validate job configuration before starting an operation."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class JobMetadata(BaseModel):
    """Require a job name and a positive worker count."""

    model_config = ConfigDict(strict=True, extra="ignore")
    name: Annotated[str, StringConstraints(pattern=r"\S")]
    workers: Annotated[int, Field(ge=1)]


def parse_metadata(payload: str) -> JobMetadata:
    """Load startup JSON; invalid configuration aborts with ValidationError."""
    return JobMetadata.model_validate_json(payload)


metadata = parse_metadata('{"name": "report", "workers": 4}')
workers = metadata.workers
# rejected[missing-attribute]: workers = metadata.worker_count
# rejected[bad-argument-type]: parse_metadata({})
