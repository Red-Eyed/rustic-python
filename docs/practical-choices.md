# Edge cases and acceptable simplifications

[Project overview and reading path](../README.md)

The patterns in this guide are choices, not requirements to reproduce Rust's APIs
in Python. Start with the smallest representation that makes the actual contract
clear. Add structure when an edge case, a second implementation, or a boundary
requires it. Simplifying a design is acceptable; silently changing its behavior is not.

## A simple function can be the right design

For five samples and batches of two, keeping the final partial batch means three
batches. Dropping it means two. This needs a small calculation and an explicit
policy, not a `BatchCount` wrapper, strategy hierarchy, or `Result` around every call.

[Source](../examples/practical_defaults.py)

```python
"""Use a plain function when a small, explicit contract needs no domain wrapper."""


def batch_count(sample_count: int, *, batch_size: int, drop_last: bool = False) -> int:
    """Count batches; reject noninteger counts and invalid ranges without I/O."""
    if type(sample_count) is not int or type(batch_size) is not int:
        raise TypeError("counts must be integers, excluding booleans")
    if sample_count < 0 or batch_size <= 0:
        raise ValueError("sample_count must be nonnegative and batch_size positive")
    full_batches, remainder = divmod(sample_count, batch_size)
    if remainder and not drop_last:
        return full_batches + 1
    return full_batches


batches = batch_count(5, batch_size=2)
full_batches_only = batch_count(5, batch_size=2, drop_last=True)
# rejected[bad-argument-type]: batch_count("5", batch_size=2)
```

**What stays simple:** ordinary integers, one function, one keyword-only policy
flag, and normal exceptions. The boolean selects a calculation policy; it does
not hide a lifecycle with different permitted operations. No protocol is needed
because this helper has no substitution requirement.

**What stays explicit:** zero samples produce zero batches. A zero batch size is
invalid. A small dataset with `drop_last=True` can produce no batches. Booleans are
rejected as counts, even though Python's type system allows them where `int` is
expected. The [tests](../tests/test_practical_defaults.py) exercise these cases.

**What this does not guarantee:** a loader may filter records, shard data, or use a
different sampling policy. This function counts according to its inputs; it does
not predict every loader's behavior. Exceptions also do not appear in its return
type. That tradeoff is acceptable when invalid arguments should abort the operation.

## Acceptable simplifications, and when to stop simplifying

| Simpler choice | Acceptable when | Keep this obligation | Escalate the design when |
| --- | --- | --- | --- |
| Native `int`, `float`, array, or tensor | The surrounding API makes its role clear | Validate relevant ranges or shapes and test calculations | Two roles are repeatedly confused at an API boundary and a distinct type can be preserved without constant relabeling |
| An ordinary function | There is no resource lifecycle or configurable object state to manage | Precise arguments, return type, and failure behavior | State or interchangeable implementations become a real concern |
| A concrete dependency | There is one implementation and callers do not need substitution | Keep the dependency at the appropriate layer | A second backend or independently injected implementation must satisfy the same contract |
| A typed callable | The extension point is one operation | Its argument/return contract and error policy | Implementations need several related operations or stateful capabilities |
| `ValueError` / `TypeError` | Invalid input should stop the current operation | Specific, documented exceptions and a deliberate catch boundary | Callers routinely need to collect, recover from, or route multiple failure outcomes |
| A local `None` from a standard API | It means one local condition, such as a failed lookup, and is handled immediately | An explicit presence check and a typed value after the check | Absence crosses the domain boundary or callers need its reason |
| A local dictionary | It is a temporary literal or a true homogeneous mapping | No concealed record schema escaping to other helpers | Fixed keys form a shared record; use a `TypedDict`, dataclass, or validated model |
| A typed field plus a guard | The invalid state is contained within a short operation | Check it before the operation that requires the value | Many callers must repeatedly remember the same state restriction |
| A boolean option | It selects one clear behavior within the same operation | Named arguments and defined behavior for both choices | Flags interact to admit invalid combinations or represent distinct lifecycles |
| Local mutation | One operation owns the mutable value and the change is easy to follow | Avoid leaking mutable aliases and document observable mutation | Other components retain the same object or concurrent use is possible |
| One boundary validation pass | Ownership or immutability preserves the validated facts | Do not assume mutable data stays valid after other code changes it | Data is mutated or crosses another trust boundary |
| Direct test setup | It is small, local, and owns no shared resource lifetime | Keep the action and assertions visible | Setup repeats or needs cleanup; introduce fixtures |

For example, handle `re.search(...)` returning `None` locally; there is no need to
create a domain error class merely to check whether one pattern matched. This does
not justify replacing an undefined metric's explanation with an unexplained `None`.
Similarly, an SDK's loose dictionary is acceptable as a vendor payload inside its
adapter, not as the unvalidated record passed through the rest of the application.

A function-local variable may rely on useful inference. Public function boundaries
and shared records still need their contracts. Removing redundant local annotations
is different from allowing `Any` to erase the return type of an entire component.

## Edge cases that types alone do not settle

Select the relevant cases for each component; not every helper needs every check.
The table distinguishes existing examples from decisions a new application must make.

| Case | Why the obvious implementation can fail | Decision or evidence |
| --- | --- | --- |
| Zero versus absence | `if value` treats a valid zero as missing | The precision tests distinguish zero from an undefined denominator |
| `bool` versus `int` | `True` can enter an integer-annotated API | The batch-count and metadata tests reject it where counts require actual integers |
| `int` passed to a `float` parameter | A runtime `float` class pattern does not match an integer | The metric formatter handles both, with regression cases for `0` and `0.0` |
| NaN and infinity | A float annotation does not mean finite; ordinary comparisons may not express the intended policy | Softmax, configuration, and SDK-response tests validate finiteness where their contracts require it |
| Empty input | Mean, first-element selection, and batch counting need different policies | Centering and `first` reject empty input; batch counting returns zero |
| Partial final batch | Rejecting, retaining, padding, and dropping affect training differently | Batch-count and iterator tests cover their declared policies; do not silently choose one for a caller |
| Missing, null, extra, or malformed fields | These are different schema conditions | Metadata parsing ignores extras; the SDK adapter requires specific fields and rejects malformed values. Decide whether unknown keys should instead be errors for a particular config |
| Integer versus string versus scalar wrapper | Coercion may change input meaning or erase an upstream error | The SDK example requires a Python float; other boundaries may explicitly normalize supported numeric types |
| Deferred failure | A call can return an iterator successfully and fail later during consumption | Strict chunking tests verify that earlier batches can be consumed before the tail error |
| Shared mutable data | A frozen outer object does not freeze contained tensors or lists | The SDK test checks payload-copy isolation; real shared arrays need an ownership or copying policy |
| Unknown plugin or future variant | Runtime names and a statically closed union are different problems | Registry lookup returns an explicit unknown-name outcome; exhaustive matching tests cover added union variants |
| Failure after a side effect | Retrying may duplicate work even if an exception looks recoverable | New integrations need an idempotency/recovery policy; the example adapter deliberately makes one call |
| Cancellation or process failure | Ordinary exception handling is not process isolation | Adapter tests preserve `KeyboardInterrupt`/`SystemExit`; native crashes require different containment |
| Resource setup fails halfway | Cleanup after an unreached `yield` cannot run | The pytest lesson uses context-managed resources; new multi-resource fixtures must handle partial acquisition |
| All-masked or otherwise empty effective data | The stored batch is nonempty, but a reduction may have no valid elements | A loss/metric implementation must choose rejection, omission, or a defined result and test it; this guide has no such loss implementation |

Python's numeric typing deliberately permits an `int` argument for a `float`
parameter. It does not convert the object to a float before your function runs.
A type-correct call and a runtime class pattern therefore need not line up.
[Numeric typing rules](https://typing.python.org/en/latest/spec/special-types.html#special-cases-for-float-and-complex).

Likewise, `0`, `0.0`, and empty containers are falsy. Use an explicit absence check
when emptiness or zero is a legitimate value.
[Python truth-value rules](https://docs.python.org/3.11/library/stdtypes.html#truth-value-testing).

### A bug this review found in the guide itself

The original [metric formatter](../examples/reasoned_absence.py) accepted
`float | Absent` but matched only `float(score)` for numeric input. Pyrefly accepted
`format_precision(0)`, yet the integer missed that branch and reached `assert_never`
at runtime. The formatter now matches both integers and floats, and
[regression tests](../tests/test_practical_defaults.py) exercise both representations.

The fix needs one additional pattern, not a new numeric class hierarchy. This is
an example of useful simplification: preserve the public contract and repair its
runtime handling with the smallest change that covers the actual edge case.

## Work through the decision on a real boundary

Suppose an SDK returns a record with `confidence: "0.8"`.

1. The value is not yet trusted. Receiving it as `object` preserves that fact.
2. Decide whether the SDK contract permits numeric strings. Do not let a convenience
   validator silently make this product decision.
3. If strings are forbidden, return a schema failure or raise the documented
   validation exception. If permitted, parse once, then validate range and finiteness.
4. Expose the validated value using the simplest useful domain record. Do not pass
   a loose dictionary onward just to avoid defining that record.
5. Test the accepted form and nearby rejected forms: malformed text, NaN, missing
   key, `True`, and an out-of-range number.

The vendor adapter in this guide rejects the string. That is its explicit policy,
not a rule that every application must reject numeric strings. The same reasoning
applies to missing labels, optional fields, partial batches, and unknown config keys.

## Simplifications that conceal errors

These are not equivalent ways to shorten the implementation:

- Adding `Any`, a cast, or a blanket ignore to make an unexplained error disappear.
- Returning zero for an undefined metric without a stated evaluation policy.
- Catching every exception and returning an empty collection, conflating failure
  with a successful empty result.
- Retrying an operation without considering whether it already changed external state.
- Making required record fields optional because one upstream payload is malformed.
- Naming a tensor `ValidatedLogits` without establishing anything about its producer.
- Running validation once and then allowing untracked mutation to invalidate it.

A scoped workaround for a verified checker/stub defect can be justified, but its
unchecked assumption must be explicit and covered by evidence. It is not a generic
escape route from modeling the boundary.
See [tested checker workarounds](checker-limitations.md) for concrete examples.

## A short review rule

For a new component, record the normal input, the relevant edge cases, the chosen
failure/absence policy, and the simplest representation that supports it. Explain
why any extra type, wrapper, protocol, or validation pass is needed. This can be a
few sentences beside the API and a small parametrized test table, not a separate
design document.

For an existing component, preserve its public behavior unless changing that behavior
is intentional. A simplification that silently drops samples or converts malformed
input is a policy change, even if the resulting code is shorter.
