# Growing the guide

[Project overview and reading path](../README.md)

This appendix is for maintaining the book. Readers do not need its tools or commands.

Keep `README.md` as the project introduction and reading path.
Put detailed guidance in the relevant page under `docs/`. For a new topic, add a
focused page and link it from the entry point. Cross-page references should use
relative filenames and heading anchors rather than references to numbered sections.

Add independent sections using this structure:

1. Before/after code showing one concrete mistake. Prefer a short diff of changed
   lines, followed by the complete improved implementation. Replace the prose
   description of the mistake with this comparison.
2. A brief “why better”: identify the misuse previously possible at runtime and
   the exact operation the checker now rejects. Label runtime-only improvements
   honestly. The complete snippet includes all imports and its contract.
3. A nearby `# rejected[diagnostic-kind]:` example that isolates the promised static
   rejection. Separate multiple expected kinds with commas.
4. A precise statement of the static guarantee, with the rejected operation,
   diagnostic category, and reason visible on the page.
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
Keep one explanation and one useful example per idea. Remove repeated policy
reminders, chapter summaries, and background that does not change a decision.
Use realistic domains for type distinctions, such as customer and order IDs.
Keep numerical APIs on native tensors; do not manufacture tuple-based softmax
implementations or nominal tensor wrappers to make a typing point.
The detailed chapter owns the rationale. Keep the checklist and agent entry points
short, linking to that chapter instead of repeating its full policy.

The book must be understandable without cloning the repository, installing
Python, or opening a terminal. Show the relevant input, resulting value or
failure, and explanation alongside each example. Source links provide optional
provenance; they must not contain the only explanation or result. Never ask readers
to run or uncomment code to discover the lesson. Keep setup and verification
commands in this contributor appendix.

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

## Verify the maintained examples

Contributors use uv from the repository root. The lockfile supplies the tested
environment; the project itself is not an installable runtime library.

```sh
uv run --python 3.11 --locked pytest
uv run --locked pyrefly check
uv run --locked ruff check .
uv run --locked ruff format --check .
```

These checks verify the examples, intended static rejections, and correspondence
between source and book listings. Keep the checker and editor environments aligned
when investigating a difference. Ruff's formatting check is read-only; formatting
changes must be reviewed before committing.

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
