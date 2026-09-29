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

```diff
- parameters: InferenceConfig = InferenceConfig.model_validate_json(payload)
+ parameters: InferenceParameters = prepare_inference(payload)
  temperature = parameters.temprature
```

**Static benefit:** both precise records reject the misspelled field. The change
adds no tensor guarantee; it separates external validation from the model's plain
configuration. Assigning an `InferenceConfig` to `InferenceParameters` is also
rejected, making the handoff explicit.

**Runtime benefit:** parse settings once before model execution. Keep Pydantic
construction, environment reads, and serialization outside compiled regions.
Model inputs and outputs remain native tensors; this example only prepares settings.

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

**Result:** `parameters` is `InferenceParameters(temperature=2.0)` and
`temperature` is `2.0`. Invalid startup options raise `ValidationError` and abort
setup. A service supporting rejected requests should expose a typed failure at
its boundary instead.

**Limit:** constructing `InferenceParameters(0.0)` directly bypasses validation.
The record is not proof that the scalar or any tensor values are valid. This
example makes no claim about graph capture; native tensors and plain records
still need verification with the actual framework and operations.

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
