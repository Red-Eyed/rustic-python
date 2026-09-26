"""Parse labels with an explicit, typed failure outcome."""

from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar, assert_never, final

T = TypeVar("T")
E = TypeVar("E")


@final
@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Carry the successful value of an operation."""

    value: T


@final
@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Carry an expected failure without a success value."""

    error: E


@dataclass(frozen=True, slots=True)
class InvalidLabel:
    """Preserve the rejected input and the reason it was rejected."""

    raw: str
    reason: str


Result: TypeAlias = Ok[T] | Err[E]


def parse_label(raw: str) -> Result[int, InvalidLabel]:
    """Parse a nonnegative label; return Err for malformed or negative input."""
    try:
        label = int(raw)
    except ValueError:
        return Err(InvalidLabel(raw, "not an integer"))
    if label < 0:
        return Err(InvalidLabel(raw, "negative label"))
    return Ok(label)


def describe_label(result: Result[int, InvalidLabel]) -> str:
    """Describe both outcomes without discarding the failure reason."""
    match result:
        case Ok(value=label):
            return f"class {label}"
        case Err(error=error):
            return f"rejected {error.raw!r}: {error.reason}"
        case _:
            assert_never(result)


outcome = parse_label("7")
description = describe_label(outcome)
# rejected[bad-assignment]: label: int = outcome
# rejected[missing-attribute]: label = outcome.value
