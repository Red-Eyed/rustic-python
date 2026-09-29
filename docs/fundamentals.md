# Principles, benefits, and costs

[Project overview and reading path](../README.md)

## Start with a mistake the checker can catch

Suppose a job configuration contains `name` and `workers`, but a caller reads
`worker_count`. A loose dictionary leaves that mismatch to runtime. A `TypedDict`
lets Pyrefly reject the wrong key while the code still uses an ordinary dictionary.
That is a useful starting point: describe an existing interface more precisely,
without requiring a different way to perform the computation.

Prioritize typed configuration and records, explicit return values, small protocols,
and validated dependency boundaries. A type annotation is useful when it catches
a plausible mistake at a reasonable maintenance cost; giving every intermediate
value a new type is not the objective.

The guide follows four principles:

1. **Represent the actual possibilities.** An input record is accepted or rejected.
   A connection is open or closed. A measurement is available or absent for a reason.
2. **Validate at boundaries.** Files, JSON, SDKs, and user input do not
   become trustworthy because a variable has an annotation.
3. **Preserve information.** Carry record schemas and generic relationships through
   helpers instead of collapsing them to `Any`, `object`, or loose dictionaries.
4. **State the guarantee precisely.** Separate what the checker rejects, what a
   runtime validator establishes, and what remains an engineering obligation.

A **boundary** is where untrusted data or an untyped dependency enters typed code.
A **union** describes alternatives, such as a successful value or a rejected input.
**Narrowing** identifies which alternative a value holds before accessing its fields.
The following chapters introduce these techniques through runnable examples.

## Principles and the reference stack

The design goal is to make incorrect API use visible before execution. The guide
recommends a consistent stack so examples can demonstrate that goal: Pyrefly for
static checking, Pydantic for external-data validation, and pydantic-settings for
configuration and CLIs. Ruff checks style and pytest verifies runtime behavior.
These are implementation choices, not properties of Python's type system.

When applying the guide to an existing project, preserve its constraints and
identify the equivalent guarantees in its tools. Do not assume another checker
accepts or rejects exactly the same programs. The guide's policies on typed
recoverable failures, meaningful absence, and restricted reflection are deliberate
design recommendations; each chapter explains their scope and costs.

## What you gain and what it costs

The payoff is not "more annotations." It is **less code that can express a mistake
without a tool objecting**, and a smaller part of the system where unknown data
and dependency behavior must be examined manually.

### A wrong metadata key becomes a static error

In [validated_records.py](../examples/validated_records.py), job configuration has
the required fields `name: str` and `workers: int`. Reading
`metadata["worker_count"]` produces `bad-typed-dict-key`. Constructing a typed record
without `workers` is also rejected. Both cases are verified by the guide tests.

The runtime representation remains a dictionary. Existing serialization and lookup
code do not need a parallel wrapper API. The external JSON still needs validation:
the record annotation tells the checker what has been established, while the parser
establishes it for actual incoming data.

This does not prove the machine has enough resources for the requested workers.
It prevents a specific schema mistake and makes the remaining operational
obligation explicit.

### What the patterns prevent

| Before | After applying the pattern | Evidence and limit |
| --- | --- | --- |
| A new task or split silently uses a wildcard fallback | Exhaustive dispatch makes the missing case visible | A test adds `holdout` to the split union and verifies failure at `assert_never` |
| An unfitted object offers methods that fail only when called | Separate fitted/unfitted types expose different operations | `unfitted.transform(...)` fails static checking; the type does not prove training-data provenance |
| A misspelled dictionary key travels into downstream code | A validated record has known keys and required fields | `worker_count` is rejected; external payloads still require runtime validation |
| An SDK error or malformed response leaks into application logic | The adapter exposes success, call failure, or invalid response | Tests exercise a genuinely unannotated dependency, mutation, exceptions, and malformed data |
| Adding a backend means modifying dispatch branches | A new protocol implementation is registered at construction | An independent `Offset` plugin works without pipeline changes; behavior still needs contract tests |

These are reproducible checks, not anecdotes about production performance.
[Guide tests](../tests/test_guide.py) verify static acceptance and rejection;
[boundary tests](../tests/test_third_party_boundary.py) and
[plugin tests](../tests/test_plugin_composition.py) cover the corresponding runtime
and extension behavior.

### Earlier detection is useful even when it saves no runtime

A diagnostic at the incorrect call usually points closer to the cause than an
exception several layers downstream. Explicit variants also reveal expected failure
modes in a function signature, so a reviewer or coding agent does not have to infer
them from scattered branches. A refactor can deliberately expand a union and use
the resulting errors to locate incomplete dispatchers.

Suppose a report generator reads a misspelled configuration key only after
processing 1,000 files. Rejecting that access before starting avoids discovering
it at the end. This illustrates earlier feedback, not a measured speedup. A report
that computes the wrong total can still type-check; its calculation needs tests.

These benefits apply to services, CLIs, and scientific pipelines: clearer contracts,
earlier feedback, and fewer assumptions carried between components. Type checking
is a development feedback mechanism; it does not make Python execution itself faster.

### Costs and failure modes

| Cost or downside | What it looks like | How to keep it proportionate |
| --- | --- | --- |
| More definitions and concepts | Small operations acquire wrapper types, variants, and annotations | Add a type when it prevents a concrete confusion; keep local, obvious transformations simple |
| Integration work | A dynamic SDK needs an adapter, validation, or corrected stubs | Concentrate uncertainty at a small boundary rather than spreading casts through callers |
| Learning and review overhead | Teams must understand narrowing, generics, and open versus closed interfaces | Prefer a few consistent patterns and readable named functions over clever type machinery |
| Tool and library friction | Inference gaps or dependency updates cause new errors | Pin versions, test the used API paths, and diagnose failures before relaxing rules |
| Runtime cost | Validation scans records or tensors; wrappers may allocate or copy | Validate at trust boundaries and measure expensive checks, especially around accelerator synchronization |
| Stronger coupling to a schema | Adding a variant or changing a record requires caller updates | Use closed unions for intentionally closed domains and protocols for open extension points |
| False confidence | A clean check is mistaken for numerical correctness or trustworthy external data | State whether each guarantee is static, runtime-validated, or a convention |
| Ceremony without protection | Repeated wrapping/unwrapping, giant protocols, and unnecessary class hierarchies | Remove abstractions that do not rule out a realistic mistake or simplify a real substitution point |

Two limits are especially easy to miss. First, `Any`, casts, suppressions, and
dynamic loading can bypass static checks; a precise-looking return annotation
does not establish a runtime fact. Second, valid types do not ensure that values
satisfy an operation's preconditions: `workers: int` does not establish a positive
count. Boundary validation establishes that constraint at runtime. Some structural
preconditions can become static contracts: the [generic batch](state-and-generics.md#preserve-relationships-with-generics)
requires a first item, so a checked caller cannot construct an empty batch.

Types also do not establish correct gradients, absence of data leakage, good labels,
numerical stability, race freedom, or resource ownership. Those need other evidence.
Frozen records and protocols are useful, but they are not a Python borrow checker.

### Where to start, and when to stop

Start at shared APIs, configuration, structured records, and external-data adapters.
The case is strongest in maintained code used
by several people or agents, where contracts need to survive refactoring.

For an exploratory notebook or a short-lived calculation, a complete plugin system
and a family of domain wrappers may cost more than they protect. Keep the checks
that clarify the calculation, and strengthen the boundaries as code becomes reused.

For every proposed abstraction, ask: **which incorrect program will now be rejected,
which runtime failure becomes explicit, or which extension no longer changes the
core?** Demonstrate that benefit with a small test. If none applies, the simpler
representation may be the better design.

See [edge cases and acceptable simplifications](practical-choices.md) for concrete
decision criteria, a plain-function example, and cases where static types are not
enough to establish the runtime behavior.
