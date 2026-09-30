---
name: rustic-python
description: Design or review Python type contracts, third-party boundaries, protocols, and pytest tests using practical Rust-inspired patterns. Use for Python API and data-model design, or when asked to apply the Rustic Python guide.
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

1. Identify the operation, the mistake to prevent, and the caller's supported
   decisions. Read [the application workflow](docs/agent-guide.md) and only the
   relevant chapters below.
2. Choose the simplest representation that makes incorrect use a checker error.
   Preserve precise records, typed recoverable outcomes, and meaningful absence.
   Keep necessary reflection and unknown library values inside documented adapters.
3. Follow the chapter's contract, including its runtime obligations. The reference
   stack uses Pydantic, pydantic-settings, and a small custom Ok/Err union; adapt
   implementation choices to the target project's constraints. Do not add a
   result framework, unchecked unwrap, or exceptions as the sole contract for
   recoverable failures. A Result annotation does not prove exception freedom.
4. Verify the promised rejection with the project's checker and runtime behavior
   with relevant tests. Use [the checklist](docs/checklist.md) for a final pass and
   report which guarantees are static, runtime-validated, or convention only.

## Topic references

All paths are relative to this installed skill, not the user's project.

- Start with [the guide's purpose](docs/fundamentals.md) and
  [reading examples](docs/tooling.md).
- For data, read [Result and match](docs/errors-and-absence.md),
  [total operations](docs/total-operations.md),
  [validated records](docs/data-modeling.md), [variants](docs/variants.md),
  or [undefined metrics](docs/absence.md) as relevant.
- For APIs, read [protocols](docs/oop-and-plugins.md),
  [composition](docs/composition.md), [state](docs/state-and-generics.md),
  or [generics](docs/generics.md).
- For boundaries, read [SDK adapters](docs/third-party-boundaries.md),
  [dynamic access](docs/dynamic-access.md), or [settings](docs/settings.md).
- For checker problems, read [local workarounds](docs/checker-limitations.md).

## Configuration templates

`pyrefly.toml`, `ruff.toml`, and `pytest.ini` are reference templates. Inspect
existing project settings first and propose a minimal merge when requested.
Never overwrite a project's settings just to make it resemble this tutorial.
The bundled `pyproject.toml` and `uv.lock` describe the tutorial's tested
environment; they are not dependency requirements for the user's application.

Examples and tests are local reference material and remain usable offline.
The guide does not establish ownership, tensor shapes, numerical correctness,
or freedom from exceptions merely because a type checker accepts a program.
