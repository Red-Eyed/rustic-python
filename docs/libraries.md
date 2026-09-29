# Supplementary libraries

[Project overview and reading path](../README.md)

| Need | Library to consider | What it contributes | What remains outside its guarantee |
| --- | --- | --- | --- |
| Batching and iterator transformations | [more-itertools](https://more-itertools.readthedocs.io/en/stable/) | Reusable iterable algorithms | Batch length, exhaustion, and buffering remain runtime concerns |
| Required boundary validation and SDK payloads | [Pydantic](https://docs.pydantic.dev/latest/concepts/strict_mode/) | Models and `TypeAdapter` with an explicit coercion policy | Runtime validation does not make arbitrary incoming data statically safe |
| Environment configuration and CLIs | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Typed settings and argument models | Source precedence and coercion need an explicit policy |

**Verified here:** Pydantic 2.13.5, pydantic-settings 2.15.0, and more-itertools
11.1.0. The lockfile records the exact environment; manifest requirements use lower
bounds. more-itertools is an optional design choice, while boundary validation
examples use Pydantic consistently.

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

**Result:** `first_batch` is `[1, 2]`; the next batch is `[3, 4]`.

**Static guarantee:** the iterator retains the element type. It cannot
be assigned to an iterator of string lists.

**Runtime obligations:** a list's length is not encoded in `list[T]`. Exhaustion,
partial batches, and exceptions occur during consumption. The wrapper validates
positive batch size immediately; tests verify the delayed partial-tail failure.
`peekable` and `seekable` can retain buffered items, so inspect access patterns
before using them on large or infinite streams.

Prefer standard-library `itertools` where it has the needed operation. For this
guide's 3.11 baseline, `itertools.batched` is unavailable: it was introduced in
3.12, with `strict` added in 3.13. [Python's batched documentation](https://docs.python.org/3/library/itertools.html#itertools.batched).

An incomplete batch violates this iterator's contract and stops consumption.
If callers support partial batches, represent that decision explicitly.

## Validation libraries complement static checking

Use Pydantic at external boundaries and pydantic-settings for shared configuration
and CLI schemas. The [data](data-modeling.md) and [settings](state-and-generics.md)
chapters cover them; internal records need not carry these dependencies.

Choose coercion deliberately. Strict float fields still accept integers; JSON
validation can accept date strings that strict Python-object validation rejects.
Label parsing deliberately accepts numeric text, including `"7.0"` as integer `7`;
that is a parsing policy, not a claim that all boundaries should coerce. See
[Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/).

`model_construct` bypasses validation, and `model_copy(update=...)` does not
validate the update. Frozen models prevent ordinary field assignment, not mutation
of a contained tensor or list. Revalidate models from untrusted paths when needed;
avoid unchecked construction as a routine optimization. Tests must cover the
actual admission path, not merely a model's happy-path constructor.
[Pydantic model behavior](https://docs.pydantic.dev/latest/concepts/models/).

## Check the API you use

A library advertising annotations may still infer `Any` or depend on a
checker-specific plugin. Verify a passing use and a misuse that should be rejected,
including lazy failures and inferred return types. Choose a library for its needed
operation; the guide's dependency list is not an application requirement.
