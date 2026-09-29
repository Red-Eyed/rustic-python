# OOP, protocols, and plugins

[Project overview and reading path](../README.md)

## Require only the interface you use

```diff
- def prepare(values: Features, transform: object) -> Features:
-     return getattr(transform, "transform")(values)
+ def prepare(values: Features, transform: FeatureTransform) -> Features:
+     return transform.transform(values)
```

**Why better:** the dynamic call leaves the method's existence and return type to
runtime. The protocol makes them checkable: `Identity` is accepted, while
`Describe`, which returns text, is rejected as `bad-argument-type`.
Implementations satisfy the protocol by their methods, without inheriting from it.

[Source](../examples/small_protocols.py)

```python
"""Depend on a small feature transformation contract."""

from typing import Protocol, TypeAlias

Features: TypeAlias = tuple[float, ...]


class FeatureTransform(Protocol):
    """Transform a vector without changing or retaining its input."""

    def transform(self, values: Features, /) -> Features:
        """Return transformed features with the same number of coordinates."""
        ...


class Identity:
    """Leave a feature vector unchanged."""

    def transform(self, values: Features, /) -> Features:
        """Return the immutable input without copying it."""
        return values


class Describe:
    """Produce text rather than a transformed feature vector."""

    def transform(self, values: Features, /) -> str:
        """Describe the vector's size."""
        return f"{len(values)} features"


def prepare(values: Features, transform: FeatureTransform) -> Features:
    """Apply the supplied transformation without choosing a concrete backend."""
    return transform.transform(values)


features = prepare((1.0, 2.0), Identity())
# rejected[bad-argument-type]: prepare((1.0, 2.0), Describe())
```

**Static guarantee:** argument and return signatures must match. Positional-only
parameters avoid requiring implementers to use the same parameter name.

**Runtime obligation:** the checker does not prove the documented length, purity,
or failure contract. A conforming signature can still have incorrect behavior.
Test implementations against the full contract. Introduce protocols at real
substitution points; do not manufacture one for every helper function.

## OOP, plugins, and extensions

Prefer **protocols for capabilities and composition for reuse**. A class does not
need to inherit from `BaseTransform` to transform a feature vector. It needs to
satisfy the caller's small contract. Use inheritance when the subtype relationship
and inherited behavior are actually part of that contract.

For example, start with scaling `(1.0, 3.0)` by two. Next add clipping to a limit
of four: the pipeline should produce `(2.0, 4.0)`. Adding that operation should
require a new implementation and composition at the application boundary, without
editing the pipeline or adding a `kind == "clip"` branch inside it.

### Choose the kind of extensibility deliberately

| Requirement | Representation | Why |
| --- | --- | --- |
| All alternatives are known and every consumer must handle them | A union of record variants or literals | Adding a variant exposes incomplete `assert_never` dispatch |
| New implementations can arrive independently | A small `Protocol` | Callers depend on a capability rather than a list of classes |
| An operation has configuration or persistent state | A dataclass or ordinary class | Data and the operations maintaining its invariants stay together |
| Reuse a sequence of behaviors | Composition | Each stage remains independently replaceable |
| Add checking, metrics, caching, or retry policy | A wrapper implementing the same protocol | Existing implementations and callers keep their signatures |
| A framework requires a base class | The framework's documented inheritance point | Its lifecycle may depend on more than a method signature |

The classification/regression union in [modeling task variants](data-modeling.md#model-alternatives-as-alternatives)
is a **sum type**: a value is one alternative, with that alternative's associated
data. A dataclass containing several fields is a product: those fields coexist.
Use sums to eliminate invalid combinations, such as classification settings paired
with a regression-only parameter. Use exhaustive matching to make an added task
visible to consumers.

A plugin interface is intentionally open. Do not enumerate every implementation
in a union and expect third-party plugins to extend that union automatically. The
closed domain and open implementation set can coexist: a validated task variant
can select an implementation at the application's construction boundary.

### A registry, a pipeline, and a wrapper

This example uses an explicit registry of configured objects. `Scale` and `Clip`
do not inherit from `Transform`; their signatures satisfy it structurally.
`Pipeline` composes them. `CheckedTransform` is an object wrapper, not a subclass
or a function decorator, and adds the length/finiteness checks that typing alone
cannot express here.

[Source](../examples/plugin_composition.py)

```python
"""Extend a transform pipeline through protocols, composition, and a registry."""

from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite
from typing import Annotated, Protocol, TypeAlias

from pydantic import ConfigDict, Field, FiniteFloat
from pydantic.dataclasses import dataclass as validated_dataclass

Features: TypeAlias = tuple[float, ...]


class Transform(Protocol):
    """Transform finite features without mutation, preserving their length."""

    def transform(self, values: Features, /) -> Features:
        """Return finite transformed features, or raise if transformation fails."""
        ...


@validated_dataclass(frozen=True, slots=True, config=ConfigDict(strict=True))
class Scale:
    """Multiply coordinates by a fixed finite factor."""

    factor: FiniteFloat

    def transform(self, values: Features, /) -> Features:
        """Scale finite coordinates; raise ValueError on nonfinite results."""
        scaled = tuple(value * self.factor for value in values)
        if not all(isfinite(value) for value in scaled):
            raise ValueError("scaled values must be finite")
        return scaled


@validated_dataclass(frozen=True, slots=True, config=ConfigDict(strict=True))
class Clip:
    """Provide an additional plugin without inheriting a common base class."""

    limit: Annotated[FiniteFloat, Field(gt=0)]

    def transform(self, values: Features, /) -> Features:
        """Clip finite coordinates to the configured symmetric interval."""
        if not all(isfinite(value) for value in values):
            raise ValueError("values must be finite")
        return tuple(max(-self.limit, min(self.limit, value)) for value in values)


@dataclass(frozen=True, slots=True)
class Pipeline:
    """Compose transforms while depending only on their shared protocol."""

    stages: tuple[Transform, ...]

    def transform(self, values: Features, /) -> Features:
        """Apply stages in order; propagate any stage's transformation failure."""
        for stage in self.stages:
            values = stage.transform(values)
        return values


@dataclass(frozen=True, slots=True)
class CheckedTransform:
    """Add runtime contract checks by wrapping an existing transform."""

    inner: Transform

    def transform(self, values: Features, /) -> Features:
        """Require finite, same-length output; propagate wrapped exceptions."""
        if not all(isfinite(value) for value in values):
            raise ValueError("values must be finite")
        transformed = self.inner.transform(values)
        if len(transformed) != len(values):
            raise ValueError("transform changed the feature count")
        if not all(isfinite(value) for value in transformed):
            raise ValueError("transform returned nonfinite features")
        return transformed


@dataclass(frozen=True, slots=True)
class UnknownPlugin:
    """Preserve the requested name when registry lookup cannot resolve it."""

    name: str


def select_plugin(
    name: str, plugins: Mapping[str, Transform]
) -> Transform | UnknownPlugin:
    """Resolve a plugin without a global registry or a hardcoded list of kinds."""
    try:
        return plugins[name]
    except KeyError:
        return UnknownPlugin(name)


class Describe:
    """Demonstrate an incompatible implementation with a familiar method name."""

    def transform(self, values: Features, /) -> str:
        """Return text rather than the required feature vector."""
        return f"{len(values)} features"


plugins: Mapping[str, Transform] = {"scale": Scale(2.0), "clip": Clip(1.0)}
pipeline = Pipeline((plugins["scale"], CheckedTransform(plugins["clip"])))
transformed = pipeline.transform((-2.0, 0.25, 3.0))
selected = select_plugin("clip", plugins)
# rejected[bad-argument-type]: Pipeline((Describe(),))
# rejected[missing-attribute]: selected.transform((1.0,))
```

**Static guarantee:** a class that returns text cannot enter the typed pipeline.
Registry lookup makes an unknown name explicit. The caller must handle that outcome
before using the result as a transform. `Mapping` exposes lookup without granting
the selector a mutation API; it does not make the underlying dictionary immutable.

**Extension demonstration:** the tests define an `Offset` plugin outside this module
and register/compose it without changing `Transform`, `Pipeline`, or `select_plugin`.
That is the extension point. In an application, put each implementation in its own
module and assemble the registry at the entry point; the common layer should not
import every plugin or maintain a central chain of type checks.

**Behavioral contract:** identical signatures do not establish substitutability.
Transforms also promise no input mutation, preserved length, and finite output
for valid input. The tests supply a correctly typed plugin that drops a coordinate;
the wrapper catches that violation at runtime. A wrapper must preserve the original
error policy or expose its change explicitly. Retrying, caching, and swallowing
errors are observable behaviors, not harmless decorations.

**Failure policy:** this pipeline stops when a transform violates its finite-value
or length contract. Continuing with corrupt output is unsupported, so guards raise.
A pipeline that supports skipping an item or selecting a fallback needs to declare
those recoverable outcomes in its interface and preserve them in every wrapper.

### Plugin registration is not plugin discovery

An injected registry is enough when the application chooses its plugins directly.
It avoids global mutable registration and import-order-dependent decorators.
Initialization/configuration belongs to the caller; individual operations should
not discover packages or rebuild every plugin on each call.

For independently installed plugins, distribution entry points can provide discovery
through [`importlib.metadata`](https://docs.python.org/3.11/library/importlib.metadata.html#entry-points).
Keep discovery, imports, configuration validation, and
construction in an outer loader. A discovered object is an untyped dependency:
apply the validation and exception-boundary approach from
[the third-party adapter](third-party-boundaries.md#contain-untyped-third-party-code) before admitting it to the core.
This runnable example demonstrates registration/composition; it does not claim to
implement packaging discovery or sandbox untrusted plugin code.

[`@runtime_checkable`](https://docs.python.org/3.11/library/typing.html#typing.runtime_checkable)
is not a validator for method signatures, return values, or
side effects. Likewise, casting a loaded object to a protocol is not proof of
compatibility. Plugin distribution and runtime admission need tests and validation
in addition to the core's static interface.

### When inheritance is appropriate

Use a framework base class when it owns lifecycle behavior you need. In PyTorch,
[`nn.Module`](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html)
is such an integration point: pretending that any object with a
`forward` method is a full replacement ignores parameter registration and other
framework behavior. Keep framework inheritance inside the adapter/model layer,
and expose a smaller protocol to callers that genuinely need less.

An abstract base class can also be appropriate when implementations intentionally
share an enforced lifecycle or implementation. Avoid deep hierarchies whose purpose
is merely to inherit utility methods. On Python 3.11, `typing.override` is not in
the standard library; use its `typing_extensions` backport if an inheritance-based
example needs that decorator. The protocol implementations here are structural,
so their methods are not overrides of an inherited method.

The design question is: **must every caller know every variant, or can it work
with any object satisfying this capability?** The first suggests a sum type; the
second suggests a protocol. Composition lets you add behavior without forcing a
new inheritance relationship.

Scale and Clip use Pydantic-validated dataclasses for configuration at construction.
Their numerical methods retain ordinary algorithm guards. Construct configured
components outside the compute path; these scalar examples do not demonstrate
Dynamo compatibility.
