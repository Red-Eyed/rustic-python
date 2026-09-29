# Result and match

[Project overview and reading path](../README.md)

An importer reads integer labels. A malformed row should be reported while valid rows continue. The caller needs both the parsed value and a way to recognize rejection.

**Typical Python**

```python,ignore
def parse_label(raw: str) -> int:
    return int(raw)


labels = [parse_label(raw) for raw in ("7", "cat", "2")]
```

The annotation exposes only success. `"cat"` raises `ValueError` at runtime and interrupts the import. Returning `-1` instead would still look like a valid integer to the checker.

**Alternative**

```python,ignore
Result: TypeAlias = Ok[T] | Err[E]


def parse_label(raw: str) -> Result[int, InvalidLabel]:
    try:
        return Ok(LABEL.validate_python(raw))
    except ValidationError:
        return Err(InvalidLabel(raw, "not a nonnegative integer"))


outcome = parse_label("cat")
match outcome:
    case Ok(value=label):
        description = f"class {label}"
    case Err(error=error):
        description = f"rejected {error.raw!r}: {error.reason}"
    case _:
        assert_never(outcome)
```

[Source](../examples/explicit_results.py)

`parse_label("7")` returns `Ok(7)`; `parse_label("cat")` returns an
`Err` carrying the rejected input and reason. `describe_label` uses `match` to
consume either outcome. It produces `"class 7"` or a rejection message.

**Result and match work together:** the union exposes failure, matching narrows
the payload, and `assert_never` checks that no variant is forgotten. Assigning
the result directly to `int`, or reading `.value` before narrowing, is rejected.
A `Raises:` docstring cannot provide that checked contract.

Rust's standard library provides `Result<T, E>` as an enum. Python does not
provide the equivalent, so this example uses an ordinary union of two small
frozen dataclasses, without inheritance or a third-party package. `Ok` and `Err`
give a reusable shape when an operation has one success type and an expected
error. Some later lessons use a direct union such as
`JobMetadata | InvalidMetadata`: naming the domain variants directly keeps
those examples focused. Both designs require narrowing before the success
value is used; `match` plus `assert_never` checks coverage of either closed union.

Use `Result` for supported retry, fallback, correction, or record rejection.
Use exceptions when the operation has no recovery path and must unwind. Translate
specific recoverable library exceptions at the boundary; do not disguise bugs.
Python can still raise unexpected exceptions, and a caller can discard the whole
result. No return annotation proves exception freedom.

The parser accepts nonnegative integer-valued text, including `"7.0"`; it does
not know the dataset's class count. The two frozen variants freeze their own
fields, not mutable payloads. Keep this small union rather than adding a result
framework or unchecked unwrap methods.
