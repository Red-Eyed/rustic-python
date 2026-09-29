# Compose interchangeable operations

[Project overview and reading path](../README.md)

A processing pipeline supports independently added operations. Scaling and clipping should compose without a new branch in the pipeline for every operation.

**Typical Python**

```python,ignore
def apply(values, operation):
    if operation == "scale":
        return tuple(value * 2 for value in values)
    if operation == "clip":
        return tuple(max(-1, min(1, value)) for value in values)
    raise ValueError("unknown operation")
```

Every new operation edits this dispatcher. The string selector also hides which behavior and configuration an operation provides.

**Alternative**

```python,ignore
class Transform(Protocol):
    def transform(self, values: Features) -> Features: ...


class Pipeline:
    def __init__(self, stages: tuple[Transform, ...]):
        self.stages = stages

    def transform(self, values: Features) -> Features:
        for stage in self.stages:
            values = stage.transform(values)
        return values
```

The [protocol lesson](oop-and-plugins.md) explains why an incompatible
implementation is rejected. The complete example adds a typed registry lookup.

[Source](../examples/plugin_composition.py)

The example scales `(-2.0, 0.25, 3.0)` by two and clips to one, producing
`(-1.0, 0.5, 1.0)`. New implementations satisfy `Transform` and are composed at
the entry point. Passing `Describe`, which returns text, is a checker error.

Unknown registry names are explicit outcomes; a caller must handle them before
using the transform. `Mapping` restricts this interface's operations, but does
not freeze the underlying dictionary.

The protocol does not prove length, finiteness, or numerical correctness. Validate
those requirements separately when they matter. Discovered implementations also
need a typed [SDK boundary](third-party-boundaries.md).
