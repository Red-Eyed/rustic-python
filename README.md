# Rustic Python

**Catch Python API mistakes before execution with precise types and explicit contracts.**

[Read the book](https://red-eyed.github.io/rustic-python/) ·
[Install in Codex, Claude Code, or Cline](docs/codex.md)

Suppose a configuration contains `workers`, but a caller reads `worker_count`.
A precise record lets a type checker reject that mistake before the application
starts. The same approach can expose an unhandled failure or a method called in
the wrong state.

This guide is for Python developers who want stronger contracts in libraries,
services, CLIs, and data pipelines. You should be comfortable with functions,
classes, and basic annotations such as `name: str`. No Rust or machine-learning
experience is required. The examples support Python 3.11+ and introduce typing
concepts as they are needed; later lessons apply them to ML and scientific code.

Read it as a book: the code, relevant results, and checker rejections are shown
on the page. No Python installation, terminal, or repository clone is needed.

Python remains dynamic. These patterns improve its contracts without providing
Rust's ownership, borrow checking, or a proof of numerical correctness.

## Start here

Read [principles, benefits, and costs](docs/fundamentals.md) for the motivation,
concrete before/after examples, and tradeoffs. Then learn to model records and
failure outcomes before moving to larger APIs. This is also the book's reading order:

| Topic | What you will learn |
| --- | --- |
| [How to read the examples](docs/tooling.md) | Passing cases, checker rejections, runtime results, and the limits of each guarantee |
| [Modeling data](docs/data-modeling.md) | Validated records, Pydantic discriminated unions, exhaustive matching, and nominal-type tradeoffs |
| [Errors and absence](docs/errors-and-absence.md) | Custom Ok/Err unions, exhaustive handling, and reason-carrying missing values |
| [OOP, protocols, and plugins](docs/oop-and-plugins.md) | Composition, small interfaces, registries, wrappers, and extensions |
| [State, generics, and immutability](docs/state-and-generics.md) | Fitted/unfitted APIs, generics, pydantic-settings, and mutation limits |
| [Untyped third-party boundaries](docs/third-party-boundaries.md) | Containing loose dictionaries, unknown outputs, exceptions, and mutation |
| [Edge cases and acceptable simplifications](docs/practical-choices.md) | When plain Python is enough, boundary decisions, and what not to simplify away |
| [Working with checker limitations](docs/checker-limitations.md) | Inference gaps, inaccurate stubs, reproducible bugs, and scoped workarounds |
| [Testing with pytest](docs/testing.md) | conftest, fixture dependency graphs, parametrization, cleanup, and anti-patterns |
| [Tensors and scientific correctness](docs/ml-correctness.md) | Optional scientific applications and guarantees types cannot provide |
| [Supplementary libraries](docs/libraries.md) | more-itertools, validation libraries, and verified limitations |
| [Design and review checklist](docs/checklist.md) | A concise reference for applying what you learned |

Optional appendices cover [agent setup](docs/codex.md),
[maintaining the book](docs/contributing.md), and the [changelog](CHANGELOG.md).

Licensed under the [MIT license](LICENSE).
