"""Express supported narrowing without casts or project-wide suppressions."""

from dataclasses import dataclass
from typing import TypeAlias, TypeGuard, assert_never, final


def is_nonempty_text(value: str | int) -> TypeGuard[str]:
    """Identify strings with visible content; promise only str to the checker."""
    return isinstance(value, str) and bool(value.strip())


@final
@dataclass(frozen=True, slots=True)
class InvalidName:
    """Explain why a value cannot be used as a name."""

    value: str | int


NameResult: TypeAlias = str | InvalidName


def normalize_name(value: str | int) -> NameResult:
    """Strip visible text or return a typed rejection."""
    if is_nonempty_text(value):
        return value.strip()
    return InvalidName(value)


outcome = normalize_name(" training ")
match outcome:
    case str() as name:
        pass
    case InvalidName():
        pass
    case _:
        assert_never(outcome)
# rejected[missing-attribute]: name = outcome.strip()
