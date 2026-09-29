# Choose a coercion policy

[Project overview and reading path](../README.md)

An SDK promises numeric confidence but returns `"0.8"`. The application must decide whether a numeric string is acceptable or a broken vendor contract.

**Typical Python**

```text
confidence = float(payload["confidence"])
```

The conversion silently accepts the string. Successful parsing does not establish that coercion was the intended policy.

**Alternative**

```text
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

class Prediction(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    confidence: FiniteFloat = Field(ge=0, le=1)

prediction = Prediction.model_validate_json(payload_json)
```

Under this schema, `"0.8"`, `True`, NaN, and `1.1` are rejected at runtime;
`0.8` is accepted. Strict float validation also accepts integer endpoints.
The checker knows the resulting field is a float, but cannot prove incoming JSON.

If the source contract permits numeric strings, choose coercion deliberately.
The [SDK adapter](third-party-boundaries.md) shows how to turn a validation failure
into a typed outcome for a caller that can recover.
