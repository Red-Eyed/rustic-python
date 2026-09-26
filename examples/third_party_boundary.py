"""Contain an untyped prediction API behind validated requests and outcomes."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, TypeAlias, TypedDict, assert_never, final

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    FiniteFloat,
    StringConstraints,
    ValidationError,
)


class PredictRequest(BaseModel, frozen=True):
    """Require a nonempty finite feature vector before crossing the SDK boundary."""

    model_config = ConfigDict(strict=True, extra="forbid")
    features: Annotated[tuple[FiniteFloat, ...], Field(min_length=1)]


class VendorPayload(TypedDict):
    """Describe the vendor's otherwise loose keyword-free request dictionary."""

    instances: list[float]


VendorCall: TypeAlias = Callable[[VendorPayload], object]


@final
class Prediction(BaseModel, frozen=True):
    """Carry the validated label and confidence returned by the adapter."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        revalidate_instances="always",
        hide_input_in_errors=True,
    )
    label: Annotated[str, StringConstraints(pattern=r"\S")]
    confidence: Annotated[FiniteFloat, Field(ge=0, le=1)]


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
    """Validate the SDK schema; return field errors without echoing input values."""
    try:
        return Prediction.model_validate(payload)
    except ValidationError as error:
        return InvalidResponse(str(error))


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
