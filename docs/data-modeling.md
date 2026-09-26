# Modeling data

[Project overview and reading path](../README.md)

## Parse untrusted data into a precise record

**Mistake:** a JSON dictionary is annotated as a batch record and passed downstream
without checking its fields. An annotation or `cast` does not validate a payload.

Accept `object` at an untrusted boundary, inspect it, and return a precise model.
Use `TypedDict` when dictionary interoperability is useful, and a dataclass for an
ordinary domain record.

[Source](../examples/validated_records.py)

```python
"""Validate a small dataset metadata record before using its fields."""

from collections.abc import Mapping
from typing import TypedDict


class DatasetMetadata(TypedDict):
    """Describe the required dataset identity and classifier output size."""

    name: str
    num_classes: int


def parse_metadata(payload: object) -> DatasetMetadata:
    """Validate required fields; ignore extra keys or raise ValueError."""
    if not isinstance(payload, Mapping):
        raise ValueError("metadata must be a mapping")
    match payload:
        case {"name": str(name), "num_classes": int(count)}:
            if name.strip() and type(count) is int and count >= 2:
                return {"name": name, "num_classes": count}
    raise ValueError("expected a nonempty name and integer num_classes >= 2")


metadata = parse_metadata({"name": "cifar10", "num_classes": 10})
classes = metadata["num_classes"]
# rejected[bad-typed-dict-key]: classes = metadata["class_count"]
# rejected[bad-typed-dict-key]: broken: DatasetMetadata = {"name": "cifar10"}
```

**Static guarantee:** consumers know the required keys and their types. Misspelled
keys and incomplete typed records are rejected.

**Runtime obligation:** only the parser establishes that the external value satisfies
the schema. `TypedDict` itself is not a runtime validator. The explicit `type(count)`
check excludes `True`, because Python's `bool` is a subtype of `int`. For larger
schemas, use a validation library and review its coercion policy. Parse dates into
`date` and timestamps into `datetime` at this same boundary.

## Model alternatives as alternatives

**Mistake:** one configuration has a string `task`, an optional `num_classes`, and
an optional regression threshold. It admits meaningless combinations.

Give each task its own fields. A union then describes the supported alternatives.

[Source](../examples/task_variants.py)

```python
"""Represent classification and regression with task-specific configuration."""

from dataclasses import dataclass
from math import isfinite
from typing import TypeAlias, assert_never, final


@final
@dataclass(frozen=True, slots=True)
class Classification:
    """Configure a classifier with at least two output classes."""

    num_classes: int

    def __post_init__(self) -> None:
        """Reject class counts that cannot describe this classifier."""
        if type(self.num_classes) is not int or self.num_classes < 2:
            raise ValueError("num_classes must be an integer of at least two")


@final
@dataclass(frozen=True, slots=True)
class Regression:
    """Configure Huber loss with a finite positive transition threshold."""

    huber_delta: float

    def __post_init__(self) -> None:
        """Reject invalid Huber thresholds at construction."""
        if not isfinite(self.huber_delta) or self.huber_delta <= 0:
            raise ValueError("huber_delta must be finite and positive")


Task: TypeAlias = Classification | Regression


def loss_name(task: Task) -> str:
    """Select the loss family for every supported task variant."""
    match task:
        case Classification():
            return "cross_entropy"
        case Regression():
            return "huber"
        case _:
            assert_never(task)


task = Classification(num_classes=10)
loss = loss_name(task)
# rejected[missing-argument,unexpected-keyword]: Classification(huber_delta=1.0)
# rejected[missing-argument,unexpected-keyword]: Regression(num_classes=10)
```

**Static guarantee:** each variant has the right fields; unknown constructor
arguments fail checking. A plain `Enum` works for labels without associated data;
dataclass variants also carry data.

**Runtime obligation:** the type `int` does not establish a positive class count.
Construction validates the numerical constraint. `@final` prevents subclassing in
checked code; it does not seal Python classes at runtime.

## Make matching exhaustive

**Mistake:** segmentation is added to a task union, but an old dispatcher silently
falls through to a default loss.

End dispatch over a closed union with `assert_never`. The checker must prove that
no variant reaches that branch. A wildcard returning a default value loses this check.

[Source](../examples/exhaustive_matching.py)

```python
"""Expose an unhandled dataset split during static checking."""

from typing import Literal, TypeAlias, assert_never

Split: TypeAlias = Literal["train", "validation", "test"]


def may_fit_preprocessor(split: Split) -> bool:
    """Allow fitting only on the training split."""
    match split:
        case "train":
            return True
        case "validation" | "test":
            return False
        case _:
            assert_never(split)


allowed = may_fit_preprocessor("train")
# rejected[bad-argument-type]: may_fit_preprocessor("holdout")
```

**Static guarantee:** an unsupported literal cannot be passed. Extend `Split` with
`"holdout"` without updating the match and Pyrefly rejects `assert_never(split)`:
the remaining possibility is no longer `Never`.

**Runtime obligation:** this function does not prove that a dataset called `"train"`
contains training-only data, or that a caller uses the returned decision. Provenance
and leakage checks remain necessary. `assert_never` is also a runtime failure if
unchecked input actually reaches it.

## Optional: nominal tags at controlled boundaries

`NewType` can prevent interchange at an API you control. It is not the default
recommendation for numerical code. The small example below demonstrates the typing
mechanism; its tuple-based softmax is not a proposed tensor or training API.

Consider a nominal tag only when callers can introduce it at a small number of
trusted boundaries and then use it without repeated relabeling. If ordinary
operations keep losing the tag and require new annotations or wrapping, prefer
the native type and a clearer API.

[Source](../examples/semantic_types.py)

```python
"""Distinguish raw classifier scores from normalized probabilities."""

from math import exp, isfinite
from typing import NewType

Logits = NewType("Logits", tuple[float, ...])
Probabilities = NewType("Probabilities", tuple[float, ...])


def softmax(scores: Logits) -> Probabilities:
    """Normalize finite, nonempty scores; raise ValueError for invalid input."""
    if not scores or not all(isfinite(score) for score in scores):
        raise ValueError("scores must be nonempty and finite")
    largest = max(scores)
    weights = tuple(exp(score - largest) for score in scores)
    total = sum(weights)
    return Probabilities(tuple(weight / total for weight in weights))


raw = Logits((2.0, -1.0, 0.5))
probabilities = softmax(raw)
# rejected[bad-argument-type]: softmax(probabilities)
# rejected[bad-argument-type]: softmax((2.0, -1.0, 0.5))
```

**What this example proves:** this particular function rejects an untagged tuple
and the other nominal type. It does not prove that the scores are logits.
`Logits(...)` does not validate or copy its input, and normal operations need not
preserve a newtype. See [Python's NewType documentation](https://docs.python.org/3.11/library/typing.html#newtype).

**Why this is usually a poor tensor strategy:** framework operations use their
own tensor signatures, not application-specific `Logits`/`Probabilities` tags.
Maintaining those distinctions throughout a model can require a parallel layer of
wrappers and repeated assertions about meaning. A caller can still mislabel a
value, so that maintenance does not buy a proof of numerical correctness.

For ordinary model code, keep native tensors, descriptive arguments and batch
fields, explicit model/loss APIs, and behavioral tests. Names alone do not provide
static protection against mixing logits and probabilities; acknowledge that gap
instead of presenting this toy example as a general solution.
