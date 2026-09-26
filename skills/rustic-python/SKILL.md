---
name: rustic-python
description: Design or review Python type contracts, third-party boundaries, protocols, and pytest tests using practical Rust-inspired patterns. Use for Python type-safety work, especially ML and data pipelines, or when asked to apply the Rustic Python guide.
---

# Rustic Python

Use this guide to prevent concrete mistakes without imitating Rust mechanically.
Respect the target project's supported Python versions, conventions, and tools.
The examples support Python 3.11+. This skill provides guidance, not permission
to install dependencies, replace configuration, or refactor unrelated code.

## Refresh before use

At the start of each task using this skill, check the current `main` revision of
`Red-Eyed/rustic-python` against `rustic-python-source.json` in this installed
folder. Follow [the update workflow](INSTALL.md#check-for-updates-before-use)
with your own network and file tools. Installing this skill opts into refreshing
its reference files; respect explicit pins, local edits, and host permissions.

When outdated, update automatically before reading chapters, then reread the
installed `SKILL.md` and relevant references. Do not ask the user to run update
commands. Check once per task, not before every tool call. If offline or blocked,
use the cached guide and disclose that its freshness was not verified. Never
claim the latest revision without a successful check.

## Workflow

1. Identify the operation, the mistake to prevent, and the relevant boundary.
2. Read the relevant chapter below and its linked examples. Read only what the
   current task needs; do not load the whole book.
3. Choose the simplest representation that preserves the required contract.
   Keep native tensors and arrays; wrappers need a concrete boundary benefit.
   Prefer exceptions for failure propagation; use explicit domain outcomes when
   callers must inspect or collect failures. Generic success/failure may use the
   small custom Ok/Err union, but is not the default for every fallible function.
   Handle variants with structural pattern matching and assert_never; avoid
   a shared result base class, third-party result packages, and unchecked unwrap.
4. Keep `Any` and `object` out of application APIs. Parse serialized external data
   directly with Pydantic; contain unknown SDK values inside adapters that return
   precise types. Load environment configuration with
   pydantic-settings. Build CLIs with its CliApp and typed argument models instead
   of hand-written argparse. Use discriminated unions for tagged payloads. Keep validation
   outside compiled inference; pass tensors and plain NamedTuple/TypedDict records
   to the core. Preserve meaningful failures and absence reasons. Prefer small
   protocols at substitution points and closed unions for exhaustive handling.
5. Verify with the target project's checker and relevant behavioral tests.
   Distinguish static guarantees, runtime validation, and conventions. Report
   checker workarounds with evidence and a removal condition.
6. Keep `getattr`, `setattr`, `hasattr`, `delattr`, and equivalent reflection out
   of application logic. Prefer declared fields, small protocols, explicit variants,
   and typed registries. Permit only documented, localized integration seams or
   tests that require dynamic behavior; recover precise types at that boundary.
   See [dynamic attribute access](docs/third-party-boundaries.md#restrict-dynamic-attribute-access).

## Topic references

All paths are relative to this installed skill, not the user's project.

| Task | Read |
| --- | --- |
| Choose a proportionate design | [Practical choices](docs/practical-choices.md), [benefits and costs](docs/fundamentals.md) |
| Model records and alternatives | [Data modeling](docs/data-modeling.md), [errors and absence](docs/errors-and-absence.md) |
| Add a plugin or extension | [Protocols and composition](docs/oop-and-plugins.md) |
| Preserve state or generic relationships | [State and generics](docs/state-and-generics.md) |
| Integrate untyped libraries | [Third-party boundaries](docs/third-party-boundaries.md) |
| Investigate a checker diagnostic | [Checker limitations](docs/checker-limitations.md) |
| Work with tensors or scientific results | [ML correctness](docs/ml-correctness.md) |
| Design tests and fixtures | [pytest practices](docs/testing.md) |
| Evaluate helper libraries | [Supplementary libraries](docs/libraries.md) |
| Configure static checks | [Tooling](docs/tooling.md) |

## Configuration templates

`pyrefly.toml`, `ruff.toml`, and `pytest.ini` are reference templates. Inspect
existing project settings first and propose a minimal merge when requested.
Never overwrite a project's settings just to make it resemble this tutorial.
The bundled `pyproject.toml` and `uv.lock` describe the tutorial's tested
environment; they are not dependency requirements for the user's application.

Examples and tests are local reference material and remain usable offline.
The guide does not establish ownership, tensor shapes, numerical correctness,
or freedom from exceptions merely because a type checker accepts a program.
