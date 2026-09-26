# Untyped third-party boundaries

[Project overview and reading path](../README.md)

## Contain untyped third-party code

**Mistake:** an SDK accepts arbitrary dictionaries, returns `Any`, mutates its
inputs, and throws undocumented exceptions. Annotating its return as `Prediction`
does not make any of those behaviors safe. A `cast` simply hides the uncertainty.

The boundary needs three separate responsibilities:

1. **Encode a typed request** into the vendor's dictionary schema. Keep vendor keys
   out of the application. Copy mutable payload members when the SDK may mutate them.
2. **Invoke the dependency** in a small exception boundary. Translate ordinary SDK
   exceptions into an explicit outcome, preserving their cause.
3. **Validate the unknown response** into a domain value. Until validation succeeds,
   the result is `object`, regardless of what a vendor's documentation claims.

For example, a response with confidence `"0.8"`, `True`, `NaN`, or `1.1` must not
quietly become a valid prediction. This example accepts finite Python floats in
`[0, 1]`; it deliberately rejects strings, integers, and numeric scalar wrappers.
Any desired coercion belongs in a separate, explicit boundary policy.

[Source](../examples/third_party_boundary.py)

```python
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
```

**Static guarantee:** callers use `PredictRequest`, not arbitrary dictionaries,
and cannot access a prediction's confidence until they handle the failure variants.
The vendor payload itself has a checked schema. Application logic consumes only
the adapter's explicit outcomes.

**The unavoidable untyped seam:** `bind_vendor` accepts `object` so a dynamically
obtained `client.predict` or module attribute can be passed into it. `callable`
proves only that it can be called somehow, not that it accepts this payload. The
wrapper's `object` result deliberately makes no claim about the returned value.
A signature mismatch becomes `CallFailed(TypeError(...))` at invocation; a
malformed returned value becomes `InvalidResponse`. This is containment, not a
static proof of the third-party implementation. There is no unchecked cast to a
domain model.

The demo callback keeps the example runnable without an external service. The
[adapter tests](../tests/test_third_party_boundary.py) also create and load a real
unannotated Python module at runtime. That fake SDK consumes a loose dictionary
and mutates its list. Tests verify that the typed request survives, and exercise
exceptions, wrong call signatures, missing fields, wrong types, NaN, infinity,
and out-of-range confidence values. This tests an actual untyped entry point,
not just a well-annotated mock standing in for one.

### Why catch `Exception` here?

At this particular boundary the dependency offers no reliable exception taxonomy,
and the adapter's contract is to expose ordinary call failures as data. Catching
`Exception` is therefore intentional. It does **not** catch `KeyboardInterrupt`,
`SystemExit`, or other `BaseException` subclasses. The `try` block encloses only
the vendor call; request encoding and response parsing stay outside it so adapter
bugs remain visible. Internal vendor bugs also become `CallFailed`, with their
original exception preserved for diagnosis.

There are still limits: importing the SDK can fail; a call can hang, mutate shared
state, or crash native code. Python exception handling cannot contain a process
crash. Configure timeouts where the dependency supports them and use process
isolation when crash containment is required. This adapter makes one call and
does not retry, log, or silently skip a sample. Those are caller policies.

`Prediction` is a public dataclass, so unchecked code can construct it directly.
The validation guarantee is specifically about values returned by `predict`.
Dependency injection also means a statically compatible callback can still have
bad behavior; the adapter checks its output rather than trusting its signature.

### Missing types versus incorrect types

| Dependency problem | Boundary strategy |
| --- | --- |
| No annotations or a return type of `Any` | Receive as `object`, then validate |
| Loose input dictionaries | Build a `TypedDict` payload from a typed request |
| Incorrect return annotations | Widen the result to `object` and validate actual values |
| Undocumented exceptions | Translate failures at the smallest relevant call boundary |
| Missing import | Install the dependency or supply accurate stubs; do not ignore the import globally |
| Useful stable API, missing stubs | Add a small `.pyi` for the real signature; describe unknown output as `object` |
| SDK mutation | Give it owned payload data and keep mutable aliases out of the core |

A stub states a contract; it does not validate the library or prove that the
implementation honors it. Never write a stub returning a trusted domain model
when the real API returns unvalidated JSON. If a scoped workaround is necessary,
keep it in the adapter and document exactly what remains unchecked.

## Escape hatches and dependency boundaries

| Shortcut | What it loses | Preferred response |
| --- | --- | --- |
| `Any` | Checking of operations and assignments involving that value | A precise schema, protocol, or `object` followed by validation |
| Bare `dict` / `list` | Element and record information | A record type or a parameterized collection |
| `cast(T, value)` | Evidence that the value really satisfies `T` | Parse or narrow; isolate a justified cast at a dependency boundary |
| Blanket ignores | Visibility of unrelated errors on the same line or file | Repair the model; narrowly suppress a verified checker defect |
| A wildcard default in variant dispatch | Evidence that every variant was considered | `assert_never` on the remaining value |
| Arbitrary `**kwargs` | The names and types of the argument contract | Explicit keyword arguments or a typed keyword schema |
| A boolean state flag | Separation of state-specific operations | Distinct types where the permitted operations differ |

An ML ecosystem includes partially typed SDKs, dataframe APIs, decorators, and
framework operations. Place these behind small adapters. Validate external results
once and expose a typed record or protocol to the rest of the code. If the boundary
cannot be verified statically, say so; do not hide it behind a confident return type.

`object` is useful at that boundary because a checker requires narrowing before
most operations. It is not a substitute for a precise return type after validation.

When an upstream stub is wrong, prefer a corrected stub or a small documented
adapter. A necessary suppression should identify the exact diagnostic, explain the
upstream mismatch, and have a removal condition. Never weaken the project-wide
configuration merely to make one integration green. Ruff's suppression rules and
Pyrefly's unused-ignore check help, but neither replaces reviewing new escape hatches.
