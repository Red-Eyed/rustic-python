# How to read the examples

[Project overview and reading path](../README.md)

Code, relevant results, and checker errors appear on the page. Source links are
optional; no Python installation, terminal, or repository clone is needed.

## Passing and rejected cases

The [record lesson](data-modeling.md) declares a job name and worker count:

| Expression or input | Result | Why |
| --- | --- | --- |
| `parse_metadata('{"name": "report", "workers": 4}')` | `{"name": "report", "workers": 4}` | Valid input |
| `metadata["workers"]` | `4`, with static type `int` | Declared field |
| `metadata["worker_count"]` | `bad-typed-dict-key` | Undeclared field |
| `broken: JobMetadata = {"name": "report"}` | `bad-typed-dict-key` | Missing required field |
| `parse_metadata('{"name": "report", "workers": 0}')` | Runtime `ValidationError` | Worker count must be positive |

Listings mark invalid statements like this:

```text
# rejected[bad-typed-dict-key]: workers = metadata["worker_count"]
```

The checker rejects the statement after the colon for the named reason.
These comments show incorrect use; they are not suppressions or exercises to run.
Assertions show expected behavior: `assert first(batch) == 0` expects zero.

## What the checks establish

- **Static checking** rejects operations inconsistent with declared types.
- **Runtime validation** checks actual values, such as a positive worker count.
- **Behavioral tests** check results the types do not prove, such as a calculation.

The examples target Python 3.11+, verified with Pyrefly 1.3.1 and Ruff 0.16.9.
Pydantic validates inputs; pytest checks behavior. The strict checker profile
rejects explicit `Any`, missing annotations, and unresolved imports. Ruff handles
style and suspicious patterns; it does not prove type compatibility.

Automated checks verify the printed listings and each intended rejection.
A clean check still does not prove exception freedom, ownership, or numerical
correctness. See [checker limitations](checker-limitations.md) for concrete gaps;
[contributing](contributing.md) contains the maintenance commands.
