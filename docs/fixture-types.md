# What fixture annotations check

[Project overview and reading path](../README.md)

A test requests a file stream from a fixture. The fixture yields a stream, while the test receives that stream directly.

**Typical Python**

```text
def test_contents(sample_stream):
    assert sample_stream.read_text() == "2.0\n4.0\n6.0\n"
```

The test confuses a stream with a `Path`: streams have `read()`, not `read_text()`.
Without the parameter annotation, that interface is not declared in the test.

**Alternative**

```text
from collections.abc import Iterator
from typing import TextIO

import pytest

@pytest.fixture
def sample_stream(sample_file) -> Iterator[TextIO]:
    with sample_file.open() as stream:
        yield stream

def test_contents(sample_stream: TextIO) -> None:
    assert sample_stream.read() == "2.0\n4.0\n6.0\n"
```

A nonexistent stream method is now rejected in the test body. The fixture's
annotation describes its iterator; the consumer receives `TextIO`.

Pytest resolves fixtures by name, not annotation. The checker does not prove that
the selected fixture matches the test's annotation, or that every parametrized
value matches its parameter type. Runtime collection and tests still matter.
