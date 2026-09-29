# Untyped third-party boundaries

[Project overview and reading path](../README.md)

## Contain untyped third-party code

```diff
- prediction = sdk.predict({"instances": [0.2, 0.8]})
- confidence = prediction["confidence"]
+ outcome = bind_vendor(sdk.predict)(PredictRequest(features=(0.2, 0.8)))
+ confidence = outcome.confidence
```

**Why better:** an untyped response lets the caller assume success. The adapter
returns `Prediction | CallFailed | InvalidResponse`, so direct `.confidence`
access is rejected as `missing-attribute` until the caller narrows the outcome.
Malformed vendor data still requires runtime validation; the checker protects
how application code uses the validated outcome.

The adapter below copies the request payload, contains the vendor call, and
validates finite confidence in `[0, 1]`. It rejects `"0.8"`, `True`, `NaN`, and
`1.1`; strict float validation accepts integer endpoints `0` and `1`.

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


def bind_vendor(candidate: object) -> Predictor:
    """Adapt a dynamic SDK callable to typed outcomes; reject noncallable bindings.

    Only this integration seam accepts an unknown dependency. Callability cannot
    prove its signature; argument mismatches become ordinary call failures.
    """
    if not callable(candidate):
        raise TypeError("vendor predict must be callable")

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
vendor = bind_vendor(demo_vendor)
outcome = vendor(request)
summary = describe(outcome)
# rejected[bad-argument-type]: vendor({"instances": [0.2, 0.8]})
# rejected[missing-attribute]: confidence = outcome.confidence
# rejected[bad-typed-dict-key]: payload: VendorPayload = {"features": [0.2]}
# rejected[bad-return]: def unchecked(request: PredictRequest) -> PredictOutcome: return {"label": "positive", "confidence": 0.8}
```

**Static guarantee:** callers use `PredictRequest`, not arbitrary dictionaries,
and cannot access a prediction's confidence until they handle the failure variants.
The vendor payload itself has a checked schema. Application logic consumes only
the adapter's explicit outcomes.

**The unavoidable untyped seam:** `bind_vendor` accepts `object` so a dynamically
obtained `client.predict` or module attribute can be passed into it. `callable`
proves only that it can be called somehow, not that it accepts this payload. The
returned `Predictor` accepts only `PredictRequest` and returns `PredictOutcome`.
The unknown result exists only inside the wrapper and its private validator.
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

`Prediction` validates ordinary construction too. `model_construct` bypasses
validation; `revalidate_instances="always"` ensures the adapter checks existing
instances again. `_parse_response` translates only Pydantic `ValidationError`;
programming defects in validation are not ordinary vendor failures.
`hide_input_in_errors` keeps raw values out of the string returned here, but it
is not general redaction: field names and custom error messages can still reveal
information, and structured errors can contain inputs. Apply logging policy at
the caller.
The dynamically bound SDK is always validated. A separate implementation of
`Predictor` must honor the same outcome contract; static compatibility alone
cannot prove its runtime behavior.

### Missing types versus incorrect types

| Dependency problem | Boundary strategy |
| --- | --- |
| No annotations or a return type of `Any` | Contain unknown values inside the SDK adapter and return validated outcomes |
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

## Restrict dynamic attribute access

```diff
- retries = getattr(config, "retrise", 3)
+ retries = config.retrise
```

**Why better:** for a typed config declaring `retries`, the typo previously selected
`3` silently. Direct access is rejected as `missing-attribute`; the correct access
is `config.retries`. Keep defaults in the declared model.

Restrict `getattr`, `setattr`, `hasattr`, `delattr`, and equivalent reflection to
necessary adapters or tests. Use these replacements in application logic:

| Dynamic pattern | Prefer |
| --- | --- |
| Read or write a known field by name | Direct attribute access or construction of a new typed value |
| Probe an object's methods with `hasattr` | A small protocol for required capabilities, or explicit union variants when capabilities differ |
| Select a handler using `getattr(component, mode)` | An explicit registry of typed callables, with a defined unknown-key outcome |
| Copy arbitrary input keys into attributes | Pydantic validation into a declared schema at the boundary |
| Delete a field to indicate a state change | A distinct state or a typed absence value when appropriate |

`hasattr` establishes neither a method's signature nor its behavioral contract.
A fallback value does not repair an unknown schema, and a dynamic write can erase
the relationship between a declared field and its permitted value type. Do not
add `__getattr__`, `__getattribute__`, `__setattr__`, or `__delattr__` merely to make
undeclared application attributes appear valid.

Reflection is permitted only when it serves a concrete boundary requirement,
such as adapting a third-party framework, or when a test deliberately exercises
dynamic behavior. Keep it in the smallest adapter or test, document why explicit
access cannot serve that purpose, validate external data with Pydantic, and
expose precise types to callers. Do not spread capability probes across consumers.
The [frozen-settings test](../tests/test_behavior.py) deliberately uses `setattr`
to verify runtime rejection of mutation; that is a justified test operation.

This is a design and review policy, not a claim that static typing forbids all
reflection. Checkers may understand some literal attribute names; dynamic names
can still lose useful information. Python frameworks can legitimately implement
dynamic APIs, but that does not require application code to adopt those APIs
throughout its typed core.

## Escape hatches and dependency boundaries

| Shortcut | What it loses | Preferred response |
| --- | --- | --- |
| `Any` | Checking of operations and assignments involving that value | A precise schema or protocol; validate unknown SDK values inside the adapter |
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

`object` is permitted only at unavoidable library seams such as this dynamic SDK
binding. It must not become an application parser signature or a downstream return
type. If the external representation is JSON text, use `model_validate_json` or
`TypeAdapter.validate_json` directly, without an untyped decoded intermediate.

When an upstream stub is wrong, prefer a corrected stub or a small documented
adapter. A necessary suppression should identify the exact diagnostic, explain the
upstream mismatch, and have a removal condition. Never weaken the project-wide
configuration merely to make one integration green. Ruff's suppression rules and
Pyrefly's unused-ignore check help, but neither replaces reviewing new escape hatches.
