# Validated records

[Project overview and reading path](../README.md)

A worker receives job metadata. Every job needs a name and a positive worker count; downstream code must use the declared field names.

**Typical Python**

```python,ignore
metadata: dict[str, str | int] = {"name": "report", "workers": 4}
workers = metadata["worker_count"]
```

The dictionary annotation allows any string key. This typo survives checking and
raises `KeyError` when the field is read.

**Alternative**

[Source](../examples/validated_records.py)

```python
"""Validate job configuration before starting an operation."""

from dataclasses import dataclass
from typing import Annotated, TypeAlias, assert_never, final

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError


class JobMetadata(BaseModel):
    """Require a job name and a positive worker count."""

    model_config = ConfigDict(strict=True, extra="ignore")
    name: Annotated[str, StringConstraints(pattern=r"\S")]
    workers: Annotated[int, Field(ge=1)]


@final
@dataclass(frozen=True, slots=True)
class InvalidMetadata:
    """Carry a validation failure for a rejected job record."""

    reason: str


MetadataResult: TypeAlias = JobMetadata | InvalidMetadata


def parse_metadata(payload: str) -> MetadataResult:
    """Validate startup JSON and return either the record or its rejection."""
    try:
        return JobMetadata.model_validate_json(payload)
    except ValidationError as error:
        return InvalidMetadata(str(error))


outcome = parse_metadata('{"name": "report", "workers": 4}')
match outcome:
    case JobMetadata(workers=workers):
        pass
    case InvalidMetadata():
        pass
    case _:
        assert_never(outcome)
# rejected[missing-attribute]: workers = JobMetadata(name="report", workers=4).worker_count
# rejected[missing-attribute]: workers = outcome.workers
# rejected[bad-argument-type]: parse_metadata({})
```

For this input, parsing returns `JobMetadata(name="report", workers=4)`. The
checker rejects both a misspelled model field and direct access to `.workers`
on the unhandled `MetadataResult`. Matching narrows the successful branch.

Pydantic validates external JSON at runtime. Nonpositive, boolean, string, and
float worker counts, missing fields, and malformed JSON return `InvalidMetadata`;
extra fields are ignored by this schema. The checker then requires a caller to
distinguish a valid record from that rejection before using its fields.

Direct model construction validates too; `model_construct` and
`model_copy(update=...)` can bypass checks. Validate the actual admission path.
