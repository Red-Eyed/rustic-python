# Modeling data

[Project overview and reading path](../README.md)

## Parse untrusted data into a precise record

```diff
- metadata: dict[str, str | int] = {"name": "report", "workers": 4}
+ metadata: JobMetadata = parse_metadata('{"name": "report", "workers": 4}')
  workers = metadata["worker_count"]
```

**Why better:** before, the misspelled key raises `KeyError` only when read.
After, the same access is rejected as `bad-typed-dict-key`: `JobMetadata` declares
`workers`, not `worker_count`. The valid access is `metadata["workers"]`.
Pydantic still validates the external JSON at runtime; the record type protects
subsequent field access.

[Source](../examples/validated_records.py)

```python
"""Validate job configuration before starting an operation."""

from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints, TypeAdapter, with_config
from typing_extensions import TypedDict


@with_config(ConfigDict(strict=True, extra="ignore"))
class JobMetadata(TypedDict):
    """Require a job name and a positive worker count."""

    name: Annotated[str, StringConstraints(pattern=r"\S")]
    workers: Annotated[int, Field(ge=1)]


METADATA = TypeAdapter[JobMetadata](JobMetadata)


def parse_metadata(payload: str) -> JobMetadata:
    """Load startup JSON; invalid configuration aborts with ValidationError."""
    return METADATA.validate_json(payload)


metadata = parse_metadata('{"name": "report", "workers": 4}')
workers = metadata["workers"]
# rejected[bad-typed-dict-key]: workers = metadata["worker_count"]
# rejected[bad-typed-dict-key]: broken: JobMetadata = {"name": "report"}
# rejected[bad-argument-type]: parse_metadata({})
```

**Result:** `metadata` is `{"name": "report", "workers": 4}` and `workers` is `4`.

**Runtime obligation:** only the parser establishes that the external value satisfies
the schema. Malformed JSON and invalid fields raise `ValidationError`.
This example loads configuration once at startup; invalid configuration stops
that operation. If callers can correct the input or reject a record and continue,
translate `ValidationError` into a typed outcome as shown in
[errors and absence](errors-and-absence.md#make-expected-failures-explicit).
`TypedDict` itself is not a runtime validator. Here strict validation
rejects boolean, string, and float worker counts; extra metadata keys are ignored.
Use `typing_extensions.TypedDict` for Pydantic's Python 3.11 compatibility.
Parse dates into
`date` and timestamps into `datetime` at this same boundary.

## Model alternatives as alternatives

```diff
- @dataclass
- class Task:
-     kind: str
-     num_classes: int | None = None
-     huber_delta: float | None = None
- task = Task(kind="classification", huber_delta=0.5)
+ task = Classification(huber_delta=0.5)
```

**Why better:** before, the type permits classification without a class count
and with a regression-only option. After, the checker rejects that construction:
`num_classes` is missing and `huber_delta` is unexpected. The valid construction
is `Classification(num_classes=10)`.

A classifier chooses a category; regression predicts a number. Each variant below
has only its own settings. The literal `kind` tag selects a schema for external
JSON; the union lets the checker distinguish the resulting types.

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

A plain `Enum` works for alternatives without associated fields.

**Runtime obligation:** the type `int` does not establish a positive class count.
Construction validates the numerical constraint. Like the startup parser above,
`parse_task` stops setup on invalid configuration; it does not offer a recovery
branch. `@final` prevents subclassing in checked code; it does not seal Python
classes at runtime.

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

```diff
  match split:
      case "train":
          return True
      case "validation" | "test":
          return False
      case _:
-         return False
+         assert_never(split)
```

**Why better:** adding `"holdout"` to `Split` previously selected the default
silently. Now the checker rejects `assert_never(split)` because `"holdout"` is
still possible. The author must decide how the new split behaves.

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

**Runtime obligation:** this function does not prove that a dataset called `"train"`
contains training-only data, or that a caller uses the returned decision. Provenance
and leakage checks remain necessary. `assert_never` is also a runtime failure if
unchecked input actually reaches it.

## Optional: distinguish identifiers with nominal types

```diff
- def order_reference(customer_id: int, order_id: int) -> str:
+ def order_reference(customer_id: CustomerId, order_id: OrderId) -> str:
      ...
  order_reference(order_id, customer_id)
```

**Why better:** both identifiers are integers, so the old signature accepts them
in the wrong order. Distinct `NewType` names make the swapped call a
`bad-argument-type` error. The valid call produces `"customer:7/order:42"`.

[Source](../examples/semantic_types.py)

```python
"""Reject swapped identifiers even when both are stored as integers."""

from typing import NewType

CustomerId = NewType("CustomerId", int)
OrderId = NewType("OrderId", int)


def order_reference(customer_id: CustomerId, order_id: OrderId) -> str:
    """Format an order reference without checking existence or ownership."""
    return f"customer:{customer_id}/order:{order_id}"


customer_id = CustomerId(7)
order_id = OrderId(42)
reference = order_reference(customer_id, order_id)
# rejected[bad-argument-type]: order_reference(order_id, customer_id)
# rejected[bad-argument-type]: order_reference(7, 42)
```

**Limit:** `NewType` changes the static contract, not the runtime integer.
`CustomerId(42)` cannot prove that 42 identifies a customer or that an order
belongs to them. Establish those facts at the database or input boundary.
Use this pattern for distinct identities that survive through an API; numerical
arrays and tensors should retain their framework's native types.
[NewType documentation](https://docs.python.org/3.11/library/typing.html#newtype).
