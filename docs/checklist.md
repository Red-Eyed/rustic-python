# Design and review checklist

[Project overview and reading path](../README.md)

Use this as a review reference after reading the relevant lessons. Apply only
items that fit the change. Each link explains the rationale, costs, and examples.

## Choose the contract

- [ ] Name a concrete mistake the design prevents; use the simplest representation
  that preserves the contract. [Practical choices](practical-choices.md)
- [ ] Give shared records precise fields and domain types. Keep required fields
  required; parse dates and timestamps at the boundary. [Data modeling](data-modeling.md)
- [ ] Preserve relationships between arguments and results, and encode structural
  preconditions where useful. [State and generics](state-and-generics.md)

## Handle outcomes and alternatives

- [ ] Declare supported recovery decisions as typed outcomes. Document why any
  remaining exceptions must unwind the operation; a `Raises:` section is not a
  checked failure contract. [Failure contracts](errors-and-absence.md#make-expected-failures-explicit)
- [ ] Narrow outcomes before consuming payloads and check closed unions with
  `assert_never`. Avoid unchecked unwraps and discarded failures.
  [Result handling](errors-and-absence.md#choose-a-representation-for-the-callers-decisions)
- [ ] Preserve meaningful absence reasons and distinguish missing values from
  valid zero or emptiness. [Absence](errors-and-absence.md#preserve-the-reason-a-value-is-absent)
- [ ] Retain the diagnostic details callers need without turning programming
  defects into routine failures. [Failure provenance](errors-and-absence.md#know-where-a-failure-happened)

## Validate at boundaries

- [ ] Validate external data with explicit coercion, missing-field, and extra-field
  policies; expose precise types afterward. Keep unknown library values inside
  adapters. [Boundary validation](third-party-boundaries.md)
- [ ] Use declared fields and typed interfaces in application logic. Keep necessary
  reflection local to documented adapters or tests. [Dynamic access](third-party-boundaries.md#restrict-dynamic-attribute-access)
- [ ] Keep configuration and CLI constraints consistent, and side effects at the
  application edge. [Settings and CLIs](state-and-generics.md#load-settings-at-startup)
- [ ] Define behavior for malformed, empty, nonfinite, and partial inputs where
  relevant. [Edge cases](practical-choices.md#edge-cases-that-types-alone-do-not-settle)

## Keep components and state understandable

- [ ] Use small protocols where substitution is needed. Implementations and
  wrappers must preserve error and mutation contracts. [Composition](oop-and-plugins.md)
- [ ] Model state-dependent operations explicitly and account for shallow
  immutability and aliases. [State and immutability](state-and-generics.md)
- [ ] In numerical code, keep native arrays and tensors; validate before compiled
  inference. [Scientific applications](ml-correctness.md)

## Verify the promises

- [ ] Check passing code and the intended static rejections. Keep workarounds
  narrow and supported by evidence. [Tooling](tooling.md), [checker limitations](checker-limitations.md)
- [ ] Test observable behavior and relevant edge cases. Compose fixtures through
  arguments and cover resource cleanup. [Testing](testing.md)
- [ ] Distinguish static guarantees, runtime validation, and conventions. Do not
  infer exception freedom, ownership, or scientific correctness from passing
  types. [Benefits and limits](fundamentals.md)
