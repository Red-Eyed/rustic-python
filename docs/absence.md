# An undefined metric is an outcome

[Project overview and reading path](../README.md)

A report calculates precision from true positives and false positives. If there
are no predicted positives, the score is undefined. A real score of zero means
something different: predictions were made, but none was correct.

**Typical Python**

```python,ignore
def precision(true_positives: int, false_positives: int) -> float:
    total = true_positives + false_positives
    return true_positives / total if total else 0.0


undefined = precision(0, 0)
incorrect = precision(0, 12)
```

Both `(0, 0)` and `(0, 12)` return `0.0`. A caller cannot tell an undefined
score from a valid zero.

**Alternative**

```python,ignore
def precision(tp: int, fp: int) -> Result[float, NoPredictedPositives | InvalidCounts]:
    if tp < 0 or fp < 0:
        return Err(InvalidCounts(tp, fp))
    if tp + fp == 0:
        return Err(NoPredictedPositives())
    return Ok(tp / (tp + fp))


outcome = precision(0, 0)
match outcome:
    case Ok(value=score):
        report = f"{score:.3f}"
    case Err(error=NoPredictedPositives()):
        report = "undefined: no predicted positives"
    case Err(error=InvalidCounts()):
        report = "invalid counts"
    case _:
        assert_never(outcome)
```

This uses the [`Result` pattern](errors-and-absence.md) defined in the preceding
lesson. The complete example also matches both error variants.

[Source](../examples/reasoned_absence.py)

`precision(0, 0)` returns `Err(NoPredictedPositives())`; `precision(0, 12)`
returns `Ok(0.0)`. Formatting produces `"undefined: no predicted positives"`
and `"0.000"` respectively.

The checker rejects assigning the `Result` directly to `float`. The caller must
match both outcomes before using the score, and `assert_never` detects a newly
added outcome variant. A missing score is a supported outcome of this calculation.

Negative counts return `Err(InvalidCounts(...))`; callers must handle that
case too. The caller must still ensure both counts describe the same population.
The type checker cannot prove that condition or the numerical correctness of
the formula.
