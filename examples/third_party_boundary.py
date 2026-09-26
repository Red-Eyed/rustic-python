"""Contain an untyped prediction API behind validated requests and outcomes."""

from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from typing import TypeAlias, TypedDict, assert_never, final


@dataclass(frozen=True, slots=True)
class PredictRequest:
    """Require a nonempty finite feature vector before crossing the SDK boundary."""

    features: tuple[float, ...]

    def __post_init__(self) -> None:
        """Reject invalid feature values before calling external code."""
        if not self.features or not all(isfinite(x) for x in self.features):
            raise ValueError("features must be nonempty and finite")


class VendorPayload(TypedDict):
    """Describe the vendor's otherwise loose keyword-free request dictionary."""

    instances: list[float]


VendorCall: TypeAlias = Callable[[VendorPayload], object]


@final
@dataclass(frozen=True, slots=True)
class Prediction:
    """Carry the validated label and confidence returned by the adapter."""

    label: str
    confidence: float


@final
@dataclass(frozen=True, slots=True)
class CallFailed:
    """Preserve a vendor exception for the caller's explicit handling policy."""

    cause: Exception


@final
@dataclass(frozen=True, slots=True)
class InvalidResponse:
    """Explain why a returned value failed the vendor response schema."""

    reason: str


PredictOutcome: TypeAlias = Prediction | CallFailed | InvalidResponse


def bind_vendor(candidate: object) -> VendorCall:
    """Wrap an unknown callable; raise TypeError for a noncallable dependency."""
    if not callable(candidate):
        raise TypeError("vendor predict must be callable")

    def invoke(payload: VendorPayload) -> object:
        """Keep the unknown result opaque; signature and SDK errors may propagate."""
        return candidate(payload)

    return invoke


def encode_request(request: PredictRequest) -> VendorPayload:
    """Give the SDK its own mutable list so it cannot mutate the request tuple."""
    return {"instances": list(request.features)}


def parse_response(payload: object) -> Prediction | InvalidResponse:
    """Validate a plain dictionary; reject malformed data without coercing it."""
    if type(payload) is not dict:
        return InvalidResponse("expected a plain dictionary")
    label: object = payload.get("label")
    confidence: object = payload.get("confidence")
    if type(label) is not str or not label.strip():
        return InvalidResponse("label must be a nonempty string")
    if type(confidence) is not float:
        return InvalidResponse("confidence must be a float")
    if not isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        return InvalidResponse("confidence must be finite and between zero and one")
    return Prediction(label=label, confidence=confidence)


def predict(request: PredictRequest, call: VendorCall) -> PredictOutcome:
    """Call the SDK once; expose ordinary call failures and invalid responses."""
    payload = encode_request(request)
    try:
        response = call(payload)
    except Exception as error:
        # Only the vendor call is inside this handler; adapter bugs must stay visible.
        return CallFailed(cause=error)
    return parse_response(response)


def describe(outcome: PredictOutcome) -> str:
    """Handle every outcome without printing potentially sensitive SDK messages."""
    match outcome:
        case Prediction(label=label, confidence=confidence):
            return f"{label}: {confidence:.3f}"
        case CallFailed(cause=cause):
            return f"vendor call failed: {type(cause).__name__}"
        case InvalidResponse(reason=reason):
            return f"invalid response: {reason}"
        case _:
            assert_never(outcome)


def demo_vendor(payload: VendorPayload) -> object:
    """Simulate a dictionary-based vendor that offers no useful output type."""
    return {"label": "positive", "confidence": 0.8}


request = PredictRequest(features=(0.2, 0.8))
vendor = bind_vendor(demo_vendor)
outcome = predict(request, vendor)
summary = describe(outcome)
# rejected[bad-argument-type]: predict({"instances": [0.2, 0.8]}, vendor)
# rejected[missing-attribute]: confidence = outcome.confidence
# rejected[bad-typed-dict-key]: payload: VendorPayload = {"features": [0.2]}
