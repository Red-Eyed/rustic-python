# Growing the guide

[Project overview and reading path](../README.md)

This appendix is for maintaining the book. Readers do not need its tools or commands.

Keep `README.md` as the project introduction and reading path.
Put detailed guidance in the relevant page under `docs/`. For a new topic, add a
focused page and link it from the entry point. Cross-page references should use
relative filenames and heading anchors rather than references to numbered sections.

Give each concept its own short page in this order:

1. Model a concrete situation and the decision the caller needs to make.
2. Show idiomatic Python for that situation. Use a brief `python,ignore` sketch
   where the point is a conventional pattern, not a complete runnable source file.
   Do not invent strawman use of `object`, `Any`, or `Err` as typical Python.
3. Show the better alternative in a short sketch containing only the contract
   and operation that change. Show a short caller use, including how it handles
   an expected failure or consumes the successful value. Link the complete
   checked source for details.
4. After the sketch, state the observed outcome and why the change helps. Name
   the exact mistake the checker rejects; label runtime improvements honestly.
5. Mention only limits and edge cases that change the design decision. If the
   pattern is checker-specific, record affected versions and removal conditions.

Each complete source needs a `# rejected[diagnostic-kind]:` statement that
isolates each claimed static rejection. Separate multiple kinds with commas.
The `python,ignore` fence highlights a contextual sketch; it does not claim that
the sketch is an independently checked complete listing. Keep the complete source
in the book as a link, without duplicating its full listing in the chapter.

Write for a reader who has not followed the project's discussions. Explain the
problem before prescribing a pattern, define unfamiliar terminology, and separate
design principles from the reference tool stack. Keep development history in the
changelog; turn past bugs into lasting lessons rather than review narratives.
Keep one explanation and one useful example per idea. Remove repeated policy
reminders, chapter summaries, and background that does not change a decision.
Do not wrap ordinary identifiers in nominal types solely to demonstrate typing.
Prefer clear names and keyword arguments; require a demonstrated recurring
mix-up before adding distinct types.
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
a recoverable failure to the checker. See [Result and match](errors-and-absence.md).

Put the executable source in `examples/` and link it below its sketch with
`[Source](../examples/name.py)`. Paths in documentation links are relative to
their page; shell commands run from the repository root. The tests discover
these files and reject missing or unlinked copies. Each module must contain at
least one rejected case. `uv run --locked pytest` checks independence, runtime
execution, and the marked negative examples. Add behavioral tests when a lesson
relies on runtime validation rather than static types alone.

Pytest lessons instead belong under `tests/pytest_patterns/`, with links to both
test modules and `conftest.py`. They are collected by pytest rather than run as
independent scripts, and do not need artificial static-rejection lines.
The source-link check discovers `README.md` and every Markdown page under
`docs/`, and covers both kinds of examples without duplicating source excerpts.

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

These checks verify the examples, intended static rejections, and book source
links. Keep the checker and editor environments aligned when investigating a
difference. Ruff's formatting check is read-only; formatting changes must be
reviewed before committing.

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
The installed skill's references do not require network access.

The GitHub Actions workflow runs checks and builds on pull requests and pushes
to `main`. Only successful builds on `main` deploy to GitHub Pages. The ZIP is
included in the site and uploaded as a workflow artifact. GitHub Pages must use
GitHub Actions as its publishing source in repository settings. Deployment access
is separate from building the book locally.

Further reading: [Python typing specification](https://typing.python.org/en/latest/spec/),
[Rust enums and pattern matching](https://doc.rust-lang.org/book/ch06-00-enums.html),
and [Rust ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html).
