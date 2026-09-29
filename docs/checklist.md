# Design and review checklist

[Project overview and reading path](../README.md)

Use this as a review reference after reading the relevant lessons. Apply only
items that fit the change. Each link explains the rationale, costs, and examples.

## Choose the contract

- [ ] Name a concrete mistake the design prevents; use the simplest representation
  that preserves the contract. [Purpose](fundamentals.md)
- [ ] Give shared records precise fields and domain types. Keep required fields
  required; parse dates and timestamps at the boundary. [Data modeling](data-modeling.md)
- [ ] Preserve relationships between arguments and results, and encode structural
  preconditions where useful. [State](state-and-generics.md), [generics](generics.md)

## Handle outcomes and alternatives

- [ ] Declare supported recovery decisions as typed outcomes. Document why any
  remaining exceptions must unwind the operation; a `Raises:` section is not a
  checked failure contract. [Failure contracts](errors-and-absence.md)
- [ ] Narrow outcomes before consuming payloads and check closed unions with
  `assert_never`. Avoid unchecked unwraps and discarded failures.
  [Result handling](errors-and-absence.md)
- [ ] Distinguish unavailable values from valid zero or emptiness with typed
  outcomes. [Undefined metrics](absence.md)
- [ ] Retain the diagnostic details callers need without turning programming
  defects into routine failures. [Result handling](errors-and-absence.md)

## Validate at boundaries

- [ ] Validate external data with explicit coercion, missing-field, and extra-field
  policies; expose precise types afterward. Keep unknown library values inside
  adapters. [Boundary validation](third-party-boundaries.md)
- [ ] Use declared fields and typed interfaces in application logic. Keep necessary
  reflection local to documented adapters or tests. [Dynamic access](dynamic-access.md)
- [ ] Keep configuration and CLI constraints consistent, and side effects at the
  application edge. [Settings](settings.md), [CLIs](typed-cli.md)
- [ ] Define behavior for malformed input at the typed boundary.
  [SDK adapter](third-party-boundaries.md)

## Keep components and state understandable

- [ ] Use small protocols where substitution is needed. Implementations and
  wrappers must preserve error and mutation contracts. [Composition](composition.md)
- [ ] Model state-dependent operations explicitly and account for shallow
  immutability and aliases. [State](state-and-generics.md), [immutability](immutability.md)
- [ ] In numerical code, keep native arrays and tensors. Check numerical behavior
  separately from static contracts. [Limits](fundamentals.md)

## Verify the promises

- [ ] Check passing code and the intended static rejections. Keep workarounds
  narrow and supported by evidence. [Static evidence](tooling.md), [checker limitations](checker-limitations.md)
- [ ] Test observable behavior and the promised checker rejection.
  [Reading examples](tooling.md)
- [ ] Distinguish static guarantees, runtime validation, and conventions. Do not
  infer exception freedom, ownership, or scientific correctness from passing
  types. [Benefits and limits](fundamentals.md)
