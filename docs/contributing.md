# Growing the guide

[Project overview and reading path](../README.md)

Keep `README.md` as the project introduction, reading path, and quick start.
Put detailed guidance in the relevant page under `docs/`. For a new topic, add a
focused page and link it from the entry point. Cross-page references should use
relative filenames and heading anchors rather than references to numbered sections.

Add independent sections using this structure:

1. A concrete API or data-model mistake and a small example. Use familiar
   application scenarios for foundations; explain any domain knowledge needed by
   ML or other specialist applications.
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

Write for a reader who has not followed the project's discussions. Explain the
problem before prescribing a pattern, define unfamiliar terminology, and separate
design principles from the reference tool stack. Keep development history in the
changelog; turn past bugs into lasting lessons rather than review narratives.
The detailed chapter owns the rationale. Keep the checklist and agent entry points
short, linking to that chapter instead of repeating its full policy.

Every failure example needs a recovery contract. Use typed outcomes when callers
can retry, correct input, or reject a record and continue. For raising examples,
state why that operation must unwind. A `Raises:` docstring alone does not expose
a recoverable failure to the checker. See [errors and absence](errors-and-absence.md).

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
version requirements, project dependencies, and lockfile together.

## Build the book and skill

`docs/` remains the chapter source, and `docs/SUMMARY.md` defines reading order.
Add new chapters to that list; tests require every topic page to appear.
`skills/rustic-python/SKILL.md` is the short agent entry point. Its references are
bundled automatically from the chapters and executable examples.

```sh
just check          # Lint, type-check, and test the guide and distributions
just book           # Prepare sources, obtain mdBook, and build the HTML book
just serve          # Build sources and preview the book in your browser
just bundle         # Build the portable skill and ZIP without downloading mdBook
```

The build uses upstream mdBook binaries on macOS and Linux and keeps them under
ignored `build/tools/`. Output goes to `build/book/`; the skill goes to
`build/skills/rustic-python/`. Generated copies are never edited or committed.
After editing source chapters, restart `just serve` to refresh its staged input.
Build from a Git checkout: skill bundles record its HEAD, dirty state, and file
hashes in `rustic-python-source.json`. Dirty local builds are usable previews,
but must not be described as an exact published revision. Build from a clean,
stable checkout when producing a distributable snapshot.
The fixture diagram uses Mermaid from a CDN; when unavailable, its source remains
visible. The installed skill's references do not require network access.

The GitHub Actions workflow runs checks and builds on pull requests and pushes
to `main`. Only successful builds on `main` deploy to GitHub Pages. The ZIP is
included in the site and uploaded as a workflow artifact. GitHub Pages must use
GitHub Actions as its publishing source in repository settings. Deployment access
is separate from building the book locally.

Further reading: [Python typing specification](https://typing.python.org/en/latest/spec/),
[Rust enums and pattern matching](https://doc.rust-lang.org/book/ch06-00-enums.html),
and [Rust ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html).
