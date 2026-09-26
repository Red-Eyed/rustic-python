# Modeling data

[Project overview and reading path](../README.md)

## Parse untrusted data into a precise record

**Mistake:** a JSON dictionary is annotated as a batch record and passed downstream
without checking its fields. An annotation or `cast` does not validate a payload.

Accept the concrete external representation, here JSON text, and parse it directly
with Pydantic. Do not expose `Any` or `object` in application APIs. Use a
`TypeAdapter` over a `TypedDict` when consumers need an ordinary dictionary, or a
`BaseModel` when a model object is useful. Internal domain records can remain
dataclasses; validation does not require carrying Pydantic through every function.

[Source](../examples/validated_records.py)

```python
"""Validate a small dataset metadata record before using its fields."""

from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints, TypeAdapter, with_config
from typing_extensions import TypedDict


@with_config(ConfigDict(strict=True, extra="ignore"))
class DatasetMetadata(TypedDict):
    """Describe the required dataset identity and classifier output size."""

    name: Annotated[str, StringConstraints(pattern=r"\S")]
    num_classes: Annotated[int, Field(ge=2)]


METADATA = TypeAdapter[DatasetMetadata](DatasetMetadata)


def parse_metadata(payload: str) -> DatasetMetadata:
    """Parse JSON metadata; ignore extra keys or raise ValidationError."""
    return METADATA.validate_json(payload)


metadata = parse_metadata('{"name": "cifar10", "num_classes": 10}')
classes = metadata["num_classes"]
# rejected[bad-typed-dict-key]: classes = metadata["class_count"]
# rejected[bad-typed-dict-key]: broken: DatasetMetadata = {"name": "cifar10"}
# rejected[bad-argument-type]: parse_metadata({})
```

**Static guarantee:** consumers know the required keys and their types. Misspelled
keys, incomplete typed records, and raw dictionary arguments to the JSON parser
are rejected.

**Runtime obligation:** only the parser establishes that the external value satisfies
the schema. Malformed JSON and invalid fields raise `ValidationError`.
`TypedDict` itself is not a runtime validator. Here strict validation
rejects boolean, string, and float class counts; extra metadata keys are ignored.
Use `typing_extensions.TypedDict` for Pydantic's Python 3.11 compatibility.
Parse dates into
`date` and timestamps into `datetime` at this same boundary.

## Model alternatives as alternatives

**Mistake:** one configuration has a string `task`, an optional `num_classes`, and
an optional regression threshold. It admits meaningless combinations.

Give each task its own fields and a literal `kind` tag. Pydantic's **discriminated
union** uses that tag to select the schema at runtime; the Python union lets
Pyrefly check downstream handling. These are separate guarantees.

[Source](../examples/task_variants.py)

```python
"""Represent classification and regression with task-specific configuration."""

from typing import Annotated, Literal, TypeAlias, assert_never, final

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, TypeAdapter


@final
class Classification(BaseModel, frozen=True):
    """Configure a classifier with at least two output classes."""

    model_config = ConfigDict(strict=True, extra="forbid")
    kind: Literal["classification"] = "classification"
    num_classes: Annotated[int, Field(ge=2)]


@final
class Regression(BaseModel, frozen=True):
    """Configure Huber loss with a finite positive transition threshold."""

    model_config = ConfigDict(strict=True, extra="forbid")
    kind: Literal["regression"] = "regression"
    huber_delta: Annotated[FiniteFloat, Field(gt=0)]


Task: TypeAlias = Annotated[Classification | Regression, Field(discriminator="kind")]
TASK = TypeAdapter[Task](Task)


def parse_task(payload: str) -> Task:
    """Parse tagged JSON and validate its fields, or raise ValidationError."""
    return TASK.validate_json(payload)


def loss_name(task: Task) -> str:
    """Select the loss family for every supported task variant."""
    match task:
        case Classification():
            return "cross_entropy"
        case Regression():
            return "huber"
        case _:
            assert_never(task)


task = parse_task('{"kind": "classification", "num_classes": 10}')
loss = loss_name(task)
# rejected[missing-argument,unexpected-keyword]: Classification(huber_delta=1.0)
# rejected[missing-argument,unexpected-keyword]: Regression(num_classes=10)
# rejected[bad-argument-type]: parse_task({})
```

**Static guarantee:** each variant has the right fields; unknown constructor
arguments fail checking. A plain `Enum` works for labels without associated data;
record variants also carry data.

**Runtime obligation:** the type `int` does not establish a positive class count.
Construction validates the numerical constraint. `@final` prevents subclassing in
checked code; it does not seal Python classes at runtime.

For example, `{"kind": "classification", "num_classes": 10}` selects
`Classification`. Missing or unknown tags fail; a classification payload with
`huber_delta` fails instead of silently ignoring a regression option. The literal
defaults make direct constructors convenient, but an incoming dictionary must
still supply `kind` for union dispatch. Tests cover each case in
[test_validation.py](../tests/test_validation.py).

Use `Annotated[Classification | Regression, Field(discriminator="kind")]`
instead of asking an untagged union to guess between overlapping schemas. Reuse
the adapter rather than rebuilding its schema per record. This works for a nested
model field too. See [Pydantic discriminated unions](https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions).
For labels with no associated fields, a `Literal` or enum remains sufficient.
Keep these configuration models outside compiled inference functions; see the
[plain-record handoff](ml-correctness.md#validation-before-compiled-inference).

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
