# Preserve useful error details

[Project overview and reading path](../README.md)

An importer rejects row 1843. Its caller needs enough information to identify the bad record or diagnose a dependency failure.

**Typical Python**

```python,ignore
rejected = []
for raw in rows:
    try:
        label = int(raw)
    except ValueError as error:
        rejected.append(str(error))
```

The messages explain the parsing failure, but do not identify the source row.
Several identical bad values produce indistinguishable reports.

**Alternative**

```python,ignore
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RejectedRow:
    source: Path
    row: int
    reason: str


rejected: list[RejectedRow] = []
for row, raw in enumerate(rows, start=1):
    try:
        label = int(raw)
    except ValueError as error:
        rejected.append(RejectedRow(source, row, str(error)))
```

The caller receives named, typed fields instead of parsing a message. The checker
can verify access to `row`; it cannot invent provenance or prove that the number
is accurate. This changes the reporting contract; parsing still fails at runtime.
The same record can be the error payload of a [Result](errors-and-absence.md).

For a code-level failure, retaining the caught exception preserves its existing
traceback. `error.add_note(...)` adds context; `traceback.print_exception(error)`
displays it. Returning the exception does not add frames or create a chain.
Tracebacks retain local objects, so prefer compact records for large rejection lists.
