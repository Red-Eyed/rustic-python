---
name: rustic-python
description: Design or review Python type contracts, third-party boundaries, protocols, and pytest tests using practical Rust-inspired patterns. Use for Python type-safety work, especially ML and data pipelines, or when asked to apply the Rustic Python guide.
---

# Rustic Python

Use this guide to prevent concrete mistakes without imitating Rust mechanically.
Respect the target project's supported Python versions, conventions, and tools.
The examples support Python 3.11+. This skill provides guidance, not permission
to install dependencies, replace configuration, or refactor unrelated code.

## Workflow

1. Identify the operation, the mistake to prevent, and the relevant boundary.
2. Read the relevant chapter below and its linked examples. Read only what the
   current task needs; do not load the whole book.
3. Choose the simplest representation that preserves the required contract.
   Keep native tensors and arrays; wrappers need a concrete boundary benefit.
4. Validate unknown data at entry points. Preserve meaningful failure and absence
   information. Prefer small protocols at real substitution points and closed
   unions when alternatives must be exhaustively handled.
5. Verify with the target project's checker and relevant behavioral tests.
   Distinguish static guarantees, runtime validation, and conventions. Report
   checker workarounds with evidence and a removal condition.

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
