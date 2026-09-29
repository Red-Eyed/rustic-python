# Principles, benefits, and costs

[Project overview and reading path](../README.md)

A job configuration contains `name` and `workers`. Reading `worker_count` is a
mistake a type checker can catch before execution if the record declares its
fields. It cannot establish that the machine has enough resources for those workers.
That distinction drives this guide: encode the contract, then check what it cannot prove.

## Four principles

1. **Represent the possibilities.** An input is accepted or rejected; a connection
   is open or closed. Types should expose the operations valid for each case.
2. **Validate at boundaries.** A boundary is where external data or an untyped
   dependency enters typed code. An annotation does not validate incoming JSON.
3. **Preserve information.** Keep record fields and input/output relationships
   visible instead of erasing them with `Any`, `object`, or loose dictionaries.
4. **State the guarantee.** Distinguish static rejection, runtime validation, and
   properties that still need behavioral tests or review.

A **union** describes alternatives. **Narrowing** identifies which alternative a
value holds before accessing its fields. A **protocol** describes the operations
an interchangeable component must provide. Each appears in a worked lesson.

## What you gain and what it costs

| Problem | Design | Remaining cost or obligation |
| --- | --- | --- |
| Misspelled record key | Declared fields | Validate external values |
| Forgotten alternative | Closed union and exhaustive matching | Update callers when adding a variant |
| Method called before setup | Separate state types | Establish setup correctly at runtime |
| Uncertain dependency output | Small validating adapter | Maintain the adapter as the dependency changes |
| Interchangeable implementations | Small protocol | Test behavioral compatibility, including failures and mutation |

These patterns move feedback closer to the mistake. They add definitions,
validation work, and maintenance, so start at shared APIs and external boundaries.
A local calculation rarely needs a wrapper or plugin system. Add structure when
it prevents a concrete error or simplifies a real substitution point.

Types do not establish resource ownership, numerical correctness, or absence of
exceptions. Frozen records do not freeze their mutable contents. Casts, suppressions,
and dynamic features can bypass checking. The relevant chapters explain each limit.

## The reference stack

The guide uses Pyrefly for static checking, Pydantic for external validation,
pydantic-settings for configuration, Ruff for linting, and pytest for behavior.
These are recommended tools, not properties of Python's type system. Existing
projects can use different tools, but must verify the guarantees they rely on.

Continue with [how to read the examples](tooling.md), then [data modeling](data-modeling.md).
Use [practical choices](practical-choices.md) when deciding how much structure a contract needs.
