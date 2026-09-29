# Supplementary libraries

[Project overview and reading path](../README.md)

Pydantic and pydantic-settings are the guide's standard boundary tools.
Small local types explain internal contracts. Use established libraries for
iterator utilities and schema validation, and verify the actual API path with
Pyrefly. A library advertising type hints does not prove that every operation
preserves types or rejects misuse.

| Need | Library to consider | What it contributes | What remains outside its guarantee |
| --- | --- | --- | --- |
| Batching and iterator transformations | [more-itertools](https://more-itertools.readthedocs.io/en/stable/) | Reusable iterable algorithms | Batch length, exhaustion, and buffering remain runtime concerns |
| Required boundary validation and SDK payloads | [Pydantic](https://docs.pydantic.dev/latest/concepts/strict_mode/) | Models and `TypeAdapter` with an explicit coercion policy | Runtime validation does not make arbitrary incoming data statically safe |
| Environment configuration and CLIs | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Typed settings and argument models | Source precedence and coercion need an explicit policy |

**Verified here:** Pydantic 2.13.5, pydantic-settings 2.15.0, and more-itertools
11.1.0. The lockfile records the exact environment; manifest requirements use lower
bounds. more-itertools is an optional design choice, while boundary validation
examples use Pydantic consistently.

Result handling needs no third-party package in this guide. The
[errors lesson](errors-and-absence.md) uses two frozen dataclass variants and a
closed union, with structural pattern matching and exhaustive handling. Keep that
representation small instead of growing a functional-programming framework.

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

The strict iterator's failure policy stops processing when a promised complete
batch cannot be formed. Since iteration is lazy, the exception occurs while
consuming it, not necessarily when creating it. If incomplete batches are a
supported outcome, expose that decision explicitly instead of documenting a
recoverable exception as the only contract.

## Validation libraries complement static checking

The guide recommends Pydantic for external schemas, including small ones:
`BaseModel` for model objects, `TypeAdapter` for plain typed structures, and validated dataclasses when
that interface fits. Use pydantic-settings for environment configuration and
[CLIs](state-and-generics.md#build-clis-with-pydantic-settings), instead of
hand-written argparse so argument and configuration constraints share a schema.
These are the guide's reference tools. The underlying requirement is to validate
unknown data and expose a precise contract; adding a dependency alone does not
establish either guarantee. In an existing project, assess its validation stack
against those requirements before proposing a replacement. See
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

Checker-specific plugins do not establish guarantees under another checker.
Validate constructors, accessors, decorators, and composition helpers with Pyrefly
before relying on their inferred types. Keep the checked API surface small.

Keep optional recommendations separate from required example dependencies. Do not
install the entire table into every application, and do not invent a custom version
of a well-supported utility merely to keep the dependency count at zero.
