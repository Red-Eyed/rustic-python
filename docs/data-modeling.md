# Validated records

[Project overview and reading path](../README.md)

A worker receives job metadata. Every job needs a name and a positive worker count; downstream code must use the declared field names.

**Typical Python**

```python,ignore
metadata: dict[str, str | int] = {"name": "report", "workers": 4}
workers = metadata["worker_count"]
```

The dictionary annotation allows any string key. This typo survives checking and
raises `KeyError` when the field is read.

**Alternative**

```python,ignore
class JobMetadata(BaseModel):
    name: str
    workers: Annotated[int, Field(ge=1)]


def parse_metadata(payload: str) -> JobMetadata | InvalidMetadata:
    try:
        return JobMetadata.model_validate_json(payload)
    except ValidationError as error:
        return InvalidMetadata(str(error))


outcome = parse_metadata('{"name": "report", "workers": 4}')
match outcome:
    case JobMetadata(workers=workers):
        summary = f"{workers} workers"
    case InvalidMetadata(reason=reason):
        summary = f"rejected: {reason}"
    case _:
        assert_never(outcome)
```

The typed rejection follows the [Result lesson](errors-and-absence.md); this
page focuses on the named record fields.

[Source](../examples/validated_records.py)

For this input, parsing returns `JobMetadata(name="report", workers=4)`. The
checker rejects both a misspelled model field and direct access to `.workers`
on the unhandled `MetadataResult`. Matching narrows the successful branch.

Pydantic validates external JSON at runtime. Nonpositive, boolean, string, and
float worker counts, missing fields, and malformed JSON return `InvalidMetadata`;
extra fields are ignored by this schema. The checker then requires a caller to
distinguish a valid record from that rejection before using its fields.

Direct model construction validates too; `model_construct` and
`model_copy(update=...)` can bypass checks. Validate the actual admission path.
