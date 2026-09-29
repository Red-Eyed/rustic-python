"""Check boundary validation, settings sources, and plain inference records."""

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import JsonValue, ValidationError
from pydantic_settings import SettingsError

from examples.immutable_config import Experiment
from examples.inference_boundary import (
    InferenceParameters,
    prepare_inference,
    scale_logits,
)
from examples.task_variants import (
    Classification,
    Regression,
    Task,
    loss_name,
    parse_task,
)
from examples.third_party_boundary import (
    InvalidResponse,
    Prediction,
    PredictRequest,
    _parse_response,
)
from examples.validated_records import JobMetadata, parse_metadata


@pytest.mark.parametrize("parser", [parse_metadata, parse_task, prepare_inference])
@pytest.mark.parametrize("payload", ["", "{", "null", "[]", '"text"', "42"])
def test_json_boundaries_reject_invalid_documents(
    parser: Callable[[str], JobMetadata | Task | InferenceParameters], payload: str
) -> None:
    """Reject invalid syntax and nonrecord JSON before values enter the core."""
    with pytest.raises(ValidationError):
        parser(payload)


@pytest.mark.parametrize("count", [True, "3", 3.0, -1, 0])
def test_metadata_requires_an_actual_integer(count: bool | str | float) -> None:
    """Pydantic strict validation must not normalize malformed worker counts."""
    with pytest.raises(ValidationError):
        parse_metadata(json.dumps({"name": "dataset", "workers": count}))


@pytest.mark.parametrize("name", ["", "   ", 42])
def test_metadata_requires_visible_text(name: str | int) -> None:
    """Reject blank and nontext identifiers at the input boundary."""
    with pytest.raises(ValidationError):
        parse_metadata(json.dumps({"name": name, "workers": 3}))


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


@pytest.fixture
def settings_environment(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Isolate the settings namespace from the developer's environment."""
    monkeypatch.delenv("RUSTIC_EXPERIMENT_SEED", raising=False)
    monkeypatch.delenv("RUSTIC_EXPERIMENT_FEATURES", raising=False)
    return monkeypatch


def test_settings_source_precedence(
    settings_environment: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Explicit values override environment, which overrides an explicit dotenv file."""
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        'RUSTIC_EXPERIMENT_SEED=11\nRUSTIC_EXPERIMENT_FEATURES=["area"]\n'
    )
    assert Experiment(_env_file=dotenv).seed == 11
    assert Experiment(_env_file=dotenv).features == ("area",)
    settings_environment.setenv("RUSTIC_EXPERIMENT_SEED", "23")
    assert Experiment(_env_file=dotenv).seed == 23
    assert Experiment(seed=31, _env_file=dotenv).seed == 31


@pytest.mark.parametrize("seed", ["bad", "-1", "true"])
def test_settings_reject_invalid_environment(
    settings_environment: pytest.MonkeyPatch, seed: str
) -> None:
    """An environment source parses numeric text but still validates the schema."""
    settings_environment.setenv("RUSTIC_EXPERIMENT_SEED", seed)
    with pytest.raises(ValidationError):
        Experiment()


def test_settings_reject_boolean_constructor_input(
    settings_environment: pytest.MonkeyPatch,
) -> None:
    """Source parsing does not permit a Python boolean to stand in for an integer."""
    with pytest.raises(ValidationError):
        Experiment(seed=True)


def test_settings_report_malformed_json(
    settings_environment: pytest.MonkeyPatch,
) -> None:
    """Invalid complex environment syntax fails at the settings source layer."""
    settings_environment.setenv("RUSTIC_EXPERIMENT_FEATURES", "not-json")
    with pytest.raises(SettingsError):
        Experiment()


def test_inference_receives_plain_records() -> None:
    """Keep validated configuration outside the numerical core's object graph."""
    parameters = prepare_inference(json.dumps({"temperature": 2.0}))
    assert isinstance(parameters, InferenceParameters)
    assert isinstance(parameters, tuple)
    output = scale_logits((2.0, -2.0), parameters)
    assert type(output) is dict
    assert output == {"scaled_logits": (1.0, -1.0)}


@pytest.mark.parametrize("temperature", [0, -1.0, float("nan"), True, "2.0"])
def test_invalid_inference_options_stop_at_boundary(temperature: float | str) -> None:
    """Reject invalid options before constructing the plain inference parameters."""
    with pytest.raises(ValidationError):
        prepare_inference(json.dumps({"temperature": temperature}))


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
    with pytest.raises(ValidationError) as failure:
        parse_task(json.dumps(payload))
    assert error_kind in {error["type"] for error in failure.value.errors()}
