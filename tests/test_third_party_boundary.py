"""Exercise the adapter against genuinely unannotated and malformed dependencies."""

import runpy
from pathlib import Path

import pytest
from pydantic import JsonValue

from examples.third_party_boundary import (
    CallFailed,
    InvalidResponse,
    Prediction,
    Predictor,
    PredictRequest,
    VendorPayload,
    _parse_response,
    bind_vendor,
)


@pytest.fixture
def request_value() -> PredictRequest:
    """Provide a valid request whose immutable features must survive the call."""
    return PredictRequest(features=(0.2, 0.8))


@pytest.fixture
def untyped_vendor(tmp_path: Path) -> Predictor:
    """Load an actually unannotated SDK stand-in outside the checked project."""
    path = tmp_path / "legacy_sdk.py"
    path.write_text(
        '"""Pretend this is an installed, untyped vendor package."""\n'
        "def predict(payload):\n"
        "    payload['instances'].clear()\n"
        "    return {'label': 'positive', 'confidence': 0.8}\n"
    )
    candidate: object = runpy.run_path(str(path))["predict"]
    return bind_vendor(candidate)


def test_untyped_vendor_is_contained(
    request_value: PredictRequest, untyped_vendor: Predictor
) -> None:
    """Validate an untyped response and isolate destructive SDK input mutation."""
    outcome = untyped_vendor(request_value)
    assert outcome == Prediction(label="positive", confidence=0.8)
    assert request_value.features == (0.2, 0.8)


@pytest.mark.parametrize("error", [OSError("offline"), ValueError("bad config")])
def test_vendor_exception_becomes_an_outcome(
    request_value: PredictRequest, error: Exception
) -> None:
    """Keep arbitrary ordinary vendor exceptions explicit and preserve the cause."""

    def broken(payload: VendorPayload) -> JsonValue:
        """Simulate a vendor failure unrelated to the adapter implementation."""
        raise error

    outcome = bind_vendor(broken)(request_value)
    match outcome:
        case CallFailed(cause=cause):
            assert cause is error
        case _:
            pytest.fail("expected the vendor exception to be contained")


def test_wrong_signature_is_a_runtime_call_failure(
    request_value: PredictRequest,
) -> None:
    """Callability alone cannot verify an unknown callable's argument contract."""

    def wrong_signature() -> JsonValue:
        """Simulate an incompatible SDK entry point."""
        return 42

    outcome = bind_vendor(wrong_signature)(request_value)
    match outcome:
        case CallFailed(cause=TypeError()):
            pass
        case _:
            pytest.fail("expected a contained argument mismatch")


@pytest.mark.parametrize("signal", [KeyboardInterrupt(), SystemExit(2)])
def test_process_control_signals_propagate(
    request_value: PredictRequest, signal: BaseException
) -> None:
    """The SDK adapter must not swallow interruption or process-exit signals."""

    def interrupted(payload: VendorPayload) -> JsonValue:
        """Simulate process control arriving during the dependency call."""
        raise signal

    with pytest.raises(type(signal)):
        bind_vendor(interrupted)(request_value)


@pytest.mark.parametrize(
    "response",
    [
        None,
        42,
        [],
        {},
        {"label": "positive"},
        {"label": "", "confidence": 0.8},
        {"label": 1, "confidence": 0.8},
        {"label": "positive", "confidence": "0.8"},
        {"label": "positive", "confidence": True},
        {"label": "positive", "confidence": float("nan")},
        {"label": "positive", "confidence": float("inf")},
        {"label": "positive", "confidence": 1.1},
    ],
)
def test_malformed_vendor_response_is_explicit(
    request_value: PredictRequest, response: JsonValue
) -> None:
    """Wrong shapes, field types, and numerical values never enter the domain."""

    def malformed(payload: VendorPayload) -> JsonValue:
        """Return an unchecked response just as an untyped dependency might."""
        return response

    outcome = bind_vendor(malformed)(request_value)
    match outcome:
        case InvalidResponse(reason=reason):
            assert reason
        case _:
            pytest.fail("expected response validation to fail")


@pytest.mark.parametrize("confidence", [0.0, 1.0])
def test_valid_confidence_endpoints(confidence: float) -> None:
    """The response validator accepts both ends of the closed probability range."""
    assert _parse_response(
        {"label": "positive", "confidence": confidence}
    ) == Prediction(label="positive", confidence=confidence)


def test_noncallable_dependency_is_a_configuration_error() -> None:
    """Reject an invalid binding at construction rather than during prediction."""
    with pytest.raises(TypeError):
        bind_vendor(object())
