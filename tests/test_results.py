"""Verify explicit result handling and preservation of useful failure diagnostics."""

import traceback
from dataclasses import FrozenInstanceError
from typing import assert_never

import pytest
from pydantic import TypeAdapter, ValidationError

from examples.explicit_results import (
    Err,
    InvalidLabel,
    Ok,
    Result,
    describe_label,
    parse_label,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0", "class 0"),
        ("7.0", "class 7"),
        ("cat", "rejected 'cat': not a nonnegative integer"),
        ("-1", "rejected '-1': not a nonnegative integer"),
        ("7.5", "rejected '7.5': not a nonnegative integer"),
    ],
)
def test_describe_handles_both_variants(raw: str, expected: str) -> None:
    """Render successes and preserve the rejected input and reason on failure."""
    assert describe_label(parse_label(raw)) == expected


def test_error_retains_exception_traceback_and_notes() -> None:
    """Storing an exception preserves its identity and existing diagnostic context."""
    with pytest.raises(ValidationError) as original:
        TypeAdapter[int](int).validate_python("cat")
    error = original.value
    original_traceback = error.__traceback__
    assert original_traceback is not None
    error.add_note("While validating shard 12, row 1843")
    result: Result[int, ValidationError] = Err(error)

    match result:
        case Err(error=stored):
            assert stored is error
            assert stored.__traceback__ is original_traceback
            diagnostic = "".join(traceback.format_exception(stored))
            assert "While validating shard 12, row 1843" in diagnostic
            assert "validate_python" in diagnostic
        case Ok():
            pytest.fail("expected the validation failure")
        case _:
            assert_never(result)


def test_caller_can_chain_a_preserved_exception() -> None:
    """Only an explicit raise establishes a new exception chain at the caller."""
    with pytest.raises(ValueError) as original:
        int("cat")
    failure = Err(original.value)
    with pytest.raises(RuntimeError) as raised:
        raise RuntimeError("dataset rejected") from failure.error
    assert raised.value.__cause__ is original.value


def test_structured_error_preserves_the_rejected_input() -> None:
    """A domain record carries the chosen details rather than an implicit traceback."""
    assert parse_label("cat") == Err(InvalidLabel("cat", "not a nonnegative integer"))


@pytest.mark.parametrize(
    ("result", "attribute"), [(Ok(7), "value"), (Err("bad"), "error")]
)
def test_result_fields_reject_dynamic_reassignment(
    result: Result[int, str], attribute: str
) -> None:
    """Exercise the frozen variants' runtime guard through deliberate dynamic access."""
    with pytest.raises(FrozenInstanceError):
        setattr(result, attribute, 9)
