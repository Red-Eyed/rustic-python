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


def parse_task(payload: object) -> Task:
    """Select the tagged schema and validate its fields, or raise ValidationError."""
    return TASK.validate_python(payload)


def loss_name(task: Task) -> str:
    """Select the loss family for every supported task variant."""
    match task:
        case Classification():
            return "cross_entropy"
        case Regression():
            return "huber"
        case _:
            assert_never(task)


task = parse_task({"kind": "classification", "num_classes": 10})
loss = loss_name(task)
# rejected[missing-argument,unexpected-keyword]: Classification(huber_delta=1.0)
# rejected[missing-argument,unexpected-keyword]: Regression(num_classes=10)
