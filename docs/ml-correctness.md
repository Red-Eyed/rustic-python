# Tensors and scientific correctness

[Project overview and reading path](../README.md)

Use native tensors in model code. `Tensor` describes the object type; it does not
establish every numerical property. Strengthen configuration, batch structure, and
component interfaces where practical, then check numerical behavior separately.
Do not introduce a wrapper for every intermediate tensor merely to give it a
semantic label.

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
