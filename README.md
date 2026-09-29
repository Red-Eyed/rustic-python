# Rustic Python

**Make type-checkable Python mistakes fail static checks before execution.**

[Read the book](https://red-eyed.github.io/rustic-python/)

A misspelled record field, an unhandled failure, or a method called before setup
can become a type-checking error. Logic and numerical correctness still need tests.

Each page covers one concept: a situation, typical Python code, a better
alternative, and why it helps. Examples and their results are visible on the page.
No cloning, Python installation, or terminal is needed.

The book assumes familiarity with Python functions, classes, and basic annotations.
It uses Python 3.11+ and requires no Rust or machine-learning background.

## Start reading

Begin with [the goal](docs/fundamentals.md) and [example notation](docs/tooling.md).
[Result and match](docs/errors-and-absence.md) shows how a recoverable error
becomes a checked outcome. Then follow [validated records](docs/data-modeling.md),
[variants](docs/variants.md), and [exhaustive matching](docs/exhaustive-matching.md).

Later pages cover state, protocols, external boundaries, and checker limitations.

Optional references cover [agent setup](docs/codex.md),
[contributing](docs/contributing.md), and the [changelog](CHANGELOG.md).

Licensed under the [MIT license](LICENSE).
