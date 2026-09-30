# Narrowing through a predicate

[Project overview and reading path](../README.md)

A helper recognizes nonempty text in a `str | int` value. Its caller wants to strip the text after the check.

**Typical Python**

```python,ignore
def is_nonempty_text(value: str | int) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalize_name(value: str | int) -> str:
    if is_nonempty_text(value):
        return value.strip()
    raise ValueError("name must be nonempty text")


name = normalize_name(7)
```

The checker rejects `.strip()` because a plain `bool` return does not tell it
which type the predicate recognized. For `7`, the caller also gets an unannounced
`ValueError` at runtime.

**Alternative**

```python,ignore
def is_nonempty_text(value: str | int) -> TypeGuard[str]:
    return isinstance(value, str) and bool(value.strip())


def normalize_name(value: str | int) -> str | InvalidName:
    if is_nonempty_text(value):
        return value.strip()
    return InvalidName(value)


outcome = normalize_name(" training ")
match outcome:
    case str() as name:
        normalized = name
    case InvalidName():
        normalized = "rejected"
    case _:
        assert_never(outcome)
```

The failure is a typed outcome as in [Result and match](errors-and-absence.md).

[Source](../examples/checker_limits.py)

`TypeGuard[str]` communicates the narrowing. `normalize_name(" training ")`
returns `"training"`, and the checker accepts `.strip()` in the guarded branch.
The return type also forces callers to distinguish `InvalidName` before calling
string methods. For a single use, an inline type check may be simpler.

The checker trusts the guard's author; it does not prove the predicate correct or
encode nonemptiness in `str`. Invalid input returns `InvalidName`; external schema
validation belongs at a [boundary](data-modeling.md).
