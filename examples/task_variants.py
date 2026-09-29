"""Represent classification and regression with task-specific configuration."""

from dataclasses import dataclass
from typing import Annotated, Literal, TypeAlias, assert_never, final

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    FiniteFloat,
    TypeAdapter,
    ValidationError,
)


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


@final
@dataclass(frozen=True, slots=True)
class InvalidTask:
    """Report a rejected task configuration."""

    reason: str


TaskResult: TypeAlias = Classification | Regression | InvalidTask


def parse_task(payload: str) -> TaskResult:
    """Parse tagged JSON into a task or a typed rejection."""
    try:
        return TASK.validate_json(payload)
    except ValidationError as error:
        return InvalidTask(str(error))


def loss_name(task: Task) -> str:
    """Select the loss family for every supported task variant."""
    match task:
        case Classification():
            return "cross_entropy"
        case Regression():
            return "huber"
        case _:
            assert_never(task)


outcome = parse_task('{"kind": "classification", "num_classes": 10}')
match outcome:
    case Classification() | Regression() as task:
        loss = loss_name(task)
    case InvalidTask():
        loss = "invalid task"
    case _:
        assert_never(outcome)
# rejected[missing-argument,unexpected-keyword]: Classification(huber_delta=1.0)
# rejected[missing-argument,unexpected-keyword]: Regression(num_classes=10)
# rejected[bad-argument-type]: parse_task({})
# rejected[bad-argument-type]: loss_name(outcome)
