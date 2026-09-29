# Validated records

[Project overview and reading path](../README.md)

A worker receives job metadata. Every job needs a name and a positive worker count; downstream code must use the declared field names.

**Typical Python**

```text
metadata: dict[str, str | int] = {"name": "report", "workers": 4}
workers = metadata["worker_count"]
```

The dictionary annotation allows any string key. This typo survives checking and
raises `KeyError` when the field is read.

**Alternative**

[Source](../examples/validated_records.py)

```python
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
```

The parser produces `JobMetadata(name="report", workers=4)`. With `JobMetadata`,
the same `worker_count` access is a `missing-attribute` error before execution.

The type describes the record; Pydantic validates external JSON at runtime.
Here it rejects nonpositive, boolean, string, and float worker counts and ignores
extra metadata. Missing fields are rejected during validation. Invalid startup
configuration aborts with `ValidationError`.
A caller supporting correction or row rejection should expose a
[typed failure](errors-and-absence.md) instead.

Direct model construction validates too; `model_construct` and
`model_copy(update=...)` can bypass checks. Validate the actual admission path.
