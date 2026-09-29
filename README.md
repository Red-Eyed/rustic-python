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

Python remains dynamic. These patterns improve its contracts without providing
Rust's ownership, borrow checking, or a proof of numerical correctness.

## Start here

Read [principles, benefits, and costs](docs/fundamentals.md) for the motivation,
concrete before/after examples, and tradeoffs. Then learn to model records and
failure outcomes before moving to larger APIs. This is also the book's reading order:

| Topic | What you will learn |
| --- | --- |
| [Tooling and strictness](docs/tooling.md) | Python 3.11 support, setup, checker policy, and running examples |
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

The examples use Pyrefly, Pydantic, and pydantic-settings as a consistent reference
stack. Each lesson distinguishes the design principle, what these tools verify,
and what still needs runtime checks. See [tooling](docs/tooling.md) to run your first
example. Reading the guide does not require installing its development environment.

For agent-assisted work, see [instructions for coding agents](docs/agent-guide.md).
To maintain the guide itself, see [contributing](docs/contributing.md).

## Install in your coding agent

Give your agent this message; it handles installation:

```text
Install the Rustic Python skill by reading and following:
https://raw.githubusercontent.com/Red-Eyed/rustic-python/main/INSTALL.md
```

Works with Codex, Claude Code, and Cline. See [agent setup](docs/codex.md) for
invocation examples, project scope, and updates.
The installed skill checks the repository before each task and refreshes its
references automatically. Offline use keeps the cached guide and reports that
freshness could not be verified.

## Contributor checks

From the repository root, uv provisions the locked development and example
dependencies automatically:

```sh
uv run --locked pyrefly check
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest
```

See [tooling](docs/tooling.md) to select Python 3.11 explicitly.

## Repository contents

- [docs/](docs/) — the guide, organized by topic.
- [examples/](examples/) — runnable examples with deliberately invalid lines kept commented.
- [tests/](tests/) — behavioral tests, expected type-error checks, and documentation synchronization.
- [pyrefly.toml](pyrefly.toml) and [ruff.toml](ruff.toml) — reusable strict configurations.
- [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock) — project tooling and pinned dependencies.
- [AGENTS.md](AGENTS.md) — repository-specific instructions for coding agents.
- [CHANGELOG.md](CHANGELOG.md) — user-visible changes to the guide and tooling.

Tests check that documentation snippets match their linked Python source files
and that each deliberately invalid example fails for its intended reason.

Licensed under the [MIT license](LICENSE).
