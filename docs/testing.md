# Test behavior beyond types

[Project overview and reading path](../README.md)

Static types constrain the programs you can write; tests exercise the behavior of
the programs that remain. A centerer that adds its mean instead of subtracting it
can be perfectly well typed. For training values `(2.0, 4.0, 6.0)`, the mean is
`4.0`, so transforming `7.0` must produce `3.0`, not `11.0`. That is a behavioral
assertion, not an assignability check.

Python's dynamic boundaries make this distinction especially important. Rust also
needs tests; neither compiler nor type checker proves an algorithm is correct.
Use pytest for numerical behavior, failure contracts, mutation, resource lifetime,
and integration. Keep static rejection tests for the separate claims about what
Pyrefly prevents.

For the centerer, subtracting the mean produces `3.0`; adding it produces `11.0`.
Both are floats. An assertion against `3.0` distinguishes the correct calculation
where its annotation cannot.

Test the public result with independently chosen expected values. Do not copy
the algorithm into the test or mock the operation being tested. Use a small fake
for an external dependency; keep separate integration checks for the real adapter.
