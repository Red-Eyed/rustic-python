# A cast asserts; it does not validate

[Project overview and reading path](../README.md)

An external JSON value must become a job record before application code reads its fields.

**Typical Python**

```text
from typing import cast

metadata = cast(JobMetadata, decoded_payload)
```

The checker trusts this assertion even if required keys are missing. The cast performs no validation or conversion.

**Alternative**

```text
metadata = parse_metadata(payload_json)
```

The [record parser](data-modeling.md) validates the wire input before returning
`JobMetadata`. Its callers then receive a checked field contract.
The improvement is runtime evidence behind the annotation, not stronger checking
from the cast itself.

A narrow cast can be justified when an invariant is already established but the
checker cannot express it. Keep the evidence and cast together at that boundary;
do not spread an unsupported assertion across callers.
