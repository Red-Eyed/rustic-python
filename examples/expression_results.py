"""Compose expected failures using Expression's typed Result operations."""

from dataclasses import dataclass
from typing import Annotated

from expression import Result
from pydantic import Field, TypeAdapter, ValidationError

LABEL = TypeAdapter[int](Annotated[int, Field(ge=0)])


@dataclass(frozen=True, slots=True)
class InvalidLabel:
    """Preserve why a dataset label could not be parsed."""

    reason: str


def parse_label(raw: str) -> Result[int, InvalidLabel]:
    """Return a nonnegative label or a typed error for malformed input."""
    try:
        value = LABEL.validate_python(raw)
    except ValidationError:
        return Result[int, InvalidLabel].Error(
            InvalidLabel("not a nonnegative integer")
        )
    return Result[int, InvalidLabel].Ok(value)


def label_name(value: int) -> str:
    """Render a successfully parsed class index."""
    return f"class {value}"


def describe_error(error: InvalidLabel) -> str:
    """Render a parse failure without assigning it a success value."""
    return f"rejected: {error.reason}"


parsed = parse_label("7")
rendered: Result[str, InvalidLabel] = parsed.map(label_name)
description: str = rendered.default_with(describe_error)
# rejected[bad-assignment]: wrong: Result[str, InvalidLabel] = parsed
