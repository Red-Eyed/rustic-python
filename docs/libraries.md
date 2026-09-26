# Supplementary libraries

[Project overview and reading path](../README.md)

The core guide's small local types explain the mechanics. In application code, established
libraries can avoid rebuilding result combinators, iterator utilities, and schema
validators. Choose the dependency for the problem it solves, and verify the actual
API path with Pyrefly. A library advertising type hints is not proof that every
operation preserves types or rejects misuse.

| Need | Library to consider | What it contributes | What remains outside its guarantee |
| --- | --- | --- | --- |
| Reusable success/failure and optional-value composition | [Expression](https://expression.readthedocs.io/en/stable/guides/getting-started.html) | `Result`, `Option`, and composition helpers | Not every variant access is statically guarded |
| Batching and iterator transformations | [more-itertools](https://more-itertools.readthedocs.io/en/stable/) | Reusable iterable algorithms | Batch length, exhaustion, and buffering remain runtime concerns |
| Validated configuration and SDK payloads | [Pydantic](https://docs.pydantic.dev/latest/concepts/strict_mode/) | Models and `TypeAdapter` with an explicit coercion policy | Runtime validation does not make arbitrary incoming data statically safe |
| Typed serialization boundaries | [msgspec](https://github.com/jcrist/msgspec) | `Struct` records and typed decoding | Decoding validation is not a proof about every direct constructor call |
| Dataframe schema and value checks | [Pandera](https://pandera.readthedocs.io/en/stable/) | Column, dtype, and value constraints | Do not assume a schema annotation makes Pyrefly prove every dataframe operation |
| Tensor shape/dtype assertions | [jaxtyping](https://docs.kidger.site/jaxtyping/api/runtime-type-checking/) | Array annotations paired with a runtime checker | Runtime shape checks are not equivalent to Pyrefly's static shape extension |

**Verified here:** Expression 5.7.0 and more-itertools 11.1.0, using Python 3.11 and
the checked-in Pyrefly/Ruff settings. Their examples and relevant limitations have
regression tests. The other entries are selection guidance from their official
documentation, not a claim of verified compatibility for every API or release.
They are not installed as project dependencies.

## Expression: use composition, understand variant access

Use Expression when success/failure pipelines recur across a codebase and shared
`map`/`bind` operations are clearer than repeated dispatch. `map` transforms a
success; `bind` composes a step that itself returns a result. Explicitly specifying
both generic arguments at construction keeps the success and error contracts
visible. See the [Result API](https://expression.readthedocs.io/en/stable/reference/result.html).

[Source](../examples/expression_results.py)

```python
"""Compose expected failures using Expression's typed Result operations."""

from dataclasses import dataclass

from expression import Result


@dataclass(frozen=True, slots=True)
class InvalidLabel:
    """Preserve why a dataset label could not be parsed."""

    reason: str


def parse_label(raw: str) -> Result[int, InvalidLabel]:
    """Return a nonnegative label or a typed error for malformed input."""
    try:
        value = int(raw)
    except ValueError:
        return Result[int, InvalidLabel].Error(InvalidLabel("not an integer"))
    if value < 0:
        return Result[int, InvalidLabel].Error(InvalidLabel("negative label"))
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
this class has the same narrowing requirement as our `Ok[T] | Err[E]` union. Use
the documented composition/handling operations; keep explicit dataclass unions
when enforcing variant access and exhaustive dispatch is the priority.

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

For a growing external schema, prefer Pydantic over repeating a large manual parser.
Use `model_validate` or `TypeAdapter.validate_python` at the boundary, select strict
validation when coercion is unwanted, and decide how extra fields are handled.
Strictness is input-dependent: JSON date strings can still be accepted where a
Python string would be rejected. Validate the actual boundary format rather than
assuming that strict mode means "never converts anything."
[Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/).

Consider msgspec when typed encoding and decoding are the central requirement;
benchmark the real workload before choosing it for speed. Prefer one boundary
schema system per component unless two serve demonstrably different needs.
[msgspec project documentation](https://github.com/jcrist/msgspec).

For dataframes, Pandera can express value constraints that plain container typing
does not capture. For arrays, jaxtyping with a runtime checker can assert shape and
dtype relationships. Put these checks where data enters a component, and measure
cost before applying them to every training step. Neither recommendation means
that an annotation alone proves the dataset or tensor is valid before execution.
[Pandera models](https://pandera.readthedocs.io/en/latest/dataframe_models.html),
[jaxtyping runtime checking](https://docs.kidger.site/jaxtyping/api/runtime-type-checking/).

## Adopt libraries without weakening the checker

Before relying on an API, pin a Python-3.11-compatible release and add a positive
example plus a misuse that must fail under this project's actual checker. Check
inferred output types, failure behavior, and lazy evaluation. Do not treat a clean
run that inferred `Any` as evidence of compatibility.

Some libraries depend on checker-specific extensions. For example, `returns`
documents a mypy plugin for parts of its typing behavior; that is not evidence
those guarantees transfer to Pyrefly. It remains a candidate, but validate the
specific operations before choosing it over a simpler result representation.
[returns plugin documentation](https://returns.readthedocs.io/en/latest/pages/contrib/mypy_plugins.html).

Keep optional recommendations separate from required example dependencies. Do not
install the entire table into every application, and do not invent a custom version
of a well-supported utility merely to keep the dependency count at zero.
