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

```python,ignore
PredictOutcome = Prediction | CallFailed | InvalidResponse


def invoke(request: PredictRequest) -> PredictOutcome:
    payload = encode_request(request)
    try:
        response: object = candidate(payload)
    except Exception as error:
        return CallFailed(error)
    return _parse_response(response)
```

The adapter owns the uncertain call and validates its response. Its typed
failure variants follow [Result and match](errors-and-absence.md); the complete
example also handles binding a dynamically discovered callable.

[Source](../examples/third_party_boundary.py)

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
