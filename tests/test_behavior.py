"""Check the runtime obligations that complement the guide's static contracts."""

import json
from dataclasses import FrozenInstanceError

import pytest
from pydantic import JsonValue

from examples import reasoned_absence as metrics
from examples.email_state import DraftEmail
from examples.explicit_results import Err, InvalidLabel, Ok, parse_label
from examples.generic_batches import Batch, first
from examples.immutable_config import Experiment
from examples.task_variants import Classification, Regression
from examples.validated_records import InvalidMetadata, JobMetadata, parse_metadata


@pytest.mark.parametrize("raw", ["cat", "-1", "", "7.5"])
def test_bad_label_preserves_input(raw: str) -> None:
    """A rejected label retains both the input and its explanation."""
    outcome = parse_label(raw)
    match outcome:
        case Err(error=InvalidLabel(raw=original, reason=reason)):
            assert original == raw
            assert reason
        case _:
            pytest.fail("expected an explicit label error")


@pytest.mark.parametrize(("raw", "expected"), [("0", 0), ("7.0", 7)])
def test_numeric_label_text_is_valid(raw: str, expected: int) -> None:
    """Accept zero and integer-valued decimal text under the parsing policy."""
    assert parse_label(raw) == Ok(expected)


def test_undefined_precision_differs_from_zero() -> None:
    """An empty denominator and incorrect positive predictions remain distinct."""
    assert metrics.precision(0, 0) == metrics.Err(metrics.NoPredictedPositives())
    assert metrics.precision(0, 12) == metrics.Ok(0.0)


def test_negative_counts_are_a_typed_outcome() -> None:
    """A malformed count is visible in the result contract."""
    assert metrics.precision(-1, 2) == metrics.Err(metrics.InvalidCounts(-1, 2))


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (metrics.Ok(0.0), "0.000"),
        (metrics.Ok(0.5), "0.500"),
        (
            metrics.Err(metrics.NoPredictedPositives()),
            "undefined: no predicted positives",
        ),
        (
            metrics.Err(metrics.InvalidCounts(-1, 2)),
            "invalid: counts must be nonnegative",
        ),
    ],
)
def test_metric_formatting(
    value: metrics.Result[float, metrics.NoPredictedPositives | metrics.InvalidCounts],
    expected: str,
) -> None:
    """Require a distinct rendering for each calculated outcome."""
    assert metrics.format_precision(value) == expected


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"name": "data", "workers": True},
        {"name": "", "workers": 10},
        {"name": "data", "workers": 0},
    ],
)
def test_metadata_rejects_invalid_payload(payload: JsonValue) -> None:
    """Reject malformed external data, including booleans masquerading as counts."""
    assert isinstance(parse_metadata(json.dumps(payload)), InvalidMetadata)


def test_metadata_discards_extra_fields() -> None:
    """The parser's documented extra-field policy keeps only the canonical schema."""
    assert parse_metadata(
        json.dumps({"name": "data", "workers": 3, "extra": 1})
    ) == JobMetadata(name="data", workers=3)


def test_addressed_email_can_be_delivered() -> None:
    """Addressing a draft supplies the recipient passed to delivery."""
    delivered: list[tuple[str, str]] = []

    def record(recipient: str, body: str) -> None:
        """Capture the delivery request in memory."""
        delivered.append((recipient, body))

    draft = DraftEmail("Hello")
    draft.to("reader@example.com").send(record)
    assert delivered == [("reader@example.com", "Hello")]


@pytest.mark.parametrize("rest", [(), (2, 3)])
def test_batch_preserves_first_item(rest: tuple[int, ...]) -> None:
    """Selection preserves a valid zero with or without remaining items."""
    batch = Batch(0, rest)
    assert first(batch) == 0
    assert batch.rest == rest


@pytest.mark.parametrize("count", [-1, 0, 1])
def test_invalid_task_parameters_are_rejected(count: int) -> None:
    """Numerical constraints remain enforced at construction, beyond static types."""
    with pytest.raises(ValueError):
        Classification(num_classes=count)
    with pytest.raises(ValueError):
        Regression(huber_delta=float("nan"))


@pytest.mark.parametrize("attribute", ["seed", "features"])
def test_frozen_config_rejects_dynamic_assignment(attribute: str) -> None:
    """Runtime assignment also respects the frozen record."""
    config = Experiment(seed=17, features=("height",))
    with pytest.raises(FrozenInstanceError):
        setattr(config, attribute, 23)
