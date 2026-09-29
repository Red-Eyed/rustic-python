# Validated records

[Project overview and reading path](../README.md)

A worker receives job metadata. Every job needs a name and a positive worker count; downstream code must use the declared field names.

**Typical Python**

```text
metadata: dict[str, str | int] = {"name": "report", "workers": 4}
workers = metadata["worker_count"]
```

The dictionary annotation allows any string key. This typo survives checking and raises `KeyError` when the field is read.

**Alternative**

[Source](../examples/validated_records.py)

```python
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
```

The parser produces `{"name": "report", "workers": 4}`. With `JobMetadata`, the
same `worker_count` access is a `bad-typed-dict-key` error before execution.
Missing required fields are also rejected in checked construction.

The type describes the record; Pydantic validates external JSON at runtime.
Here it rejects nonpositive, boolean, string, and float worker counts and ignores
extra metadata. Invalid startup configuration aborts with `ValidationError`.
A caller supporting correction or row rejection should expose a
[typed failure](errors-and-absence.md) instead.

`TypedDict` itself performs no validation. Unchecked Pydantic construction or
`model_copy(update=...)` can bypass checks; validate the actual admission path.
