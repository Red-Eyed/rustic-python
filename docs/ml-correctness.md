# Tensors and scientific correctness

[Project overview and reading path](../README.md)

This optional chapter applies the earlier boundary and record patterns to
scientific code. A *tensor* is a multidimensional numerical array; *inference*
means running a model to produce predictions. Framework-specific performance and
numerical obligations complement the API guarantees taught in the core chapters.

Use native tensors in model code. `Tensor` describes the object type; it does not
establish every numerical property. Strengthen configuration, batch structure, and
component interfaces where practical, then check numerical behavior separately.
Do not introduce a wrapper for every intermediate tensor merely to give it a
semantic label.

## Validation before compiled inference

Validate external configuration with Pydantic and load environment settings with
pydantic-settings **before** entering the numerical core. Pass native tensors and
plain records such as `NamedTuple` inputs and `TypedDict` outputs through model
execution. A `TypedDict` is an ordinary dictionary at runtime.

Keep `BaseModel` construction, `TypeAdapter`, settings reads, validation decorators,
and model serialization outside `torch.compile` regions. Do not assume Dynamo can
trace Pydantic internals. Nor are named tuples and dictionaries the only possible
supported containers: compatibility depends on the operations and PyTorch version.

This executable example demonstrates the handoff using small scalar tuples. It
does not import PyTorch or establish `torch.compile` compatibility. In an actual
model, keep tensors as tensors instead of converting their contents to Python.

[Source](../examples/inference_boundary.py)

```python
"""Validate inference options once, then pass plain records to a numerical core."""

from typing import Annotated, NamedTuple, TypedDict

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class InferenceConfig(BaseModel, frozen=True):
    """Validate external options outside the numerical execution path."""

    model_config = ConfigDict(strict=True, extra="forbid")
    temperature: Annotated[FiniteFloat, Field(gt=0)]


class InferenceParameters(NamedTuple):
    """Carry already-validated scalar options without a runtime validation layer."""

    temperature: float


class InferenceOutput(TypedDict):
    """Describe the plain dictionary returned by the numerical core."""

    scaled_logits: tuple[float, ...]


def prepare_inference(payload: str) -> InferenceParameters:
    """Parse JSON options or raise ValidationError, then create plain parameters."""
    config = InferenceConfig.model_validate_json(payload)
    return InferenceParameters(temperature=config.temperature)


def scale_logits(
    logits: tuple[float, ...], parameters: InferenceParameters
) -> InferenceOutput:
    """Scale scores using prepared options; perform no parsing or validation."""
    return {"scaled_logits": tuple(value / parameters.temperature for value in logits)}


parameters = prepare_inference('{"temperature": 2.0}')
output = scale_logits((2.0, -2.0), parameters)
# rejected[bad-typed-dict-key]: scores = output["probabilities"]
# rejected[bad-argument-type]: scale_logits((2.0,), InferenceConfig(temperature=2.0))
# rejected[bad-argument-type]: prepare_inference({})
```

**Static guarantee:** callers cannot substitute the Pydantic config for the
declared inference parameters, or read a nonexistent output field.

**Failure policy:** invalid startup options abort inference setup here. A service
that supports rejecting a request and continuing should translate validation
errors into a typed outcome before calling the numerical core.

**Runtime obligation:** only `prepare_inference` validates temperature. Directly
constructing `InferenceParameters(0.0)` bypasses that guarantee; plain records are
not proof objects. The core also assumes its scores are suitable for the operation.
Validate shape, dtype, device, and value requirements at appropriate admission
points, with tests for numerical outputs. Avoid adding `.tolist()`, `.item()`, or
full-tensor scans per step just to route tensors through a schema validator.
`arbitrary_types_allowed=True` checks a tensor object's type, not its shape or values.

In a PyTorch application, compare eager and compiled outputs on representative
inputs, and test `torch.compile(fullgraph=True)` when claiming execution without
graph breaks. Test dynamic dimensions and changed scalar options too: scalar
specialization can cause recompilation. Container typing alone proves none of
these properties. See [PyTorch fullgraph checks](https://docs.pytorch.org/docs/stable/user_guide/torch_compiler/compile/programming_model.fullgraph_true.html).

## What tensor annotations establish

| Property | Useful representation | Remaining obligation |
| --- | --- | --- |
| Logits vs probabilities | Explicit model/loss API and descriptive inputs | Verify the producing computation and loss behavior; ordinary Tensor annotations do not distinguish these meanings |
| Class IDs vs embeddings | Separate batch fields and record types | Validate dtype, rank, range, and alignment |
| Batch/sequence/channel axes | Shape-aware annotations where supported | Verify operator coverage and dynamic shapes |
| CPU vs accelerator data | Explicit placement at the I/O or training boundary | Check actual devices before operations |
| Valid probability distribution | Validated constructor or producer | Check finiteness, range, and normalization |
| Train vs validation data | Explicit split/provenance records | Prevent leakage through actual data lineage |
| Loss and gradient correctness | Typed signatures plus numerical tests | Verify reductions, masks, and gradient flow |

For example, PyTorch's `CrossEntropyLoss` expects unnormalized logits as input.
Keep that requirement explicit in the model/loss integration and test it; renaming
a tensor's static type does not verify it. [CrossEntropyLoss documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html).

Pyrefly now documents **experimental tensor-shape checking** for PyTorch. This is
distinct from merely annotating a value as `Tensor`, and its API may change. Treat
it as an additional, versioned capability with its own positive and negative
examples before relying on it in a project. This guide's verified baseline does
not enable or demonstrate that extension. See the official
[tensor-shape documentation](https://pyrefly.org/en/docs/tensor-shapes/).

Arbitrary `Annotated[Tensor, "batch channels height width"]` metadata is not, by
itself, proof that an ordinary checker enforces those dimensions. Runtime shape
libraries and static extensions offer different guarantees; document which one
an example actually uses.

Types do not prove numerical stability, correct labels, representative evaluation,
deterministic execution, or an absence of NaNs. Keep numerical tests and runtime
checks focused on those properties. Avoid inserting expensive device synchronization
or full-dataset scans into hot paths just to make a wrapper look validated.
