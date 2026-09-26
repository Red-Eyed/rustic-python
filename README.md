# Rustic Python

**Rust-inspired types and design for Python 3.11+, with an ML and data science bias.**

[Read the book](https://red-eyed.github.io/rustic-python/) ·
[Install the Codex skill](docs/codex.md)

Catch incorrect API calls, missing cases, and invalid state transitions before
running your code. Model uncertainty explicitly, validate external data at the
boundary, and test the behavior that static types cannot establish.

This is a living guide for engineers and LLM coding agents, with runnable examples
and strict Pyrefly/Ruff configurations. The principles apply to libraries, services,
CLIs, and data pipelines; most examples come from ML and data science.

Python remains dynamic. These patterns improve its contracts without providing
Rust's ownership, borrow checking, or a proof of numerical correctness.

## Start here

Read [principles, benefits, and costs](docs/fundamentals.md) for the motivation,
concrete before/after examples, and tradeoffs. Then follow the guide by topic:

| Topic | What you will learn |
| --- | --- |
| [Edge cases and acceptable simplifications](docs/practical-choices.md) | When plain Python is enough, boundary decisions, and what not to simplify away |
| [Working with checker limitations](docs/checker-limitations.md) | Inference gaps, inaccurate stubs, reproducible bugs, and scoped workarounds |
| [Tooling and strictness](docs/tooling.md) | Python 3.11 support, setup, checker policy, and running examples |
| [Modeling data](docs/data-modeling.md) | Precise records, sum types, exhaustive matching, and nominal-type tradeoffs |
| [Errors and absence](docs/errors-and-absence.md) | Explicit results and reason-carrying missing values |
| [OOP, protocols, and plugins](docs/oop-and-plugins.md) | Composition, small interfaces, registries, wrappers, and extensions |
| [State, generics, and immutability](docs/state-and-generics.md) | Fitted/unfitted APIs, preserved type relationships, and mutation limits |
| [Untyped third-party boundaries](docs/third-party-boundaries.md) | Containing loose dictionaries, unknown outputs, exceptions, and mutation |
| [Tensors and scientific correctness](docs/ml-correctness.md) | Static shape support, runtime checks, and guarantees types cannot provide |
| [Testing with pytest](docs/testing.md) | conftest, fixture dependency graphs, parametrization, cleanup, and anti-patterns |
| [Supplementary libraries](docs/libraries.md) | Expression, more-itertools, validation libraries, and verified limitations |

For team workflows, see [instructions for coding agents](docs/agent-guide.md).
For adding or updating material, see [growing the guide](docs/contributing.md).

## Run the checks

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
