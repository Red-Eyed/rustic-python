"""Verify returns handling and the runtime obligations left by static checking."""

import traceback

import pytest
from pydantic import TypeAdapter, ValidationError
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Result, Success

from examples.explicit_results import (
    InvalidLabel,
    describe_label,
    label_name,
    parse_label,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0", "class 0"),
        ("7.0", "class 7"),
        ("cat", "rejected 'cat': not a nonnegative integer"),
        ("-1", "rejected '-1': not a nonnegative integer"),
    ],
)
def test_describe_handles_both_variants(raw: str, expected: str) -> None:
    """Rendering extracts the appropriate payload without losing failure details."""
    assert describe_label(parse_label(raw)) == expected


def test_mapping_transforms_success() -> None:
    """A successful label becomes text while retaining the declared error type."""
    rendered: Result[str, InvalidLabel] = parse_label("7").map(label_name)
    assert rendered == Success("class 7")


def test_mapping_skips_failure() -> None:
    """A failure preserves its error and never calls the success callback."""

    def unexpected_callback(label: int) -> str:
        """Fail if mapping invokes this callback on a failed parse."""
        pytest.fail("map called the success callback on Failure")

    mapped = parse_label("cat").map(unexpected_callback)
    assert mapped == Failure(InvalidLabel("cat", "not a nonnegative integer"))


def test_unchecked_unwrap_is_a_runtime_failure() -> None:
    """This checker-accepted call raises when the actual result is a failure."""
    result = parse_label("cat")
    with pytest.raises(UnwrapFailedError):
        result.unwrap()


def test_error_extraction_from_success_raises() -> None:
    """The error accessor also requires checking the actual variant."""
    result = parse_label("7")
    with pytest.raises(UnwrapFailedError):
        result.failure()


def test_unwrap_preserves_caught_exception_traceback_and_notes() -> None:
    """Exception payloads remain the cause with their original diagnostic context."""
    with pytest.raises(ValidationError) as original:
        TypeAdapter[int](int).validate_python("cat")
    error = original.value
    original_traceback = error.__traceback__
    assert original_traceback is not None
    error.add_note("While validating shard 12, row 1843")
    result: Result[int, ValidationError] = Failure(error)

    with pytest.raises(UnwrapFailedError) as unwrapped:
        result.unwrap()

    assert unwrapped.value.__cause__ is error
    assert error.__traceback__ is original_traceback
    diagnostic = "".join(traceback.format_exception(unwrapped.value))
    assert "While validating shard 12, row 1843" in diagnostic
    assert "validate_python" in diagnostic
    assert "UnwrapFailedError" in diagnostic


def test_structured_error_does_not_restore_discarded_exception() -> None:
    """An ordinary error record carries data rather than an original exception cause."""
    result = parse_label("cat")
    with pytest.raises(UnwrapFailedError) as unwrapped:
        result.unwrap()
    assert unwrapped.value.__cause__ is None
    assert result.failure() == InvalidLabel("cat", "not a nonnegative integer")
