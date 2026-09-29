# Variants instead of optional fields

[Project overview and reading path](../README.md)

A service supports classification and regression. Classification needs a class count; regression needs a positive error threshold. A request must select exactly one.

**Typical Python**

```python,ignore
from dataclasses import dataclass


@dataclass
class Task:
    kind: str
    num_classes: int | None = None
    huber_delta: float | None = None


task = Task(kind="classification", huber_delta=0.5)
```

This well-typed object lacks the classifier setting and contains an unrelated regression setting. The error is left for later code to discover.

**Alternative**

```python,ignore
class Classification(BaseModel):
    kind: Literal["classification"] = "classification"
    num_classes: int


class Regression(BaseModel):
    kind: Literal["regression"] = "regression"
    huber_delta: float


Task = Classification | Regression
```

Each variant owns its required fields. The complete example adds boundary
validation and a typed rejection, using the [Result idea](errors-and-absence.md).

[Source](../examples/task_variants.py)

`Classification(huber_delta=0.5)` is rejected: `num_classes` is missing and
`huber_delta` is unexpected. `Classification(num_classes=10)` is valid.
Each variant owns only its relevant fields.

For JSON input, the `kind` tag selects the runtime schema. Missing or unknown
tags and mismatched fields return `InvalidTask`. The checker rejects passing the
unhandled `TaskResult` to `loss_name`; matching the valid variants narrows it.
The checker cannot establish positive numbers or validate JSON itself.
`@final` prevents checked subclassing, not runtime class manipulation.
Use a literal or enum when an alternative needs no associated fields.
