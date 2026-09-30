# Small protocols

[Project overview and reading path](../README.md)

A preprocessing helper accepts interchangeable transforms. Each must return a numerical vector; a method with the right name but the wrong return type is insufficient.

**Typical Python**

```python,ignore
def prepare(values, transform):
    return transform.transform(values)


class Describe:
    def transform(self, values):
        return f"{len(values)} features"


features = prepare((1.0, 2.0), Describe())
total = sum(features)
```

The helper returns `"2 features"` where later code expects numbers. `sum(features)`
raises `TypeError` at runtime. The interface is implicit, so the mismatch survives
until the caller uses the value.

**Alternative**

```python,ignore
class FeatureTransform(Protocol):
    def transform(self, values: Features) -> Features: ...


def prepare(values: Features, transform: FeatureTransform) -> Features:
    return transform.transform(values)


features = prepare((1.0, 2.0), Identity())
total = sum(features)
```

[Source](../examples/small_protocols.py)

`Identity` is accepted, returns `(1.0, 2.0)`, and gives `total == 3.0`.
Passing `Describe` is rejected as `bad-argument-type`: its return type violates
`FeatureTransform`.
Implementations satisfy the protocol structurally, without inheriting from it.
Positional-only arguments avoid requiring identical parameter names.

The checker does not prove preserved length, purity, or failure behavior. Test
those contracts. Use a protocol where substitution is needed, not for every helper.

Framework inheritance is a separate requirement. For example, `nn.Module` supplies
PyTorch parameter registration; a protocol cannot replace that lifecycle. Keep
the framework base where required and expose only the capability a caller needs.
