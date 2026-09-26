# Supplementary libraries

[Project overview and reading path](../README.md)

Pydantic and pydantic-settings are the guide's standard boundary tools.
Small local types explain internal contracts. In application code, established
libraries can avoid rebuilding result combinators, iterator utilities, and schema
validators. Choose the dependency for the problem it solves, and verify the actual
API path with Pyrefly. A library advertising type hints is not proof that every
operation preserves types or rejects misuse.

| Need | Library to consider | What it contributes | What remains outside its guarantee |
| --- | --- | --- | --- |
| Expected success/failure outcomes | [returns](https://returns.readthedocs.io/en/latest/pages/result.html) | `Result`, `Success`, `Failure`, and composition | Unchecked unwrapping can raise; mypy-plugin guarantees do not transfer to Pyrefly |
| Reusable success/failure and optional-value composition | [Expression](https://expression.readthedocs.io/en/stable/guides/getting-started.html) | `Result`, `Option`, and composition helpers | Not every variant access is statically guarded |
| Batching and iterator transformations | [more-itertools](https://more-itertools.readthedocs.io/en/stable/) | Reusable iterable algorithms | Batch length, exhaustion, and buffering remain runtime concerns |
| Required boundary validation and SDK payloads | [Pydantic](https://docs.pydantic.dev/latest/concepts/strict_mode/) | Models and `TypeAdapter` with an explicit coercion policy | Runtime validation does not make arbitrary incoming data statically safe |

**Verified here:** returns 0.29.0, Pydantic 2.13.5, pydantic-settings 2.15.0, Expression 5.7.0,
and more-itertools 11.1.0. The lockfile records the exact environment; manifest
requirements use lower bounds. Expression and more-itertools are optional design
choices, while boundary validation examples use Pydantic consistently.

Use **returns** for result containers rather than defining custom `Ok`/`Err`/`Result`
types. The [errors lesson](errors-and-absence.md) demonstrates parsing, handling
both outcomes, and mapping successful values with runnable examples. Expression
below is an optional comparison for projects already using its functional APIs.

## Expression: use composition, understand variant access

For projects already using Expression, shared
`map`/`bind` operations are clearer than repeated dispatch. `map` transforms a
success; `bind` composes a step that itself returns a result. Explicitly specifying
both generic arguments at construction keeps the success and error contracts
visible. See the [Result API](https://expression.readthedocs.io/en/stable/reference/result.html).

[Source](../examples/expression_results.py)

```python
"""Compose expected failures using Expression's typed Result operations."""

from dataclasses import dataclass
from typing import Annotated

from expression import Result
from pydantic import Field, TypeAdapter, ValidationError

LABEL = TypeAdapter[int](Annotated[int, Field(ge=0)])


@dataclass(frozen=True, slots=True)
class InvalidLabel:
    """Preserve why a dataset label could not be parsed."""

    reason: str


def parse_label(raw: str) -> Result[int, InvalidLabel]:
    """Return a nonnegative label or a typed error for malformed input."""
    try:
        value = LABEL.validate_python(raw)
    except ValidationError:
        return Result[int, InvalidLabel].Error(
            InvalidLabel("not a nonnegative integer")
        )
    return Result[int, InvalidLabel].Ok(value)


def label_name(value: int) -> str:
    """Render a successfully parsed class index."""
    return f"class {value}"


def describe_error(error: InvalidLabel) -> str:
    """Render a parse failure without assigning it a success value."""
    return f"rejected: {error.reason}"


parsed = parse_label("7")
rendered: Result[str, InvalidLabel] = parsed.map(label_name)
description: str = rendered.default_with(describe_error)
# rejected[bad-assignment]: wrong: Result[str, InvalidLabel] = parsed
```

**Static guarantee demonstrated:** mapping the integer label to text preserves the
error type and changes the success type. Assigning the original integer result to
`Result[str, InvalidLabel]` is rejected.

**Important limit verified by our tests:** Pyrefly accepts `.ok` on an Expression
`Error` result, but that access raises `AttributeError` at runtime. Do not assume
library containers force callers to check the variant before accessing it. Use
documented handling operations. The returns lesson likewise tests unchecked
unwrapping as a runtime failure, not a rejected static operation.

An `Option` is useful for ordinary presence/absence. Where the reason matters,
keep a reason-carrying variant or a `Result` error instead. Callback exceptions
still require the explicit boundary policy from the third-party adapter lesson.

## more-itertools: preserve element types, specify stream policy

Use more-itertools for established iterator algorithms instead of hand-rolled
buffering loops. For five samples and a batch size of two, `chunked` normally
yields lengths `2, 2, 1`. With `strict=True`, it raises before yielding the short
final batch. Earlier batches have already been yielded; this is not an all-or-nothing
validation of the source. See the [chunked reference](https://more-itertools.readthedocs.io/en/stable/api.html#more_itertools.chunked).

[Source](../examples/iterator_batches.py)

```python
"""Preserve element types while forming strict batches with more-itertools."""

from collections.abc import Iterable, Iterator
from typing import TypeVar

from more_itertools import chunked

T = TypeVar("T")


def full_batches(samples: Iterable[T], batch_size: int) -> Iterator[list[T]]:
    """Yield full lists; reject invalid size now and a partial tail on iteration."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    return chunked(samples, batch_size, strict=True)


batches: Iterator[list[int]] = full_batches((1, 2, 3, 4), batch_size=2)
first_batch = next(batches)
# rejected[bad-assignment]: wrong: Iterator[list[str]] = batches
```

**Static guarantee demonstrated:** the iterator retains the element type. It cannot
be assigned to an iterator of string lists.

**Runtime obligations:** a list's length is not encoded in `list[T]`. Exhaustion,
partial batches, and exceptions occur during consumption. The wrapper validates
positive batch size immediately; tests verify the delayed partial-tail failure.
`peekable` and `seekable` can retain buffered items, so inspect access patterns
before using them on large or infinite streams.

Prefer standard-library `itertools` where it has the needed operation. For this
guide's 3.11 baseline, `itertools.batched` is unavailable: it was introduced in
3.12, with `strict` added in 3.13. [Python's batched documentation](https://docs.python.org/3/library/itertools.html#itertools.batched).

## Validation libraries complement static checking

Use Pydantic for external schemas, including small ones: `BaseModel` for model
objects, `TypeAdapter` for plain typed structures, and validated dataclasses when
that interface fits. Use pydantic-settings for environment configuration and
[CLIs](state-and-generics.md#build-clis-with-pydantic-settings), instead of
hand-written argparse. See
[data modeling](data-modeling.md), [settings](state-and-generics.md#load-settings-at-startup),
and the [SDK adapter](third-party-boundaries.md) for executable examples.

Choose coercion deliberately. Strict float fields still accept integers; JSON
validation can accept date strings that strict Python-object validation rejects.
Label parsing deliberately accepts numeric text, including `"7.0"` as integer `7`;
that is a parsing policy, not a claim that all boundaries should coerce. See
[Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/).

Keep validators at ingress. Internal dataclasses, plain records, and ordinary
algorithm precondition checks do not need a Pydantic wrapper. In particular, never
move schema validation into compiled inference just to standardize all objects;
see [the inference handoff](ml-correctness.md#validation-before-compiled-inference).

`model_construct` bypasses validation, and `model_copy(update=...)` does not
validate the update. Frozen models prevent ordinary field assignment, not mutation
of a contained tensor or list. Revalidate models from untrusted paths when needed;
avoid unchecked construction as a routine optimization. Tests must cover the
actual admission path, not merely a model's happy-path constructor.
[Pydantic model behavior](https://docs.pydantic.dev/latest/concepts/models/).

## Adopt libraries without weakening the checker

Before relying on an API, pin a Python-3.11-compatible release and add a positive
example plus a misuse that must fail under this project's actual checker. Check
inferred output types, failure behavior, and lazy evaluation. Do not treat a clean
run that inferred `Any` as evidence of compatibility.

Some libraries depend on checker-specific extensions. For example, `returns`
documents a mypy plugin for parts of its typing behavior; that is not evidence
those guarantees transfer to Pyrefly. This guide verifies the demonstrated
constructors, typed accessors, and mapping under Pyrefly; validate additional
decorators and composition helpers before relying on their inferred types.
[returns plugin documentation](https://returns.readthedocs.io/en/latest/pages/contrib/mypy_plugins.html).

Keep optional recommendations separate from required example dependencies. Do not
install the entire table into every application, and do not invent a custom version
of a well-supported utility merely to keep the dependency count at zero.
