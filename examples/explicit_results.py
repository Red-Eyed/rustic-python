"""Parse labels with an explicit, typed failure outcome."""

from dataclasses import dataclass
from typing import Annotated

from pydantic import Field, TypeAdapter, ValidationError
from returns.result import Failure, Result, Success

LABEL = TypeAdapter[int](Annotated[int, Field(ge=0)])


@dataclass(frozen=True, slots=True)
class InvalidLabel:
    """Preserve the rejected input and the reason it was rejected."""

    raw: str
    reason: str


def parse_label(raw: str) -> Result[int, InvalidLabel]:
    """Parse a nonnegative label; return Failure for malformed or negative input."""
    try:
        label = LABEL.validate_python(raw)
    except ValidationError:
        return Failure(InvalidLabel(raw, "not a nonnegative integer"))
    return Success(label)


def label_name(label: int) -> str:
    """Render a parsed class index without changing its meaning."""
    return f"class {label}"


def describe_label(result: Result[int, InvalidLabel]) -> str:
    """Describe both outcomes without discarding the failure reason."""
    match result:
        case Success():
            return label_name(result.unwrap())
        case Failure():
            error = result.failure()
            return f"rejected {error.raw!r}: {error.reason}"
        case _:
            raise TypeError("unsupported Result implementation")


outcome = parse_label("7")
description = describe_label(outcome)
rendered: Result[str, InvalidLabel] = outcome.map(label_name)
# rejected[bad-assignment]: label: int = outcome
# rejected[bad-assignment]: wrong: Result[str, InvalidLabel] = outcome
# rejected[bad-assignment]: wrong_error: Result[int, str] = outcome
