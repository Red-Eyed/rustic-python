# Handle a checker defect locally

[Project overview and reading path](../README.md)

A boundary receives an unknown mapping. Valid Python extracts a text field, but
Pyrefly 1.3.1 rejects its mapping pattern. The goal is to isolate the checker defect
without weakening the application's checks.

**Reproduction**

```python,ignore
def record_name(payload: object) -> str:
    match payload:
        case {"name": str(name)}:
            return name.strip()
    raise ValueError("expected a text name field")
```

For `{"name": " training "}`, Python returns `"training"`. The pinned checker
reports `not-callable` at the case, referring to `__getitem__` and `Never`.
The `object` parameter isolates an unknown-library boundary; it is not a suggested
application record type.

**Scoped repair**

```python,ignore
def record_name(payload: object) -> str:
    match payload:
        # Pyrefly 1.3.1 mapping-pattern defect; remove once fixed.
        # pyrefly: ignore[not-callable]
        case {"name": str(name)}:
            return name.strip()
    raise ValueError("expected a text name field")
```

Only the reproduced diagnostic is suppressed. Unrelated bad assignments remain
errors. The verification suite checks both facts on temporary inputs, along with
the runtime result. An upgrade fixing the defect must trigger removal of the workaround.

Prefer a supported annotation or guard when it expresses the same contract clearly.
Do not change accepted inputs, error behavior, or coercion just to satisfy one
checker version. A suppression needs runtime evidence and a removal condition;
unknown external schemas still need [validation](data-modeling.md).
