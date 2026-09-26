# Tooling and strictness

[Project overview and reading path](../README.md)

The guide and all examples target **Python 3.11+**. Boundary lessons use Pydantic
and pydantic-settings; supplementary lessons use Expression and more-itertools.
The lockfile pins the tested environment. Small tuples stand in for model outputs and feature vectors so the
lessons do not require installing a GPU framework. They are not proposed training
implementations.

Examples use `TypeVar`, `Generic`, and `TypeAlias` rather than the Python 3.12-only
`class Batch[T]`, `def first[T](...)`, and `type Alias = ...` syntax. Both tool
configurations target 3.11, and `requires-python` records that minimum. Compatibility
means executing tests on 3.11 as well as checking syntax and types. To verify the
minimum explicitly, use `uv run --python 3.11 --locked pytest`.

Verified baseline: **Pyrefly 1.3.1**, **Ruff 0.16.9**. The config files require those
versions, making upgrades an explicit review of diagnostics and examples.

From this repository, these commands provision the development environment through
`uv` and use the checked-in configurations. `uv.lock` records dependency resolution;
`--locked` rejects unexpected dependency changes:

```sh
uv run --locked pyrefly check
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest
```

In an existing project, run the tools in its dependency environment so Pyrefly can
resolve the installed libraries. Keep the editor's checker version aligned too.
Formatting checks are read-only; `ruff format .` applies formatting changes.

Every Python fence in the guide links to source in [examples/](../examples/) or the
[pytest lesson](../tests/pytest_patterns/).
For example, `uv run examples/validated_records.py` runs the metadata example; examples
normally produce no console output. They also work as small modules to explore in
an editor or REPL.

**The tests keep the guide honest.** They compare documentation fences with linked
source files, check and execute each example independently, activate deliberately
invalid lines one at a time, and assert exact diagnostic categories and locations.
They also verify that a new union variant breaks incomplete matching, and exercise
runtime obligations such as response validation. Ruff and Pyrefly alone do not
inspect Markdown fences; the synchronization test connects those fences to checked
Python files.

The repository is a non-distributable `uv` project: `pyproject.toml` manages tools
and project metadata without installing a library package. One dependency list
includes the tools and libraries needed by this tutorial;
`uv run` provisions them automatically. To adopt the policy in another project,
the two standalone TOML configs are the reusable starting point.

## What the configurations enforce

[Pyrefly's strict preset](https://pyrefly.org/en/docs/configuration/#preset)
is the starting point. Our config additionally rejects explicit `Any`, returns
leaking `Any`, missing annotations, empty implementation bodies, and several
suspicious constructs. Imports must resolve; unrelated checker suppressions must
not hide errors. See the [diagnostic reference](https://pyrefly.org/en/docs/error-kinds/)
for individual rules.

This is an opinionated, verified profile, not a claim that every optional diagnostic
is enabled. Inference remains useful for local variables; annotations belong at
function and data boundaries. More annotations do not automatically mean more safety.

[Ruff](https://docs.astral.sh/ruff/settings/) complements type checking with bug
patterns, annotation hygiene, imports, modern syntax, and suppression checks. It
does not prove assignability or exhaustive matching. Its typing rules can affect
imports needed for runtime annotation inspection; review fixes in projects using
Pydantic or other annotation consumers.

No configuration turns Python into a sound, closed-world language. `Any` flowing
through third-party code, deliberate casts, mutation, and dynamic features still
require boundary design and review.

A checker can also reject valid Python. See [working with checker limitations](checker-limitations.md)
for tested inference and stub failures, local repairs, and when a narrow suppression
is preferable to restructuring good code.

## Reading the examples

Each application example is self-contained; the pytest lesson's test modules and
`conftest.py` run together through pytest. Comments such as
`# rejected[bad-argument-type]: ...` hold deliberately invalid examples and the
expected diagnostic kinds. The tests activate them independently in temporary
files; the checked-in modules remain valid. These comments are not suppressions.
