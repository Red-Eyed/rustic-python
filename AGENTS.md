# AGENTS.md

This file provides guidance to Codex when working with code in this repository.

## Project overview

Rustic Python is a living guide to making type-checkable Python mistakes fail
static checks before execution. It targets Python 3.11+ and teaches general application contracts
before applying them to ML and scientific code. Readers need basic Python, not
Rust or ML experience; separate reader, agent, and contributor workflows. It does not provide
Rust's ownership, borrow checking, or scientific correctness guarantees.

The reader experience is a self-contained book. Show code, relevant values,
checker rejections, and their explanations directly in the chapters. Never require
readers to clone, install Python, open a terminal, or execute/uncomment an example.
Lead lessons with a concrete situation, idiomatic Python, the alternative, then
the specific mistake now rejected by the type checker. Label runtime-only
improvements honestly. Replace prose with
focused comparisons; avoid duplicate explanations. Source links are optional
provenance; maintenance commands belong in the contributor
appendix, and agent installation belongs in its optional appendix.

Pyrefly is the static type checker; Ruff checks and formats code; uv manages the
environment and lockfile. pytest verifies runtime behavior and the guide's static
claims. Use typed outcomes for recoverable failures and exceptions when an
operation has no supported recovery path and must unwind. Convert recoverable
library errors at boundaries; keep broken internal assumptions visible. A Result
annotation does not prove that unexpected exceptions cannot escape. The Result lesson
uses small custom frozen Ok and Err dataclasses with a union alias, not a shared
result base class or a third-party result package. Handle variants
with structural pattern matching and assert_never; do not add unchecked unwrap
methods.

A *boundary* is where untrusted or untyped values enter typed code. A *sum type*
is a closed union of alternatives. A *protocol* describes the small structural
interface a caller needs. A *rejected case* is a commented invalid statement whose
expected checker diagnostics are verified by the test harness.

## Development commands

Run from the repository root. Use uv for all Python commands; `uv run --locked`
provisions the project's dependencies automatically.

```sh
uv run --python 3.11 --locked pytest  # Verify the minimum supported Python version
uv run --locked pytest tests/test_guide.py  # Check source links and static guarantees
uv run --locked pytest tests/test_behavior.py::test_undefined_precision_differs_from_zero  # Focus a test
uv run --locked ruff check .  # Check code and configured lint rules
uv run --locked ruff format .  # Format; reread any changed files
uv run --locked pyrefly check  # Check the entire project using strict settings
uv run --locked python examples/plugin_composition.py  # Run one independent example
```

Before committing, run Ruff check, Ruff format, Pyrefly, and pytest. Keep the
manifest and lockfile versions synchronized when updating the project version.
`.github/workflows/book.yml` runs checks and builds on pull requests and main;
successful main builds deploy through GitHub Pages once Pages is enabled.

## Architecture and verification

This is a documentation project with independent executable lessons, not a shared
runtime framework. Keep README.md as the entry point and put detailed lessons in
`docs/`. `docs/agent-guide.md` contains portable advice for readers' projects;
this file contains instructions for maintaining this repository.

`docs/SUMMARY.md` is the book reading order. `just book` stages maintained sources
and builds mdBook; `just bundle` builds the portable agent skill from the same
chapters. `skills/rustic-python/SKILL.md` is its entry point. `tools/` contains
distribution tooling, not tutorial examples, so it does not need rejected cases.
Never edit generated `build/` copies or include this maintenance AGENTS.md in the
installed skill. `just install-skill` links the bundle locally and rejects
conflicting installations. Test changes through temporary destinations.

`INSTALL.md` is the agent-readable installation entry point for Codex, Claude
Code, and Cline. Keep its host locations grounded in official documentation.
The primary reader flow is a link given to the agent, which installs the ready-made
ZIP; local build tools are only needed by contributors.
Bundles include `rustic-python-source.json` with the source revision, dirty state,
and file inventory hashes. The skill checks GitHub before each task and follows
INSTALL.md for refresh, Pages-lag fallback, and preservation of local edits.
Keep this workflow agent-operated; do not add a background updater or install
application dependencies just to refresh reference material.

`pyproject.toml` defines dependencies; `pytest.ini` defines pytest settings and
discovery. `pyrefly.toml` and
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
It checks that every example is linked once from README.md or `docs/*.md`.
Temporary checker inputs and simulated vendor stubs belong in pytest's temporary
directories, not committed example code.

## Adding or changing a lesson

- Read `docs/contributing.md` and `docs/agent-guide.md` first. Explain a concrete
  mistake, the static guarantee, runtime obligations, edge cases, and when a
  simpler representation is acceptable.
- Keep each example self-contained with all imports, documented contracts, and
  at least one `# rejected[diagnostic-kind]: invalid_statement` line. Use commas
  between multiple expected diagnostic kinds.
- Show a short `python,ignore` sketch of the relevant alternative, then link the
  complete checked source with `[Source](../examples/name.py)`. The book bundles
  those source files, so readers need no clone. Update sketches and source
  together; do not duplicate entire source listings in chapter pages.
- If adding a pytest lesson, keep its tests and local `conftest.py` under
  `tests/pytest_patterns/`. Link their sources; pytest lessons do not need
  artificial rejected statements.
- Preserve Python 3.11 syntax: use `TypeVar`, `Generic`, and `TypeAlias` where
  needed, rather than Python 3.12 type-parameter syntax.
- Prefer precise records for known schemas. Validate unknown inputs once at the
  boundary using Pydantic; use pydantic-settings for environment configuration
  and CLIs. Build command interfaces with CliApp and typed argument models,
  not hand-written argparse. Keep CLI parsing and output at the entry point.
  Use discriminated unions for tagged external alternatives. Keep validation and
  model construction outside compiled inference; use native tensors and plain
  NamedTuple/TypedDict records there. Internal dataclasses and algorithm guards
  remain appropriate. Keep native arrays and tensors in numerical code. Do not demonstrate
  numerical APIs with tuple-based stand-ins or nominal Logits/Probabilities wrappers;
  use realistic domains such as distinct identifiers to teach nominal types.
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
- Keep `CHANGELOG.md` commit-based: newest first, with an actual commit link,
  its Git date, and concrete user-visible changes. Do not add an `Unreleased`
  section or invent commit hashes. Record a change once its commit exists;
  changelog-only bookkeeping does not need its own entry. Commit messages contain an
  imperative title, concrete change bullets, and a paragraph explaining why.
