# A cast asserts; it does not validate

[Project overview and reading path](../README.md)

An external JSON value must become a job record before application code reads its fields.

**Typical Python**

```python,ignore
from typing import cast

decoded_payload = {"name": "report"}
metadata = cast(JobMetadata, decoded_payload)
workers = metadata.workers
```

The checker trusts this assertion even if required keys are missing. The cast
performs no validation or conversion: `metadata` is still a dictionary, so
reading `.workers` raises `AttributeError` at runtime.

**Alternative**

```python,ignore
outcome = parse_metadata('{"name": "report"}')
match outcome:
    case JobMetadata(workers=workers):
        result = f"{workers} workers"
    case InvalidMetadata(reason=reason):
        result = f"rejected: {reason}"
    case _:
        assert_never(outcome)
```

The [record parser](data-modeling.md) validates the wire input before returning
`JobMetadata`. This missing-worker input returns `InvalidMetadata`, which the
caller handles before accessing `workers`.
The improvement is runtime evidence behind the annotation, not stronger checking
from the cast itself.

A narrow cast can be justified when an invariant is already established but the
checker cannot express it. Keep the evidence and cast together at that boundary;
do not spread an unsupported assertion across callers.
