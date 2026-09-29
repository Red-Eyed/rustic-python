# Fixture lifetimes and cleanup

[Project overview and reading path](../README.md)

A test reads a file through a fixture. The file must close even if setup or the assertion fails.

**Typical Python**

```text
stream = path.open()
assert read_value(stream) == expected
stream.close()
```

A failed assertion skips `close()`. Cleanup depends on the test reaching its final line.

**Alternative**

```text
@pytest.fixture
def sample_stream(sample_file):
    with sample_file.open(encoding="utf-8") as stream:
        yield stream
```

The context manager closes the stream when pytest finishes using the fixture,
including after a test failure. This is a runtime lifetime guarantee; annotations
alone cannot establish cleanup.

Use function scope unless sharing is safe and useful. Shared mutable models,
iterators, or transactions can leak state between tests. For partial setup failures,
protect each acquired resource with a context manager or registered finalizer;
code after an unreached `yield` will not run. The [fixture lesson](fixtures.md)
contains the complete file example.
