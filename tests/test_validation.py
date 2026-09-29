"""Check boundary validation, settings sources, and plain inference records."""

import json
from collections.abc import Callable

import pytest
from pydantic import JsonValue, ValidationError

from examples.task_variants import (
    Classification,
    InvalidTask,
    Regression,
    TaskResult,
    loss_name,
    parse_task,
)
from examples.third_party_boundary import (
    InvalidResponse,
    Prediction,
    PredictRequest,
    _parse_response,
)
from examples.validated_records import InvalidMetadata, MetadataResult, parse_metadata


@pytest.mark.parametrize("parser", [parse_metadata, parse_task])
@pytest.mark.parametrize("payload", ["", "{", "null", "[]", '"text"', "42"])
def test_json_boundaries_reject_invalid_documents(
    parser: Callable[[str], MetadataResult | TaskResult], payload: str
) -> None:
    """Reject invalid syntax and nonrecord JSON through typed outcomes."""
    assert isinstance(parser(payload), (InvalidMetadata, InvalidTask))


@pytest.mark.parametrize("count", [True, "3", 3.0, -1, 0])
def test_metadata_requires_an_actual_integer(count: bool | str | float) -> None:
    """Pydantic strict validation must not normalize malformed worker counts."""
    assert isinstance(
        parse_metadata(json.dumps({"name": "dataset", "workers": count})),
        InvalidMetadata,
    )


@pytest.mark.parametrize("name", ["", "   ", 42])
def test_metadata_requires_visible_text(name: str | int) -> None:
    """Reject blank and nontext identifiers at the input boundary."""
    assert isinstance(
        parse_metadata(json.dumps({"name": name, "workers": 3})),
        InvalidMetadata,
    )


@pytest.mark.parametrize(
    "features", [(), (float("nan"),), (float("inf"),), (True,), ("0.5",)]
)
def test_request_validates_feature_values(features: tuple[float | str, ...]) -> None:
    """Unknown request values cannot bypass shape and finite-number checks."""
    with pytest.raises(ValidationError):
        PredictRequest.model_validate({"features": features})


def test_response_rejects_extra_fields_and_hides_values() -> None:
    """Keep unexpected response data out of the schema and failure summary."""
    response = _parse_response(
        {"label": "ok", "confidence": 0.5, "secret": "private-value"}
    )
    assert isinstance(response, InvalidResponse)
    assert "private-value" not in response.reason


def test_response_revalidates_existing_model_instances() -> None:
    """A model created through an unchecked escape hatch is not trusted on entry."""
    unchecked = Prediction.model_construct(label="ok", confidence=2.0)
    assert isinstance(_parse_response(unchecked), InvalidResponse)


@pytest.mark.parametrize("confidence", [0, 1])
def test_strict_float_accepts_integer_endpoints(confidence: int) -> None:
    """Document Pydantic's intentional integer-to-float numeric conversion."""
    assert _parse_response({"label": "ok", "confidence": confidence}) == Prediction(
        label="ok", confidence=float(confidence)
    )


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"kind": "classification", "num_classes": 10}, Classification(num_classes=10)),
        ({"kind": "regression", "huber_delta": 0.5}, Regression(huber_delta=0.5)),
    ],
)
def test_discriminator_selects_the_variant(
    payload: JsonValue, expected: Classification | Regression
) -> None:
    """Tagged input selects a validated variant with an exhaustive downstream API."""
    parsed = parse_task(json.dumps(payload))
    assert parsed == expected
    assert isinstance(parsed, (Classification, Regression))
    assert loss_name(parsed) == loss_name(expected)


@pytest.mark.parametrize(
    ("payload", "error_kind"),
    [
        ({"num_classes": 10}, "union_tag_not_found"),
        ({"kind": "clustering", "num_classes": 10}, "union_tag_invalid"),
        ({"kind": "classification", "huber_delta": 0.5}, "missing"),
        (
            {"kind": "classification", "num_classes": 10, "huber_delta": 0.5},
            "extra_forbidden",
        ),
        ({"kind": "classification", "num_classes": True}, "int_type"),
        ({"kind": "regression", "huber_delta": -1.0}, "greater_than"),
    ],
)
def test_discriminated_union_rejects_invalid_payloads(
    payload: JsonValue, error_kind: str
) -> None:
    """Missing tags, unknown variants, and mismatched fields fail at the boundary."""
    result = parse_task(json.dumps(payload))
    assert isinstance(result, InvalidTask)
    assert error_kind in result.reason
