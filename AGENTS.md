# AGENTS.md

This file provides guidance to Codex when working with code in this repository.

## Project overview

Rustic Python is a living guide to catching Python API and data-model mistakes
before execution. It is general purpose with an ML and data science bias, targets
Python 3.11+, and serves both engineers and coding agents. It does not provide
Rust's ownership, borrow checking, or scientific correctness guarantees.

Pyrefly is the static type checker; Ruff checks and formats code; uv manages the
environment and lockfile. pytest verifies runtime behavior and the guide's static
claims. Expression demonstrates library-provided result types; more-itertools
demonstrates iterator utilities. Neither is a mandatory design style.

A *boundary* is where untrusted or untyped values enter typed code. A *sum type*
is a closed union of alternatives. A *protocol* describes the small structural
interface a caller needs. A *rejected case* is a commented invalid statement whose
expected checker diagnostics are verified by the test harness.

## Development commands

Run from the repository root. Use uv for all Python commands; `uv run --locked`
provisions the configured dependency groups automatically.

```sh
uv run --python 3.11 --locked pytest  # Verify the minimum supported Python version
uv run --locked pytest tests/test_guide.py  # Check snippets and static guarantees
uv run --locked pytest tests/test_practical_defaults.py::test_batch_policy  # Focus a test
uv run --locked ruff check .  # Check code and configured lint rules
uv run --locked ruff format .  # Format; reread any changed files
uv run --locked pyrefly check  # Check the entire project using strict settings
uv run --locked python examples/plugin_composition.py  # Run one independent example
```

Before committing, run Ruff check, Ruff format, Pyrefly, and pytest. Keep the
manifest and lockfile versions synchronized when updating the project version.
There is no hosted CI workflow; do not imply local checks run on GitHub.

## Architecture and verification

This is a documentation project with independent executable lessons, not a shared
runtime framework. Keep README.md as the entry point and put detailed lessons in
`docs/`. `docs/agent-guide.md` contains portable advice for readers' projects;
this file contains instructions for maintaining this repository.

`pyproject.toml` defines dependencies and pytest discovery. `pyrefly.toml` and
`ruff.toml` define strictness and required tool versions. Tool upgrades must update
these files, `uv.lock`, and the verified baseline in `docs/tooling.md` together.

Examples express separate contracts: `Transform` demonstrates substitution and
composition; fitted/unfitted centerers demonstrate state transitions; third-party
adapters convert unknown data into validated records or explicit failure variants.
Keep side effects at boundaries and use injected dependencies where substitution
is part of the lesson. Do not introduce a common base class across lessons.

`tests/test_guide.py` discovers examples, runs them independently, checks passing
types, and activates each rejected statement in a temporary copy. It checks the
diagnostic kinds and locations, so an unrelated error is not a passing result.
It also compares linked Python fences in README.md and `docs/*.md` with their
source files. Temporary checker inputs and simulated vendor stubs belong in
pytest's temporary directories, not committed example code.

## Adding or changing a lesson

- Read `docs/contributing.md` and `docs/agent-guide.md` first. Explain a concrete
  mistake, the static guarantee, runtime obligations, edge cases, and when a
  simpler representation is acceptable.
- Keep each example self-contained with all imports, documented contracts, and
  at least one `# rejected[diagnostic-kind]: invalid_statement` line. Use commas
  between multiple expected diagnostic kinds.
- Link the complete source immediately before its Python fence using
  `[Source](../examples/name.py)`. Update source and documentation together; avoid
  duplicate source excerpts across pages.
- Pytest lessons live in `tests/pytest_patterns/`, including their local
  `conftest.py`. Link their complete sources too. They are collected as tests and
  do not need artificial rejected statements.
- Preserve Python 3.11 syntax: use `TypeVar`, `Generic`, and `TypeAlias` where
  needed, rather than Python 3.12 type-parameter syntax.
- Prefer precise records for known schemas. Validate unknown inputs once at the
  boundary. Keep native arrays and tensors in numerical code; nominal wrappers
  need a demonstrated benefit, not resemblance to Rust.
- Use small protocols at real extension points, composition for added behavior,
  and exhaustive matching for closed unions. Do not manufacture abstractions for
  ordinary pure functions.
- Test runtime contracts through observable behavior. Compose fixtures through
  fixture arguments; keep shared fixtures in the nearest `conftest.py`. Cover
  invalid data and relevant numeric edge cases, not only happy paths.
- For a checker defect, preserve a minimal reproduction, runtime evidence,
  affected tool version, and removal condition. Keep suppressions narrow and
  tested; never relax project strictness to hide one diagnostic. Consult
  `docs/checker-limitations.md` before changing a workaround.
- Describe guarantees as statically checked, runtime validated, or convention
  only. Passing type checks do not establish tensor shapes, finiteness, ownership,
  absence of exceptions, or correct training behavior.
- Record user-visible changes under `[Unreleased]` in `CHANGELOG.md`. Do not
  invent release dates or published versions. Commit messages must contain an
  imperative title, concrete change bullets, and a paragraph explaining why.
