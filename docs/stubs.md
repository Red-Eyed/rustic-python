# Correct an inaccurate stub

[Project overview and reading path](../README.md)

A dependency returns the output name `"embedding"`, but its type stub says the return value is an integer.

**Typical Python**

```text
# vendor.pyi
def output_name() -> int: ...

# caller
name: str = output_name()
```

The checker reports `bad-assignment` even though the runtime result is a string.

**Alternative**

```text
# corrected vendor.pyi
def output_name() -> str: ...

# unchanged caller
name: str = output_name()
```

The same caller is now accepted. Repairing the dependency contract preserves
both runtime behavior and meaningful static checking.

Base the correction on verified behavior of the supported version. Keep local
stubs in the project's configured search path, preserving the API surface in use.
Do not claim an unknown payload is a trusted record just to silence a diagnostic;
validate it at a [boundary](third-party-boundaries.md).
