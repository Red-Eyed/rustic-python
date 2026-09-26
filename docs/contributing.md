# Growing the guide

[Project overview and reading path](../README.md)

Keep `README.md` as the project introduction, reading path, and quick start.
Put detailed guidance in the relevant page under `docs/`. For a new topic, add a
focused page and link it from the entry point. Cross-page references should use
relative filenames and heading anchors rather than references to numbered sections.

Add independent sections using this structure:

1. An actual ML mistake and a small concrete example.
2. A self-contained passing snippet with all imports and documented contracts.
3. A nearby `# rejected[diagnostic-kind]:` example that isolates the promised static
   rejection. Separate multiple expected kinds with commas.
4. A precise statement of the static guarantee.
5. Runtime validation requirements, limitations, and relevant performance costs.
6. Relevant edge cases and the chosen behavior for each, backed by tests where the
   lesson makes a guarantee. Distinguish unimplemented application concerns from
   cases actually covered by the example.
7. An acceptable simpler alternative, when it applies, and the trigger for needing
   the stronger pattern. Do not present an elaborate representation as a universal
   default.
8. If a workaround is checker-specific, record a minimal reproduction, affected
   versions, runtime evidence, and a removal condition. Keep normal application
   examples free of broad suppressions.

Put the executable source in `examples/` and link it immediately before its
documentation fence using `[Source](../examples/name.py)`. Paths in documentation
links are relative to their page; shell commands run from the repository root.
The tests discover these files and reject
missing, stale, or unlinked copies. Each module must contain at least one rejected
case. `uv run --locked pytest` automatically checks independence, runtime execution,
and the marked negative examples. Add behavioral tests when a new lesson relies on
runtime validation rather than static types alone.

Pytest lessons instead belong under `tests/pytest_patterns/`, with linked source
fences for both test modules and `conftest.py`. They are collected by pytest rather
than run as independent scripts, and do not need artificial static-rejection lines.
The synchronization check discovers `README.md` and every Markdown page under
`docs/`, and covers both kinds of snippets without duplicating source excerpts.

For tool upgrades, recheck the config files and examples together, then update the
version requirements, project dependencies, and lockfile together. The current
automation runs locally through pytest; no hosted CI workflow is included yet.

Further reading: [Python typing specification](https://typing.python.org/en/latest/spec/),
[Rust enums and pattern matching](https://doc.rust-lang.org/book/ch06-00-enums.html),
and [Rust ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html).
