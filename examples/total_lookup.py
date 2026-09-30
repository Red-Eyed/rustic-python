"""Make an expected missing mapping key a checked outcome."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar, assert_never, final

T = TypeVar("T")
E = TypeVar("E")


@final
@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Carry a successful value for the caller to handle."""

    value: T


@final
@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Carry an expected failure and its details."""

    error: E


Result: TypeAlias = Ok[T] | Err[E]


@dataclass(frozen=True, slots=True)
class User:
    """Describe a user available to this lookup."""

    name: str


@dataclass(frozen=True, slots=True)
class UserNotFound:
    """Identify the missing key so the caller can report or skip it."""

    user_id: str


def find_user(users: Mapping[str, User], user_id: str) -> Result[User, UserNotFound]:
    """Return a user or a typed missing-key outcome."""
    user = users.get(user_id)
    if user is None:
        return Err(UserNotFound(user_id))
    return Ok(user)


def describe_user(outcome: Result[User, UserNotFound]) -> str:
    """Handle found and missing users without unchecked success access."""
    match outcome:
        case Ok(value=User(name=name)):
            return name
        case Err(error=UserNotFound(user_id=user_id)):
            return f"user {user_id} not found"
        case _:
            assert_never(outcome)


users: Mapping[str, User] = {"u-7": User("Ada")}
found = find_user(users, "u-7")
missing = find_user(users, "u-9")
found_description = describe_user(found)
missing_description = describe_user(missing)
# rejected[missing-attribute]: unchecked_name = found.value.name
