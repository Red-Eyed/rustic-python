# What tensor types cannot prove

[Project overview and reading path](../README.md)

A classifier passes scores to a loss function. Both raw logits and normalized probabilities are tensors, but the loss expects one of those meanings.

**Typical Python**

```python,ignore
probabilities = model(inputs).softmax(dim=-1)
loss = cross_entropy(probabilities, labels)
```

Ordinary `Tensor` annotations cannot identify this error. The call is type-compatible even though cross-entropy expects unnormalized logits.

**Alternative**

```python,ignore
logits = model(inputs)
loss = cross_entropy(logits, labels)
```

The computation now matches the loss contract. This is a numerical correction,
not a static guarantee; wrapping tensors in nominal types would not prove their
contents or provenance. Keep native tensors and test model/loss integration.

Likewise, ordinary tensor annotations do not prove dimensions, finiteness, device,
correct gradients, or absence of data leakage. Use small known answers, intentional
tolerances, and relevant runtime checks. Avoid unnecessary device synchronization
or full-tensor scans in hot paths.

[Pyrefly's experimental tensor-shape checking](https://pyrefly.org/en/docs/tensor-shapes/)
is a separate capability, not enabled by this guide's verified baseline.
Arbitrary `Annotated` shape strings do not establish checked dimensions.
[CrossEntropyLoss contract](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html).
