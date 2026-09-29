# Validate settings before inference

[Project overview and reading path](../README.md)

A model reads a positive temperature setting. Parsing external configuration should happen once, before numerical execution.

**Typical Python**

```text
def predict(logits, payload):
    config = InferenceConfig.model_validate_json(payload)
    return logits / config.temperature
```

Every invocation parses configuration inside the compute path. Type annotations alone do not make that validation suitable for compilation.

**Alternative**

[Source](../examples/inference_boundary.py)

```python
"""Validate inference settings before handing plain parameters to model code."""

from typing import Annotated, NamedTuple

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class InferenceConfig(BaseModel, frozen=True):
    """Validate external options outside the numerical execution path."""

    model_config = ConfigDict(strict=True, extra="forbid")
    temperature: Annotated[FiniteFloat, Field(gt=0)]


class InferenceParameters(NamedTuple):
    """Carry already-validated scalar options without a runtime validation layer."""

    temperature: float


def prepare_inference(payload: str) -> InferenceParameters:
    """Parse startup options; invalid configuration aborts with ValidationError."""
    config = InferenceConfig.model_validate_json(payload)
    return InferenceParameters(temperature=config.temperature)


parameters = prepare_inference('{"temperature": 2.0}')
temperature: float = parameters.temperature
# rejected[missing-attribute]: temperature = parameters.temprature
# rejected[bad-assignment]: wrong: InferenceParameters = InferenceConfig(temperature=2.0)
# rejected[bad-argument-type]: prepare_inference({})
```

The result is `InferenceParameters(temperature=2.0)`. A misspelled field is
rejected, as is assigning a Pydantic configuration object to the plain parameter
type. Model inputs and outputs remain native tensors.

The main benefit of moving parsing is runtime separation, not a new tensor proof.
Invalid startup settings abort with `ValidationError`; a service supporting
rejected requests needs a typed failure at its boundary. Directly constructing
`InferenceParameters(0.0)` bypasses validation. Verify graph capture with the
actual framework and operations rather than inferring it from the container type.
