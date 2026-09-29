# Typed SDK boundaries

[Project overview and reading path](../README.md)

An application calls an untyped prediction SDK. The SDK can mutate its request, fail, or return malformed data. Application code needs a checked outcome.

**Typical Python**

```python,ignore
prediction = sdk.predict({"instances": [0.2, 0.8]})
confidence = prediction["confidence"]
```

The caller assumes success and a valid schema. Missing fields, invalid confidence, or SDK exceptions are discovered only when the application consumes them.

**Alternative**

[Source](../examples/third_party_boundary.py)

```python
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


class VendorResponse(TypedDict):
    """Describe only the demo SDK's response, without asserting validation."""

    label: str
    confidence: float


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
Predictor: TypeAlias = Callable[[PredictRequest], PredictOutcome]


@final
@dataclass(frozen=True, slots=True)
class InvalidBinding:
    """Explain why a discovered dependency cannot be called."""

    reason: str


BindingResult: TypeAlias = Predictor | InvalidBinding


def bind_vendor(candidate: object) -> BindingResult:
    """Adapt a dynamic SDK callable or return a typed binding failure.

    Only this integration seam accepts an unknown dependency. Callability cannot
    prove its signature; argument mismatches become ordinary call failures.
    """
    if not callable(candidate):
        return InvalidBinding("vendor predict must be callable")

    def invoke(request: PredictRequest) -> PredictOutcome:
        """Call once with owned payload data and validate before returning."""
        payload = encode_request(request)
        try:
            response: object = candidate(payload)
        except Exception as error:
            # Contain SDK failures, while leaving adapter defects visible.
            return CallFailed(cause=error)
        return _parse_response(response)

    return invoke


def encode_request(request: PredictRequest) -> VendorPayload:
    """Give the SDK its own mutable list so it cannot mutate the request tuple."""
    return {"instances": list(request.features)}


def _parse_response(payload: object) -> Prediction | InvalidResponse:
    """Validate the SDK schema; return field errors without echoing input values."""
    try:
        return Prediction.model_validate(payload)
    except ValidationError as error:
        return InvalidResponse(str(error))


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


def demo_vendor(payload: VendorPayload) -> VendorResponse:
    """Simulate a dictionary-based vendor that has no validated response schema."""
    return {"label": "positive", "confidence": 0.8}


request = PredictRequest(features=(0.2, 0.8))
binding = bind_vendor(demo_vendor)
match binding:
    case InvalidBinding(reason=reason):
        summary = reason
    case _:
        outcome = binding(request)
        summary = describe(outcome)
unhandled: PredictOutcome = _parse_response({"label": "positive", "confidence": 0.8})
# rejected[bad-argument-type,not-callable]: binding({"instances": [0.2, 0.8]})
# rejected[missing-attribute]: confidence = unhandled.confidence
# rejected[bad-typed-dict-key]: payload: VendorPayload = {"features": [0.2]}
# rejected[bad-return]: def unchecked(request: PredictRequest) -> PredictOutcome: return {"label": "positive", "confidence": 0.8}
```

The demo returns `Prediction(label="positive", confidence=0.8)`.
Binding may first return `InvalidBinding`; after matching a valid `Predictor`,
the call returns `Prediction | CallFailed | InvalidResponse`. Direct
`.confidence` access is rejected until the caller narrows the outcome.
Copying the payload also keeps SDK mutation away from the typed request.

Validation still happens at runtime. Confidence must be finite and in `[0, 1]`;
text, booleans, NaN, and out-of-range values are rejected. Strict float validation
accepts integer endpoints. Existing model instances are revalidated too.

### Why catch `Exception` here?

This SDK offers no reliable exception taxonomy. The adapter catches `Exception`
only around the vendor call, retaining its cause as `CallFailed`; encoding and
validation bugs outside that call remain visible. It does not catch
`KeyboardInterrupt` or `SystemExit`, stop hangs, or contain native crashes.
Timeouts, retries, and process isolation remain caller policies.

`bind_vendor` accepts `object` only at this unavoidable library seam. A
noncallable candidate returns `InvalidBinding`. `callable` does not prove the
signature: a mismatch becomes `CallFailed(TypeError(...))`.
Unknown values stay inside the adapter, which returns precise types.
`hide_input_in_errors` is not general redaction; apply reporting policy at the caller.
See [declared fields](dynamic-access.md) for avoiding reflection in ordinary logic.
